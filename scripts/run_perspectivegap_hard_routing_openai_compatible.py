#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
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


def completed_requests(path: Path, model: str) -> set[str]:
    completed: set[str] = set()
    if not path.exists():
        return completed
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("model") == model and row.get("task") == "hard_routing" and (
            "response" in row or "error" in row
        ):
            completed.add(str(row.get("hard_evaluation_id", "")))
    return completed


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
        print(f"[{index}/{len(rows)}] hard_routing {request_id}", flush=True)
        out_row = {
            "hard_evaluation_id": request_id,
            "base_evaluation_id": row["base_evaluation_id"],
            "scenario_id": row["scenario_id"],
            "shuffle_seed": row["shuffle_seed"],
            "task": "hard_routing",
            "model": args.model,
            "provider": "openai-compatible",
        }
        try:
            out_row["response"] = call_chat(client, args, row["hard_routing_prompt"])
            out_row["status"] = "ok"
        except Exception as error:  # noqa: BLE001
            out_row["response"] = None
            out_row["status"] = "error"
            out_row["error"] = {"type": type(error).__name__, "message": str(error)}
        append_jsonl(args.out, out_row)
        completed.add(request_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run PerspectiveGap hard-routing prompts through an OpenAI-compatible API.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--scenario-id", action="append", default=[])
    parser.add_argument("--hard-evaluation-id", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1536)
    parser.add_argument("--retries", type=int, default=2)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run(args)


if __name__ == "__main__":
    main()
