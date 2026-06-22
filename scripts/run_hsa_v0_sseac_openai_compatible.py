#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any


TASK_NAME = "hsa_v0_sseac_candidate_units"
INSUFFICIENT = "insufficient_evidence"


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


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


def compact_text(text: Any, max_chars: int) -> str:
    if not isinstance(text, str):
        return ""
    compact = " ".join(text.strip().split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max(0, max_chars - 3)].rstrip() + "..."


def completed_requests(path: Path, model: str) -> set[str]:
    completed: set[str] = set()
    if not path.exists():
        return completed
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("model") == model and row.get("task") == TASK_NAME and ("response" in row or "error" in row):
            completed.add(str(row.get("packet_id", "")))
    return completed


def card_prompt_view(card: dict[str, Any], max_content_chars: int) -> dict[str, Any]:
    return {
        "card_id": card.get("card_id"),
        "source_role": card.get("source_role"),
        "recipient_scope": card.get("recipient_scope", []),
        "verification_state": card.get("verification_state"),
        "evidence_type": card.get("evidence_type"),
        "cost": card.get("cost", 1),
        "content": compact_text(card.get("content", ""), max_content_chars),
    }


def build_hsa_prompt(row: dict[str, Any], max_content_chars: int, prompt_contract: str = "baseline") -> str:
    answer_options = [option for option in row.get("candidate_options", []) if option != INSUFFICIENT]
    prompt_packet = {
        "packet_id": row.get("packet_id"),
        "benchmark": row.get("benchmark"),
        "roles": row.get("roles", []),
        "final_decider": row.get("final_decider"),
        "role_budgets": row.get("role_budgets", {}),
        "answer_options": answer_options,
        "source_cards": [card_prompt_view(card, max_content_chars) for card in row.get("source_cards", []) if isinstance(card, dict)],
    }
    response_schema: dict[str, Any] = {
        "option_states": [
            {
                "option": "one answer option",
                "state": "enabled|blocked|insufficient",
                "supporting_slots": ["card ids or concise evidence labels"],
                "blocking_slots": ["card ids or concise blocker labels"],
                "missing_slots": ["missing evidence descriptions"],
            }
        ],
        "candidate_units": [
            {
                "unit_id": "short unique id",
                "recipient": "final_decider",
                "card_ids": ["card_id"],
                "priority": 10.0,
                "claimed_slots": ["optional evidence labels"],
                "claimed_effect": "how this card supports, blocks, or constrains an answer option",
            }
        ],
        "proposed_rejections": [
            {
                "card_id": "card_id",
                "reason": "why this source should not support final decision",
            }
        ],
        "final_decision": "one answer option or insufficient_evidence",
    }
    if prompt_contract in {"recall_sweep", "focused_recall", "constraint_recall"}:
        response_schema = {
            "answer_evidence_sweep": [
                {
                    "option": "one answer option",
                    "support_cards": ["card_id"],
                    "blocker_cards": ["card_id"],
                    "background_constraint_cards": ["card_id"],
                    "unavailable_or_invalid_cards": ["card_id"],
                    "readout": "enabled|blocked|insufficient",
                }
            ],
            **response_schema,
        }
    lines = [
        "You are the proposal stage of Hidden-State Admission v0 (HSA-v0), implemented through SSEAC-v0.",
        "A deterministic compiler will enforce recipient scope, verification state, duplicate removal, and role budgets after your answer.",
        "",
        "Your task:",
        "- Propose evidence admission units for the final_decider.",
        "- Each candidate unit targets exactly one recipient role, normally final_decider.",
        "- Use card_id values from SOURCE_CARDS only.",
        "- Rank candidate_units by priority, highest first.",
        "- Prefer facts that directly enable the selected answer or block tempting alternatives.",
        "- Treat unverified, rejected, or quarantined cards as unable to support a final decision.",
        "- Treat cards outside final_decider recipient_scope as unavailable to final_decider.",
        "- If admissible evidence is insufficient for a single answer, set final_decision to insufficient_evidence.",
        "- Return JSON only. No markdown fences, prose, or comments.",
        "",
    ]
    if prompt_contract in {"recall_sweep", "focused_recall", "constraint_recall"}:
        lines.extend(
            [
                "Recall sweep contract:",
                "- First scan every answer option, not just the answer that currently looks best.",
                "- For each option, record verified final_decider-visible support, blocker, and background constraint cards.",
                "- Background constraints are important when they affect feasibility or safety, even if they do not name one answer directly.",
                "- Blockers for losing options are important evidence for the final decision; do not reject them as irrelevant.",
                "- Emit one candidate_unit per card_id. Do not put multiple card_ids in one candidate_unit.",
                "- Emit candidate_units for selected-answer support and for blockers/background constraints that justify rejecting alternatives.",
                "- Use high priority for low-cost verified cards that affect feasibility, safety, availability, or route closure.",
                "",
            ]
        )
    if prompt_contract in {"focused_recall", "constraint_recall"}:
        lines.extend(
            [
                "Focused admission contract:",
                "- After the sweep, decide which option is best supported by admissible evidence.",
                "- Emit candidate_units only for: selected-option support cards, blockers for non-selected options, and necessary background constraints.",
                "- Do not emit ordinary support cards for options you are rejecting.",
                "- A blocker blocks only the option it specifically makes unavailable, unsafe, or infeasible.",
                "- Do not mark the selected option blocked just because another route, venue, or alternative has a problem.",
                "- If one option is supported and the other options are blocked, choose that option rather than insufficient_evidence.",
                "- Use insufficient_evidence only when no single answer can be justified from verified final_decider-visible cards.",
                "",
            ]
        )
    if prompt_contract == "constraint_recall":
        lines.extend(
            [
                "Constraint retention contract:",
                "- Keep verified final_decider-visible blocker or background-constraint cards when they affect feasibility, safety, routes, availability, or timing.",
                "- Keep such constraint cards even when they do not eliminate the selected answer by themselves.",
                "- Do not reject a verified blocker or background constraint merely because the selected answer remains viable.",
                "- Still exclude ordinary support cards for rejected options unless they are needed as background constraints.",
                "- Each candidate_unit must contain exactly one card_id.",
                "",
            ]
        )
    lines.extend(
        [
        "Important boundary:",
        "- You are not given the gold answer.",
        "- You are not given evaluator-required slots.",
        "- Do not invent card ids or roles.",
        "",
        "PACKET:",
        json.dumps(prompt_packet, ensure_ascii=False, indent=2),
        "",
        "Return one valid JSON object with this shape:",
        json.dumps(response_schema, ensure_ascii=False, indent=2),
        ]
    )
    return "\n".join(lines)


def filter_rows(rows: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    packet_ids = set(args.packet_id)
    if packet_ids:
        rows = [row for row in rows if row.get("packet_id") in packet_ids]
    if args.limit:
        rows = rows[: args.limit]
    return rows


def write_prompt_dry_run(rows: list[dict[str, Any]], args: argparse.Namespace) -> None:
    out_rows: list[dict[str, Any]] = []
    for row in rows:
        prompt = build_hsa_prompt(row, args.max_content_chars, args.prompt_contract)
        out_rows.append(
            {
                "packet_id": row.get("packet_id"),
                "benchmark": row.get("benchmark"),
                "prompt_contract": args.prompt_contract,
                "roles": row.get("roles"),
                "final_decider": row.get("final_decider"),
                "condition": row.get("hsa_meta", {}).get("condition"),
                "variant_id": row.get("hsa_meta", {}).get("variant_id"),
                "source_card_count": len(row.get("source_cards", [])),
                "prompt_chars": len(prompt),
                "prompt": prompt,
            }
        )
    write_jsonl(args.dry_run_prompts_out, out_rows)
    print(json.dumps({"rows": len(out_rows), "dry_run_prompts_out": str(args.dry_run_prompts_out)}, ensure_ascii=False, indent=2))


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
    print(f"prompt_contract={args.prompt_contract}")
    print(f"completed={len(completed)}")
    for index, row in enumerate(rows, start=1):
        request_id = str(row.get("packet_id"))
        if request_id in completed:
            print(f"[{index}/{len(rows)}] skip {request_id}", flush=True)
            continue
        print(f"[{index}/{len(rows)}] hsa_v0_sseac {request_id}", flush=True)
        out_row = {
            "packet_id": request_id,
            "task_id": row.get("task_id"),
            "benchmark": row.get("benchmark"),
            "task": TASK_NAME,
            "model": args.model,
            "provider": "openai-compatible",
        }
        try:
            prompt = build_hsa_prompt(row, args.max_content_chars, args.prompt_contract)
            response_text = call_chat(client, args, prompt)
            parsed, parse_error = parse_json_object_loose(response_text)
            out_row["hsa_prompt"] = prompt if args.include_prompts else None
            out_row["prompt_contract"] = args.prompt_contract
            out_row["response"] = parsed if not parse_error else response_text
            out_row["response_parse_error"] = parse_error
            out_row["status"] = "ok" if not parse_error else "parse_warning"
        except Exception as error:  # noqa: BLE001
            out_row["response"] = None
            out_row["status"] = "error"
            out_row["error"] = {"type": type(error).__name__, "message": str(error)}
        append_jsonl(args.out, out_row)
        completed.add(request_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run HSA-v0 SSEAC candidate-unit proposer on a HiddenBench-derived packet.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--base-url")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--model", default="hsa-v0-sseac-proposer")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--packet-id", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--max-content-chars", type=int, default=900)
    parser.add_argument("--prompt-contract", choices=["baseline", "recall_sweep", "focused_recall", "constraint_recall"], default="baseline")
    parser.add_argument("--include-prompts", action="store_true")
    parser.add_argument("--dry-run-prompts-out", type=Path)
    return parser


def main() -> None:
    run(build_parser().parse_args())


if __name__ == "__main__":
    main()
