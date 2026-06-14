#!/usr/bin/env python3
"""Probe deterministic public-state arbitration over saved PACT traces."""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from audit_pact_extraction_only import (
    candidate,
    clean_candidate,
    collect_candidates,
    exact_match,
    final_event,
    load_jsonl,
    normalize_answer,
    numeric_literals,
    write_json,
    write_jsonl,
)
from audit_pact_question_aware_extraction import question_aware_policy, transition


FIELD_SCORE = {
    "environment_state": 4,
    "action_result": 3,
    "final_answer": 2,
}

CONTRACT_RULE_SCORES = {
    "role": {
        "after_served_as": 100,
        "after_position_of": 90,
        "leading_span_before_verb": 25,
    },
    "count": {
        "after_population_was": 100,
        "after_can_seat": 95,
        "numeric_literal": 70,
        "single_numeric_literal": 70,
    },
    "location": {
        "after_formed_in": 100,
        "after_hails_from": 75,
        "leading_span_before_verb": 10,
    },
    "time": {
        "question_timeframe": 100,
        "numeric_literal": 75,
        "single_numeric_literal": 75,
        "full_field": 35,
    },
    "entity": {
        "possessive_owner": 90,
        "parenthetical_subject": 85,
        "leading_span_before_verb": 70,
        "before_wrote": 70,
        "after_answer_is": 50,
        "full_field": 10,
    },
    "choice": {
        "possessive_owner": 90,
        "leading_span_before_verb": 75,
        "parenthetical_subject": 70,
        "after_answer_is": 50,
        "full_field": 5,
    },
    "yes_no": {
        "yes_no_first_token": 100,
        "full_field": 20,
    },
}

GENERIC_NORMALIZED = {
    "",
    "answer",
    "both",
    "county population",
    "government position",
    "it",
    "population",
    "the population",
    "woman",
}

DATE_MONTH_RE = re.compile(
    r"\b(?:january|february|march|april|may|june|july|august|september|"
    r"october|november|december)\b",
    re.I,
)
YES_NO_QUESTION_RE = re.compile(r"^\s*(are|is|was|were|do|does|did|can|could|has|have|had)\b", re.I)


def load_optional_jsonl(path: Optional[Path]) -> List[Dict[str, Any]]:
    if not path:
        return []
    return load_jsonl(path)


def final_event_texts(record: Dict[str, Any]) -> List[Tuple[str, str]]:
    event = final_event(record)
    return [
        ("final_answer", event.get("final_answer") or ""),
        ("action_result", event.get("action_result") or ""),
        ("environment_state", event.get("environment_state") or ""),
    ]


def extra_question_candidates(record: Dict[str, Any], *, scope: str) -> List[Dict[str, Any]]:
    """Add a few contract-shaped candidates not present in the generic extractor."""
    output: List[Dict[str, Any]] = []
    events = [final_event(record)] if scope == "final_event" else record.get("communication_events") or []
    question = (record.get("question") or "").lower()

    for event in events:
        for field in ("final_answer", "action_result", "environment_state"):
            text = str(event.get(field) or "")
            if not text:
                continue

            if "writer" in question or "who was" in question or "who is" in question:
                match = re.search(r"\bwas\s+([A-Z][A-Za-z.\-]+(?:\s+[A-Z][A-Za-z.\-]+){1,4})\b", text)
                if match:
                    output.append(
                        candidate(
                            scope=scope,
                            turn=event.get("turn"),
                            stage=event.get("stage"),
                            field=field,
                            rule="after_was_named_entity",
                            text=clean_candidate(match.group(1)),
                        )
                    )

            if "when" in question or "what year" in question:
                full_date = re.search(
                    r"\b((?:January|February|March|April|May|June|July|August|September|October|"
                    r"November|December)\s+\d{1,2},?\s+\d{4})\b",
                    text,
                    re.I,
                )
                if full_date:
                    output.append(
                        candidate(
                            scope=scope,
                            turn=event.get("turn"),
                            stage=event.get("stage"),
                            field=field,
                            rule="full_date",
                            text=clean_candidate(full_date.group(1)),
                        )
                    )

    return output


def candidates_for_scope(record: Dict[str, Any], *, scope: str) -> List[Dict[str, Any]]:
    rows = collect_candidates(record, scope=scope)
    rows.extend(extra_question_candidates(record, scope=scope))

    seen = set()
    deduped = []
    for row in rows:
        key = (row.get("turn"), row.get("field"), row.get("rule"), row.get("normalized"))
        if row.get("normalized") and key not in seen:
            seen.add(key)
            deduped.append(row)
    return deduped


def classify_question(question: str) -> str:
    q = question.lower().strip()
    if "what government position" in q or "government position" in q:
        return "role"
    if "how many" in q or "population" in q or "inhabitants" in q:
        return "count"
    if q.startswith("where") or "where does" in q or "hail from" in q or "hails from" in q:
        return "location"
    if q.startswith("when") or "what year" in q or "what years" in q or "during what" in q:
        return "time"
    if q.startswith("who") or "who was" in q or "who is" in q:
        return "entity"
    if q.startswith("which"):
        return "choice"
    if "founded by" in q and ("who became" in q or "known as" in q):
        return "entity"
    if YES_NO_QUESTION_RE.search(q):
        return "yes_no"
    return "open"


def candidate_is_plausible(candidate_row: Dict[str, Any], contract: str) -> bool:
    norm = candidate_row.get("normalized") or ""
    tokens = norm.split()
    rule = candidate_row.get("rule")
    text = str(candidate_row.get("text") or "")

    if norm in GENERIC_NORMALIZED:
        return False
    if not tokens:
        return False

    if contract in {"entity", "choice", "role", "location"}:
        if norm in {"yes", "no"}:
            return False
        if rule == "full_field" and len(tokens) > 7:
            return False
        if len(tokens) > 8:
            return False

    if contract == "count":
        return bool(numeric_literals(text))

    if contract == "time":
        if rule == "full_date":
            return True
        if rule in {"numeric_literal", "single_numeric_literal"}:
            return bool(re.fullmatch(r"\d{4}", norm))
        if rule == "full_field":
            return bool(DATE_MONTH_RE.search(text) and re.search(r"\b\d{4}\b", text))

    return True


def specificity_bonus(candidate_row: Dict[str, Any], contract: str) -> int:
    text = str(candidate_row.get("text") or "")
    norm = candidate_row.get("normalized") or ""
    tokens = norm.split()
    bonus = 0

    if contract == "location" and "," in text:
        bonus += 15
    if contract in {"entity", "choice", "role"} and 1 <= len(tokens) <= 4:
        bonus += 6
    if contract == "time" and candidate_row.get("rule") == "numeric_literal":
        bonus += 3
    if contract == "time" and candidate_row.get("rule") == "full_date":
        bonus += 8
    if contract == "count" and len(norm) >= 4:
        bonus += 4

    return bonus


def turn_score(candidate_row: Dict[str, Any], max_turn: int, *, scope: str) -> int:
    turn = candidate_row.get("turn")
    if not isinstance(turn, int):
        return 0
    if scope == "final_event":
        return 0
    return max(0, 4 - (max_turn - turn))


def rank_candidate(
    candidate_row: Dict[str, Any],
    *,
    contract: str,
    max_turn: int,
    scope: str,
) -> Tuple[int, int, int, int, str]:
    if not candidate_is_plausible(candidate_row, contract):
        return (-1000, 0, 0, 0, candidate_row.get("normalized") or "")

    rule_scores = CONTRACT_RULE_SCORES.get(contract, {})
    rule_score = rule_scores.get(candidate_row.get("rule"), 0)
    field_score = FIELD_SCORE.get(candidate_row.get("field"), 0)
    recency = turn_score(candidate_row, max_turn, scope=scope)
    bonus = specificity_bonus(candidate_row, contract)
    text_key = candidate_row.get("normalized") or ""
    return (rule_score + field_score + recency + bonus, rule_score, field_score, recency, text_key)


def arbitration_policy(record: Dict[str, Any], *, scope: str) -> Dict[str, Any]:
    base = question_aware_policy(record)
    contract = classify_question(record.get("question") or "")
    if contract == "open":
        output = dict(base)
        output["scope"] = f"{scope}_arbitration"
        output["contract"] = contract
        output["source"] = "question_aware_fallback"
        return output

    candidates = candidates_for_scope(record, scope=scope)
    events = record.get("communication_events") or []
    max_turn = max((event.get("turn") for event in events if isinstance(event.get("turn"), int)), default=0)
    ranked = [
        (rank_candidate(row, contract=contract, max_turn=max_turn, scope=scope), row)
        for row in candidates
    ]
    ranked = [item for item in ranked if item[0][0] > 0]
    if not ranked:
        output = dict(base)
        output["scope"] = f"{scope}_arbitration"
        output["contract"] = contract
        output["source"] = "question_aware_fallback"
        return output

    _, best = max(ranked, key=lambda item: item[0])
    output = dict(best)
    output["scope"] = f"{scope}_arbitration"
    output["contract"] = contract
    output["source"] = "public_state_ranked_candidate"
    return output


def should_try_guarded_override(base: Dict[str, Any], *, contract: str, question: str) -> bool:
    if contract in {"open", "yes_no"}:
        return False

    rule = base.get("rule")
    text = str(base.get("text") or "")
    norm = base.get("normalized") or normalize_answer(text)
    tokens = norm.split()
    q = question.lower()

    if str(rule).startswith("question_"):
        return False

    if contract == "role":
        return rule not in {"after_served_as", "after_position_of"}

    if contract == "count":
        if rule in {"after_population_was", "after_can_seat", "numeric_literal", "single_numeric_literal"}:
            return False
        return True

    if contract == "location":
        if len(tokens) <= 3 and "," not in text and rule == "full_field":
            return False
        return rule not in {"after_formed_in", "after_hails_from"}

    if contract == "entity":
        if norm in {"yes", "no"}:
            return True
        if rule == "single_numeric_literal":
            return True
        if rule == "full_field" and len(tokens) > 4:
            return True
        if "founded by" in q and rule == "yes_no_first_token":
            return True
        return False

    if contract == "choice":
        if rule == "full_field":
            return True
        if rule == "leading_span_before_verb" and "'s" in text and len(tokens) > 2:
            return True
        return False

    if contract == "time":
        if rule == "full_field" and DATE_MONTH_RE.search(text) and re.search(r"\b\d{4}\b", text):
            return True
        return False

    return False


def guarded_arbitration_policy(record: Dict[str, Any], *, scope: str) -> Dict[str, Any]:
    base = question_aware_policy(record)
    contract = classify_question(record.get("question") or "")
    if not should_try_guarded_override(base, contract=contract, question=record.get("question") or ""):
        output = dict(base)
        output["scope"] = f"guarded_{scope}_arbitration"
        output["contract"] = contract
        output["source"] = "question_aware_preserved"
        return output

    output = arbitration_policy(record, scope=scope)
    output["scope"] = f"guarded_{scope}_arbitration"
    output["source"] = "guarded_public_state_ranked_candidate"
    return output


def case_result(record: Dict[str, Any], manual_by_index: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    gold = record.get("gold_answer")
    official_correct = bool((record.get("final") or {}).get("correct"))
    question_policy = question_aware_policy(record)
    final_policy = arbitration_policy(record, scope="final_event")
    all_policy = arbitration_policy(record, scope="all_public_state")
    guarded_final_policy = guarded_arbitration_policy(record, scope="final_event")
    guarded_all_policy = guarded_arbitration_policy(record, scope="all_public_state")
    question_correct = exact_match(question_policy["text"], gold)
    final_correct = exact_match(final_policy["text"], gold)
    all_correct = exact_match(all_policy["text"], gold)
    guarded_final_correct = exact_match(guarded_final_policy["text"], gold)
    guarded_all_correct = exact_match(guarded_all_policy["text"], gold)
    sample_index = record.get("sample_index")
    manual = manual_by_index.get(sample_index, {})

    return {
        "sample_index": sample_index,
        "instance_id": record.get("instance_id"),
        "question": record.get("question"),
        "gold_answer": gold,
        "gold_normalized": normalize_answer(gold),
        "official_prediction": (record.get("final") or {}).get("answer"),
        "official_correct": official_correct,
        "type": ((record.get("method_comparison") or {}).get("metric") or {}).get("type"),
        "level": ((record.get("method_comparison") or {}).get("metric") or {}).get("level"),
        "question_contract": classify_question(record.get("question") or ""),
        "question_aware_policy": question_policy,
        "question_aware_policy_correct": question_correct,
        "final_event_arbitration_policy": final_policy,
        "final_event_arbitration_policy_correct": final_correct,
        "all_public_state_arbitration_policy": all_policy,
        "all_public_state_arbitration_policy_correct": all_correct,
        "guarded_final_event_arbitration_policy": guarded_final_policy,
        "guarded_final_event_arbitration_policy_correct": guarded_final_correct,
        "guarded_all_public_state_arbitration_policy": guarded_all_policy,
        "guarded_all_public_state_arbitration_policy_correct": guarded_all_correct,
        "question_aware_to_final_event_transition": transition(question_correct, final_correct),
        "question_aware_to_all_public_state_transition": transition(question_correct, all_correct),
        "question_aware_to_guarded_final_event_transition": transition(
            question_correct, guarded_final_correct
        ),
        "question_aware_to_guarded_all_public_state_transition": transition(
            question_correct, guarded_all_correct
        ),
        "official_to_final_event_transition": transition(official_correct, final_correct),
        "official_to_all_public_state_transition": transition(official_correct, all_correct),
        "official_to_guarded_final_event_transition": transition(official_correct, guarded_final_correct),
        "official_to_guarded_all_public_state_transition": transition(official_correct, guarded_all_correct),
        "manual_family": manual.get("manual_family"),
        "manual_label": manual.get("manual_label"),
        "final_event": {
            "action_required": final_event(record).get("action_required"),
            "environment_state": final_event(record).get("environment_state"),
            "action_result": final_event(record).get("action_result"),
            "final_answer": final_event(record).get("final_answer"),
        },
    }


def summarize_policy(cases: List[Dict[str, Any]], policy_prefix: str) -> Dict[str, Any]:
    correct_key = f"{policy_prefix}_policy_correct"
    q_transition_key = f"question_aware_to_{policy_prefix.replace('_arbitration', '')}_transition"
    official_transition_key = f"official_to_{policy_prefix.replace('_arbitration', '')}_transition"
    policy_key = f"{policy_prefix}_policy"
    total = len(cases)
    correct = sum(1 for case in cases if case[correct_key])
    q_transitions = Counter(case[q_transition_key] for case in cases)
    official_transitions = Counter(case[official_transition_key] for case in cases)
    contracts = Counter(case["question_contract"] for case in cases)
    changed_cases = [
        case["sample_index"]
        for case in cases
        if normalize_answer(case[policy_key]["text"]) != normalize_answer(case["question_aware_policy"]["text"])
    ]
    changed_and_correct = [
        case["sample_index"]
        for case in cases
        if case["sample_index"] in changed_cases and case[correct_key]
    ]
    changed_and_wrong = [
        case["sample_index"]
        for case in cases
        if case["sample_index"] in changed_cases and not case[correct_key]
    ]
    rules = Counter(
        f"{case[policy_key].get('contract')}:{case[policy_key].get('field')}:{case[policy_key].get('rule')}"
        for case in cases
    )

    return {
        "correct": correct,
        "em": correct / total if total else None,
        "question_aware_to_policy_transitions": dict(sorted(q_transitions.items())),
        "official_to_policy_transitions": dict(sorted(official_transitions.items())),
        "rescues_vs_question_aware": q_transitions.get("wrong_to_right", 0),
        "regressions_vs_question_aware": q_transitions.get("right_to_wrong", 0),
        "rescues_vs_official": official_transitions.get("wrong_to_right", 0),
        "regressions_vs_official": official_transitions.get("right_to_wrong", 0),
        "changed_cases": changed_cases,
        "changed_and_correct_cases": changed_and_correct,
        "changed_and_wrong_cases": changed_and_wrong,
        "contract_counts": dict(sorted(contracts.items())),
        "policy_rule_counts": dict(sorted(rules.items())),
    }


def summarize(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(cases)
    official_correct = sum(1 for case in cases if case["official_correct"])
    question_correct = sum(1 for case in cases if case["question_aware_policy_correct"])
    manual_focus = [case for case in cases if case.get("manual_family")]
    manual_family_counts = Counter(case["manual_family"] for case in manual_focus)
    manual_final_correct = Counter(
        case["manual_family"] for case in manual_focus if case["final_event_arbitration_policy_correct"]
    )
    manual_all_correct = Counter(
        case["manual_family"] for case in manual_focus if case["all_public_state_arbitration_policy_correct"]
    )
    manual_guarded_final_correct = Counter(
        case["manual_family"]
        for case in manual_focus
        if case["guarded_final_event_arbitration_policy_correct"]
    )
    manual_guarded_all_correct = Counter(
        case["manual_family"]
        for case in manual_focus
        if case["guarded_all_public_state_arbitration_policy_correct"]
    )

    return {
        "records": total,
        "official_correct": official_correct,
        "official_em": official_correct / total if total else None,
        "question_aware_policy_correct": question_correct,
        "question_aware_policy_em": question_correct / total if total else None,
        "final_event_arbitration": summarize_policy(cases, "final_event_arbitration"),
        "all_public_state_arbitration": summarize_policy(cases, "all_public_state_arbitration"),
        "guarded_final_event_arbitration": summarize_policy(
            cases, "guarded_final_event_arbitration"
        ),
        "guarded_all_public_state_arbitration": summarize_policy(
            cases, "guarded_all_public_state_arbitration"
        ),
        "manual_focus_cases": len(manual_focus),
        "manual_focus_family_counts": dict(sorted(manual_family_counts.items())),
        "manual_focus_final_event_correct_by_family": dict(sorted(manual_final_correct.items())),
        "manual_focus_all_public_state_correct_by_family": dict(sorted(manual_all_correct.items())),
        "manual_focus_guarded_final_event_correct_by_family": dict(
            sorted(manual_guarded_final_correct.items())
        ),
        "manual_focus_guarded_all_public_state_correct_by_family": dict(
            sorted(manual_guarded_all_correct.items())
        ),
        "note": (
            "Arbitration policies are deterministic postprocessing probes over saved PACT public "
            "fields and question text. They do not use gold labels to select outputs; gold is used "
            "only for evaluation. They are diagnostics for public-state arbitration and answer "
            "contract, not replacement official scores."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--manual-labels", type=Path)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    records = load_jsonl(args.trace)
    manual_by_index = {
        row["sample_index"]: row for row in load_optional_jsonl(args.manual_labels)
    }
    cases = [case_result(record, manual_by_index) for record in records]
    write_json(
        args.summary_out,
        {
            "trace": str(args.trace),
            "manual_labels": str(args.manual_labels) if args.manual_labels else None,
            "summary": summarize(cases),
        },
    )
    write_jsonl(args.cases_out, cases)


if __name__ == "__main__":
    main()
