#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


def load_renderer(perspectivegap_root: Path) -> Any:
    src = perspectivegap_root / "src"
    sys.path.insert(0, str(src))
    from perspective_gap.renderer import render_evaluation  # type: ignore

    return render_evaluation


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()


def parse_csv_values(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        out.extend(part.strip() for part in value.split(",") if part.strip())
    return out


def completed_requests(path: Path, model: str) -> set[str]:
    completed: set[str] = set()
    if not path.exists():
        return completed
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("model") == model and row.get("task") == "role_assignment" and (
            "response" in row or "error" in row
        ):
            completed.add(str(row.get("evaluation_id", "")))
    return completed


def build_evaluations(args: argparse.Namespace) -> list[dict[str, Any]]:
    render_evaluation = load_renderer(args.perspectivegap_root)
    scenarios_dir = args.perspectivegap_root / "data" / "scenarios"
    distractors_dir = args.perspectivegap_root / "data" / "distractors"
    scenario_ids = parse_csv_values(args.scenario_id)
    shuffle_seeds = args.shuffle_seed or [1]
    if not scenario_ids:
        scenario_paths = sorted(scenarios_dir.glob("*.md"))
    else:
        scenario_paths = [scenarios_dir / f"{scenario_id}.md" for scenario_id in scenario_ids]
    missing = [path.stem for path in scenario_paths if not path.exists()]
    if missing:
        raise SystemExit(f"unknown scenario_id(s): {', '.join(missing)}")
    rows: list[dict[str, Any]] = []
    for scenario_path in scenario_paths:
        for seed in shuffle_seeds:
            rows.append(render_evaluation(scenario_path, seed, distractors_dir))
    return rows


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
    from openai import OpenAI

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is not set")
    client = OpenAI(api_key=api_key, base_url=args.base_url)
    evaluations = build_evaluations(args)
    completed = completed_requests(args.out, args.model)
    total = len(evaluations)
    print(f"model={args.model}")
    print(f"evaluations={total}")
    print(f"temperature={args.temperature}")
    print(f"max_tokens={args.max_tokens}")
    print(f"completed={len(completed)}")
    for index, evaluation in enumerate(evaluations, start=1):
        request_id = f"{evaluation['evaluation_id']}__task_role_assignment"
        if request_id in completed:
            print(f"[{index}/{total}] skip {request_id}", flush=True)
            continue
        print(f"[{index}/{total}] role_assignment {request_id}", flush=True)
        row = {
            "evaluation_id": request_id,
            "base_evaluation_id": evaluation["evaluation_id"],
            "scenario_id": evaluation["scenario_id"],
            "shuffle_seed": evaluation["shuffle_seed"],
            "task": "role_assignment",
            "model": args.model,
            "provider": "openai-compatible",
        }
        try:
            row["response"] = call_chat(client, args, evaluation["role_assignment_prompt"])
            row["status"] = "ok"
        except Exception as error:  # noqa: BLE001
            row["response"] = None
            row["status"] = "error"
            row["error"] = {"type": type(error).__name__, "message": str(error)}
        append_jsonl(args.out, row)
        completed.add(request_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run PerspectiveGap role assignment through an OpenAI-compatible API.")
    parser.add_argument("--perspectivegap-root", type=Path, default=Path("baselines/PerspectiveGap/upstream"))
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--scenario-id", action="append", default=[])
    parser.add_argument("--shuffle-seed", action="append", type=int, default=[])
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--retries", type=int, default=2)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run(args)


if __name__ == "__main__":
    main()
