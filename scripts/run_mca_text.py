#!/usr/bin/env python3
"""Run text-based Metacognitive Communication for multi-agent reasoning.

MCA-T is a diagnostic runner. It extracts answer-free cue atoms from initial
agent traces, filters obvious answer leaks and generic advice, then asks blind
reviewers to re-solve from the problem plus anonymous cues.
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
from run_mad_mm import extract_xml_answer, prepare_question


CUE_TYPES = {
    "formula",
    "representation",
    "invariant",
    "constraint",
    "subgoal",
    "sanity_check",
    "pitfall",
}

CUE_FORMAT = (
    "\n\nReply with XML only. Use this exact structure:\n"
    "<cues>\n"
    "  <cue>\n"
    "    <type>formula|representation|invariant|constraint|subgoal|sanity_check|pitfall</type>\n"
    "    <text>one concrete answer-free cue, 8 to 40 words</text>\n"
    "    <why>one short sentence explaining relevance</why>\n"
    "    <answer_leak>yes|no</answer_leak>\n"
    "  </cue>\n"
    "</cues>\n"
    "If no concrete answer-free cue exists, reply with <cues></cues>."
)

RESOLVE_FORMAT = (
    "\n\nEnd with exactly these XML tags:\n"
    "<used_cues>comma-separated cue ids or NONE</used_cues>\n"
    "<ignored_cues>comma-separated cue ids or NONE</ignored_cues>\n"
    "<new_realization>one sentence or NONE</new_realization>\n"
    "<answer>final answer only</answer>"
)

GENERIC_PHRASES = (
    "be careful",
    "check your work",
    "double check",
    "solve step by step",
    "think step by step",
    "read the problem",
    "verify the answer",
    "check the answer",
    "do the calculation",
    "use math",
)

SPECIFICITY_MARKERS = (
    "base",
    "mod",
    "modulo",
    "parity",
    "integer",
    "domain",
    "range",
    "boundary",
    "extreme",
    "invariant",
    "symmetry",
    "vieta",
    "recurrence",
    "telescop",
    "substitution",
    "coordinate",
    "geometry",
    "area",
    "angle",
    "probability",
    "overcount",
    "complement",
    "case",
    "constraint",
    "unit",
    "dimension",
    "factor",
    "root",
    "sign",
    "monotonic",
    "derivative",
    "matrix",
    "vector",
    "notation",
    "pitfall",
)


@dataclass(frozen=True)
class CueAtom:
    cue_id: str
    source_agent_index: int
    source_answer: str | None
    cue_type: str
    cue_text: str
    why_relevant: str
    self_reported_answer_leak: bool


@dataclass(frozen=True)
class FilteredCue:
    cue: CueAtom
    keep: bool
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ParsedCueResolve:
    output: str
    parsed_answer: str | None
    normalized_answer: str | None
    used_cues: tuple[str, ...]
    ignored_cues: tuple[str, ...]
    new_realization: str


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
    parser.add_argument(
        "--pool-state-scope",
        choices=("all", "collapse", "minority_bearing", "no_majority_conflict", "plurality_conflict"),
        default="all",
        help="Only run cue extraction/resolve for this CPAC pool state; others keep initial majority.",
    )
    parser.add_argument(
        "--input-records",
        default="",
        help="Optional existing CQG/CPAC records.jsonl to reuse initial outputs.",
    )
    parser.add_argument("--overlap-threshold", type=float, default=0.72)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--cue-temperature", type=float, default=0.2)
    parser.add_argument("--resolve-temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--cue-max-tokens", type=int, default=512)
    parser.add_argument("--resolve-max-tokens", type=int, default=1536)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.85)
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    parser.add_argument(
        "--disable-tqdm",
        action="store_true",
        help="Disable vLLM progress bars; useful for remote nohup/CI runs.",
    )
    return parser.parse_args()


def _extract_tag(text: str, tag: str) -> str:
    match = re.search(fr"<{tag}>(.*?)</{tag}>", text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _word_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_]+", text.lower())


def _word_set(text: str) -> set[str]:
    return set(_word_tokens(text))


def _truthy_answer_leak(text: str) -> bool:
    compact = re.sub(r"[^a-z]+", "", text.lower())
    return compact.startswith("y") or compact in {"true", "leak", "leaks"}


def _normalize_cue_type(text: str) -> str:
    value = re.sub(r"[^a-z_]+", "_", text.lower()).strip("_")
    return value if value in CUE_TYPES else "subgoal"


def cue_extraction_prompt(
    question: str,
    agent_output: dict[str, Any],
    *,
    cue_k: int,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You extract metacognitive cue atoms from math reasoning traces. "
                "A cue is not a final answer and not a full solution. It is a short, concrete, "
                "task-specific reminder about the formula, representation, constraint, subgoal, "
                "sanity check, invariant, or pitfall that matters for solving the problem."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                "Agent reasoning trace:\n"
                f"{agent_output.get('output') or ''}\n\n"
                f"Extract at most {cue_k} useful answer-free cue atoms. "
                "Do not include any final answer, candidate answer, vote, confidence, or full derivation. "
                "Do not write generic advice such as 'be careful' or 'check your work'."
                f"{CUE_FORMAT}"
            ),
        },
    ]


def parse_cue_atoms(
    text: str,
    *,
    source_agent_index: int,
    source_answer: str | None,
    max_cues: int,
) -> list[CueAtom]:
    cues: list[CueAtom] = []
    cue_blocks = re.findall(r"<cue>(.*?)</cue>", text, flags=re.DOTALL | re.IGNORECASE)
    for cue_idx, block in enumerate(cue_blocks[: max(0, max_cues)]):
        cue_text = _normalize_space(_extract_tag(block, "text"))
        why = _normalize_space(_extract_tag(block, "why"))
        if not cue_text and not why:
            continue
        cues.append(
            CueAtom(
                cue_id=f"S{source_agent_index + 1}C{cue_idx + 1}",
                source_agent_index=source_agent_index,
                source_answer=source_answer,
                cue_type=_normalize_cue_type(_extract_tag(block, "type")),
                cue_text=cue_text,
                why_relevant=why,
                self_reported_answer_leak=_truthy_answer_leak(_extract_tag(block, "answer_leak")),
            )
        )
    return cues


def _leak_normalize(text: str) -> str:
    value = str(text or "").lower()
    value = value.replace("\\boxed", "")
    value = re.sub(r"expr:|str:", "", value)
    value = re.sub(r"[^a-z0-9_./+-]+", " ", value)
    return _normalize_space(value)


def candidate_answer_strings(cards: list[CandidateCard]) -> set[str]:
    answers: set[str] = set()
    for card in cards:
        for value in (card.parsed_answer, card.normalized_answer):
            cleaned = _leak_normalize(str(value or ""))
            if cleaned:
                answers.add(cleaned)
            if ":" in str(value or ""):
                payload = str(value).split(":", 1)[1]
                payload_cleaned = _leak_normalize(payload)
                if payload_cleaned:
                    answers.add(payload_cleaned)
    return answers


def contains_candidate_answer(text: str, candidate_answers: set[str]) -> bool:
    haystack = f" {_leak_normalize(text)} "
    for answer in candidate_answers:
        if not answer:
            continue
        escaped = re.escape(answer)
        if re.search(fr"(?<![a-z0-9_]){escaped}(?![a-z0-9_])", haystack):
            return True
    return False


def is_generic_cue(text: str) -> bool:
    lower = text.lower()
    tokens = _word_tokens(text)
    if len(tokens) < 4:
        return True
    if any(phrase in lower for phrase in GENERIC_PHRASES) and len(tokens) <= 8:
        return True
    if len(tokens) <= 6 and not any(marker in lower for marker in SPECIFICITY_MARKERS):
        return True
    return False


def jaccard_similarity(left: str, right: str) -> float:
    left_words = _word_set(left)
    right_words = _word_set(right)
    if not left_words or not right_words:
        return 0.0
    return len(left_words & right_words) / len(left_words | right_words)


def filter_cues(
    cues: list[CueAtom],
    cards: list[CandidateCard],
    *,
    max_words: int = 48,
    duplicate_threshold: float = 0.82,
) -> list[FilteredCue]:
    candidate_answers = candidate_answer_strings(cards)
    kept_texts: list[str] = []
    filtered: list[FilteredCue] = []
    for cue in cues:
        reasons: list[str] = []
        if not cue.cue_text:
            reasons.append("empty")
        if cue.self_reported_answer_leak:
            reasons.append("self_reported_answer_leak")
        if contains_candidate_answer(cue.cue_text, candidate_answers):
            reasons.append("candidate_answer_leak")
        if is_generic_cue(cue.cue_text):
            reasons.append("generic")
        if len(_word_tokens(cue.cue_text)) > max_words:
            reasons.append("too_long")
        if any(jaccard_similarity(cue.cue_text, kept) >= duplicate_threshold for kept in kept_texts):
            reasons.append("duplicate")
        keep = not reasons
        if keep:
            kept_texts.append(cue.cue_text)
        filtered.append(FilteredCue(cue=cue, keep=keep, reasons=tuple(reasons)))
    return filtered


def cue_resolve_prompt(
    question: str,
    reviewer_index: int,
    kept_cues: list[FilteredCue],
) -> list[dict[str, str]]:
    cue_text = "\n".join(
        f"{item.cue.cue_id} [{item.cue.cue_type}]: {item.cue.cue_text}"
        for item in kept_cues
        if item.keep
    )
    role = ROLE_NAMES[reviewer_index % len(ROLE_NAMES)]
    return [
        {
            "role": "system",
            "content": (
                f"You are MCA cue resolver {reviewer_index + 1}, a {role}. "
                "You receive anonymous answer-free metacognitive cues. "
                "Do not infer vote counts or trust cue sources. Use only cues that are independently checkable."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                "Anonymous metacognitive cues:\n"
                f"{cue_text}\n\n"
                "Re-solve the problem independently. You may ignore any cue that is irrelevant or misleading."
                f"{RESOLVE_FORMAT}"
            ),
        },
    ]


def parse_cue_id_list(text: str) -> tuple[str, ...]:
    compact = text.strip()
    if not compact:
        return ()
    if re.sub(r"[^a-z]+", "", compact.lower()) in {"none", "no", "na"}:
        return ()
    parts = re.split(r"[,;\s]+", compact)
    return tuple(part for part in (part.strip() for part in parts) if part)


def parse_cue_resolve_output(text: str) -> ParsedCueResolve:
    parsed_answer = extract_xml_answer(text)
    return ParsedCueResolve(
        output=text,
        parsed_answer=parsed_answer,
        normalized_answer=normalize_numeric(parsed_answer),
        used_cues=parse_cue_id_list(_extract_tag(text, "used_cues")),
        ignored_cues=parse_cue_id_list(_extract_tag(text, "ignored_cues")),
        new_realization=_normalize_space(_extract_tag(text, "new_realization")),
    )


def cue_payload(cue: CueAtom) -> dict[str, Any]:
    return {
        "cue_id": cue.cue_id,
        "source_agent_index": cue.source_agent_index,
        "source_answer": cue.source_answer,
        "cue_type": cue.cue_type,
        "cue_text": cue.cue_text,
        "why_relevant": cue.why_relevant,
        "self_reported_answer_leak": cue.self_reported_answer_leak,
    }


def filtered_cue_payload(item: FilteredCue) -> dict[str, Any]:
    return {
        **cue_payload(item.cue),
        "keep": item.keep,
        "filter_reasons": list(item.reasons),
    }


def resolve_payload(item: ParsedCueResolve) -> dict[str, Any]:
    return {
        "output": item.output,
        "parsed_answer": item.parsed_answer,
        "normalized_answer": item.normalized_answer,
        "used_cues": list(item.used_cues),
        "ignored_cues": list(item.ignored_cues),
        "new_realization": item.new_realization,
    }


def row_in_scope(pool_state: str, scope: str) -> bool:
    return scope == "all" or pool_state == scope


def load_input_record_rows(path: Path, limit: int) -> tuple[list[dict[str, Any]], list[list[dict[str, Any]]]]:
    rows: list[dict[str, Any]] = []
    initial_outputs: list[list[dict[str, Any]]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            protocol = record.get("cpac") or record.get("cqg")
            if isinstance(protocol, dict) and "initial_outputs" in protocol:
                row_initial_outputs = protocol["initial_outputs"]
            else:
                mad_mm = record.get("mad_mm")
                rounds = mad_mm.get("rounds") if isinstance(mad_mm, dict) else None
                first_round = rounds[0] if isinstance(rounds, list) and rounds else None
                row_initial_outputs = first_round.get("agent_outputs") if isinstance(first_round, dict) else None
            if not isinstance(row_initial_outputs, list):
                raise SystemExit(f"input record lacks reusable initial outputs: {record.get('id')}")
            rows.append(
                {
                    "index": record.get("index", len(rows)),
                    "id": record.get("id"),
                    "question": record.get("question"),
                    "answer": record.get("gold_answer"),
                }
            )
            initial_outputs.append(row_initial_outputs)
            if limit and len(rows) >= limit:
                break
    return rows, initial_outputs


def main() -> int:
    args = parse_args()
    if args.agents < 2:
        raise SystemExit("--agents must be >= 2")
    if args.reviewers < 1:
        raise SystemExit("--reviewers must be >= 1")
    if args.cue_k < 1:
        raise SystemExit("--cue-k must be >= 1")

    work_dir = Path(args.work_dir).expanduser().resolve()
    method_key = f"mca-text-{args.pool_state_scope}"
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-{method_key}",
        work_dir,
        "output dir",
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    from vllm import LLM, SamplingParams

    if args.input_records:
        input_records_path = resolve_inside(Path(args.input_records), work_dir, "input records")
        rows, initial_by_row = load_input_record_rows(input_records_path, args.limit)
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
    resolve_sampling = SamplingParams(
        temperature=args.resolve_temperature,
        top_p=args.top_p,
        max_tokens=args.resolve_max_tokens,
        logprobs=1,
    )
    use_tqdm = not args.disable_tqdm

    if not initial_by_row:
        initial_prompts = []
        for question in questions:
            for agent_idx in range(args.agents):
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
            cue_prompts.append(
                prompt_from_messages(tokenizer, cue_extraction_prompt(question, output, cue_k=args.cue_k))
            )
            cue_owners.append((row_idx, agent_idx))

    cue_texts = (
        generate_plain_texts(llm, cue_prompts, cue_sampling, args.batch_size, use_tqdm=use_tqdm)
        if cue_prompts
        else []
    )
    cue_atoms_by_row: list[list[CueAtom]] = [[] for _ in rows]
    cue_raw_outputs_by_row: list[list[dict[str, Any]]] = [[] for _ in rows]
    for (row_idx, agent_idx), cue_output in zip(cue_owners, cue_texts):
        source_answer = initial_by_row[row_idx][agent_idx].get("parsed_answer")
        cue_atoms = parse_cue_atoms(
            cue_output,
            source_agent_index=agent_idx,
            source_answer=source_answer,
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
        filter_cues(cues, cards)
        if row_in_scope(decision.pool_state, args.pool_state_scope)
        else []
        for cues, cards, decision in zip(cue_atoms_by_row, cards_by_row, decisions)
    ]

    resolve_prompts: list[str] = []
    resolve_owners: list[int] = []
    for row_idx, (question, filtered, decision) in enumerate(zip(questions, filtered_by_row, decisions)):
        if not row_in_scope(decision.pool_state, args.pool_state_scope):
            continue
        kept = [item for item in filtered if item.keep]
        if not kept:
            continue
        for reviewer_idx in range(args.reviewers):
            resolve_prompts.append(prompt_from_messages(tokenizer, cue_resolve_prompt(question, reviewer_idx, kept)))
            resolve_owners.append(row_idx)

    resolve_flat = (
        generate_outputs(llm, resolve_prompts, resolve_sampling, args.batch_size, use_tqdm=use_tqdm)
        if resolve_prompts
        else []
    )
    resolves_by_row: list[list[ParsedCueResolve]] = [[] for _ in rows]
    for row_idx, output in zip(resolve_owners, resolve_flat):
        resolves_by_row[row_idx].append(parse_cue_resolve_output(str(output.get("output") or "")))

    records_path = output_dir / "records.jsonl"
    summary_counts: dict[str, Any] = {
        "total": len(rows),
        "scoped_cases": 0,
        "initial_majority_correct": 0,
        "final_correct": 0,
        "cue_prompt_count": len(cue_prompts),
        "cue_atoms": 0,
        "kept_cues": 0,
        "cue_coverage_cases": 0,
        "cue_resolve_cases": 0,
        "cue_resolve_outputs": len(resolve_prompts),
        "cue_uptake_reports": 0,
        "final_parse_fail": 0,
        "final_majority_ties": 0,
        "answer_changed": 0,
        "MaC_to_C": 0,
        "MaC_to_W": 0,
        "MaW_to_C": 0,
        "MaW_to_W": 0,
    }
    pool_state_counts: Counter[str] = Counter()
    filter_reason_counts: Counter[str] = Counter()
    pool_state_metrics: dict[str, Counter[str]] = {}

    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for idx, row in enumerate(rows):
            gold = row.get("answer")
            initial_answers = [output.get("parsed_answer") for output in initial_by_row[idx]]
            initial_majority, initial_tie = majority_vote(initial_answers)
            decision = decisions[idx]
            scoped = row_in_scope(decision.pool_state, args.pool_state_scope)
            pool_state_counts[decision.pool_state] += 1
            pool_metrics = pool_state_metrics.setdefault(decision.pool_state, Counter())
            pool_metrics["total"] += 1
            if scoped:
                summary_counts["scoped_cases"] += 1

            kept_cues = [item for item in filtered_by_row[idx] if item.keep]
            for item in filtered_by_row[idx]:
                if not item.keep:
                    for reason in item.reasons:
                        filter_reason_counts[reason] += 1
            summary_counts["cue_atoms"] += len(cue_atoms_by_row[idx])
            summary_counts["kept_cues"] += len(kept_cues)
            if kept_cues:
                summary_counts["cue_coverage_cases"] += 1
                pool_metrics["cue_coverage_cases"] += 1

            if resolves_by_row[idx]:
                review_answers = [resolve.parsed_answer for resolve in resolves_by_row[idx]]
                final_answer, final_tie = majority_vote(review_answers)
                summary_counts["cue_resolve_cases"] += 1
                pool_metrics["cue_resolve_cases"] += 1
            else:
                final_answer, final_tie = initial_majority, initial_tie

            used_reports = sum(1 for resolve in resolves_by_row[idx] if resolve.used_cues)
            summary_counts["cue_uptake_reports"] += used_reports

            initial_ok = is_correct(initial_majority, gold)
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
            if normalize_numeric(initial_majority) != normalize_numeric(final_answer):
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
                    "variant": "text",
                    "pool_state_scope": args.pool_state_scope,
                    "agents": args.agents,
                    "reviewers": args.reviewers,
                    "cue_k": args.cue_k,
                    "initial_outputs": initial_by_row[idx],
                    "initial_majority_answer": initial_majority,
                    "initial_majority_tie": initial_tie,
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
                    "cue_resolve_outputs": [resolve_payload(item) for item in resolves_by_row[idx]],
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
    total = max(1, len(rows))
    scoped_total = max(1, int(summary_counts["scoped_cases"]))
    cue_atoms_total = max(1, int(summary_counts["cue_atoms"]))
    resolve_outputs_total = max(1, int(summary_counts["cue_resolve_outputs"]))
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
                "cue_resolve_rate": counts["cue_resolve_cases"] / state_total,
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
        "protocol": "mca-text",
        "agents": args.agents,
        "reviewers": args.reviewers,
        "cue_k": args.cue_k,
        "pool_state_scope": args.pool_state_scope,
        "input_records": args.input_records or None,
        "temperature": args.temperature,
        "cue_temperature": args.cue_temperature,
        "resolve_temperature": args.resolve_temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": {
            **summary_counts,
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
            "cue_uptake_self_report_rate": summary_counts["cue_uptake_reports"] / resolve_outputs_total,
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
        handle.write(f"# {args.benchmark}-{args.model_key}-mca-text\n\n")
        handle.write(f"- Rows: {len(rows)}\n")
        handle.write(f"- Pool-state scope: {args.pool_state_scope}\n")
        handle.write(f"- Initial majority accuracy: {summary['metrics']['initial_majority_accuracy']:.4f}\n")
        handle.write(f"- Final accuracy: {summary['metrics']['final_accuracy']:.4f}\n")
        handle.write(f"- Cue coverage rate: {summary['metrics']['cue_coverage_rate']:.4f}\n")
        handle.write(f"- Cue uptake self-report rate: {summary['metrics']['cue_uptake_self_report_rate']:.4f}\n")
        handle.write(f"- Wrong-majority recovery rate: {summary['metrics']['wrong_majority_recovery_rate']:.4f}\n")
        handle.write(f"- Correct-majority harm rate: {summary['metrics']['correct_majority_harm_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
