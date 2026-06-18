#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_response(row: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    try:
        response = row.get("response")
        parsed = json.loads(response) if isinstance(response, str) else response
        if not isinstance(parsed, dict):
            return {}, "response_not_object"
        return parsed, None
    except Exception as error:  # noqa: BLE001
        return {}, f"{type(error).__name__}: {error}"


def as_set(items: Any) -> set[str]:
    if not isinstance(items, list):
        return set()
    return {item for item in items if isinstance(item, str)}


def unit_matches(expected: dict[str, Any], unit: dict[str, Any]) -> bool:
    if unit.get("unit_type") != expected.get("unit_type"):
        return False
    if unit.get("target_option") != expected.get("target_option"):
        return False
    required = set(expected.get("required_fact_ids", []))
    if not required.issubset(as_set(unit.get("fact_ids"))):
        return False
    expected_roles = set(expected.get("admit_to", []))
    if not expected_roles.issubset(as_set(unit.get("admit_to"))):
        return False
    forbidden_roles = set(expected.get("not_admit_to", []))
    if forbidden_roles & as_set(unit.get("admit_to")):
        return False
    return True


def rejection_matches(expected: dict[str, Any], rejection: dict[str, Any]) -> bool:
    expected_facts = set(expected.get("source_fact_ids", []))
    if not expected_facts.issubset(as_set(rejection.get("fact_ids"))):
        return False
    reason = str(rejection.get("reason", ""))
    expected_reason = str(expected.get("reason", ""))
    aliases = {
        "verification_reject": {"verification_reject", "quarantined", "unverified", "verification"},
        "recipient_scope_reject_for_final_decider": {"recipient_scope_reject", "recipient_scope_reject_for_final_decider", "scope"},
        "dependency_scope_incomplete": {"dependency_scope_incomplete", "dependency", "incomplete"},
    }
    allowed = aliases.get(expected_reason, {expected_reason})
    return not expected_reason or reason in allowed or any(item in reason for item in allowed)


def normalize_answer(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.lower().strip().split())


def downstream_ok(packet: dict[str, Any], parsed: dict[str, Any]) -> bool:
    state = parsed.get("final_decider_state", {})
    if not isinstance(state, dict):
        return False
    expected = str(packet.get("expected_downstream_state", "")).lower()
    status = str(state.get("status", "")).lower()
    answer = normalize_answer(state.get("answer"))
    gold = normalize_answer(packet.get("gold_answer"))
    expects_insufficient = any(token in expected for token in ["insufficient", "cannot", "should not", "not count"])
    if expects_insufficient:
        return "insufficient" in status or answer in {"", "null", "none"}
    return bool(gold) and answer == gold


def option_state_matches(expected: dict[str, Any], option_state: dict[str, Any]) -> bool:
    option = option_state.get("option")
    if option != expected.get("target_option", expected.get("option")):
        return False
    state = str(option_state.get("state", "")).lower()
    expected_state = {
        "option_blocker": "blocked",
        "option_enabler": "enabled",
    }.get(expected.get("unit_type"), str(expected.get("state", "")).lower())
    if not expected_state or expected_state not in state:
        return False
    return set(expected.get("required_fact_ids", [])).issubset(as_set(option_state.get("fact_ids")))


def option_state_recall(packet: dict[str, Any], parsed: dict[str, Any]) -> float:
    expected = packet.get("expected_option_states")
    if not isinstance(expected, list):
        expected = [
            unit
            for unit in packet.get("expected_units", [])
            if unit.get("unit_type") in {"option_blocker", "option_enabler"}
        ]
    if not expected:
        return 1.0
    states = [item for item in parsed.get("option_states", []) if isinstance(item, dict)]
    matched = [unit for unit in expected if any(option_state_matches(unit, state) for state in states)]
    return len(matched) / len(expected)


def count_scope_violations(packet: dict[str, Any], parsed: dict[str, Any]) -> int:
    facts = {fact["fact_id"]: fact for fact in packet["source_facts"]}
    violations = 0
    if isinstance(parsed.get("admitted_facts"), list):
        for admitted in parsed.get("admitted_facts", []):
            if not isinstance(admitted, dict):
                continue
            fact = facts.get(admitted.get("fact_id"))
            roles = as_set(admitted.get("admit_to"))
            if not fact:
                violations += 1
                continue
            if fact.get("verification_status") in {"quarantined", "unverified"}:
                violations += 1
            allowed = set(fact.get("eligible_recipients", []))
            if roles - allowed:
                violations += 1
        return violations
    for unit in parsed.get("admission_units", []):
        if not isinstance(unit, dict):
            continue
        roles = as_set(unit.get("admit_to"))
        for fact_id in as_set(unit.get("fact_ids")):
            fact = facts.get(fact_id)
            if not fact:
                violations += 1
                continue
            if fact.get("verification_status") in {"quarantined", "unverified"}:
                violations += 1
            allowed = set(fact.get("eligible_recipients", []))
            if roles - allowed:
                violations += 1
    return violations


def score_row(packet: dict[str, Any], prediction: dict[str, Any]) -> dict[str, Any]:
    parsed, parse_error = parse_response(prediction)
    units = [unit for unit in parsed.get("admission_units", []) if isinstance(unit, dict)] if not parse_error else []
    rejections = [rej for rej in parsed.get("rejections", []) if isinstance(rej, dict)] if not parse_error else []

    expected_units = packet.get("expected_units", [])
    matched_units = [unit for unit in expected_units if any(unit_matches(unit, pred) for pred in units)]
    absent_ids = set(packet.get("expected_absent_units", []))
    absent_violations = 0
    for absent_id in absent_ids:
        expected = next((unit for unit in packet.get("expected_units_all", []) if unit.get("unit_id") == absent_id), None)
        if expected and any(unit_matches(expected, pred) for pred in units):
            absent_violations += 1
    # If expected_units_all is absent, approximate absent checks by target/facts encoded in packet caveats are unavailable.
    expected_rejections = packet.get("expected_rejections", [])
    matched_rejections = [rej for rej in expected_rejections if any(rejection_matches(rej, pred) for pred in rejections)]
    scope_violations = count_scope_violations(packet, parsed) if not parse_error else 0
    downstream_match = parse_error is None and downstream_ok(packet, parsed)
    option_recall = option_state_recall(packet, parsed) if not parse_error else 0.0
    unit_recall = len(matched_units) / len(expected_units) if expected_units else 1.0
    rejection_recall = len(matched_rejections) / len(expected_rejections) if expected_rejections else 1.0
    strict = (
        parse_error is None
        and unit_recall == 1.0
        and rejection_recall == 1.0
        and scope_violations == 0
        and absent_violations == 0
        and downstream_match
        and option_recall == 1.0
    )
    return {
        "packet_id": packet["packet_id"],
        "sketch_id": packet["sketch_id"],
        "variant_id": packet["variant_id"],
        "condition": packet["condition"],
        "prediction_status": prediction.get("status"),
        "parse_error": parse_error,
        "metrics": {
            "strict": float(strict),
            "unit_recall": unit_recall,
            "rejection_recall": rejection_recall,
            "scope_violations": scope_violations,
            "absent_unit_violations": absent_violations,
            "downstream_ok": float(downstream_match),
            "option_state_recall": option_recall,
        },
        "matched_units": [unit.get("unit_id") for unit in matched_units],
        "matched_rejections": [rej.get("reason") for rej in matched_rejections],
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    metrics = [
        "strict",
        "unit_recall",
        "rejection_recall",
        "scope_violations",
        "absent_unit_violations",
        "downstream_ok",
        "option_state_recall",
    ]
    return {
        "rows": n,
        "metrics": {
            key: (sum(float(row["metrics"][key]) for row in rows) / n if n else 0.0)
            for key in metrics
        },
        "by_condition": {
            condition: {
                key: (
                    sum(float(row["metrics"][key]) for row in rows if row["condition"] == condition)
                    / max(1, sum(1 for row in rows if row["condition"] == condition))
                )
                for key in metrics
            }
            for condition in sorted({row["condition"] for row in rows})
        },
    }


def format_summary(summary: dict[str, Any]) -> str:
    lines = [f"rows: {summary['rows']}"]
    for key, value in summary["metrics"].items():
        lines.append(f"{key}: {value:.4f}")
    for condition, metrics in summary["by_condition"].items():
        joined = ", ".join(f"{key}={value:.4f}" for key, value in metrics.items())
        lines.append(f"{condition}: {joined}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    args = parser.parse_args()

    packet = {row["packet_id"]: row for row in read_jsonl(args.packet)}
    predictions = {row["packet_id"]: row for row in read_jsonl(args.predictions)}
    scored = [score_row(row, predictions.get(packet_id, {})) for packet_id, row in packet.items()]
    write_jsonl(args.out, scored)
    summary = summarize(scored)
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(format_summary(summary) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
