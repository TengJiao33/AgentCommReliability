#!/usr/bin/env python3
"""Audit MOC merge prompts on role-sensitive synthetic cases.

This script calls an OpenAI-compatible chat-completions endpoint with the five
merge prompts used by MOC's `merge_multiple_messages`. It does not run the MOC
graph or evaluate a benchmark. The output is a role-slot preservation audit for
the merge prompt itself.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


SCHEMA_VERSION = "acr.comm_trace.v1.1"
METHOD_FAMILY = "MOCMergePromptRoleAudit"

AUDIT_SLOTS = [
    "answer_type",
    "clue_object",
    "bridge_entity",
    "requested_relation",
    "required_qualifier",
    "forbidden_replacement",
    "gold_answer",
]

MERGE_SURFACES = ["labeled_role_messages", "natural_evidence_messages"]

STOPWORDS = {
    "a",
    "about",
    "after",
    "all",
    "an",
    "and",
    "answer",
    "are",
    "as",
    "at",
    "be",
    "both",
    "by",
    "case",
    "city",
    "does",
    "for",
    "from",
    "had",
    "has",
    "in",
    "is",
    "it",
    "its",
    "known",
    "made",
    "must",
    "not",
    "object",
    "of",
    "or",
    "played",
    "recorded",
    "relation",
    "required",
    "should",
    "slot",
    "the",
    "this",
    "to",
    "type",
    "what",
    "where",
    "which",
    "whose",
    "with",
}


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def estimate_tokens(parts: Iterable[str]) -> int:
    total = 0
    for part in parts:
        text = str(part).replace("->", " -> ").replace(";", " ; ")
        total += max(1, len(text.split()))
    return total


def normalize(text: Any) -> str:
    return " ".join(str(text).lower().replace("/", " ").replace("-", " ").split())


def significant_terms(text: Any) -> List[str]:
    terms = []
    for token in re.findall(r"[a-zA-Z0-9]+", str(text).lower()):
        if len(token) <= 1 or token in STOPWORDS:
            continue
        terms.append(token)
    return terms


def term_score(output: str, expected: Any) -> Tuple[bool, List[str], List[str]]:
    terms = significant_terms(expected)
    if not terms:
        return True, [], []
    norm_output = normalize(output)
    found = [term for term in terms if term in norm_output]
    missing = [term for term in terms if term not in norm_output]
    threshold = 1 if len(terms) <= 2 else max(2, (len(terms) + 1) // 2)
    return len(found) >= threshold, found, missing


def build_messages(case: Dict[str, Any], surface: str) -> Tuple[str, str, str, str]:
    facts = case["facts"]
    fact_text = " ".join(fact["text"] for fact in facts)
    if surface == "labeled_role_messages":
        role_i = "TargetRoleMapper"
        content_i = (
            f"Question target roles:\n"
            f"- answer_type: {case['answer_type']}\n"
            f"- clue_object: {case['clue_object']}\n"
            f"- requested_relation: {case['requested_relation']}\n"
            f"- required_qualifier: {case['required_qualifier']}\n"
        )
        role_j = "EvidenceBridge"
        content_j = (
            f"Evidence bridge and guardrails:\n"
            f"- bridge_entity: {case['bridge_entity']}\n"
            f"- gold_answer: {case['gold_answer']}\n"
            f"- forbidden_replacement: {case['forbidden_replacement']}\n"
            f"- source_facts: {fact_text}\n"
        )
        return role_i, content_i, role_j, content_j

    if surface == "natural_evidence_messages":
        role_i = "QuestionReader"
        content_i = (
            f"The question starts from {case['clue_object']} and asks for "
            f"{case['requested_relation']}. The answer should be a "
            f"{case['answer_type']}. Keep this qualifier: {case['required_qualifier']}."
        )
        role_j = "EvidenceReader"
        content_j = (
            f"The evidence connects {case['clue_object']} to {case['bridge_entity']}. "
            f"The answer is {case['gold_answer']}. Do not replace it with "
            f"{case['forbidden_replacement']}. Source facts: {fact_text}"
        )
        return role_i, content_i, role_j, content_j

    raise ValueError(f"Unknown merge surface: {surface}")


def moc_merge_prompts(
    *,
    id_i: str,
    role_i: str,
    content_i: str,
    id_j: str,
    role_j: str,
    content_j: str,
    kppa: int,
) -> List[Dict[str, str]]:
    messages_set = f"""AGENT_1: [ID: {id_i} | Role: {role_i}]
{content_i}

AGENT_2: [ID: {id_j} | Role: {role_j}]
{content_j}"""
    prompts = [
        (
            "narrative_synthesis",
            f"""Synthesize the messages from AGENT_1 and AGENT_2 into a single, cohesive update.
Target length: approximately {kppa}% of the original token count.
Task: Merge overlapping information and deduplicate common findings while preserving both agents' distinct contributions.
Constraint: Do not add new information. Output ONLY the synthesized text with no preamble.

{messages_set}""",
        ),
        (
            "logical_integrity",
            f"""Merge the communications from AGENT_1 and AGENT_2.
Target length: roughly {kppa}% of the original volume.
Task: Compress the text but strictly retain the complete reasoning chain and all logical dependencies leading to the conclusion.
Constraint: Do not add new information. Output ONLY the synthesized text with no preamble.

{messages_set}""",
        ),
        (
            "technical_precision",
            f"""Consolidate the data from AGENT_1 and AGENT_2 into a high-density summary.
Target length: around {kppa}% of original tokens.
Task: Ensure zero-loss for all Agent IDs, technical parameters, formulas, and specific values. Strip away all conversational fillers.
Constraint: Do not add new information. Output ONLY the synthesized text with no preamble.

{messages_set}""",
        ),
        (
            "actionable_intelligence",
            f"""Combine AGENT_1 and AGENT_2 messages into a "telegram-style" actionable update.
Target length: approximately {kppa}% volume.
Task: Prioritize actionable data and final decisions. Use shorthand where possible while maintaining source attribution for key facts.
Constraint: Do not add new information. Output ONLY the synthesized text with no preamble.

{messages_set}""",
        ),
        (
            "dedup_structure",
            f"""Integrate the content from AGENT_1 and AGENT_2 while maintaining any structural headers.
Target length: about {kppa}% of the original count.
Task: Identify and merge redundant statements between the two agents to maximize information density per token.
Constraint: Do not add new information. Output ONLY the synthesized text with no preamble.

{messages_set}""",
        ),
    ]
    return [
        {"strategy_index": str(index), "strategy_name": name, "prompt": prompt}
        for index, (name, prompt) in enumerate(prompts, start=1)
    ]


def chat_completion(
    *,
    base_url: str,
    model: str,
    api_key: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> Tuple[str, Dict[str, Any]]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {detail}") from exc
    data = json.loads(raw)
    content = data["choices"][0]["message"]["content"]
    return content, data.get("usage") or {}


def audit_output(case: Dict[str, Any], output: str) -> Dict[str, Any]:
    expected = {
        "answer_type": case["answer_type"],
        "clue_object": case["clue_object"],
        "bridge_entity": case["bridge_entity"],
        "requested_relation": case["requested_relation"],
        "required_qualifier": case["required_qualifier"],
        "forbidden_replacement": case["forbidden_replacement"],
        "gold_answer": case["gold_answer"],
    }
    slot_details = {}
    preserved = []
    lost = []
    for slot, value in expected.items():
        ok, found, missing = term_score(output, value)
        slot_details[slot] = {
            "expected": value,
            "preserved": ok,
            "found_terms": found,
            "missing_terms": missing,
        }
        if ok:
            preserved.append(slot)
        else:
            lost.append(slot)
    source_attribution = bool(re.search(r"agent[_\s-]*1", output, re.I)) and bool(
        re.search(r"agent[_\s-]*2", output, re.I)
    )
    return {
        "slot_details": slot_details,
        "role_slots_preserved": preserved,
        "role_slots_lost": lost,
        "all_required_slots_preserved": len(lost) == 0,
        "preserved_slot_count": len(preserved),
        "lost_slot_count": len(lost),
        "source_attribution_preserved": source_attribution,
    }


def build_trace_record(
    *,
    run_id: str,
    case: Dict[str, Any],
    surface: str,
    strategy: Dict[str, str],
    output: str,
    usage: Dict[str, Any],
    audit: Dict[str, Any],
    model: str,
    prompt_tokens_estimate: int,
) -> Dict[str, Any]:
    completion_tokens_estimate = estimate_tokens([output])
    prompt_tokens = usage.get("prompt_tokens") or prompt_tokens_estimate
    completion_tokens = usage.get("completion_tokens") or completion_tokens_estimate
    total_tokens = usage.get("total_tokens") or (prompt_tokens + completion_tokens)
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "method_family": METHOD_FAMILY,
        "method": f"{surface}_strategy_{strategy['strategy_index']}",
        "instance_id": case["instance_id"],
        "sample_index": case["sample_index"],
        "question": case["question"],
        "gold_answer": case["gold_answer"],
        "task_regime": "split_evidence_role_probe",
        "public_state": {
            "surface": "llm_merged_summary",
            "communication_policy": "moc_merge_prompt_only",
        },
        "final": {
            "answer": f"preserved {audit['preserved_slot_count']}/{len(AUDIT_SLOTS)} role slots",
            "correct": audit["all_required_slots_preserved"],
        },
        "transition": {
            "from_stage": "source_role_messages",
            "to_stage": f"merge_strategy_{strategy['strategy_index']}",
            "type": "unknown",
            "before_answer": None,
            "before_correct": None,
            "after_answer": None,
            "after_correct": audit["all_required_slots_preserved"],
        },
        "rounds": [],
        "retention_events": [],
        "communication_events": [
            {
                "stage": "merge_prompt_audit",
                "mechanism": "moc_merge_prompt",
                "scope": "message_pair",
                "model": model,
                "merge_surface": surface,
                "strategy_index": int(strategy["strategy_index"]),
                "strategy_name": strategy["strategy_name"],
                "initial_message_count": 2,
                "final_message_count": 1,
                "neighbor_hops": 2,
                "role_slots_preserved": audit["role_slots_preserved"],
                "role_slots_lost": audit["role_slots_lost"],
                "role_loss_detected": bool(audit["role_slots_lost"]),
                "source_attribution_preserved": audit["source_attribution_preserved"],
                "merged_text": output,
            }
        ],
        "context_events": [
            {
                "stage": "recipient_context",
                "agent_id": "MOCMergeRecipient",
                "context_surface": "llm_merged_summary",
                "role_slots_visible": audit["role_slots_preserved"],
                "role_slots_missing": audit["role_slots_lost"],
                "context_text": output,
            }
        ],
        "token_cost": {
            "scope": "merge_prompt",
            "input_tokens": int(prompt_tokens),
            "output_tokens": int(completion_tokens),
            "total_tokens": int(total_tokens),
            "compressed_prompt_tokens": int(prompt_tokens),
            "compressed_completion_tokens": int(completion_tokens),
            "compressed_total_tokens": int(total_tokens),
        },
        "method_comparison": None,
        "role_audit": audit,
        "role_probe": {
            "answer_type": case["answer_type"],
            "clue_object": case["clue_object"],
            "bridge_entity": case["bridge_entity"],
            "requested_relation": case["requested_relation"],
            "required_qualifier": case["required_qualifier"],
            "forbidden_replacement": case["forbidden_replacement"],
            "failure_family": case["failure_family"],
        },
        "source": {
            "generator": "scripts/run_moc_merge_prompt_role_audit.py",
            "case_source": "experiments/20260614-1832-local-moc-role-sensitive-split-evidence-probe/cases.jsonl",
        },
    }


def summarize(records: Sequence[Dict[str, Any]], run_id: str, model: str) -> Dict[str, Any]:
    groups: Dict[Tuple[str, int], List[Dict[str, Any]]] = defaultdict(list)
    surface_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        event = record["communication_events"][0]
        surface = event["merge_surface"]
        strategy = int(event["strategy_index"])
        groups[(surface, strategy)].append(record)
        surface_groups[surface].append(record)

    rows = []
    for (surface, strategy), group in sorted(groups.items()):
        slot_loss = Counter(
            slot for record in group for slot in record["communication_events"][0]["role_slots_lost"]
        )
        all_preserved = sum(1 for record in group if record["role_audit"]["all_required_slots_preserved"])
        rows.append(
            {
                "merge_surface": surface,
                "strategy_index": strategy,
                "strategy_name": group[0]["communication_events"][0]["strategy_name"],
                "records": len(group),
                "all_required_slots_preserved": all_preserved,
                "all_required_slot_rate": all_preserved / len(group) if group else None,
                "avg_preserved_slot_count": sum(
                    record["role_audit"]["preserved_slot_count"] for record in group
                )
                / len(group)
                if group
                else None,
                "slot_loss_counts": dict(sorted(slot_loss.items())),
                "source_attribution_preserved": sum(
                    1 for record in group if record["role_audit"]["source_attribution_preserved"]
                ),
            }
        )

    surface_rows = []
    for surface, group in sorted(surface_groups.items()):
        slot_loss = Counter(
            slot for record in group for slot in record["communication_events"][0]["role_slots_lost"]
        )
        all_preserved = sum(1 for record in group if record["role_audit"]["all_required_slots_preserved"])
        surface_rows.append(
            {
                "merge_surface": surface,
                "records": len(group),
                "all_required_slots_preserved": all_preserved,
                "all_required_slot_rate": all_preserved / len(group) if group else None,
                "avg_preserved_slot_count": sum(
                    record["role_audit"]["preserved_slot_count"] for record in group
                )
                / len(group)
                if group
                else None,
                "slot_loss_counts": dict(sorted(slot_loss.items())),
            }
        )

    return {
        "run_id": run_id,
        "schema_version": SCHEMA_VERSION,
        "method_family": METHOD_FAMILY,
        "model": model,
        "records": len(records),
        "cases": len({record["instance_id"] for record in records}),
        "merge_surfaces": MERGE_SURFACES,
        "strategies": rows,
        "surface_rows": surface_rows,
        "caveats": [
            "Merge-prompt-only audit; the MOC graph, ISM pair selection, and embedding-based strategy selection were not run.",
            "Synthetic cases from the local role-loss probe; this is not benchmark evidence.",
            "Slot preservation uses deterministic lexical checks and should be read as an audit signal, not semantic truth.",
        ],
    }


def write_readme(out_dir: Path, summary: Dict[str, Any], command: str, started_at: str, ended_at: str) -> None:
    surface_rows = "\n".join(
        "| {merge_surface} | {records} | {all_required_slots_preserved} | {all_required_slot_rate:.2f} | {avg_preserved_slot_count:.2f} | {slot_loss_counts} |".format(
            **row
        )
        for row in summary["surface_rows"]
    )
    strategy_rows = "\n".join(
        "| {merge_surface} | {strategy_index} | {strategy_name} | {all_required_slots_preserved}/{records} | {avg_preserved_slot_count:.2f} | {source_attribution_preserved}/{records} |".format(
            **row
        )
        for row in summary["strategies"]
    )
    readme = f"""# {summary['run_id']}

## What We Tried

Ran the five MOC merge prompts against the six synthetic split-evidence role
cases from the previous MOC role-loss probe. This only audits the merge prompt;
it does not run the MOC graph.

## Scope

- Method family: `{METHOD_FAMILY}`
- Model: `{summary['model']}`
- Cases: `{summary['cases']}`
- Records: `{summary['records']}`
- Surfaces: `{', '.join(summary['merge_surfaces'])}`

## Command

```bash
{command}
```

## Outputs

- `comm_trace_moc_merge_prompt_role_audit_v11.jsonl`
- `merge_outputs.jsonl`
- `summary.json`
- `manifest.json`

## Surface Summary

| Merge Surface | Records | All Slots Preserved | Rate | Avg Preserved Slots | Slot Loss Counts |
| --- | ---: | ---: | ---: | ---: | --- |
{surface_rows}

## Strategy Summary

| Merge Surface | Strategy | Name | All Slots Preserved | Avg Preserved Slots | Source Attribution |
| --- | ---: | --- | ---: | ---: | ---: |
{strategy_rows}

## Caveats

- This is a merge-prompt audit, not a MOC run.
- The audit uses lexical slot checks over synthetic cases.
- No claim is made about benchmark accuracy or the full MOC summarizer path.

## Timeline

- `{started_at}`: launched
- `{ended_at}`: completed
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")


def run(args: argparse.Namespace) -> Dict[str, Any]:
    started_at = datetime.now().isoformat(timespec="seconds")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = read_jsonl(Path(args.cases_jsonl))

    records = []
    output_rows = []
    for case in cases:
        for surface in args.surfaces:
            role_i, content_i, role_j, content_j = build_messages(case, surface)
            prompts = moc_merge_prompts(
                id_i="Agent1",
                role_i=role_i,
                content_i=content_i,
                id_j="Agent2",
                role_j=role_j,
                content_j=content_j,
                kppa=args.kppa,
            )
            for strategy in prompts:
                prompt = strategy["prompt"]
                output, usage = chat_completion(
                    base_url=args.base_url,
                    model=args.model,
                    api_key=args.api_key,
                    prompt=prompt,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                    timeout=args.request_timeout,
                )
                audit = audit_output(case, output)
                record = build_trace_record(
                    run_id=args.run_id,
                    case=case,
                    surface=surface,
                    strategy=strategy,
                    output=output,
                    usage=usage,
                    audit=audit,
                    model=args.model,
                    prompt_tokens_estimate=estimate_tokens([prompt]),
                )
                records.append(record)
                output_rows.append(
                    {
                        "run_id": args.run_id,
                        "instance_id": case["instance_id"],
                        "sample_index": case["sample_index"],
                        "merge_surface": surface,
                        "strategy_index": int(strategy["strategy_index"]),
                        "strategy_name": strategy["strategy_name"],
                        "prompt": prompt if args.include_prompts else None,
                        "output": output,
                        "usage": usage,
                        "audit": audit,
                    }
                )
                if args.sleep_seconds:
                    time.sleep(args.sleep_seconds)

    summary = summarize(records, args.run_id, args.model)
    trace_path = out_dir / "comm_trace_moc_merge_prompt_role_audit_v11.jsonl"
    outputs_path = out_dir / "merge_outputs.jsonl"
    summary_path = out_dir / "summary.json"
    manifest_path = out_dir / "manifest.json"
    write_jsonl(trace_path, records)
    write_jsonl(outputs_path, output_rows)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    ended_at = datetime.now().isoformat(timespec="seconds")
    command = "python scripts/run_moc_merge_prompt_role_audit.py " + " ".join(args.raw_args)
    manifest = {
        "run_id": args.run_id,
        "status": "completed",
        "method": METHOD_FAMILY,
        "model": args.model,
        "dataset": str(args.cases_jsonl),
        "seed": None,
        "samples": len(cases),
        "machine": args.machine,
        "gpu_ids": args.gpu_ids,
        "timeout_minutes": None,
        "started_at": started_at,
        "ended_at": ended_at,
        "upstream_repo": "https://github.com/yao-guan/MOC",
        "upstream_commit": "9c67c92507570704a7df73e452552a3f49e83897",
        "local_changes": ["scripts/run_moc_merge_prompt_role_audit.py"],
        "command": command,
        "log_path": args.server_log or "",
        "result_paths": [str(trace_path), str(outputs_path), str(summary_path)],
        "metrics": {
            "accuracy": None,
            "total_tokens": sum(record["token_cost"]["total_tokens"] for record in records),
            "eval_time_seconds": None,
            "wall_time_seconds": None,
        },
        "caveats": summary["caveats"],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    write_readme(out_dir, summary, command, started_at, ended_at)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--cases-jsonl", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--base-url", required=True, help="OpenAI-compatible base URL, usually http://host:port/v1")
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key", default="EMPTY")
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--max-tokens", type=int, default=220)
    parser.add_argument("--request-timeout", type=int, default=120)
    parser.add_argument("--kppa", type=int, default=45)
    parser.add_argument("--surfaces", nargs="+", default=MERGE_SURFACES, choices=MERGE_SURFACES)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--include-prompts", action="store_true")
    parser.add_argument("--machine", default="local")
    parser.add_argument("--gpu-ids", nargs="*", default=[])
    parser.add_argument("--server-log", default="")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.raw_args = list(argv) if argv is not None else sys.argv[1:]
    summary = run(args)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
