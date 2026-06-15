#!/usr/bin/env python3
"""Build a stricter prompt-v2 packet from the PACT answer-contract verifier packet."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


DEFAULT_INPUT_PACKET = Path("experiments/20260615-local-pact-answer-contract-verifier-packet/verifier_packet.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-answer-contract-verifier-packet-v2")

PRIMARY_SURFACES = [
    "answer_type_or_relation_mismatch",
    "short_span_or_granularity_mismatch",
    "public_target_misdirection",
    "evidence_sentence_or_distractor_copy",
    "question_root_ambiguity_regression",
    "evidence_or_content_failure",
    "final_candidate_attractor",
    "strict_span_or_granularity_surface",
    "no_answer_contract_failure",
]


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


def render_prompt(row: Mapping[str, Any]) -> str:
    fields = row.get("public_state_fields") or {}
    surfaces = ", ".join(PRIMARY_SURFACES)
    return "\n".join([
        "You are a strict public-state verifier for a multi-agent QA handoff.",
        "",
        "Your job is to decide whether the visible public fields are safe task authority for answering the original question.",
        "You do not see the gold answer or downstream model behavior.",
        "Return exactly one JSON object and no extra text.",
        "",
        "Output JSON schema:",
        "{",
        '  "answer_contract_alarm": "yes|no",',
        '  "target_authority_alarm": "yes|no|soft",',
        '  "answer_type_relation_alarm": "yes|no",',
        '  "short_span_granularity_alarm": "yes|no",',
        '  "evidence_adequacy_alarm": "yes|no",',
        '  "final_candidate_alarm": "yes|no",',
        f'  "primary_failure_surface": "{surfaces}",',
        '  "rationale": "one short sentence"',
        "}",
        "",
        "Consistency rules:",
        "- If primary_failure_surface is not no_answer_contract_failure, answer_contract_alarm must be yes.",
        "- If any subalarm is yes, answer_contract_alarm must be yes.",
        "- If answer_contract_alarm is no, every subalarm must be no and primary_failure_surface must be no_answer_contract_failure.",
        "- Use target_authority_alarm = soft rarely. Soft means Action Required is not the main failure, but it weakly contributes to another alarm.",
        "- Do not use soft for ordinary evidence/content failures, final-candidate attraction, strict-span-only failures, or no-failure rows.",
        "",
        "Decision order:",
        "1. Compare Action Required to the Original Question.",
        "2. Check whether Action Required changes the requested relation, target entity, answer type, or span granularity.",
        "3. Check whether Environment State and Action Result give enough evidence for the original question, not just a related entity.",
        "4. Check whether Final Answer Candidate is a risky attractor or unsupported commitment.",
        "5. Choose exactly one primary_failure_surface.",
        "",
        "Surface definitions:",
        "- public_target_misdirection: Action Required itself points at the wrong entity, wrong relation, or a distractor target.",
        "- answer_type_or_relation_mismatch: the public fields ask for or steer toward the wrong answer type or relation, even if the target looks related.",
        "- short_span_or_granularity_mismatch: the public target/result asks for the wrong level of specificity, misses a qualifier, or demands an over/under-specific span.",
        "- evidence_sentence_or_distractor_copy: evidence wording is copied from a distractor-like sentence or unrelated evidence sentence.",
        "- question_root_ambiguity_regression: the original question root is ambiguous enough that a public target can reopen a wrong interpretation.",
        "- evidence_or_content_failure: Action Required is broadly compatible with the question, but Environment State or Action Result is missing, contradictory, insufficient, or about the wrong related entity.",
        "- final_candidate_attractor: Final Answer Candidate is visible and likely to cause copying, over-commitment, or wrong brevity.",
        "- strict_span_or_granularity_surface: the only visible problem is span formatting or granularity of an otherwise relevant answer.",
        "- no_answer_contract_failure: the public fields are safe enough for this audit.",
        "",
        "Target-authority rule:",
        "- target_authority_alarm = yes only when Action Required itself changes, narrows, misstates, or over-authorizes the original question contract.",
        "- target_authority_alarm = no when the main problem is evidence adequacy, final candidate attraction, or strict span/granularity while Action Required remains compatible with the original question.",
        "- target_authority_alarm = soft only for a secondary Action Required issue; do not use it as a general uncertainty label.",
        "",
        "Visible public-state input:",
        f"Original Question: {prompt_value(row.get('question'))}",
        f"Action Required: {prompt_value(fields.get('action_required'))}",
        f"Environment State: {prompt_value(fields.get('environment_state'))}",
        f"Action Result: {prompt_value(fields.get('action_result'))}",
        f"Final Answer Candidate: {prompt_value(fields.get('final_answer_candidate'))}",
    ])


def label_counts(rows: Iterable[Mapping[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str((row.get("gold_label") or {}).get(field)) for row in rows).items()))


def nested_counts(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> dict[str, dict[str, int]]:
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        out[str(row.get(outer))][str((row.get("gold_label") or {}).get(inner))] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(out.items())}


def summarize(rows: list[Mapping[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    return {
        "records": len(rows),
        "input_packet": str(args.input_packet),
        "prompt_version": "v2_strict_consistency",
        "label_source_counts": dict(sorted(Counter(str(row.get("label_source")) for row in rows).items())),
        "records_by_slice": dict(sorted(Counter(str(row.get("slice")) for row in rows).items())),
        "primary_failure_surface_counts": label_counts(rows, "primary_failure_surface"),
        "answer_contract_alarm_counts": label_counts(rows, "answer_contract_alarm"),
        "target_authority_alarm_counts": label_counts(rows, "target_authority_alarm"),
        "primary_surface_by_label_source": nested_counts(rows, "label_source", "primary_failure_surface"),
        "outputs": {
            "verifier_packet": str(args.out_dir / "verifier_packet.jsonl"),
            "gold_labels": str(args.out_dir / "gold_labels.jsonl"),
            "summary": str(args.out_dir / "summary.json"),
            "scoring_plan": str(args.out_dir / "scoring_plan.md"),
        },
        "note": "Same records and labels as the v1 verifier packet; only prompt text is changed.",
    }


def render_scoring_plan(summary: Mapping[str, Any]) -> str:
    return "\n".join([
        "# PACT Answer-Contract Verifier Packet V2",
        "",
        "This packet keeps the same records and gold labels as the v1 verifier packet.",
        "Only the prompt is changed.",
        "",
        "## Prompt Repair",
        "",
        "- Adds consistency rules tying `answer_contract_alarm` to subalarms and primary surface.",
        "- Restricts `target_authority_alarm = soft` to secondary Action Required issues.",
        "- Adds a decision order and sharper surface definitions.",
        "- Separates target authority from evidence adequacy, final-candidate attraction, and strict span/granularity.",
        "",
        "## Size",
        "",
        f"- Records: `{summary['records']}`",
        f"- Label sources: `{summary['label_source_counts']}`",
        f"- Primary surfaces: `{summary['primary_failure_surface_counts']}`",
        "",
        "## Scoring",
        "",
        "Use `scripts/evaluate_pact_answer_contract_verifier.py` with `--prediction-source outputs`.",
        "",
    ])


def build(args: argparse.Namespace) -> dict[str, Any]:
    rows = load_jsonl(args.input_packet)
    rewritten: list[dict[str, Any]] = []
    for row in rows:
        new_row = dict(row)
        new_row["prompt"] = render_prompt(row)
        metadata = dict(new_row.get("metadata") or {})
        metadata["prompt_version"] = "v2_strict_consistency"
        metadata["prompt_repair"] = {
            "same_records_and_labels_as_v1": True,
            "answer_contract_consistency_rules": True,
            "target_authority_soft_restriction": True,
        }
        new_row["metadata"] = metadata
        rewritten.append(new_row)

    summary = summarize(rewritten, args)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "verifier_packet.jsonl", rewritten)
    write_jsonl(
        args.out_dir / "gold_labels.jsonl",
        [
            {
                "packet_id": row["packet_id"],
                "case_id": row["case_id"],
                "label_source": row["label_source"],
                "slice": row.get("slice"),
                "sample_index": row.get("sample_index"),
                "source_run": row.get("source_run"),
                "gold_label": row["gold_label"],
                "gold_note": row.get("gold_note"),
            }
            for row in rewritten
        ],
    )
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "scoring_plan.md", render_scoring_plan(summary))
    return summary


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
