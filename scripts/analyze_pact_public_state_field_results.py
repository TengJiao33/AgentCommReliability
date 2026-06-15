#!/usr/bin/env python3
"""Analyze condition deltas for a completed PACT public-state field packet run."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


DEFAULT_PACKET = Path("experiments/20260615-local-pact-public-state-field-packet/field_packet.jsonl")
DEFAULT_EVALUATED = Path(
    "experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/evaluation/evaluated_rows.jsonl"
)
DEFAULT_OUT_DIR = Path("experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/field_delta_audit")


BASE_CONDITION = "question_plus_public_state_no_final"
COMPARISONS = [
    (
        "hide_public_target",
        "question_plus_evidence_no_target_no_final",
        "Question and evidence are visible, but public Action Required is removed.",
    ),
    (
        "freeze_question_target",
        "frozen_target_plus_evidence_no_final",
        "Question/evidence are visible and the public target is replaced with a frozen question-derived target.",
    ),
    (
        "hide_question_keep_public_target",
        "public_target_plus_evidence_no_question_no_final",
        "Original question is hidden; only public target and evidence remain.",
    ),
    (
        "show_final_answer_candidate",
        "question_plus_public_state_with_final",
        "Final Answer Candidate is visible in addition to question, public target, and evidence.",
    ),
]


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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def packet_by_id(path: Path) -> Dict[str, Dict[str, Any]]:
    return {
        str(row["packet_id"]): row
        for row in load_jsonl(path)
    }


def merge_rows(packet: Mapping[str, Mapping[str, Any]], evaluated: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for row in evaluated:
        source = dict(packet.get(str(row["packet_id"]), {}))
        merged = dict(row)
        merged["question"] = source.get("question")
        merged["official_final_answer"] = source.get("official_final_answer")
        merged["source_final_event"] = source.get("source_final_event")
        merged["target_slot_diagnostic"] = source.get("target_slot_diagnostic")
        merged["public_state_input"] = source.get("public_state_input")
        rows.append(merged)
    return rows


def grouped_by_unit(rows: Iterable[Mapping[str, Any]]) -> Dict[Tuple[int, str], Dict[str, Mapping[str, Any]]]:
    table: Dict[Tuple[int, str], Dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in rows:
        key = (int(row["sample_index"]), str(row["source_run"]))
        table[key][str(row["condition"])] = row
    return table


def outcome(before: Optional[Mapping[str, Any]], after: Optional[Mapping[str, Any]]) -> str:
    if not before or not after:
        return "missing"
    b = bool(before.get("exact_match"))
    a = bool(after.get("exact_match"))
    if not b and a:
        return "base_wrong_to_variant_right"
    if b and not a:
        return "base_right_to_variant_wrong"
    if b and a:
        return "both_right"
    return "both_wrong"


def delta_cards(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    table = grouped_by_unit(rows)
    cards: List[Dict[str, Any]] = []
    for (sample_index, source_run), by_condition in sorted(table.items()):
        base = by_condition.get(BASE_CONDITION)
        if not base:
            continue
        for comparison_name, condition, note in COMPARISONS:
            other = by_condition.get(condition)
            if not other:
                continue
            cards.append({
                "sample_index": sample_index,
                "source_run": source_run,
                "comparison": comparison_name,
                "condition": condition,
                "comparison_note": note,
                "delta_outcome": outcome(base, other),
                "base_correct": bool(base.get("exact_match")),
                "variant_correct": bool(other.get("exact_match")),
                "base_prediction": base.get("prediction"),
                "variant_prediction": other.get("prediction"),
                "gold_answer": base.get("gold_answer"),
                "bridge_layer": base.get("bridge_layer"),
                "bridge_family": base.get("bridge_family"),
                "target_slot_drift_candidate": bool(base.get("target_slot_drift_candidate")),
                "candidate_visible": bool(other.get("candidate_visible")),
                "candidate_copy": bool(other.get("candidate_copy")),
                "candidate_correction": bool(other.get("candidate_correction")),
                "candidate_regression": bool(other.get("candidate_regression")),
                "question": base.get("question"),
                "source_final_event": base.get("source_final_event"),
                "target_slot_diagnostic": base.get("target_slot_diagnostic"),
            })
    return cards


def summarize_cards(cards: List[Mapping[str, Any]]) -> Dict[str, Any]:
    by_comparison: Dict[str, Counter[str]] = defaultdict(Counter)
    by_bridge: Dict[str, Counter[str]] = defaultdict(Counter)
    by_target_candidate: Dict[str, Counter[str]] = defaultdict(Counter)
    source_by_comparison: Dict[str, Counter[str]] = defaultdict(Counter)
    for card in cards:
        comparison = str(card["comparison"])
        outcome_name = str(card["delta_outcome"])
        by_comparison[comparison][outcome_name] += 1
        by_bridge[f"{comparison} | {card['bridge_layer']}"][outcome_name] += 1
        by_target_candidate[f"{comparison} | target_candidate={card['target_slot_drift_candidate']}"][outcome_name] += 1
        source_by_comparison[f"{comparison} | {card['source_run']}"][outcome_name] += 1

    return {
        "base_condition": BASE_CONDITION,
        "comparisons": {
            comparison: dict(sorted(counter.items()))
            for comparison, counter in sorted(by_comparison.items())
        },
        "comparisons_by_source_run": {
            key: dict(sorted(counter.items()))
            for key, counter in sorted(source_by_comparison.items())
        },
        "comparisons_by_bridge_layer": {
            key: dict(sorted(counter.items()))
            for key, counter in sorted(by_bridge.items())
        },
        "comparisons_by_target_candidate": {
            key: dict(sorted(counter.items()))
            for key, counter in sorted(by_target_candidate.items())
        },
        "notable_cards": {
            "hide_public_target_rescues": [
                card for card in cards
                if card["comparison"] == "hide_public_target"
                and card["delta_outcome"] == "base_wrong_to_variant_right"
            ],
            "freeze_question_target_rescues": [
                card for card in cards
                if card["comparison"] == "freeze_question_target"
                and card["delta_outcome"] == "base_wrong_to_variant_right"
            ],
            "public_target_only_regressions": [
                card for card in cards
                if card["comparison"] == "hide_question_keep_public_target"
                and card["delta_outcome"] == "base_right_to_variant_wrong"
            ],
            "candidate_corrections": [
                card for card in cards
                if card["comparison"] == "show_final_answer_candidate"
                and card.get("candidate_correction")
            ],
            "candidate_regressions": [
                card for card in cards
                if card["comparison"] == "show_final_answer_candidate"
                and card.get("candidate_regression")
            ],
        },
    }


def compact_card(card: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "sample_index": card["sample_index"],
        "source_run": card["source_run"],
        "bridge_layer": card["bridge_layer"],
        "bridge_family": card["bridge_family"],
        "target_slot_drift_candidate": card["target_slot_drift_candidate"],
        "gold_answer": card["gold_answer"],
        "base_prediction": card["base_prediction"],
        "variant_prediction": card["variant_prediction"],
        "delta_outcome": card["delta_outcome"],
    }


def md_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return " ".join(text.split()).replace("|", "\\|")


def render_count_table(title: str, counts: Mapping[str, Mapping[str, int]]) -> List[str]:
    outcomes = [
        "base_wrong_to_variant_right",
        "base_right_to_variant_wrong",
        "both_right",
        "both_wrong",
    ]
    lines = [
        f"## {title}",
        "",
        "| Slice | " + " | ".join(outcomes) + " |",
        "| --- | " + " | ".join("---:" for _ in outcomes) + " |",
    ]
    for key, counter in counts.items():
        lines.append(
            "| {key} | {values} |".format(
                key=key,
                values=" | ".join(str(counter.get(outcome, 0)) for outcome in outcomes),
            )
        )
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# PACT Field Packet Delta Audit",
        "",
        f"Base condition: `{summary['base_condition']}`",
        "",
    ]
    lines.extend(render_count_table("Condition Deltas", summary["comparisons"]))
    lines.extend(render_count_table("By Source Run", summary["comparisons_by_source_run"]))
    lines.extend(render_count_table("By Target Candidate", summary["comparisons_by_target_candidate"]))

    notable = summary["notable_cards"]
    sections = [
        ("Hide Public Target Rescues", "hide_public_target_rescues"),
        ("Freeze Target Rescues", "freeze_question_target_rescues"),
        ("Public Target Only Regressions", "public_target_only_regressions"),
        ("Candidate Corrections", "candidate_corrections"),
        ("Candidate Regressions", "candidate_regressions"),
    ]
    for title, key in sections:
        lines.extend([f"## {title}", ""])
        cards = [compact_card(card) for card in notable[key]]
        if not cards:
            lines.extend(["None.", ""])
            continue
        lines.append("| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |")
        lines.append("| ---: | --- | --- | --- | --- | --- | --- |")
        for card in cards[:20]:
            lines.append(
                "| {sample_index} | {source_run} | {bridge} | {target_candidate} | {gold} | {base} | {variant} |".format(
                    sample_index=card["sample_index"],
                    source_run=md_cell(card["source_run"]),
                    bridge=md_cell(f"{card['bridge_layer']}/{card['bridge_family']}"),
                    target_candidate=md_cell(card["target_slot_drift_candidate"]),
                    gold=md_cell(card["gold_answer"]),
                    base=md_cell(card["base_prediction"]),
                    variant=md_cell(card["variant_prediction"]),
                )
            )
        if len(cards) > 20:
            lines.append(f"| ... | ... | ... | ... | {len(cards) - 20} more | ... | ... |")
        lines.append("")
    return "\n".join(lines)


def build(args: argparse.Namespace) -> Dict[str, Any]:
    packet = packet_by_id(args.packet)
    evaluated = load_jsonl(args.evaluated)
    merged = merge_rows(packet, evaluated)
    cards = delta_cards(merged)
    summary = summarize_cards(cards)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "delta_summary.json", summary)
    write_jsonl(args.out_dir / "delta_cards.jsonl", cards)
    write_text(args.out_dir / "delta_summary.md", render_markdown(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--evaluated", type=Path, default=DEFAULT_EVALUATED)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
