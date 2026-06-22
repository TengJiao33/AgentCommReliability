#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "baselines" / "PerspectiveGap" / "upstream"
sys.path.insert(0, str(UPSTREAM / "src"))

from perspective_gap.model_runner import TASK_EVALUATION_ID_MARKER, task_evaluation_id
from perspective_gap.renderer import iter_scenario_paths, render_evaluation, write_jsonl


ARM_NAMES = (
    "official_json",
    "recall_heavy",
    "precision_guarded",
    "role_by_role",
    "matrix_then_json",
)

FORBIDDEN_PROMPT_TERMS = (
    "reference_need_sets",
    "distractor_id",
    "is_distractor",
    "expected",
    "oracle",
    "gold",
)


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()


def parse_scenario_ids(values: list[str]) -> set[str]:
    return {part.strip() for value in values for part in value.split(",") if part.strip()}


def select_scenario_paths(upstream_root: Path, scenario_ids: list[str]) -> list[Path]:
    selected = parse_scenario_ids(scenario_ids)
    paths = iter_scenario_paths(upstream_root / "data" / "scenarios")
    if not selected:
        return paths
    out = []
    for scenario_id in selected:
        path = upstream_root / "data" / "scenarios" / f"{scenario_id}.md"
        if not path.exists():
            raise SystemExit(f"unknown scenario_id: {scenario_id}")
        out.append(path)
    return sorted(out)


def load_evaluations(args: argparse.Namespace) -> list[dict[str, Any]]:
    upstream_root = args.upstream_root.resolve()
    seeds = args.shuffle_seed or [42]
    evaluations: list[dict[str, Any]] = []
    for scenario_path in select_scenario_paths(upstream_root, args.scenario_id):
        for seed in seeds:
            evaluations.append(render_evaluation(scenario_path, seed, upstream_root / "data" / "distractors"))
    if args.limit:
        evaluations = evaluations[: args.limit]
    return evaluations


def arm_suffix(arm: str) -> str:
    return f"__arm_{arm}"


def model_name(base_model: str, arm: str) -> str:
    return f"{base_model}+pg_{arm}"


def completed_requests(path: Path, model: str, arm: str) -> set[str]:
    if not path.exists():
        return set()
    completed = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("model") == model and row.get("task") == "role_assignment" and row.get("arm") == arm:
            if "response" in row or "error" in row:
                completed.add(str(row.get("evaluation_id", "")))
    return completed


def prompt_for_arm(evaluation: dict[str, Any], arm: str) -> str:
    base = evaluation["role_assignment_prompt"].strip()
    if arm == "official_json":
        return base
    if arm == "recall_heavy":
        return "\n\n".join(
            [
                base,
                "Decision policy for this run:",
                "- Favor recall: include every fragment that plausibly helps a role do its assigned job.",
                "- Still exclude generic prompt-writing advice or fragments that only belong to another role.",
                "- If a fragment is shared background needed by several roles, include it for each such role.",
                "- Return only one JSON object mapping role names to lists of fragment ids.",
            ]
        )
    if arm == "precision_guarded":
        return "\n\n".join(
            [
                base,
                "Decision policy for this run:",
                "- Favor boundary precision: include a fragment only when it is specifically needed by that role.",
                "- Do not include generic prompting tips, general best practices, or role instructions meant for a different role.",
                "- Keep shared setup only when the role cannot perform its job without it.",
                "- Return only one JSON object mapping role names to lists of fragment ids.",
            ]
        )
    if arm == "role_by_role":
        return "\n\n".join(
            [
                base,
                "Use this internal process, but do not show it:",
                "1. For the first role, identify its deliverable and required context.",
                "2. Select only fragments that directly support that role.",
                "3. Repeat independently for every role.",
                "4. Check whether any selected fragment is really for another role.",
                "Final response: only the JSON object.",
            ]
        )
    if arm == "matrix_then_json":
        return "\n\n".join(
            [
                base,
                "Use this internal process, but do not show it:",
                "- Build a hidden role-by-fragment relevance matrix.",
                "- Mark a fragment as include only if it changes that role's instructions, inputs, outputs, stopping rules, or evaluation criteria.",
                "- Mark generic prompt advice and unrelated operational guidance as exclude.",
                "- Convert the hidden matrix to the final JSON object.",
                "Final response: only the JSON object, with exact role names and fragment ids.",
            ]
        )
    raise ValueError(f"unknown arm: {arm}")


def leak_flags(prompt: str) -> list[str]:
    lowered = prompt.lower()
    return [term for term in FORBIDDEN_PROMPT_TERMS if term.lower() in lowered]


def write_dry_run(evaluations: list[dict[str, Any]], args: argparse.Namespace) -> None:
    rows: list[dict[str, Any]] = []
    for evaluation in evaluations:
        for arm in args.arm:
            prompt = prompt_for_arm(evaluation, arm)
            rows.append(
                {
                    "evaluation_id": task_evaluation_id(evaluation["evaluation_id"], "role_assignment") + arm_suffix(arm),
                    "base_evaluation_id": evaluation["evaluation_id"],
                    "scenario_id": evaluation["scenario_id"],
                    "shuffle_seed": evaluation["shuffle_seed"],
                    "task": "role_assignment",
                    "arm": arm,
                    "roles": evaluation["roles"],
                    "fragment_ids": [fragment["id"] for fragment in evaluation["fragments"]],
                    "prompt_chars": len(prompt),
                    "leak_flags": leak_flags(prompt),
                    "prompt": prompt,
                }
            )
    write_jsonl(rows, args.dry_run_prompts_out)
    leak_count = sum(1 for row in rows if row["leak_flags"])
    print(json.dumps({"rows": len(rows), "leak_flagged_rows": leak_count, "out": str(args.dry_run_prompts_out)}, indent=2))


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
        except Exception as error:  # noqa: BLE001 - retry transient endpoint errors.
            last_error = error
            status_code = getattr(error, "status_code", None) or getattr(error, "status", None)
            try:
                status_code = int(status_code) if status_code is not None else None
            except (TypeError, ValueError):
                status_code = None
            if status_code in {400, 401, 403, 404, 422} or attempt == args.retries:
                break
            time.sleep(min(4 * (2**attempt), 60))
    raise RuntimeError(f"chat completion failed after {args.retries + 1} attempts: {last_error}")


def run_model(evaluations: list[dict[str, Any]], args: argparse.Namespace) -> None:
    if len(args.arm) != 1:
        raise SystemExit("actual model calls require exactly one --arm; use dry-run for multiple arms")
    if not args.base_url or not args.out:
        raise SystemExit("provide --base-url and --out for model calls")
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is not set")
    from openai import OpenAI

    arm = args.arm[0]
    out_model = model_name(args.model, arm)
    completed = completed_requests(args.out, out_model, arm)
    client = OpenAI(api_key=api_key, base_url=args.base_url)
    print(f"model={args.model}")
    print(f"arm={arm}")
    print(f"out_model={out_model}")
    print(f"evaluations={len(evaluations)}")
    print(f"completed={len(completed)}")
    for index, evaluation in enumerate(evaluations, start=1):
        evaluation_id = task_evaluation_id(evaluation["evaluation_id"], "role_assignment")
        if evaluation_id in completed:
            print(f"[{index}/{len(evaluations)}] skip {evaluation_id}", flush=True)
            continue
        prompt = prompt_for_arm(evaluation, arm)
        row = {
            "evaluation_id": evaluation_id,
            "base_evaluation_id": evaluation["evaluation_id"],
            "scenario_id": evaluation["scenario_id"],
            "shuffle_seed": evaluation["shuffle_seed"],
            "task": "role_assignment",
            "model": out_model,
            "provider": "openai-compatible",
            "arm": arm,
            "prompt_leak_flags": leak_flags(prompt),
        }
        print(f"[{index}/{len(evaluations)}] {arm} {evaluation_id}", flush=True)
        try:
            row["response"] = call_chat(client, args, prompt)
            row["status"] = "ok"
            if args.include_prompts:
                row["prompt"] = prompt
        except Exception as error:  # noqa: BLE001 - keep failed rows for official-compatible accounting.
            row["response"] = None
            row["status"] = "error"
            row["error"] = {"type": type(error).__name__, "message": str(error)}
        append_jsonl(args.out, row)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run PerspectiveGap role-assignment prompt arms.")
    parser.add_argument("--upstream-root", type=Path, default=UPSTREAM)
    parser.add_argument("--arm", action="append", choices=ARM_NAMES, default=[])
    parser.add_argument("--scenario-id", action="append", default=[])
    parser.add_argument("--shuffle-seed", action="append", type=int, default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run-prompts-out", type=Path)
    parser.add_argument("--base-url")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--model", default="perspectivegap-role-router")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--include-prompts", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if not args.arm:
        args.arm = ["official_json"]
    evaluations = load_evaluations(args)
    if args.dry_run_prompts_out:
        write_dry_run(evaluations, args)
    else:
        run_model(evaluations, args)


if __name__ == "__main__":
    main()
