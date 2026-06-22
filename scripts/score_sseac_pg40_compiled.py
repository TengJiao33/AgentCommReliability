#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from score_perspectivegap_tight_budget import (
    add_tight_metrics,
    format_tight_summary,
    read_jsonl,
    score_packet_row,
    summarize_tight,
    write_jsonl,
)


def visibility_from_selected_roles(selected_roles: list[str], all_roles: list[str]) -> str:
    if len(selected_roles) == len(all_roles):
        return "shared_all"
    if len(selected_roles) > 1:
        return "shared_subset"
    return "role_private"


def response_from_compiled(row: dict[str, Any], compiled: dict[str, Any]) -> str:
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    roles = list(row["roles"])
    selected_by_role: dict[str, list[str]] = {role: [] for role in roles}
    for unit in compiled.get("admitted_units", []):
        if not isinstance(unit, dict):
            continue
        role = unit.get("recipient")
        if role not in selected_by_role:
            continue
        for card_id in unit.get("card_ids", []):
            if isinstance(card_id, str) and card_id in fragments and card_id not in selected_by_role[role]:
                selected_by_role[role].append(card_id)

    selected_roles_by_fragment: dict[str, list[str]] = {}
    for role, fragment_ids in selected_by_role.items():
        for fragment_id in fragment_ids:
            selected_roles_by_fragment.setdefault(fragment_id, []).append(role)
    for fragment_id in selected_roles_by_fragment:
        selected_roles_by_fragment[fragment_id].sort(key=roles.index)

    response: dict[str, Any] = {"roles": {}, "rejected": []}
    for role in roles:
        cards: list[dict[str, Any]] = []
        for fragment_id in selected_by_role[role]:
            fragment = fragments[fragment_id]
            cards.append(
                {
                    "fragment_id": fragment_id,
                    "source_id": fragment["source_id"],
                    "visibility": visibility_from_selected_roles(selected_roles_by_fragment[fragment_id], roles),
                    "reason": "sseac_compiled_admission",
                }
            )
        response["roles"][role] = cards

    for unit in compiled.get("rejected_units", []):
        if not isinstance(unit, dict):
            continue
        for card_id in unit.get("card_ids", []):
            if isinstance(card_id, str) and card_id in fragments:
                response["rejected"].append(
                    {
                        "fragment_id": card_id,
                        "source_id": fragments[card_id]["source_id"],
                        "reason": unit.get("reason", "sseac_rejected"),
                    }
                )
    raw = compiled.get("raw_model_output", {})
    proposed_rejections = raw.get("proposed_rejections", []) if isinstance(raw, dict) else []
    if isinstance(proposed_rejections, list):
        for item in proposed_rejections:
            if not isinstance(item, dict):
                continue
            fragment_id = item.get("fragment_id") or item.get("card_id")
            if isinstance(fragment_id, str) and fragment_id in fragments:
                response["rejected"].append(
                    {
                        "fragment_id": fragment_id,
                        "source_id": fragments[fragment_id]["source_id"],
                        "reason": item.get("reason", "model_proposed_rejection"),
                    }
                )
    return json.dumps(response, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pg-packet", type=Path, required=True)
    parser.add_argument("--compiled", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    args = parser.parse_args()

    pg_rows = {row["hard_evaluation_id"]: row for row in read_jsonl(args.pg_packet)}
    compiled_rows = read_jsonl(args.compiled)
    scored: list[dict[str, Any]] = []
    for compiled in compiled_rows:
        packet_id = compiled.get("packet_id")
        row = pg_rows.get(packet_id)
        if row is None:
            raise KeyError(f"compiled row does not match PG packet: {packet_id}")
        response = response_from_compiled(row, compiled)
        scored_row = add_tight_metrics(row, response, score_packet_row(row, response))
        scored_row["sseac_compile_status"] = compiled.get("status")
        scored_row["sseac_final_state"] = compiled.get("final_state")
        scored_row["sseac_metrics_debug"] = compiled.get("metrics_debug")
        scored.append(scored_row)
    write_jsonl(args.out, scored)
    summary = summarize_tight(scored)
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(format_tight_summary(summary) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
