#!/usr/bin/env python3
"""Audit PACT final-answer surface errors from unified trace records."""

import argparse
import json
import re
import string
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


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


def normalize_answer(value: Optional[str]) -> str:
    """HotpotQA-style normalization used by the PACT upstream utils."""
    if value is None:
        return ""

    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text: str) -> str:
        return " ".join(text.split())

    def remove_punc(text: str) -> str:
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    return white_space_fix(remove_articles(remove_punc(str(value).lower())))


def exact_match(prediction: Optional[str], gold: Optional[str]) -> bool:
    return normalize_answer(prediction) == normalize_answer(gold)


def final_event(record: Dict[str, Any]) -> Dict[str, Any]:
    for event in record.get("communication_events") or []:
        if event.get("is_final"):
            return event
    events = record.get("communication_events") or []
    return events[-1] if events else {}


def first_token(text: str) -> str:
    tokens = normalize_answer(text).split()
    return tokens[0] if tokens else ""


def starts_with_gold(text: Optional[str], gold: Optional[str]) -> bool:
    text_norm = normalize_answer(text)
    gold_norm = normalize_answer(gold)
    return bool(gold_norm) and (text_norm == gold_norm or text_norm.startswith(gold_norm + " "))


def contains_gold(text: Optional[str], gold: Optional[str]) -> bool:
    text_norm = normalize_answer(text)
    gold_norm = normalize_answer(gold)
    if not gold_norm:
        return False
    return text_norm == gold_norm or f" {gold_norm} " in f" {text_norm} "


def is_numeric_gold(gold: Optional[str]) -> bool:
    gold_norm = normalize_answer(gold)
    return bool(re.fullmatch(r"\d+(?:\s+\d+)*", gold_norm))


def classify_case(record: Dict[str, Any]) -> Dict[str, Any]:
    event = final_event(record)
    gold = record.get("gold_answer")
    gold_norm = normalize_answer(gold)
    official_prediction = (record.get("final") or {}).get("answer")
    official_correct = bool((record.get("final") or {}).get("correct"))
    final_answer = event.get("final_answer")
    action_result = event.get("action_result")
    metric = (record.get("method_comparison") or {}).get("metric") or {}
    official_prediction_norm = normalize_answer(official_prediction)
    final_answer_norm = normalize_answer(final_answer)
    action_result_norm = normalize_answer(action_result)

    is_yes_no = gold_norm in {"yes", "no"}
    yes_no_prefix_candidate = None
    gold_prefix_candidate = None
    numeric_candidate = None
    action_result_candidate = None
    category = "official_correct" if official_correct else "wrong_no_simple_surface_signal"

    if not official_correct and is_yes_no:
        token = first_token(final_answer or official_prediction or "")
        if token == gold_norm:
            yes_no_prefix_candidate = token
            category = "wrong_yes_no_prefix_matches_gold"

    if not official_correct and not is_yes_no and starts_with_gold(final_answer or official_prediction, gold):
        gold_prefix_candidate = gold_norm
        category = "wrong_non_yes_no_gold_prefix"

    if not official_correct and category == "wrong_no_simple_surface_signal" and is_numeric_gold(gold):
        if contains_gold(final_answer or official_prediction, gold):
            numeric_candidate = gold_norm
            category = "wrong_numeric_answer_contained"

    if not official_correct and exact_match(action_result, gold):
        action_result_candidate = action_result_norm
        category = "wrong_action_result_exact_gold"
    elif not official_correct and action_result_candidate is None and starts_with_gold(action_result, gold):
        action_result_candidate = gold_norm
        if category == "wrong_no_simple_surface_signal":
            category = "wrong_action_result_gold_prefix"

    return {
        "sample_index": record.get("sample_index"),
        "instance_id": record.get("instance_id"),
        "question": record.get("question"),
        "gold_answer": gold,
        "gold_normalized": gold_norm,
        "official_prediction": official_prediction,
        "official_prediction_normalized": official_prediction_norm,
        "official_correct": official_correct,
        "f1": metric.get("f1"),
        "type": metric.get("type"),
        "level": metric.get("level"),
        "final_answer_field": final_answer,
        "final_answer_normalized": final_answer_norm,
        "action_result_field": action_result,
        "action_result_normalized": action_result_norm,
        "environment_state": event.get("environment_state"),
        "category": category,
        "is_yes_no_gold": is_yes_no,
        "final_answer_starts_with_gold": starts_with_gold(final_answer or official_prediction, gold),
        "final_answer_contains_gold": contains_gold(final_answer or official_prediction, gold),
        "action_result_starts_with_gold": starts_with_gold(action_result, gold),
        "action_result_contains_gold": contains_gold(action_result, gold),
        "yes_no_prefix_candidate": yes_no_prefix_candidate,
        "gold_prefix_candidate": gold_prefix_candidate,
        "numeric_candidate": numeric_candidate,
        "action_result_candidate": action_result_candidate,
        "raw_prediction": metric.get("raw_prediction"),
    }


def summarize(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(cases)
    correct = sum(1 for case in cases if case["official_correct"])
    wrong = total - correct
    categories = Counter(case["category"] for case in cases)
    type_counts = Counter(str(case.get("type")) for case in cases)
    wrong_type_counts = Counter(str(case.get("type")) for case in cases if not case["official_correct"])
    f1_values = [float(case["f1"]) for case in cases if case.get("f1") is not None]
    wrong_surface_candidate = sum(
        1
        for case in cases
        if case["category"]
        in {
            "wrong_yes_no_prefix_matches_gold",
            "wrong_non_yes_no_gold_prefix",
            "wrong_numeric_answer_contained",
            "wrong_action_result_exact_gold",
            "wrong_action_result_gold_prefix",
        }
    )
    final_contains_gold_wrong = sum(
        1 for case in cases if not case["official_correct"] and case["final_answer_contains_gold"]
    )
    action_contains_gold_wrong = sum(
        1 for case in cases if not case["official_correct"] and case["action_result_contains_gold"]
    )
    return {
        "records": total,
        "official_correct": correct,
        "official_wrong": wrong,
        "official_em": correct / total if total else None,
        "category_counts": dict(sorted(categories.items())),
        "type_counts": dict(sorted(type_counts.items())),
        "wrong_type_counts": dict(sorted(wrong_type_counts.items())),
        "wrong_surface_false_negative_candidates": wrong_surface_candidate,
        "wrong_final_answer_contains_gold": final_contains_gold_wrong,
        "wrong_action_result_contains_gold": action_contains_gold_wrong,
        "f1_average": sum(f1_values) / len(f1_values) if f1_values else None,
        "note": (
            "Surface candidates are postprocessing-only diagnostics. They are not alternate "
            "official scores and do not prove the underlying evidence state was correct."
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
    cases = [classify_case(record) for record in records]
    payload = {
        "trace": str(args.trace),
        "summary": summarize(cases),
    }
    write_json(args.summary_out, payload)
    write_jsonl(args.cases_out, cases)


if __name__ == "__main__":
    main()
