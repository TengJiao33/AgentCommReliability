#!/usr/bin/env python3
"""Extract focused PACT cases for manual inspection."""

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


FOCUS_CATEGORIES = {
    "remaining_wrong_output_signal_not_recovered",
    "yes_no_polarity_mismatch",
}


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def public_turn(event: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "turn": event.get("turn"),
        "actor_agent_id": event.get("actor_agent_id"),
        "is_final": event.get("is_final"),
        "action_required": event.get("action_required"),
        "environment_state": event.get("environment_state"),
        "action_result": event.get("action_result"),
        "final_answer": event.get("final_answer"),
    }


def build_focus_cases(stable_cases: List[Dict[str, Any]], trace_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    trace_by_index = {row["sample_index"]: row for row in trace_rows}
    focus = []
    for case in stable_cases:
        category = case.get("stable_wrong_category")
        if category not in FOCUS_CATEGORIES:
            continue
        trace = trace_by_index[case["sample_index"]]
        focus.append(
            {
                "sample_index": case.get("sample_index"),
                "instance_id": case.get("instance_id"),
                "stable_wrong_category": category,
                "type": case.get("type"),
                "question": case.get("question"),
                "gold_answer": case.get("gold_answer"),
                "official_prediction": case.get("official_prediction"),
                "final_answer_policy": case.get("final_answer_policy"),
                "evidence_field_category": case.get("evidence_field_category"),
                "final_event_matching_candidate_count": case.get("final_event_matching_candidate_count"),
                "all_public_state_matching_candidate_count": case.get(
                    "all_public_state_matching_candidate_count"
                ),
                "public_turns": [public_turn(event) for event in trace.get("communication_events") or []],
            }
        )
    return focus


def summarize(focus_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    category_counts = Counter(row["stable_wrong_category"] for row in focus_cases)
    type_counts = Counter(str(row.get("type")) for row in focus_cases)
    return {
        "focus_cases": len(focus_cases),
        "sample_indices": [row["sample_index"] for row in focus_cases],
        "category_counts": dict(sorted(category_counts.items())),
        "type_counts": dict(sorted(type_counts.items())),
        "note": (
            "This pack is a mechanical extraction for manual inspection. It includes the "
            "stable-wrong cases categorized as unrecovered output signals or yes/no polarity "
            "mismatch after the fixed PACT final-answer extraction policy."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stable-cases", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    focus_cases = build_focus_cases(load_jsonl(args.stable_cases), load_jsonl(args.trace))
    write_json(
        args.summary_out,
        {
            "stable_cases": str(args.stable_cases),
            "trace": str(args.trace),
            "summary": summarize(focus_cases),
        },
    )
    write_jsonl(args.cases_out, focus_cases)


if __name__ == "__main__":
    main()
