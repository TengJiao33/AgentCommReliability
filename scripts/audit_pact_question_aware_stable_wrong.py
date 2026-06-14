#!/usr/bin/env python3
"""Classify PACT cases still wrong after question-aware extraction."""

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


def classify_case(
    question_case: Dict[str, Any],
    extraction_case: Dict[str, Any],
    evidence_case: Dict[str, Any],
) -> str:
    if extraction_case.get("final_event_matching_candidates"):
        return "final_event_candidate_available_question_policy_missed"
    if extraction_case.get("all_public_state_matching_candidates"):
        return "earlier_public_state_candidate_available_question_policy_missed"
    evidence_category = evidence_case.get("category")
    if evidence_category == "wrong_yes_no_final_polarity_mismatch_or_unclear":
        return "semantic_polarity_or_predicate_failure"
    if evidence_category in ENVIRONMENT_SIGNAL_CATEGORIES:
        return "strict_environment_signal_but_no_extraction_candidate"
    if evidence_category == "wrong_no_strict_gold_field_signal":
        return "no_strict_gold_field_signal"
    return "output_signal_not_recovered"


def audit_cases(
    question_cases: List[Dict[str, Any]],
    extraction_cases: List[Dict[str, Any]],
    evidence_cases: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    extraction_by_index = {case["sample_index"]: case for case in extraction_cases}
    evidence_by_index = {case["sample_index"]: case for case in evidence_cases}
    rows = []

    for case in question_cases:
        if case.get("official_to_question_aware_transition") != "stable_wrong":
            continue
        sample_index = case["sample_index"]
        extraction_case = extraction_by_index[sample_index]
        evidence_case = evidence_by_index[sample_index]
        category = classify_case(case, extraction_case, evidence_case)
        rows.append(
            {
                "sample_index": sample_index,
                "instance_id": case.get("instance_id"),
                "question": case.get("question"),
                "type": case.get("type"),
                "level": case.get("level"),
                "gold_answer": case.get("gold_answer"),
                "official_prediction": case.get("official_prediction"),
                "baseline_final_answer_policy": case.get("baseline_final_answer_policy"),
                "question_aware_policy": case.get("question_aware_policy"),
                "question_aware_stable_wrong_category": category,
                "evidence_field_category": evidence_case.get("category"),
                "final_event_matching_candidate_count": len(
                    extraction_case.get("final_event_matching_candidates") or []
                ),
                "all_public_state_matching_candidate_count": len(
                    extraction_case.get("all_public_state_matching_candidates") or []
                ),
                "final_event_matching_candidates": extraction_case.get(
                    "final_event_matching_candidates"
                )
                or [],
                "all_public_state_matching_candidates": extraction_case.get(
                    "all_public_state_matching_candidates"
                )
                or [],
                "strict_gold_signals": evidence_case.get("strict_gold_signals"),
                "relaxed_gold_signals": evidence_case.get("relaxed_gold_signals"),
                "final_event": case.get("final_event"),
            }
        )
    return rows


def summarize(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    categories = Counter(row["question_aware_stable_wrong_category"] for row in rows)
    type_counts = Counter(str(row.get("type")) for row in rows)
    category_by_type: Dict[str, Counter[str]] = defaultdict(Counter)
    examples_by_category: Dict[str, List[int]] = defaultdict(list)

    for row in rows:
        category = row["question_aware_stable_wrong_category"]
        category_by_type[category][str(row.get("type"))] += 1
        if len(examples_by_category[category]) < 8:
            examples_by_category[category].append(row["sample_index"])

    return {
        "question_aware_stable_wrong_cases": len(rows),
        "category_counts": dict(sorted(categories.items())),
        "type_counts": dict(sorted(type_counts.items())),
        "category_by_type": {
            key: dict(sorted(value.items())) for key, value in sorted(category_by_type.items())
        },
        "examples_by_category": dict(sorted(examples_by_category.items())),
        "final_event_candidate_available_question_policy_missed": categories.get(
            "final_event_candidate_available_question_policy_missed", 0
        ),
        "earlier_public_state_candidate_available_question_policy_missed": categories.get(
            "earlier_public_state_candidate_available_question_policy_missed", 0
        ),
        "strict_environment_signal_but_no_extraction_candidate": categories.get(
            "strict_environment_signal_but_no_extraction_candidate", 0
        ),
        "semantic_polarity_or_predicate_failure": categories.get(
            "semantic_polarity_or_predicate_failure", 0
        ),
        "no_strict_gold_field_signal": categories.get("no_strict_gold_field_signal", 0),
        "output_signal_not_recovered": categories.get("output_signal_not_recovered", 0),
        "note": (
            "This audit only classifies cases that remain wrong under the question-aware "
            "extraction probe. It joins prior extraction and evidence-field diagnostics; it "
            "does not generate model outputs."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question-aware-cases", type=Path, required=True)
    parser.add_argument("--extraction-cases", type=Path, required=True)
    parser.add_argument("--evidence-cases", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    rows = audit_cases(
        load_jsonl(args.question_aware_cases),
        load_jsonl(args.extraction_cases),
        load_jsonl(args.evidence_cases),
    )
    write_json(
        args.summary_out,
        {
            "question_aware_cases": str(args.question_aware_cases),
            "extraction_cases": str(args.extraction_cases),
            "evidence_cases": str(args.evidence_cases),
            "summary": summarize(rows),
        },
    )
    write_jsonl(args.cases_out, rows)


if __name__ == "__main__":
    main()
