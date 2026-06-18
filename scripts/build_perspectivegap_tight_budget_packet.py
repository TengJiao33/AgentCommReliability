from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any


DEFAULT_PACKET = Path("experiments/20260618-local-perspectivegap-source-perturbation-v0/source_perturbation_rotated20.jsonl")


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


def source_rank(fragment_id: str) -> int:
    match = re.search(r"(\d+)$", fragment_id)
    return int(match.group(1)) if match else 999


def visibility_label(recipients: list[str], roles: list[str]) -> str:
    if not recipients:
        return "budget_skipped"
    if len(recipients) == len(roles):
        return "shared_all"
    if len(recipients) > 1:
        return "shared_subset"
    return "role_private"


def role_utility(fragment: dict[str, Any], role: str, roles: list[str]) -> int:
    eligible = set(fragment.get("needed_by", []))
    if role not in eligible:
        return 0
    rank_component = max(1, 12 - source_rank(fragment["id"]))
    scope_bonus = 2 if len(eligible) == len(roles) else 0
    private_bonus = 1 if len(eligible) == 1 else 0
    return rank_component + scope_bonus + private_bonus


def tight_budget(full_cost: int, candidate_costs: list[int], fraction: float) -> int:
    if not candidate_costs:
        return 0
    min_cost = min(candidate_costs)
    budget = max(min_cost, int(math.floor(full_cost * fraction)))
    if budget >= full_cost and len(candidate_costs) > 1:
        budget = max(min_cost, full_cost - min_cost)
    return min(budget, full_cost)


def better_solution(
    candidate: tuple[int, int, tuple[str, ...]],
    incumbent: tuple[int, int, tuple[str, ...]] | None,
) -> bool:
    if incumbent is None:
        return True
    value, spent, ids = candidate
    best_value, best_spent, best_ids = incumbent
    if value != best_value:
        return value > best_value
    if spent != best_spent:
        return spent < best_spent
    return ids < best_ids


def optimal_subset(
    candidates: list[dict[str, Any]],
    budget: int,
    utilities: dict[str, int],
) -> tuple[list[str], int, int]:
    states: dict[int, tuple[int, tuple[str, ...]]] = {0: (0, tuple())}
    for fragment in sorted(candidates, key=lambda item: item["id"]):
        cost = int(fragment["cost"])
        utility = int(utilities[fragment["id"]])
        next_states = dict(states)
        for spent, (value, ids) in states.items():
            new_spent = spent + cost
            if new_spent > budget:
                continue
            new_ids = tuple(sorted((*ids, fragment["id"])))
            existing = next_states.get(new_spent)
            if existing is None or better_solution((value + utility, new_spent, new_ids), (existing[0], new_spent, existing[1])):
                next_states[new_spent] = (value + utility, new_ids)
        states = next_states

    best: tuple[int, int, tuple[str, ...]] | None = None
    for spent, (value, ids) in states.items():
        candidate = (value, spent, ids)
        if better_solution(candidate, best):
            best = candidate
    if best is None:
        return [], 0, 0
    value, spent, ids = best
    return list(ids), value, spent


def build_tight_row(row: dict[str, Any], budget_fraction: float, utility_rule: str) -> dict[str, Any]:
    roles = list(row["roles"])
    fragments_by_id = {fragment["id"]: fragment for fragment in row["fragments"]}
    candidate_need_sets = {role: list(row["reference_need_sets"].get(role, [])) for role in roles}

    role_utilities: dict[str, dict[str, int]] = {}
    role_budgets: dict[str, int] = {}
    role_full_costs: dict[str, int] = {}
    reference_need_sets: dict[str, list[str]] = {}
    role_oracle_values: dict[str, int] = {}
    role_oracle_spent: dict[str, int] = {}
    for role in roles:
        candidates = [fragments_by_id[fragment_id] for fragment_id in candidate_need_sets[role]]
        utilities = {
            fragment["id"]: role_utility(fragment, role, roles)
            for fragment in candidates
        }
        full_cost = sum(int(fragment["cost"]) for fragment in candidates)
        budget = tight_budget(full_cost, [int(fragment["cost"]) for fragment in candidates], budget_fraction)
        selected, oracle_value, oracle_spent = optimal_subset(candidates, budget, utilities)
        role_utilities[role] = utilities
        role_full_costs[role] = full_cost
        role_budgets[role] = budget
        reference_need_sets[role] = selected
        role_oracle_values[role] = oracle_value
        role_oracle_spent[role] = oracle_spent

    selected_roles_by_fragment: dict[str, list[str]] = {}
    for role, fragment_ids in reference_need_sets.items():
        for fragment_id in fragment_ids:
            selected_roles_by_fragment.setdefault(fragment_id, []).append(role)
    for fragment_id in selected_roles_by_fragment:
        selected_roles_by_fragment[fragment_id].sort(key=roles.index)

    fragments: list[dict[str, Any]] = []
    for fragment in row["fragments"]:
        target_needed_by = selected_roles_by_fragment.get(fragment["id"], [])
        eligible_by = list(fragment.get("needed_by", []))
        enriched = dict(fragment)
        enriched["eligible_by"] = eligible_by
        enriched["candidate_needed_by"] = eligible_by
        enriched["target_needed_by"] = target_needed_by
        enriched["needed_by"] = target_needed_by
        enriched["source_scope_visibility_gold"] = fragment.get("visibility_gold")
        enriched["visibility_gold"] = (
            visibility_label(target_needed_by, roles)
            if target_needed_by
            else ("reject" if not eligible_by else "budget_skipped")
        )
        enriched["utility_by_recipient"] = {
            role: role_utilities[role].get(fragment["id"], 0)
            for role in eligible_by
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
                "utility": role_utilities[role][fragment_id],
            }
            for fragment_id in reference_need_sets[role]
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
    for entry in row["source_scope_ledger"]:
        fragment_id = entry["fragment_id"]
        recipients = list(entry.get("recipients", []))
        source_scope_ledger.append(
            {
                **entry,
                "recipients": recipients,
                "route": "reject" if not recipients else "deliver",
                "utility_by_recipient": {
                    role: role_utilities[role].get(fragment_id, 0)
                    for role in recipients
                },
            }
        )

    suffix = f"tightbf{int(round(budget_fraction * 100)):02d}_{utility_rule}_v0"
    return {
        **row,
        "hard_evaluation_id": f"{row['hard_evaluation_id']}__{suffix}",
        "source_hard_evaluation_id": row["hard_evaluation_id"],
        "tight_budget_variant": suffix,
        "tight_budget_policy": {
            "budget_fraction": budget_fraction,
            "utility_rule": utility_rule,
            "selection": "per_role_0_1_knapsack_max_utility_then_min_cost",
            "note": "candidate_need_sets preserves the full eligible scope; reference_need_sets is the scarce-budget target.",
        },
        "fragments": fragments,
        "source_scope_ledger": source_scope_ledger,
        "candidate_need_sets": candidate_need_sets,
        "role_utilities": role_utilities,
        "role_budgets": role_budgets,
        "role_full_costs": role_full_costs,
        "role_oracle_values": role_oracle_values,
        "role_oracle_spent": role_oracle_spent,
        "reference_need_sets": reference_need_sets,
        "reference_cards": reference_cards,
        "reference_rejections": reference_rejections,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    role_budget_ratios: list[float] = []
    scarce_roles = 0
    total_roles = 0
    for row in rows:
        for role in row["roles"]:
            full_cost = row["role_full_costs"][role]
            budget = row["role_budgets"][role]
            if full_cost:
                role_budget_ratios.append(budget / full_cost)
                scarce_roles += int(budget < full_cost)
            total_roles += 1
    return {
        "rows": len(rows),
        "tight_budget_variants": sorted({row["tight_budget_variant"] for row in rows}),
        "role_count_distribution": {
            str(count): sum(1 for row in rows if len(row["roles"]) == count)
            for count in sorted({len(row["roles"]) for row in rows})
        },
        "scarce_roles": scarce_roles,
        "total_roles": total_roles,
        "mean_budget_ratio": sum(role_budget_ratios) / len(role_budget_ratios) if role_budget_ratios else 0.0,
        "mean_oracle_sources_per_role": (
            sum(len(row["reference_need_sets"][role]) for row in rows for role in row["roles"]) / total_roles
            if total_roles
            else 0.0
        ),
        "mean_candidate_sources_per_role": (
            sum(len(row["candidate_need_sets"][role]) for row in rows for role in row["roles"]) / total_roles
            if total_roles
            else 0.0
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--budget-fraction", type=float, default=0.55)
    parser.add_argument("--utility-rule", default="rank_scope")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    rows = read_jsonl(args.packet)
    if args.limit:
        rows = rows[: args.limit]
    out_rows = [
        build_tight_row(row, budget_fraction=args.budget_fraction, utility_rule=args.utility_rule)
        for row in rows
    ]
    write_jsonl(args.out, out_rows)
    print(json.dumps({**summarize(out_rows), "packet": str(args.out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
