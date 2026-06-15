#!/usr/bin/env python3
"""Build a compact audit packet for slot-control peer-exposure runs."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

from peer_probe.io_utils import read_jsonl, write_json, write_jsonl


INTERESTING_TRANSITIONS = {"right_to_wrong", "wrong_to_right", "stable_wrong", "unknown"}


def load_summary(run_dir: Path) -> Dict[str, Any]:
    return json.loads(run_dir.joinpath("summary.json").read_text(encoding="utf-8"))


def peer_source_answer(peer: Dict[str, Any]) -> Any:
    return peer.get("source_answer") or peer.get("answer")


def build_transition_cards(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for row in records:
        if row.get("condition") == "no_peer":
            continue
        if row.get("transition") not in INTERESTING_TRANSITIONS and row.get("post_exposure_correct") is not None:
            continue
        peer = (row.get("peer_exposure") or [{}])[0]
        cards.append(
            {
                "case_index": row.get("case_index"),
                "instance_id": row.get("instance_id"),
                "condition": row.get("condition"),
                "surface": peer.get("surface"),
                "expected_correct": peer.get("expected_correct"),
                "source_answer": peer_source_answer(peer),
                "gold_answer": row.get("gold_answer"),
                "pre_exposure_answer": row.get("pre_exposure_answer"),
                "pre_exposure_correct": row.get("pre_exposure_correct"),
                "post_exposure_answer": row.get("post_exposure_answer"),
                "post_exposure_correct": row.get("post_exposure_correct"),
                "transition": row.get("transition"),
                "peer_answer_adopted": row.get("peer_answer_adopted"),
                "peer_text": peer.get("text"),
                "post_exposure_output_excerpt": (row.get("post_exposure_output") or "")[:1200],
            }
        )
    return cards


def condition_table(summary: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    table = {}
    for condition, stats in summary["conditions"].items():
        table[condition] = {
            "records": stats.get("records", 0),
            "correct": stats.get("correct", 0),
            "unparseable": stats.get("unparseable", 0),
            "right_to_wrong": stats.get("right_to_wrong", 0),
            "wrong_to_right": stats.get("wrong_to_right", 0),
            "stable_wrong": stats.get("stable_wrong", 0),
            "stable_right": stats.get("stable_right", 0),
            "unknown": stats.get("unknown", 0),
            "peer_answer_adoption_rate": stats.get("peer_answer_adoption_rate"),
        }
    return table


def case_transition_counts(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    by_case: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in records:
        by_case[str(row.get("case_index"))][str(row.get("transition"))] += 1
    return {case: dict(counter) for case, counter in sorted(by_case.items(), key=lambda kv: int(kv[0]))}


def build_audit(run_dir: Path) -> Dict[str, Any]:
    summary = load_summary(run_dir)
    records = read_jsonl(run_dir / "peer_exposure_records.jsonl")
    cards = build_transition_cards(records)
    return {
        "run_id": summary["run_id"],
        "num_cases": summary["num_cases"],
        "num_records": summary["num_records"],
        "cases": summary["cases"],
        "condition_table": condition_table(summary),
        "interesting_card_count": len(cards),
        "case_transition_counts": case_transition_counts(records),
        "notes": [
            "Slot-control surfaces are deterministic transforms over saved peer rationales and are diagnostic, not method claims.",
            "Number-masked surfaces can create unnatural prompts; treat their harms as evidence about numeric-slot removal, not as benchmark performance.",
        ],
    }


def build(args: argparse.Namespace) -> Dict[str, Any]:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    records = read_jsonl(args.run_dir / "peer_exposure_records.jsonl")
    cards = build_transition_cards(records)
    audit = build_audit(args.run_dir)
    write_json(args.out_dir / "slot_control_audit.json", audit)
    write_jsonl(args.out_dir / "slot_transition_cards.jsonl", cards)
    return audit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=None)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.out_dir is None:
        args.out_dir = args.run_dir
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
