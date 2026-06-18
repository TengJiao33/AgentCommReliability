from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from score_perspectivegap_hard_routing import (
    format_summary,
    normalize_response,
    parse_json_object_loose,
    read_jsonl,
    score_packet_row,
    summarize,
    write_jsonl,
)


def better_group_solution(
    candidate: tuple[int, int, tuple[str, ...]],
    incumbent: tuple[int, int, tuple[str, ...]] | None,
) -> bool:
    if incumbent is None:
        return True
    utility, cost, ids = candidate
    best_utility, best_cost, best_ids = incumbent
    if utility != best_utility:
        return utility > best_utility
    if cost != best_cost:
        return cost < best_cost
    return ids < best_ids


def best_disjoint_group_utility(groups: list[dict[str, Any]], budget: int) -> int:
    best: tuple[int, int, tuple[str, ...]] | None = None
    group_count = len(groups)
    for mask in range(1 << group_count):
        selected: list[dict[str, Any]] = []
        used_roles: set[str] = set()
        valid = True
        for index, group in enumerate(groups):
            if not (mask & (1 << index)):
                continue
            group_roles = set(group.get("roles", []))
            if used_roles & group_roles:
                valid = False
                break
            used_roles |= group_roles
            selected.append(group)
        if not valid:
            continue
        cost = sum(int(group["cost"]) for group in selected)
        if cost > budget:
            continue
        utility = sum(int(group["utility"]) for group in selected)
        ids = tuple(sorted(group["group_id"] for group in selected))
        candidate = (utility, cost, ids)
        if better_group_solution(candidate, best):
            best = candidate
    return best[0] if best else 0


def predicted_ids_by_role(response_text: str | None) -> tuple[dict[str, set[str]], str | None]:
    try:
        parsed = parse_json_object_loose(response_text)
        normalized_roles, _ = normalize_response(parsed)
    except (json.JSONDecodeError, ValueError) as error:
        return {}, f"parse: {error}"
    out: dict[str, set[str]] = {}
    for role, items in normalized_roles.items():
        out[role] = {
            item.get("fragment_id")
            for item in items
            if isinstance(item.get("fragment_id"), str)
        }
    return out, None


def add_state_admission_metrics(row: dict[str, Any], response_text: str | None, scored: dict[str, Any]) -> dict[str, Any]:
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    predicted_by_role, parse_error = predicted_ids_by_role(response_text)

    total_oracle = int(row.get("state_admission_oracle_utility", 0))
    completed_utility = 0
    raw_completed_utility = 0
    closure_violations = 0
    completed_roles = 0
    exact_oracle_roles = 0
    per_role_budget_pass = 0
    global_spent = 0
    per_role: dict[str, Any] = {}
    role_bundle_complete: dict[str, bool] = {}
    role_feasible_bundle_complete: dict[str, bool] = {}
    global_budget = int(row.get("global_budget", 0))

    for role in row["roles"]:
        predicted = {
            fragment_id
            for fragment_id in predicted_by_role.get(role, set())
            if fragment_id in fragments
        }
        spent = sum(int(fragments[fragment_id]["cost"]) for fragment_id in predicted)
        global_spent += spent
        budget = int(row["role_budgets"].get(role, 0))
        budget_pass = parse_error is None and spent <= budget
        per_role_budget_pass += int(budget_pass)

        bundle = row.get("role_bundles", {}).get(role)
        role_utility = 0
        role_raw_utility = 0
        role_closure_violation = 0
        bundle_complete = False
        if bundle:
            requires = set(bundle.get("requires", []))
            touched = bool(predicted & requires)
            bundle_complete = bool(requires) and requires.issubset(predicted)
            if bundle_complete:
                role_raw_utility = int(bundle["utility"])
                if budget_pass:
                    role_utility = int(bundle["utility"])
                    completed_roles += 1
            elif touched:
                role_closure_violation = 1
                closure_violations += 1
        role_bundle_complete[role] = bundle_complete
        role_feasible_bundle_complete[role] = bundle_complete and budget_pass

        reference = set(row["reference_need_sets"].get(role, []))
        exact_oracle_roles += int(predicted == reference)
        raw_completed_utility += role_raw_utility
        completed_utility += role_utility
        per_role[role] = {
            "predicted": sorted(predicted),
            "reference": sorted(reference),
            "spent": spent,
            "budget": budget,
            "budget_pass": budget_pass,
            "bundle_complete": bundle_complete,
            "closure_violation": bool(role_closure_violation),
            "raw_bundle_utility": role_raw_utility,
            "feasible_bundle_utility": role_utility,
        }

    if row.get("oracle_groups"):
        raw_completed_utility = 0
        completed_utility = 0
        feasible_group_roles: set[str] = set()
        raw_completed_groups: list[dict[str, Any]] = []
        feasible_completed_groups: list[dict[str, Any]] = []
        for group in row.get("cross_role_groups", []):
            group_roles = list(group.get("roles", []))
            if group_roles and all(role_bundle_complete.get(role, False) for role in group_roles):
                raw_completed_groups.append(group)
            if group_roles and all(role_feasible_bundle_complete.get(role, False) for role in group_roles):
                feasible_completed_groups.append(group)
                feasible_group_roles.update(group_roles)
        raw_completed_utility = best_disjoint_group_utility(raw_completed_groups, global_budget)
        completed_utility = best_disjoint_group_utility(feasible_completed_groups, global_budget)
        completed_roles = len(feasible_group_roles)

    global_budget_pass = parse_error is None and global_spent <= global_budget
    feasible_utility = completed_utility if global_budget_pass else 0

    total_roles = len(row["roles"])
    state_metrics = {
        "oracle_utility": total_oracle,
        "raw_completed_utility": raw_completed_utility,
        "feasible_completed_utility": feasible_utility,
        "utility_ratio": feasible_utility / total_oracle if total_oracle else 1.0,
        "raw_utility_ratio": raw_completed_utility / total_oracle if total_oracle else 1.0,
        "completed_role_rate": completed_roles / total_roles if total_roles else 0.0,
        "exact_oracle_role_rate": exact_oracle_roles / total_roles if total_roles else 0.0,
        "per_role_budget_pass_rate": per_role_budget_pass / total_roles if total_roles else 0.0,
        "global_spent": global_spent,
        "global_budget": global_budget,
        "global_budget_pass": global_budget_pass,
        "global_budget_overrun": max(0, global_spent - global_budget),
        "closure_violations": closure_violations,
        "per_role": per_role,
    }
    scored["state_admission"] = state_metrics
    scored["metrics"].update(
        {
            "utility_ratio": state_metrics["utility_ratio"],
            "raw_utility_ratio": state_metrics["raw_utility_ratio"],
            "completed_role_rate": state_metrics["completed_role_rate"],
            "exact_oracle_role_rate": state_metrics["exact_oracle_role_rate"],
            "per_role_budget_pass_rate": state_metrics["per_role_budget_pass_rate"],
            "global_budget_pass": float(state_metrics["global_budget_pass"]),
            "global_budget_overrun": float(state_metrics["global_budget_overrun"]),
            "closure_violations": float(state_metrics["closure_violations"]),
        }
    )
    return scored


def summarize_state(rows: list[dict[str, Any]]) -> dict[str, Any]:
    base = summarize(rows)
    n = len(rows)
    oracle = sum(row.get("state_admission", {}).get("oracle_utility", 0) for row in rows)
    raw = sum(row.get("state_admission", {}).get("raw_completed_utility", 0) for row in rows)
    feasible = sum(row.get("state_admission", {}).get("feasible_completed_utility", 0) for row in rows)
    base["state_admission"] = {
        "oracle_utility": oracle,
        "raw_completed_utility": raw,
        "feasible_completed_utility": feasible,
        "utility_ratio": feasible / oracle if oracle else 1.0,
        "raw_utility_ratio": raw / oracle if oracle else 1.0,
        "completed_role_rate": (
            sum(row.get("state_admission", {}).get("completed_role_rate", 0.0) for row in rows) / n
            if n
            else 0.0
        ),
        "exact_oracle_role_rate": (
            sum(row.get("state_admission", {}).get("exact_oracle_role_rate", 0.0) for row in rows) / n
            if n
            else 0.0
        ),
        "per_role_budget_pass_rate": (
            sum(row.get("state_admission", {}).get("per_role_budget_pass_rate", 0.0) for row in rows) / n
            if n
            else 0.0
        ),
        "global_budget_pass": (
            sum(float(row.get("state_admission", {}).get("global_budget_pass", False)) for row in rows) / n
            if n
            else 0.0
        ),
        "global_budget_overrun": (
            sum(row.get("state_admission", {}).get("global_budget_overrun", 0) for row in rows) / n
            if n
            else 0.0
        ),
        "closure_violations": (
            sum(row.get("state_admission", {}).get("closure_violations", 0) for row in rows) / n
            if n
            else 0.0
        ),
    }
    base["metrics"].update(
        {
            "utility_ratio": base["state_admission"]["utility_ratio"],
            "raw_utility_ratio": base["state_admission"]["raw_utility_ratio"],
            "completed_role_rate": base["state_admission"]["completed_role_rate"],
            "exact_oracle_role_rate": base["state_admission"]["exact_oracle_role_rate"],
            "per_role_budget_pass_rate": base["state_admission"]["per_role_budget_pass_rate"],
            "global_budget_pass": base["state_admission"]["global_budget_pass"],
            "global_budget_overrun": base["state_admission"]["global_budget_overrun"],
            "closure_violations": base["state_admission"]["closure_violations"],
        }
    )
    return base


def format_state_summary(summary: dict[str, Any]) -> str:
    state = summary["state_admission"]
    return "\n".join(
        [
            format_summary(summary),
            f"utility_ratio: {state['utility_ratio']:.4f}",
            f"raw_utility_ratio: {state['raw_utility_ratio']:.4f}",
            f"completed_role_rate: {state['completed_role_rate']:.4f}",
            f"exact_oracle_role_rate: {state['exact_oracle_role_rate']:.4f}",
            f"per_role_budget_pass_rate: {state['per_role_budget_pass_rate']:.4f}",
            f"global_budget_pass: {state['global_budget_pass']:.4f}",
            f"global_budget_overrun: {state['global_budget_overrun']:.4f}",
            f"closure_violations: {state['closure_violations']:.4f}",
            f"oracle_utility: {state['oracle_utility']}",
            f"feasible_completed_utility: {state['feasible_completed_utility']}",
            f"raw_completed_utility: {state['raw_completed_utility']}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    args = parser.parse_args()

    packet = read_jsonl(args.packet)
    predictions_by_id: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(args.predictions):
        if "hard_evaluation_id" in row:
            predictions_by_id[row["hard_evaluation_id"]] = row
        if "source_hard_evaluation_id" in row:
            predictions_by_id[row["source_hard_evaluation_id"]] = row
        if "base_evaluation_id" in row:
            predictions_by_id[row["base_evaluation_id"]] = row

    scored: list[dict[str, Any]] = []
    for row in packet:
        prediction = (
            predictions_by_id.get(row["hard_evaluation_id"])
            or predictions_by_id.get(row.get("source_hard_evaluation_id", ""))
            or predictions_by_id.get(row["base_evaluation_id"], {})
        )
        response = prediction.get("response")
        scored.append(add_state_admission_metrics(row, response, score_packet_row(row, response)))

    write_jsonl(args.out, scored)
    summary = summarize_state(scored)
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(format_state_summary(summary) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
