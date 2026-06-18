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


def visibility_from_selected_roles(selected_roles: list[str], all_roles: list[str]) -> str:
    if len(selected_roles) == len(all_roles):
        return "shared_all"
    if len(selected_roles) > 1:
        return "shared_subset"
    return "role_private"


def choose_for_role(row: dict[str, Any], role: str, baseline: str) -> list[str]:
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    candidates = list(row.get("candidate_need_sets", row["reference_need_sets"])[role])
    budget = int(row["role_budgets"][role])
    utilities = row.get("role_utilities", {}).get(role, {})

    if baseline == "oracle_utility":
        return list(row["reference_need_sets"][role])
    if baseline == "eligible_all":
        return candidates

    spent = 0
    selected: list[str] = []
    if baseline == "eligible_cheapest":
        ordered = sorted(candidates, key=lambda item: (fragments[item]["cost"], item))
    elif baseline == "utility_density_greedy":
        ordered = sorted(
            candidates,
            key=lambda item: (
                -(float(utilities.get(item, 0)) / max(1, int(fragments[item]["cost"]))),
                -int(utilities.get(item, 0)),
                int(fragments[item]["cost"]),
                item,
            ),
        )
    else:
        raise ValueError(f"unknown baseline: {baseline}")

    for fragment_id in ordered:
        cost = int(fragments[fragment_id]["cost"])
        if spent + cost <= budget:
            selected.append(fragment_id)
            spent += cost
    return selected


def response_for_row(row: dict[str, Any], baseline: str) -> str:
    roles = list(row["roles"])
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    selected_by_role = {
        role: choose_for_role(row, role, baseline)
        for role in roles
    }
    selected_roles_by_fragment: dict[str, list[str]] = {}
    for role, fragment_ids in selected_by_role.items():
        for fragment_id in fragment_ids:
            selected_roles_by_fragment.setdefault(fragment_id, []).append(role)
    for fragment_id in selected_roles_by_fragment:
        selected_roles_by_fragment[fragment_id].sort(key=roles.index)

    response: dict[str, Any] = {"roles": {}, "rejected": list(row.get("reference_rejections", []))}
    for role in roles:
        cards: list[dict[str, Any]] = []
        for fragment_id in selected_by_role[role]:
            fragment = fragments[fragment_id]
            cards.append(
                {
                    "fragment_id": fragment_id,
                    "source_id": fragment["source_id"],
                    "visibility": visibility_from_selected_roles(selected_roles_by_fragment[fragment_id], roles),
                    "reason": baseline,
                }
            )
        response["roles"][role] = cards
    return json.dumps(response, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--baseline", choices=["oracle_utility", "eligible_all", "eligible_cheapest", "utility_density_greedy"], required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    out_rows = []
    for row in read_jsonl(args.packet):
        out_rows.append(
            {
                "hard_evaluation_id": row["hard_evaluation_id"],
                "base_evaluation_id": row["base_evaluation_id"],
                "scenario_id": row["scenario_id"],
                "shuffle_seed": row["shuffle_seed"],
                "source_perturbation_variant": row.get("source_perturbation_variant"),
                "tight_budget_variant": row.get("tight_budget_variant"),
                "task": f"tight_budget_baseline_{args.baseline}",
                "model": args.baseline,
                "provider": "local",
                "response": response_for_row(row, args.baseline),
                "status": "ok",
            }
        )
    write_jsonl(args.out, out_rows)
    print(json.dumps({"rows": len(out_rows), "baseline": args.baseline, "out": str(args.out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
