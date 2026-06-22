#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "baselines" / "PerspectiveGap" / "upstream"
sys.path.insert(0, str(UPSTREAM / "src"))

from perspective_gap.model_runner import TASK_EVALUATION_ID_MARKER, task_evaluation_id
from perspective_gap.renderer import render_evaluation, write_jsonl


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_json_object_loose(text: str | None) -> dict[str, Any]:
    if text is None:
        raise ValueError("empty response")
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("no JSON object")
        parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("response is not a JSON object")
    return parsed


def split_evaluation_id(evaluation_id: str) -> tuple[str, int]:
    if TASK_EVALUATION_ID_MARKER in evaluation_id:
        evaluation_id, _task = evaluation_id.rsplit(TASK_EVALUATION_ID_MARKER, 1)
    marker = "__seed_"
    if marker not in evaluation_id:
        raise ValueError(f"invalid evaluation_id: {evaluation_id}")
    scenario_id, seed = evaluation_id.rsplit(marker, 1)
    return scenario_id, int(seed)


def load_evaluation(upstream_root: Path, scenario_id: str, shuffle_seed: int) -> dict[str, Any]:
    scenario_path = upstream_root / "data" / "scenarios" / f"{scenario_id}.md"
    if not scenario_path.exists():
        raise ValueError(f"unknown scenario_id: {scenario_id}")
    return render_evaluation(scenario_path, shuffle_seed, upstream_root / "data" / "distractors")


def normalize_assignment(raw: dict[str, Any]) -> dict[str, list[str]]:
    normalized: dict[str, list[str]] = {}
    for role, fragment_ids in raw.items():
        if not isinstance(role, str) or not isinstance(fragment_ids, list):
            continue
        normalized[role] = sorted({fragment_id for fragment_id in fragment_ids if isinstance(fragment_id, str)})
    return normalized


def render_prompt_from_assignment(evaluation: dict[str, Any], assignment: dict[str, list[str]]) -> str:
    fragments = {fragment["id"]: fragment["text"] for fragment in evaluation["fragments"]}
    sections: list[str] = []
    for role in evaluation["roles"]:
        fragment_texts = []
        for fragment_id in assignment.get(role, []):
            text = fragments.get(fragment_id)
            if text:
                fragment_texts.append(f'<fragment id="{fragment_id}">\n{text}\n</fragment>')
        body = "\n\n".join(fragment_texts)
        sections.append(f"# {role}\n\n{body}".rstrip())
    return "\n\n".join(sections).strip()


def convert_assignment_row(row: dict[str, Any], upstream_root: Path, model_suffix: str) -> dict[str, Any]:
    base_evaluation_id = row.get("base_evaluation_id")
    if not base_evaluation_id:
        base_evaluation_id = str(row.get("evaluation_id", "")).split(TASK_EVALUATION_ID_MARKER, 1)[0]
    scenario_id = row.get("scenario_id")
    shuffle_seed = row.get("shuffle_seed")
    if scenario_id is None or shuffle_seed is None:
        scenario_id, shuffle_seed = split_evaluation_id(base_evaluation_id)
    evaluation = load_evaluation(upstream_root, str(scenario_id), int(shuffle_seed))

    out = {
        "evaluation_id": task_evaluation_id(evaluation["evaluation_id"], "prompt_writing"),
        "base_evaluation_id": evaluation["evaluation_id"],
        "scenario_id": evaluation["scenario_id"],
        "shuffle_seed": evaluation["shuffle_seed"],
        "task": "prompt_writing",
        "model": f"{row.get('model', 'unknown')}{model_suffix}",
        "provider": row.get("provider", "assignment-to-prompt"),
        "assignment_source_evaluation_id": row.get("evaluation_id"),
    }
    try:
        raw_assignment = parse_json_object_loose(row.get("response"))
        assignment = normalize_assignment(raw_assignment)
        out["response"] = render_prompt_from_assignment(evaluation, assignment)
        out["status"] = "ok"
    except Exception as error:  # noqa: BLE001 - preserve row-level conversion failures.
        out["response"] = None
        out["status"] = "error"
        out["error"] = {"type": type(error).__name__, "message": str(error)}
    return out


def iter_oracle_assignment_rows(upstream_root: Path, scenario_ids: list[str], seeds: list[int]) -> list[dict[str, Any]]:
    scenario_paths = sorted((upstream_root / "data" / "scenarios").glob("*.md"))
    selected = set(scenario_ids)
    rows: list[dict[str, Any]] = []
    for scenario_path in scenario_paths:
        scenario_id = scenario_path.stem
        if selected and scenario_id not in selected:
            continue
        for seed in seeds:
            evaluation = load_evaluation(upstream_root, scenario_id, seed)
            rows.append(
                {
                    "evaluation_id": task_evaluation_id(evaluation["evaluation_id"], "role_assignment"),
                    "base_evaluation_id": evaluation["evaluation_id"],
                    "scenario_id": evaluation["scenario_id"],
                    "shuffle_seed": evaluation["shuffle_seed"],
                    "task": "role_assignment",
                    "model": "oracle_role_assignment",
                    "provider": "local_oracle_smoke",
                    "response": json.dumps(evaluation["reference_need_sets"], ensure_ascii=False),
                    "status": "ok",
                }
            )
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert PerspectiveGap role-assignment predictions into prompt-writing predictions."
    )
    parser.add_argument("--assignments", type=Path, help="Role-assignment prediction JSONL.")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--upstream-root", type=Path, default=UPSTREAM)
    parser.add_argument("--model-suffix", default="+det_prompt_from_assignment")
    parser.add_argument("--oracle", action="store_true", help="Generate oracle assignment rows for scorer smoke only.")
    parser.add_argument("--scenario-id", action="append", default=[])
    parser.add_argument("--shuffle-seed", action="append", type=int, default=[])
    return parser


def main() -> None:
    args = build_parser().parse_args()
    upstream_root = args.upstream_root.resolve()
    if args.oracle:
        seeds = args.shuffle_seed or [1, 42]
        assignment_rows = iter_oracle_assignment_rows(upstream_root, args.scenario_id, seeds)
    else:
        if args.assignments is None:
            raise SystemExit("--assignments is required unless --oracle is set")
        assignment_rows = [
            row
            for row in read_jsonl(args.assignments)
            if row.get("task") == "role_assignment" or str(row.get("evaluation_id", "")).endswith("__task_role_assignment")
        ]
    rows = [convert_assignment_row(row, upstream_root, args.model_suffix) for row in assignment_rows]
    write_jsonl(rows, args.out)
    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status", "missing"))
        status_counts[status] = status_counts.get(status, 0) + 1
    print(json.dumps({"rows": len(rows), "status": status_counts, "out": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
