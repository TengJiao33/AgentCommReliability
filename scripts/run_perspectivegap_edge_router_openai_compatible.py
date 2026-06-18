#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()


def parse_json_object_loose(text: str | None) -> dict[str, Any]:
    if text is None:
        raise ValueError("empty response")
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("response is not a JSON object")
    return parsed


def completed_requests(path: Path, model: str) -> set[str]:
    completed: set[str] = set()
    if not path.exists():
        return completed
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("model") == model and row.get("task") == "edge_router_compiled_scope" and (
            "response" in row or "error" in row
        ):
            completed.add(str(row.get("hard_evaluation_id", "")))
    return completed


def build_edge_prompt(row: dict[str, Any]) -> str:
    roles = list(row["roles"])
    lines = [
        "You are routing information fragments to roles in a multi-agent workflow.",
        "Your job is ONLY to decide role-to-fragment edges and global rejections.",
        "",
        "Rules:",
        "- Use exact fragment ids only.",
        "- A fragment may be assigned to multiple roles.",
        "- Each role should receive every fragment it needs, while staying within its budget.",
        "- The rejected list is global: include a fragment only when no listed role should receive it.",
        "- Never reject a fragment that you assign to any role.",
        "- Do not output source_id, visibility, explanations, markdown, or extra text.",
        "",
        "Roles:",
    ]
    for role in roles:
        lines.append(f"- {role}: budget {row['role_budgets'][role]} cost units")
    lines.extend(["", "Fragments:"])
    for fragment in row["fragments"]:
        lines.extend(
            [
                f"<{fragment['id']} cost=\"{fragment['cost']}\">",
                fragment["text"],
                f"</{fragment['id']}>",
                "",
            ]
        )
    schema = {
        "roles": {role: ["f?"] for role in roles},
        "rejected": ["f?"],
    }
    lines.extend(
        [
            "Return a single valid JSON object with this exact shape:",
            json.dumps(schema, ensure_ascii=False, indent=2),
        ]
    )
    return "\n".join(lines)


def normalize_fragment_ids(blob: Any) -> list[str]:
    if not isinstance(blob, list):
        return []
    out: list[str] = []
    for item in blob:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict) and isinstance(item.get("fragment_id"), str):
            out.append(item["fragment_id"])
    return out


def visibility_from_selected_roles(selected_roles: list[str], all_roles: list[str]) -> str:
    if len(selected_roles) == len(all_roles):
        return "shared_all"
    if len(selected_roles) > 1:
        return "shared_subset"
    return "role_private"


def compile_state_cards(row: dict[str, Any], edge_response: str) -> tuple[str, dict[str, Any]]:
    parsed = parse_json_object_loose(edge_response)
    role_blob = parsed.get("roles", parsed)
    if not isinstance(role_blob, dict):
        role_blob = {}
    roles = list(row["roles"])
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    selected_by_role: dict[str, list[str]] = {
        role: normalize_fragment_ids(role_blob.get(role, []))
        for role in roles
    }
    selected_roles_by_fragment: dict[str, list[str]] = {}
    for role, fragment_ids in selected_by_role.items():
        for fragment_id in fragment_ids:
            if fragment_id not in selected_roles_by_fragment:
                selected_roles_by_fragment[fragment_id] = []
            if role not in selected_roles_by_fragment[fragment_id]:
                selected_roles_by_fragment[fragment_id].append(role)

    compiled: dict[str, Any] = {"roles": {}, "rejected": []}
    for role in roles:
        cards: list[dict[str, Any]] = []
        for fragment_id in selected_by_role.get(role, []):
            fragment = fragments.get(fragment_id)
            if fragment is None:
                cards.append({"fragment_id": fragment_id, "reason": "edge_router_invalid_fragment"})
                continue
            cards.append(
                {
                    "fragment_id": fragment_id,
                    "source_id": fragment["source_id"],
                    "visibility": visibility_from_selected_roles(
                        selected_roles_by_fragment.get(fragment_id, []),
                        roles,
                    ),
                    "reason": "compiled_from_edge_router",
                }
            )
        compiled["roles"][role] = cards

    for fragment_id in normalize_fragment_ids(parsed.get("rejected", [])):
        fragment = fragments.get(fragment_id)
        if fragment is None:
            compiled["rejected"].append({"fragment_id": fragment_id, "reason": "edge_router_rejected_invalid"})
        else:
            compiled["rejected"].append(
                {
                    "fragment_id": fragment_id,
                    "source_id": fragment["source_id"],
                    "reason": "edge_router_global_reject",
                }
            )

    meta = {
        "edge_parsed": parsed,
        "selected_roles_by_fragment": selected_roles_by_fragment,
    }
    return json.dumps(compiled, ensure_ascii=False), meta


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


def filter_rows(rows: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    scenario_ids = set(args.scenario_id)
    hard_ids = set(args.hard_evaluation_id)
    if scenario_ids:
        rows = [row for row in rows if row.get("scenario_id") in scenario_ids]
    if hard_ids:
        rows = [row for row in rows if row.get("hard_evaluation_id") in hard_ids]
    if args.limit:
        rows = rows[: args.limit]
    return rows


def run(args: argparse.Namespace) -> None:
    from openai import OpenAI

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is not set")
    client = OpenAI(api_key=api_key, base_url=args.base_url)
    rows = filter_rows(read_jsonl(args.packet), args)
    completed = completed_requests(args.out, args.model)
    print(f"model={args.model}")
    print(f"packet={args.packet}")
    print(f"evaluations={len(rows)}")
    print(f"temperature={args.temperature}")
    print(f"max_tokens={args.max_tokens}")
    print(f"completed={len(completed)}")
    for index, row in enumerate(rows, start=1):
        request_id = row["hard_evaluation_id"]
        if request_id in completed:
            print(f"[{index}/{len(rows)}] skip {request_id}", flush=True)
            continue
        print(f"[{index}/{len(rows)}] edge_router {request_id}", flush=True)
        out_row = {
            "hard_evaluation_id": request_id,
            "base_evaluation_id": row["base_evaluation_id"],
            "scenario_id": row["scenario_id"],
            "shuffle_seed": row["shuffle_seed"],
            "task": "edge_router_compiled_scope",
            "model": args.model,
            "provider": "openai-compatible",
        }
        try:
            prompt = build_edge_prompt(row)
            edge_response = call_chat(client, args, prompt)
            compiled_response, meta = compile_state_cards(row, edge_response)
            out_row["edge_prompt"] = prompt if args.include_prompts else None
            out_row["edge_response"] = edge_response
            out_row["edge_meta"] = meta
            out_row["response"] = compiled_response
            out_row["status"] = "ok"
        except Exception as error:  # noqa: BLE001
            out_row["response"] = None
            out_row["status"] = "error"
            out_row["error"] = {"type": type(error).__name__, "message": str(error)}
        append_jsonl(args.out, out_row)
        completed.add(request_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a PerspectiveGap edge router and compile source/scope cards.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--scenario-id", action="append", default=[])
    parser.add_argument("--hard-evaluation-id", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--include-prompts", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run(args)


if __name__ == "__main__":
    main()
