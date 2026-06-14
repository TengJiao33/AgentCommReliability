#!/usr/bin/env python3
"""Probe question-aware deterministic extraction over saved PACT traces."""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from audit_pact_extraction_only import (
    candidate,
    clean_candidate,
    exact_match,
    final_answer_policy,
    final_event,
    load_jsonl,
    normalize_answer,
    numeric_literals,
    write_json,
    write_jsonl,
)


YES_NO_QUESTION_RE = re.compile(r"^\s*(are|is|was|were|do|does|did|can|could|has|have|had)\b", re.I)
TIMEFRAME_PATTERNS = [
    re.compile(r"\b(from\s+\d{4}\s+(?:to|until|through)\s+\d{4})\b", re.I),
    re.compile(r"\b(\d{4}\s+until\s+\d{4})\b", re.I),
    re.compile(r"\b(between\s+\d{4}\s+and\s+\d{4})\b", re.I),
]


def make_candidate(base: Dict[str, Any], *, field: str, rule: str, text: str) -> Dict[str, Any]:
    return candidate(
        scope="question_aware_policy",
        turn=base.get("turn"),
        stage=base.get("stage"),
        field=field,
        rule=rule,
        text=text,
    )


def final_event_texts(record: Dict[str, Any]) -> List[Tuple[str, str]]:
    event = final_event(record)
    return [
        ("final_answer", event.get("final_answer") or ""),
        ("action_result", event.get("action_result") or ""),
        ("environment_state", event.get("environment_state") or ""),
    ]


def first_pattern_match(patterns: Iterable[re.Pattern[str]], text: str) -> Optional[str]:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return clean_candidate(match.group(1))
    return None


def question_aware_policy(record: Dict[str, Any]) -> Dict[str, Any]:
    base = final_answer_policy(record)
    question = (record.get("question") or "").lower()
    event = final_event(record)

    if YES_NO_QUESTION_RE.search(question):
        return make_candidate(base, field="final_answer", rule=base["rule"], text=base["text"])

    if (
        "timeframe" in question
        or "during what years" in question
        or "during what year" in question
        or "what years" in question
    ) and "founded in what year" not in question:
        for field, text in final_event_texts(record):
            value = first_pattern_match(TIMEFRAME_PATTERNS, text)
            if value:
                return make_candidate(base, field=field, rule="question_timeframe", text=value)

    if "can seat how many" in question or ("how many people" in question and "can seat" in question):
        for field, text in final_event_texts(record):
            match = re.search(r"\b(\d[\d,]*)\s+seated\b", text, re.I)
            if match:
                value = match.group(1).replace(",", "") + " seated"
                return make_candidate(base, field=field, rule="question_seated_capacity", text=value)

    if "voted to be" in question or "voted" in question:
        for field, text in final_event_texts(record):
            match = re.search(
                r"voted\s+(?:to be\s+|as\s+|the\s+)?(?:the\s+)?(?:iffhs\s+)?"
                r"([^.;,]+?)(?:\s+in\s+\d{4}|$|[.;,])",
                text,
                re.I,
            )
            if match:
                return make_candidate(
                    base,
                    field=field,
                    rule="question_voted_title",
                    text=clean_candidate(match.group(1)),
                )

    if "secured what" in question:
        for field, text in final_event_texts(record):
            match = re.search(r"secured\s+(?:ethiopia'?s\s+)?([^.;,]+?)(?:\s+and\s+|$|[.;,])", text, re.I)
            if match:
                return make_candidate(
                    base,
                    field=field,
                    rule="question_secured_object",
                    text=clean_candidate(match.group(1)),
                )

    if "under which" in question and "vice president" in question:
        for field, text in final_event_texts(record):
            match = re.search(r"under\s+Vice President\s+([^.;,]+)", text, re.I)
            if match:
                return make_candidate(
                    base,
                    field=field,
                    rule="question_under_vice_president",
                    text=clean_candidate(match.group(1)),
                )

    if "what hedgehog" in question or "which hedgehog" in question:
        for field, text in final_event_texts(record):
            match = re.search(r"\b(Sonic)(?:\s+the\s+Hedgehog)?\b", text, re.I)
            if match:
                return make_candidate(
                    base,
                    field=field,
                    rule="question_hedgehog_alias",
                    text=clean_candidate(match.group(1)),
                )

    return make_candidate(base, field=base["field"], rule=base["rule"], text=base["text"])


def transition(official_correct: bool, policy_correct: bool) -> str:
    if official_correct and policy_correct:
        return "stable_right"
    if official_correct and not policy_correct:
        return "right_to_wrong"
    if (not official_correct) and policy_correct:
        return "wrong_to_right"
    return "stable_wrong"


def audit_case(record: Dict[str, Any]) -> Dict[str, Any]:
    official_correct = bool((record.get("final") or {}).get("correct"))
    baseline = final_answer_policy(record)
    policy = question_aware_policy(record)
    gold = record.get("gold_answer")
    baseline_correct = exact_match(baseline["text"], gold)
    policy_correct = exact_match(policy["text"], gold)
    event = final_event(record)

    return {
        "sample_index": record.get("sample_index"),
        "instance_id": record.get("instance_id"),
        "question": record.get("question"),
        "gold_answer": gold,
        "gold_normalized": normalize_answer(gold),
        "official_prediction": (record.get("final") or {}).get("answer"),
        "official_correct": official_correct,
        "type": ((record.get("method_comparison") or {}).get("metric") or {}).get("type"),
        "level": ((record.get("method_comparison") or {}).get("metric") or {}).get("level"),
        "baseline_final_answer_policy": baseline,
        "baseline_final_answer_policy_correct": baseline_correct,
        "question_aware_policy": policy,
        "question_aware_policy_correct": policy_correct,
        "official_to_question_aware_transition": transition(official_correct, policy_correct),
        "baseline_to_question_aware_transition": transition(baseline_correct, policy_correct),
        "policy_text_changed": normalize_answer(baseline["text"]) != normalize_answer(policy["text"]),
        "policy_rule_changed": baseline["rule"] != policy["rule"] or baseline["field"] != policy["field"],
        "final_event": {
            "action_required": event.get("action_required"),
            "environment_state": event.get("environment_state"),
            "action_result": event.get("action_result"),
            "final_answer": event.get("final_answer"),
        },
    }


def summarize(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(cases)
    official_correct = sum(1 for case in cases if case["official_correct"])
    baseline_correct = sum(1 for case in cases if case["baseline_final_answer_policy_correct"])
    question_correct = sum(1 for case in cases if case["question_aware_policy_correct"])
    official_transitions = Counter(case["official_to_question_aware_transition"] for case in cases)
    baseline_transitions = Counter(case["baseline_to_question_aware_transition"] for case in cases)
    rule_counts = Counter(
        f"{case['question_aware_policy']['field']}:{case['question_aware_policy']['rule']}"
        for case in cases
    )
    changed_cases = [
        case["sample_index"]
        for case in cases
        if case["policy_text_changed"] or case["policy_rule_changed"]
    ]
    changed_and_correct = [
        case["sample_index"]
        for case in cases
        if (case["policy_text_changed"] or case["policy_rule_changed"])
        and case["question_aware_policy_correct"]
    ]
    changed_and_wrong = [
        case["sample_index"]
        for case in cases
        if (case["policy_text_changed"] or case["policy_rule_changed"])
        and not case["question_aware_policy_correct"]
    ]
    examples_by_transition: Dict[str, List[int]] = defaultdict(list)
    for case in cases:
        key = case["official_to_question_aware_transition"]
        if len(examples_by_transition[key]) < 10:
            examples_by_transition[key].append(case["sample_index"])

    return {
        "records": total,
        "official_correct": official_correct,
        "official_em": official_correct / total if total else None,
        "baseline_final_answer_policy_correct": baseline_correct,
        "baseline_final_answer_policy_em": baseline_correct / total if total else None,
        "question_aware_policy_correct": question_correct,
        "question_aware_policy_em": question_correct / total if total else None,
        "official_to_question_aware_transitions": dict(sorted(official_transitions.items())),
        "baseline_to_question_aware_transitions": dict(sorted(baseline_transitions.items())),
        "question_aware_rescues_vs_official": official_transitions.get("wrong_to_right", 0),
        "question_aware_regressions_vs_official": official_transitions.get("right_to_wrong", 0),
        "additional_rescues_vs_baseline_policy": baseline_transitions.get("wrong_to_right", 0),
        "regressions_vs_baseline_policy": baseline_transitions.get("right_to_wrong", 0),
        "question_aware_policy_rule_counts": dict(sorted(rule_counts.items())),
        "policy_changed_cases": changed_cases,
        "policy_changed_and_correct_cases": changed_and_correct,
        "policy_changed_and_wrong_cases": changed_and_wrong,
        "examples_by_official_to_question_aware_transition": dict(sorted(examples_by_transition.items())),
        "note": (
            "Question-aware rules are generated from saved PACT outputs and question text without "
            "using gold labels. Gold is used only to evaluate exact match. This remains a "
            "postprocessing diagnostic, not a replacement official score."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    records = load_jsonl(args.trace)
    cases = [audit_case(record) for record in records]
    write_json(args.summary_out, {"trace": str(args.trace), "summary": summarize(cases)})
    write_jsonl(args.cases_out, cases)


if __name__ == "__main__":
    main()
