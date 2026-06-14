#!/usr/bin/env python3
"""Build a small inspection packet for PACT target-state freezing.

This is a diagnostic over saved traces. It does not score a frozen-target
method; it asks which existing compact-target cases would even be worth trying
to freeze from the first public target slot.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


TEMPLATE_MARKERS = (
    "answer type; anchor entity or entities; required qualifier",
    "answer type; anchor entities; required qualifier",
    "answer type; anchor entity; required qualifier",
)


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
    text = re.sub(r"[^a-z0-9\s;]", " ", text)
    return " ".join(text.split())


def slot_head(target_slot: Any) -> str:
    text = "" if target_slot is None else str(target_slot).strip()
    text = text.strip("[] ")
    if not text:
        return ""
    return normalize(text.split(";", 1)[0])


def is_template_slot(target_slot: Any) -> bool:
    norm = normalize(target_slot)
    return any(marker in norm for marker in TEMPLATE_MARKERS)


def first_nonempty(values: Iterable[Any]) -> Optional[str]:
    for value in values:
        if normalize(value):
            return str(value)
    return None


def event_view(event: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "turn": event.get("turn"),
        "actor_agent_id": event.get("actor_agent_id"),
        "target_slot": event.get("target_slot"),
        "action_required": event.get("action_required"),
        "environment_state": event.get("environment_state"),
        "action_result": event.get("action_result"),
        "final_answer": event.get("final_answer"),
    }


def freeze_bucket(
    transition: str,
    first_slot: Optional[str],
    final_slot: Optional[str],
    unique_slots: List[str],
    head_sequence: List[str],
    has_template_slot: bool,
) -> str:
    if not first_slot:
        return "no_initial_target_slot"
    if has_template_slot:
        return "template_collapse"
    if len(unique_slots) <= 1:
        if transition == "right_to_wrong":
            return "regression_despite_stable_target"
        if transition == "wrong_to_right":
            return "rescue_despite_stable_target"
        return "stable_target"
    if normalize(first_slot) == normalize(final_slot):
        return "target_returns_after_drift"
    if len(set(head for head in head_sequence if head)) > 1:
        return "answer_type_drift"
    if transition == "right_to_wrong":
        return "visible_target_drift_regression"
    if transition == "wrong_to_right":
        return "visible_target_drift_rescue"
    return "visible_target_drift"


def build_case(
    trace_row: Dict[str, Any],
    comparison: Dict[str, Any],
    baseline_trace_row: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    events = trace_row.get("communication_events") or []
    slots = [event.get("target_slot") for event in events]
    normalized_slots = [normalize(slot) for slot in slots if normalize(slot)]
    unique_slots = sorted(set(normalized_slots))
    first_slot = first_nonempty(slots)
    final_slot = str(slots[-1]) if slots else None
    head_sequence = [slot_head(slot) for slot in slots]
    transition = comparison.get("transition") or "unknown"
    has_template_slot = any(is_template_slot(slot) for slot in slots)

    bucket = freeze_bucket(
        transition=transition,
        first_slot=first_slot,
        final_slot=final_slot,
        unique_slots=unique_slots,
        head_sequence=head_sequence,
        has_template_slot=has_template_slot,
    )

    baseline_events = (
        baseline_trace_row.get("communication_events") if baseline_trace_row else []
    ) or []
    baseline_final_event = baseline_events[-1] if baseline_events else {}
    variant_final_event = events[-1] if events else {}

    return {
        "sample_index": trace_row.get("sample_index"),
        "instance_id": trace_row.get("instance_id"),
        "type": comparison.get("type"),
        "transition": transition,
        "freeze_bucket": bucket,
        "question": trace_row.get("question"),
        "gold_answer": trace_row.get("gold_answer"),
        "baseline_correct": comparison.get("baseline_correct"),
        "variant_correct": comparison.get("variant_correct"),
        "baseline_f1": comparison.get("baseline_f1"),
        "variant_f1": comparison.get("variant_f1"),
        "f1_delta": comparison.get("f1_delta"),
        "baseline_final_answer_text": comparison.get("baseline_final_answer_text"),
        "variant_final_answer_text": comparison.get("variant_final_answer_text"),
        "target_slot_count": len(normalized_slots),
        "unique_target_slot_count": len(unique_slots),
        "first_target_slot": first_slot,
        "final_target_slot": final_slot,
        "target_slot_sequence": slots,
        "target_slot_head_sequence": head_sequence,
        "first_final_slot_match": normalize(first_slot) == normalize(final_slot),
        "has_template_slot": has_template_slot,
        "baseline_final_event": event_view(baseline_final_event),
        "variant_events": [event_view(event) for event in events],
    }


def case_priority(row: Dict[str, Any]) -> tuple:
    transition_rank = {
        "right_to_wrong": 0,
        "wrong_to_right": 1,
        "stable_wrong": 2,
        "stable_right": 3,
    }
    bucket_rank = {
        "template_collapse": 0,
        "answer_type_drift": 1,
        "visible_target_drift_regression": 2,
        "visible_target_drift": 3,
        "target_returns_after_drift": 4,
        "regression_despite_stable_target": 5,
        "rescue_despite_stable_target": 6,
        "stable_target": 7,
    }
    return (
        transition_rank.get(row["transition"], 9),
        bucket_rank.get(row["freeze_bucket"], 9),
        -int(row["unique_target_slot_count"] or 0),
        row["sample_index"],
    )


def markdown_case(row: Dict[str, Any]) -> str:
    lines = [
        f"### Sample {row['sample_index']} - {row['transition']} - {row['freeze_bucket']}",
        "",
        f"- Question: {row['question']}",
        f"- Gold: `{row['gold_answer']}`",
        f"- Final-only answer: `{row['baseline_final_answer_text']}`",
        f"- Compact-target answer: `{row['variant_final_answer_text']}`",
        f"- First target slot: `{row['first_target_slot']}`",
        f"- Final target slot: `{row['final_target_slot']}`",
        "",
        "| Turn | Agent | Target Slot | Action Required | Action Result |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for event in row["variant_events"]:
        lines.append(
            "| {turn} | {actor} | {slot} | {action} | {result} |".format(
                turn=event.get("turn"),
                actor=event.get("actor_agent_id") or "",
                slot=str(event.get("target_slot") or "").replace("|", "\\|"),
                action=str(event.get("action_required") or "").replace("|", "\\|"),
                result=str(event.get("action_result") or "").replace("|", "\\|"),
            )
        )
    lines.append("")
    return "\n".join(lines)


def write_markdown(path: Path, summary: Dict[str, Any], rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sections = [
        "# PACT Target-State Freeze Inspection Packet",
        "",
        "This packet is diagnostic only. It inspects saved offset150 PACT traces",
        "to see where a first-turn frozen target state might have been meaningful.",
        "",
        "## Summary",
        "",
        f"- Records: `{summary['records']}`",
        f"- Focus records: `{summary['focus_records']}`",
        f"- Unstable target slots: `{summary['unstable_target_slot_records']}`",
        f"- First/final target mismatch: `{summary['first_final_target_mismatch_records']}`",
        "",
        "## Buckets",
        "",
    ]
    for bucket, count in summary["freeze_bucket_counts"].items():
        sections.append(f"- `{bucket}`: `{count}`")
    sections.extend(["", "## Focus Cases", ""])
    sections.extend(markdown_case(row) for row in rows)
    path.write_text("\n".join(sections), encoding="utf-8")


def build(args: argparse.Namespace) -> Dict[str, Any]:
    trace_by_sample = {
        row["sample_index"]: row for row in load_jsonl(args.compact_trace)
    }
    baseline_trace_by_sample = {
        row["sample_index"]: row for row in load_jsonl(args.baseline_trace)
    }
    comparisons = load_jsonl(args.comparison_cases)

    rows = [
        build_case(
            trace_row=trace_by_sample[comparison["sample_index"]],
            comparison=comparison,
            baseline_trace_row=baseline_trace_by_sample.get(comparison["sample_index"]),
        )
        for comparison in comparisons
        if comparison.get("sample_index") in trace_by_sample
    ]
    rows.sort(key=lambda row: row["sample_index"])

    focus_rows = [
        row
        for row in rows
        if row["transition"] != "stable_right"
        or row["unique_target_slot_count"] > 1
        or row["has_template_slot"]
    ]
    focus_rows.sort(key=case_priority)
    if args.focus_limit:
        focus_rows = focus_rows[: args.focus_limit]

    bucket_counts = Counter(row["freeze_bucket"] for row in rows)
    transition_counts = Counter(row["transition"] for row in rows)
    bucket_by_transition: Dict[str, Counter[str]] = {}
    for row in rows:
        bucket_by_transition.setdefault(row["transition"], Counter())
        bucket_by_transition[row["transition"]][row["freeze_bucket"]] += 1

    summary = {
        "compact_trace": str(args.compact_trace),
        "baseline_trace": str(args.baseline_trace),
        "comparison_cases": str(args.comparison_cases),
        "records": len(rows),
        "focus_records": len(focus_rows),
        "unstable_target_slot_records": sum(
            1 for row in rows if row["unique_target_slot_count"] > 1
        ),
        "first_final_target_mismatch_records": sum(
            1 for row in rows if not row["first_final_slot_match"]
        ),
        "template_slot_records": sum(1 for row in rows if row["has_template_slot"]),
        "transition_counts": dict(sorted(transition_counts.items())),
        "freeze_bucket_counts": dict(sorted(bucket_counts.items())),
        "freeze_bucket_by_transition": {
            transition: dict(sorted(counter.items()))
            for transition, counter in sorted(bucket_by_transition.items())
        },
        "sample_indices_by_bucket": {
            bucket: [row["sample_index"] for row in rows if row["freeze_bucket"] == bucket]
            for bucket in sorted(bucket_counts)
        },
        "note": (
            "Buckets are mechanical inspection aids. A first-turn frozen target "
            "state was not actually run."
        ),
    }

    write_json(args.summary_out, summary)
    write_jsonl(args.cases_out, rows)
    write_jsonl(args.focus_out, focus_rows)
    write_markdown(args.markdown_out, summary, focus_rows)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact-trace", type=Path, required=True)
    parser.add_argument("--baseline-trace", type=Path, required=True)
    parser.add_argument("--comparison-cases", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, required=True)
    parser.add_argument("--focus-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    parser.add_argument("--focus-limit", type=int, default=16)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
