#!/usr/bin/env python3
"""Build field-bridge labels from evaluated PACT public-state field packets."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


DEFAULT_EVALUATED = Path(
    "experiments/20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b/evaluation/evaluated_rows.jsonl"
)
DEFAULT_SPAN_ROWS = Path(
    "experiments/20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b/span_granularity_audit/span_granularity_rows.jsonl"
)
DEFAULT_PACKET = Path("experiments/20260615-local-pact-public-state-field-packet-offset100/field_packet.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-public-state-field-bridge-offset100")

BASE = "question_plus_public_state_no_final"
FREEZE = "frozen_target_plus_evidence_no_final"
HIDE_TARGET = "question_plus_evidence_no_target_no_final"
TARGET_ONLY = "public_target_plus_evidence_no_question_no_final"
WITH_FINAL = "question_plus_public_state_with_final"

STRICT_SPAN_FAMILIES = {
    "missing_required_token_or_qualifier",
    "over_specific_or_sentence_expansion",
    "high_overlap_strict_span_mismatch",
    "partial_overlap_possible_alias_or_type",
}


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
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


def by_unit_condition(rows: Iterable[Mapping[str, Any]]) -> Dict[Tuple[int, str, str], Mapping[str, Any]]:
    return {
        (int(row["sample_index"]), str(row["source_run"]), str(row["condition"])): row
        for row in rows
    }


def packet_by_id(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Mapping[str, Any]]:
    return {str(row["packet_id"]): row for row in rows if row.get("packet_id")}


def grouped_units(rows: Iterable[Mapping[str, Any]]) -> Dict[Tuple[int, str], Dict[str, Mapping[str, Any]]]:
    grouped: Dict[Tuple[int, str], Dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in rows:
        grouped[(int(row["sample_index"]), str(row["source_run"]))][str(row["condition"])] = row
    return grouped


def correct(row: Optional[Mapping[str, Any]]) -> bool:
    return bool(row and row.get("exact_match"))


def f1(row: Optional[Mapping[str, Any]]) -> float:
    return float((row or {}).get("f1") or 0.0)


def pred(row: Optional[Mapping[str, Any]]) -> Optional[str]:
    return None if row is None else row.get("prediction")


def delta_signal(
    name: str,
    before: Optional[Mapping[str, Any]],
    after: Optional[Mapping[str, Any]],
) -> Dict[str, Any]:
    before_correct = correct(before)
    after_correct = correct(after)
    if not before or not after:
        outcome = "missing"
    elif not before_correct and after_correct:
        outcome = "rescue"
    elif before_correct and not after_correct:
        outcome = "regression"
    elif before_correct and after_correct:
        outcome = "both_right"
    else:
        outcome = "both_wrong"
    return {
        "name": name,
        "outcome": outcome,
        "before_correct": before_correct,
        "after_correct": after_correct,
        "before_prediction": pred(before),
        "after_prediction": pred(after),
        "before_f1": f1(before),
        "after_f1": f1(after),
    }


def choose_bridge(
    *,
    base: Mapping[str, Any],
    freeze: Optional[Mapping[str, Any]],
    hide_target: Optional[Mapping[str, Any]],
    target_only: Optional[Mapping[str, Any]],
    with_final: Optional[Mapping[str, Any]],
    span_base: Optional[Mapping[str, Any]],
) -> Tuple[str, str, str]:
    base_correct = correct(base)
    freeze_correct = correct(freeze)
    target_only_correct = correct(target_only)
    final_correct = correct(with_final)
    hide_correct = correct(hide_target)
    target_candidate = bool(base.get("target_slot_drift_candidate"))
    span_family = str((span_base or {}).get("span_error_family") or "")

    if base_correct and not target_only_correct:
        return (
            "target_authority",
            "public_target_without_question_regression",
            "The public target and evidence are insufficient without the original question, so the target field is not a standalone task contract.",
        )
    if not base_correct and freeze_correct:
        family = "target_drift_rescued_by_question_projection" if target_candidate else "frozen_question_target_rescue"
        return (
            "target_contract",
            family,
            "Replacing public target authority with a question-derived target changes a wrong base answer to correct.",
        )
    if base_correct and not freeze_correct:
        return (
            "target_contract",
            "frozen_question_target_regression",
            "The frozen question-derived target loses a case that the original public-state surface answered correctly.",
        )
    if base_correct and not final_correct:
        return (
            "final_answer_commitment",
            "final_candidate_attractor_regression",
            "Showing the final-answer candidate changes a correct base answer to wrong or over-committed.",
        )
    if not base_correct and final_correct:
        return (
            "final_answer_commitment",
            "final_candidate_rescue",
            "Showing the final-answer candidate recovers the answer from a wrong base answer.",
        )
    if base_correct and not hide_correct:
        return (
            "target_field_ablation",
            "public_target_helped_when_question_visible",
            "Removing the public target hurts even when the original question and evidence remain visible.",
        )
    if not base_correct and hide_correct:
        return (
            "target_field_ablation",
            "public_target_hurt_when_question_visible",
            "Removing the public target rescues a wrong base answer.",
        )
    if not base_correct and span_family in STRICT_SPAN_FAMILIES:
        return (
            "final_answer_commitment",
            "strict_span_or_granularity_failure",
            "The base public-state answer is near the gold answer but fails strict span or granularity.",
        )
    if not base_correct:
        return (
            "evidence_or_content",
            "content_mismatch_after_public_state",
            "The base public-state answer is wrong beyond a strict span or granularity mismatch.",
        )
    return (
        "stable_answer",
        "stable_right_under_public_state",
        "The base public-state answer is already correct and no higher-priority field failure is triggered.",
    )


def compact_condition(row: Optional[Mapping[str, Any]], span_row: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if row is None:
        return {"missing": True}
    return {
        "correct": correct(row),
        "prediction": row.get("prediction"),
        "f1": f1(row),
        "span_error_family": (span_row or {}).get("span_error_family"),
    }


def make_bridge_case(
    key: Tuple[int, str],
    by_condition: Mapping[str, Mapping[str, Any]],
    packet_by_packet_id: Mapping[str, Mapping[str, Any]],
    span_table: Mapping[Tuple[int, str, str], Mapping[str, Any]],
) -> Dict[str, Any]:
    sample_index, source_run = key
    base = by_condition[BASE]
    freeze = by_condition.get(FREEZE)
    hide_target = by_condition.get(HIDE_TARGET)
    target_only = by_condition.get(TARGET_ONLY)
    with_final = by_condition.get(WITH_FINAL)
    span_base = span_table.get((sample_index, source_run, BASE))
    bridge_layer, bridge_family, bridge_read = choose_bridge(
        base=base,
        freeze=freeze,
        hide_target=hide_target,
        target_only=target_only,
        with_final=with_final,
        span_base=span_base,
    )
    packet = packet_by_packet_id.get(str(base.get("packet_id"))) or {}
    target_slot = packet.get("target_slot_diagnostic") or {}
    source_event = packet.get("source_final_event") or {}
    signals = [
        delta_signal("freeze_question_target", base, freeze),
        delta_signal("hide_public_target", base, hide_target),
        delta_signal("hide_question_keep_public_target", base, target_only),
        delta_signal("show_final_answer_candidate", base, with_final),
    ]
    return {
        "sample_index": sample_index,
        "source_run": source_run,
        "bridge_layer": bridge_layer,
        "bridge_family": bridge_family,
        "bridge_read": bridge_read,
        "question": packet.get("question"),
        "gold_answer": base.get("gold_answer"),
        "target_slot_drift_candidate": bool(base.get("target_slot_drift_candidate")),
        "target_slot_diagnostic": target_slot,
        "source_final_event": source_event,
        "conditions": {
            BASE: compact_condition(base, span_base),
            FREEZE: compact_condition(freeze, span_table.get((sample_index, source_run, FREEZE))),
            HIDE_TARGET: compact_condition(hide_target, span_table.get((sample_index, source_run, HIDE_TARGET))),
            TARGET_ONLY: compact_condition(target_only, span_table.get((sample_index, source_run, TARGET_ONLY))),
            WITH_FINAL: compact_condition(with_final, span_table.get((sample_index, source_run, WITH_FINAL))),
        },
        "signals": signals,
    }


def counter_by(rows: Iterable[Mapping[str, Any]], key: str) -> Dict[str, int]:
    return dict(sorted(Counter(str(row.get(key) or "") for row in rows).items()))


def nested_counter(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        out[str(row.get(outer) or "")][str(row.get(inner) or "")] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(out.items())}


def sample_indices_by(rows: Iterable[Mapping[str, Any]], key: str) -> Dict[str, List[str]]:
    buckets: Dict[str, List[str]] = defaultdict(list)
    for row in rows:
        buckets[str(row.get(key) or "")].append(f"{row['sample_index']}:{row['source_run']}")
    return {key: sorted(values) for key, values in sorted(buckets.items())}


def signal_counts(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        for signal in row.get("signals") or []:
            out[str(signal["name"])][str(signal["outcome"])] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(out.items())}


def md_cell(value: Any) -> str:
    return " ".join(("" if value is None else str(value)).split()).replace("|", "\\|")


def render_table(headers: List[str], rows: List[List[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(md_cell(item) for item in row) + " |")
    return "\n".join(lines)


def render_markdown(summary: Mapping[str, Any], rows: List[Mapping[str, Any]], args: argparse.Namespace) -> str:
    layer_rows = [
        [layer, count, ", ".join(summary["sample_units_by_layer"][layer][:20])]
        for layer, count in summary["bridge_layer_counts"].items()
    ]
    family_rows = [
        [family, count, ", ".join(summary["sample_units_by_family"][family][:20])]
        for family, count in summary["bridge_family_counts"].items()
    ]
    signal_rows = [
        [name, counts]
        for name, counts in summary["signal_counts"].items()
    ]
    focus_rows = [
        [
            row["sample_index"],
            row["source_run"],
            row["bridge_layer"],
            row["bridge_family"],
            row["gold_answer"],
            row["conditions"][BASE]["prediction"],
        ]
        for row in rows
        if row["bridge_layer"] != "stable_answer"
    ][:40]
    return "\n".join([
        "# PACT Field Bridge From Packet",
        "",
        "This bridge audit is built from evaluated public-state field packet rows, not from the older offset50 case atlas.",
        "",
        "## Sources",
        "",
        f"- Evaluated rows: `{args.evaluated}`",
        f"- Span rows: `{args.span_rows}`",
        f"- Packet rows: `{args.packet}`",
        "",
        "## Counts",
        "",
        f"- Units: `{summary['records']}`",
        f"- Unique samples: `{summary['unique_samples']}`",
        "",
        render_table(["Bridge layer", "Count", "Sample:source units"], layer_rows),
        "",
        render_table(["Bridge family", "Count", "Sample:source units"], family_rows),
        "",
        "## Delta Signals",
        "",
        render_table(["Signal", "Outcome counts"], signal_rows),
        "",
        "## Non-Stable Focus Units",
        "",
        render_table(["Sample", "Source", "Layer", "Family", "Gold", "Base prediction"], focus_rows),
        "",
        "## Caveats",
        "",
        "- These are heuristic field-bridge labels over a saved-field re-answering packet.",
        "- Labels use gold correctness and span-family audits, so they are evaluation labels, not runtime verifier decisions.",
        "- A unit can trigger several signals; `bridge_layer` is the highest-priority label for inspection.",
        "",
    ])


def build(args: argparse.Namespace) -> Dict[str, Any]:
    evaluated_rows = load_jsonl(args.evaluated)
    packet_rows = load_jsonl(args.packet)
    span_table = by_unit_condition(load_jsonl(args.span_rows))
    packet_index = packet_by_id(packet_rows)
    grouped = grouped_units(evaluated_rows)
    bridge_rows = [
        make_bridge_case(key, conditions, packet_index, span_table)
        for key, conditions in sorted(grouped.items())
        if BASE in conditions
    ]
    summary = {
        "records": len(bridge_rows),
        "unique_samples": len({row["sample_index"] for row in bridge_rows}),
        "bridge_layer_counts": counter_by(bridge_rows, "bridge_layer"),
        "bridge_family_counts": counter_by(bridge_rows, "bridge_family"),
        "bridge_family_by_layer": nested_counter(bridge_rows, "bridge_layer", "bridge_family"),
        "sample_units_by_layer": sample_indices_by(bridge_rows, "bridge_layer"),
        "sample_units_by_family": sample_indices_by(bridge_rows, "bridge_family"),
        "target_slot_candidate_by_layer": nested_counter(
            [
                {
                    "bridge_layer": row["bridge_layer"],
                    "target_slot_drift_candidate": row["target_slot_drift_candidate"],
                }
                for row in bridge_rows
            ],
            "bridge_layer",
            "target_slot_drift_candidate",
        ),
        "signal_counts": signal_counts(bridge_rows),
        "source_paths": {
            "evaluated": str(args.evaluated),
            "span_rows": str(args.span_rows),
            "packet": str(args.packet),
        },
        "note": (
            "Offline bridge labels over evaluated packet rows; this is an inspection surface, "
            "not a new model run."
        ),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "bridge_cases.jsonl", bridge_rows)
    write_text(args.out_dir / "bridge_packet.md", render_markdown(summary, bridge_rows, args))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluated", type=Path, default=DEFAULT_EVALUATED)
    parser.add_argument("--span-rows", type=Path, default=DEFAULT_SPAN_ROWS)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
