#!/usr/bin/env python3
"""Audit PACT public-state fields for gold-answer evidence signals."""

import argparse
import json
import re
import string
from collections import Counter, defaultdict
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


def normalized_tokens(value: Optional[str]) -> List[str]:
    return normalize_answer(value).split()


def relaxed_token_equal(left: str, right: str) -> bool:
    if left == right:
        return True
    if len(left) > 3 and left.endswith("s") and left[:-1] == right:
        return True
    if len(right) > 3 and right.endswith("s") and right[:-1] == left:
        return True
    return False


def contains_gold(text: Optional[str], gold: Optional[str]) -> bool:
    text_norm = normalize_answer(text)
    gold_norm = normalize_answer(gold)
    if not gold_norm:
        return False
    return text_norm == gold_norm or f" {gold_norm} " in f" {text_norm} "


def starts_with_gold(text: Optional[str], gold: Optional[str]) -> bool:
    text_norm = normalize_answer(text)
    gold_norm = normalize_answer(gold)
    return bool(gold_norm) and (text_norm == gold_norm or text_norm.startswith(gold_norm + " "))


def contains_gold_relaxed(text: Optional[str], gold: Optional[str]) -> bool:
    text_tokens = normalized_tokens(text)
    gold_tokens = normalized_tokens(gold)
    if not text_tokens or not gold_tokens or len(gold_tokens) > len(text_tokens):
        return False
    width = len(gold_tokens)
    for start in range(0, len(text_tokens) - width + 1):
        window = text_tokens[start : start + width]
        if all(relaxed_token_equal(left, right) for left, right in zip(window, gold_tokens)):
            return True
    return False


def starts_with_gold_relaxed(text: Optional[str], gold: Optional[str]) -> bool:
    text_tokens = normalized_tokens(text)
    gold_tokens = normalized_tokens(gold)
    if not text_tokens or not gold_tokens or len(gold_tokens) > len(text_tokens):
        return False
    return all(relaxed_token_equal(left, right) for left, right in zip(text_tokens, gold_tokens))


def first_token(text: Optional[str]) -> str:
    tokens = normalized_tokens(text)
    return tokens[0] if tokens else ""


def final_event(record: Dict[str, Any]) -> Dict[str, Any]:
    for event in record.get("communication_events") or []:
        if event.get("is_final"):
            return event
    events = record.get("communication_events") or []
    return events[-1] if events else {}


def stages_with_gold(
    events: List[Dict[str, Any]],
    field: str,
    gold: Optional[str],
    *,
    relaxed: bool = False,
) -> List[str]:
    predicate = contains_gold_relaxed if relaxed else contains_gold
    stages = []
    for event in events:
        if predicate(event.get(field), gold):
            stages.append(str(event.get("stage") or event.get("turn") or "unknown"))
    return stages


def classify_case(record: Dict[str, Any]) -> Dict[str, Any]:
    events = record.get("communication_events") or []
    event = final_event(record)
    gold = record.get("gold_answer")
    gold_norm = normalize_answer(gold)
    official_prediction = (record.get("final") or {}).get("answer")
    official_correct = bool((record.get("final") or {}).get("correct"))
    final_answer = event.get("final_answer") or official_prediction
    action_result = event.get("action_result")
    environment_state = event.get("environment_state")
    metric = (record.get("method_comparison") or {}).get("metric") or {}
    is_yes_no = gold_norm in {"yes", "no"}

    strict = {
        "final_answer_starts_with_gold": starts_with_gold(final_answer, gold),
        "final_answer_contains_gold": contains_gold(final_answer, gold),
        "action_result_starts_with_gold": starts_with_gold(action_result, gold),
        "action_result_contains_gold": contains_gold(action_result, gold),
        "final_environment_contains_gold": contains_gold(environment_state, gold),
        "any_environment_contains_gold": any(contains_gold(e.get("environment_state"), gold) for e in events),
        "any_action_result_contains_gold": any(contains_gold(e.get("action_result"), gold) for e in events),
    }
    strict["prior_environment_contains_gold"] = (
        strict["any_environment_contains_gold"] and not strict["final_environment_contains_gold"]
    )

    relaxed = {
        "final_answer_starts_with_gold": starts_with_gold_relaxed(final_answer, gold),
        "final_answer_contains_gold": contains_gold_relaxed(final_answer, gold),
        "action_result_starts_with_gold": starts_with_gold_relaxed(action_result, gold),
        "action_result_contains_gold": contains_gold_relaxed(action_result, gold),
        "final_environment_contains_gold": contains_gold_relaxed(environment_state, gold),
        "any_environment_contains_gold": any(
            contains_gold_relaxed(e.get("environment_state"), gold) for e in events
        ),
        "any_action_result_contains_gold": any(
            contains_gold_relaxed(e.get("action_result"), gold) for e in events
        ),
    }

    yes_no = {
        "final_answer_first_token": first_token(final_answer),
        "official_prediction_first_token": first_token(official_prediction),
        "final_polarity_matches_gold": first_token(final_answer) == gold_norm if is_yes_no else None,
    }

    if official_correct:
        category = "official_correct"
    elif is_yes_no:
        if yes_no["final_polarity_matches_gold"]:
            category = "wrong_yes_no_final_polarity_matches"
        else:
            category = "wrong_yes_no_final_polarity_mismatch_or_unclear"
    elif strict["final_answer_starts_with_gold"]:
        category = "wrong_final_answer_starts_with_gold"
    elif strict["action_result_starts_with_gold"]:
        category = "wrong_action_result_starts_with_gold"
    elif strict["final_answer_contains_gold"]:
        category = "wrong_final_answer_contains_gold_not_prefix"
    elif strict["action_result_contains_gold"]:
        category = "wrong_action_result_contains_gold_not_prefix"
    elif strict["final_environment_contains_gold"]:
        category = "wrong_final_environment_contains_gold_but_output_lost"
    elif strict["prior_environment_contains_gold"]:
        category = "wrong_prior_environment_contains_gold_but_not_final"
    else:
        category = "wrong_no_strict_gold_field_signal"

    return {
        "sample_index": record.get("sample_index"),
        "instance_id": record.get("instance_id"),
        "question": record.get("question"),
        "gold_answer": gold,
        "gold_normalized": gold_norm,
        "gold_type": "yes_no" if is_yes_no else "span_or_numeric",
        "official_prediction": official_prediction,
        "official_prediction_normalized": normalize_answer(official_prediction),
        "official_correct": official_correct,
        "f1": metric.get("f1"),
        "type": metric.get("type"),
        "level": metric.get("level"),
        "category": category,
        "final_event": {
            "stage": event.get("stage"),
            "turn": event.get("turn"),
            "actor_agent_id": event.get("actor_agent_id"),
            "action_required": event.get("action_required"),
            "environment_state": environment_state,
            "action_result": action_result,
            "final_answer": final_answer,
        },
        "strict_gold_signals": strict,
        "relaxed_gold_signals": relaxed,
        "yes_no_signals": yes_no,
        "environment_gold_stages": stages_with_gold(events, "environment_state", gold),
        "action_result_gold_stages": stages_with_gold(events, "action_result", gold),
        "environment_gold_stages_relaxed": stages_with_gold(
            events, "environment_state", gold, relaxed=True
        ),
        "action_result_gold_stages_relaxed": stages_with_gold(events, "action_result", gold, relaxed=True),
        "raw_prediction": metric.get("raw_prediction"),
    }


def summarize(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(cases)
    correct = sum(1 for case in cases if case["official_correct"])
    wrong_cases = [case for case in cases if not case["official_correct"]]
    wrong_non_yes_no = [case for case in wrong_cases if case["gold_type"] != "yes_no"]
    wrong_yes_no = [case for case in wrong_cases if case["gold_type"] == "yes_no"]
    categories = Counter(case["category"] for case in cases)
    wrong_categories = Counter(case["category"] for case in wrong_cases)
    category_by_type: Dict[str, Counter[str]] = defaultdict(Counter)
    examples_by_category: Dict[str, List[int]] = defaultdict(list)

    for case in wrong_cases:
        category_by_type[case["category"]][str(case.get("type"))] += 1
        if len(examples_by_category[case["category"]]) < 5:
            examples_by_category[case["category"]].append(case["sample_index"])

    output_signal_categories = {
        "wrong_yes_no_final_polarity_matches",
        "wrong_final_answer_starts_with_gold",
        "wrong_action_result_starts_with_gold",
        "wrong_final_answer_contains_gold_not_prefix",
        "wrong_action_result_contains_gold_not_prefix",
    }
    environment_only_categories = {
        "wrong_final_environment_contains_gold_but_output_lost",
        "wrong_prior_environment_contains_gold_but_not_final",
    }

    def count_non_yes_no_strict(signal: str) -> int:
        return sum(1 for case in wrong_non_yes_no if case["strict_gold_signals"][signal])

    def count_non_yes_no_relaxed(signal: str) -> int:
        return sum(1 for case in wrong_non_yes_no if case["relaxed_gold_signals"][signal])

    return {
        "records": total,
        "official_correct": correct,
        "official_wrong": len(wrong_cases),
        "official_em": correct / total if total else None,
        "wrong_yes_no": len(wrong_yes_no),
        "wrong_non_yes_no": len(wrong_non_yes_no),
        "category_counts": dict(sorted(categories.items())),
        "wrong_category_counts": dict(sorted(wrong_categories.items())),
        "wrong_category_by_type": {
            key: dict(sorted(value.items())) for key, value in sorted(category_by_type.items())
        },
        "examples_by_wrong_category": dict(sorted(examples_by_category.items())),
        "wrong_output_field_signal": sum(
            1 for case in wrong_cases if case["category"] in output_signal_categories
        ),
        "wrong_environment_only_signal": sum(
            1 for case in wrong_cases if case["category"] in environment_only_categories
        ),
        "wrong_no_strict_gold_field_signal": wrong_categories.get(
            "wrong_no_strict_gold_field_signal", 0
        ),
        "wrong_yes_no_final_polarity_matches": sum(
            1 for case in wrong_yes_no if case["yes_no_signals"]["final_polarity_matches_gold"]
        ),
        "wrong_yes_no_final_polarity_mismatch_or_unclear": sum(
            1
            for case in wrong_yes_no
            if not case["yes_no_signals"]["final_polarity_matches_gold"]
        ),
        "wrong_non_yes_no_final_answer_contains_gold": count_non_yes_no_strict(
            "final_answer_contains_gold"
        ),
        "wrong_non_yes_no_action_result_contains_gold": count_non_yes_no_strict(
            "action_result_contains_gold"
        ),
        "wrong_non_yes_no_final_environment_contains_gold": count_non_yes_no_strict(
            "final_environment_contains_gold"
        ),
        "wrong_non_yes_no_any_environment_contains_gold": count_non_yes_no_strict(
            "any_environment_contains_gold"
        ),
        "wrong_non_yes_no_relaxed_final_answer_contains_gold": count_non_yes_no_relaxed(
            "final_answer_contains_gold"
        ),
        "wrong_non_yes_no_relaxed_final_environment_contains_gold": count_non_yes_no_relaxed(
            "final_environment_contains_gold"
        ),
        "note": (
            "This is a field-level diagnostic over saved PACT outputs. Strict field signals use "
            "the same HotpotQA-style normalization as the PACT audit; relaxed signals only help "
            "spot simple possessive/plural surface mismatches and are not scoring rules."
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
