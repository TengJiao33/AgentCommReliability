from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from score_perspectivegap_hard_routing import (
    baseline_response,
    format_summary,
    legacy_role_assignment_to_cards,
    normalize_response,
    parse_json_object_loose,
    read_jsonl,
    score_packet_row,
    summarize,
    write_jsonl,
)


def predicted_fragment_ids(response_text: str | None, role: str) -> tuple[set[str], str | None]:
    try:
        parsed = parse_json_object_loose(response_text)
        normalized_roles, _ = normalize_response(parsed)
    except (json.JSONDecodeError, ValueError) as error:
        return set(), f"parse: {error}"
    ids = {
        item.get("fragment_id")
        for item in normalized_roles.get(role, [])
        if isinstance(item.get("fragment_id"), str)
    }
    return ids, None


def add_tight_metrics(row: dict[str, Any], response_text: str | None, scored: dict[str, Any]) -> dict[str, Any]:
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    candidate_need_sets = row.get("candidate_need_sets", row["reference_need_sets"])
    role_utilities = row.get("role_utilities", {})

    oracle_utility = 0
    raw_utility = 0
    feasible_utility = 0
    exact_target_roles = 0
    feasible_roles = 0
    total_roles = len(row["roles"])
    per_role_utility: dict[str, Any] = {}
    for role in row["roles"]:
        predicted_ids, parse_error = predicted_fragment_ids(response_text, role)
        valid_predicted = {fragment_id for fragment_id in predicted_ids if fragment_id in fragments}
        eligible = set(candidate_need_sets.get(role, []))
        target = set(row["reference_need_sets"].get(role, []))
        utilities = {
            fragment_id: int(value)
            for fragment_id, value in role_utilities.get(role, {}).items()
        }
        role_oracle = int(row.get("role_oracle_values", {}).get(role, sum(utilities.get(item, 0) for item in target)))
        role_raw_utility = sum(utilities.get(fragment_id, 0) for fragment_id in valid_predicted & eligible)
        spent = sum(int(fragments[fragment_id]["cost"]) for fragment_id in valid_predicted)
        budget = int(row["role_budgets"][role])
        budget_feasible = parse_error is None and spent <= budget
        role_feasible_utility = role_raw_utility if budget_feasible else 0
        exact_target = valid_predicted == target

        oracle_utility += role_oracle
        raw_utility += role_raw_utility
        feasible_utility += role_feasible_utility
        exact_target_roles += int(exact_target)
        feasible_roles += int(budget_feasible)
        per_role_utility[role] = {
            "oracle_utility": role_oracle,
            "raw_predicted_utility": role_raw_utility,
            "feasible_predicted_utility": role_feasible_utility,
            "candidate_total_utility": sum(utilities.get(fragment_id, 0) for fragment_id in eligible),
            "spent": spent,
            "budget": budget,
            "budget_feasible": budget_feasible,
            "exact_target": exact_target,
        }

    scored["tight_budget"] = {
        "oracle_utility": oracle_utility,
        "raw_predicted_utility": raw_utility,
        "feasible_predicted_utility": feasible_utility,
        "utility_ratio": feasible_utility / oracle_utility if oracle_utility else 1.0,
        "raw_utility_ratio": raw_utility / oracle_utility if oracle_utility else 1.0,
        "exact_target_role_rate": exact_target_roles / total_roles if total_roles else 1.0,
        "budget_feasible_role_rate": feasible_roles / total_roles if total_roles else 1.0,
        "per_role": per_role_utility,
    }
    scored["metrics"]["utility_ratio"] = scored["tight_budget"]["utility_ratio"]
    scored["metrics"]["raw_utility_ratio"] = scored["tight_budget"]["raw_utility_ratio"]
    scored["metrics"]["exact_target_role_rate"] = scored["tight_budget"]["exact_target_role_rate"]
    scored["metrics"]["budget_feasible_role_rate"] = scored["tight_budget"]["budget_feasible_role_rate"]
    return scored


def summarize_tight(rows: list[dict[str, Any]]) -> dict[str, Any]:
    base = summarize(rows)
    oracle = sum(row.get("tight_budget", {}).get("oracle_utility", 0) for row in rows)
    raw = sum(row.get("tight_budget", {}).get("raw_predicted_utility", 0) for row in rows)
    feasible = sum(row.get("tight_budget", {}).get("feasible_predicted_utility", 0) for row in rows)
    n = len(rows)
    base["tight_budget"] = {
        "oracle_utility": oracle,
        "raw_predicted_utility": raw,
        "feasible_predicted_utility": feasible,
        "utility_ratio": feasible / oracle if oracle else 1.0,
        "raw_utility_ratio": raw / oracle if oracle else 1.0,
        "exact_target_role_rate": (
            sum(row.get("tight_budget", {}).get("exact_target_role_rate", 0.0) for row in rows) / n
            if n
            else 0.0
        ),
        "budget_feasible_role_rate": (
            sum(row.get("tight_budget", {}).get("budget_feasible_role_rate", 0.0) for row in rows) / n
            if n
            else 0.0
        ),
    }
    base["metrics"].update(
        {
            "utility_ratio": base["tight_budget"]["utility_ratio"],
            "raw_utility_ratio": base["tight_budget"]["raw_utility_ratio"],
            "exact_target_role_rate": base["tight_budget"]["exact_target_role_rate"],
            "budget_feasible_role_rate": base["tight_budget"]["budget_feasible_role_rate"],
        }
    )
    return base


def format_tight_summary(summary: dict[str, Any]) -> str:
    tight = summary["tight_budget"]
    return "\n".join(
        [
            format_summary(summary),
            f"utility_ratio: {tight['utility_ratio']:.4f}",
            f"raw_utility_ratio: {tight['raw_utility_ratio']:.4f}",
            f"exact_target_role_rate: {tight['exact_target_role_rate']:.4f}",
            f"budget_feasible_role_rate: {tight['budget_feasible_role_rate']:.4f}",
            f"oracle_utility: {tight['oracle_utility']}",
            f"feasible_predicted_utility: {tight['feasible_predicted_utility']}",
            f"raw_predicted_utility: {tight['raw_predicted_utility']}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--baseline", choices=["oracle", "all_to_all", "no_distractor_all_to_all", "shared_only", "budget_cheapest"])
    parser.add_argument("--legacy-role-assignment", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    args = parser.parse_args()

    packet = read_jsonl(args.packet)
    predictions_by_id: dict[str, dict[str, Any]] = {}
    if args.predictions:
        for row in read_jsonl(args.predictions):
            if "hard_evaluation_id" in row:
                predictions_by_id[row["hard_evaluation_id"]] = row
            if "source_hard_evaluation_id" in row:
                predictions_by_id[row["source_hard_evaluation_id"]] = row
            if "base_evaluation_id" in row:
                predictions_by_id[row["base_evaluation_id"]] = row
    if not args.baseline and not args.predictions:
        raise SystemExit("provide --baseline or --predictions")

    scored: list[dict[str, Any]] = []
    for row in packet:
        if args.baseline:
            response = baseline_response(row, args.baseline)
        else:
            prediction = (
                predictions_by_id.get(row["hard_evaluation_id"])
                or predictions_by_id.get(row.get("source_hard_evaluation_id", ""))
                or predictions_by_id.get(row["base_evaluation_id"], {})
            )
            if args.legacy_role_assignment and prediction.get("response") is not None:
                try:
                    response = legacy_role_assignment_to_cards(row, prediction.get("response"))
                except (json.JSONDecodeError, ValueError):
                    response = prediction.get("response")
            else:
                response = prediction.get("response")
        scored.append(add_tight_metrics(row, response, score_packet_row(row, response)))
    write_jsonl(args.out, scored)
    summary = summarize_tight(scored)
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(format_tight_summary(summary) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
