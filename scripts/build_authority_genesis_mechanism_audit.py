#!/usr/bin/env python3
"""Build mechanism-audit cards for the Authority Genesis Ladder run."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_EVALUATED = Path(
    "experiments/20260615-2318-a8002-authority-genesis-ladder-qwen25-14b/evaluation/evaluated_rows.jsonl"
)
DEFAULT_DELTAS = Path(
    "experiments/20260615-2318-a8002-authority-genesis-ladder-qwen25-14b/evaluation/paired_deltas.jsonl"
)
DEFAULT_PACKET = Path("experiments/20260615-local-authority-genesis-ladder-packet/authority_genesis_ladder_packet.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260615-local-authority-genesis-ladder-mechanism-audit")


REFUSAL_MARKERS = [
    "does not contain",
    "does not provide",
    "cannot be accurately answered",
    "not enough information",
    "insufficient information",
    "provided information only",
    "given context does not",
]

RELATION_FAMILIES = {
    "public_target_misdirection",
    "evidence_sentence_or_distractor",
    "question_root_boundary_regression",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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


def row_key(row: Mapping[str, Any]) -> tuple[str, str]:
    return (str(row.get("case_id")), str(row.get("variant")))


def has_refusal_drift(text: Any) -> bool:
    lower = str(text or "").lower()
    return any(marker in lower for marker in REFUSAL_MARKERS)


def copy_kind(row: Mapping[str, Any]) -> str:
    if row.get("prediction_equals_injected"):
        return "exact_injected_copy"
    if row.get("prediction_injected_substring") or float(row.get("prediction_injected_f1") or 0.0) >= 0.8:
        return "partial_or_surface_overlap"
    return "no_direct_copy"


def mechanism_seed(row: Mapping[str, Any]) -> tuple[str, list[str]]:
    semantic = str(row.get("semantic_family"))
    polarity = str(row.get("content_polarity"))
    variant_prediction = row.get("variant_prediction")
    mechanisms: list[str] = []

    if row.get("prediction_equals_injected"):
        if polarity == "wrong_lure":
            mechanisms.append("exact_lure_copy")
        elif polarity == "correct_gold":
            mechanisms.append("exact_gold_copy")
        else:
            mechanisms.append("exact_injected_content_copy")
    elif row.get("prediction_injected_substring") or float(row.get("prediction_injected_f1") or 0.0) >= 0.8:
        mechanisms.append("partial_lure_or_surface_copy")

    if has_refusal_drift(variant_prediction):
        mechanisms.append("refusal_or_insufficient_evidence_drift")
    if semantic == "answer_type_projection":
        mechanisms.append("answer_contract_shift")
    if semantic == "short_span_or_granularity":
        mechanisms.append("short_span_or_granularity")
    if semantic in RELATION_FAMILIES:
        mechanisms.append("relation_or_entity_role_switch")
    if semantic == "final_candidate_attractor" and "refusal_or_insufficient_evidence_drift" not in mechanisms:
        mechanisms.append("final_candidate_contract_disturbance")
    if bool(row.get("authority_violation")) and float(row.get("variant_f1") or 0.0) >= 0.8:
        mechanisms.append("strict_output_contract_violation")

    if has_refusal_drift(variant_prediction):
        primary = "refusal_or_insufficient_evidence_drift"
    elif semantic == "answer_type_projection":
        primary = "answer_contract_surface_uptake"
    elif semantic == "short_span_or_granularity":
        primary = "short_span_or_granularity_uptake"
    elif semantic in RELATION_FAMILIES:
        primary = "relation_or_entity_role_uptake"
    elif row.get("prediction_equals_injected"):
        if polarity == "wrong_lure":
            primary = "exact_lure_copy"
        elif polarity == "correct_gold":
            primary = "exact_gold_copy"
        else:
            primary = "exact_injected_content_copy"
    else:
        primary = "other_contract_disturbance"

    return primary, sorted(set(mechanisms))


def compact_public_state(packet_row: Mapping[str, Any]) -> dict[str, Any]:
    state = packet_row.get("base_public_state_input") or {}
    return {
        "question": state.get("question") or packet_row.get("question"),
        "environment_state": state.get("environment_state"),
        "action_result": state.get("action_result"),
    }


def make_card(
    delta: Mapping[str, Any],
    evaluated_by_key: Mapping[tuple[str, str], Mapping[str, Any]],
    packet_by_key: Mapping[tuple[str, str], Mapping[str, Any]],
    event_type: str,
) -> dict[str, Any]:
    evaluated = evaluated_by_key.get(row_key(delta), {})
    packet = packet_by_key.get(row_key(delta), {})
    primary, mechanisms = mechanism_seed(delta)
    return {
        "event_type": event_type,
        "case_id": delta.get("case_id"),
        "variant": delta.get("variant"),
        "sample_index": evaluated.get("sample_index"),
        "source_run": evaluated.get("source_run"),
        "source_type": delta.get("source_type"),
        "semantic_family": delta.get("semantic_family"),
        "bridge_layer": delta.get("bridge_layer"),
        "bridge_family": delta.get("bridge_family"),
        "future_signal": delta.get("future_signal"),
        "future_level": delta.get("future_level"),
        "content_polarity": delta.get("content_polarity"),
        "injected_visible_to_model": delta.get("injected_visible_to_model"),
        "injected_content_source": delta.get("injected_content_source"),
        "injected_content": evaluated.get("injected_content"),
        "question": evaluated.get("question") or packet.get("question"),
        "gold_answer": evaluated.get("gold_answer"),
        "base_prediction": delta.get("base_prediction"),
        "variant_prediction": delta.get("variant_prediction"),
        "base_f1": delta.get("base_f1"),
        "variant_f1": delta.get("variant_f1"),
        "f1_delta": delta.get("f1_delta"),
        "prediction_equals_injected": delta.get("prediction_equals_injected"),
        "prediction_injected_substring": delta.get("prediction_injected_substring"),
        "prediction_injected_f1": delta.get("prediction_injected_f1"),
        "copy_kind": copy_kind(delta),
        "primary_mechanism_seed": primary,
        "mechanism_seed_labels": mechanisms,
        "base_public_state_input": compact_public_state(packet),
        "prompt": packet.get("prompt"),
        "caveat": "Mechanism labels are deterministic seed labels for audit triage, not population claims.",
    }


def nested_counts(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> dict[str, dict[str, int]]:
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        out[str(row.get(outer))][str(row.get(inner))] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(out.items())}


def summarize_cards(cards: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "records": len(cards),
        "future_signal_counts": dict(sorted(Counter(str(row.get("future_signal")) for row in cards).items())),
        "semantic_family_counts": dict(sorted(Counter(str(row.get("semantic_family")) for row in cards).items())),
        "copy_kind_counts": dict(sorted(Counter(str(row.get("copy_kind")) for row in cards).items())),
        "primary_mechanism_seed_counts": dict(
            sorted(Counter(str(row.get("primary_mechanism_seed")) for row in cards).items())
        ),
        "primary_mechanism_by_future_signal": nested_counts(cards, "future_signal", "primary_mechanism_seed"),
        "copy_kind_by_future_signal": nested_counts(cards, "future_signal", "copy_kind"),
        "strict_output_contract_violation_count": sum(
            1 for row in cards if "strict_output_contract_violation" in (row.get("mechanism_seed_labels") or [])
        ),
    }


def md_cell(value: Any) -> str:
    return " ".join(("" if value is None else str(value)).split()).replace("|", "\\|")


def render_cards_table(cards: list[Mapping[str, Any]], limit: int = 24) -> list[str]:
    lines = [
        "| Case | Signal | Primary seed | Copy kind | Gold | Base | Variant | Injected |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in cards[:limit]:
        lines.append(
            "| {case} | {signal} | {primary} | {copy} | {gold} | {base} | {variant} | {injected} |".format(
                case=md_cell(row.get("case_id")),
                signal=md_cell(row.get("future_signal")),
                primary=md_cell(row.get("primary_mechanism_seed")),
                copy=md_cell(row.get("copy_kind")),
                gold=md_cell(row.get("gold_answer")),
                base=md_cell(row.get("base_prediction")),
                variant=md_cell(row.get("variant_prediction")),
                injected=md_cell(row.get("injected_content")),
            )
        )
    return lines


def render_markdown(summary: Mapping[str, Any], violation_cards: list[Mapping[str, Any]], utility_cards: list[Mapping[str, Any]]) -> str:
    lines = [
        "# Authority Genesis Ladder Mechanism Audit",
        "",
        "This audit extracts behavior-changing rows from the first Authority Genesis Ladder run.",
        "Mechanism labels are deterministic seed labels for inspection, not final manual taxonomy labels.",
        "",
        "## Counts",
        "",
        f"- Authority-violation cards: `{summary['violations']['records']}`",
        f"- Correct-gold utility cards: `{summary['correct_utility']['records']}`",
        f"- Violation copy kinds: `{summary['violations']['copy_kind_counts']}`",
        f"- Violation primary mechanism seeds: `{summary['violations']['primary_mechanism_seed_counts']}`",
        f"- Strict output-contract violation seeds: `{summary['violations']['strict_output_contract_violation_count']}`",
        "",
        "## Violation Cards",
        "",
    ]
    lines.extend(render_cards_table(violation_cards))
    lines.extend([
        "",
        "## Correct-Gold Utility Cards",
        "",
    ])
    lines.extend(render_cards_table(utility_cards))
    lines.extend([
        "",
        "## Caveat",
        "",
        "The card labels are meant to guide closer reading. They should not be cited as population-level manual labels.",
        "",
    ])
    return "\n".join(lines)


def build(args: argparse.Namespace) -> dict[str, Any]:
    evaluated = load_jsonl(args.evaluated)
    deltas = load_jsonl(args.deltas)
    packet = load_jsonl(args.packet)
    evaluated_by_key = {row_key(row): row for row in evaluated}
    packet_by_key = {row_key(row): row for row in packet}

    violation_deltas = [
        row for row in deltas
        if row.get("content_polarity") == "wrong_lure"
        and row.get("base_correct")
        and row.get("authority_violation")
    ]
    utility_deltas = [
        row for row in deltas
        if row.get("content_polarity") == "correct_gold"
        and not row.get("base_correct")
        and row.get("correct_utility")
    ]

    violation_cards = [
        make_card(row, evaluated_by_key, packet_by_key, "wrong_lure_authority_violation")
        for row in violation_deltas
    ]
    utility_cards = [
        make_card(row, evaluated_by_key, packet_by_key, "correct_gold_utility")
        for row in utility_deltas
    ]

    summary = {
        "source_paths": {
            "evaluated_rows": str(args.evaluated),
            "paired_deltas": str(args.deltas),
            "packet": str(args.packet),
        },
        "violations": summarize_cards(violation_cards),
        "correct_utility": summarize_cards(utility_cards),
        "note": (
            "Authority-violation cards are base-correct wrong-lure rows that become wrong under a future signal. "
            "Correct-gold utility cards are base-wrong rows rescued by correct-gold future signals."
        ),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "violation_cards.jsonl", violation_cards)
    write_jsonl(args.out_dir / "correct_utility_cards.jsonl", utility_cards)
    write_text(args.out_dir / "mechanism_audit.md", render_markdown(summary, violation_cards, utility_cards))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluated", type=Path, default=DEFAULT_EVALUATED)
    parser.add_argument("--deltas", type=Path, default=DEFAULT_DELTAS)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
