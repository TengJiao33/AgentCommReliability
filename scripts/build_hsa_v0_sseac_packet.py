#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_FACT_DRAFT = Path("experiments/20260618-local-state-admission-v2-preflight/hiddenbench_fact_units.draft.json")
DEFAULT_PERT_DRAFT = Path("experiments/20260618-local-state-admission-v2-preflight/source_scope_perturbations.draft.json")
DEFAULT_OUT_DIR = Path("experiments/20260618-local-hsa-v0-sseac-adapter")
INSUFFICIENT = "insufficient_evidence"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_state(value: str, fallback_recipients: list[str]) -> dict[str, Any]:
    if ":" in value:
        kind, recipients = value.split(":", 1)
        eligible = [item.strip() for item in recipients.split(",") if item.strip()]
    else:
        kind = value
        eligible = list(fallback_recipients)
    if "quarantined" in kind:
        verification = "quarantined"
    elif "unverified" in kind:
        verification = "unverified"
    elif "rejected" in kind:
        verification = "rejected"
    else:
        verification = "verified"
    return {"source_kind": kind, "verification_state": verification, "recipient_scope": eligible}


def base_fact_state(fact: dict[str, Any], state_map: dict[str, str]) -> dict[str, Any]:
    fallback = list(fact.get("candidate_recipients", []))
    if fact["fact_id"] in state_map:
        return parse_state(state_map[fact["fact_id"]], fallback)
    if fact.get("channel") == "shared":
        return {"source_kind": "shared_context", "verification_state": "verified", "recipient_scope": fallback}
    return {"source_kind": "hidden_observation", "verification_state": "verified", "recipient_scope": fallback}


def apply_variant_override(fact_id: str, state: dict[str, Any], variant_id: str) -> dict[str, Any]:
    state = dict(state)
    if variant_id == "hb10_b_hazard_quarantined" and fact_id == "hb10_hidden_3":
        state["source_kind"] = "quarantined_sensor"
        state["verification_state"] = "quarantined"
    elif variant_id == "hb10_c_enabler_no_final_scope" and fact_id == "hb10_hidden_2":
        state["recipient_scope"] = ["logistics_planner"]
    elif variant_id == "hb11_school_repair_quarantined" and fact_id == "hb11_hidden_1":
        state["source_kind"] = "unverified_repair_claim"
        state["verification_state"] = "unverified"
    elif variant_id == "hb11_library_fuel_no_final_scope" and fact_id == "hb11_hidden_0":
        state["recipient_scope"] = ["facilities_checker"]
    elif variant_id == "hb01_west_bridge_unverified" and fact_id == "hb01_shared_3":
        state["source_kind"] = "unverified_public_notice"
        state["verification_state"] = "unverified"
    elif variant_id == "hb01_north_hill_split_scope_no_group_edge" and fact_id == "hb01_hidden_2":
        state["recipient_scope"] = ["route_planner"]
    elif variant_id == "hb01_north_hill_split_scope_no_group_edge" and fact_id == "hb01_hidden_3":
        state["recipient_scope"] = ["risk_checker"]
    return state


def evidence_type(fact: dict[str, Any]) -> str:
    treatment = str(fact.get("expected_treatment", ""))
    if "blocker" in treatment:
        return "blocker"
    if "enabler" in treatment or "support" in treatment:
        return "support"
    if "reject" in treatment or "inert" in treatment:
        return "background"
    return "background"


def source_card(fact: dict[str, Any], state: dict[str, Any], sketch_id: str) -> dict[str, Any]:
    return {
        "card_id": fact["fact_id"],
        "source_id": fact["fact_id"],
        "source_role": state["source_kind"],
        "content": fact["text"],
        "recipient_scope": list(state.get("recipient_scope", [])),
        "visibility": "shared" if fact.get("channel") == "shared" else "role_scoped",
        "verification_state": state["verification_state"],
        "evidence_type": evidence_type(fact),
        "cost": 1,
        "provenance": {
            "benchmark": "HiddenBench",
            "sketch_id": sketch_id,
            "channel": fact.get("channel"),
            "expected_treatment": fact.get("expected_treatment"),
        },
    }


def unit_fact_ids(unit: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("required_fact_ids", "supporting_fact_ids"):
        for fact_id in unit.get(key, []):
            if isinstance(fact_id, str) and fact_id not in out:
                out.append(fact_id)
    return out


def required_slots(fact_row: dict[str, Any], final_decider: str) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    gold = fact_row["evaluator_metadata"]["correct_answer"]
    for unit in fact_row.get("oracle_admission_units", []):
        unit_type = str(unit.get("unit_type", ""))
        polarity = "constraint" if "blocker" in unit_type else "support"
        for fact_id in unit_fact_ids(unit):
            slots.append(
                {
                    "slot_id": f"{unit['unit_id']}::{fact_id}",
                    "recipient": final_decider,
                    "option": gold,
                    "polarity": polarity,
                    "acceptable_card_ids": [fact_id],
                    "required_state": "verified",
                    "hsa_unit_id": unit.get("unit_id"),
                    "hsa_unit_type": unit.get("unit_type"),
                    "target_option": unit.get("target_option"),
                }
            )
    return slots


def variant_expects_insufficient(variant: dict[str, Any] | None) -> bool:
    if not variant:
        return False
    text = str(variant.get("expected_downstream_delta", "")).lower()
    markers = ["insufficient", "cannot", "should not", "not count"]
    return any(marker in text for marker in markers)


def build_packet_row(fact_row: dict[str, Any], pert_row: dict[str, Any], variant: dict[str, Any] | None) -> dict[str, Any]:
    base = pert_row["base_variant"]
    variant_id = variant["variant_id"] if variant else base["variant_id"]
    roles = list(fact_row["roles"])
    final_decider = "final_decider" if "final_decider" in roles else roles[-1]
    state_map = base.get("source_scope_state", {})
    cards: list[dict[str, Any]] = []
    for fact in fact_row["source_facts"]:
        state = base_fact_state(fact, state_map)
        if variant:
            state = apply_variant_override(fact["fact_id"], state, variant_id)
            override_map = variant.get("source_scope_state_overrides", {})
            if isinstance(override_map, dict) and fact["fact_id"] in override_map:
                state = parse_state(str(override_map[fact["fact_id"]]), list(fact.get("candidate_recipients", [])))
        cards.append(source_card(fact, state, fact_row["sketch_id"]))
    expected_decision = INSUFFICIENT if variant_expects_insufficient(variant) else fact_row["evaluator_metadata"]["correct_answer"]
    return {
        "packet_id": f"{fact_row['sketch_id']}__{variant_id}__hsa_v0",
        "task_id": f"{fact_row['source_ref']['task_id']}::{variant_id}",
        "benchmark": "Hidden-State-Admission-v0",
        "roles": roles,
        "final_decider": final_decider,
        "candidate_options": list(fact_row["evaluator_metadata"]["possible_answers"]) + [INSUFFICIENT],
        "role_budgets": {role: len(cards) for role in roles},
        "decision_rule": "gold option is enabled only when all evaluator-only evidence slots for the final decider are satisfied; otherwise insufficient_evidence",
        "expected_final_decision": expected_decision,
        "source_cards": cards,
        "required_slots": required_slots(fact_row, final_decider),
        "hsa_meta": {
            "sketch_id": fact_row["sketch_id"],
            "variant_id": variant_id,
            "condition": "base" if variant is None else "perturbation",
            "source_ref": fact_row["source_ref"],
            "gold_answer": fact_row["evaluator_metadata"]["correct_answer"],
            "expected_downstream_delta": variant.get("expected_downstream_delta") if variant else base.get("expected_downstream_state"),
            "prompt_forbidden_fields": fact_row["prompt_visibility_policy"]["forbidden"],
            "downstream_scoring_obligations": fact_row.get("downstream_scoring_obligations", []),
            "oracle_unit_ids": [unit.get("unit_id") for unit in fact_row.get("oracle_admission_units", [])],
        },
    }


def is_legal_for_final(card: dict[str, Any], final_decider: str) -> bool:
    return card.get("verification_state") == "verified" and final_decider in set(card.get("recipient_scope", []))


def prediction_from_cards(row: dict[str, Any], model: str, card_ids: list[str]) -> dict[str, Any]:
    cards = {card["card_id"]: card for card in row["source_cards"]}
    candidate_units: list[dict[str, Any]] = []
    for index, card_id in enumerate(card_ids):
        if card_id not in cards:
            continue
        candidate_units.append(
            {
                "unit_id": f"{model}::{index:03d}::{card_id}",
                "recipient": row["final_decider"],
                "card_ids": [card_id],
                "priority": float(max(0, len(card_ids) - index)),
                "claimed_slots": [
                    slot["slot_id"]
                    for slot in row["required_slots"]
                    if card_id in slot.get("acceptable_card_ids", [])
                ],
                "claimed_effect": f"{model}_candidate_fact",
            }
        )
    return {
        "packet_id": row["packet_id"],
        "model": model,
        "provider": "local",
        "status": "ok",
        "response": {
            "option_states": [],
            "candidate_units": candidate_units,
            "proposed_rejections": [],
            "final_decision": row["expected_final_decision"],
        },
    }


def oracle_admissible_prediction(row: dict[str, Any]) -> dict[str, Any]:
    required_card_ids = []
    for slot in row["required_slots"]:
        for card_id in slot.get("acceptable_card_ids", []):
            if card_id not in required_card_ids:
                required_card_ids.append(card_id)
    legal_ids = [
        card_id
        for card_id in required_card_ids
        for card in row["source_cards"]
        if card["card_id"] == card_id and is_legal_for_final(card, row["final_decider"])
    ]
    return prediction_from_cards(row, "oracle_admissible_facts", legal_ids)


def shared_only_prediction(row: dict[str, Any]) -> dict[str, Any]:
    card_ids = [
        card["card_id"]
        for card in row["source_cards"]
        if card.get("provenance", {}).get("channel") == "shared" and is_legal_for_final(card, row["final_decider"])
    ]
    return prediction_from_cards(row, "shared_only_verified", card_ids)


def all_scoped_verified_prediction(row: dict[str, Any]) -> dict[str, Any]:
    card_ids = [
        card["card_id"]
        for card in row["source_cards"]
        if is_legal_for_final(card, row["final_decider"])
    ]
    return prediction_from_cards(row, "all_scoped_verified", card_ids)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fact-draft", type=Path, default=DEFAULT_FACT_DRAFT)
    parser.add_argument("--perturbation-draft", type=Path, default=DEFAULT_PERT_DRAFT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    fact_rows = {row["sketch_id"]: row for row in read_json(args.fact_draft)}
    perturbations = read_json(args.perturbation_draft)
    packet: list[dict[str, Any]] = []
    for pert_row in perturbations:
        fact_row = fact_rows[pert_row["sketch_id"]]
        packet.append(build_packet_row(fact_row, pert_row, None))
        for variant in pert_row.get("perturbation_variants", []):
            packet.append(build_packet_row(fact_row, pert_row, variant))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "hsa_v0_packet.jsonl", packet)
    write_jsonl(args.out_dir / "predictions_oracle_admissible_facts.jsonl", [oracle_admissible_prediction(row) for row in packet])
    write_jsonl(args.out_dir / "predictions_shared_only_verified.jsonl", [shared_only_prediction(row) for row in packet])
    write_jsonl(args.out_dir / "predictions_all_scoped_verified.jsonl", [all_scoped_verified_prediction(row) for row in packet])
    summary = {
        "rows": len(packet),
        "base_rows": sum(1 for row in packet if row.get("hsa_meta", {}).get("condition") == "base"),
        "perturbation_rows": sum(1 for row in packet if row.get("hsa_meta", {}).get("condition") == "perturbation"),
        "out_dir": str(args.out_dir),
    }
    (args.out_dir / "adapter_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
