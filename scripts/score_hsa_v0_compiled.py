#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


INSUFFICIENT = "insufficient_evidence"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def norm(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def slot_recall(compiled: dict[str, Any]) -> float:
    slots = [slot for slot in compiled.get("slot_table", []) if isinstance(slot, dict)]
    if not slots:
        return 0.0
    return sum(1 for slot in slots if slot.get("status") == "satisfied") / len(slots)


def final_admitted_cards(compiled: dict[str, Any], final_decider: str) -> set[str]:
    out: set[str] = set()
    for unit in compiled.get("admitted_units", []):
        if not isinstance(unit, dict) or unit.get("recipient") != final_decider:
            continue
        for card_id in unit.get("card_ids", []):
            if isinstance(card_id, str):
                out.add(card_id)
    return out


def required_cards(packet: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for slot in packet.get("required_slots", []):
        for card_id in slot.get("acceptable_card_ids", []):
            if isinstance(card_id, str):
                out.add(card_id)
    return out


def score_row(packet: dict[str, Any], compiled: dict[str, Any]) -> dict[str, Any]:
    expected = packet.get("expected_final_decision")
    decision = compiled.get("final_state", {}).get("decision")
    final_decider = packet.get("final_decider")
    admitted = final_admitted_cards(compiled, str(final_decider))
    required = required_cards(packet)
    extra = admitted - required
    return {
        "packet_id": packet.get("packet_id"),
        "sketch_id": packet.get("hsa_meta", {}).get("sketch_id"),
        "variant_id": packet.get("hsa_meta", {}).get("variant_id"),
        "condition": packet.get("hsa_meta", {}).get("condition"),
        "compile_status": compiled.get("status"),
        "expected_final_decision": expected,
        "compiled_decision": decision,
        "strict": float(norm(expected) == norm(decision)),
        "expected_insufficient": float(norm(expected) == INSUFFICIENT),
        "compiled_insufficient": float(norm(decision) == INSUFFICIENT),
        "slot_recall": slot_recall(compiled),
        "admitted_final_cards": sorted(admitted),
        "required_cards": sorted(required),
        "extra_final_card_count": len(extra),
        "scope_violations_prevented": compiled.get("metrics_debug", {}).get("scope_violations_prevented", 0),
        "invalid_support_prevented": compiled.get("metrics_debug", {}).get("invalid_support_prevented", 0),
        "budget_rejections": compiled.get("metrics_debug", {}).get("budget_rejections", 0),
        "forced_commitment_detected": compiled.get("metrics_debug", {}).get("forced_commitment_detected", 0.0),
    }


def average(rows: list[dict[str, Any]], key: str) -> float:
    vals = [float(row.get(key, 0.0)) for row in rows]
    return sum(vals) / len(vals) if vals else 0.0


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    base = [row for row in rows if row.get("condition") == "base"]
    pert = [row for row in rows if row.get("condition") == "perturbation"]
    return {
        "rows": len(rows),
        "strict": sum(int(row.get("strict", 0.0)) for row in rows),
        "strict_rate": average(rows, "strict"),
        "base_rows": len(base),
        "base_strict_rate": average(base, "strict"),
        "perturbation_rows": len(pert),
        "perturbation_strict_rate": average(pert, "strict"),
        "slot_recall": average(rows, "slot_recall"),
        "extra_final_card_count": sum(int(row.get("extra_final_card_count", 0)) for row in rows),
        "scope_violations_prevented": sum(int(row.get("scope_violations_prevented", 0)) for row in rows),
        "invalid_support_prevented": sum(int(row.get("invalid_support_prevented", 0)) for row in rows),
        "budget_rejections": sum(int(row.get("budget_rejections", 0)) for row in rows),
        "forced_commitment_rate": average(rows, "forced_commitment_detected"),
    }


def format_summary(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# HSA-v0 Compiled Summary",
            "",
            f"- rows: `{summary['rows']}`",
            f"- strict: `{summary['strict']}/{summary['rows']}`",
            f"- strict_rate: `{summary['strict_rate']:.4f}`",
            f"- base_strict_rate: `{summary['base_strict_rate']:.4f}` over `{summary['base_rows']}` rows",
            f"- perturbation_strict_rate: `{summary['perturbation_strict_rate']:.4f}` over `{summary['perturbation_rows']}` rows",
            f"- slot_recall: `{summary['slot_recall']:.4f}`",
            f"- extra_final_card_count: `{summary['extra_final_card_count']}`",
            f"- scope_violations_prevented: `{summary['scope_violations_prevented']}`",
            f"- invalid_support_prevented: `{summary['invalid_support_prevented']}`",
            f"- budget_rejections: `{summary['budget_rejections']}`",
            f"- forced_commitment_rate: `{summary['forced_commitment_rate']:.4f}`",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--compiled", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    args = parser.parse_args()

    packets = {row["packet_id"]: row for row in read_jsonl(args.packet)}
    rows = []
    for compiled in read_jsonl(args.compiled):
        packet_id = compiled.get("packet_id")
        if packet_id not in packets:
            raise KeyError(f"compiled row does not match packet: {packet_id}")
        rows.append(score_row(packets[packet_id], compiled))
    write_jsonl(args.out, rows)
    summary = summarize(rows)
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(format_summary(summary) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
