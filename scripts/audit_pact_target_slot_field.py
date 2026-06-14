#!/usr/bin/env python3
"""Audit Target Slot field compliance and stability in PACT traces."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Set


STOPWORDS = {
    "a",
    "an",
    "and",
    "answer",
    "for",
    "from",
    "in",
    "of",
    "on",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
}

GENERIC_TARGETS = {
    "",
    "answer",
    "the answer",
    "provide answer",
    "provide the answer",
    "final answer",
    "none",
    "n a",
    "unknown",
}


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
        token
        for token in normalize(text).split()
        if token and token not in STOPWORDS
    }


def overlap(question: str, target_slot: str) -> float:
    q_tokens = tokens(question)
    t_tokens = tokens(target_slot)
    if not q_tokens:
        return 0.0
    return len(q_tokens & t_tokens) / len(q_tokens)


def is_generic(target_slot: Any) -> bool:
    norm = normalize(target_slot)
    if norm in GENERIC_TARGETS:
        return True
    target_tokens = tokens(norm)
    return not target_tokens


def audit_record(row: Dict[str, Any]) -> Dict[str, Any]:
    events = row.get("communication_events") or []
    target_slots = [event.get("target_slot") for event in events]
    normalized = [normalize(value) for value in target_slots if normalize(value)]
    unique = sorted(set(normalized))
    final_target_slot = target_slots[-1] if target_slots else None
    question = row.get("question") or ""
    return {
        "sample_index": row.get("sample_index"),
        "question": question,
        "gold_answer": row.get("gold_answer"),
        "final_correct": row.get("final", {}).get("correct"),
        "event_count": len(events),
        "target_slot_count": sum(1 for value in target_slots if normalize(value)),
        "target_slots": target_slots,
        "unique_target_slots": unique,
        "unique_target_slot_count": len(unique),
        "all_turns_have_target_slot": bool(events)
        and all(bool(normalize(value)) for value in target_slots),
        "target_slot_stable": len(unique) == 1,
        "final_target_slot": final_target_slot,
        "final_target_slot_words": len(str(final_target_slot or "").split()),
        "final_target_slot_generic": is_generic(final_target_slot),
        "final_target_question_overlap": round(overlap(question, str(final_target_slot or "")), 4),
    }


def build(args: argparse.Namespace) -> Dict[str, Any]:
    records = [audit_record(row) for row in load_jsonl(args.trace)]
    total = len(records)
    event_total = sum(row["event_count"] for row in records)
    target_slot_total = sum(row["target_slot_count"] for row in records)
    summary = {
        "trace": str(args.trace),
        "records": total,
        "events": event_total,
        "events_with_target_slot": target_slot_total,
        "event_target_slot_rate": target_slot_total / event_total if event_total else None,
        "records_all_turns_have_target_slot": sum(
            1 for row in records if row["all_turns_have_target_slot"]
        ),
        "records_with_stable_target_slot": sum(
            1 for row in records if row["target_slot_stable"]
        ),
        "records_with_generic_final_target_slot": sum(
            1 for row in records if row["final_target_slot_generic"]
        ),
        "avg_final_target_slot_words": mean(
            row["final_target_slot_words"] for row in records
        )
        if records
        else None,
        "avg_unique_target_slot_count": mean(
            row["unique_target_slot_count"] for row in records
        )
        if records
        else None,
        "avg_final_target_question_overlap": mean(
            row["final_target_question_overlap"] for row in records
        )
        if records
        else None,
    }
    write_json(args.summary_out, summary)
    write_jsonl(args.cases_out, records)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
