#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PACKET = Path("experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl")
ROUTING_COMPLETE = "routing_complete"
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


def source_card(fragment: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    eligible = list(fragment.get("candidate_needed_by") or fragment.get("eligible_by") or fragment.get("needed_by") or [])
    if fragment.get("is_distractor"):
        evidence_type = "distractor"
    elif eligible:
        evidence_type = "support"
    else:
        evidence_type = "background"
    return {
        "card_id": fragment["id"],
        "source_id": fragment["source_id"],
        "source_role": "perspectivegap_fragment",
        "content": fragment.get("text", ""),
        "recipient_scope": eligible,
        "visibility": "role_scoped" if len(eligible) == 1 else ("shared" if len(eligible) > 1 else "private"),
        "verification_state": "verified",
        "evidence_type": evidence_type,
        "cost": int(fragment.get("cost", 1)),
        "provenance": {
            "benchmark": "PerspectiveGap",
            "scenario_id": row.get("scenario_id"),
            "shuffle_seed": row.get("shuffle_seed"),
            "hard_evaluation_id": row.get("hard_evaluation_id"),
            "tight_budget_variant": row.get("tight_budget_variant"),
            "fragment_id": fragment.get("id"),
        },
    }


def slot_id(role: str, fragment_id: str) -> str:
    return f"{role}::{fragment_id}"


def build_sseac_row(row: dict[str, Any]) -> dict[str, Any]:
    roles = list(row["roles"])
    required_slots: list[dict[str, Any]] = []
    for role in roles:
        for fragment_id in row.get("reference_need_sets", {}).get(role, []):
            required_slots.append(
                {
                    "slot_id": slot_id(role, fragment_id),
                    "recipient": role,
                    "option": ROUTING_COMPLETE,
                    "polarity": "support",
                    "acceptable_card_ids": [fragment_id],
                    "required_state": "verified",
                }
            )
    return {
        "packet_id": row["hard_evaluation_id"],
        "task_id": row["hard_evaluation_id"],
        "benchmark": "PerspectiveGap-tight-budget",
        "roles": roles,
        "final_decider": roles[0],
        "candidate_options": [ROUTING_COMPLETE, INSUFFICIENT],
        "role_budgets": {role: int(row["role_budgets"][role]) for role in roles},
        "decision_rule": "routing_complete iff every oracle routing slot is satisfied; otherwise insufficient_evidence",
        "expected_final_decision": ROUTING_COMPLETE,
        "source_cards": [source_card(fragment, row) for fragment in row["fragments"]],
        "required_slots": required_slots,
        "sseac_adapter_meta": {
            "source_hard_evaluation_id": row.get("source_hard_evaluation_id"),
            "base_evaluation_id": row.get("base_evaluation_id"),
            "scenario_id": row.get("scenario_id"),
            "shuffle_seed": row.get("shuffle_seed"),
            "source_perturbation_variant": row.get("source_perturbation_variant"),
            "tight_budget_variant": row.get("tight_budget_variant"),
            "reference_need_sets": row.get("reference_need_sets"),
            "candidate_need_sets": row.get("candidate_need_sets"),
        },
    }


def build_oracle_prediction(row: dict[str, Any]) -> dict[str, Any]:
    candidate_units: list[dict[str, Any]] = []
    for role in row["roles"]:
        utilities = row.get("role_utilities", {}).get(role, {})
        for fragment_id in row.get("reference_need_sets", {}).get(role, []):
            candidate_units.append(
                {
                    "unit_id": f"oracle::{role}::{fragment_id}",
                    "recipient": role,
                    "card_ids": [fragment_id],
                    "priority": float(utilities.get(fragment_id, 1.0)),
                    "claimed_slots": [slot_id(role, fragment_id)],
                    "claimed_effect": "satisfies oracle routing slot",
                }
            )
    return {
        "packet_id": row["hard_evaluation_id"],
        "model": "oracle_pg40_to_sseac_adapter",
        "response": {
            "option_states": [
                {
                    "option": ROUTING_COMPLETE,
                    "state": "enabled",
                    "supporting_slots": [
                        slot_id(role, fragment_id)
                        for role in row["roles"]
                        for fragment_id in row.get("reference_need_sets", {}).get(role, [])
                    ],
                    "blocking_slots": [],
                    "missing_slots": [],
                }
            ],
            "candidate_units": candidate_units,
            "proposed_rejections": [],
            "final_decision": ROUTING_COMPLETE,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--oracle-predictions-out", type=Path)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    rows = read_jsonl(args.packet)
    if args.limit:
        rows = rows[: args.limit]
    write_jsonl(args.out, [build_sseac_row(row) for row in rows])
    if args.oracle_predictions_out:
        write_jsonl(args.oracle_predictions_out, [build_oracle_prediction(row) for row in rows])
    print(
        json.dumps(
            {
                "rows": len(rows),
                "out": str(args.out),
                "oracle_predictions_out": str(args.oracle_predictions_out) if args.oracle_predictions_out else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
