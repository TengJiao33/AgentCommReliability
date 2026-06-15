#!/usr/bin/env python3
"""Build narrow per-alarm verifier prompts from the PACT answer-contract packet."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_INPUT_PACKET = Path("experiments/20260615-local-pact-answer-contract-verifier-packet/verifier_packet.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-answer-contract-split-alarm-packet")

ALARM_TASKS = [
    "answer_contract_alarm",
    "target_authority_alarm",
    "answer_type_relation_alarm",
    "short_span_granularity_alarm",
    "evidence_adequacy_alarm",
    "final_candidate_alarm",
]

TASK_DEFINITIONS = {
    "answer_contract_alarm": [
        "Question: Can any visible public field mislead the downstream answerer about the original question contract?",
        "Return yes for wrong target, wrong relation, wrong answer type, wrong span/granularity, missing or distractor evidence, or risky final-answer commitment.",
        "Return no only if the public fields are safe enough for this audit.",
        "Allowed labels: yes, no.",
    ],
    "target_authority_alarm": [
        "Question: Does Action Required itself change, narrow, misstate, or over-authorize the original question contract?",
        "Return yes when Action Required points at the wrong entity, wrong relation, wrong answer type, or wrong requested granularity.",
        "Return soft only when Action Required is not the main failure but weakly contributes to another alarm.",
        "Return no when the main problem is evidence adequacy, final-candidate attraction, strict span formatting, or no failure while Action Required remains compatible with the original question.",
        "Allowed labels: yes, no, soft.",
    ],
    "answer_type_relation_alarm": [
        "Question: Do the public fields steer toward the wrong answer type or wrong relation for the original question?",
        "Return yes for entity-vs-date, yes/no-vs-entity, location-vs-person, wrong relation, or similar answer-contract mismatch.",
        "Return no if answer type and relation are compatible, even when evidence is insufficient or the final candidate is risky.",
        "Allowed labels: yes, no.",
    ],
    "short_span_granularity_alarm": [
        "Question: Do the public fields request or encourage the wrong span length or granularity?",
        "Return yes for missing qualifiers, over-specific spans, under-specific spans, wrong level of granularity, or formatting/span-only mismatch.",
        "Return no for wrong relation, wrong entity, bad evidence, or final-candidate attraction unless span/granularity is the issue.",
        "Allowed labels: yes, no.",
    ],
    "evidence_adequacy_alarm": [
        "Question: Are Environment State or Action Result missing, contradictory, distractor-like, or insufficient for the original question?",
        "Return yes if the evidence/result is about a related but wrong entity, does not support the required relation, or cannot answer the original question.",
        "Return no when evidence/result is adequate or when the only issue is target wording, span granularity, or final-candidate attraction.",
        "Allowed labels: yes, no.",
    ],
    "final_candidate_alarm": [
        "Question: Is Final Answer Candidate a risky attractor for copying, over-commitment, wrong brevity, or wrong answer commitment?",
        "Return yes only when the final candidate itself is the visible risk.",
        "Return no if the main problem is Action Required, evidence adequacy, answer type/relation, span/granularity, or no failure.",
        "Allowed labels: yes, no.",
    ],
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def prompt_value(value: Any) -> str:
    if value is None:
        return "[missing]"
    text = str(value).strip()
    return text if text else "[missing]"


def render_prompt(base: Mapping[str, Any], task: str) -> str:
    fields = base.get("public_state_fields") or {}
    definition_lines = TASK_DEFINITIONS[task]
    return "\n".join([
        "You are auditing one narrow alarm in a multi-agent QA public-state handoff.",
        "You do not see the gold answer or downstream model behavior.",
        "Return exactly one JSON object and no extra text.",
        "",
        "Output JSON schema:",
        "{",
        '  "label": "yes|no|soft",',
        '  "rationale": "one short sentence"',
        "}",
        "",
        *definition_lines,
        "",
        "Important:",
        "- Judge only the named alarm for this prompt.",
        "- Do not mark yes just because some other alarm might be present.",
        "- Use the Original Question as the trusted root.",
        "",
        "Visible public-state input:",
        f"Original Question: {prompt_value(base.get('question'))}",
        f"Action Required: {prompt_value(fields.get('action_required'))}",
        f"Environment State: {prompt_value(fields.get('environment_state'))}",
        f"Action Result: {prompt_value(fields.get('action_result'))}",
        f"Final Answer Candidate: {prompt_value(fields.get('final_answer_candidate'))}",
    ])


def build(args: argparse.Namespace) -> dict[str, Any]:
    base_rows = load_jsonl(args.input_packet)
    rows: list[dict[str, Any]] = []
    for base in base_rows:
        for task in ALARM_TASKS:
            gold = str((base.get("gold_label") or {}).get(task, "no"))
            rows.append({
                "packet_id": f"{base['packet_id']}::split-alarm::{task}",
                "base_packet_id": base["packet_id"],
                "case_id": base.get("case_id"),
                "label_source": base.get("label_source"),
                "slice": base.get("slice"),
                "sample_index": base.get("sample_index"),
                "source_run": base.get("source_run"),
                "task": task,
                "gold_label": gold,
                "prompt": render_prompt(base, task),
                "metadata": {
                    "source_packet": str(args.input_packet),
                    "base_primary_failure_surface": (base.get("gold_label") or {}).get("primary_failure_surface"),
                },
            })

    summary = {
        "records": len(rows),
        "base_records": len(base_rows),
        "tasks": list(ALARM_TASKS),
        "records_by_task": dict(sorted(Counter(row["task"] for row in rows).items())),
        "label_source_counts": dict(sorted(Counter(str(row.get("label_source")) for row in rows).items())),
        "gold_by_task": {
            task: dict(sorted(Counter(str(row["gold_label"]) for row in rows if row["task"] == task).items()))
            for task in ALARM_TASKS
        },
        "records_by_task_and_label_source": {
            task: dict(sorted(Counter(str(row.get("label_source")) for row in rows if row["task"] == task).items()))
            for task in ALARM_TASKS
        },
        "input_packet": str(args.input_packet),
        "outputs": {
            "packet": str(args.out_dir / "split_alarm_packet.jsonl"),
            "summary": str(args.out_dir / "summary.json"),
            "scoring_plan": str(args.out_dir / "scoring_plan.md"),
        },
        "note": "Each row asks exactly one alarm question over the same public-state fields.",
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "split_alarm_packet.jsonl", rows)
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "scoring_plan.md", render_scoring_plan(summary))
    return summary


def render_scoring_plan(summary: Mapping[str, Any]) -> str:
    lines = [
        "# PACT Answer-Contract Split-Alarm Packet",
        "",
        "This packet decomposes the answer-contract verifier into one narrow prompt per alarm.",
        "",
        f"- Base records: `{summary['base_records']}`",
        f"- Prompt rows: `{summary['records']}`",
        f"- Tasks: `{summary['tasks']}`",
        "",
        "## Gold Counts By Task",
        "",
        "| Task | Gold counts |",
        "| --- | --- |",
    ]
    for task, counts in summary["gold_by_task"].items():
        lines.append(f"| `{task}` | `{counts}` |")
    lines.extend([
        "",
        "## Output Schema",
        "",
        "Each model output should be one JSON object with:",
        "",
        "- `label`: `yes`, `no`, or `soft` for target-authority; `yes` or `no` for other tasks;",
        "- `rationale`: one short sentence.",
        "",
    ])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-packet", type=Path, default=DEFAULT_INPUT_PACKET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
