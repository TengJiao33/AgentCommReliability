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


def visibility_from_roles(selected_roles: list[str], roles: list[str]) -> str:
    if len(selected_roles) == len(roles):
        return "shared_all"
    if len(selected_roles) > 1:
        return "shared_subset"
    return "role_private"


def build_response(row: dict[str, Any], selected_by_role: dict[str, list[str]], reason: str) -> str:
    roles = list(row["roles"])
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    selected_roles_by_fragment: dict[str, list[str]] = {}
    for role, fragment_ids in selected_by_role.items():
        for fragment_id in fragment_ids:
            if fragment_id in fragments:
                selected_roles_by_fragment.setdefault(fragment_id, []).append(role)
    for fragment_id, selected_roles in selected_roles_by_fragment.items():
        selected_roles_by_fragment[fragment_id] = sorted(set(selected_roles), key=roles.index)

    response: dict[str, Any] = {"roles": {}, "rejected": list(row.get("reference_rejections", []))}
    for role in roles:
        cards: list[dict[str, Any]] = []
        for fragment_id in selected_by_role.get(role, []):
            fragment = fragments.get(fragment_id)
            if not fragment:
                cards.append({"fragment_id": fragment_id, "reason": reason})
                continue
            cards.append(
                {
                    "fragment_id": fragment_id,
                    "source_id": fragment["source_id"],
                    "visibility": visibility_from_roles(selected_roles_by_fragment.get(fragment_id, [role]), roles),
                    "reason": reason,
                }
            )
        response["roles"][role] = cards
    return json.dumps(response, ensure_ascii=False)


def oracle_selection(row: dict[str, Any]) -> dict[str, list[str]]:
    return {role: list(row["reference_need_sets"].get(role, [])) for role in row["roles"]}


def eligible_all_selection(row: dict[str, Any]) -> dict[str, list[str]]:
    return {role: list(row.get("candidate_need_sets", {}).get(role, [])) for role in row["roles"]}


def item_density_selection(row: dict[str, Any], use_global_budget: bool) -> dict[str, list[str]]:
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    spent_by_role = {role: 0 for role in row["roles"]}
    selected_by_role = {role: [] for role in row["roles"]}
    global_spent = 0
    edges: list[tuple[float, int, str, str]] = []
    for role in row["roles"]:
        scores = row.get("role_standalone_hint_scores", {}).get(role, {})
        for fragment_id in row.get("candidate_need_sets", {}).get(role, []):
            if fragment_id not in fragments:
                continue
            cost = max(1, int(fragments[fragment_id]["cost"]))
            score = int(scores.get(fragment_id, 0))
            edges.append((score / cost, score, role, fragment_id))
    edges.sort(key=lambda item: (-item[0], -item[1], item[2], item[3]))

    for _, _, role, fragment_id in edges:
        cost = int(fragments[fragment_id]["cost"])
        if spent_by_role[role] + cost > int(row["role_budgets"].get(role, 0)):
            continue
        if use_global_budget and global_spent + cost > int(row.get("global_budget", 0)):
            continue
        selected_by_role[role].append(fragment_id)
        spent_by_role[role] += cost
        global_spent += cost
    return selected_by_role


def bundle_density_selection(row: dict[str, Any]) -> dict[str, list[str]]:
    selected_by_role = {role: [] for role in row["roles"]}
    global_spent = 0
    bundles = list(row.get("role_bundles", {}).values())
    bundles.sort(
        key=lambda bundle: (
            -(float(bundle["utility"]) / max(1, int(bundle["cost"]))),
            -int(bundle["utility"]),
            int(bundle["cost"]),
            bundle["role"],
        )
    )
    for bundle in bundles:
        cost = int(bundle["cost"])
        if global_spent + cost > int(row.get("global_budget", 0)):
            continue
        role = bundle["role"]
        if cost > int(row["role_budgets"].get(role, 0)):
            continue
        selected_by_role[role] = list(bundle["requires"])
        global_spent += cost
    return selected_by_role


def cheapest_bundle_selection(row: dict[str, Any]) -> dict[str, list[str]]:
    selected_by_role = {role: [] for role in row["roles"]}
    global_spent = 0
    bundles = list(row.get("role_bundles", {}).values())
    bundles.sort(key=lambda bundle: (int(bundle["cost"]), -int(bundle["utility"]), bundle["role"]))
    for bundle in bundles:
        cost = int(bundle["cost"])
        if global_spent + cost > int(row.get("global_budget", 0)):
            continue
        role = bundle["role"]
        selected_by_role[role] = list(bundle["requires"])
        global_spent += cost
    return selected_by_role


def group_density_selection(row: dict[str, Any]) -> dict[str, list[str]]:
    selected_by_role = {role: [] for role in row["roles"]}
    used_roles: set[str] = set()
    global_spent = 0
    groups = list(row.get("cross_role_groups", []))
    groups.sort(
        key=lambda group: (
            -(float(group["utility"]) / max(1, int(group["cost"]))),
            -int(group["utility"]),
            int(group["cost"]),
            group["group_id"],
        )
    )
    for group in groups:
        group_roles = set(group.get("roles", []))
        cost = int(group["cost"])
        if used_roles & group_roles:
            continue
        if global_spent + cost > int(row.get("global_budget", 0)):
            continue
        for role in group.get("roles", []):
            bundle = row.get("role_bundles", {}).get(role)
            if bundle:
                selected_by_role[role] = list(bundle["requires"])
        used_roles |= group_roles
        global_spent += cost
    return selected_by_role


def selection_for(row: dict[str, Any], baseline: str) -> dict[str, list[str]]:
    if baseline == "oracle":
        return oracle_selection(row)
    if baseline == "eligible_all":
        return eligible_all_selection(row)
    if baseline == "item_density_per_role":
        return item_density_selection(row, use_global_budget=False)
    if baseline == "item_density_global":
        return item_density_selection(row, use_global_budget=True)
    if baseline == "bundle_density_global":
        return bundle_density_selection(row)
    if baseline == "cheapest_bundle_global":
        return cheapest_bundle_selection(row)
    if baseline == "group_density_global":
        return group_density_selection(row)
    raise ValueError(f"unknown baseline: {baseline}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument(
        "--baseline",
        choices=[
            "oracle",
            "eligible_all",
            "item_density_per_role",
            "item_density_global",
            "bundle_density_global",
            "cheapest_bundle_global",
            "group_density_global",
        ],
        required=True,
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    out_rows: list[dict[str, Any]] = []
    for row in read_jsonl(args.packet):
        selected = selection_for(row, args.baseline)
        out_rows.append(
            {
                "hard_evaluation_id": row["hard_evaluation_id"],
                "base_evaluation_id": row["base_evaluation_id"],
                "scenario_id": row["scenario_id"],
                "shuffle_seed": row["shuffle_seed"],
                "state_admission_variant": row.get("state_admission_variant"),
                "task": f"state_admission_v1_baseline_{args.baseline}",
                "model": args.baseline,
                "provider": "local",
                "response": build_response(row, selected, reason=args.baseline),
                "status": "ok",
            }
        )
    write_jsonl(args.out, out_rows)
    print(json.dumps({"rows": len(out_rows), "baseline": args.baseline, "out": str(args.out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
