from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_EVALUATIONS = Path("experiments/20260618-local-perspectivegap-contact/evaluations.jsonl")


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


def word_cost(text: str) -> int:
    words = [piece for piece in text.replace("\n", " ").split(" ") if piece.strip()]
    return max(1, math.ceil(len(words) / 35))


def visibility_label(fragment_id: str, roles: list[str], reference_need_sets: dict[str, list[str]]) -> str:
    needed_by = [role for role in roles if fragment_id in set(reference_need_sets.get(role, []))]
    if not needed_by:
        return "reject"
    if len(needed_by) == len(roles):
        return "shared_all"
    if len(needed_by) > 1:
        return "shared_subset"
    return "role_private"


def build_prompt(row: dict[str, Any], fragments: list[dict[str, Any]], budgets: dict[str, int]) -> str:
    roles = ", ".join(row["roles"])
    lines = [
        row["role_assignment_prompt"].split("I'm providing the following information:")[0].strip(),
        "",
        "You are building role-specific state cards under a strict communication budget.",
        f"Roles: {roles}",
        "",
        "Budget per role:",
    ]
    for role in row["roles"]:
        lines.append(f"- {role}: {budgets[role]} cost units")
    lines.extend(
        [
            "",
            "Each fragment has a source_id and a cost. Select only the fragments each role needs.",
            "For every selected fragment, copy fragment_id, source_id, and visibility exactly.",
            "A fragment may appear under multiple roles when multiple roles need it.",
            "visibility describes intended recipient scope, not whether the text sounds generally useful:",
            "- shared_all: every listed role should receive this fragment.",
            "- shared_subset: more than one role, but not every listed role, should receive this fragment.",
            "- role_private: exactly one listed role should receive this fragment.",
            "Use the same visibility label for the same selected fragment wherever it appears.",
            "The rejected list is global. Put a fragment in rejected only when no listed role should receive it.",
            "Never put a fragment in rejected if you also assign it to any role.",
            "",
            "Fragments:",
        ]
    )
    for fragment in fragments:
        lines.extend(
            [
                f"<{fragment['id']} source_id=\"{fragment['source_id']}\" cost=\"{fragment['cost']}\">",
                fragment["text"],
                f"</{fragment['id']}>",
                "",
            ]
        )
    schema = {
        "roles": {
            role: [
                {
                    "fragment_id": "f?",
                    "source_id": f"{row['scenario_id']}:f?",
                    "visibility": "shared_all|shared_subset|role_private",
                    "reason": "short reason",
                }
            ]
            for role in row["roles"]
        },
        "rejected": [
            {
                "fragment_id": "f?",
                "source_id": f"{row['scenario_id']}:f?",
                "reason": "distractor|unneeded",
            }
        ],
    }
    lines.extend(
        [
            "Respond with a single JSON object matching this schema. No markdown, no extra text.",
            json.dumps(schema, ensure_ascii=False, indent=2),
        ]
    )
    return "\n".join(lines)


def enrich_row(row: dict[str, Any]) -> dict[str, Any]:
    roles = row["roles"]
    reference_need_sets = row["reference_need_sets"]
    fragments: list[dict[str, Any]] = []
    fragment_by_id: dict[str, dict[str, Any]] = {}
    for fragment in row["fragments"]:
        source_id = f"{row['scenario_id']}:{fragment['id']}"
        cost = word_cost(fragment["text"])
        enriched = {
            "id": fragment["id"],
            "source_id": source_id,
            "text": fragment["text"],
            "is_distractor": bool(fragment.get("is_distractor")),
            "cost": cost,
            "visibility_gold": visibility_label(fragment["id"], roles, reference_need_sets),
            "needed_by": [role for role in roles if fragment["id"] in set(reference_need_sets.get(role, []))],
        }
        fragments.append(enriched)
        fragment_by_id[fragment["id"]] = enriched
    budgets = {
        role: sum(fragment_by_id[fragment_id]["cost"] for fragment_id in reference_need_sets.get(role, []))
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
            for fragment_id in reference_need_sets.get(role, [])
        ]
        for role in roles
    }
    rejected = [
        {
            "fragment_id": fragment["id"],
            "source_id": fragment["source_id"],
            "reason": "distractor" if fragment["is_distractor"] else "unneeded",
        }
        for fragment in fragments
        if fragment["visibility_gold"] == "reject"
    ]
    return {
        "hard_evaluation_id": f"{row['evaluation_id']}__hard_cards_v0",
        "base_evaluation_id": row["evaluation_id"],
        "scenario_id": row["scenario_id"],
        "shuffle_seed": row["shuffle_seed"],
        "roles": roles,
        "fragments": fragments,
        "role_budgets": budgets,
        "reference_need_sets": reference_need_sets,
        "reference_cards": reference_cards,
        "reference_rejections": rejected,
        "distractor_id": row.get("distractor_id"),
        "hard_routing_prompt": build_prompt(row, fragments, budgets),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluations", type=Path, default=DEFAULT_EVALUATIONS)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--scenario-id", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    rows = read_jsonl(args.evaluations)
    if args.scenario_id:
        keep = set(args.scenario_id)
        rows = [row for row in rows if row["scenario_id"] in keep]
    if args.limit:
        rows = rows[: args.limit]
    packet = [enrich_row(row) for row in rows]
    write_jsonl(args.out, packet)
    role_counts: dict[int, int] = {}
    for row in packet:
        role_counts[len(row["roles"])] = role_counts.get(len(row["roles"]), 0) + 1
    summary = {
        "packet": str(args.out),
        "evaluations": len(packet),
        "role_count_distribution": dict(sorted(role_counts.items())),
        "mean_fragments": sum(len(row["fragments"]) for row in packet) / len(packet) if packet else 0,
        "mean_budget_per_role": (
            sum(sum(row["role_budgets"].values()) / len(row["roles"]) for row in packet) / len(packet)
            if packet
            else 0
        ),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
