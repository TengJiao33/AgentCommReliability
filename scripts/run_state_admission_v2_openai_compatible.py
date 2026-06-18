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
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()


def parse_json_object_loose(text: str | None) -> dict[str, Any]:
    if not text:
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
        raise ValueError("response is not an object")
    return parsed


def compact(text: str, max_chars: int = 1000) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= max_chars else text[:max_chars] + " ..."


def admitted_fact_ids_for_final_decider(row: dict[str, Any]) -> list[str]:
    facts = {fact["fact_id"]: fact for fact in row.get("source_facts", [])}
    fact_ids: list[str] = []
    for unit in row.get("expected_units", []):
        admit_to = set(unit.get("admit_to", []))
        not_admit_to = set(unit.get("not_admit_to", []))
        if "final_decider" not in admit_to or "final_decider" in not_admit_to:
            continue
        for fact_id in unit.get("required_fact_ids", []) + unit.get("supporting_fact_ids", []):
            fact = facts.get(fact_id)
            if not fact or fact.get("verification_status") != "verified":
                continue
            if "final_decider" not in set(fact.get("eligible_recipients", [])):
                continue
            if fact_id not in fact_ids:
                fact_ids.append(fact_id)
    return fact_ids


def build_direct_answer_prompt(row: dict[str, Any], prompt_style: str) -> str:
    if prompt_style == "direct_answer_all_facts":
        facts = row.get("source_facts", [])
        control_rule = "Treat every listed fact as available evidence for solving the original decision task."
    elif prompt_style == "direct_answer_admissible_facts":
        allowed = set(admitted_fact_ids_for_final_decider(row))
        facts = [fact for fact in row.get("source_facts", []) if fact.get("fact_id") in allowed]
        control_rule = (
            "Only the listed facts are available to the final_decider. If they do not directly support one answer, "
            "return insufficient_admissible_evidence with answer null."
        )
    else:
        raise ValueError(f"unknown direct-answer prompt style: {prompt_style}")
    lines = [
        "You are the final decider for a direct-answer control.",
        "This control does not ask you to construct admission units.",
        control_rule,
        "Output JSON only.",
        "",
        f"Packet id: {row['packet_id']}",
        f"Variant: {row['variant_id']}",
        f"Prompt style: {prompt_style}",
        f"Possible answers: {json.dumps(row['possible_answers'], ensure_ascii=False)}",
        "",
        "Task description:",
        compact(row["task_description"], 1400),
        "",
        "Available facts:",
    ]
    for fact in facts:
        lines.append(json.dumps({"fact_id": fact["fact_id"], "text": fact["text"]}, ensure_ascii=False))
    schema = {
        "final_decider_state": {
            "status": "decidable_from_available_facts|insufficient_admissible_evidence",
            "answer": "answer option or null",
            "rationale_fact_ids": ["fact_id"],
            "rationale": "short reason",
        }
    }
    lines.extend(["", "Return exactly one JSON object with this shape:", json.dumps(schema, ensure_ascii=False, indent=2)])
    return "\n".join(lines)


def build_prompt(row: dict[str, Any], prompt_style: str = "unit_first") -> str:
    if prompt_style.startswith("direct_answer_"):
        return build_direct_answer_prompt(row, prompt_style)
    lines = [
        "You are a state-admission router for a multi-agent decision workflow.",
        "Your job is to decide which source-scoped facts may enter each role's local state, and to propose admission units.",
        "",
        "Rules:",
        "- Use only facts with verification_status=verified for admitted units.",
        "- Do not admit quarantined or unverified facts; reject them with a reason.",
        "- A fact may be admitted only to roles listed in eligible_recipients.",
        "- Do not turn tempting context into a recommendation unless admissible blocker/enabler facts support it.",
        "- If a complete blocker/enabler cannot be assembled from admissible facts, mark the downstream state as insufficient_admissible_evidence.",
        "- Output JSON only.",
        "",
        f"Packet id: {row['packet_id']}",
        f"Variant: {row['variant_id']}",
        f"Prompt style: {prompt_style}",
        f"Roles: {json.dumps(row['roles'], ensure_ascii=False)}",
        f"Possible answers: {json.dumps(row['possible_answers'], ensure_ascii=False)}",
        "",
        "Task description:",
        compact(row["task_description"], 1400),
        "",
        "Source facts:",
    ]
    for fact in row["source_facts"]:
        lines.append(
            json.dumps(
                {
                    "fact_id": fact["fact_id"],
                    "text": fact["text"],
                    "verification_status": fact["verification_status"],
                    "source_kind": fact["source_kind"],
                    "eligible_recipients": fact["eligible_recipients"],
                },
                ensure_ascii=False,
            )
        )
    if prompt_style == "option_state_first":
        lines.extend(
            [
                "",
                "Decision procedure:",
                "1. For each possible answer, classify its option_state before writing admission units.",
                "2. Use blocked when admissible facts rule the option out.",
                "3. Use enabled when admissible facts positively keep the option viable.",
                "4. Use insufficient when a required blocker or enabler is missing, quarantined, unverified, or not visible to the final_decider.",
                "5. Only after option_state is complete, write admission_units that justify those option states.",
                "6. The final answer must follow from option_state, not from tempting shared context.",
            ]
        )
    schema = {
        "option_states": [
            {
                "option": "one possible answer",
                "state": "blocked|enabled|insufficient",
                "fact_ids": ["fact_id"],
                "rationale": "short reason",
            }
        ],
        "admitted_facts": [
            {
                "fact_id": "fact_id",
                "admit_to": ["role"],
            }
        ],
        "admission_units": [
            {
                "unit_type": "option_blocker|option_enabler|context|insufficient",
                "target_option": "answer option or null",
                "fact_ids": ["fact_id"],
                "admit_to": ["role"],
                "rationale": "short reason",
            }
        ],
        "rejections": [
            {
                "fact_ids": ["fact_id"],
                "reason": "verification_reject|recipient_scope_reject|dependency_scope_incomplete|recommendation_leakage_reject|off_option_reject_or_inert",
                "rationale": "short reason",
            }
        ],
        "final_decider_state": {
            "status": "decidable_from_admitted_facts|insufficient_admissible_evidence",
            "answer": "answer option or null",
            "supporting_units": ["short labels"],
        },
    }
    lines.extend(["", "Return exactly one JSON object with this shape:", json.dumps(schema, ensure_ascii=False, indent=2)])
    return "\n".join(lines)


def completed_requests(path: Path, model: str) -> set[str]:
    if not path.exists():
        return set()
    out = set()
    for row in read_jsonl(path):
        if row.get("model") == model and row.get("packet_id") and ("response" in row or "error" in row):
            out.add(row["packet_id"])
    return out


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
    rows = read_jsonl(args.packet)
    if args.limit:
        rows = rows[: args.limit]
    if args.dry_run_prompts_out:
        args.dry_run_prompts_out.parent.mkdir(parents=True, exist_ok=True)
        with args.dry_run_prompts_out.open("w", encoding="utf-8") as handle:
            for row in rows:
                prompt = build_prompt(row, args.prompt_style)
                handle.write(
                    json.dumps(
                        {
                            "packet_id": row["packet_id"],
                            "prompt_style": args.prompt_style,
                            "prompt_chars": len(prompt),
                            "prompt": prompt,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        print(json.dumps({"rows": len(rows), "dry_run_prompts_out": str(args.dry_run_prompts_out)}, ensure_ascii=False, indent=2))
        return

    from openai import OpenAI

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is not set")
    client = OpenAI(api_key=api_key, base_url=args.base_url)
    completed = completed_requests(args.out, args.model)
    print(f"model={args.model} packet={args.packet} rows={len(rows)} completed={len(completed)}", flush=True)
    for index, row in enumerate(rows, start=1):
        packet_id = row["packet_id"]
        if packet_id in completed:
            print(f"[{index}/{len(rows)}] skip {packet_id}", flush=True)
            continue
        print(f"[{index}/{len(rows)}] state_admission_v2 {packet_id}", flush=True)
        out = {
            "packet_id": packet_id,
            "sketch_id": row["sketch_id"],
            "variant_id": row["variant_id"],
            "task": "state_admission_v2_smoke",
            "model": args.model,
            "provider": "openai-compatible",
            "prompt_style": args.prompt_style,
        }
        try:
            prompt = build_prompt(row, args.prompt_style)
            raw = call_chat(client, args, prompt)
            parsed = parse_json_object_loose(raw)
            out["prompt"] = prompt if args.include_prompts else None
            out["raw_response"] = raw
            out["response"] = json.dumps(parsed, ensure_ascii=False)
            out["status"] = "ok"
        except Exception as error:  # noqa: BLE001
            out["status"] = "error"
            out["error"] = {"type": type(error).__name__, "message": str(error)}
        append_jsonl(args.out, out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--base-url")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--model", default="state-admission-v2-smoke")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument(
        "--prompt-style",
        choices=["unit_first", "option_state_first", "direct_answer_all_facts", "direct_answer_admissible_facts"],
        default="unit_first",
    )
    parser.add_argument("--include-prompts", action="store_true")
    parser.add_argument("--dry-run-prompts-out", type=Path)
    args = parser.parse_args()
    if not args.dry_run_prompts_out and (not args.base_url or not args.out):
        raise SystemExit("provide --base-url and --out unless using --dry-run-prompts-out")
    run(args)


if __name__ == "__main__":
    main()
