#!/usr/bin/env python3
"""Summarize manual field labels for the MATH200 peer claim-hygiene packet."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from peer_probe.io_utils import read_jsonl, write_json, write_jsonl


def row_key(row: Dict[str, Any]) -> Tuple[str, str, str]:
    return (str(row.get("case_index")), str(row.get("condition")), str(row.get("mode")))


def count_field(rows: Iterable[Dict[str, Any]], field: str) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        value = row.get(field)
        if value is None:
            value = "null"
        counter[str(value)] += 1
    return dict(counter)


def count_by_surface(rows: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter[str(row.get("surface"))] += 1
    return dict(counter)


def index_packet(packet_rows: List[Dict[str, Any]]) -> Dict[Tuple[str, str, str], Dict[str, Any]]:
    indexed: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for row in packet_rows:
        indexed[row_key(row)] = row
    return indexed


def attach_packet_context(
    manual_rows: List[Dict[str, Any]],
    packet_index: Dict[Tuple[str, str, str], Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged = []
    for row in manual_rows:
        packet = packet_index.get(row_key(row)) or {}
        merged.append(
            {
                **row,
                "reason": packet.get("reason"),
                "surface": packet.get("surface"),
                "visible_slots": packet.get("visible_slots"),
                "hidden_slots": packet.get("hidden_slots"),
                "pre_answer_raw": packet.get("pre_answer_raw"),
                "post_answer_raw": packet.get("post_answer_raw"),
                "gold_answer_raw": packet.get("gold_answer_raw"),
            }
        )
    return merged


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    packet_rows = read_jsonl(args.field_label_packet)
    seed_rows = read_jsonl(args.manual_seed_labels)
    source_rows = read_jsonl(args.manual_source_label_sensitive_seed_labels)
    packet_index = index_packet(packet_rows)
    seed_keys = {row_key(row) for row in seed_rows}
    source_keys = {row_key(row) for row in source_rows}
    labeled_keys = seed_keys | source_keys
    unlabeled = [row for row in packet_rows if row_key(row) not in labeled_keys]
    merged_seed = attach_packet_context(seed_rows, packet_index)
    merged_source = attach_packet_context(source_rows, packet_index)

    unlabeled_by_reason: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in unlabeled:
        unlabeled_by_reason[str(row.get("reason"))][str(row.get("surface"))] += 1

    return {
        "inputs": {
            "field_label_packet": str(args.field_label_packet),
            "manual_seed_labels": str(args.manual_seed_labels),
            "manual_source_label_sensitive_seed_labels": str(args.manual_source_label_sensitive_seed_labels),
        },
        "counts": {
            "packet_rows": len(packet_rows),
            "manual_seed_rows": len(seed_rows),
            "manual_source_label_sensitive_seed_rows": len(source_rows),
            "unique_labeled_rows": len(labeled_keys),
            "unlabeled_rows": len(unlabeled),
            "packet_by_reason": count_field(packet_rows, "reason"),
            "packet_by_surface": count_by_surface(packet_rows),
            "unlabeled_by_reason": count_field(unlabeled, "reason"),
            "unlabeled_by_surface": count_by_surface(unlabeled),
            "unlabeled_by_reason_surface": {
                reason: dict(counter) for reason, counter in unlabeled_by_reason.items()
            },
        },
        "anonymous_behavior_labels": {
            "rows": len(merged_seed),
            "by_condition": count_field(merged_seed, "condition"),
            "by_surface": count_by_surface(merged_seed),
            "target_predicate_preserved": count_field(merged_seed, "target_predicate_preserved"),
            "relation_skeleton_quality": count_field(merged_seed, "relation_skeleton_quality"),
            "numeric_role_slot_quality": count_field(merged_seed, "numeric_role_slot_quality"),
            "equation_surface_quality": count_field(merged_seed, "equation_surface_quality"),
            "final_answer_authority_visible": count_field(merged_seed, "final_answer_authority_visible"),
        },
        "source_label_sensitive_labels": {
            "rows": len(merged_source),
            "by_condition": count_field(merged_source, "condition"),
            "by_surface": count_by_surface(merged_source),
            "sensitivity_category": count_field(merged_source, "sensitivity_category"),
            "field_family": count_field(merged_source, "field_family"),
            "final_answer_authority_visible": count_field(merged_source, "final_answer_authority_visible"),
            "parser_surface_confound": count_field(merged_source, "parser_surface_confound"),
        },
        "unlabeled_rows": unlabeled,
        "merged_manual_seed_labels": merged_seed,
        "merged_manual_source_label_sensitive_seed_labels": merged_source,
    }


def markdown_table(counter: Dict[str, int]) -> List[str]:
    lines = ["| Value | Rows |", "| --- | ---: |"]
    for key, value in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{key}` | {value} |")
    return lines


def build_markdown(payload: Dict[str, Any]) -> str:
    counts = payload["counts"]
    lines = [
        "# Peer Field-Label Summary",
        "",
        "This summarizes existing manual seed labels for the MATH200 claim-hygiene packet. It does not infer new labels.",
        "",
        "## Coverage",
        "",
        f"- Packet rows: `{counts['packet_rows']}`",
        f"- Manual seed rows: `{counts['manual_seed_rows']}`",
        f"- Manual source-label-sensitive seed rows: `{counts['manual_source_label_sensitive_seed_rows']}`",
        f"- Unique labeled rows: `{counts['unique_labeled_rows']}`",
        f"- Unlabeled rows: `{counts['unlabeled_rows']}`",
        "",
        "Unlabeled by reason:",
        "",
        *markdown_table(counts["unlabeled_by_reason"]),
        "",
        "Unlabeled by surface:",
        "",
        *markdown_table(counts["unlabeled_by_surface"]),
        "",
        "## Anonymous Behavior Labels",
        "",
        "Relation skeleton quality:",
        "",
        *markdown_table(payload["anonymous_behavior_labels"]["relation_skeleton_quality"]),
        "",
        "Numeric / role slot quality:",
        "",
        *markdown_table(payload["anonymous_behavior_labels"]["numeric_role_slot_quality"]),
        "",
        "Final-answer authority visible:",
        "",
        *markdown_table(payload["anonymous_behavior_labels"]["final_answer_authority_visible"]),
        "",
        "## Source-Label-Sensitive Labels",
        "",
        "Sensitivity category:",
        "",
        *markdown_table(payload["source_label_sensitive_labels"]["sensitivity_category"]),
        "",
        "Field family:",
        "",
        *markdown_table(payload["source_label_sensitive_labels"]["field_family"]),
        "",
        "Final-answer authority visible:",
        "",
        *markdown_table(payload["source_label_sensitive_labels"]["final_answer_authority_visible"]),
        "",
        "Parser-surface confound:",
        "",
        *markdown_table(payload["source_label_sensitive_labels"]["parser_surface_confound"]),
        "",
        "## Reading Rule",
        "",
        "These are seed labels and coverage counts, not population estimates. Use the unlabeled sidecar to decide whether another manual pass is worth doing before moving to a split-evidence task.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(payload: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        key: value
        for key, value in payload.items()
        if key
        not in {
            "unlabeled_rows",
            "merged_manual_seed_labels",
            "merged_manual_source_label_sensitive_seed_labels",
        }
    }
    write_json(out_dir / "manual_label_summary.json", summary)
    write_jsonl(out_dir / "manual_unlabeled_rows.jsonl", payload["unlabeled_rows"])
    write_jsonl(out_dir / "merged_manual_seed_labels.jsonl", payload["merged_manual_seed_labels"])
    write_jsonl(
        out_dir / "merged_manual_source_label_sensitive_seed_labels.jsonl",
        payload["merged_manual_source_label_sensitive_seed_labels"],
    )
    out_dir.joinpath("manual_label_summary.md").write_text(build_markdown(payload), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--field-label-packet", type=Path, required=True)
    parser.add_argument("--manual-seed-labels", type=Path, required=True)
    parser.add_argument("--manual-source-label-sensitive-seed-labels", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    payload = build_payload(args)
    write_outputs(payload, args.out_dir)
    print(json.dumps({"counts": payload["counts"]}, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
