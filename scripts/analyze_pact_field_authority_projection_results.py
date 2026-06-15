#!/usr/bin/env python3
"""Compare field-authority projection outputs against fixed field controls."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


DEFAULT_CONTROL_EVALUATED = Path(
    "experiments/20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b/evaluation/evaluated_rows.jsonl"
)
DEFAULT_PROJECTION_EVALUATED = Path(
    "experiments/20260615-1805-a8002-pact-field-authority-projection-offset100-qwen25-14b/evaluation/evaluated_rows.jsonl"
)
DEFAULT_PROJECTION_PACKET = Path(
    "experiments/20260615-local-pact-field-authority-projection-offset100/projection_packet.jsonl"
)
DEFAULT_OUT_DIR = Path(
    "experiments/20260615-1805-a8002-pact-field-authority-projection-offset100-qwen25-14b/projection_delta_audit"
)

COMPARISONS = [
    (
        "security_vs_public_state",
        "security_projection_question_root_no_final",
        "question_plus_public_state_no_final",
    ),
    (
        "security_vs_hide_target",
        "security_projection_question_root_no_final",
        "question_plus_evidence_no_target_no_final",
    ),
    (
        "security_vs_frozen_target",
        "security_projection_question_root_no_final",
        "frozen_target_plus_evidence_no_final",
    ),
    (
        "standalone_vs_public_state",
        "standalone_authority_quarantine_no_final",
        "question_plus_public_state_no_final",
    ),
    (
        "standalone_vs_hide_target",
        "standalone_authority_quarantine_no_final",
        "question_plus_evidence_no_target_no_final",
    ),
    (
        "standalone_vs_frozen_target",
        "standalone_authority_quarantine_no_final",
        "frozen_target_plus_evidence_no_final",
    ),
    (
        "standalone_vs_security",
        "standalone_authority_quarantine_no_final",
        "security_projection_question_root_no_final",
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


def table(rows: Iterable[Mapping[str, Any]]) -> Dict[Tuple[int, str, str], Mapping[str, Any]]:
    return {
        (int(row["sample_index"]), str(row["source_run"]), str(row["condition"])): row
        for row in rows
    }


def packet_table(rows: Iterable[Mapping[str, Any]]) -> Dict[Tuple[int, str, str], Mapping[str, Any]]:
    return {
        (int(row["sample_index"]), str(row["source_run"]), str(row["condition"])): row
        for row in rows
    }


def outcome(left: Optional[Mapping[str, Any]], right: Optional[Mapping[str, Any]]) -> str:
    if not left or not right:
        return "missing"
    left_correct = bool(left.get("exact_match"))
    right_correct = bool(right.get("exact_match"))
    if not right_correct and left_correct:
        return "projection_rescue"
    if right_correct and not left_correct:
        return "projection_regression"
    if right_correct and left_correct:
        return "both_right"
    return "both_wrong"


def build_cards(
    projection_rows: Mapping[Tuple[int, str, str], Mapping[str, Any]],
    control_rows: Mapping[Tuple[int, str, str], Mapping[str, Any]],
    packet_rows: Mapping[Tuple[int, str, str], Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    units = sorted({
        (sample, source)
        for sample, source, _condition in projection_rows
    })
    for sample_index, source_run in units:
        for comparison, projection_condition, reference_condition in COMPARISONS:
            projection = projection_rows.get((sample_index, source_run, projection_condition))
            if reference_condition in {
                "security_projection_question_root_no_final",
                "standalone_authority_quarantine_no_final",
            }:
                reference = projection_rows.get((sample_index, source_run, reference_condition))
            else:
                reference = control_rows.get((sample_index, source_run, reference_condition))
            packet = packet_rows.get((sample_index, source_run, projection_condition)) or {}
            detector = packet.get("authority_detector") or {}
            if projection is None or reference is None:
                continue
            cards.append({
                "sample_index": sample_index,
                "source_run": source_run,
                "comparison": comparison,
                "projection_condition": projection_condition,
                "reference_condition": reference_condition,
                "delta_outcome": outcome(projection, reference),
                "projection_correct": bool(projection.get("exact_match")),
                "reference_correct": bool(reference.get("exact_match")),
                "projection_prediction": projection.get("prediction"),
                "reference_prediction": reference.get("prediction"),
                "gold_answer": projection.get("gold_answer"),
                "projection_f1": projection.get("f1"),
                "reference_f1": reference.get("f1"),
                "target_slot_drift_candidate": bool(projection.get("target_slot_drift_candidate")),
                "detector_action": detector.get("target_action"),
                "detector_reasons": detector.get("target_reasons") or [],
            })
    return cards


def summarize_group(rows: List[Mapping[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    exact = sum(1 for row in rows if row.get("exact_match"))
    return {
        "records": total,
        "exact_matches": exact,
        "exact_match": exact / total if total else 0.0,
        "avg_f1": sum(float(row.get("f1") or 0.0) for row in rows) / total if total else 0.0,
    }


def condition_summaries(
    projection_rows: Iterable[Mapping[str, Any]],
    control_rows: Iterable[Mapping[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    wanted = {
        "security_projection_question_root_no_final",
        "standalone_authority_quarantine_no_final",
        "question_plus_public_state_no_final",
        "question_plus_evidence_no_target_no_final",
        "frozen_target_plus_evidence_no_final",
        "public_target_plus_evidence_no_question_no_final",
        "question_plus_public_state_with_final",
    }
    by_condition: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for row in list(projection_rows) + list(control_rows):
        condition = str(row.get("condition"))
        if condition in wanted:
            by_condition[condition].append(row)
    return {
        condition: summarize_group(rows)
        for condition, rows in sorted(by_condition.items())
    }


def count_by(cards: Iterable[Mapping[str, Any]], *keys: str) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Counter[str]] = defaultdict(Counter)
    for card in cards:
        key = " | ".join(str(card.get(key_name)) for key_name in keys)
        out[key][str(card["delta_outcome"])] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(out.items())}


def md_cell(value: Any) -> str:
    return " ".join(("" if value is None else str(value)).split()).replace("|", "\\|")


def render_condition_table(rows: Mapping[str, Mapping[str, Any]]) -> List[str]:
    lines = [
        "## Condition Scores",
        "",
        "| Condition | Records | EM | Avg F1 |",
        "| --- | ---: | ---: | ---: |",
    ]
    for condition, row in rows.items():
        lines.append(
            f"| `{condition}` | {row['records']} | {row['exact_match']:.3f} | {row['avg_f1']:.3f} |"
        )
    lines.append("")
    return lines


def render_delta_table(title: str, rows: Mapping[str, Mapping[str, int]]) -> List[str]:
    outcomes = ["projection_rescue", "projection_regression", "both_right", "both_wrong"]
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


def render_examples(title: str, rows: List[Mapping[str, Any]]) -> List[str]:
    lines = [
        f"## {title}",
        "",
        "| Sample | Source | Detector | Gold | Reference | Projection |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows[:20]:
        detector = row.get("detector_action")
        reasons = ",".join(row.get("detector_reasons") or [])
        lines.append(
            "| {sample} | {source} | {detector} | {gold} | {ref} | {proj} |".format(
                sample=row["sample_index"],
                source=md_cell(row["source_run"]),
                detector=md_cell(f"{detector}:{reasons}"),
                gold=md_cell(row["gold_answer"]),
                ref=md_cell(row["reference_prediction"]),
                proj=md_cell(row["projection_prediction"]),
            )
        )
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = ["# PACT Field-Authority Projection Delta Audit", ""]
    lines.extend(render_condition_table(summary["condition_scores"]))
    lines.extend(render_delta_table("Projection Versus Controls", summary["comparisons"]))
    lines.extend(render_delta_table("By Detector Action", summary["comparisons_by_detector_action"]))
    notable = summary["notable_cards"]
    lines.extend(render_examples("Security Regressions Versus Frozen Target", notable["security_regressions_vs_frozen"]))
    lines.extend(render_examples("Standalone Regressions Versus Security", notable["standalone_regressions_vs_security"]))
    return "\n".join(lines)


def build(args: argparse.Namespace) -> Dict[str, Any]:
    projection_eval_rows = load_jsonl(args.projection_evaluated)
    control_eval_rows = load_jsonl(args.control_evaluated)
    cards = build_cards(
        projection_rows=table(projection_eval_rows),
        control_rows=table(control_eval_rows),
        packet_rows=packet_table(load_jsonl(args.projection_packet)),
    )
    summary = {
        "condition_scores": condition_summaries(projection_eval_rows, control_eval_rows),
        "comparisons": count_by(cards, "comparison"),
        "comparisons_by_detector_action": count_by(cards, "comparison", "detector_action"),
        "comparisons_by_target_candidate": count_by(cards, "comparison", "target_slot_drift_candidate"),
        "notable_cards": {
            "security_regressions_vs_frozen": [
                card for card in cards
                if card["comparison"] == "security_vs_frozen_target"
                and card["delta_outcome"] == "projection_regression"
            ],
            "standalone_regressions_vs_security": [
                card for card in cards
                if card["comparison"] == "standalone_vs_security"
                and card["delta_outcome"] == "projection_regression"
            ],
        },
        "paths": {
            "control_evaluated": str(args.control_evaluated),
            "projection_evaluated": str(args.projection_evaluated),
            "projection_packet": str(args.projection_packet),
        },
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "projection_delta_summary.json", summary)
    write_jsonl(args.out_dir / "projection_delta_cards.jsonl", cards)
    write_text(args.out_dir / "projection_delta_summary.md", render_markdown(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-evaluated", type=Path, default=DEFAULT_CONTROL_EVALUATED)
    parser.add_argument("--projection-evaluated", type=Path, default=DEFAULT_PROJECTION_EVALUATED)
    parser.add_argument("--projection-packet", type=Path, default=DEFAULT_PROJECTION_PACKET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
