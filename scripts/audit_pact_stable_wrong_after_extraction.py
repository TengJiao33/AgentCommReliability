#!/usr/bin/env python3
"""Classify PACT cases that remain wrong after deterministic extraction."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List


ENVIRONMENT_SIGNAL_CATEGORIES = {
    "wrong_final_environment_contains_gold_but_output_lost",
    "wrong_prior_environment_contains_gold_but_not_final",
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


def classify_stable_wrong(extraction_case: Dict[str, Any], evidence_case: Dict[str, Any]) -> str:
    final_matches = bool(extraction_case.get("final_event_matching_candidates"))
    all_matches = bool(extraction_case.get("all_public_state_matching_candidates"))
    evidence_category = evidence_case.get("category")

    if final_matches:
        return "final_event_candidate_available_policy_missed"
    if all_matches:
        return "earlier_public_state_candidate_available"
    if evidence_category in ENVIRONMENT_SIGNAL_CATEGORIES:
        return "strict_environment_signal_but_no_extraction_candidate"
    if evidence_category == "wrong_yes_no_final_polarity_mismatch_or_unclear":
        return "yes_no_polarity_mismatch"
    if evidence_category == "wrong_no_strict_gold_field_signal":
        return "no_strict_gold_field_signal"
    return "remaining_wrong_output_signal_not_recovered"


def audit_cases(
    extraction_cases: List[Dict[str, Any]],
    evidence_cases: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    evidence_by_index = {case["sample_index"]: case for case in evidence_cases}
    rows = []

    for case in extraction_cases:
        if case.get("policy_transition") != "stable_wrong":
            continue
        sample_index = case["sample_index"]
        evidence_case = evidence_by_index[sample_index]
        category = classify_stable_wrong(case, evidence_case)
        final_event = evidence_case.get("final_event") or {}
        rows.append(
            {
                "sample_index": sample_index,
                "instance_id": case.get("instance_id"),
                "question": case.get("question"),
                "type": case.get("type"),
                "level": case.get("level"),
                "gold_answer": case.get("gold_answer"),
                "official_prediction": case.get("official_prediction"),
                "final_answer_policy": case.get("final_answer_policy"),
                "stable_wrong_category": category,
                "evidence_field_category": evidence_case.get("category"),
                "final_event_matching_candidate_count": len(case.get("final_event_matching_candidates") or []),
                "all_public_state_matching_candidate_count": len(
                    case.get("all_public_state_matching_candidates") or []
                ),
                "final_event_matching_candidates": case.get("final_event_matching_candidates") or [],
                "all_public_state_matching_candidates": case.get("all_public_state_matching_candidates") or [],
                "strict_gold_signals": evidence_case.get("strict_gold_signals"),
                "relaxed_gold_signals": evidence_case.get("relaxed_gold_signals"),
                "final_event": {
                    "action_required": final_event.get("action_required"),
                    "environment_state": final_event.get("environment_state"),
                    "action_result": final_event.get("action_result"),
                    "final_answer": final_event.get("final_answer"),
                },
            }
        )
    return rows


def summarize(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    category_counts = Counter(row["stable_wrong_category"] for row in rows)
    type_counts = Counter(str(row.get("type")) for row in rows)
    category_by_type: Dict[str, Counter[str]] = defaultdict(Counter)
    examples_by_category: Dict[str, List[int]] = defaultdict(list)

    for row in rows:
        category_by_type[row["stable_wrong_category"]][str(row.get("type"))] += 1
        if len(examples_by_category[row["stable_wrong_category"]]) < 8:
            examples_by_category[row["stable_wrong_category"]].append(row["sample_index"])

    return {
        "stable_wrong_cases": len(rows),
        "category_counts": dict(sorted(category_counts.items())),
        "type_counts": dict(sorted(type_counts.items())),
        "category_by_type": {
            key: dict(sorted(value.items())) for key, value in sorted(category_by_type.items())
        },
        "examples_by_category": dict(sorted(examples_by_category.items())),
        "final_event_candidate_available_policy_missed": category_counts.get(
            "final_event_candidate_available_policy_missed", 0
        ),
        "earlier_public_state_candidate_available": category_counts.get(
            "earlier_public_state_candidate_available", 0
        ),
        "strict_environment_signal_but_no_extraction_candidate": category_counts.get(
            "strict_environment_signal_but_no_extraction_candidate", 0
        ),
        "yes_no_polarity_mismatch": category_counts.get("yes_no_polarity_mismatch", 0),
        "no_strict_gold_field_signal": category_counts.get("no_strict_gold_field_signal", 0),
        "remaining_wrong_output_signal_not_recovered": category_counts.get(
            "remaining_wrong_output_signal_not_recovered", 0
        ),
        "note": (
            "This audit only classifies official-wrong cases that remain wrong under the fixed "
            "final-answer extraction policy. Categories are diagnostics over saved outputs, "
            "not new model behavior."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extraction-cases", type=Path, required=True)
    parser.add_argument("--evidence-cases", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    extraction_cases = load_jsonl(args.extraction_cases)
    evidence_cases = load_jsonl(args.evidence_cases)
    rows = audit_cases(extraction_cases, evidence_cases)
    write_json(
        args.summary_out,
        {
            "extraction_cases": str(args.extraction_cases),
            "evidence_cases": str(args.evidence_cases),
            "summary": summarize(rows),
        },
    )
    write_jsonl(args.cases_out, rows)


if __name__ == "__main__":
    main()
