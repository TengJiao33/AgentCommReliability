#!/usr/bin/env python3
"""Extract PACT field-selection focus cases for manual inspection."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List


FOCUS_CATEGORIES = {
    "final_event_candidate_available_question_policy_missed",
    "earlier_public_state_candidate_available_question_policy_missed",
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


def public_turn(event: Dict[str, Any], turn_matches: Dict[int, List[Dict[str, Any]]]) -> Dict[str, Any]:
    turn = event.get("turn")
    return {
        "turn": turn,
        "actor_agent_id": event.get("actor_agent_id"),
        "is_final": event.get("is_final"),
        "action_required": event.get("action_required"),
        "environment_state": event.get("environment_state"),
        "action_result": event.get("action_result"),
        "final_answer": event.get("final_answer"),
        "matching_candidates": turn_matches.get(turn, []),
    }


def candidates_by_turn(candidates: Iterable[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    grouped: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        turn = candidate.get("turn")
        if isinstance(turn, int):
            grouped[turn].append(candidate)
    return grouped


def build_focus_cases(stable_cases: List[Dict[str, Any]], trace_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    trace_by_index = {row["sample_index"]: row for row in trace_rows}
    focus = []

    for case in stable_cases:
        category = case.get("question_aware_stable_wrong_category")
        if category not in FOCUS_CATEGORIES:
            continue

        trace = trace_by_index[case["sample_index"]]
        all_candidates = case.get("all_public_state_matching_candidates") or []
        turn_matches = candidates_by_turn(all_candidates)

        focus.append(
            {
                "sample_index": case.get("sample_index"),
                "instance_id": case.get("instance_id"),
                "question_aware_stable_wrong_category": category,
                "type": case.get("type"),
                "level": case.get("level"),
                "question": case.get("question"),
                "gold_answer": case.get("gold_answer"),
                "official_prediction": case.get("official_prediction"),
                "baseline_final_answer_policy": case.get("baseline_final_answer_policy"),
                "question_aware_policy": case.get("question_aware_policy"),
                "evidence_field_category": case.get("evidence_field_category"),
                "final_event_matching_candidate_count": case.get("final_event_matching_candidate_count"),
                "all_public_state_matching_candidate_count": case.get(
                    "all_public_state_matching_candidate_count"
                ),
                "final_event_matching_candidates": case.get("final_event_matching_candidates") or [],
                "all_public_state_matching_candidates": all_candidates,
                "strict_gold_signals": case.get("strict_gold_signals"),
                "relaxed_gold_signals": case.get("relaxed_gold_signals"),
                "final_event": case.get("final_event"),
                "public_turns": [
                    public_turn(event, turn_matches) for event in trace.get("communication_events") or []
                ],
            }
        )

    return focus


def summarize(focus_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    category_counts = Counter(row["question_aware_stable_wrong_category"] for row in focus_cases)
    type_counts = Counter(str(row.get("type")) for row in focus_cases)
    question_policy_fields = Counter(
        (row.get("question_aware_policy") or {}).get("field", "missing") for row in focus_cases
    )
    question_policy_rules = Counter(
        (row.get("question_aware_policy") or {}).get("rule", "missing") for row in focus_cases
    )
    matching_candidate_fields = Counter()
    matching_candidate_rules = Counter()

    for row in focus_cases:
        for candidate in row.get("all_public_state_matching_candidates") or []:
            matching_candidate_fields[candidate.get("field", "missing")] += 1
            matching_candidate_rules[candidate.get("rule", "missing")] += 1

    return {
        "focus_cases": len(focus_cases),
        "sample_indices": [row["sample_index"] for row in focus_cases],
        "category_counts": dict(sorted(category_counts.items())),
        "type_counts": dict(sorted(type_counts.items())),
        "question_policy_fields": dict(sorted(question_policy_fields.items())),
        "question_policy_rules": dict(sorted(question_policy_rules.items())),
        "matching_candidate_fields": dict(sorted(matching_candidate_fields.items())),
        "matching_candidate_rules": dict(sorted(matching_candidate_rules.items())),
        "note": (
            "This pack mechanically extracts the question-aware stable-wrong PACT cases "
            "where a gold-matching candidate appears in the final action-state event or "
            "only in earlier/wider public state. It is for manual case-contact only and "
            "does not change model behavior or scoring."
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
