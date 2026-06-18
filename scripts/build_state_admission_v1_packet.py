from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Any


DEFAULT_SOURCE = Path("experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl")


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


def visibility_label(recipients: list[str], roles: list[str]) -> str:
    if not recipients:
        return "budget_skipped"
    if len(recipients) == len(roles):
        return "shared_all"
    if len(recipients) > 1:
        return "shared_subset"
    return "role_private"


def role_index(roles: list[str], role: str) -> int:
    return roles.index(role)


def fragment_cost(fragments: dict[str, dict[str, Any]], fragment_id: str) -> int:
    return int(fragments[fragment_id]["cost"])


def choose_core_ids(row: dict[str, Any], role: str, max_bundle_size: int) -> list[str]:
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    candidates = list(row.get("candidate_need_sets", row["reference_need_sets"]).get(role, []))
    if not candidates:
        return []

    utilities = row.get("role_utilities", {}).get(role, {})
    core: list[str] = []
    for fragment_id in row["reference_need_sets"].get(role, []):
        if fragment_id in candidates and fragment_id not in core:
            core.append(fragment_id)
    if not core:
        ordered = sorted(
            candidates,
            key=lambda item: (-int(utilities.get(item, 0)), fragment_cost(fragments, item), item),
        )
        core.append(ordered[0])

    if len(core) < 2 and len(candidates) > len(core):
        extras = [item for item in candidates if item not in core]
        extras.sort(key=lambda item: (-int(utilities.get(item, 0)), fragment_cost(fragments, item), item))
        core.append(extras[0])

    core = core[:max_bundle_size]
    return sorted(core)


def role_bundle_utility(roles: list[str], role: str, core_ids: list[str]) -> int:
    # Make role priority explicit so global-budget selection is non-trivial.
    # Earlier roles are slightly more valuable, but bundle size still matters.
    priority = len(roles) - role_index(roles, role)
    return 100 + 13 * priority + 7 * len(core_ids)


def standalone_hint_scores(
    row: dict[str, Any],
    role: str,
    core_ids: list[str],
) -> dict[str, int]:
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    utilities = row.get("role_utilities", {}).get(role, {})
    candidates = list(row.get("candidate_need_sets", row["reference_need_sets"]).get(role, []))
    scores: dict[str, int] = {}
    for fragment_id in candidates:
        cost = fragment_cost(fragments, fragment_id)
        if fragment_id in core_ids:
            scores[fragment_id] = max(1, 24 + int(utilities.get(fragment_id, 0)) - cost)
        else:
            # This deliberately creates semantically tempting singleton evidence.
            scores[fragment_id] = max(1, 86 + int(utilities.get(fragment_id, 0)) - cost)
    return scores


def select_oracle_roles(
    role_bundles: dict[str, dict[str, Any]],
    global_budget: int,
    roles: list[str],
) -> list[str]:
    available = [role for role in roles if role in role_bundles]
    best: tuple[int, int, tuple[str, ...]] | None = None
    for size in range(len(available) + 1):
        for subset in combinations(available, size):
            cost = sum(int(role_bundles[role]["cost"]) for role in subset)
            if cost > global_budget:
                continue
            utility = sum(int(role_bundles[role]["utility"]) for role in subset)
            ordered = tuple(sorted(subset, key=lambda role: role_index(roles, role)))
            candidate = (utility, cost, ordered)
            if best is None:
                best = candidate
                continue
            best_utility, best_cost, best_roles = best
            if utility != best_utility:
                if utility > best_utility:
                    best = candidate
                continue
            if cost != best_cost:
                if cost < best_cost:
                    best = candidate
                continue
            if ordered < best_roles:
                best = candidate
    return list(best[2]) if best else []


def build_cross_role_groups(
    role_bundles: dict[str, dict[str, Any]],
    roles: list[str],
) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    available = [role for role in roles if role in role_bundles]
    for group_roles_tuple in combinations(available, 2):
        group_roles = list(group_roles_tuple)
        cost = sum(int(role_bundles[role]["cost"]) for role in group_roles)
        base_utility = sum(int(role_bundles[role]["utility"]) for role in group_roles)
        groups.append(
            {
                "group_id": "mission_group_" + "_".join(group_roles),
                "roles": group_roles,
                "requires_bundles": [role_bundles[role]["bundle_id"] for role in group_roles],
                "cost": cost,
                "base_utility": base_utility,
                "utility": base_utility,
                "credit": "all_roles_in_group_complete_or_zero",
            }
        )
    return groups


def assign_adversarial_group_utilities(groups: list[dict[str, Any]], global_budget: int) -> list[dict[str, Any]]:
    if not groups:
        return groups
    feasible = [group for group in groups if int(group["cost"]) <= global_budget]
    if not feasible:
        return groups
    target = sorted(feasible, key=lambda group: (-int(group["cost"]), group["group_id"]))[0]
    target_roles = set(target.get("roles", []))
    target_cost = max(1, int(target["cost"]))
    target_utility = 1000
    target_density = target_utility / target_cost

    out: list[dict[str, Any]] = []
    for group in groups:
        enriched = dict(group)
        group_roles = set(group.get("roles", []))
        cost = max(1, int(group["cost"]))
        if group["group_id"] == target["group_id"]:
            enriched["utility"] = target_utility
            enriched["group_family"] = "target_pair"
        elif group_roles & target_roles and cost < target_cost:
            # These groups look better to density greedy but block the target role.
            decoy_utility = int((target_density + 25) * cost)
            enriched["utility"] = min(400, max(160, decoy_utility))
            enriched["group_family"] = "overlap_decoy_pair"
        else:
            enriched["utility"] = max(80, int(group.get("base_utility", 0) * 0.45))
            enriched["group_family"] = "background_pair"
        out.append(enriched)
    return out


def select_oracle_groups(groups: list[dict[str, Any]], global_budget: int) -> list[str]:
    best: tuple[int, int, tuple[str, ...]] | None = None
    for size in range(len(groups) + 1):
        for subset in combinations(groups, size):
            role_memberships = [
                role
                for group in subset
                for role in group.get("roles", [])
            ]
            if len(role_memberships) != len(set(role_memberships)):
                continue
            cost = sum(int(group["cost"]) for group in subset)
            if cost > global_budget:
                continue
            utility = sum(int(group["utility"]) for group in subset)
            ids = tuple(sorted(group["group_id"] for group in subset))
            candidate = (utility, cost, ids)
            if best is None:
                best = candidate
                continue
            best_utility, best_cost, best_ids = best
            if utility != best_utility:
                if utility > best_utility:
                    best = candidate
                continue
            if cost != best_cost:
                if cost < best_cost:
                    best = candidate
                continue
            if ids < best_ids:
                best = candidate
    return list(best[2]) if best else []


def build_row(row: dict[str, Any], global_budget_fraction: float, max_bundle_size: int) -> dict[str, Any]:
    roles = list(row["roles"])
    fragments_by_id = {fragment["id"]: fragment for fragment in row["fragments"]}

    role_bundles: dict[str, dict[str, Any]] = {}
    role_budgets: dict[str, int] = {}
    role_hint_scores: dict[str, dict[str, int]] = {}
    for role in roles:
        core_ids = choose_core_ids(row, role, max_bundle_size=max_bundle_size)
        if not core_ids:
            role_budgets[role] = 0
            role_hint_scores[role] = {}
            continue
        cost = sum(fragment_cost(fragments_by_id, fragment_id) for fragment_id in core_ids)
        role_bundles[role] = {
            "bundle_id": f"{role}:evidence_bundle",
            "role": role,
            "requires": core_ids,
            "cost": cost,
            "utility": role_bundle_utility(roles, role, core_ids),
            "closure": "all_required_fragments_or_zero_utility",
        }
        role_budgets[role] = cost
        role_hint_scores[role] = standalone_hint_scores(row, role, core_ids)

    full_oracle_cost = sum(int(bundle["cost"]) for bundle in role_bundles.values())
    if full_oracle_cost:
        global_budget = max(
            max(int(bundle["cost"]) for bundle in role_bundles.values()),
            int(full_oracle_cost * global_budget_fraction),
        )
        global_budget = min(global_budget, full_oracle_cost)
    else:
        global_budget = 0

    cross_role_groups = assign_adversarial_group_utilities(
        build_cross_role_groups(role_bundles, roles),
        global_budget=global_budget,
    )
    oracle_group_ids = select_oracle_groups(cross_role_groups, global_budget)
    groups_by_id = {group["group_id"]: group for group in cross_role_groups}
    oracle_roles = sorted(
        {
            role
            for group_id in oracle_group_ids
            for role in groups_by_id[group_id]["roles"]
        },
        key=lambda item: role_index(roles, item),
    )
    if not oracle_roles:
        oracle_roles = select_oracle_roles(role_bundles, global_budget, roles)
    reference_need_sets: dict[str, list[str]] = {role: [] for role in roles}
    for role in oracle_roles:
        reference_need_sets[role] = list(role_bundles[role]["requires"])

    selected_roles_by_fragment: dict[str, list[str]] = {}
    eligible_roles_by_fragment: dict[str, list[str]] = {}
    candidate_need_sets = row.get("candidate_need_sets", row["reference_need_sets"])
    for role in roles:
        for fragment_id in candidate_need_sets.get(role, []):
            eligible_roles_by_fragment.setdefault(fragment_id, []).append(role)
        for fragment_id in reference_need_sets.get(role, []):
            selected_roles_by_fragment.setdefault(fragment_id, []).append(role)
    for mapping in (selected_roles_by_fragment, eligible_roles_by_fragment):
        for fragment_id, fragment_roles in mapping.items():
            mapping[fragment_id] = sorted(set(fragment_roles), key=lambda item: role_index(roles, item))

    fragments: list[dict[str, Any]] = []
    for fragment in row["fragments"]:
        fragment_id = fragment["id"]
        selected_roles = selected_roles_by_fragment.get(fragment_id, [])
        eligible_roles = eligible_roles_by_fragment.get(fragment_id, [])
        enriched = dict(fragment)
        enriched["eligible_by"] = eligible_roles
        enriched["candidate_needed_by"] = eligible_roles
        enriched["target_needed_by"] = selected_roles
        enriched["needed_by"] = selected_roles
        enriched["visibility_gold"] = (
            visibility_label(selected_roles, roles)
            if selected_roles
            else ("reject" if not eligible_roles else "budget_skipped")
        )
        enriched["standalone_hint_by_recipient"] = {
            role: role_hint_scores.get(role, {}).get(fragment_id, 0)
            for role in eligible_roles
        }
        fragments.append(enriched)

    fragment_lookup = {fragment["id"]: fragment for fragment in fragments}
    reference_cards = {
        role: [
            {
                "fragment_id": fragment_id,
                "source_id": fragment_lookup[fragment_id]["source_id"],
                "visibility": fragment_lookup[fragment_id]["visibility_gold"],
                "cost": fragment_lookup[fragment_id]["cost"],
                "bundle_id": role_bundles[role]["bundle_id"],
            }
            for fragment_id in reference_need_sets.get(role, [])
        ]
        for role in roles
    }
    reference_rejections = [
        {
            "fragment_id": fragment["id"],
            "source_id": fragment["source_id"],
            "reason": "source_scope_reject",
        }
        for fragment in fragments
        if not fragment.get("eligible_by")
    ]

    source_scope_ledger: list[dict[str, Any]] = []
    source_ledger_by_fragment = {
        entry["fragment_id"]: entry
        for entry in row.get("source_scope_ledger", [])
        if isinstance(entry, dict) and "fragment_id" in entry
    }
    for fragment in fragments:
        source_entry = source_ledger_by_fragment.get(fragment["id"], {})
        source_scope_ledger.append(
            {
                **source_entry,
                "fragment_id": fragment["id"],
                "source_id": fragment["source_id"],
                "recipients": list(fragment.get("eligible_by", [])),
                "route": "reject" if not fragment.get("eligible_by") else "candidate",
                "target_recipients": list(fragment.get("target_needed_by", [])),
                "standalone_hint_by_recipient": fragment["standalone_hint_by_recipient"],
            }
        )

    oracle_utility = (
        sum(int(groups_by_id[group_id]["utility"]) for group_id in oracle_group_ids)
        if oracle_group_ids
        else sum(int(role_bundles[role]["utility"]) for role in oracle_roles)
    )
    oracle_spent = sum(int(role_bundles[role]["cost"]) for role in oracle_roles)
    return {
        **row,
        "hard_evaluation_id": f"{row['hard_evaluation_id']}__state_admission_v1",
        "source_hard_evaluation_id": row["hard_evaluation_id"],
        "state_admission_variant": "bundle_closure_global_budget_v1",
        "state_admission_policy": {
            "global_budget_fraction": global_budget_fraction,
            "max_bundle_size": max_bundle_size,
            "objective": "maximize completed cross-role evidence groups under per-role and global budgets",
            "group_utility_rule": "adversarial_pair_density_trap",
            "bundle_credit": "zero unless all required fragments for that role are admitted",
            "group_credit": "zero unless all roles in a cross-role group complete their bundles",
        },
        "fragments": fragments,
        "source_scope_ledger": source_scope_ledger,
        "candidate_need_sets": {role: list(candidate_need_sets.get(role, [])) for role in roles},
        "role_budgets": role_budgets,
        "global_budget": global_budget,
        "global_oracle_spent": oracle_spent,
        "role_bundles": role_bundles,
        "cross_role_groups": cross_role_groups,
        "role_standalone_hint_scores": role_hint_scores,
        "oracle_roles": oracle_roles,
        "oracle_groups": oracle_group_ids,
        "reference_need_sets": reference_need_sets,
        "reference_cards": reference_cards,
        "reference_rejections": reference_rejections,
        "state_admission_oracle_utility": oracle_utility,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    role_rows = sum(len(row["roles"]) for row in rows)
    roles_with_bundles = sum(len(row.get("role_bundles", {})) for row in rows)
    oracle_roles = sum(len(row.get("oracle_roles", [])) for row in rows)
    full_cost = sum(
        sum(int(bundle["cost"]) for bundle in row.get("role_bundles", {}).values())
        for row in rows
    )
    global_budget = sum(int(row.get("global_budget", 0)) for row in rows)
    return {
        "rows": len(rows),
        "role_rows": role_rows,
        "roles_with_bundles": roles_with_bundles,
        "oracle_served_roles": oracle_roles,
        "mean_oracle_served_role_rate": oracle_roles / roles_with_bundles if roles_with_bundles else 0.0,
        "full_bundle_cost": full_cost,
        "global_budget_sum": global_budget,
        "global_budget_ratio": global_budget / full_cost if full_cost else 0.0,
        "oracle_utility": sum(int(row.get("state_admission_oracle_utility", 0)) for row in rows),
        "role_count_distribution": {
            str(count): sum(1 for row in rows if len(row["roles"]) == count)
            for count in sorted({len(row["roles"]) for row in rows})
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--global-budget-fraction", type=float, default=0.68)
    parser.add_argument("--max-bundle-size", type=int, default=3)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    rows = read_jsonl(args.packet)
    if args.limit:
        rows = rows[: args.limit]
    out_rows = [
        build_row(row, global_budget_fraction=args.global_budget_fraction, max_bundle_size=args.max_bundle_size)
        for row in rows
    ]
    write_jsonl(args.out, out_rows)
    print(json.dumps({**summarize(out_rows), "packet": str(args.out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
