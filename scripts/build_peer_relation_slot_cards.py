#!/usr/bin/env python3
"""Build focus cards for semantic peer evidence relation-slot inspection.

This is a local audit helper. It does not call a model. It joins the latest
auto-evidence audit rows back to their source cases and downstream revision
records, then emits compact cards for the cases where peer evidence changed the
answer or exposed a notable leakage/surface issue.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_FOCUS_LABELS = {
    "correct_evidence_rescue",
    "wrong_evidence_harmful_relation",
    "wrong_evidence_recoverable_skeleton",
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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def row_key(row: Dict[str, Any]) -> Tuple[str, str, str]:
    return str(row.get("run_id")), str(row.get("case_index")), str(row.get("condition"))


def source_case_key(row: Dict[str, Any]) -> Tuple[str, str]:
    return str(row.get("run_id")), str(row.get("case_index"))


def load_run_records(run_dirs: Iterable[Path]) -> Tuple[Dict[Tuple[str, str, str], Dict[str, Any]], Dict[Tuple[str, str], Dict[str, Any]]]:
    post_records: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    source_cases: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for run_dir in run_dirs:
        for row in load_jsonl(run_dir / "peer_exposure_records.jsonl"):
            post_records[row_key(row)] = row
        for row in load_jsonl(run_dir / "source_cases.jsonl"):
            run_id = run_dir.name
            source_cases[(run_id, str(row.get("case_index")))] = row
    return post_records, source_cases


def compact_text(text: Optional[str], max_chars: int = 1200) -> str:
    value = (text or "").strip()
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 20].rstrip() + "\n...[truncated]"


def build_cards(args: argparse.Namespace) -> List[Dict[str, Any]]:
    audit_rows = load_jsonl(args.audit_cases_jsonl)
    run_dirs = [Path(path) for path in args.run_dirs]
    post_records, source_cases = load_run_records(run_dirs)
    focus_labels = set(args.focus_labels or DEFAULT_FOCUS_LABELS)
    conditions = set(args.conditions or [])
    target_behaviors = set(args.target_behaviors or [])
    case_indices = {str(case_index) for case_index in args.case_indices or []}

    cards: List[Dict[str, Any]] = []
    for row in audit_rows:
        if row.get("contact_label") not in focus_labels:
            continue
        if case_indices and str(row.get("case_index")) not in case_indices:
            continue
        if conditions and row.get("condition") not in conditions:
            continue
        if target_behaviors and row.get("target_behavior") not in target_behaviors:
            continue
        key = row_key(row)
        source_key = source_case_key(row)
        post = post_records.get(key, {})
        source = source_cases.get(source_key, {})
        peers = post.get("peer_exposure") or []
        peer = peers[0] if peers else {}
        cards.append(
            {
                "card_id": f"{row.get('case_index')}::{row.get('condition')}",
                "run_id": row.get("run_id"),
                "source_family": row.get("source_family"),
                "case_index": row.get("case_index"),
                "condition": row.get("condition"),
                "surface": row.get("surface"),
                "contact_label": row.get("contact_label"),
                "transition": row.get("transition"),
                "target_behavior": row.get("target_behavior"),
                "question": source.get("question") or post.get("question"),
                "gold_answer": row.get("gold_answer"),
                "pre_exposure_answer": row.get("pre_exposure_answer"),
                "post_exposure_answer": row.get("post_exposure_answer"),
                "source_answer": row.get("source_answer"),
                "evidence_text": row.get("evidence_text"),
                "leakage_label": row.get("leakage_label"),
                "has_blank_final_slot": row.get("has_blank_final_slot"),
                "has_final_answer_phrase": row.get("has_final_answer_phrase"),
                "numeric_tokens": row.get("numeric_tokens"),
                "source_agent_id": row.get("source_agent_id"),
                "peer_surface_text": compact_text(peer.get("text")),
                "pre_exposure_output": compact_text(post.get("pre_exposure_output"), max_chars=900),
                "post_exposure_output": compact_text(post.get("post_exposure_output"), max_chars=900),
                "source_peer_response": compact_text(
                    (source.get("correct_peer") if row.get("expected_correct") == "true" else source.get("wrong_peer") or {}).get("response"),
                    max_chars=1200,
                ),
            }
        )
    cards.sort(key=lambda item: (str(item["contact_label"]), int(item["case_index"]), str(item["condition"])))
    return cards


def write_packet(path: Path, cards: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    lines = [
        "# Peer Relation-Slot Focus Cards",
        "",
        "## Summary",
        "",
        f"- Cards: `{summary['cards']}`",
        f"- Contact labels: `{summary['contact_label_counts']}`",
        f"- Transitions: `{summary['transition_counts']}`",
        "",
        "## Cards",
        "",
    ]
    for card in cards:
        lines += [
            f"### {card['card_id']}",
            "",
            f"- Family: `{card['source_family']}`",
            f"- Condition: `{card['condition']}` / `{card['surface']}`",
            f"- Contact label: `{card['contact_label']}`",
            f"- Transition: `{card['transition']}`",
            f"- Target behavior: `{card['target_behavior']}`",
            f"- Answers: pre `{card['pre_exposure_answer']}` -> post `{card['post_exposure_answer']}`; source `{card['source_answer']}`; gold `{card['gold_answer']}`",
            f"- Leakage: `{card['leakage_label']}`; blank slot `{card['has_blank_final_slot']}`; final phrase `{card['has_final_answer_phrase']}`",
            "",
            "Question:",
            "",
            card["question"] or "",
            "",
            "Evidence text:",
            "",
            card["evidence_text"] or "",
            "",
            "Post-exposure output excerpt:",
            "",
            card["post_exposure_output"] or "",
            "",
        ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def summarize(cards: List[Dict[str, Any]], args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "audit_cases_jsonl": str(args.audit_cases_jsonl),
        "run_dirs": [str(path) for path in args.run_dirs],
        "conditions": list(args.conditions or []),
        "target_behaviors": list(args.target_behaviors or []),
        "case_indices": [str(case_index) for case_index in args.case_indices or []],
        "cards": len(cards),
        "contact_label_counts": dict(Counter(str(card.get("contact_label")) for card in cards)),
        "transition_counts": dict(Counter(str(card.get("transition")) for card in cards)),
        "target_behavior_counts": dict(Counter(str(card.get("target_behavior")) for card in cards)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-cases-jsonl", type=Path, required=True)
    parser.add_argument("--run-dirs", type=Path, nargs="+", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--focus-labels", nargs="*", default=sorted(DEFAULT_FOCUS_LABELS))
    parser.add_argument("--conditions", nargs="*", default=None)
    parser.add_argument("--target-behaviors", nargs="*", default=None)
    parser.add_argument("--case-indices", nargs="*", default=None)
    args = parser.parse_args()

    cards = build_cards(args)
    summary = summarize(cards, args)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "focus_cards.jsonl", cards)
    write_packet(args.out_dir / "focus_packet.md", cards, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
