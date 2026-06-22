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


def base_evaluation_key(row: dict[str, Any]) -> str:
    base = row.get("base_evaluation_id")
    if isinstance(base, str) and base:
        return base
    evaluation_id = str(row.get("evaluation_id", ""))
    if TASK_EVALUATION_ID_MARKER in evaluation_id:
        return evaluation_id.rsplit(TASK_EVALUATION_ID_MARKER, 1)[0]
    return evaluation_id


def load_evaluation(upstream_root: Path, base_evaluation_id: str) -> dict[str, Any]:
    scenario_id, shuffle_seed = split_evaluation_id(base_evaluation_id)
    scenario_path = upstream_root / "data" / "scenarios" / f"{scenario_id}.md"
    if not scenario_path.exists():
        raise ValueError(f"unknown scenario_id: {scenario_id}")
    # The renderer returns gold fields too; this script only uses roles and fragment ids.
    return render_evaluation(scenario_path, shuffle_seed, upstream_root / "data" / "distractors")


def normalize_assignment(row: dict[str, Any], roles: list[str], fragment_ids: set[str]) -> tuple[dict[str, set[str]], str | None]:
    try:
        parsed = parse_json_object_loose(row.get("response"))
    except Exception as error:  # noqa: BLE001 - parse failures become empty votes.
        return {role: set() for role in roles}, f"{type(error).__name__}: {error}"
    normalized: dict[str, set[str]] = {role: set() for role in roles}
    for role, items in parsed.items():
        if role not in normalized or not isinstance(items, list):
            continue
        normalized[role].update(item for item in items if isinstance(item, str) and item in fragment_ids)
    return normalized, None


def load_prediction_map(paths: list[Path]) -> list[dict[str, dict[str, Any]]]:
    maps: list[dict[str, dict[str, Any]]] = []
    for path in paths:
        rows = [
            row
            for row in read_jsonl(path)
            if row.get("task") == "role_assignment"
            or str(row.get("evaluation_id", "")).endswith(f"{TASK_EVALUATION_ID_MARKER}role_assignment")
        ]
        maps.append({base_evaluation_key(row): row for row in rows})
    return maps


def combine_assignments(
    assignments: list[dict[str, set[str]]],
    roles: list[str],
    strategy: str,
    min_votes: int,
) -> dict[str, list[str]]:
    combined: dict[str, list[str]] = {}
    for role in roles:
        counts: dict[str, int] = {}
        for assignment in assignments:
            for fragment_id in assignment.get(role, set()):
                counts[fragment_id] = counts.get(fragment_id, 0) + 1
        if strategy == "union":
            threshold = 1
        elif strategy == "intersection":
            threshold = len(assignments)
        else:
            threshold = min_votes
        combined[role] = sorted(fragment_id for fragment_id, count in counts.items() if count >= threshold)
    return combined


def build_ensemble_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    upstream_root = args.upstream_root.resolve()
    prediction_maps = load_prediction_map(args.predictions)
    key_sets = [set(prediction_map) for prediction_map in prediction_maps]
    common_keys = sorted(set.intersection(*key_sets)) if key_sets else []
    if args.evaluation_id:
        requested = set(args.evaluation_id)
        common_keys = [key for key in common_keys if key in requested]
    rows: list[dict[str, Any]] = []
    for key in common_keys:
        evaluation = load_evaluation(upstream_root, key)
        roles = list(evaluation["roles"])
        fragment_ids = {fragment["id"] for fragment in evaluation["fragments"]}
        assignments: list[dict[str, set[str]]] = []
        parse_errors: list[dict[str, str]] = []
        source_models: list[str] = []
        for path, prediction_map in zip(args.predictions, prediction_maps):
            source_row = prediction_map[key]
            source_models.append(str(source_row.get("model", path.stem)))
            assignment, parse_error = normalize_assignment(source_row, roles, fragment_ids)
            assignments.append(assignment)
            if parse_error:
                parse_errors.append({"source": str(path), "error": parse_error})
        combined = combine_assignments(assignments, roles, args.strategy, args.min_votes)
        rows.append(
            {
                "evaluation_id": task_evaluation_id(evaluation["evaluation_id"], "role_assignment"),
                "base_evaluation_id": evaluation["evaluation_id"],
                "scenario_id": evaluation["scenario_id"],
                "shuffle_seed": evaluation["shuffle_seed"],
                "task": "role_assignment",
                "model": args.model_name,
                "provider": "local_no_gold_ensemble",
                "response": json.dumps(combined, ensure_ascii=False),
                "status": "ok" if not parse_errors else "parse_warning",
                "ensemble_meta": {
                    "strategy": args.strategy,
                    "min_votes": args.min_votes,
                    "source_prediction_files": [str(path) for path in args.predictions],
                    "source_models": source_models,
                    "parse_errors": parse_errors,
                },
            }
        )
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="No-gold ensemble for PerspectiveGap role-assignment predictions.")
    parser.add_argument("--predictions", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--upstream-root", type=Path, default=UPSTREAM)
    parser.add_argument("--strategy", choices=["union", "intersection", "vote"], default="union")
    parser.add_argument("--min-votes", type=int, default=2)
    parser.add_argument("--model-name", default="perspectivegap_no_gold_ensemble")
    parser.add_argument("--evaluation-id", action="append", default=[])
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.strategy == "vote" and args.min_votes < 1:
        raise SystemExit("--min-votes must be positive")
    rows = build_ensemble_rows(args)
    write_jsonl(rows, args.out)
    print(
        json.dumps(
            {
                "rows": len(rows),
                "strategy": args.strategy,
                "min_votes": args.min_votes,
                "out": str(args.out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
