#!/usr/bin/env python3
"""Audit rough target-slot drift in paired PACT action-required fields."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set


STOPWORDS = {
    "a",
    "an",
    "and",
    "answer",
    "are",
    "as",
    "at",
    "based",
    "be",
    "by",
    "context",
    "did",
    "do",
    "does",
    "for",
    "from",
    "given",
    "has",
    "have",
    "how",
    "in",
    "information",
    "is",
    "it",
    "needed",
    "of",
    "on",
    "or",
    "provide",
    "question",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "what",
    "when",
    "where",
    "whether",
    "which",
    "who",
    "whom",
    "whose",
    "with",
}

TRACKED_SLOT_TERMS = {
    "album",
    "answer",
    "artist",
    "author",
    "city",
    "company",
    "conference",
    "country",
    "date",
    "director",
    "district",
    "event",
    "film",
    "founder",
    "genus",
    "location",
    "name",
    "number",
    "person",
    "population",
    "record",
    "school",
    "season",
    "singer",
    "song",
    "state",
    "team",
    "title",
    "town",
    "type",
    "year",
}

RISK_INTRODUCTIONS = {
    "borough",
    "civil",
    "district",
    "film",
    "parish",
    "song",
    "village",
}

CAPITALIZED_PHRASE_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*(?:\s+[A-Z][A-Za-z0-9]*)*\b")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
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


def normalize(text: Any) -> str:
    text = "" if text is None else str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def tokens(text: Any) -> Set[str]:
    return {
        tok for tok in normalize(text).split()
        if tok and tok not in STOPWORDS
    }


def overlap(question_tokens: Set[str], action_tokens: Set[str]) -> float:
    if not question_tokens:
        return 0.0
    return len(question_tokens & action_tokens) / len(question_tokens)


def compact_list(values: Iterable[str], limit: int = 12) -> List[str]:
    return sorted(set(values))[:limit]


def extract_anchor_phrases(question: str) -> List[str]:
    phrases = []
    seen = set()
    for match in CAPITALIZED_PHRASE_RE.findall(question):
        phrase = match.strip()
        norm = normalize(phrase)
        if not norm or norm in STOPWORDS:
            continue
        if norm in {"according"}:
            continue
        # Single capitalized words at sentence start are often just grammar.
        if " " not in phrase and question.startswith(phrase):
            continue
        if norm not in seen:
            phrases.append(phrase)
            seen.add(norm)
    return phrases


def anchor_preserved(anchor: str, action_required: str) -> bool:
    anchor_tokens = tokens(anchor)
    action_tokens = tokens(action_required)
    return bool(anchor_tokens) and anchor_tokens.issubset(action_tokens)


def final_public_target(trace: Dict[str, Any]) -> str:
    events = trace.get("communication_events") or []
    if not events:
        return ""
    final_event = events[-1] or {}
    return str(final_event.get("target_slot") or final_event.get("action_required") or "")


def event_public_targets(trace: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for event in trace.get("communication_events") or []:
        rows.append({
            "turn": event.get("turn"),
            "actor_agent_id": event.get("actor_agent_id"),
            "target_slot": event.get("target_slot"),
            "action_required": event.get("action_required"),
            "public_target": event.get("target_slot") or event.get("action_required"),
        })
    return rows


def inspect_case(
    change: Dict[str, Any],
    baseline_trace: Dict[str, Any],
    variant_trace: Dict[str, Any],
) -> Dict[str, Any]:
    question = str(change.get("question") or baseline_trace.get("question") or "")
    q_tokens = tokens(question)
    anchors = extract_anchor_phrases(question)

    baseline_ar = final_public_target(baseline_trace)
    variant_ar = final_public_target(variant_trace)
    baseline_tokens = tokens(baseline_ar)
    variant_tokens = tokens(variant_ar)

    baseline_overlap = overlap(q_tokens, baseline_tokens)
    variant_overlap = overlap(q_tokens, variant_tokens)
    baseline_anchor_losses = [
        anchor for anchor in anchors if not anchor_preserved(anchor, baseline_ar)
    ]
    variant_anchor_losses = [
        anchor for anchor in anchors if not anchor_preserved(anchor, variant_ar)
    ]
    newly_lost_anchors = [
        anchor for anchor in variant_anchor_losses
        if anchor not in baseline_anchor_losses
    ]

    question_slot_terms = q_tokens & TRACKED_SLOT_TERMS
    baseline_slot_terms = baseline_tokens & TRACKED_SLOT_TERMS
    variant_slot_terms = variant_tokens & TRACKED_SLOT_TERMS
    variant_introduced_risk_terms = (variant_tokens - q_tokens) & RISK_INTRODUCTIONS

    overlap_delta = variant_overlap - baseline_overlap
    candidate_reasons = []
    if newly_lost_anchors:
        candidate_reasons.append("new_anchor_loss")
    if overlap_delta <= -0.25:
        candidate_reasons.append("large_overlap_drop")
    if variant_overlap < 0.45 and baseline_overlap >= 0.55:
        candidate_reasons.append("low_variant_overlap")
    if question_slot_terms - variant_slot_terms and variant_introduced_risk_terms:
        candidate_reasons.append("slot_term_replacement")

    target_slot_drift_candidate = (
        not bool(change.get("variant_correct"))
        and bool(candidate_reasons)
    )

    return {
        "sample_index": change.get("sample_index"),
        "transition": change.get("transition"),
        "question": question,
        "gold_answer": change.get("gold_answer"),
        "baseline_correct": change.get("baseline_correct"),
        "variant_correct": change.get("variant_correct"),
        "baseline_final_answer_text": change.get("baseline_final_answer_text"),
        "variant_final_answer_text": change.get("variant_final_answer_text"),
        "baseline_final_action_required": baseline_ar,
        "variant_final_action_required": variant_ar,
        "baseline_final_public_target": baseline_ar,
        "variant_final_public_target": variant_ar,
        "baseline_question_overlap": round(baseline_overlap, 4),
        "variant_question_overlap": round(variant_overlap, 4),
        "overlap_delta": round(overlap_delta, 4),
        "question_terms": compact_list(q_tokens),
        "baseline_missing_question_terms": compact_list(q_tokens - baseline_tokens),
        "variant_missing_question_terms": compact_list(q_tokens - variant_tokens),
        "variant_introduced_terms": compact_list(variant_tokens - q_tokens),
        "question_slot_terms": compact_list(question_slot_terms),
        "baseline_slot_terms": compact_list(baseline_slot_terms),
        "variant_slot_terms": compact_list(variant_slot_terms),
        "variant_introduced_risk_terms": compact_list(variant_introduced_risk_terms),
        "anchor_phrases": anchors,
        "baseline_anchor_losses": baseline_anchor_losses,
        "variant_anchor_losses": variant_anchor_losses,
        "newly_lost_anchors": newly_lost_anchors,
        "candidate_reasons": candidate_reasons,
        "target_slot_drift_candidate": target_slot_drift_candidate,
        "baseline_action_requireds": event_public_targets(baseline_trace),
        "variant_action_requireds": event_public_targets(variant_trace),
        "baseline_public_targets": event_public_targets(baseline_trace),
        "variant_public_targets": event_public_targets(variant_trace),
    }


def build(args: argparse.Namespace) -> Dict[str, Any]:
    changes = load_jsonl(args.changed_cases)
    if args.focus_only:
        changes = [row for row in changes if row.get("transition") != "stable_right"]
    baseline_by_index = {
        row["sample_index"]: row
        for row in load_jsonl(args.baseline_trace)
    }
    variant_by_index = {
        row["sample_index"]: row
        for row in load_jsonl(args.variant_trace)
    }

    cases = []
    for change in changes:
        idx = change.get("sample_index")
        baseline_trace = baseline_by_index.get(idx)
        variant_trace = variant_by_index.get(idx)
        if baseline_trace and variant_trace:
            cases.append(inspect_case(change, baseline_trace, variant_trace))

    candidates = [row for row in cases if row["target_slot_drift_candidate"]]
    transitions = Counter(row["transition"] for row in cases)
    candidate_transitions = Counter(row["transition"] for row in candidates)
    reasons = Counter(
        reason for row in candidates for reason in row["candidate_reasons"]
    )
    summary = {
        "records": len(cases),
        "focus_only": args.focus_only,
        "transition_counts": dict(sorted(transitions.items())),
        "target_slot_drift_candidate_count": len(candidates),
        "target_slot_drift_candidates_by_transition": dict(sorted(candidate_transitions.items())),
        "candidate_reason_counts": dict(sorted(reasons.items())),
        "candidate_sample_indices": [row["sample_index"] for row in candidates],
        "note": (
            "This is a rough lexical diagnostic over Action Required fields, "
            "not a semantic target-preservation classifier."
        ),
    }
    write_json(args.summary_out, summary)
    write_jsonl(args.cases_out, cases)
    write_jsonl(args.candidates_out, candidates)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-trace", type=Path, required=True)
    parser.add_argument("--variant-trace", type=Path, required=True)
    parser.add_argument("--changed-cases", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, required=True)
    parser.add_argument("--candidates-out", type=Path, required=True)
    parser.add_argument("--focus-only", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
