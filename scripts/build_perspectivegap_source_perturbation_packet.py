from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PACKET = Path("experiments/20260618-local-perspectivegap-hard-routing-v0/hard_packet_stratified20.jsonl")


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
        return "reject"
    if len(recipients) == len(roles):
        return "shared_all"
    if len(recipients) > 1:
        return "shared_subset"
    return "role_private"


def rotate_recipients(recipients: list[str], roles: list[str], shift: int) -> list[str]:
    if not recipients:
        return []
    role_to_index = {role: index for index, role in enumerate(roles)}
    rotated: list[str] = []
    for role in recipients:
        index = role_to_index[role]
        rotated.append(roles[(index + shift) % len(roles)])
    return sorted(set(rotated), key=roles.index)


def build_variant(row: dict[str, Any], variant: str) -> dict[str, Any]:
    roles = list(row["roles"])
    if variant == "original_scope":
        shift = 0
    elif variant == "rotated_scope":
        shift = 1
    else:
        raise ValueError(f"unknown variant: {variant}")

    fragments: list[dict[str, Any]] = []
    reference_need_sets: dict[str, list[str]] = {role: [] for role in roles}
    source_scope_ledger: list[dict[str, Any]] = []
    for fragment in row["fragments"]:
        original_recipients = [
            role
            for role in roles
            if fragment["id"] in set(row["reference_need_sets"].get(role, []))
        ]
        recipients = rotate_recipients(original_recipients, roles, shift)
        source_id = f"{row['scenario_id']}:{variant}:{fragment['id']}"
        visibility = visibility_label(recipients, roles)
        enriched = {
            "id": fragment["id"],
            "source_id": source_id,
            "text": fragment["text"],
            "is_distractor": bool(fragment.get("is_distractor")),
            "cost": fragment["cost"],
            "visibility_gold": visibility,
            "needed_by": recipients,
            "original_needed_by": original_recipients,
        }
        fragments.append(enriched)
        for role in recipients:
            reference_need_sets[role].append(fragment["id"])
        source_scope_ledger.append(
            {
                "fragment_id": fragment["id"],
                "source_id": source_id,
                "recipients": recipients,
                "route": "reject" if not recipients else "deliver",
                "original_recipients": original_recipients,
            }
        )

    fragment_by_id = {fragment["id"]: fragment for fragment in fragments}
    budgets = {
        role: sum(fragment_by_id[fragment_id]["cost"] for fragment_id in reference_need_sets[role])
        for role in roles
    }
    reference_cards = {
        role: [
            {
                "fragment_id": fragment_id,
                "source_id": fragment_by_id[fragment_id]["source_id"],
                "visibility": fragment_by_id[fragment_id]["visibility_gold"],
                "cost": fragment_by_id[fragment_id]["cost"],
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
        if fragment["visibility_gold"] == "reject"
    ]
    return {
        "hard_evaluation_id": f"{row['base_evaluation_id']}__source_{variant}_v0",
        "base_evaluation_id": row["base_evaluation_id"],
        "scenario_id": row["scenario_id"],
        "shuffle_seed": row["shuffle_seed"],
        "source_perturbation_variant": variant,
        "roles": roles,
        "fragments": fragments,
        "source_scope_ledger": source_scope_ledger,
        "role_budgets": budgets,
        "reference_need_sets": reference_need_sets,
        "reference_cards": reference_cards,
        "reference_rejections": reference_rejections,
        "distractor_id": row.get("distractor_id"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--variant", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    variants = args.variant or ["rotated_scope"]
    rows = read_jsonl(args.packet)
    if args.limit:
        rows = rows[: args.limit]
    out_rows: list[dict[str, Any]] = []
    for row in rows:
        for variant in variants:
            out_rows.append(build_variant(row, variant))
    write_jsonl(args.out, out_rows)

    role_counts: dict[int, int] = {}
    variant_counts: dict[str, int] = {}
    for row in out_rows:
        role_counts[len(row["roles"])] = role_counts.get(len(row["roles"]), 0) + 1
        variant = row["source_perturbation_variant"]
        variant_counts[variant] = variant_counts.get(variant, 0) + 1
    summary = {
        "packet": str(args.out),
        "rows": len(out_rows),
        "variants": variant_counts,
        "role_count_distribution": dict(sorted(role_counts.items())),
        "mean_fragments": sum(len(row["fragments"]) for row in out_rows) / len(out_rows) if out_rows else 0,
        "mean_budget_per_role": (
            sum(sum(row["role_budgets"].values()) / len(row["roles"]) for row in out_rows) / len(out_rows)
            if out_rows
            else 0
        ),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
