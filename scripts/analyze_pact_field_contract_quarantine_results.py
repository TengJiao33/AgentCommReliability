#!/usr/bin/env python3
"""Analyze paired deltas for the PACT field-contract quarantine run."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


DEFAULT_REFERENCE_EVALUATED = Path(
    "experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/evaluation/evaluated_rows.jsonl"
)
DEFAULT_QUARANTINE_EVALUATED = Path(
    "experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/evaluation/evaluated_rows.jsonl"
)
DEFAULT_QUARANTINE_PACKET = Path(
    "experiments/20260615-local-pact-field-contract-verifier/verified_quarantine_packet.jsonl"
)
DEFAULT_OUT_DIR = Path(
    "experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/quarantine_delta_audit"
)

REFERENCE_CONDITIONS = [
    ("base_public_state", "question_plus_public_state_no_final"),
    ("hide_public_target", "question_plus_evidence_no_target_no_final"),
    ("freeze_question_target", "frozen_target_plus_evidence_no_final"),
    ("show_final_answer_candidate", "question_plus_public_state_with_final"),
]


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def table_by_condition(rows: Iterable[Mapping[str, Any]]) -> Dict[Tuple[int, str, str], Mapping[str, Any]]:
    return {
        (int(row["sample_index"]), str(row["source_run"]), str(row["condition"])): row
        for row in rows
    }


def packet_by_unit(rows: Iterable[Mapping[str, Any]]) -> Dict[Tuple[int, str], Mapping[str, Any]]:
    return {
        (int(row["sample_index"]), str(row["source_run"])): row
        for row in rows
    }


def outcome(reference: Optional[Mapping[str, Any]], quarantine: Optional[Mapping[str, Any]]) -> str:
    if not reference or not quarantine:
        return "missing"
    ref = bool(reference.get("exact_match"))
    new = bool(quarantine.get("exact_match"))
    if not ref and new:
        return "reference_wrong_to_quarantine_right"
    if ref and not new:
        return "reference_right_to_quarantine_wrong"
    if ref and new:
        return "both_right"
    return "both_wrong"


def md_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return " ".join(text.split()).replace("|", "\\|")


def build_cards(
    *,
    reference: Mapping[Tuple[int, str, str], Mapping[str, Any]],
    quarantine: Iterable[Mapping[str, Any]],
    packet: Mapping[Tuple[int, str], Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for new_row in quarantine:
        key = (int(new_row["sample_index"]), str(new_row["source_run"]))
        packet_row = packet.get(key) or {}
        verifier = packet_row.get("verifier") or {}
        for comparison, condition in REFERENCE_CONDITIONS:
            ref_row = reference.get((key[0], key[1], condition))
            if ref_row is None:
                continue
            cards.append({
                "sample_index": key[0],
                "source_run": key[1],
                "comparison": comparison,
                "reference_condition": condition,
                "delta_outcome": outcome(ref_row, new_row),
                "reference_correct": bool(ref_row.get("exact_match")),
                "quarantine_correct": bool(new_row.get("exact_match")),
                "reference_prediction": ref_row.get("prediction"),
                "quarantine_prediction": new_row.get("prediction"),
                "gold_answer": new_row.get("gold_answer"),
                "bridge_layer": new_row.get("bridge_layer"),
                "bridge_family": new_row.get("bridge_family"),
                "target_slot_drift_candidate": bool(new_row.get("target_slot_drift_candidate")),
                "target_action": verifier.get("target_action"),
                "target_reasons": verifier.get("target_reasons") or [],
                "candidate_action": verifier.get("candidate_action"),
                "question": packet_row.get("question"),
                "action_required": (packet_row.get("public_state_input") or {}).get("action_required"),
            })
    return cards


def count_by(cards: Iterable[Mapping[str, Any]], *keys: str) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Counter[str]] = defaultdict(Counter)
    for card in cards:
        slice_key = " | ".join(str(card.get(key)) for key in keys)
        out[slice_key][str(card["delta_outcome"])] += 1
    return {
        key: dict(sorted(value.items()))
        for key, value in sorted(out.items())
    }


def summarize(cards: List[Mapping[str, Any]]) -> Dict[str, Any]:
    return {
        "comparisons": count_by(cards, "comparison"),
        "comparisons_by_source_run": count_by(cards, "comparison", "source_run"),
        "comparisons_by_bridge_layer": count_by(cards, "comparison", "bridge_layer"),
        "comparisons_by_target_action": count_by(cards, "comparison", "target_action"),
        "comparisons_by_target_candidate": count_by(cards, "comparison", "target_slot_drift_candidate"),
        "notable_cards": {
            "quarantine_rescues_vs_base": [
                card for card in cards
                if card["comparison"] == "base_public_state"
                and card["delta_outcome"] == "reference_wrong_to_quarantine_right"
            ],
            "quarantine_regressions_vs_base": [
                card for card in cards
                if card["comparison"] == "base_public_state"
                and card["delta_outcome"] == "reference_right_to_quarantine_wrong"
            ],
            "quarantine_rescues_vs_hide": [
                card for card in cards
                if card["comparison"] == "hide_public_target"
                and card["delta_outcome"] == "reference_wrong_to_quarantine_right"
            ],
            "quarantine_regressions_vs_hide": [
                card for card in cards
                if card["comparison"] == "hide_public_target"
                and card["delta_outcome"] == "reference_right_to_quarantine_wrong"
            ],
        },
    }


def render_count_table(title: str, rows: Mapping[str, Mapping[str, int]]) -> List[str]:
    outcomes = [
        "reference_wrong_to_quarantine_right",
        "reference_right_to_quarantine_wrong",
        "both_right",
        "both_wrong",
    ]
    lines = [
        f"## {title}",
        "",
        "| Slice | " + " | ".join(outcomes) + " |",
        "| --- | " + " | ".join("---:" for _ in outcomes) + " |",
    ]
    for key, counter in rows.items():
        lines.append(
            "| {key} | {values} |".format(
                key=md_cell(key),
                values=" | ".join(str(counter.get(outcome, 0)) for outcome in outcomes),
            )
        )
    lines.append("")
    return lines


def render_cards(title: str, cards: List[Mapping[str, Any]]) -> List[str]:
    lines = [f"## {title}", ""]
    if not cards:
        return lines + ["None.", ""]
    lines.append("| Sample | Source | Bridge | Target action | Gold | Reference | Quarantine |")
    lines.append("| ---: | --- | --- | --- | --- | --- | --- |")
    for card in cards[:20]:
        lines.append(
            "| {sample} | {source} | {bridge} | {target} | {gold} | {ref} | {new} |".format(
                sample=card["sample_index"],
                source=md_cell(card["source_run"]),
                bridge=md_cell(f"{card['bridge_layer']}/{card['bridge_family']}"),
                target=md_cell(card["target_action"]),
                gold=md_cell(card["gold_answer"]),
                ref=md_cell(card["reference_prediction"]),
                new=md_cell(card["quarantine_prediction"]),
            )
        )
    if len(cards) > 20:
        lines.append(f"| ... | ... | ... | ... | {len(cards) - 20} more | ... | ... |")
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = ["# PACT Field-Contract Quarantine Delta Audit", ""]
    lines.extend(render_count_table("Comparisons", summary["comparisons"]))
    lines.extend(render_count_table("By Source Run", summary["comparisons_by_source_run"]))
    lines.extend(render_count_table("By Target Action", summary["comparisons_by_target_action"]))
    notable = summary["notable_cards"]
    lines.extend(render_cards("Rescues vs Base Public State", notable["quarantine_rescues_vs_base"]))
    lines.extend(render_cards("Regressions vs Base Public State", notable["quarantine_regressions_vs_base"]))
    lines.extend(render_cards("Rescues vs Hide Public Target", notable["quarantine_rescues_vs_hide"]))
    lines.extend(render_cards("Regressions vs Hide Public Target", notable["quarantine_regressions_vs_hide"]))
    return "\n".join(lines)


def build(args: argparse.Namespace) -> Dict[str, Any]:
    reference = table_by_condition(load_jsonl(args.reference_evaluated))
    quarantine_rows = load_jsonl(args.quarantine_evaluated)
    packet = packet_by_unit(load_jsonl(args.quarantine_packet))
    cards = build_cards(reference=reference, quarantine=quarantine_rows, packet=packet)
    summary = summarize(cards)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "quarantine_delta_summary.json", summary)
    write_jsonl(args.out_dir / "quarantine_delta_cards.jsonl", cards)
    write_text(args.out_dir / "quarantine_delta_summary.md", render_markdown(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-evaluated", type=Path, default=DEFAULT_REFERENCE_EVALUATED)
    parser.add_argument("--quarantine-evaluated", type=Path, default=DEFAULT_QUARANTINE_EVALUATED)
    parser.add_argument("--quarantine-packet", type=Path, default=DEFAULT_QUARANTINE_PACKET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
