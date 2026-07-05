#!/usr/bin/env python3
"""Run conservative text-based MCA with cue-derived audit certificates.

This runner keeps the original MCA-T cue extraction path, but changes the
receiver contract. Reviewers may change the initial majority only when they
produce an admissible certificate: a cue-derived checkable condition where the
initial answer fails and an alternative answer passes.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from run_basic_mad import (
    ROLE_NAMES,
    is_correct,
    load_rows,
    majority_vote,
    normalize_numeric,
    prompt_from_messages,
    resolve_inside,
)
from run_consensus_quarantine import (
    CandidateCard,
    build_candidate_cards,
    generate_outputs,
    generate_plain_texts,
    independent_prompt,
    reshape,
    transition_label,
)
from run_cpac_dcac import analyze_candidate_pool, decision_payload
from run_mad_mm import cot_prompt, extract_xml_answer, prepare_question
from run_mca_text import (
    CueAtom,
    FilteredCue,
    cue_extraction_prompt,
    cue_payload,
    filter_cues,
    filtered_cue_payload,
    load_input_record_rows,
    parse_cue_atoms,
    parse_cue_id_list,
    row_in_scope,
)


AUDIT_FORMAT = (
    "\n\nReply with exactly one XML tag named certificate containing these child tags:\n"
    "<used_cues>comma-separated cue ids or NONE</used_cues>\n"
    "<condition>one checkable condition derived from the cues</condition>\n"
    "<initial>pass|fail|unknown</initial>\n"
    "<alternative>pass|fail|unknown</alternative>\n"
    "<calculation>minimal verification, not a full solution</calculation>\n"
    "<answer>final answer only; repeat the current answer if keeping it</answer>\n"
    "<decision>keep|change</decision>\n"
    "A change is allowed only when the current answer fails the condition and "
    "the alternative answer passes the same condition. Otherwise keep."
)


@dataclass(frozen=True)
class ParsedAuditCertificate:
    output: str
    used_cues: tuple[str, ...]
    condition: str
    initial_status: str
    alternative_status: str
    calculation: str
    decision: str
    parsed_answer: str | None
    normalized_answer: str | None
    admissible_change: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default=os.environ.get("ACR_WORK_DIR", os.getcwd()))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--split", default="test")
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--gpu-id", default=os.environ.get("CUDA_VISIBLE_DEVICES", "0"))
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--reviewers", type=int, default=3)
    parser.add_argument("--cue-k", type=int, default=2)
    parser.add_argument("--min-change-certificates", type=int, default=2)
    parser.add_argument(
        "--pool-state-scope",
        choices=("all", "collapse", "minority_bearing", "no_majority_conflict", "plurality_conflict"),
        default="all",
        help="Only run cue audit for this CPAC pool state; others keep initial majority.",
    )
    parser.add_argument("--input-records", default="", help="Optional existing records.jsonl to reuse initial outputs.")
    parser.add_argument(
        "--initial-prompt-style",
        choices=("mca", "standard-mad"),
        default="mca",
        help="Prompt family for newly sampled initial answers when --input-records is not used.",
    )
    parser.add_argument("--overlap-threshold", type=float, default=0.72)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--cue-temperature", type=float, default=0.2)
    parser.add_argument("--audit-temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--cue-max-tokens", type=int, default=512)
    parser.add_argument("--audit-max-tokens", type=int, default=1536)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.85)
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    parser.add_argument("--disable-tqdm", action="store_true")
    return parser.parse_args()


def _extract_tag(text: str, tag: str) -> str:
    match = re.search(fr"<{tag}>(.*?)</{tag}>", text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_status(value: str) -> str:
    compact = re.sub(r"[^a-z]+", "", value.lower())
    if compact.startswith("pass"):
        return "pass"
    if compact.startswith("fail"):
        return "fail"
    return "unknown"


def _normalize_decision(value: str) -> str:
    compact = re.sub(r"[^a-z]+", "", value.lower())
    return "change" if compact.startswith("change") else "keep"


def parse_audit_certificate(text: str) -> ParsedAuditCertificate:
    used_cues = parse_cue_id_list(_extract_tag(text, "used_cues"))
    condition = _normalize_space(_extract_tag(text, "condition"))
    initial_status = _normalize_status(_extract_tag(text, "initial"))
    alternative_status = _normalize_status(_extract_tag(text, "alternative"))
    calculation = _normalize_space(_extract_tag(text, "calculation"))
    parsed_answer = _extract_tag(text, "answer") or extract_xml_answer(text)
    decision = _normalize_decision(_extract_tag(text, "decision"))
    normalized_answer = normalize_numeric(parsed_answer)
    admissible_change = (
        decision == "change"
        and initial_status == "fail"
        and alternative_status == "pass"
        and normalized_answer is not None
    )
    return ParsedAuditCertificate(
        output=text,
        used_cues=used_cues,
        condition=condition,
        initial_status=initial_status,
        alternative_status=alternative_status,
        calculation=calculation,
        decision=decision,
        parsed_answer=parsed_answer,
        normalized_answer=normalized_answer,
        admissible_change=admissible_change,
    )


def audit_prompt(
    question: str,
    reviewer_index: int,
    current_answer: str | None,
    current_card: CandidateCard | None,
    cards: list[CandidateCard],
    kept_cues: list[FilteredCue],
) -> list[dict[str, str]]:
    role = ROLE_NAMES[reviewer_index % len(ROLE_NAMES)]
    cue_text = "\n".join(
        f"{item.cue.cue_id} [{item.cue.cue_type}]: {item.cue.cue_text}"
        for item in kept_cues
        if item.keep
    )
    current_reasoning = current_card.representative_output if current_card is not None else ""
    alternative_cards = [card for card in cards if card.normalized_answer != current_answer]
    alternative_text = "\n\n".join(
        (
            f"Candidate {card.card_id}\n"
            f"Answer: {card.parsed_answer}\n"
            f"Reasoning:\n{card.representative_output}"
        )
        for card in alternative_cards
    )
    if not alternative_text:
        alternative_text = "No separate initial alternative candidate is available. You may propose a new answer only if a cue-derived condition proves the current answer fails."
    return [
        {
            "role": "system",
            "content": (
                f"You are conservative MCA audit reviewer {reviewer_index + 1}, a {role}. "
                "Cues are not evidence by themselves. Convert cues into one checkable condition. "
                "Keep the current answer unless the condition proves it fails and an alternative passes."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                "Current answer to audit:\n"
                f"{current_answer}\n\n"
                "Current answer reasoning:\n"
                f"{current_reasoning}\n\n"
                "Alternative candidates, if any:\n"
                f"{alternative_text}\n\n"
                "Anonymous metacognitive cues:\n"
                f"{cue_text}\n\n"
                "Do not change the answer just because a cue suggests another route. "
                "A change needs a concrete shared test where the current answer fails and the alternative passes."
                f"{AUDIT_FORMAT}"
            ),
        },
    ]


def aggregate_audit_decision(
    initial_answer: str | None,
    certificates: list[ParsedAuditCertificate],
    *,
    min_change_certificates: int,
) -> tuple[str | None, str, int, int]:
    initial_norm = normalize_numeric(initial_answer)
    required = min(max(1, min_change_certificates), max(1, len(certificates)))
    counts: Counter[str] = Counter()
    answer_by_norm: dict[str, str] = {}
    for certificate in certificates:
        if not certificate.admissible_change:
            continue
        if certificate.normalized_answer == initial_norm:
            continue
        norm = certificate.normalized_answer
        if norm is None:
            continue
        counts[norm] += 1
        answer_by_norm[norm] = certificate.parsed_answer or norm
    if counts:
        best_norm, best_count = counts.most_common(1)[0]
        if best_count >= required:
            return answer_by_norm[best_norm], "change", best_count, required
    return initial_answer, "keep", 0, required


def certificate_payload(item: ParsedAuditCertificate) -> dict[str, Any]:
    return {
        "output": item.output,
        "used_cues": list(item.used_cues),
        "condition": item.condition,
        "initial_status": item.initial_status,
        "alternative_status": item.alternative_status,
        "calculation": item.calculation,
        "decision": item.decision,
        "parsed_answer": item.parsed_answer,
        "normalized_answer": item.normalized_answer,
        "admissible_change": item.admissible_change,
    }


def main() -> int:
    args = parse_args()
    if args.agents < 2:
        raise SystemExit("--agents must be >= 2")
    if args.reviewers < 1:
        raise SystemExit("--reviewers must be >= 1")
    if args.cue_k < 1:
        raise SystemExit("--cue-k must be >= 1")
    if args.min_change_certificates < 1:
        raise SystemExit("--min-change-certificates must be >= 1")

    work_dir = Path(args.work_dir).expanduser().resolve()
    method_key = f"mca-text-audit-{args.pool_state_scope}"
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-{method_key}",
        work_dir,
        "output dir",
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    from vllm import LLM, SamplingParams

    if args.input_records:
        rows, initial_by_row = load_input_record_rows(resolve_inside(Path(args.input_records), work_dir, "input records"), args.limit)
    else:
        data_path = resolve_inside(
            work_dir / "data" / "benchmarks" / args.benchmark / args.split / "canonical.jsonl",
            work_dir,
            "benchmark path",
        )
        rows = load_rows(data_path, args.limit)
        initial_by_row = []

    questions = [prepare_question(str(row.get("question") or ""), args.benchmark) for row in rows]
    started_at = time.time()
    model_path = Path(args.model_path).expanduser().resolve()
    llm = LLM(
        model=str(model_path),
        trust_remote_code=True,
        dtype=args.dtype,
        max_model_len=args.max_model_len,
        gpu_memory_utilization=args.gpu_memory_utilization,
        tensor_parallel_size=1,
        seed=args.seed,
    )
    tokenizer = llm.get_tokenizer()

    initial_sampling = SamplingParams(
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        logprobs=1,
    )
    cue_sampling = SamplingParams(
        temperature=args.cue_temperature,
        top_p=args.top_p,
        max_tokens=args.cue_max_tokens,
    )
    audit_sampling = SamplingParams(
        temperature=args.audit_temperature,
        top_p=args.top_p,
        max_tokens=args.audit_max_tokens,
    )
    use_tqdm = not args.disable_tqdm

    if not initial_by_row:
        initial_prompts: list[str] = []
        for question in questions:
            for agent_idx in range(args.agents):
                if args.initial_prompt_style == "standard-mad":
                    initial_prompts.append(prompt_from_messages(tokenizer, [{"role": "user", "content": cot_prompt(question)}]))
                else:
                    initial_prompts.append(prompt_from_messages(tokenizer, independent_prompt(question, agent_idx)))
        initial_flat = generate_outputs(llm, initial_prompts, initial_sampling, args.batch_size, use_tqdm=use_tqdm)
        initial_by_row = reshape(initial_flat, len(rows), args.agents)

    cards_by_row = [build_candidate_cards(outputs) for outputs in initial_by_row]
    decisions = [
        analyze_candidate_pool(
            outputs,
            cards,
            no_majority_action="listwise",
            overlap_threshold=args.overlap_threshold,
        )
        for outputs, cards in zip(initial_by_row, cards_by_row)
    ]

    cue_prompts: list[str] = []
    cue_owners: list[tuple[int, int]] = []
    for row_idx, (question, outputs, decision) in enumerate(zip(questions, initial_by_row, decisions)):
        if not row_in_scope(decision.pool_state, args.pool_state_scope):
            continue
        for agent_idx, output in enumerate(outputs):
            cue_prompts.append(prompt_from_messages(tokenizer, cue_extraction_prompt(question, output, cue_k=args.cue_k)))
            cue_owners.append((row_idx, agent_idx))

    cue_texts = generate_plain_texts(llm, cue_prompts, cue_sampling, args.batch_size, use_tqdm=use_tqdm) if cue_prompts else []
    cue_atoms_by_row: list[list[CueAtom]] = [[] for _ in rows]
    cue_raw_outputs_by_row: list[list[dict[str, Any]]] = [[] for _ in rows]
    for (row_idx, agent_idx), cue_output in zip(cue_owners, cue_texts):
        cue_atoms = parse_cue_atoms(
            cue_output,
            source_agent_index=agent_idx,
            source_answer=initial_by_row[row_idx][agent_idx].get("parsed_answer"),
            max_cues=args.cue_k,
        )
        cue_atoms_by_row[row_idx].extend(cue_atoms)
        cue_raw_outputs_by_row[row_idx].append(
            {
                "source_agent_index": agent_idx,
                "cue_output": cue_output,
                "parsed_cue_ids": [cue.cue_id for cue in cue_atoms],
            }
        )

    filtered_by_row = [
        filter_cues(cues, cards) if row_in_scope(decision.pool_state, args.pool_state_scope) else []
        for cues, cards, decision in zip(cue_atoms_by_row, cards_by_row, decisions)
    ]

    audit_prompts: list[str] = []
    audit_owners: list[int] = []
    initial_majorities: list[str | None] = []
    initial_ties: list[bool] = []
    for outputs in initial_by_row:
        majority_answer, initial_tie = majority_vote([output.get("parsed_answer") for output in outputs])
        initial_majorities.append(majority_answer)
        initial_ties.append(initial_tie)

    for row_idx, (question, cards, decision, filtered) in enumerate(zip(questions, cards_by_row, decisions, filtered_by_row)):
        if not row_in_scope(decision.pool_state, args.pool_state_scope):
            continue
        kept = [item for item in filtered if item.keep]
        if not kept:
            continue
        current_answer = initial_majorities[row_idx]
        current_card = next((card for card in cards if card.normalized_answer == current_answer), None)
        for reviewer_idx in range(args.reviewers):
            audit_prompts.append(
                prompt_from_messages(tokenizer, audit_prompt(question, reviewer_idx, current_answer, current_card, cards, kept))
            )
            audit_owners.append(row_idx)

    audit_texts = generate_plain_texts(llm, audit_prompts, audit_sampling, args.batch_size, use_tqdm=use_tqdm) if audit_prompts else []
    certificates_by_row: list[list[ParsedAuditCertificate]] = [[] for _ in rows]
    for row_idx, text in zip(audit_owners, audit_texts):
        certificates_by_row[row_idx].append(parse_audit_certificate(text))

    records_path = output_dir / "records.jsonl"
    summary_counts: Counter[str] = Counter()
    pool_state_counts: Counter[str] = Counter()
    filter_reason_counts: Counter[str] = Counter()
    pool_state_metrics: dict[str, Counter[str]] = {}

    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for idx, row in enumerate(rows):
            gold = row.get("answer")
            decision = decisions[idx]
            scoped = row_in_scope(decision.pool_state, args.pool_state_scope)
            pool_state_counts[decision.pool_state] += 1
            pool_metrics = pool_state_metrics.setdefault(decision.pool_state, Counter())
            pool_metrics["total"] += 1
            summary_counts["total"] += 1
            if scoped:
                summary_counts["scoped_cases"] += 1

            filtered = filtered_by_row[idx]
            kept_cues = [item for item in filtered if item.keep]
            summary_counts["cue_atoms"] += len(cue_atoms_by_row[idx])
            summary_counts["kept_cues"] += len(kept_cues)
            if kept_cues:
                summary_counts["cue_coverage_cases"] += 1
                pool_metrics["cue_coverage_cases"] += 1
            for item in filtered:
                if not item.keep:
                    for reason in item.reasons:
                        filter_reason_counts[reason] += 1

            final_answer, audit_decision, admissible_count, required = aggregate_audit_decision(
                initial_majorities[idx],
                certificates_by_row[idx],
                min_change_certificates=args.min_change_certificates,
            )
            final_tie = False
            if certificates_by_row[idx]:
                summary_counts["audit_cases"] += 1
                pool_metrics["audit_cases"] += 1
            if audit_decision == "change":
                summary_counts["accepted_changes"] += 1
                pool_metrics["accepted_changes"] += 1
            summary_counts["admissible_change_certificates"] += sum(
                1 for certificate in certificates_by_row[idx] if certificate.admissible_change
            )

            initial_ok = is_correct(initial_majorities[idx], gold)
            final_ok = is_correct(final_answer, gold)
            transition = transition_label(initial_ok, final_ok)
            if initial_ok:
                summary_counts["initial_majority_correct"] += 1
                pool_metrics["initial_majority_correct"] += 1
            if final_ok:
                summary_counts["final_correct"] += 1
                pool_metrics["final_correct"] += 1
            if normalize_numeric(final_answer) is None:
                summary_counts["final_parse_fail"] += 1
            if final_tie:
                summary_counts["final_majority_ties"] += 1
            if normalize_numeric(initial_majorities[idx]) != normalize_numeric(final_answer):
                summary_counts["answer_changed"] += 1
            summary_counts[transition] += 1
            pool_metrics[transition] += 1

            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row.get("index", idx),
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "mca": {
                    "variant": "text_audit",
                    "pool_state_scope": args.pool_state_scope,
                    "agents": args.agents,
                    "reviewers": args.reviewers,
                    "cue_k": args.cue_k,
                    "min_change_certificates": args.min_change_certificates,
                    "initial_outputs": initial_by_row[idx],
                    "initial_majority_answer": initial_majorities[idx],
                    "initial_majority_tie": initial_ties[idx],
                    "candidate_cards": [
                        {
                            "card_id": card.card_id,
                            "parsed_answer": card.parsed_answer,
                            "normalized_answer": card.normalized_answer,
                            "supporter_count_hidden_from_prompt": card.supporter_count,
                            "source_indices": list(card.source_indices),
                            "representative_output": card.representative_output,
                        }
                        for card in cards_by_row[idx]
                    ],
                    "candidate_pool_decision": decision_payload(decision),
                    "in_scope": scoped,
                    "cue_raw_outputs": cue_raw_outputs_by_row[idx],
                    "cue_atoms": [cue_payload(cue) for cue in cue_atoms_by_row[idx]],
                    "filtered_cues": [filtered_cue_payload(item) for item in filtered_by_row[idx]],
                    "audit_certificates": [certificate_payload(item) for item in certificates_by_row[idx]],
                    "branch_result": {
                        "decision": audit_decision,
                        "admissible_change_certificates": admissible_count,
                        "required_change_certificates": required,
                    },
                    "final_majority_answer": final_answer,
                    "final_normalized_answer": normalize_numeric(final_answer),
                    "final_majority_tie": final_tie,
                    "correct": final_ok,
                    "transition": transition,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    elapsed = time.time() - started_at
    total = max(1, summary_counts["total"])
    scoped_total = max(1, summary_counts["scoped_cases"])
    cue_atoms_total = max(1, summary_counts["cue_atoms"])
    audit_outputs_total = max(1, len(audit_prompts))
    initial_wrong = max(1, summary_counts["MaW_to_C"] + summary_counts["MaW_to_W"])
    initial_correct = max(1, summary_counts["MaC_to_C"] + summary_counts["MaC_to_W"])

    pool_metrics_payload = {}
    for state, counts in sorted(pool_state_metrics.items()):
        state_total = max(1, counts["total"])
        state_initial_wrong = max(1, counts["MaW_to_C"] + counts["MaW_to_W"])
        state_initial_correct = max(1, counts["MaC_to_C"] + counts["MaC_to_W"])
        pool_metrics_payload[state] = {
            "counts": dict(sorted(counts.items())),
            "metrics": {
                "initial_majority_accuracy": counts["initial_majority_correct"] / state_total,
                "final_accuracy": counts["final_correct"] / state_total,
                "cue_coverage_rate": counts["cue_coverage_cases"] / state_total,
                "audit_rate": counts["audit_cases"] / state_total,
                "accepted_change_rate": counts["accepted_changes"] / state_total,
                "wrong_majority_recovery_rate": counts["MaW_to_C"] / state_initial_wrong,
                "correct_majority_harm_rate": counts["MaC_to_W"] / state_initial_correct,
            },
        }

    summary = {
        "run_id": args.run_id,
        "model_key": args.model_key,
        "model_path": str(model_path),
        "benchmark": args.benchmark,
        "split": args.split,
        "rows": len(rows),
        "protocol": "mca-text-audit",
        "agents": args.agents,
        "reviewers": args.reviewers,
        "cue_k": args.cue_k,
        "min_change_certificates": args.min_change_certificates,
        "pool_state_scope": args.pool_state_scope,
        "input_records": args.input_records or None,
        "initial_prompt_style": args.initial_prompt_style,
        "temperature": args.temperature,
        "cue_temperature": args.cue_temperature,
        "audit_temperature": args.audit_temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": {
            **dict(summary_counts),
            "audit_prompt_count": len(audit_prompts),
            "pool_states": dict(sorted(pool_state_counts.items())),
            "filter_reasons": dict(sorted(filter_reason_counts.items())),
        },
        "metrics": {
            "initial_majority_accuracy": summary_counts["initial_majority_correct"] / total,
            "final_accuracy": summary_counts["final_correct"] / total,
            "scoped_case_rate": summary_counts["scoped_cases"] / total,
            "cue_coverage_rate": summary_counts["cue_coverage_cases"] / scoped_total,
            "kept_cues_per_scoped_case": summary_counts["kept_cues"] / scoped_total,
            "answer_leak_rejection_rate": (
                filter_reason_counts["candidate_answer_leak"] + filter_reason_counts["self_reported_answer_leak"]
            )
            / cue_atoms_total,
            "generic_cue_rejection_rate": filter_reason_counts["generic"] / cue_atoms_total,
            "admissible_change_certificate_rate": summary_counts["admissible_change_certificates"] / audit_outputs_total,
            "accepted_change_rate": summary_counts["accepted_changes"] / total,
            "answer_change_rate": summary_counts["answer_changed"] / total,
            "wrong_majority_recovery_rate": summary_counts["MaW_to_C"] / initial_wrong,
            "correct_majority_harm_rate": summary_counts["MaC_to_W"] / initial_correct,
            "final_parse_fail_rate": summary_counts["final_parse_fail"] / total,
            "final_majority_tie_rate": summary_counts["final_majority_ties"] / total,
        },
        "pool_state_metrics": pool_metrics_payload,
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {args.benchmark}-{args.model_key}-mca-text-audit\n\n")
        handle.write(f"- Rows: {len(rows)}\n")
        handle.write(f"- Pool-state scope: {args.pool_state_scope}\n")
        handle.write(f"- Initial majority accuracy: {summary['metrics']['initial_majority_accuracy']:.4f}\n")
        handle.write(f"- Final accuracy: {summary['metrics']['final_accuracy']:.4f}\n")
        handle.write(f"- Cue coverage rate: {summary['metrics']['cue_coverage_rate']:.4f}\n")
        handle.write(f"- Admissible change certificate rate: {summary['metrics']['admissible_change_certificate_rate']:.4f}\n")
        handle.write(f"- Accepted change rate: {summary['metrics']['accepted_change_rate']:.4f}\n")
        handle.write(f"- Wrong-majority recovery rate: {summary['metrics']['wrong_majority_recovery_rate']:.4f}\n")
        handle.write(f"- Correct-majority harm rate: {summary['metrics']['correct_majority_harm_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
