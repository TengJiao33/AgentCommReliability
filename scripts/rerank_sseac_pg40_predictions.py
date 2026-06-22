#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


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


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_str_list(value: Any) -> list[str]:
    return [item for item in as_list(value) if isinstance(item, str)]


def unit_priority(unit: dict[str, Any]) -> float:
    try:
        return float(unit.get("priority", 0.0))
    except (TypeError, ValueError):
        return 0.0


def card_cost(card: dict[str, Any]) -> int:
    try:
        return max(0, int(card.get("cost", 1)))
    except (TypeError, ValueError):
        return 1


def rejection_card_ids(response: dict[str, Any]) -> set[str]:
    rejected: set[str] = set()
    for item in as_list(response.get("proposed_rejections")):
        if not isinstance(item, dict):
            continue
        card_id = item.get("card_id") or item.get("fragment_id")
        if isinstance(card_id, str):
            rejected.add(card_id)
    return rejected


def visible_support_card(card: dict[str, Any]) -> bool:
    return (
        str(card.get("verification_state")) == "verified"
        and str(card.get("evidence_type")) != "distractor"
        and bool(as_str_list(card.get("recipient_scope")))
    )


def unit_key(recipient: str, card_id: str) -> tuple[str, str]:
    return recipient, card_id


def build_reranked_response(
    packet: dict[str, Any],
    response: dict[str, Any],
    *,
    project_scope: bool,
    prune_to_budget: bool,
    cost_penalty: float,
    projection_penalty: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    roles = set(as_str_list(packet.get("roles")))
    cards = {
        card["card_id"]: card
        for card in as_list(packet.get("source_cards"))
        if isinstance(card, dict) and isinstance(card.get("card_id"), str)
    }
    rejected_ids = rejection_card_ids(response)
    candidates: dict[tuple[str, str], dict[str, Any]] = {}

    def add_candidate(
        *,
        recipient: str,
        card_id: str,
        source_unit: dict[str, Any],
        projected: bool,
    ) -> None:
        card = cards.get(card_id)
        if recipient not in roles or card is None:
            return
        if card_id in rejected_ids or not visible_support_card(card):
            return
        if recipient not in set(as_str_list(card.get("recipient_scope"))):
            return

        base_priority = unit_priority(source_unit)
        priority = base_priority - (card_cost(card) * cost_penalty)
        if projected:
            priority -= projection_penalty

        key = unit_key(recipient, card_id)
        previous = candidates.get(key)
        if previous is not None and unit_priority(previous) >= priority:
            return

        source = "scope_projection" if projected else "model_original"
        candidates[key] = {
            "unit_id": f"{source}::{recipient}::{card_id}",
            "recipient": recipient,
            "card_ids": [card_id],
            "priority": priority,
            "claimed_slots": [f"{recipient}::{card_id}"],
            "claimed_effect": source,
            "rerank_debug": {
                "source": source,
                "source_unit_id": source_unit.get("unit_id"),
                "source_recipient": source_unit.get("recipient"),
                "source_priority": base_priority,
                "cost": card_cost(card),
            },
        }

    for unit in as_list(response.get("candidate_units")):
        if not isinstance(unit, dict):
            continue
        recipient = str(unit.get("recipient", ""))
        card_ids = as_str_list(unit.get("card_ids"))
        if len(card_ids) != 1:
            continue
        card_id = card_ids[0]
        add_candidate(recipient=recipient, card_id=card_id, source_unit=unit, projected=False)
        if project_scope and card_id in cards:
            for scoped_role in as_str_list(cards[card_id].get("recipient_scope")):
                if scoped_role != recipient:
                    add_candidate(recipient=scoped_role, card_id=card_id, source_unit=unit, projected=True)

    candidate_units_all = sorted(
        candidates.values(),
        key=lambda item: (-unit_priority(item), str(item.get("recipient", "")), str(item.get("unit_id", ""))),
    )
    pruned_units = 0
    if prune_to_budget:
        budgets = {
            role: int(packet.get("role_budgets", {}).get(role, 0))
            for role in roles
        }
        spent = {role: 0 for role in roles}
        seen_by_role = {role: set() for role in roles}
        candidate_units: list[dict[str, Any]] = []
        for unit in candidate_units_all:
            recipient = str(unit.get("recipient", ""))
            if recipient not in roles:
                pruned_units += 1
                continue
            new_cost = 0
            for card_id in as_str_list(unit.get("card_ids")):
                if card_id not in seen_by_role[recipient] and card_id in cards:
                    new_cost += card_cost(cards[card_id])
            if spent[recipient] + new_cost > budgets[recipient]:
                pruned_units += 1
                continue
            for card_id in as_str_list(unit.get("card_ids")):
                if card_id not in seen_by_role[recipient] and card_id in cards:
                    seen_by_role[recipient].add(card_id)
                    spent[recipient] += card_cost(cards[card_id])
            candidate_units.append(unit)
    else:
        candidate_units = candidate_units_all
    option_states = [
        {
            "option": "routing_complete",
            "state": "enabled" if candidate_units else "insufficient",
            "supporting_slots": [
                slot
                for unit in candidate_units
                for slot in as_str_list(unit.get("claimed_slots"))
            ],
            "blocking_slots": [],
            "missing_slots": [],
        }
    ]
    reranked = {
        **response,
        "option_states": option_states,
        "candidate_units": candidate_units,
        "final_decision": response.get("final_decision", "routing_complete"),
        "rerank_strategy": {
            "name": "scope_project_cost_rank" if project_scope else "cost_rank",
            "project_scope": project_scope,
            "prune_to_budget": prune_to_budget,
            "cost_penalty": cost_penalty,
            "projection_penalty": projection_penalty,
            "visible_fields_used": [
                "source_cards.card_id",
                "source_cards.recipient_scope",
                "source_cards.verification_state",
                "source_cards.evidence_type",
                "source_cards.cost",
                "roles",
                "model candidate_units",
                "model proposed_rejections",
            ],
            "forbidden_fields_not_used": [
                "required_slots",
                "acceptable_card_ids",
                "expected_final_decision",
                "reference_need_sets",
                "candidate_need_sets",
                "role_utilities",
            ],
        },
    }
    diagnostics = {
        "candidate_units_in": len(as_list(response.get("candidate_units"))),
        "candidate_units_out": len(candidate_units),
        "candidate_units_before_prune": len(candidate_units_all),
        "projected_units": sum(
            1
            for unit in candidate_units
            if unit.get("rerank_debug", {}).get("source") == "scope_projection"
        ),
        "pruned_units": pruned_units,
    }
    return reranked, diagnostics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--project-scope", action="store_true")
    parser.add_argument("--prune-to-budget", action="store_true")
    parser.add_argument("--cost-penalty", type=float, default=3.0)
    parser.add_argument("--projection-penalty", type=float, default=0.25)
    args = parser.parse_args()

    packets = {row.get("packet_id"): row for row in read_jsonl(args.packet)}
    output_rows: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    for prediction in read_jsonl(args.predictions):
        packet_id = prediction.get("packet_id")
        packet = packets.get(packet_id)
        response = prediction.get("response")
        if packet is None or not isinstance(response, dict):
            output_rows.append(prediction)
            diagnostics.append(
                {
                    "packet_id": packet_id,
                    "status": "skipped",
                    "reason": "missing_packet_or_response_not_object",
                }
            )
            continue
        reranked, row_diag = build_reranked_response(
            packet,
            response,
            project_scope=args.project_scope,
            prune_to_budget=args.prune_to_budget,
            cost_penalty=args.cost_penalty,
            projection_penalty=args.projection_penalty,
        )
        output_rows.append(
            {
                **prediction,
                "model": f"{prediction.get('model', 'unknown')}+{reranked['rerank_strategy']['name']}",
                "response": reranked,
            }
        )
        diagnostics.append({"packet_id": packet_id, "status": "ok", **row_diag})

    write_jsonl(args.out, output_rows)
    summary = {
        "rows": len(output_rows),
        "ok_rows": sum(1 for item in diagnostics if item.get("status") == "ok"),
        "skipped_rows": sum(1 for item in diagnostics if item.get("status") != "ok"),
        "candidate_units_in": sum(int(item.get("candidate_units_in", 0)) for item in diagnostics),
        "candidate_units_before_prune": sum(int(item.get("candidate_units_before_prune", 0)) for item in diagnostics),
        "candidate_units_out": sum(int(item.get("candidate_units_out", 0)) for item in diagnostics),
        "projected_units": sum(int(item.get("projected_units", 0)) for item in diagnostics),
        "pruned_units": sum(int(item.get("pruned_units", 0)) for item in diagnostics),
        "project_scope": args.project_scope,
        "prune_to_budget": args.prune_to_budget,
        "cost_penalty": args.cost_penalty,
        "projection_penalty": args.projection_penalty,
    }
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
