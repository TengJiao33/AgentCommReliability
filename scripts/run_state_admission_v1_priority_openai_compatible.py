#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from run_state_admission_v1_openai_compatible import (
    append_jsonl,
    call_chat,
    compact_text,
    filter_rows,
    parse_json_object_loose,
    read_jsonl,
    source_cost,
    visibility_from_selected_roles,
)


def completed_requests(path: Path, model: str) -> set[str]:
    completed: set[str] = set()
    if not path.exists():
        return completed
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("model") == model and row.get("task") == "state_admission_v1_priority_router" and (
            "response" in row or "error" in row
        ):
            completed.add(str(row.get("hard_evaluation_id", "")))
    return completed


def build_priority_prompt(row: dict[str, Any], prompt_style: str = "default") -> str:
    roles = list(row["roles"])
    source_by_fragment = {fragment["id"]: fragment["source_id"] for fragment in row["fragments"]}
    lines = [
        "You are an admission-priority planner for a multi-agent workflow.",
        "You do not output source cards directly. A deterministic executor will enforce all budgets and source assignments.",
        "",
        "Your job:",
        "- Rank admission units by priority.",
        "- An admission unit is either a pair group id or a role bundle id.",
        "- The executor reads your priority list in order and admits the first feasible units.",
        "- Pair groups are admitted atomically: all required role bundles enter together if they fit.",
        "- Role bundles are admitted atomically: all required sources enter that role if the bundle fits.",
        "- Once a role bundle is admitted, that role is closed; later units for the same role are skipped.",
        "- The executor rejects every unselected source, including eligible sources that did not enter an admitted bundle.",
        "",
        "Optimization rule:",
        "- Maximize completed pair-group utility under per-role budgets and the global budget.",
        "- If no high-value pair group fits, rank the best individual role bundles under the same budgets.",
        "- Locally useful bundles should be omitted when admitting them would block a higher-value global plan.",
        "",
        f"Global budget: {row['global_budget']} cost units",
        "",
        "Roles and per-role budgets:",
    ]
    for role in roles:
        lines.append(f"- {role}: budget={row['role_budgets'][role]}")

    lines.extend(["", "Role bundles:"])
    for role in roles:
        bundle = row.get("role_bundles", {}).get(role)
        if not bundle:
            continue
        source_ids = [source_by_fragment[fragment_id] for fragment_id in bundle.get("requires", [])]
        lines.append(
            f"- bundle_id={bundle['bundle_id']} role={role} cost={bundle['cost']} utility={bundle['utility']} requires_sources={json.dumps(source_ids, ensure_ascii=False)}"
        )

    lines.extend(["", "Pair groups:"])
    for group in row.get("cross_role_groups", []):
        lines.append(
            f"- group_id={group['group_id']} cost={group['cost']} utility={group['utility']} roles={json.dumps(group['roles'], ensure_ascii=False)} requires_bundles={json.dumps(group['requires_bundles'], ensure_ascii=False)}"
        )

    lines.extend(["", "Source access ledger:"])
    for entry in row.get("source_scope_ledger", []):
        recipients = entry.get("recipients", [])
        recipient_text = json.dumps(recipients, ensure_ascii=False) if recipients else "REJECT_ONLY"
        lines.append(
            f"- source_id={entry['source_id']} fragment_id={entry['fragment_id']} cost={source_cost(row, entry['fragment_id'])} eligible_recipients={recipient_text}"
        )

    if prompt_style == "with_payload":
        lines.extend(["", "Payload previews:"])
        for fragment in row["fragments"]:
            lines.append(
                f"- source_id={fragment['source_id']} fragment_id={fragment['id']} cost={fragment['cost']} text=\"{compact_text(fragment['text'])}\""
            )

    if prompt_style == "fallback_required":
        lines.extend(
            [
                "",
                "Executable priority requirements:",
                "- The deterministic executor reads only the JSON priority list. Explanations are ignored.",
                "- If a pair group may exceed the global budget, include the best feasible individual role bundles immediately after that group.",
                "- If the top pair group fits, still include the best fallback role bundles later in the list for auditability.",
                "- Every unit id must exactly match one listed pair group id or role bundle id.",
                "- Return JSON only. Do not use Markdown fences or prose after the JSON.",
            ]
        )

    schema = {"priority": ["pair_group_id_or_role_bundle_id"]}
    lines.extend(
        [
            "",
            "Return one valid JSON object only, with this exact shape:",
            json.dumps(schema, ensure_ascii=False, indent=2),
        ]
    )
    return "\n".join(lines)


def strip_unit_prefix(value: str) -> str:
    unit_id = value.strip()
    lowered = unit_id.lower()
    for prefix in ("bundle_id=", "group_id=", "unit_id=", "id="):
        if lowered.startswith(prefix):
            return unit_id[len(prefix) :].strip()
    return unit_id


def unit_alias_key(value: str) -> str:
    return " ".join(strip_unit_prefix(value).replace("_", " ").lower().split())


def resolve_priority_units(priority: list[str], valid_unit_ids: list[str]) -> list[str]:
    valid = set(valid_unit_ids)
    alias_to_id: dict[str, str] = {}
    ambiguous_aliases: set[str] = set()
    for unit_id in valid_unit_ids:
        alias = unit_alias_key(unit_id)
        if alias in alias_to_id and alias_to_id[alias] != unit_id:
            ambiguous_aliases.add(alias)
            continue
        alias_to_id[alias] = unit_id

    resolved: list[str] = []
    seen: set[str] = set()
    for raw_unit_id in priority:
        stripped = strip_unit_prefix(raw_unit_id)
        if stripped in valid:
            unit_id = stripped
        else:
            alias = unit_alias_key(stripped)
            unit_id = alias_to_id.get(alias) if alias not in ambiguous_aliases else None
            unit_id = unit_id or stripped
        if unit_id in seen:
            continue
        seen.add(unit_id)
        resolved.append(unit_id)
    return resolved


def token_to_unit_id(item: Any) -> str | None:
    if isinstance(item, str):
        return strip_unit_prefix(item)
    if isinstance(item, dict):
        for key in ("unit_id", "id", "group_id", "bundle_id"):
            value = item.get(key)
            if isinstance(value, str):
                return strip_unit_prefix(value)
    return None


def priority_from_response(text: str | None) -> tuple[list[str], dict[str, Any]]:
    parsed = parse_json_object_loose(text)
    blobs: list[Any] = []
    for key in ("priority", "ranked_admission_units", "admission_units", "selected_units"):
        value = parsed.get(key)
        if isinstance(value, list):
            blobs.extend(value)
    selected_groups = parsed.get("selected_groups")
    if isinstance(selected_groups, list):
        blobs.extend(selected_groups)
    selected_bundles = parsed.get("selected_bundles")
    if isinstance(selected_bundles, list):
        blobs.extend(selected_bundles)

    priority: list[str] = []
    seen: set[str] = set()
    for item in blobs:
        unit_id = token_to_unit_id(item)
        if not unit_id or unit_id in seen:
            continue
        seen.add(unit_id)
        priority.append(unit_id)
    return priority, {"priority_parsed": parsed, "priority_units": priority}


def priority_for_local_baseline(row: dict[str, Any], baseline: str) -> list[str]:
    if baseline == "oracle":
        units: list[str] = list(row.get("oracle_groups", []))
        covered_roles: set[str] = set()
        groups = {group["group_id"]: group for group in row.get("cross_role_groups", [])}
        for group_id in units:
            covered_roles.update(groups.get(group_id, {}).get("roles", []))
        for role in row.get("oracle_roles", []):
            if role not in covered_roles:
                bundle = row.get("role_bundles", {}).get(role)
                if bundle:
                    units.append(bundle["bundle_id"])
        return units
    if baseline == "group_density":
        groups = list(row.get("cross_role_groups", []))
        groups.sort(
            key=lambda group: (
                -(float(group["utility"]) / max(1, int(group["cost"]))),
                -int(group["utility"]),
                int(group["cost"]),
                group["group_id"],
            )
        )
        return [group["group_id"] for group in groups]
    if baseline == "bundle_density":
        bundles = list(row.get("role_bundles", {}).values())
        bundles.sort(
            key=lambda bundle: (
                -(float(bundle["utility"]) / max(1, int(bundle["cost"]))),
                -int(bundle["utility"]),
                int(bundle["cost"]),
                bundle["role"],
            )
        )
        return [bundle["bundle_id"] for bundle in bundles]
    raise ValueError(f"unknown local priority baseline: {baseline}")


def build_response_from_selected(row: dict[str, Any], selected_by_role: dict[str, list[str]], reason: str) -> str:
    roles = list(row["roles"])
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    selected_roles_by_fragment: dict[str, list[str]] = {}
    selected_fragments: set[str] = set()
    for role, fragment_ids in selected_by_role.items():
        for fragment_id in fragment_ids:
            if fragment_id not in fragments:
                continue
            selected_fragments.add(fragment_id)
            selected_roles_by_fragment.setdefault(fragment_id, [])
            if role not in selected_roles_by_fragment[fragment_id]:
                selected_roles_by_fragment[fragment_id].append(role)

    compiled: dict[str, Any] = {"roles": {}, "rejected": []}
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
                    "visibility": visibility_from_selected_roles(
                        selected_roles_by_fragment.get(fragment_id, [role]),
                        roles,
                    ),
                    "reason": reason,
                }
            )
        compiled["roles"][role] = cards

    for fragment in row["fragments"]:
        if fragment["id"] in selected_fragments:
            continue
        compiled["rejected"].append(
            {
                "fragment_id": fragment["id"],
                "source_id": fragment["source_id"],
                "reason": "priority_executor_reject_unselected",
            }
        )
    return json.dumps(compiled, ensure_ascii=False)


def compile_priority_cards_pair_group_primary(row: dict[str, Any], priority: list[str]) -> tuple[str, dict[str, Any]]:
    roles = list(row["roles"])
    bundles_by_id = {bundle["bundle_id"]: bundle for bundle in row.get("role_bundles", {}).values()}
    groups_by_id = {group["group_id"]: group for group in row.get("cross_role_groups", [])}
    resolved_priority = resolve_priority_units(priority, list(groups_by_id) + list(bundles_by_id))
    selected_by_role: dict[str, list[str]] = {role: [] for role in roles}
    selected_roles: set[str] = set()
    global_budget = int(row.get("global_budget", 0))
    global_spent = 0
    accepted_units: list[str] = []
    skipped_units: list[dict[str, Any]] = []

    def accept_bundle(bundle: dict[str, Any]) -> None:
        nonlocal global_spent
        role = bundle["role"]
        selected_by_role[role] = list(bundle.get("requires", []))
        selected_roles.add(role)
        global_spent += int(bundle["cost"])

    def try_accept_group(unit_id: str) -> None:
        nonlocal global_spent
        group = groups_by_id[unit_id]
        group_bundles = [bundles_by_id[bundle_id] for bundle_id in group.get("requires_bundles", []) if bundle_id in bundles_by_id]
        group_roles = {bundle["role"] for bundle in group_bundles}
        if len(group_bundles) != len(group.get("requires_bundles", [])):
            skipped_units.append({"unit_id": unit_id, "reason": "missing_bundle"})
            return
        if selected_roles & group_roles:
            skipped_units.append({"unit_id": unit_id, "reason": "role_already_closed"})
            return
        if global_spent + int(group["cost"]) > global_budget:
            skipped_units.append({"unit_id": unit_id, "reason": "global_budget"})
            return
        for bundle in group_bundles:
            if int(bundle["cost"]) > int(row["role_budgets"].get(bundle["role"], 0)):
                skipped_units.append({"unit_id": unit_id, "reason": "role_budget"})
                return
        for bundle in group_bundles:
            accept_bundle(bundle)
        accepted_units.append(unit_id)

    def try_accept_bundle(unit_id: str) -> None:
        bundle = bundles_by_id[unit_id]
        role = bundle["role"]
        cost = int(bundle["cost"])
        if role in selected_roles:
            skipped_units.append({"unit_id": unit_id, "reason": "role_already_closed"})
            return
        if cost > int(row["role_budgets"].get(role, 0)):
            skipped_units.append({"unit_id": unit_id, "reason": "role_budget"})
            return
        if global_spent + cost > global_budget:
            skipped_units.append({"unit_id": unit_id, "reason": "global_budget"})
            return
        accept_bundle(bundle)
        accepted_units.append(unit_id)

    for unit_id in resolved_priority:
        if unit_id in groups_by_id:
            try_accept_group(unit_id)
        elif unit_id not in bundles_by_id:
            skipped_units.append({"unit_id": unit_id, "reason": "unknown_unit"})

    accepted_group_count = sum(1 for unit_id in accepted_units if unit_id in groups_by_id)
    if accepted_group_count:
        for unit_id in resolved_priority:
            if unit_id in bundles_by_id:
                skipped_units.append({"unit_id": unit_id, "reason": "pair_group_primary_mode"})
    else:
        for unit_id in resolved_priority:
            if unit_id in bundles_by_id:
                try_accept_bundle(unit_id)

    meta = {
        "executor_policy": "pair_group_primary",
        "raw_priority_units": priority,
        "priority_units": resolved_priority,
        "accepted_units": accepted_units,
        "skipped_units": skipped_units,
        "selected_roles": sorted(selected_roles, key=roles.index),
        "executor_global_spent": global_spent,
        "executor_global_budget": global_budget,
    }
    return build_response_from_selected(row, selected_by_role, "compiled_from_state_admission_priority"), meta


def compile_priority_cards(row: dict[str, Any], priority: list[str], executor_policy: str = "greedy") -> tuple[str, dict[str, Any]]:
    if executor_policy == "pair_group_primary":
        return compile_priority_cards_pair_group_primary(row, priority)
    if executor_policy != "greedy":
        raise ValueError(f"unknown executor policy: {executor_policy}")

    roles = list(row["roles"])
    bundles_by_id = {bundle["bundle_id"]: bundle for bundle in row.get("role_bundles", {}).values()}
    groups_by_id = {group["group_id"]: group for group in row.get("cross_role_groups", [])}
    resolved_priority = resolve_priority_units(priority, list(groups_by_id) + list(bundles_by_id))
    selected_by_role: dict[str, list[str]] = {role: [] for role in roles}
    selected_roles: set[str] = set()
    global_budget = int(row.get("global_budget", 0))
    global_spent = 0
    accepted_units: list[str] = []
    skipped_units: list[dict[str, Any]] = []

    def can_accept_bundle(bundle: dict[str, Any]) -> tuple[bool, str]:
        role = bundle["role"]
        cost = int(bundle["cost"])
        if role in selected_roles:
            return False, "role_already_closed"
        if cost > int(row["role_budgets"].get(role, 0)):
            return False, "role_budget"
        if global_spent + cost > global_budget:
            return False, "global_budget"
        return True, "ok"

    def accept_bundle(bundle: dict[str, Any]) -> None:
        nonlocal global_spent
        role = bundle["role"]
        selected_by_role[role] = list(bundle.get("requires", []))
        selected_roles.add(role)
        global_spent += int(bundle["cost"])

    for unit_id in resolved_priority:
        if unit_id in groups_by_id:
            group = groups_by_id[unit_id]
            group_bundles = [bundles_by_id[bundle_id] for bundle_id in group.get("requires_bundles", []) if bundle_id in bundles_by_id]
            group_roles = {bundle["role"] for bundle in group_bundles}
            if len(group_bundles) != len(group.get("requires_bundles", [])):
                skipped_units.append({"unit_id": unit_id, "reason": "missing_bundle"})
                continue
            if selected_roles & group_roles:
                skipped_units.append({"unit_id": unit_id, "reason": "role_already_closed"})
                continue
            if global_spent + int(group["cost"]) > global_budget:
                skipped_units.append({"unit_id": unit_id, "reason": "global_budget"})
                continue
            failed_reason = None
            for bundle in group_bundles:
                cost = int(bundle["cost"])
                if cost > int(row["role_budgets"].get(bundle["role"], 0)):
                    failed_reason = "role_budget"
                    break
            if failed_reason:
                skipped_units.append({"unit_id": unit_id, "reason": failed_reason})
                continue
            for bundle in group_bundles:
                accept_bundle(bundle)
            accepted_units.append(unit_id)
            continue

        if unit_id in bundles_by_id:
            bundle = bundles_by_id[unit_id]
            ok, reason = can_accept_bundle(bundle)
            if not ok:
                skipped_units.append({"unit_id": unit_id, "reason": reason})
                continue
            accept_bundle(bundle)
            accepted_units.append(unit_id)
            continue

        skipped_units.append({"unit_id": unit_id, "reason": "unknown_unit"})

    meta = {
        "executor_policy": "greedy",
        "raw_priority_units": priority,
        "priority_units": resolved_priority,
        "accepted_units": accepted_units,
        "skipped_units": skipped_units,
        "selected_roles": sorted(selected_roles, key=roles.index),
        "executor_global_spent": global_spent,
        "executor_global_budget": global_budget,
    }
    return build_response_from_selected(row, selected_by_role, "compiled_from_state_admission_priority"), meta


def write_prompt_dry_run(rows: list[dict[str, Any]], path: Path, prompt_style: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            prompt = build_priority_prompt(row, prompt_style)
            handle.write(
                json.dumps(
                    {
                        "hard_evaluation_id": row["hard_evaluation_id"],
                        "base_evaluation_id": row["base_evaluation_id"],
                        "scenario_id": row["scenario_id"],
                        "shuffle_seed": row["shuffle_seed"],
                        "prompt_style": prompt_style,
                        "roles": row["roles"],
                        "global_budget": row["global_budget"],
                        "oracle_groups": row.get("oracle_groups", []),
                        "oracle_roles": row.get("oracle_roles", []),
                        "prompt": prompt,
                        "prompt_chars": len(prompt),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def run_local_baseline(args: argparse.Namespace, rows: list[dict[str, Any]]) -> None:
    for row in rows:
        priority = priority_for_local_baseline(row, args.local_priority_baseline)
        compiled_response, meta = compile_priority_cards(row, priority, args.executor_policy)
        append_jsonl(
            args.out,
            {
                "hard_evaluation_id": row["hard_evaluation_id"],
                "base_evaluation_id": row["base_evaluation_id"],
                "scenario_id": row["scenario_id"],
                "shuffle_seed": row["shuffle_seed"],
                "state_admission_variant": row.get("state_admission_variant"),
                "task": f"state_admission_v1_priority_{args.local_priority_baseline}",
                "model": args.local_priority_baseline,
                "provider": "local",
                "priority_response": json.dumps({"priority": priority}, ensure_ascii=False),
                "priority_meta": meta,
                "response": compiled_response,
                "status": "ok",
            },
        )


def run_recompile(args: argparse.Namespace, rows: list[dict[str, Any]]) -> None:
    predictions_by_id: dict[str, dict[str, Any]] = {}
    for prediction in read_jsonl(args.recompile_predictions):
        if "hard_evaluation_id" in prediction:
            predictions_by_id[prediction["hard_evaluation_id"]] = prediction
        if "source_hard_evaluation_id" in prediction:
            predictions_by_id[prediction["source_hard_evaluation_id"]] = prediction
        if "base_evaluation_id" in prediction:
            predictions_by_id[prediction["base_evaluation_id"]] = prediction

    for row in rows:
        request_id = row["hard_evaluation_id"]
        source_prediction = (
            predictions_by_id.get(request_id)
            or predictions_by_id.get(row.get("source_hard_evaluation_id", ""))
            or predictions_by_id.get(row["base_evaluation_id"])
        )
        out_row = {
            "hard_evaluation_id": request_id,
            "base_evaluation_id": row["base_evaluation_id"],
            "scenario_id": row["scenario_id"],
            "shuffle_seed": row["shuffle_seed"],
            "state_admission_variant": row.get("state_admission_variant"),
            "task": "state_admission_v1_priority_recompiled",
            "model": (source_prediction or {}).get("model", "unknown"),
            "provider": "local-recompile",
            "prompt_style": (source_prediction or {}).get("prompt_style"),
            "executor_policy": args.executor_policy,
        }
        try:
            if not source_prediction:
                raise ValueError("missing source priority prediction")
            priority_response = source_prediction.get("priority_response")
            priority, priority_meta = priority_from_response(priority_response)
            compiled_response, compile_meta = compile_priority_cards(row, priority, args.executor_policy)
            out_row["priority_response"] = priority_response
            out_row["priority_meta"] = {**priority_meta, **compile_meta}
            out_row["response"] = compiled_response
            out_row["status"] = "ok"
        except Exception as error:  # noqa: BLE001
            out_row["response"] = None
            out_row["status"] = "error"
            out_row["error"] = {"type": type(error).__name__, "message": str(error)}
        append_jsonl(args.out, out_row)


def run(args: argparse.Namespace) -> None:
    rows = filter_rows(read_jsonl(args.packet), args)
    if args.dry_run_prompts_out:
        write_prompt_dry_run(rows, args.dry_run_prompts_out, args.prompt_style)
        print(json.dumps({"rows": len(rows), "dry_run_prompts_out": str(args.dry_run_prompts_out)}, ensure_ascii=False, indent=2))
        return

    if args.local_priority_baseline:
        if not args.out:
            raise SystemExit("--out is required for local priority baselines")
        run_local_baseline(args, rows)
        print(
            json.dumps(
                {"rows": len(rows), "local_priority_baseline": args.local_priority_baseline, "out": str(args.out)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.recompile_predictions:
        if not args.out:
            raise SystemExit("--out is required for recompile mode")
        run_recompile(args, rows)
        print(
            json.dumps(
                {
                    "rows": len(rows),
                    "recompile_predictions": str(args.recompile_predictions),
                    "executor_policy": args.executor_policy,
                    "out": str(args.out),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if not args.base_url or not args.out:
        raise SystemExit("provide --base-url and --out unless using --dry-run-prompts-out or --local-priority-baseline")

    from openai import OpenAI

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is not set")
    client = OpenAI(api_key=api_key, base_url=args.base_url)
    completed = completed_requests(args.out, args.model)
    print(f"model={args.model}")
    print(f"packet={args.packet}")
    print(f"evaluations={len(rows)}")
    print(f"temperature={args.temperature}")
    print(f"max_tokens={args.max_tokens}")
    print(f"prompt_style={args.prompt_style}")
    print(f"completed={len(completed)}")
    for index, row in enumerate(rows, start=1):
        request_id = row["hard_evaluation_id"]
        if request_id in completed:
            print(f"[{index}/{len(rows)}] skip {request_id}", flush=True)
            continue
        print(f"[{index}/{len(rows)}] state_admission_priority {request_id}", flush=True)
        out_row = {
            "hard_evaluation_id": request_id,
            "base_evaluation_id": row["base_evaluation_id"],
            "scenario_id": row["scenario_id"],
            "shuffle_seed": row["shuffle_seed"],
            "state_admission_variant": row.get("state_admission_variant"),
            "task": "state_admission_v1_priority_router",
            "model": args.model,
            "provider": "openai-compatible",
            "prompt_style": args.prompt_style,
        }
        try:
            prompt = build_priority_prompt(row, args.prompt_style)
            priority_response = call_chat(client, args, prompt)
            priority, priority_meta = priority_from_response(priority_response)
            compiled_response, compile_meta = compile_priority_cards(row, priority, args.executor_policy)
            out_row["admission_prompt"] = prompt if args.include_prompts else None
            out_row["priority_response"] = priority_response
            out_row["priority_meta"] = {**priority_meta, **compile_meta}
            out_row["response"] = compiled_response
            out_row["status"] = "ok"
        except Exception as error:  # noqa: BLE001
            out_row["response"] = None
            out_row["status"] = "error"
            out_row["error"] = {"type": type(error).__name__, "message": str(error)}
        append_jsonl(args.out, out_row)
        completed.add(request_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run State Admission V1 priority router with deterministic executor.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--base-url")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--model", default="state-admission-v1-priority-router")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--scenario-id", action="append", default=[])
    parser.add_argument("--hard-evaluation-id", action="append", default=[])
    parser.add_argument("--role-count", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--prompt-style", choices=["default", "with_payload", "fallback_required"], default="default")
    parser.add_argument("--executor-policy", choices=["greedy", "pair_group_primary"], default="greedy")
    parser.add_argument("--local-priority-baseline", choices=["oracle", "group_density", "bundle_density"])
    parser.add_argument("--recompile-predictions", type=Path)
    parser.add_argument("--include-prompts", action="store_true")
    parser.add_argument("--dry-run-prompts-out", type=Path)
    return parser


def main() -> None:
    run(build_parser().parse_args())


if __name__ == "__main__":
    main()
