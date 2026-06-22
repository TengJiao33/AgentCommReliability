#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any


TASK_NAME = "pg40_pairwise_role_card_selector"
PROMPT_VERSION = "pairwise_role_card_v0"
ROUTING_COMPLETE = "routing_complete"
INSUFFICIENT = "insufficient_evidence"

FORBIDDEN_PROMPT_TERMS = (
    "recipient_scope",
    "required_slots",
    "acceptable_card_ids",
    "expected_final_decision",
    "reference_need_sets",
    "candidate_need_sets",
    "role_utilities",
    "needed_by",
    "eligible_by",
    "target_needed_by",
    "utility_by_recipient",
    "visibility_gold",
    "source_scope_ledger",
    "oracle",
    "gold",
    "distractor",
)


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


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_str_list(value: Any) -> list[str]:
    return [item for item in as_list(value) if isinstance(item, str)]


def compact_text(text: Any, max_chars: int) -> str:
    if not isinstance(text, str):
        return ""
    compact = " ".join(text.strip().split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max(0, max_chars - 3)].rstrip() + "..."


def parse_json_object_loose(text: str | None) -> tuple[dict[str, Any], str | None]:
    if text is None:
        return {}, "empty_response"
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {}, "no_json_object"
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as error:
            return {}, f"json_decode_error:{error}"
    if not isinstance(parsed, dict):
        return {}, "response_not_object"
    return parsed, None


def card_cost(card: dict[str, Any]) -> int:
    try:
        return max(0, int(card.get("cost", 1)))
    except (TypeError, ValueError):
        return 1


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number < 0:
        return 0.0
    if number > 1:
        return 1.0
    return number


def card_prompt_view(card: dict[str, Any], max_content_chars: int) -> dict[str, Any]:
    return {
        "card_id": card.get("card_id"),
        "cost": card.get("cost", 1),
        "text": compact_text(card.get("content", ""), max_content_chars),
    }


def leak_flags(prompt: str) -> list[str]:
    lowered = prompt.lower()
    return [term for term in FORBIDDEN_PROMPT_TERMS if term.lower() in lowered]


def build_pairwise_prompt(row: dict[str, Any], max_content_chars: int) -> str:
    source_cards = [
        card_prompt_view(card, max_content_chars)
        for card in as_list(row.get("source_cards"))
        if isinstance(card, dict)
    ]
    prompt_packet = {
        "packet_id": row.get("packet_id"),
        "roles": as_str_list(row.get("roles")),
        "role_budgets": row.get("role_budgets", {}),
        "source_cards": source_cards,
    }
    response_schema = {
        "assignments": [
            {
                "role": "exact role name",
                "card_id": "f1",
                "confidence": 0.0,
                "reason": "short reason for this role-card pair",
            }
        ],
        "notes": "optional short note about uncertainty",
    }
    return "\n".join(
        [
            "You are selecting which source cards should be admitted for each role in a multi-agent task.",
            "Judge each role-card pair from the visible role name, role budget, card id, card cost, and card text.",
            "Return only pairs that should be assigned to that role.",
            "A card can be assigned to multiple roles when its text is useful for each of them.",
            "Do not assign generic prompting advice unless that role genuinely needs it to perform the task.",
            "Prefer role-specific task instructions over broad background when the role budget is tight.",
            "Use exact role names and card_id values from the packet.",
            "Keep reasons short. Return JSON only: no markdown fences, prose, or comments.",
            "",
            "PACKET:",
            json.dumps(prompt_packet, ensure_ascii=False, indent=2),
            "",
            "Return one valid JSON object with this shape:",
            json.dumps(response_schema, ensure_ascii=False, indent=2),
        ]
    )


def filter_rows(rows: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    packet_ids = set(args.packet_id)
    if packet_ids:
        rows = [row for row in rows if row.get("packet_id") in packet_ids]
    if args.limit:
        rows = rows[: args.limit]
    return rows


def completed_requests(path: Path, model: str) -> set[str]:
    completed: set[str] = set()
    if not path.exists():
        return completed
    for row in read_jsonl(path):
        if row.get("model") == model and row.get("task") == TASK_NAME and ("response" in row or "error" in row):
            completed.add(str(row.get("packet_id", "")))
    return completed


def build_sseac_response(
    packet: dict[str, Any],
    pairwise_response: dict[str, Any],
    *,
    confidence_threshold: float,
    cost_penalty: float,
    prune_to_budget: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    roles = set(as_str_list(packet.get("roles")))
    budgets = packet.get("role_budgets", {}) if isinstance(packet.get("role_budgets"), dict) else {}
    cards = {
        str(card.get("card_id")): card
        for card in as_list(packet.get("source_cards"))
        if isinstance(card, dict) and isinstance(card.get("card_id"), str)
    }
    raw_assignments = [item for item in as_list(pairwise_response.get("assignments")) if isinstance(item, dict)]
    candidates: list[dict[str, Any]] = []
    invalid_assignments: list[dict[str, Any]] = []
    for index, item in enumerate(raw_assignments):
        role = str(item.get("role", ""))
        card_id = str(item.get("card_id", ""))
        confidence = safe_float(item.get("confidence"), 0.0)
        if role not in roles or card_id not in cards:
            invalid_assignments.append({"index": index, "role": role, "card_id": card_id, "reason": "unknown_role_or_card"})
            continue
        if confidence < confidence_threshold:
            invalid_assignments.append(
                {
                    "index": index,
                    "role": role,
                    "card_id": card_id,
                    "confidence": confidence,
                    "reason": "below_threshold",
                }
            )
            continue
        card = cards[card_id]
        priority = (confidence * 100.0) - (card_cost(card) * cost_penalty)
        candidates.append(
            {
                "unit_id": f"pairwise::{role}::{card_id}",
                "recipient": role,
                "card_ids": [card_id],
                "priority": priority,
                "claimed_slots": [f"{role}::{card_id}"],
                "claimed_effect": "pairwise_role_card_assignment",
                "pairwise_debug": {
                    "confidence": confidence,
                    "reason": item.get("reason"),
                    "cost": card_cost(card),
                },
            }
        )

    candidates.sort(
        key=lambda unit: (
            -float(unit.get("priority", 0.0)),
            str(unit.get("recipient", "")),
            str(unit.get("unit_id", "")),
        )
    )
    selected: list[dict[str, Any]] = []
    pruned_for_budget = 0
    if prune_to_budget:
        spent = {role: 0 for role in roles}
        seen = {role: set() for role in roles}
        for unit in candidates:
            role = str(unit.get("recipient", ""))
            cost = 0
            for card_id in as_str_list(unit.get("card_ids")):
                if card_id not in seen[role]:
                    cost += card_cost(cards[card_id])
            budget = int(budgets.get(role, 0))
            if spent[role] + cost > budget:
                pruned_for_budget += 1
                continue
            for card_id in as_str_list(unit.get("card_ids")):
                if card_id not in seen[role]:
                    seen[role].add(card_id)
                    spent[role] += card_cost(cards[card_id])
            selected.append(unit)
    else:
        selected = candidates

    response = {
        "option_states": [
            {
                "option": ROUTING_COMPLETE,
                "state": "enabled" if selected else "insufficient",
                "supporting_slots": [
                    slot
                    for unit in selected
                    for slot in as_str_list(unit.get("claimed_slots"))
                ],
                "blocking_slots": [],
                "missing_slots": [],
            }
        ],
        "candidate_units": selected,
        "proposed_rejections": [],
        "final_decision": ROUTING_COMPLETE if selected else INSUFFICIENT,
        "selector_strategy": {
            "name": "pairwise_role_card_selector",
            "prompt_version": PROMPT_VERSION,
            "confidence_threshold": confidence_threshold,
            "cost_penalty": cost_penalty,
            "prune_to_budget": prune_to_budget,
            "visible_fields_used": [
                "packet_id",
                "roles",
                "role_budgets",
                "source_cards.card_id",
                "source_cards.content",
                "source_cards.cost",
            ],
            "forbidden_fields_not_used": list(FORBIDDEN_PROMPT_TERMS),
        },
    }
    diagnostics = {
        "raw_assignments": len(raw_assignments),
        "candidate_units_before_budget": len(candidates),
        "candidate_units": len(selected),
        "invalid_assignments": len(invalid_assignments),
        "pruned_for_budget": pruned_for_budget,
    }
    if invalid_assignments:
        diagnostics["invalid_assignment_samples"] = invalid_assignments[:10]
    return response, diagnostics


def write_prompt_dry_run(rows: list[dict[str, Any]], args: argparse.Namespace) -> None:
    out_rows: list[dict[str, Any]] = []
    for row in rows:
        prompt = build_pairwise_prompt(row, args.max_content_chars)
        out_rows.append(
            {
                "packet_id": row.get("packet_id"),
                "prompt_version": PROMPT_VERSION,
                "roles": row.get("roles"),
                "role_budgets": row.get("role_budgets"),
                "source_card_count": len(row.get("source_cards", [])),
                "prompt_chars": len(prompt),
                "leak_flags": leak_flags(prompt),
                "prompt": prompt,
            }
        )
    write_jsonl(args.dry_run_prompts_out, out_rows)
    prompt_chars = [int(row["prompt_chars"]) for row in out_rows]
    summary = {
        "rows": len(out_rows),
        "leak_flagged_rows": sum(1 for row in out_rows if row["leak_flags"]),
        "max_prompt_chars": max(prompt_chars) if prompt_chars else 0,
        "min_prompt_chars": min(prompt_chars) if prompt_chars else 0,
        "avg_prompt_chars": (sum(prompt_chars) / len(prompt_chars)) if prompt_chars else 0.0,
        "dry_run_prompts_out": str(args.dry_run_prompts_out),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


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
            time.sleep(min(4 * (2**attempt), 60))
    raise RuntimeError(f"chat completion failed after {args.retries + 1} attempts: {last_error}")


def run(args: argparse.Namespace) -> None:
    rows = filter_rows(read_jsonl(args.packet), args)
    if args.dry_run_prompts_out:
        write_prompt_dry_run(rows, args)
        return
    if not args.base_url or not args.out:
        raise SystemExit("provide --base-url and --out unless using --dry-run-prompts-out")

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
    print(f"prompt_version={PROMPT_VERSION}")
    print(f"completed={len(completed)}")
    for index, row in enumerate(rows, start=1):
        request_id = str(row.get("packet_id"))
        if request_id in completed:
            print(f"[{index}/{len(rows)}] skip {request_id}", flush=True)
            continue
        print(f"[{index}/{len(rows)}] pairwise {request_id}", flush=True)
        out_row: dict[str, Any] = {
            "packet_id": request_id,
            "task_id": row.get("task_id"),
            "benchmark": row.get("benchmark"),
            "task": TASK_NAME,
            "prompt_version": PROMPT_VERSION,
            "model": args.model,
            "provider": "openai-compatible",
        }
        try:
            prompt = build_pairwise_prompt(row, args.max_content_chars)
            prompt_leaks = leak_flags(prompt)
            response_text = call_chat(client, args, prompt)
            parsed, parse_error = parse_json_object_loose(response_text)
            out_row["prompt_leak_flags"] = prompt_leaks
            out_row["pairwise_parse_error"] = parse_error
            if parse_error:
                out_row["response"] = response_text
                out_row["status"] = "parse_warning"
            else:
                response, diagnostics = build_sseac_response(
                    row,
                    parsed,
                    confidence_threshold=args.confidence_threshold,
                    cost_penalty=args.cost_penalty,
                    prune_to_budget=not args.no_prune_to_budget,
                )
                out_row["response"] = response
                out_row["raw_pairwise_response"] = parsed
                out_row["selector_diagnostics"] = diagnostics
                out_row["status"] = "ok"
            if args.include_prompts:
                out_row["prompt"] = prompt
        except Exception as error:  # noqa: BLE001
            out_row["response"] = None
            out_row["status"] = "error"
            out_row["error"] = {"type": type(error).__name__, "message": str(error)}
        append_jsonl(args.out, out_row)
        completed.add(request_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a PG40 no-scope pairwise role-card selector.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--base-url")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--model", default="pg40-pairwise-role-card-selector")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--packet-id", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=3072)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--max-content-chars", type=int, default=700)
    parser.add_argument("--confidence-threshold", type=float, default=0.50)
    parser.add_argument("--cost-penalty", type=float, default=1.0)
    parser.add_argument("--no-prune-to-budget", action="store_true")
    parser.add_argument("--include-prompts", action="store_true")
    parser.add_argument("--dry-run-prompts-out", type=Path)
    return parser


def main() -> None:
    run(build_parser().parse_args())


if __name__ == "__main__":
    main()
