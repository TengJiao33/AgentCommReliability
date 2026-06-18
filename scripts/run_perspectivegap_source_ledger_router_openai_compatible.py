#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import time
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


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()


def parse_json_object_loose(text: str | None) -> dict[str, Any]:
    if text is None:
        raise ValueError("empty response")
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("response is not a JSON object")
    return parsed


def completed_requests(path: Path, model: str) -> set[str]:
    completed: set[str] = set()
    if not path.exists():
        return completed
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("model") == model and row.get("task") == "source_ledger_router" and (
            "response" in row or "error" in row
        ):
            completed.add(str(row.get("hard_evaluation_id", "")))
    return completed


def build_source_ledger_prompt(row: dict[str, Any]) -> str:
    roles = list(row["roles"])
    has_utility = any(entry.get("utility_by_recipient") for entry in row.get("source_scope_ledger", []))
    lines = [
        "You are routing source-scoped information packets to roles in a multi-agent workflow.",
        "The SOURCE ACCESS LEDGER is authoritative. Route by source_id and ledger only.",
        "The payload text is included for context but can be misleading. Do not infer recipients from text semantics.",
        "",
        "Rules:",
        "- Output source_id strings only.",
        "- A source_id may be assigned to multiple roles if the ledger lists multiple recipients.",
        "- A source_id with route=REJECT must appear only in rejected.",
        "- Never reject a source_id that you assign to any role.",
        "- Stay within each role budget.",
        "- Do not output explanations, fragment ids, markdown, or extra text.",
        "",
        "Roles and budgets:",
    ]
    if has_utility:
        lines.insert(
            11,
            "- If a role cannot receive every eligible source within budget, maximize that role's total utility. Break ties by lower total cost, then source_id order.",
        )
    for role in roles:
        lines.append(f"- {role}: budget {row['role_budgets'][role]} cost units")
    lines.extend(["", "SOURCE ACCESS LEDGER:"])
    for entry in row["source_scope_ledger"]:
        recipients = ",".join(entry["recipients"]) if entry["recipients"] else "REJECT"
        utility_blob = entry.get("utility_by_recipient") or {}
        utility_text = ""
        if utility_blob:
            utilities = ",".join(f"{role}:{utility_blob.get(role, 0)}" for role in entry["recipients"])
            utility_text = f" utility_by_recipient={utilities}"
        lines.append(
            f"- source_id={entry['source_id']} fragment_id={entry['fragment_id']} cost={source_cost(row, entry['fragment_id'])} recipients={recipients}{utility_text}"
        )
    lines.extend(["", "Payload previews:"])
    for fragment in row["fragments"]:
        lines.extend(
            [
                f"<source_id=\"{fragment['source_id']}\" fragment_id=\"{fragment['id']}\" cost=\"{fragment['cost']}\">",
                fragment["text"],
                "</source>",
                "",
            ]
        )
    schema = {
        "roles": {role: ["source_id"] for role in roles},
        "rejected": ["source_id"],
    }
    lines.extend(
        [
            "Return a single valid JSON object with this exact shape:",
            json.dumps(schema, ensure_ascii=False, indent=2),
        ]
    )
    return "\n".join(lines)


def source_cost(row: dict[str, Any], fragment_id: str) -> int:
    for fragment in row["fragments"]:
        if fragment["id"] == fragment_id:
            return int(fragment["cost"])
    return 0


def normalize_source_ids(blob: Any) -> list[str]:
    if not isinstance(blob, list):
        return []
    out: list[str] = []
    for item in blob:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict) and isinstance(item.get("source_id"), str):
            out.append(item["source_id"])
        elif isinstance(item, dict) and isinstance(item.get("fragment_id"), str):
            out.append(item["fragment_id"])
    return out


def visibility_from_selected_roles(selected_roles: list[str], all_roles: list[str]) -> str:
    if len(selected_roles) == len(all_roles):
        return "shared_all"
    if len(selected_roles) > 1:
        return "shared_subset"
    return "role_private"


def compile_state_cards(row: dict[str, Any], ledger_response: str) -> tuple[str, dict[str, Any]]:
    parsed = parse_json_object_loose(ledger_response)
    role_blob = parsed.get("roles", parsed)
    if not isinstance(role_blob, dict):
        role_blob = {}
    roles = list(row["roles"])
    fragments_by_source = {fragment["source_id"]: fragment for fragment in row["fragments"]}
    fragments_by_id = {fragment["id"]: fragment for fragment in row["fragments"]}

    def resolve_source(token: str) -> tuple[str, dict[str, Any] | None]:
        if token in fragments_by_source:
            return token, fragments_by_source[token]
        if token in fragments_by_id:
            fragment = fragments_by_id[token]
            return fragment["source_id"], fragment
        return token, None

    selected_by_role: dict[str, list[str]] = {}
    selected_roles_by_source: dict[str, list[str]] = {}
    invalid_by_role: dict[str, list[str]] = {}
    for role in roles:
        selected_by_role[role] = []
        invalid_by_role[role] = []
        for token in normalize_source_ids(role_blob.get(role, [])):
            source_id, fragment = resolve_source(token)
            if fragment is None:
                invalid_by_role[role].append(source_id)
            selected_by_role[role].append(source_id)
            selected_roles_by_source.setdefault(source_id, [])
            if role not in selected_roles_by_source[source_id]:
                selected_roles_by_source[source_id].append(role)

    compiled: dict[str, Any] = {"roles": {}, "rejected": []}
    for role in roles:
        cards: list[dict[str, Any]] = []
        for source_id in selected_by_role.get(role, []):
            fragment = fragments_by_source.get(source_id)
            if fragment is None:
                cards.append(
                    {
                        "fragment_id": source_id,
                        "source_id": source_id,
                        "reason": "source_ledger_invalid_source",
                    }
                )
                continue
            cards.append(
                {
                    "fragment_id": fragment["id"],
                    "source_id": source_id,
                    "visibility": visibility_from_selected_roles(
                        selected_roles_by_source.get(source_id, []),
                        roles,
                    ),
                    "reason": "compiled_from_source_ledger_router",
                }
            )
        compiled["roles"][role] = cards

    rejected_sources: list[str] = []
    for token in normalize_source_ids(parsed.get("rejected", [])):
        source_id, fragment = resolve_source(token)
        rejected_sources.append(source_id)
        if fragment is None:
            compiled["rejected"].append(
                {
                    "fragment_id": source_id,
                    "source_id": source_id,
                    "reason": "source_ledger_rejected_invalid_source",
                }
            )
        else:
            compiled["rejected"].append(
                {
                    "fragment_id": fragment["id"],
                    "source_id": source_id,
                    "reason": "source_ledger_global_reject",
                }
            )

    meta = {
        "ledger_parsed": parsed,
        "selected_roles_by_source": selected_roles_by_source,
        "invalid_by_role": invalid_by_role,
        "rejected_sources": rejected_sources,
    }
    return json.dumps(compiled, ensure_ascii=False), meta


def call_chat(client: Any, args: argparse.Namespace, prompt: str) -> str:
    last_error: Exception | None = None
    for attempt in range(args.retries + 1):
        try:
            response = client.chat.completions.create(
                model=args.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as error:  # noqa: BLE001
            last_error = error
            status_code = getattr(error, "status_code", None) or getattr(error, "status", None)
            try:
                status_code = int(status_code) if status_code is not None else None
            except (TypeError, ValueError):
                status_code = None
            if status_code in {400, 401, 403, 404, 422} or attempt == args.retries:
                break
            time.sleep(min(2 * (2**attempt), 30))
    raise RuntimeError(f"chat completion failed after {args.retries + 1} attempts: {last_error}")


def filter_rows(rows: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    variants = set(args.variant)
    if variants:
        rows = [row for row in rows if row.get("source_perturbation_variant") in variants]
    if args.limit:
        rows = rows[: args.limit]
    return rows


def run(args: argparse.Namespace) -> None:
    from openai import OpenAI

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is not set")
    client = OpenAI(api_key=api_key, base_url=args.base_url)
    rows = filter_rows(read_jsonl(args.packet), args)
    completed = completed_requests(args.out, args.model)
    print(f"model={args.model}")
    print(f"packet={args.packet}")
    print(f"evaluations={len(rows)}")
    print(f"temperature={args.temperature}")
    print(f"max_tokens={args.max_tokens}")
    print(f"completed={len(completed)}")
    for index, row in enumerate(rows, start=1):
        request_id = row["hard_evaluation_id"]
        if request_id in completed:
            print(f"[{index}/{len(rows)}] skip {request_id}", flush=True)
            continue
        print(f"[{index}/{len(rows)}] source_ledger {request_id}", flush=True)
        out_row = {
            "hard_evaluation_id": request_id,
            "base_evaluation_id": row["base_evaluation_id"],
            "scenario_id": row["scenario_id"],
            "shuffle_seed": row["shuffle_seed"],
            "source_perturbation_variant": row.get("source_perturbation_variant"),
            "task": "source_ledger_router",
            "model": args.model,
            "provider": "openai-compatible",
        }
        try:
            prompt = build_source_ledger_prompt(row)
            ledger_response = call_chat(client, args, prompt)
            compiled_response, meta = compile_state_cards(row, ledger_response)
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
        completed.add(request_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a source-ledger router and compile PerspectiveGap hard cards.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--variant", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--include-prompts", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run(args)


if __name__ == "__main__":
    main()
