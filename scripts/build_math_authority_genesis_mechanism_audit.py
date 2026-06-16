#!/usr/bin/env python3
"""Build mechanism-audit cards for the MATH Authority Genesis Ladder run."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_EVALUATED = Path(
    "experiments/20260616-0102-a8002-math-authority-genesis-ladder-qwen25-14b-max768/evaluation/evaluated_rows.jsonl"
)
DEFAULT_DELTAS = Path(
    "experiments/20260616-0102-a8002-math-authority-genesis-ladder-qwen25-14b-max768/evaluation/paired_deltas.jsonl"
)
DEFAULT_PACKET = Path(
    "experiments/20260615-local-math-authority-genesis-ladder-packet/math_authority_genesis_ladder_packet.jsonl"
)
DEFAULT_OUT_DIR = Path("experiments/20260616-local-math-authority-genesis-mechanism-audit")
BASE_VARIANT = "baseline_previous_solution"


PRIMARY_OPERATOR_BY_ARTIFACT = {
    "wrong_relation_skeleton": "relation_skeleton_operator_uptake",
    "wrong_numeric_role_binding": "numeric_role_binding_operator_uptake",
    "wrong_equation_surface": "equation_surface_operator_uptake",
    "wrong_final_answer": "final_answer_anchor_disturbance",
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


def baseline_key(case_id: Any) -> tuple[str, str]:
    return (str(case_id), BASE_VARIANT)


def compact(value: Any) -> str:
    return " ".join(("" if value is None else str(value)).split())


def quality_labels(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "relation_skeleton_quality": row.get("relation_skeleton_quality"),
        "numeric_role_slot_quality": row.get("numeric_role_slot_quality"),
        "equation_surface_quality": row.get("equation_surface_quality"),
        "final_answer_authority_visible_seed": row.get("final_answer_authority_visible_seed"),
        "target_predicate_preserved": row.get("target_predicate_preserved"),
        "target_revision_behavior": row.get("target_revision_behavior"),
    }


def primary_mechanism(delta: Mapping[str, Any]) -> str:
    if delta.get("wrong_answer_uptake"):
        return "direct_wrong_answer_uptake"
    if delta.get("operator_uptake_candidate"):
        return PRIMARY_OPERATOR_BY_ARTIFACT.get(str(delta.get("artifact_type")), "other_operator_uptake")
    return "other_authority_violation"


def mechanism_labels(delta: Mapping[str, Any]) -> list[str]:
    labels: set[str] = set()
    if delta.get("wrong_answer_uptake"):
        labels.add("semantic_match_to_wrong_peer_answer")
    if delta.get("artifact_answer_uptake"):
        labels.add("semantic_match_to_artifact_text")
    if delta.get("artifact_text_overlap"):
        labels.add("surface_overlap_with_artifact_text")
    if delta.get("operator_uptake_candidate"):
        labels.add("non_peer_wrong_answer_shift")
        artifact_type = str(delta.get("artifact_type"))
        if artifact_type == "wrong_relation_skeleton":
            labels.add("relation_skeleton_candidate")
        elif artifact_type == "wrong_numeric_role_binding":
            labels.add("numeric_role_binding_candidate")
        elif artifact_type == "wrong_equation_surface":
            labels.add("equation_surface_candidate")
        elif artifact_type == "wrong_final_answer":
            labels.add("final_answer_anchor_without_exact_copy")
    return sorted(labels)


def manual_review_priority(delta: Mapping[str, Any], case_violation_count: int) -> str:
    if delta.get("operator_uptake_candidate") and str(delta.get("artifact_type")) in {
        "wrong_equation_surface",
        "wrong_numeric_role_binding",
        "wrong_relation_skeleton",
    }:
        return "operator_core"
    if delta.get("operator_uptake_candidate"):
        return "operator_secondary"
    if delta.get("wrong_answer_uptake"):
        return "answer_copy"
    if case_violation_count >= 5:
        return "case_cluster"
    return "standard"


def make_violation_card(
    delta: Mapping[str, Any],
    evaluated_by_key: Mapping[tuple[str, str], Mapping[str, Any]],
    packet_by_key: Mapping[tuple[str, str], Mapping[str, Any]],
    case_violation_count: int,
) -> dict[str, Any]:
    evaluated = evaluated_by_key.get(row_key(delta), {})
    packet = packet_by_key.get(row_key(delta), {})
    baseline = evaluated_by_key.get(baseline_key(delta.get("case_id")), {})
    genesis = packet.get("math_authority_genesis") or {}
    manual = packet.get("manual_seed_label") or {}
    primary = primary_mechanism(delta)
    return {
        "event_type": "math_authority_violation",
        "case_id": delta.get("case_id"),
        "math_case_id": delta.get("math_case_id"),
        "condition": delta.get("condition"),
        "source_surface": delta.get("source_surface"),
        "variant": delta.get("variant"),
        "artifact_type": delta.get("artifact_type"),
        "future_level": delta.get("future_level"),
        "future_signal": delta.get("future_signal"),
        "operator_family": delta.get("operator_family"),
        "artifact_visible_to_model": delta.get("artifact_visible_to_model"),
        "primary_mechanism_seed": primary,
        "mechanism_seed_labels": mechanism_labels(delta),
        "manual_review_priority": manual_review_priority(delta, case_violation_count),
        "case_violation_count": case_violation_count,
        "gold_answer": delta.get("gold_answer"),
        "wrong_peer_answer": delta.get("wrong_peer_answer"),
        "artifact_text": genesis.get("artifact_text") or evaluated.get("artifact_text"),
        "base_prediction_answer": delta.get("base_prediction_answer"),
        "variant_prediction_answer": delta.get("variant_prediction_answer"),
        "wrong_answer_uptake": delta.get("wrong_answer_uptake"),
        "artifact_answer_uptake": delta.get("artifact_answer_uptake"),
        "artifact_text_overlap": delta.get("artifact_text_overlap"),
        "operator_uptake_candidate": delta.get("operator_uptake_candidate"),
        "question": packet.get("question"),
        "manual_note": manual.get("manual_note"),
        "target_revision_behavior": delta.get("target_revision_behavior"),
        "quality_labels": quality_labels(delta),
        "baseline_prediction_text": baseline.get("prediction_text"),
        "variant_prediction_text": evaluated.get("prediction_text"),
        "prompt": packet.get("prompt"),
        "caveat": (
            "Mechanism labels are deterministic seed labels for triage. "
            "They are not final manual taxonomy labels."
        ),
    }


def summarize_rows(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "records": len(rows),
        "authority_violation_count": sum(1 for row in rows if row.get("authority_violation")),
        "wrong_answer_uptake_count": sum(1 for row in rows if row.get("wrong_answer_uptake")),
        "operator_uptake_candidate_count": sum(1 for row in rows if row.get("operator_uptake_candidate")),
    }


def nested_counts(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> dict[str, dict[str, int]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[str(row.get(outer))][str(row.get(inner))] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(grouped.items())}


def card_summary(cards: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "records": len(cards),
        "primary_mechanism_seed_counts": dict(
            sorted(Counter(str(row.get("primary_mechanism_seed")) for row in cards).items())
        ),
        "artifact_type_counts": dict(sorted(Counter(str(row.get("artifact_type")) for row in cards).items())),
        "future_signal_counts": dict(sorted(Counter(str(row.get("future_signal")) for row in cards).items())),
        "source_surface_counts": dict(sorted(Counter(str(row.get("source_surface")) for row in cards).items())),
        "case_counts": dict(sorted(Counter(str(row.get("case_id")) for row in cards).items())),
        "manual_review_priority_counts": dict(
            sorted(Counter(str(row.get("manual_review_priority")) for row in cards).items())
        ),
        "primary_by_future_signal": nested_counts(cards, "future_signal", "primary_mechanism_seed"),
        "primary_by_artifact_type": nested_counts(cards, "artifact_type", "primary_mechanism_seed"),
    }


def top_counts(counts: Mapping[str, int], limit: int = 12) -> list[tuple[str, int]]:
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]


def md_cell(value: Any) -> str:
    return compact(value).replace("|", "\\|")


def render_count_table(title: str, counts: Mapping[str, int]) -> list[str]:
    lines = [f"## {title}", "", "| Slice | Count |", "| --- | ---: |"]
    for key, value in top_counts(counts, limit=30):
        lines.append(f"| {md_cell(key)} | {value} |")
    lines.append("")
    return lines


def render_cards_table(cards: list[Mapping[str, Any]], limit: int = 30) -> list[str]:
    lines = [
        "| Case | Artifact | Signal | Primary seed | Gold | Base | Variant | Wrong peer | Priority |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in cards[:limit]:
        lines.append(
            "| {case} | {artifact} | {signal} | {primary} | {gold} | {base} | {variant} | {wrong} | {priority} |".format(
                case=md_cell(row.get("case_id")),
                artifact=md_cell(row.get("artifact_type")),
                signal=md_cell(row.get("future_signal")),
                primary=md_cell(row.get("primary_mechanism_seed")),
                gold=md_cell(row.get("gold_answer")),
                base=md_cell(row.get("base_prediction_answer")),
                variant=md_cell(row.get("variant_prediction_answer")),
                wrong=md_cell(row.get("wrong_peer_answer")),
                priority=md_cell(row.get("manual_review_priority")),
            )
        )
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any], cards: list[Mapping[str, Any]]) -> str:
    violations = summary["violations"]
    hidden = summary["hidden_metadata_controls"]
    lines = [
        "# MATH Authority Genesis Mechanism Audit",
        "",
        "This audit extracts the behavior-changing cards from the MATH Authority Genesis Ladder run.",
        "Mechanism labels are deterministic seed labels for inspection, not final manual taxonomy labels.",
        "",
        "## Counts",
        "",
        f"- Violation cards: `{violations['records']}`",
        f"- Hidden-metadata control rows: `{hidden['records']}`",
        f"- Hidden-metadata authority violations: `{hidden['authority_violation_count']}`",
        f"- Wrong-answer uptake cards: `{summary['wrong_answer_uptake_cards']}`",
        f"- Operator-uptake candidate cards: `{summary['operator_uptake_candidate_cards']}`",
        "",
    ]
    lines.extend(render_count_table("Primary Mechanism Seeds", violations["primary_mechanism_seed_counts"]))
    lines.extend(render_count_table("Artifact Types", violations["artifact_type_counts"]))
    lines.extend(render_count_table("Future Signals", violations["future_signal_counts"]))
    lines.extend(render_count_table("Case Concentration", violations["case_counts"]))
    lines.extend(["## Violation Cards", ""])
    lines.extend(render_cards_table(cards))
    lines.extend(
        [
            "## Caveat",
            "",
            "The card labels are meant to guide closer reading. They should not be cited as population-level manual labels.",
            "",
        ]
    )
    return "\n".join(lines)


def build(args: argparse.Namespace) -> dict[str, Any]:
    evaluated = load_jsonl(args.evaluated)
    deltas = load_jsonl(args.deltas)
    packet = load_jsonl(args.packet)
    evaluated_by_key = {row_key(row): row for row in evaluated}
    packet_by_key = {row_key(row): row for row in packet}

    violation_deltas = [row for row in deltas if row.get("authority_violation")]
    case_counts = Counter(str(row.get("case_id")) for row in violation_deltas)
    violation_cards = [
        make_violation_card(
            row,
            evaluated_by_key,
            packet_by_key,
            case_counts[str(row.get("case_id"))],
        )
        for row in violation_deltas
    ]

    hidden_controls = [row for row in deltas if row.get("future_signal") == "hidden_metadata"]
    visible_controls = [row for row in deltas if row.get("artifact_visible_to_model")]

    summary = {
        "source_paths": {
            "evaluated_rows": str(args.evaluated),
            "paired_deltas": str(args.deltas),
            "packet": str(args.packet),
        },
        "violations": card_summary(violation_cards),
        "hidden_metadata_controls": summarize_rows(hidden_controls),
        "visible_future_signal_rows": summarize_rows(visible_controls),
        "wrong_answer_uptake_cards": sum(1 for row in violation_cards if row.get("wrong_answer_uptake")),
        "operator_uptake_candidate_cards": sum(1 for row in violation_cards if row.get("operator_uptake_candidate")),
        "note": (
            "Cards are base-correct rows that become semantically wrong under a future signal. "
            "Operator-uptake candidates are authority violations that do not semantically match the wrong peer answer."
        ),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "violation_cards.jsonl", violation_cards)
    write_text(args.out_dir / "mechanism_audit.md", render_markdown(summary, violation_cards))
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
