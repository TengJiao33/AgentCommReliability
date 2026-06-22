#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


INVALID_SUPPORT_STATES = {"rejected", "quarantined", "unverified"}
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


def parse_json_object_loose(blob: Any) -> tuple[dict[str, Any], str | None]:
    if isinstance(blob, dict):
        return blob, None
    if not isinstance(blob, str):
        return {}, "response_not_object_or_string"
    text = blob.strip()
    fence = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {}, "no_json_object"
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as error:
            return {}, f"json_decode_error: {error}"
    if not isinstance(parsed, dict):
        return {}, "response_not_object"
    return parsed, None


def as_list(blob: Any) -> list[Any]:
    return blob if isinstance(blob, list) else []


def as_str_list(blob: Any) -> list[str]:
    return [item for item in as_list(blob) if isinstance(item, str)]


def normalize_decision(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().lower().split())


def card_cost(card: dict[str, Any]) -> int:
    try:
        return max(0, int(card.get("cost", 1)))
    except (TypeError, ValueError):
        return 1


def validate_packet(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    roles = set(as_str_list(row.get("roles")))
    if not row.get("packet_id"):
        errors.append("missing_packet_id")
    if not roles:
        errors.append("missing_roles")
    if row.get("final_decider") not in roles:
        errors.append("final_decider_not_in_roles")
    budgets = row.get("role_budgets", {})
    if not isinstance(budgets, dict):
        errors.append("role_budgets_not_object")
    for role in roles:
        if role not in budgets:
            errors.append(f"missing_budget:{role}")
    card_ids: set[str] = set()
    for card in as_list(row.get("source_cards")):
        if not isinstance(card, dict) or not isinstance(card.get("card_id"), str):
            errors.append("bad_source_card")
            continue
        if card["card_id"] in card_ids:
            errors.append(f"duplicate_card_id:{card['card_id']}")
        card_ids.add(card["card_id"])
    for slot in as_list(row.get("required_slots")):
        if not isinstance(slot, dict):
            errors.append("bad_required_slot")
            continue
        for card_id in as_str_list(slot.get("acceptable_card_ids")):
            if card_id not in card_ids:
                errors.append(f"slot_unknown_card:{slot.get('slot_id')}:{card_id}")
    return errors


def unit_priority(unit: dict[str, Any]) -> float:
    try:
        return float(unit.get("priority", 0.0))
    except (TypeError, ValueError):
        return 0.0


def sorted_units(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        units,
        key=lambda unit: (-unit_priority(unit), str(unit.get("unit_id", ""))),
    )


def rejection(
    unit: dict[str, Any],
    recipient: str,
    card_ids: list[str],
    reason: str,
    details: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "unit_id": unit.get("unit_id"),
        "recipient": recipient,
        "card_ids": card_ids,
        "reason": reason,
        "details": details or [],
        "priority": unit_priority(unit),
    }


def card_is_supporting(card: dict[str, Any], required_state: str = "verified") -> bool:
    state = str(card.get("verification_state", ""))
    if required_state == "unverified_allowed":
        return state not in {"rejected", "quarantined"}
    return state == "verified"


def compile_units(packet: dict[str, Any], parsed: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    cards = {card["card_id"]: card for card in as_list(packet.get("source_cards")) if isinstance(card, dict) and "card_id" in card}
    roles = set(as_str_list(packet.get("roles")))
    budgets = {
        role: int(packet.get("role_budgets", {}).get(role, 0))
        for role in roles
    }
    spent = {role: 0 for role in roles}
    admitted_card_ids = {role: set() for role in roles}
    admitted_units: list[dict[str, Any]] = []
    rejected_units: list[dict[str, Any]] = []
    stats: dict[str, Any] = {
        "role_budget": budgets,
        "role_spent": spent,
        "scope_violations_prevented": 0,
        "invalid_support_prevented": 0,
        "budget_rejections": 0,
        "unknown_card_rejections": 0,
    }

    candidate_units = [unit for unit in as_list(parsed.get("candidate_units")) if isinstance(unit, dict)]
    for unit in sorted_units(candidate_units):
        recipient = str(unit.get("recipient", ""))
        card_ids = as_str_list(unit.get("card_ids"))
        if recipient not in roles:
            rejected_units.append(rejection(unit, recipient, card_ids, "unknown_recipient"))
            continue
        if not card_ids:
            rejected_units.append(rejection(unit, recipient, card_ids, "empty_unit"))
            continue

        details: list[str] = []
        unit_cards: list[dict[str, Any]] = []
        for card_id in card_ids:
            card = cards.get(card_id)
            if card is None:
                details.append(f"unknown_card:{card_id}")
                stats["unknown_card_rejections"] += 1
                continue
            if recipient not in set(as_str_list(card.get("recipient_scope"))):
                details.append(f"out_of_scope:{card_id}")
                stats["scope_violations_prevented"] += 1
                continue
            if str(card.get("verification_state")) in INVALID_SUPPORT_STATES:
                details.append(f"invalid_support:{card_id}:{card.get('verification_state')}")
                stats["invalid_support_prevented"] += 1
                continue
            unit_cards.append(card)
        if details:
            rejected_units.append(rejection(unit, recipient, card_ids, "hard_constraint_reject", details))
            continue

        new_cost = sum(card_cost(card) for card in unit_cards if card["card_id"] not in admitted_card_ids[recipient])
        if spent[recipient] + new_cost > budgets[recipient]:
            stats["budget_rejections"] += 1
            rejected_units.append(rejection(unit, recipient, card_ids, "over_budget", [f"needed:{new_cost}", f"remaining:{budgets[recipient] - spent[recipient]}"]))
            continue

        for card in unit_cards:
            if card["card_id"] not in admitted_card_ids[recipient]:
                admitted_card_ids[recipient].add(card["card_id"])
                spent[recipient] += card_cost(card)
        admitted_units.append(
            {
                "unit_id": unit.get("unit_id"),
                "recipient": recipient,
                "card_ids": card_ids,
                "claimed_slots": as_str_list(unit.get("claimed_slots")),
                "claimed_effect": unit.get("claimed_effect"),
                "priority": unit_priority(unit),
            }
        )
    return admitted_units, rejected_units, stats


def model_only_units(packet: dict[str, Any], parsed: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    cards = {card["card_id"]: card for card in as_list(packet.get("source_cards")) if isinstance(card, dict) and "card_id" in card}
    roles = set(as_str_list(packet.get("roles")))
    budgets = {
        role: int(packet.get("role_budgets", {}).get(role, 0))
        for role in roles
    }
    spent = {role: 0 for role in roles}
    admitted_card_ids = {role: set() for role in roles}
    admitted_units: list[dict[str, Any]] = []
    stats: dict[str, Any] = {
        "role_budget": budgets,
        "role_spent": spent,
        "scope_violations_prevented": 0,
        "invalid_support_prevented": 0,
        "budget_rejections": 0,
        "unknown_card_rejections": 0,
        "scope_violations_unprevented": 0,
        "invalid_support_unprevented": 0,
        "unknown_card_attempts": 0,
        "unknown_recipient_attempts": 0,
        "budget_overrun_raw": 0,
    }

    candidate_units = [unit for unit in as_list(parsed.get("candidate_units")) if isinstance(unit, dict)]
    for unit in candidate_units:
        recipient = str(unit.get("recipient", ""))
        card_ids = as_str_list(unit.get("card_ids"))
        if recipient not in roles:
            stats["unknown_recipient_attempts"] += 1
        for card_id in card_ids:
            card = cards.get(card_id)
            if card is None:
                stats["unknown_card_attempts"] += 1
                continue
            if recipient in roles:
                if card_id not in admitted_card_ids[recipient]:
                    admitted_card_ids[recipient].add(card_id)
                    spent[recipient] += card_cost(card)
                if recipient not in set(as_str_list(card.get("recipient_scope"))):
                    stats["scope_violations_unprevented"] += 1
            if str(card.get("verification_state")) in INVALID_SUPPORT_STATES:
                stats["invalid_support_unprevented"] += 1
        admitted_units.append(
            {
                "unit_id": unit.get("unit_id"),
                "recipient": recipient,
                "card_ids": card_ids,
                "claimed_slots": as_str_list(unit.get("claimed_slots")),
                "claimed_effect": unit.get("claimed_effect"),
                "priority": unit_priority(unit),
            }
        )

    stats["budget_overrun_raw"] = sum(max(0, spent[role] - budgets[role]) for role in roles)
    return admitted_units, [], stats


def build_slot_table(packet: dict[str, Any], admitted_units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards = {card["card_id"]: card for card in as_list(packet.get("source_cards")) if isinstance(card, dict) and "card_id" in card}
    admitted_by_recipient: dict[str, set[str]] = {}
    for unit in admitted_units:
        recipient = str(unit.get("recipient", ""))
        admitted_by_recipient.setdefault(recipient, set()).update(as_str_list(unit.get("card_ids")))

    rows: list[dict[str, Any]] = []
    for slot in as_list(packet.get("required_slots")):
        if not isinstance(slot, dict):
            continue
        recipient = str(slot.get("recipient", ""))
        acceptable = as_str_list(slot.get("acceptable_card_ids"))
        admitted = [card_id for card_id in acceptable if card_id in admitted_by_recipient.get(recipient, set())]
        status = "missing"
        reason = None
        if admitted:
            status = "satisfied"
        else:
            scoped_cards = [
                cards[card_id]
                for card_id in acceptable
                if card_id in cards and recipient in set(as_str_list(cards[card_id].get("recipient_scope")))
            ]
            if not scoped_cards:
                status = "not_visible"
                reason = "no_acceptable_card_in_recipient_scope"
            elif any(not card_is_supporting(card, str(slot.get("required_state", "verified"))) for card in scoped_cards):
                status = "blocked_by_rejection"
                reason = "acceptable_card_not_supporting"
        rows.append(
            {
                "slot_id": slot.get("slot_id"),
                "recipient": recipient,
                "option": slot.get("option"),
                "polarity": slot.get("polarity"),
                "status": status,
                "satisfying_cards": admitted,
                "blocking_reason": reason,
            }
        )
    return rows


def decide(packet: dict[str, Any], parsed: dict[str, Any], slot_table: list[dict[str, Any]]) -> dict[str, Any]:
    options = [option for option in as_str_list(packet.get("candidate_options")) if normalize_decision(option) != INSUFFICIENT]
    rows_by_option: dict[str, list[dict[str, Any]]] = {option: [] for option in options}
    for row in slot_table:
        option = row.get("option")
        if option in rows_by_option:
            rows_by_option[option].append(row)

    option_states: list[dict[str, Any]] = []
    enabled: list[str] = []
    for option in options:
        rows = rows_by_option[option]
        support_rows = [row for row in rows if row.get("polarity") in {"support", "enabler", "constraint"}]
        blocker_rows = [row for row in rows if row.get("polarity") in {"blocker", "exclusion"}]
        support_ok = bool(support_rows) and all(row.get("status") == "satisfied" for row in support_rows)
        blocker_hit = any(row.get("status") == "satisfied" for row in blocker_rows)
        if blocker_hit:
            state = "blocked"
        elif support_ok:
            state = "enabled"
            enabled.append(option)
        else:
            state = "insufficient"
        option_states.append(
            {
                "option": option,
                "state": state,
                "support_slots": [row.get("slot_id") for row in support_rows],
                "blocker_slots": [row.get("slot_id") for row in blocker_rows],
            }
        )

    if len(enabled) == 1:
        decision = enabled[0]
        status = "committed"
    else:
        decision = INSUFFICIENT
        status = "insufficient"

    model_decision = parsed.get("final_decision")
    if isinstance(model_decision, dict):
        model_decision = model_decision.get("decision") or model_decision.get("answer")
    forced = (
        status == "insufficient"
        and isinstance(model_decision, str)
        and normalize_decision(model_decision) not in {"", INSUFFICIENT, "insufficient", "none", "null"}
    )
    return {
        "decision": decision,
        "decision_status": status,
        "enabled_options": enabled,
        "option_states": option_states,
        "model_proposed_decision": model_decision,
        "forced_commitment_detected": forced,
    }


def model_only_decide(packet: dict[str, Any], parsed: dict[str, Any], gate_state: dict[str, Any]) -> dict[str, Any]:
    candidate_options = as_str_list(packet.get("candidate_options"))
    normalized_options = {normalize_decision(option): option for option in candidate_options}
    model_decision = parsed.get("final_decision")
    if isinstance(model_decision, dict):
        model_decision = model_decision.get("decision") or model_decision.get("answer")
    if not isinstance(model_decision, str):
        decision = INSUFFICIENT
    else:
        decision = normalized_options.get(normalize_decision(model_decision), model_decision)

    concrete_decision = normalize_decision(decision) not in {"", INSUFFICIENT, "insufficient", "none", "null"}
    gate_decision = normalize_decision(gate_state.get("decision"))
    forced = concrete_decision and gate_decision != normalize_decision(decision)
    return {
        "decision": decision,
        "decision_status": "model_committed" if concrete_decision else "model_insufficient",
        "enabled_options": gate_state.get("enabled_options", []),
        "option_states": gate_state.get("option_states", []),
        "model_proposed_decision": model_decision,
        "compiler_gate_decision": gate_state.get("decision"),
        "compiler_gate_status": gate_state.get("decision_status"),
        "forced_commitment_detected": forced,
    }


def compile_row(packet: dict[str, Any], prediction: dict[str, Any], mode: str = "compiler") -> dict[str, Any]:
    validation_errors = validate_packet(packet)
    parsed, parse_error = parse_json_object_loose(prediction.get("response"))
    if validation_errors or parse_error:
        return {
            "packet_id": packet.get("packet_id"),
            "status": "error",
            "validation_errors": validation_errors,
            "parse_error": parse_error,
            "model": prediction.get("model"),
        }

    if mode == "model_only":
        admitted_units, rejected_units, stats = model_only_units(packet, parsed)
    else:
        admitted_units, rejected_units, stats = compile_units(packet, parsed)
    slot_table = build_slot_table(packet, admitted_units)
    gate_state = decide(packet, parsed, slot_table)
    final_state = model_only_decide(packet, parsed, gate_state) if mode == "model_only" else gate_state
    expected = packet.get("expected_final_decision")
    downstream_ok = None
    if isinstance(expected, str):
        downstream_ok = float(normalize_decision(expected) == normalize_decision(final_state["decision"]))
    return {
        "packet_id": packet["packet_id"],
        "task_id": packet.get("task_id"),
        "benchmark": packet.get("benchmark"),
        "condition": "structured_no_compiler" if mode == "model_only" else "ours_sseac_v0",
        "status": "ok",
        "model": prediction.get("model"),
        "compile_mode": mode,
        "admitted_units": admitted_units,
        "rejected_units": rejected_units,
        "slot_table": slot_table,
        "final_state": final_state,
        "metrics_debug": {
            **stats,
            "downstream_ok": downstream_ok,
            "forced_commitment_detected": float(final_state["forced_commitment_detected"]),
            "admitted_unit_count": len(admitted_units),
            "rejected_unit_count": len(rejected_units),
        },
        "raw_model_output": parsed,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    n = len(ok_rows)
    def avg_metric(key: str) -> float:
        vals = [
            float(row.get("metrics_debug", {}).get(key))
            for row in ok_rows
            if row.get("metrics_debug", {}).get(key) is not None
        ]
        return sum(vals) / len(vals) if vals else 0.0

    return {
        "rows": len(rows),
        "ok_rows": n,
        "error_rows": len(rows) - n,
        "scope_violations_prevented": sum(int(row.get("metrics_debug", {}).get("scope_violations_prevented", 0)) for row in ok_rows),
        "invalid_support_prevented": sum(int(row.get("metrics_debug", {}).get("invalid_support_prevented", 0)) for row in ok_rows),
        "budget_rejections": sum(int(row.get("metrics_debug", {}).get("budget_rejections", 0)) for row in ok_rows),
        "forced_commitment_rate": avg_metric("forced_commitment_detected"),
        "downstream_ok": avg_metric("downstream_ok"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--mode", choices=["compiler", "model_only"], default="compiler")
    args = parser.parse_args()

    packet_rows = read_jsonl(args.packet)
    prediction_rows = {row.get("packet_id"): row for row in read_jsonl(args.predictions)}
    compiled = [
        compile_row(packet, prediction_rows.get(packet.get("packet_id"), {}), args.mode)
        for packet in packet_rows
    ]
    write_jsonl(args.out, compiled)
    summary = summarize(compiled)
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
