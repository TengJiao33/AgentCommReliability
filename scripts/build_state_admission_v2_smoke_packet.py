#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_FACT_DRAFT = Path("experiments/20260618-local-state-admission-v2-preflight/hiddenbench_fact_units.draft.json")
DEFAULT_PERT_DRAFT = Path("experiments/20260618-local-state-admission-v2-preflight/source_scope_perturbations.draft.json")
DEFAULT_BENCHMARK = Path("data/external/hiddenbench/benchmark.json")
DEFAULT_OUT_DIR = Path("experiments/20260618-local-state-admission-v2-smoke")


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
    elif "verified" in kind:
        verification = "verified"
    else:
        verification = "unspecified"
    return {"source_kind": kind, "verification_status": verification, "eligible_recipients": eligible}


def base_fact_state(fact: dict[str, Any], state_map: dict[str, str]) -> dict[str, Any]:
    fallback = list(fact.get("candidate_recipients", []))
    if fact["fact_id"] in state_map:
        return parse_state(state_map[fact["fact_id"]], fallback)
    if fact.get("channel") == "shared":
        return {
            "source_kind": "shared_context",
            "verification_status": "verified",
            "eligible_recipients": fallback,
        }
    return {
        "source_kind": "hidden_observation",
        "verification_status": "verified",
        "eligible_recipients": fallback,
    }


def apply_variant_override(fact_id: str, state: dict[str, Any], variant_id: str) -> dict[str, Any]:
    state = dict(state)
    if variant_id == "hb10_b_hazard_quarantined" and fact_id == "hb10_hidden_3":
        state["source_kind"] = "quarantined_sensor"
        state["verification_status"] = "quarantined"
    elif variant_id == "hb10_c_enabler_no_final_scope" and fact_id == "hb10_hidden_2":
        state["eligible_recipients"] = ["logistics_planner"]
    elif variant_id == "hb11_school_repair_quarantined" and fact_id == "hb11_hidden_1":
        state["source_kind"] = "unverified_repair_claim"
        state["verification_status"] = "unverified"
    elif variant_id == "hb11_library_fuel_no_final_scope" and fact_id == "hb11_hidden_0":
        state["eligible_recipients"] = ["facilities_checker"]
    elif variant_id == "hb01_west_bridge_unverified" and fact_id == "hb01_shared_3":
        state["source_kind"] = "unverified_public_notice"
        state["verification_status"] = "unverified"
    elif variant_id == "hb01_north_hill_split_scope_no_group_edge" and fact_id == "hb01_hidden_2":
        state["eligible_recipients"] = ["route_planner"]
    elif variant_id == "hb01_north_hill_split_scope_no_group_edge" and fact_id == "hb01_hidden_3":
        state["eligible_recipients"] = ["risk_checker"]
    return state


def expected_for_variant(units: list[dict[str, Any]], variant: dict[str, Any] | None) -> dict[str, Any]:
    expected_units = [json.loads(json.dumps(unit, ensure_ascii=False)) for unit in units]
    absent_units: list[str] = []
    expected_rejections: list[dict[str, Any]] = []
    if not variant:
        return {
            "expected_units": expected_units,
            "expected_absent_units": absent_units,
            "expected_rejections": expected_rejections,
            "expected_downstream_state": "decidable_from_admitted_facts",
        }
    delta = variant.get("expected_admission_delta", {})
    drop_units = set(delta.get("drop_units", []))
    absent_units.extend(sorted(drop_units))
    expected_units = [unit for unit in expected_units if unit.get("unit_id") not in drop_units]
    for mod in delta.get("modify_units", []):
        for unit in expected_units:
            if unit.get("unit_id") == mod.get("unit_id"):
                unit["admit_to"] = list(mod.get("admit_to", unit.get("admit_to", [])))
                unit["not_admit_to"] = list(mod.get("not_admit_to", []))
                unit["recipient_scope_reason"] = mod.get("reason")
    expected_rejections.extend(delta.get("add_rejections", []))
    return {
        "expected_units": expected_units,
        "expected_absent_units": absent_units,
        "expected_rejections": expected_rejections,
        "expected_downstream_state": variant.get("expected_downstream_delta", ""),
    }


def option_states_from_units(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    state_by_type = {
        "option_blocker": "blocked",
        "option_enabler": "enabled",
    }
    states: list[dict[str, Any]] = []
    for unit in units:
        state = state_by_type.get(unit.get("unit_type"))
        if not state:
            continue
        fact_ids = unit.get("required_fact_ids", []) + unit.get("supporting_fact_ids", [])
        states.append(
            {
                "unit_id": unit.get("unit_id"),
                "option": unit.get("target_option"),
                "state": state,
                "required_fact_ids": unit.get("required_fact_ids", []),
                "supporting_fact_ids": unit.get("supporting_fact_ids", []),
                "fact_ids": fact_ids,
                "rationale": unit.get("rationale", ""),
            }
        )
    return states


def make_packet_row(
    fact_row: dict[str, Any],
    pert_row: dict[str, Any],
    benchmark_task: dict[str, Any],
    variant: dict[str, Any] | None,
) -> dict[str, Any]:
    base = pert_row["base_variant"]
    variant_id = variant["variant_id"] if variant else base["variant_id"]
    source_scope_state = base.get("source_scope_state", {})
    source_facts = []
    for fact in fact_row["source_facts"]:
        state = base_fact_state(fact, source_scope_state)
        if variant:
            state = apply_variant_override(fact["fact_id"], state, variant_id)
        source_facts.append(
            {
                "fact_id": fact["fact_id"],
                "channel": fact.get("channel"),
                "text": fact["text"],
                "source_kind": state["source_kind"],
                "verification_status": state["verification_status"],
                "eligible_recipients": state["eligible_recipients"],
                "expected_treatment": fact.get("expected_treatment"),
            }
        )
    expected = expected_for_variant(fact_row["oracle_admission_units"], variant)
    expected_units_all = [json.loads(json.dumps(unit, ensure_ascii=False)) for unit in fact_row["oracle_admission_units"]]
    if not variant:
        expected["expected_rejections"] = list(fact_row.get("oracle_rejections", []))
    return {
        "packet_id": f"{fact_row['sketch_id']}__{variant_id}__state_admission_v2_smoke",
        "sketch_id": fact_row["sketch_id"],
        "variant_id": variant_id,
        "condition": "base" if variant is None else "perturbation",
        "task": "state_admission_v2_smoke",
        "source_ref": fact_row["source_ref"],
        "task_description": benchmark_task["description"],
        "possible_answers": list(benchmark_task["possible_answers"]),
        "gold_answer": benchmark_task["correct_answer"],
        "gold_visibility": "evaluator_only_never_prompt",
        "roles": list(fact_row["roles"]),
        "source_facts": source_facts,
        "expected_units": expected["expected_units"],
        "expected_option_states": option_states_from_units(expected["expected_units"]),
        "expected_units_all": expected_units_all,
        "expected_absent_units": expected["expected_absent_units"],
        "expected_rejections": expected["expected_rejections"],
        "expected_downstream_state": expected["expected_downstream_state"],
        "source_scope_change": variant.get("source_scope_change", "base verified role-scoped state") if variant else "base verified role-scoped state",
        "prompt_forbidden_fields": list(fact_row["prompt_visibility_policy"]["forbidden"]),
        "draft_caveat": fact_row.get("draft_caveat", ""),
    }


def oracle_response(row: dict[str, Any]) -> dict[str, Any]:
    facts = {fact["fact_id"]: fact for fact in row["source_facts"]}
    admitted_fact_ids = {
        fact_id
        for unit in row["expected_units"]
        for fact_id in unit.get("required_fact_ids", []) + unit.get("supporting_fact_ids", [])
    }
    expected = str(row.get("expected_downstream_state", "")).lower()
    expects_insufficient = any(token in expected for token in ["insufficient", "cannot", "should not", "not count"])
    return {
        "option_states": [
            {
                "option": state.get("option"),
                "state": state.get("state"),
                "fact_ids": state.get("fact_ids", []),
                "rationale": state.get("rationale", ""),
            }
            for state in row["expected_option_states"]
        ],
        "admitted_facts": [
            {
                "fact_id": fact_id,
                "admit_to": facts[fact_id]["eligible_recipients"],
            }
            for fact_id in sorted(admitted_fact_ids)
            if fact_id in facts and facts[fact_id]["verification_status"] == "verified"
        ],
        "admission_units": [
            {
                "unit_type": unit["unit_type"],
                "target_option": unit.get("target_option"),
                "fact_ids": unit.get("required_fact_ids", []) + unit.get("supporting_fact_ids", []),
                "admit_to": unit.get("admit_to", []),
                "rationale": unit.get("rationale", ""),
            }
            for unit in row["expected_units"]
        ],
        "rejections": [
            {
                "fact_ids": rej.get("source_fact_ids", []),
                "reason": rej.get("reason", "expected_reject"),
                "rationale": rej.get("rationale", ""),
            }
            for rej in row["expected_rejections"]
        ],
        "final_decider_state": {
            "status": "insufficient_admissible_evidence" if expects_insufficient else "decidable_from_admitted_facts",
            "answer": None if expects_insufficient else row.get("gold_answer"),
            "supporting_units": [unit.get("unit_id", unit.get("target_option", "")) for unit in row["expected_units"]],
        },
    }


def shared_context_response(row: dict[str, Any]) -> dict[str, Any]:
    admitted_fact_ids = [
        fact["fact_id"]
        for fact in row["source_facts"]
        if fact["verification_status"] not in {"quarantined", "unverified"}
    ]
    return {
        "option_states": [
            {
                "option": option,
                "state": "enabled",
                "fact_ids": admitted_fact_ids,
                "rationale": "shared-context baseline does not construct option-specific blockers",
            }
            for option in row.get("possible_answers", [])
        ],
        "admitted_facts": [
            {
                "fact_id": fact_id,
                "admit_to": row["roles"],
            }
            for fact_id in admitted_fact_ids
        ],
        "admission_units": [
            {
                "unit_type": "shared_context",
                "target_option": "all_options",
                "fact_ids": admitted_fact_ids,
                "admit_to": row["roles"],
                "rationale": "transparent shared-context baseline admits all verified facts to all roles",
            }
        ],
        "rejections": [],
        "final_decider_state": {"status": "shared_context_baseline"},
    }


def prediction_row(row: dict[str, Any], model: str, response: dict[str, Any]) -> dict[str, Any]:
    return {
        "packet_id": row["packet_id"],
        "sketch_id": row["sketch_id"],
        "variant_id": row["variant_id"],
        "task": "state_admission_v2_smoke",
        "model": model,
        "status": "ok",
        "response": json.dumps(response, ensure_ascii=False),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fact-draft", type=Path, default=DEFAULT_FACT_DRAFT)
    parser.add_argument("--perturbation-draft", type=Path, default=DEFAULT_PERT_DRAFT)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    fact_rows = {row["sketch_id"]: row for row in read_json(args.fact_draft)}
    perturbations = read_json(args.perturbation_draft)
    benchmark = {row["id"]: row for row in read_json(args.benchmark)}

    packet: list[dict[str, Any]] = []
    for pert_row in perturbations:
        fact_row = fact_rows[pert_row["sketch_id"]]
        task = benchmark[fact_row["source_ref"]["task_id"]]
        packet.append(make_packet_row(fact_row, pert_row, task, None))
        for variant in pert_row.get("perturbation_variants", []):
            packet.append(make_packet_row(fact_row, pert_row, task, variant))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    packet_path = args.out_dir / "packet.jsonl"
    write_jsonl(packet_path, packet)
    write_jsonl(args.out_dir / "oracle_predictions.jsonl", [prediction_row(row, "oracle", oracle_response(row)) for row in packet])
    write_jsonl(
        args.out_dir / "shared_context_predictions.jsonl",
        [prediction_row(row, "shared_context_baseline", shared_context_response(row)) for row in packet],
    )
    (args.out_dir / "README.md").write_text(
        "\n".join(
            [
                "# State Admission V2 Smoke Packet",
                "",
                "状态：local smoke packet。这里还没有 GPU output；`gold_answer`、`expected_units` 和 scoring obligations 都是 evaluator-only metadata。",
                "",
                f"- packet: `{packet_path}`",
                f"- rows: `{len(packet)}`",
                "- variants: each HiddenBench row has one base variant and two same-text source/scope perturbations.",
                "- model prompt must not render `gold_answer`, `expected_units`, `expected_option_states`, `expected_absent_units`, `expected_rejections`, or `expected_downstream_state`.",
                "",
                "Next gate: score `oracle_predictions.jsonl` before launching a model smoke.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"out_dir": str(args.out_dir), "packet": str(packet_path), "rows": len(packet)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
