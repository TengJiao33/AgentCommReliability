#!/usr/bin/env python3
"""Analyze a MATH sender-receiver micro-protocol run."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_RUN_DIR = Path("experiments/20260616-local-math-sender-receiver-micro-protocol-packet/gold-smoke")
DEFAULT_PACKET = Path(
    "experiments/20260616-local-math-sender-receiver-micro-protocol-packet/math_sender_receiver_micro_protocol_packet.jsonl"
)
DEFAULT_OUT_DIR = Path("experiments/20260616-local-math-sender-receiver-micro-protocol-packet/analysis-gold-smoke")


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


def compact(value: Any) -> str:
    return re.sub(r"\s+", "", "" if value is None else str(value)).strip().lower()


def literal_visible(needle: Any, haystack: Any) -> bool:
    n = compact(needle)
    h = compact(haystack)
    return bool(n and h and n in h)


def lifecycle(packet_row: Mapping[str, Any]) -> dict[str, Any]:
    return dict(packet_row.get("sender_receiver") or packet_row.get("type_erasure") or {})


def has_substantive_visible_artifact(meta: Mapping[str, Any]) -> bool:
    text = compact(meta.get("visible_artifact_text"))
    if not text:
        return False
    if "candidateanswerremoved" in text or "withheldbyquarantinepolicy" in text:
        return False
    return True


def taxonomy(delta: Mapping[str, Any], packet_row: Mapping[str, Any]) -> dict[str, Any]:
    meta = lifecycle(packet_row)
    artifact_type = str(delta.get("artifact_type"))
    channel = str(delta.get("future_signal"))
    family = str(meta.get("channel_condition"))
    admission = str(meta.get("admission_status"))
    wrong_visible = bool(
        meta.get("wrong_answer_literal_in_prompt")
        or literal_visible(delta.get("wrong_peer_answer"), packet_row.get("prompt"))
    )
    substantive = has_substantive_visible_artifact(meta)

    labels: set[str] = {f"family:{family}", f"admission:{admission}", f"channel:{channel}"}
    if wrong_visible:
        labels.add("wrong_answer_literal_visible")
    else:
        labels.add("wrong_answer_literal_not_visible")

    if delta.get("wrong_answer_uptake") and wrong_visible:
        primary = "direct_visible_answer_uptake"
    elif (
        delta.get("operator_uptake_candidate")
        and family == "admitted"
        and artifact_type in {"wrong_equation_surface", "wrong_numeric_role_binding", "wrong_relation_skeleton"}
    ):
        primary = "admitted_state_inherited_operator"
        labels.add("invalid_cast_core")
    elif (
        delta.get("operator_uptake_candidate")
        and channel in {"peer_message_direct", "broadcast_peer_message"}
        and artifact_type in {"wrong_equation_surface", "wrong_numeric_role_binding", "wrong_relation_skeleton"}
    ):
        primary = "peer_message_operator_influence"
    elif delta.get("operator_uptake_candidate") and not substantive:
        primary = "local_re_solve_or_empty_artifact_error"
    elif not wrong_visible and delta.get("wrong_answer_uptake"):
        primary = "final_answer_contract_or_hidden_collision"
    elif delta.get("operator_uptake_candidate"):
        primary = "operator_candidate_needs_manual_review"
    else:
        primary = "authority_violation_needs_manual_review"

    return {
        "taxonomy_primary": primary,
        "taxonomy_labels": sorted(labels),
        "wrong_answer_literal_visible": wrong_visible,
        "substantive_visible_artifact": substantive,
    }


def make_card(
    delta: Mapping[str, Any],
    evaluated_by_key: Mapping[tuple[str, str], Mapping[str, Any]],
    packet_by_key: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    key = row_key(delta)
    evaluated = evaluated_by_key.get(key, {})
    packet = packet_by_key.get(key, {})
    meta = lifecycle(packet)
    tax = taxonomy(delta, packet)
    return {
        "event_type": "math_sender_receiver_authority_violation",
        "case_id": delta.get("case_id"),
        "math_case_id": delta.get("math_case_id"),
        "variant": delta.get("variant"),
        "artifact_type": delta.get("artifact_type"),
        "future_signal": delta.get("future_signal"),
        "channel_condition": meta.get("channel_condition"),
        "admission_status": meta.get("admission_status"),
        "delivery_scope": meta.get("delivery_scope"),
        "persistence": meta.get("persistence"),
        "candidate_visibility": meta.get("candidate_visibility"),
        "gold_answer": delta.get("gold_answer"),
        "wrong_peer_answer": delta.get("wrong_peer_answer"),
        "base_prediction_answer": delta.get("base_prediction_answer"),
        "variant_prediction_answer": delta.get("variant_prediction_answer"),
        "wrong_answer_uptake": delta.get("wrong_answer_uptake"),
        "operator_uptake_candidate": delta.get("operator_uptake_candidate"),
        "artifact_text": meta.get("visible_artifact_text") or evaluated.get("artifact_text"),
        "prediction_text": evaluated.get("prediction_text"),
        "prompt": packet.get("prompt"),
        **tax,
    }


def authority_by(deltas: list[Mapping[str, Any]], packet_by_key: Mapping[tuple[str, str], Mapping[str, Any]], *keys: str) -> dict[str, dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in deltas:
        packet = packet_by_key.get(row_key(row), {})
        meta = lifecycle(packet)
        values = []
        for key in keys:
            if key in row:
                values.append(str(row.get(key)))
            else:
                values.append(str(meta.get(key)))
        grouped[tuple(values)].append(row)
    out: dict[str, dict[str, Any]] = {}
    for key, rows in sorted(grouped.items()):
        base_correct = [row for row in rows if row.get("base_correct") is True]
        violations = [row for row in base_correct if row.get("authority_violation")]
        answer = [row for row in base_correct if row.get("wrong_answer_uptake")]
        operator = [row for row in base_correct if row.get("operator_uptake_candidate")]
        out[" | ".join(key)] = {
            "records": len(rows),
            "base_correct_records": len(base_correct),
            "authority_violation_count": len(violations),
            "authority_violation_rate": len(violations) / len(base_correct) if base_correct else None,
            "wrong_answer_uptake_count": len(answer),
            "operator_uptake_candidate_count": len(operator),
        }
    return out


def nested_counts(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> dict[str, dict[str, int]]:
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        out[str(row.get(outer))][str(row.get(inner))] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(out.items())}


def card_summary(cards: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "records": len(cards),
        "taxonomy_primary_counts": dict(sorted(Counter(str(row.get("taxonomy_primary")) for row in cards).items())),
        "taxonomy_by_channel_condition": nested_counts(cards, "channel_condition", "taxonomy_primary"),
        "taxonomy_by_admission_status": nested_counts(cards, "admission_status", "taxonomy_primary"),
        "taxonomy_by_future_signal": nested_counts(cards, "future_signal", "taxonomy_primary"),
        "artifact_type_counts": dict(sorted(Counter(str(row.get("artifact_type")) for row in cards).items())),
        "case_counts": dict(sorted(Counter(str(row.get("case_id")) for row in cards).items())),
    }


def pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def md_cell(value: Any) -> str:
    return " ".join(("" if value is None else str(value)).split()).replace("|", "\\|")


def render_authority_table(title: str, grouped: Mapping[str, Mapping[str, Any]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, row in grouped.items():
        lines.append(
            f"| {md_cell(key)} | {row['records']} | {row['base_correct_records']} | "
            f"{row['authority_violation_count']} | {pct(row.get('authority_violation_rate'))} | "
            f"{row['wrong_answer_uptake_count']} | {row['operator_uptake_candidate_count']} |"
        )
    lines.append("")
    return lines


def render_cards(cards: list[Mapping[str, Any]], limit: int = 40) -> list[str]:
    lines = [
        "## Violation Cards",
        "",
        "| Case | Channel | Admission | Artifact | Taxonomy | Base -> Variant |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in cards[:limit]:
        lines.append(
            "| {case} | {channel} | {admission} | {artifact} | {tax} | {base} -> {variant} |".format(
                case=md_cell(row.get("case_id")),
                channel=md_cell(row.get("future_signal")),
                admission=md_cell(row.get("admission_status")),
                artifact=md_cell(row.get("artifact_type")),
                tax=md_cell(row.get("taxonomy_primary")),
                base=md_cell(row.get("base_prediction_answer")),
                variant=md_cell(row.get("variant_prediction_answer")),
            )
        )
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any], cards: list[Mapping[str, Any]]) -> str:
    card_counts = summary["violation_cards"]
    lines = [
        "# MATH Sender-Receiver Micro-Protocol Analysis",
        "",
        f"- Evaluated rows: `{summary['records']}`",
        f"- Paired delta rows: `{summary['paired_delta_rows']}`",
        f"- Authority-violation cards: `{card_counts['records']}`",
        f"- Taxonomy counts: `{card_counts['taxonomy_primary_counts']}`",
        "",
    ]
    lines.extend(render_authority_table("Authority By Channel Condition", summary["authority_by_channel_condition"]))
    lines.extend(render_authority_table("Authority By Admission Status", summary["authority_by_admission_status"]))
    lines.extend(render_authority_table("Authority By Future Signal", summary["authority_by_future_signal"]))
    lines.extend(render_cards(cards))
    lines.extend(
        [
            "## Caveat",
            "",
            "Taxonomy labels are deterministic seed labels for triage. Manual inspection is still required before turning counts into claims.",
            "",
        ]
    )
    return "\n".join(lines)


def build(args: argparse.Namespace) -> dict[str, Any]:
    evaluated_path = args.run_dir / "evaluated_rows.jsonl"
    deltas_path = args.run_dir / "paired_deltas.jsonl"
    evaluated = load_jsonl(evaluated_path)
    deltas = load_jsonl(deltas_path)
    packet = load_jsonl(args.packet)
    evaluated_by_key = {row_key(row): row for row in evaluated}
    packet_by_key = {row_key(row): row for row in packet}
    violation_deltas = [row for row in deltas if row.get("authority_violation")]
    cards = [make_card(row, evaluated_by_key, packet_by_key) for row in violation_deltas]
    summary = {
        "source_paths": {
            "run_dir": str(args.run_dir),
            "evaluated_rows": str(evaluated_path),
            "paired_deltas": str(deltas_path),
            "packet": str(args.packet),
        },
        "records": len(evaluated),
        "paired_delta_rows": len(deltas),
        "violation_cards": card_summary(cards),
        "authority_by_channel_condition": authority_by(deltas, packet_by_key, "channel_condition"),
        "authority_by_admission_status": authority_by(deltas, packet_by_key, "admission_status"),
        "authority_by_future_signal": authority_by(deltas, packet_by_key, "future_signal"),
        "authority_by_artifact_type_channel_condition": authority_by(deltas, packet_by_key, "artifact_type", "channel_condition"),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "violation_cards.jsonl", cards)
    write_text(args.out_dir / "summary.md", render_markdown(summary, cards))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
