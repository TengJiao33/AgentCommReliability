#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any


TASK_NAME = "pg40_direct_routing"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()


def compact_text(text: Any, max_chars: int) -> str:
    if not isinstance(text, str):
        return ""
    compact = " ".join(text.strip().split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max(0, max_chars - 3)].rstrip() + "..."


def parse_json_object_loose(text: str | None) -> tuple[dict[str, Any], str | None]:
    if text is None:
        return {}, "empty_response"
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {}, "no_json_object"
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as error:
            return {}, f"json_decode_error:{error}"
    if not isinstance(parsed, dict):
        return {}, "response_not_object"
    return parsed, None


def fragment_view(fragment: dict[str, Any], max_content_chars: int) -> dict[str, Any]:
    return {
        "fragment_id": fragment.get("id"),
        "source_id": fragment.get("source_id"),
        "cost": fragment.get("cost", 1),
        "text": compact_text(fragment.get("text", ""), max_content_chars),
    }


def build_direct_prompt(row: dict[str, Any], max_content_chars: int) -> str:
    prompt_packet = {
        "evaluation_id": row.get("hard_evaluation_id"),
        "scenario_id": row.get("scenario_id"),
        "roles": row.get("roles", []),
        "role_budgets": row.get("role_budgets", {}),
        "fragments": [fragment_view(fragment, max_content_chars) for fragment in row.get("fragments", [])],
    }
    response_schema = {
        "roles": {
            "role_name": [
                {
                    "fragment_id": "f1",
                    "source_id": "copy source_id for this fragment",
                    "visibility": "role_private|shared_subset|shared_all",
                    "reason": "short reason",
                }
            ]
        },
        "rejected": [
            {
                "fragment_id": "f2",
                "source_id": "copy source_id for this fragment",
                "reason": "why this fragment should not be sent to any role",
            }
        ],
    }
    return "\n".join(
        [
            "You are assigning prompt fragments to sub-agent roles under a tight token budget.",
            "For each role, choose only the fragments needed by that role.",
            "Each fragment has a cost. The total cost for a role should not exceed that role's budget.",
            "Do not include irrelevant best-practice or distractor fragments.",
            "If one fragment is needed by multiple roles, include it separately for each role and set visibility accordingly.",
            "Use only fragment_id values from FRAGMENTS.",
            "Copy source_id exactly from the selected fragment.",
            "Return JSON only. No markdown fences, prose, or comments.",
            "",
            "PACKET:",
            json.dumps(prompt_packet, ensure_ascii=False, indent=2),
            "",
            "Return one valid JSON object with this shape:",
            json.dumps(response_schema, ensure_ascii=False, indent=2),
        ]
    )


def filter_rows(rows: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    ids = set(args.evaluation_id)
    if ids:
        rows = [
            row
            for row in rows
            if row.get("hard_evaluation_id") in ids
            or row.get("base_evaluation_id") in ids
            or row.get("scenario_id") in ids
        ]
    if args.limit:
        rows = rows[: args.limit]
    return rows


def completed_requests(path: Path, model: str) -> set[str]:
    completed: set[str] = set()
    if not path.exists():
        return completed
    for row in read_jsonl(path):
        if row.get("model") == model and row.get("task") == TASK_NAME and ("response" in row or "error" in row):
            completed.add(str(row.get("hard_evaluation_id", "")))
    return completed


def write_prompt_dry_run(rows: list[dict[str, Any]], args: argparse.Namespace) -> None:
    out_rows = []
    for row in rows:
        prompt = build_direct_prompt(row, args.max_content_chars)
        out_rows.append(
            {
                "hard_evaluation_id": row.get("hard_evaluation_id"),
                "base_evaluation_id": row.get("base_evaluation_id"),
                "scenario_id": row.get("scenario_id"),
                "shuffle_seed": row.get("shuffle_seed"),
                "roles": row.get("roles", []),
                "role_budgets": row.get("role_budgets", {}),
                "fragment_count": len(row.get("fragments", [])),
                "prompt_chars": len(prompt),
                "prompt": prompt,
            }
        )
    write_jsonl(args.dry_run_prompts_out, out_rows)
    print(json.dumps({"rows": len(out_rows), "dry_run_prompts_out": str(args.dry_run_prompts_out)}, ensure_ascii=False, indent=2))


def call_chat(client: Any, args: argparse.Namespace, prompt: str) -> str:
    last_error: Exception | None = None
    for attempt in range(args.retries + 1):
        try:
            response = client.chat.completions.create(
                model=args.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as error:  # noqa: BLE001
            last_error = error
            status_code = getattr(error, "status_code", None) or getattr(error, "status", None)
            try:
                status_code = int(status_code) if status_code is not None else None
            except (TypeError, ValueError):
                status_code = None
            if status_code in {400, 401, 403, 404, 422} or attempt == args.retries:
                break
            time.sleep(min(2 * (2**attempt), 30))
    raise RuntimeError(f"chat completion failed after {args.retries + 1} attempts: {last_error}")


def run(args: argparse.Namespace) -> None:
    rows = filter_rows(read_jsonl(args.packet), args)
    if args.dry_run_prompts_out:
        write_prompt_dry_run(rows, args)
        return
    if not args.base_url or not args.out:
        raise SystemExit("provide --base-url and --out unless using --dry-run-prompts-out")

    from openai import OpenAI

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is not set")
    client = OpenAI(api_key=api_key, base_url=args.base_url)
    completed = completed_requests(args.out, args.model)
    print(f"model={args.model}")
    print(f"packet={args.packet}")
    print(f"evaluations={len(rows)}")
    print(f"temperature={args.temperature}")
    print(f"max_tokens={args.max_tokens}")
    print(f"completed={len(completed)}")
    for index, row in enumerate(rows, start=1):
        request_id = str(row.get("hard_evaluation_id"))
        if request_id in completed:
            print(f"[{index}/{len(rows)}] skip {request_id}", flush=True)
            continue
        print(f"[{index}/{len(rows)}] pg40_direct {request_id}", flush=True)
        out_row: dict[str, Any] = {
            "hard_evaluation_id": request_id,
            "base_evaluation_id": row.get("base_evaluation_id"),
            "scenario_id": row.get("scenario_id"),
            "shuffle_seed": row.get("shuffle_seed"),
            "task": TASK_NAME,
            "model": args.model,
            "provider": "openai-compatible",
        }
        try:
            prompt = build_direct_prompt(row, args.max_content_chars)
            response_text = call_chat(client, args, prompt)
            parsed, parse_error = parse_json_object_loose(response_text)
            out_row["prompt"] = prompt if args.include_prompts else None
            out_row["response"] = parsed if not parse_error else response_text
            out_row["response_parse_error"] = parse_error
            out_row["status"] = "ok" if not parse_error else "parse_warning"
        except Exception as error:  # noqa: BLE001
            out_row["response"] = None
            out_row["status"] = "error"
            out_row["error"] = {"type": type(error).__name__, "message": str(error)}
        append_jsonl(args.out, out_row)
        completed.add(request_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a direct PG40 tight-budget routing prompt.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--base-url")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--model", default="pg40-direct-router")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--evaluation-id", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--max-content-chars", type=int, default=900)
    parser.add_argument("--include-prompts", action="store_true")
    parser.add_argument("--dry-run-prompts-out", type=Path)
    return parser


def main() -> None:
    run(build_parser().parse_args())


if __name__ == "__main__":
    main()
