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
)


def completed_requests(path: Path, model: str) -> set[str]:
    completed: set[str] = set()
    if not path.exists():
        return completed
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("model") == model and row.get("task") == "state_admission_v1_ledger_router" and (
            "response" in row or "error" in row
        ):
            completed.add(str(row.get("hard_evaluation_id", "")))
    return completed


def normalize_source_tokens(blob: Any) -> list[str]:
    if not isinstance(blob, list):
        return []
    out: list[str] = []
    for item in blob:
        if isinstance(item, str):
            out.append(item.strip())
        elif isinstance(item, dict) and isinstance(item.get("source_id"), str):
            out.append(item["source_id"].strip())
        elif isinstance(item, dict) and isinstance(item.get("fragment_id"), str):
            out.append(item["fragment_id"].strip())
    return [item for item in out if item]


def visibility_from_selected_roles(selected_roles: list[str], all_roles: list[str]) -> str:
    if len(selected_roles) == len(all_roles):
        return "shared_all"
    if len(selected_roles) > 1:
        return "shared_subset"
    return "role_private"


def build_ledger_prompt(row: dict[str, Any], prompt_style: str = "utility_payload") -> str:
    roles = list(row["roles"])
    lines = [
        "You are a source-ledger admission planner for a multi-agent workflow.",
        "No role-bundle or pair-group table is available. Construct source-level admission priorities from the ledger.",
        "A deterministic executor will read each role list in order and admit only feasible source assignments.",
        "",
        "Rules:",
        "- Output source_id strings only.",
        "- Admit a source to a role only if that role is listed in eligible_recipients.",
        "- A source with REJECT_ONLY must not be assigned to any role.",
        "- Stay within every per-role budget and the global budget; the executor will skip infeasible assignments.",
        "- Incomplete evidence sets may score zero after evaluation, so prefer coherent sets over isolated attractive snippets.",
        "- Return JSON only, with no markdown or explanations.",
        "",
        f"Global budget: {row['global_budget']} cost units",
        "",
        "Roles and per-role budgets:",
    ]
    for role in roles:
        lines.append(f"- {role}: budget={row['role_budgets'][role]}")

    lines.extend(["", "Source access ledger:"])
    for entry in row.get("source_scope_ledger", []):
        recipients = entry.get("recipients", [])
        recipient_text = json.dumps(recipients, ensure_ascii=False) if recipients else "REJECT_ONLY"
        utility = entry.get("utility_by_recipient", {})
        hint = entry.get("standalone_hint_by_recipient", {})
        lines.append(
            f"- source_id={entry['source_id']} fragment_id={entry['fragment_id']} "
            f"cost={source_cost(row, entry['fragment_id'])} eligible_recipients={recipient_text} "
            f"utility_by_recipient={json.dumps(utility, ensure_ascii=False)} "
            f"standalone_hint={json.dumps(hint, ensure_ascii=False)}"
        )

    if prompt_style == "utility_payload":
        lines.extend(["", "Payload previews:"])
        for fragment in row["fragments"]:
            lines.append(
                f"- source_id={fragment['source_id']} fragment_id={fragment['id']} cost={fragment['cost']} "
                f"text=\"{compact_text(fragment['text'])}\""
            )

    schema = {"roles": {role: ["source_id"] for role in roles}, "rejected": ["source_id"]}
    lines.extend(["", "Return one valid JSON object with this exact shape:", json.dumps(schema, ensure_ascii=False, indent=2)])
    return "\n".join(lines)


def compile_ledger_cards(row: dict[str, Any], ledger_response: str | None) -> tuple[str, dict[str, Any]]:
    parsed = parse_json_object_loose(ledger_response)
    role_blob = parsed.get("roles", parsed)
    if not isinstance(role_blob, dict):
        role_blob = {}
    roles = list(row["roles"])
    fragments_by_source = {fragment["source_id"]: fragment for fragment in row["fragments"]}
    fragments_by_id = {fragment["id"]: fragment for fragment in row["fragments"]}
    ledger_by_source = {
        entry["source_id"]: {
            "fragment_id": entry["fragment_id"],
            "recipients": set(entry.get("recipients", [])),
        }
        for entry in row.get("source_scope_ledger", [])
    }

    def resolve_source(token: str) -> tuple[str, dict[str, Any] | None]:
        if token in fragments_by_source:
            return token, fragments_by_source[token]
        if token in fragments_by_id:
            fragment = fragments_by_id[token]
            return fragment["source_id"], fragment
        return token, None

    selected_by_role: dict[str, list[str]] = {role: [] for role in roles}
    selected_roles_by_source: dict[str, list[str]] = {}
    global_spent = 0
    meta: dict[str, Any] = {
        "ledger_parsed": parsed,
        "compiler": "source_priority_filter_to_ledger_scope_and_budgets",
        "role_stats": {},
    }

    for role in roles:
        spent = 0
        seen: set[str] = set()
        stats = {
            "budget": int(row["role_budgets"].get(role, 0)),
            "spent": 0,
            "invalid": [],
            "duplicate": [],
            "wrong_recipient": [],
            "role_budget": [],
            "global_budget": [],
        }
        for token in normalize_source_tokens(role_blob.get(role, [])):
            source_id, fragment = resolve_source(token)
            if source_id in seen:
                stats["duplicate"].append(source_id)
                continue
            seen.add(source_id)
            if fragment is None or source_id not in ledger_by_source:
                stats["invalid"].append(source_id)
                continue
            if role not in ledger_by_source[source_id]["recipients"]:
                stats["wrong_recipient"].append(source_id)
                continue
            cost = int(fragment["cost"])
            if spent + cost > int(row["role_budgets"].get(role, 0)):
                stats["role_budget"].append(source_id)
                continue
            if global_spent + cost > int(row.get("global_budget", 0)):
                stats["global_budget"].append(source_id)
                continue
            selected_by_role[role].append(source_id)
            selected_roles_by_source.setdefault(source_id, [])
            if role not in selected_roles_by_source[source_id]:
                selected_roles_by_source[source_id].append(role)
            spent += cost
            global_spent += cost
        stats["spent"] = spent
        meta["role_stats"][role] = stats

    compiled: dict[str, Any] = {"roles": {}, "rejected": []}
    for role in roles:
        cards: list[dict[str, Any]] = []
        for source_id in selected_by_role[role]:
            fragment = fragments_by_source[source_id]
            cards.append(
                {
                    "fragment_id": fragment["id"],
                    "source_id": source_id,
                    "visibility": visibility_from_selected_roles(selected_roles_by_source[source_id], roles),
                    "reason": "compiled_from_state_admission_ledger_priority",
                }
            )
        compiled["roles"][role] = cards

    selected_sources = set(selected_roles_by_source)
    for fragment in row["fragments"]:
        if fragment["source_id"] in selected_sources:
            continue
        compiled["rejected"].append(
            {
                "fragment_id": fragment["id"],
                "source_id": fragment["source_id"],
                "reason": "ledger_priority_reject_unselected",
            }
        )

    meta["selected_roles_by_source"] = selected_roles_by_source
    meta["executor_global_spent"] = global_spent
    meta["executor_global_budget"] = int(row.get("global_budget", 0))
    return json.dumps(compiled, ensure_ascii=False), meta


def local_ledger_priority(row: dict[str, Any], baseline: str) -> dict[str, list[str]]:
    if baseline == "oracle":
        return {
            role: [fragment["source_id"] for fragment in row["fragments"] if fragment["id"] in row["reference_need_sets"].get(role, [])]
            for role in row["roles"]
        }

    use_hint = baseline == "hint_density"
    edges: list[tuple[float, int, str, str]] = []
    for entry in row.get("source_scope_ledger", []):
        for role in entry.get("recipients", []):
            scores = entry.get("standalone_hint_by_recipient" if use_hint else "utility_by_recipient", {})
            score = int(scores.get(role, 0))
            cost = max(1, source_cost(row, entry["fragment_id"]))
            edges.append((score / cost, score, role, entry["source_id"]))
    edges.sort(key=lambda item: (-item[0], -item[1], item[2], item[3]))
    priority = {role: [] for role in row["roles"]}
    for _, _, role, source_id in edges:
        priority[role].append(source_id)
    return priority


def write_prompt_dry_run(rows: list[dict[str, Any]], path: Path, prompt_style: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            prompt = build_ledger_prompt(row, prompt_style)
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
                        "prompt": prompt,
                        "prompt_chars": len(prompt),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def run_local_baseline(args: argparse.Namespace, rows: list[dict[str, Any]]) -> None:
    for row in rows:
        priority = local_ledger_priority(row, args.local_ledger_baseline)
        response, meta = compile_ledger_cards(row, json.dumps({"roles": priority, "rejected": []}, ensure_ascii=False))
        append_jsonl(
            args.out,
            {
                "hard_evaluation_id": row["hard_evaluation_id"],
                "base_evaluation_id": row["base_evaluation_id"],
                "scenario_id": row["scenario_id"],
                "shuffle_seed": row["shuffle_seed"],
                "state_admission_variant": row.get("state_admission_variant"),
                "task": f"state_admission_v1_ledger_{args.local_ledger_baseline}",
                "model": args.local_ledger_baseline,
                "provider": "local",
                "ledger_response": json.dumps({"roles": priority, "rejected": []}, ensure_ascii=False),
                "ledger_meta": meta,
                "response": response,
                "status": "ok",
            },
        )


def run_model(args: argparse.Namespace, rows: list[dict[str, Any]]) -> None:
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
        print(f"[{index}/{len(rows)}] state_admission_ledger {request_id}", flush=True)
        out_row = {
            "hard_evaluation_id": request_id,
            "base_evaluation_id": row["base_evaluation_id"],
            "scenario_id": row["scenario_id"],
            "shuffle_seed": row["shuffle_seed"],
            "state_admission_variant": row.get("state_admission_variant"),
            "task": "state_admission_v1_ledger_router",
            "model": args.model,
            "provider": "openai-compatible",
            "prompt_style": args.prompt_style,
        }
        try:
            prompt = build_ledger_prompt(row, args.prompt_style)
            ledger_response = call_chat(client, args, prompt)
            compiled_response, meta = compile_ledger_cards(row, ledger_response)
            out_row["ledger_prompt"] = prompt if args.include_prompts else None
            out_row["ledger_response"] = ledger_response
            out_row["ledger_meta"] = meta
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
        print(json.dumps({"rows": len(rows), "dry_run_prompts_out": str(args.dry_run_prompts_out)}, indent=2))
        return
    if args.local_ledger_baseline:
        if not args.out:
            raise SystemExit("--out is required for local baseline")
        run_local_baseline(args, rows)
        print(json.dumps({"rows": len(rows), "baseline": args.local_ledger_baseline, "out": str(args.out)}, indent=2))
        return
    if not args.out:
        raise SystemExit("--out is required")
    run_model(args, rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run State Admission V1 source-ledger router with budget compiler.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--base-url")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--model", default="state-admission-v1-ledger-router")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--scenario-id", action="append", default=[])
    parser.add_argument("--hard-evaluation-id", action="append", default=[])
    parser.add_argument("--role-count", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--prompt-style", choices=["utility", "utility_payload"], default="utility_payload")
    parser.add_argument("--local-ledger-baseline", choices=["oracle", "utility_density", "hint_density"])
    parser.add_argument("--include-prompts", action="store_true")
    parser.add_argument("--dry-run-prompts-out", type=Path)
    return parser


def main() -> None:
    run(build_parser().parse_args())


if __name__ == "__main__":
    main()
