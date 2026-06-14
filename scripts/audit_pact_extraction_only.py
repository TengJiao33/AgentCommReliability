#!/usr/bin/env python3
"""Audit deterministic answer extraction candidates over saved PACT traces."""

import argparse
import json
import re
import string
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


STOP_VERB_RE = re.compile(
    r"\b(?:is|are|was|were|has|have|had|held|served|wrote|directed|portrayed|"
    r"became|won|lost|hails|hail|can|could|will|would|should|does|do|did|"
    r"include|includes)\b",
    re.IGNORECASE,
)

CUE_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("after_answer_is", re.compile(r"(?:the answer is|answer is|final answer is)\s+([^.;,]+)", re.I)),
    ("after_position_of", re.compile(r"position of\s+([^.;,]+)", re.I)),
    (
        "after_served_as",
        re.compile(r"served as\s+([^.;,]+?)(?:\s+of\s+the\s+United States|$|[.;,])", re.I),
    ),
    ("after_hails_from", re.compile(r"hails? from\s+([^.;]+?)(?:\s+in\s+\d{4}|$|[.;])", re.I)),
    ("after_formed_in", re.compile(r"formed in\s+([^.;]+?)(?:\s+in\s+\d{4}|$|[.;])", re.I)),
    ("after_population_was", re.compile(r"population (?:was|is)\s+([\d,]+)", re.I)),
    ("after_can_seat", re.compile(r"can seat\s+([\d,]+)", re.I)),
    ("after_voted", re.compile(r"voted (?:to be |as |the )?([^.;,]+?)(?:\s+in\s+\d{4}|$|[.;,])", re.I)),
    ("after_secured", re.compile(r"secured\s+([^.;,]+?)(?:\s+and\s+|$|[.;,])", re.I)),
    ("before_wrote", re.compile(r"^(.+?)\s+wrote\b", re.I)),
    ("parenthetical_subject", re.compile(r"^([^()]{2,80}?)\s*\(")),
    ("possessive_owner", re.compile(r"^(.+?)'s\b")),
]

GENERIC_LEADS = {
    "answer",
    "battle",
    "county population",
    "father",
    "forum",
    "government position",
    "man",
    "mother",
    "people",
    "person",
    "population",
    "woman",
}

GENERIC_LEAD_FIRST_TOKENS = {
    "answer",
    "battle",
    "county",
    "father",
    "forum",
    "government",
    "man",
    "mother",
    "people",
    "person",
    "population",
    "woman",
}

MONTH_RE = re.compile(
    r"\b(?:january|february|march|april|may|june|july|august|september|"
    r"october|november|december)\b",
    re.IGNORECASE,
)


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


def clean_candidate(value: Optional[str]) -> str:
    text = (value or "").strip().strip(" .,:;()[]\"'")
    text = re.sub(r"^(yes|no)\s*,?\s+", "", text, flags=re.I)
    text = re.sub(r"^(the answer is|answer is|final answer is)\s+", "", text, flags=re.I)
    text = re.sub(r"\s+in\s+\d{4}$", "", text, flags=re.I)
    text = re.sub(r"^(the|a|an)\s+", "", text, flags=re.I)
    return text.strip(" .,:;()[]\"'")


def numeric_literals(text: Optional[str]) -> List[str]:
    return [m.group(0).replace(",", "") for m in re.finditer(r"\b\d[\d,]*(?:\.\d+)?\b", text or "")]


def is_specific_short_span(text: str) -> bool:
    tokens = normalize_answer(text).split()
    return (
        0 < len(tokens) <= 5
        and normalize_answer(text) not in GENERIC_LEADS
        and tokens[0] not in GENERIC_LEAD_FIRST_TOKENS
    )


def candidate(
    *,
    scope: str,
    turn: Any,
    stage: Optional[str],
    field: str,
    rule: str,
    text: str,
) -> Dict[str, Any]:
    return {
        "scope": scope,
        "turn": turn,
        "stage": stage,
        "field": field,
        "rule": rule,
        "text": text,
        "normalized": normalize_answer(text),
    }


def candidates_from_field(
    *,
    scope: str,
    event: Dict[str, Any],
    field: str,
) -> List[Dict[str, Any]]:
    text = event.get(field)
    if not text:
        return []

    output: List[Dict[str, Any]] = [
        candidate(
            scope=scope,
            turn=event.get("turn"),
            stage=event.get("stage"),
            field=field,
            rule="full_field",
            text=str(text).strip(),
        )
    ]

    tokens = normalize_answer(text).split()
    if tokens and tokens[0] in {"yes", "no"}:
        output.append(
            candidate(
                scope=scope,
                turn=event.get("turn"),
                stage=event.get("stage"),
                field=field,
                rule="yes_no_first_token",
                text=tokens[0],
            )
        )

    stop = STOP_VERB_RE.search(str(text))
    if stop:
        lead = clean_candidate(str(text)[: stop.start()])
        if lead:
            output.append(
                candidate(
                    scope=scope,
                    turn=event.get("turn"),
                    stage=event.get("stage"),
                    field=field,
                    rule="leading_span_before_verb",
                    text=lead,
                )
            )

    for rule, pattern in CUE_PATTERNS:
        for match in pattern.finditer(str(text)):
            value = clean_candidate(match.group(1))
            if value:
                output.append(
                    candidate(
                        scope=scope,
                        turn=event.get("turn"),
                        stage=event.get("stage"),
                        field=field,
                        rule=rule,
                        text=value,
                    )
                )

    for value in numeric_literals(str(text)):
        output.append(
            candidate(
                scope=scope,
                turn=event.get("turn"),
                stage=event.get("stage"),
                field=field,
                rule="numeric_literal",
                text=value,
            )
        )

    seen = set()
    deduped = []
    for row in output:
        key = (row["scope"], row["turn"], row["field"], row["rule"], row["normalized"])
        if row["normalized"] and key not in seen:
            seen.add(key)
            deduped.append(row)
    return deduped


def final_event(record: Dict[str, Any]) -> Dict[str, Any]:
    for event in record.get("communication_events") or []:
        if event.get("is_final"):
            return event
    events = record.get("communication_events") or []
    return events[-1] if events else {}


def collect_candidates(record: Dict[str, Any], *, scope: str) -> List[Dict[str, Any]]:
    if scope == "final_event":
        events = [final_event(record)]
    elif scope == "all_public_state":
        events = record.get("communication_events") or []
    else:
        raise ValueError(f"unknown candidate scope: {scope}")

    output: List[Dict[str, Any]] = []
    for event in events:
        for field in ("final_answer", "action_result", "environment_state"):
            output.extend(candidates_from_field(scope=scope, event=event, field=field))
    return output


def final_answer_policy(record: Dict[str, Any]) -> Dict[str, Any]:
    event = final_event(record)
    text = event.get("final_answer") or (record.get("final") or {}).get("answer") or ""
    tokens = normalize_answer(text).split()
    if tokens and tokens[0] in {"yes", "no"}:
        return candidate(
            scope="final_answer_policy",
            turn=event.get("turn"),
            stage=event.get("stage"),
            field="final_answer",
            rule="yes_no_first_token",
            text=tokens[0],
        )

    numbers = numeric_literals(text)
    if len(numbers) == 1:
        if not MONTH_RE.search(str(text)):
            return candidate(
                scope="final_answer_policy",
                turn=event.get("turn"),
                stage=event.get("stage"),
                field="final_answer",
                rule="single_numeric_literal",
                text=numbers[0],
            )

    stop = STOP_VERB_RE.search(str(text))
    if stop:
        lead = clean_candidate(str(text)[: stop.start()])
        if is_specific_short_span(lead):
            return candidate(
                scope="final_answer_policy",
                turn=event.get("turn"),
                stage=event.get("stage"),
                field="final_answer",
                rule="leading_span_before_verb",
                text=lead,
            )

    for rule in ("parenthetical_subject", "possessive_owner"):
        pattern = next(pattern for name, pattern in CUE_PATTERNS if name == rule)
        match = pattern.search(str(text))
        if match:
            value = clean_candidate(match.group(1))
            if is_specific_short_span(value):
                return candidate(
                    scope="final_answer_policy",
                    turn=event.get("turn"),
                    stage=event.get("stage"),
                    field="final_answer",
                    rule=rule,
                    text=value,
                )

    return candidate(
        scope="final_answer_policy",
        turn=event.get("turn"),
        stage=event.get("stage"),
        field="final_answer",
        rule="full_field",
        text=str(text).strip(),
    )


def matching_candidates(candidates: List[Dict[str, Any]], gold: Optional[str]) -> List[Dict[str, Any]]:
    return [row for row in candidates if exact_match(row["text"], gold)]


def audit_case(record: Dict[str, Any]) -> Dict[str, Any]:
    gold = record.get("gold_answer")
    official_correct = bool((record.get("final") or {}).get("correct"))
    final_candidates = collect_candidates(record, scope="final_event")
    all_candidates = collect_candidates(record, scope="all_public_state")
    final_matches = matching_candidates(final_candidates, gold)
    all_matches = matching_candidates(all_candidates, gold)
    policy = final_answer_policy(record)
    policy_correct = exact_match(policy["text"], gold)

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
        "final_answer_policy": policy,
        "final_answer_policy_correct": policy_correct,
        "policy_transition": (
            "stable_right"
            if official_correct and policy_correct
            else "right_to_wrong"
            if official_correct and not policy_correct
            else "wrong_to_right"
            if (not official_correct) and policy_correct
            else "stable_wrong"
        ),
        "final_event_candidate_count": len(final_candidates),
        "final_event_matching_candidates": final_matches,
        "all_public_state_candidate_count": len(all_candidates),
        "all_public_state_matching_candidates": all_matches,
        "final_event_candidate_upper_bound_correct": official_correct or bool(final_matches),
        "all_public_state_candidate_upper_bound_correct": official_correct or bool(all_matches),
    }


def summarize(cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(cases)
    official_correct = sum(1 for case in cases if case["official_correct"])
    policy_correct = sum(1 for case in cases if case["final_answer_policy_correct"])
    transitions = Counter(case["policy_transition"] for case in cases)
    final_upper = sum(1 for case in cases if case["final_event_candidate_upper_bound_correct"])
    all_upper = sum(1 for case in cases if case["all_public_state_candidate_upper_bound_correct"])
    wrong_cases = [case for case in cases if not case["official_correct"]]
    final_wrong_matches = sum(1 for case in wrong_cases if case["final_event_matching_candidates"])
    all_wrong_matches = sum(1 for case in wrong_cases if case["all_public_state_matching_candidates"])
    policy_rules = Counter(
        f"{case['final_answer_policy']['field']}:{case['final_answer_policy']['rule']}"
        for case in cases
    )
    final_match_rules: Counter[str] = Counter()
    all_match_rules: Counter[str] = Counter()
    examples_by_transition: Dict[str, List[int]] = defaultdict(list)

    for case in cases:
        if len(examples_by_transition[case["policy_transition"]]) < 8:
            examples_by_transition[case["policy_transition"]].append(case["sample_index"])
        for row in case["final_event_matching_candidates"]:
            final_match_rules[f"{row['field']}:{row['rule']}"] += 1
        for row in case["all_public_state_matching_candidates"]:
            all_match_rules[f"{row['field']}:{row['rule']}"] += 1

    return {
        "records": total,
        "official_correct": official_correct,
        "official_em": official_correct / total if total else None,
        "final_answer_policy_correct": policy_correct,
        "final_answer_policy_em": policy_correct / total if total else None,
        "final_answer_policy_transitions": dict(sorted(transitions.items())),
        "final_answer_policy_rescues": transitions.get("wrong_to_right", 0),
        "final_answer_policy_regressions": transitions.get("right_to_wrong", 0),
        "final_event_candidate_upper_bound_correct": final_upper,
        "final_event_candidate_upper_bound_em": final_upper / total if total else None,
        "final_event_wrong_cases_with_matching_candidate": final_wrong_matches,
        "all_public_state_candidate_upper_bound_correct": all_upper,
        "all_public_state_candidate_upper_bound_em": all_upper / total if total else None,
        "all_public_state_wrong_cases_with_matching_candidate": all_wrong_matches,
        "final_answer_policy_rule_counts": dict(sorted(policy_rules.items())),
        "final_event_matching_candidate_rule_counts": dict(sorted(final_match_rules.items())),
        "all_public_state_matching_candidate_rule_counts": dict(sorted(all_match_rules.items())),
        "examples_by_policy_transition": dict(sorted(examples_by_transition.items())),
        "note": (
            "Candidates are generated without gold labels, but candidate matching is evaluated "
            "against gold. Candidate upper bounds are therefore diagnostics, not deployable "
            "scores. The final-answer policy is a fixed heuristic over the saved final-answer "
            "field only."
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
