#!/usr/bin/env python3
"""Run Consensus Quarantine Gate on prepared JSONL benchmarks.

The protocol treats an apparent majority as a provisional hypothesis when the
initial answers diverge. It hides vote counts, gives minority candidates one
evidence-based appeal pass, and asks blind reviewers to re-solve from anonymous
candidate cards before final aggregation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import string
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
from run_mad_mm import extract_xml_answer, prepare_question, selected_token_logprobs, sequence_score


RESPONSE_FORMAT = (
    "\n\nEnd with exactly one XML tag named answer. "
    "Put only the final answer between the opening and closing answer tags."
)

APPEAL_FORMAT = (
    "\n\nReply with exactly one XML tag named appeal. "
    "Put only the concrete objection inside the tag. "
    "If no concrete objection exists, put exactly NO_VALID_APPEAL inside the tag."
)


@dataclass(frozen=True)
class CandidateCard:
    card_id: str
    parsed_answer: str | None
    normalized_answer: str | None
    representative_output: str
    source_indices: tuple[int, ...]

    @property
    def supporter_count(self) -> int:
        return len(self.source_indices)


@dataclass(frozen=True)
class QuarantineDecision:
    should_quarantine: bool
    reason: str
    majority_answer: str | None
    majority_count: int
    unique_answer_count: int
    duplicate_reasoning_score: float


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
    parser.add_argument(
        "--quarantine-mode",
        choices=("divergent", "risk", "always", "never"),
        default="divergent",
        help=(
            "divergent: quarantine any non-unanimous majority; "
            "risk: require divergence plus a shallow risk signal; "
            "always/never: force behavior for ablations."
        ),
    )
    parser.add_argument("--overlap-threshold", type=float, default=0.72)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--appeal-temperature", type=float, default=0.2)
    parser.add_argument("--review-temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--appeal-max-tokens", type=int, default=512)
    parser.add_argument("--review-max-tokens", type=int, default=1536)
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


def independent_prompt(question: str, agent_index: int) -> list[dict[str, str]]:
    role = ROLE_NAMES[agent_index % len(ROLE_NAMES)]
    return [
        {
            "role": "system",
            "content": (
                f"You are agent {agent_index + 1}, a {role}. Solve independently. "
                "Do not assume other agents agree with you. Show concise reasoning."
            ),
        },
        {"role": "user", "content": question + RESPONSE_FORMAT},
    ]


def appeal_prompt(question: str, consensus: CandidateCard, challenger: CandidateCard) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are an anonymous challenger in a multi-agent reasoning audit. "
                "Your job is not to be contrarian; make an appeal only if there is a concrete flaw, "
                "missing constraint, arithmetic error, or stronger derivation."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                "A provisional consensus has been quarantined. Vote counts and agent identities are hidden.\n\n"
                f"Consensus candidate answer:\n{consensus.parsed_answer}\n\n"
                f"Consensus candidate reasoning:\n{consensus.representative_output}\n\n"
                f"Alternative candidate answer:\n{challenger.parsed_answer}\n\n"
                f"Alternative candidate reasoning:\n{challenger.representative_output}\n\n"
                "State the strongest concrete reason the alternative should remain live. "
                "If there is no concrete reason, write NO VALID APPEAL."
                f"{APPEAL_FORMAT}"
            ),
        },
    ]


def review_prompt(
    question: str,
    reviewer_index: int,
    cards: list[CandidateCard],
    appeals: list[dict[str, Any]],
) -> list[dict[str, str]]:
    card_text = "\n\n".join(
        (
            f"Card {card.card_id}\n"
            f"Proposed answer: {card.parsed_answer}\n"
            f"Reasoning:\n{card.representative_output}"
        )
        for card in cards
    )
    appeal_text = "\n\n".join(
        f"Appeal against provisional consensus from Card {item['challenger_card_id']}:\n{item['appeal_output']}"
        for item in appeals
    )
    if not appeal_text:
        appeal_text = "No challenger produced a concrete appeal."
    role = ROLE_NAMES[reviewer_index % len(ROLE_NAMES)]
    return [
        {
            "role": "system",
            "content": (
                f"You are blind reviewer {reviewer_index + 1}, a {role}. "
                "You are not told how many agents supported each card. "
                "Do not treat consensus, confidence, or repetition as evidence; judge only reasoning quality."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                "Anonymous candidate cards:\n"
                f"{card_text}\n\n"
                "Minority appeals:\n"
                f"{appeal_text}\n\n"
                "Re-solve the problem from scratch. Identify any invalid card logic, then choose the best answer."
                f"{RESPONSE_FORMAT}"
            ),
        },
    ]


def extract_appeal(text: str) -> str:
    match = re.search(r"<appeal>(.*?)</appeal>", text, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return text.strip()
    return match.group(1).strip()


def is_valid_appeal_text(text: str) -> bool:
    compact = re.sub(r"[^a-z0-9]+", "", text.lower())
    if compact in {"", "novalidappeal", "none", "noconcreteobjection"}:
        return False
    if "novalidappeal" in compact:
        return False
    if compact in {"yourconcreteobjection", "concreteobjection"}:
        return False
    return len(_word_set(text)) >= 4


def _word_set(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9]+", text.lower()))


def jaccard_similarity(left: str, right: str) -> float:
    left_words = _word_set(left)
    right_words = _word_set(right)
    if not left_words or not right_words:
        return 0.0
    return len(left_words & right_words) / len(left_words | right_words)


def duplicate_reasoning_score(outputs: list[str]) -> float:
    if len(outputs) < 2:
        return 0.0
    scores: list[float] = []
    for left_idx in range(len(outputs)):
        for right_idx in range(left_idx + 1, len(outputs)):
            scores.append(jaccard_similarity(outputs[left_idx], outputs[right_idx]))
    return sum(scores) / len(scores) if scores else 0.0


def build_candidate_cards(agent_outputs: list[dict[str, Any]]) -> list[CandidateCard]:
    grouped: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    order: list[str] = []
    for agent_idx, output in enumerate(agent_outputs):
        normalized = output.get("normalized_answer") or normalize_numeric(output.get("parsed_answer"))
        if normalized is None:
            continue
        if normalized not in grouped:
            grouped[normalized] = []
            order.append(normalized)
        grouped[normalized].append((agent_idx, output))

    cards: list[CandidateCard] = []
    for card_idx, normalized in enumerate(order):
        members = grouped[normalized]
        representative_idx, representative = min(
            members,
            key=lambda item: len(str(item[1].get("output") or "")),
        )
        card_id = string.ascii_uppercase[card_idx] if card_idx < 26 else f"C{card_idx + 1}"
        cards.append(
            CandidateCard(
                card_id=card_id,
                parsed_answer=representative.get("parsed_answer"),
                normalized_answer=normalized,
                representative_output=str(representative.get("output") or ""),
                source_indices=tuple(idx for idx, _output in members),
            )
        )
        if representative_idx not in cards[-1].source_indices:
            raise AssertionError("representative source lost during card construction")
    return cards


def analyze_quarantine(
    agent_outputs: list[dict[str, Any]],
    cards: list[CandidateCard],
    mode: str,
    overlap_threshold: float,
) -> QuarantineDecision:
    normalized_answers = [card.normalized_answer for card in cards for _ in card.source_indices]
    counts = Counter(answer for answer in normalized_answers if answer is not None)
    if not counts:
        return QuarantineDecision(False, "no_parseable_initial_answer", None, 0, 0, 0.0)

    majority_answer, tied = majority_vote([output.get("parsed_answer") for output in agent_outputs])
    majority_count = counts.get(majority_answer, 0) if majority_answer is not None else 0
    majority_outputs = [
        str(agent_outputs[idx].get("output") or "")
        for card in cards
        if card.normalized_answer == majority_answer
        for idx in card.source_indices
    ]
    overlap = duplicate_reasoning_score(majority_outputs)
    unique_answer_count = len(counts)

    if tied:
        return QuarantineDecision(False, "initial_vote_tie", majority_answer, majority_count, unique_answer_count, overlap)
    if mode == "never":
        return QuarantineDecision(False, "mode_never", majority_answer, majority_count, unique_answer_count, overlap)
    if unique_answer_count < 2:
        return QuarantineDecision(False, "unanimous_or_single_answer", majority_answer, majority_count, unique_answer_count, overlap)
    if mode == "always":
        return QuarantineDecision(True, "mode_always_with_divergence", majority_answer, majority_count, unique_answer_count, overlap)
    if mode == "divergent":
        return QuarantineDecision(True, "non_unanimous_majority", majority_answer, majority_count, unique_answer_count, overlap)
    if mode == "risk":
        if majority_count < len(agent_outputs):
            return QuarantineDecision(True, "non_unanimous_majority", majority_answer, majority_count, unique_answer_count, overlap)
        if overlap >= overlap_threshold:
            return QuarantineDecision(True, "high_majority_reasoning_overlap", majority_answer, majority_count, unique_answer_count, overlap)
        return QuarantineDecision(False, "no_risk_signal", majority_answer, majority_count, unique_answer_count, overlap)
    raise ValueError(f"unknown quarantine mode: {mode}")


def generate_outputs(
    llm: Any,
    prompts: list[str],
    sampling_params: Any,
    batch_size: int,
    *,
    use_tqdm: bool,
) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for start in range(0, len(prompts), batch_size):
        batch = prompts[start : start + batch_size]
        for result in llm.generate(batch, sampling_params, use_tqdm=use_tqdm):
            completion = result.outputs[0]
            logprobs = selected_token_logprobs(completion)
            text = completion.text
            answer = extract_xml_answer(text)
            outputs.append(
                {
                    "output": text,
                    "parsed_answer": answer,
                    "normalized_answer": normalize_numeric(answer),
                    "mean_selected_logprob": (sum(logprobs) / len(logprobs)) if logprobs else None,
                    "sequence_score": sequence_score(logprobs),
                    "output_tokens": len(getattr(completion, "token_ids", []) or []),
                    "prompt_tokens": len(getattr(result, "prompt_token_ids", []) or []),
                }
            )
    return outputs


def generate_plain_texts(
    llm: Any,
    prompts: list[str],
    sampling_params: Any,
    batch_size: int,
    *,
    use_tqdm: bool,
) -> list[str]:
    texts: list[str] = []
    for start in range(0, len(prompts), batch_size):
        batch = prompts[start : start + batch_size]
        for result in llm.generate(batch, sampling_params, use_tqdm=use_tqdm):
            texts.append(result.outputs[0].text)
    return texts


def reshape(flat: list[Any], rows: int, width: int) -> list[list[Any]]:
    return [flat[i * width : (i + 1) * width] for i in range(rows)]


def transition_label(initial_correct: bool, final_correct: bool) -> str:
    if initial_correct and final_correct:
        return "MaC_to_C"
    if initial_correct and not final_correct:
        return "MaC_to_W"
    if not initial_correct and final_correct:
        return "MaW_to_C"
    return "MaW_to_W"


def main() -> int:
    args = parse_args()
    if args.agents < 2:
        raise SystemExit("--agents must be >= 2")
    if args.reviewers < 1:
        raise SystemExit("--reviewers must be >= 1")

    work_dir = Path(args.work_dir).expanduser().resolve()
    data_path = resolve_inside(
        work_dir / "data" / "benchmarks" / args.benchmark / args.split / "canonical.jsonl",
        work_dir,
        "benchmark path",
    )
    method_key = f"cqg-{args.quarantine_mode}"
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-{method_key}",
        work_dir,
        "output dir",
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    from vllm import LLM, SamplingParams

    rows = load_rows(data_path, args.limit)
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
    appeal_sampling = SamplingParams(
        temperature=args.appeal_temperature,
        top_p=args.top_p,
        max_tokens=args.appeal_max_tokens,
    )
    review_sampling = SamplingParams(
        temperature=args.review_temperature,
        top_p=args.top_p,
        max_tokens=args.review_max_tokens,
        logprobs=1,
    )
    use_tqdm = not args.disable_tqdm

    initial_prompts = []
    for question in questions:
        for agent_idx in range(args.agents):
            initial_prompts.append(prompt_from_messages(tokenizer, independent_prompt(question, agent_idx)))
    initial_flat = generate_outputs(llm, initial_prompts, initial_sampling, args.batch_size, use_tqdm=use_tqdm)
    initial_by_row = reshape(initial_flat, len(rows), args.agents)

    cards_by_row = [build_candidate_cards(outputs) for outputs in initial_by_row]
    decisions = [
        analyze_quarantine(outputs, cards, args.quarantine_mode, args.overlap_threshold)
        for outputs, cards in zip(initial_by_row, cards_by_row)
    ]

    appeal_prompts: list[str] = []
    appeal_owners: list[tuple[int, str]] = []
    for row_idx, (question, cards, decision) in enumerate(zip(questions, cards_by_row, decisions)):
        if not decision.should_quarantine or decision.majority_answer is None:
            continue
        consensus = next((card for card in cards if card.normalized_answer == decision.majority_answer), None)
        if consensus is None:
            continue
        for challenger in cards:
            if challenger.normalized_answer == decision.majority_answer:
                continue
            appeal_prompts.append(prompt_from_messages(tokenizer, appeal_prompt(question, consensus, challenger)))
            appeal_owners.append((row_idx, challenger.card_id))

    appeal_texts = (
        generate_plain_texts(llm, appeal_prompts, appeal_sampling, args.batch_size, use_tqdm=use_tqdm)
        if appeal_prompts
        else []
    )
    appeals_by_row: list[list[dict[str, Any]]] = [[] for _ in rows]
    for (row_idx, challenger_card_id), appeal_output in zip(appeal_owners, appeal_texts):
        appeals_by_row[row_idx].append(
            {
                "challenger_card_id": challenger_card_id,
                "appeal_output": appeal_output,
                "parsed_appeal": extract_appeal(appeal_output),
                "valid_appeal": is_valid_appeal_text(extract_appeal(appeal_output)),
            }
        )

    review_prompts: list[str] = []
    review_owners: list[int] = []
    for row_idx, (question, cards, decision) in enumerate(zip(questions, cards_by_row, decisions)):
        if not decision.should_quarantine:
            continue
        valid_appeals = [item for item in appeals_by_row[row_idx] if item["valid_appeal"]]
        for reviewer_idx in range(args.reviewers):
            review_prompts.append(
                prompt_from_messages(tokenizer, review_prompt(question, reviewer_idx, cards, valid_appeals))
            )
            review_owners.append(row_idx)

    review_flat = (
        generate_outputs(llm, review_prompts, review_sampling, args.batch_size, use_tqdm=use_tqdm)
        if review_prompts
        else []
    )
    reviews_by_row: list[list[dict[str, Any]]] = [[] for _ in rows]
    for row_idx, review_output in zip(review_owners, review_flat):
        reviews_by_row[row_idx].append(review_output)

    records_path = output_dir / "records.jsonl"
    summary_counts = {
        "total": len(rows),
        "initial_majority_correct": 0,
        "final_correct": 0,
        "quarantined_cases": 0,
        "appeal_prompts": len(appeal_prompts),
        "valid_appeals": 0,
        "final_parse_fail": 0,
        "final_majority_ties": 0,
        "answer_changed": 0,
        "MaC_to_C": 0,
        "MaC_to_W": 0,
        "MaW_to_C": 0,
        "MaW_to_W": 0,
    }

    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for idx, row in enumerate(rows):
            gold = row.get("answer")
            initial_answers = [output.get("parsed_answer") for output in initial_by_row[idx]]
            initial_majority, initial_tie = majority_vote(initial_answers)
            if decisions[idx].should_quarantine and reviews_by_row[idx]:
                review_answers = [output.get("parsed_answer") for output in reviews_by_row[idx]]
                final_answer, final_tie = majority_vote(review_answers)
            else:
                final_answer = initial_majority
                final_tie = initial_tie
            initial_ok = is_correct(initial_majority, gold)
            final_ok = is_correct(final_answer, gold)
            transition = transition_label(initial_ok, final_ok)

            if initial_ok:
                summary_counts["initial_majority_correct"] += 1
            if final_ok:
                summary_counts["final_correct"] += 1
            if decisions[idx].should_quarantine:
                summary_counts["quarantined_cases"] += 1
            if normalize_numeric(final_answer) is None:
                summary_counts["final_parse_fail"] += 1
            if final_tie:
                summary_counts["final_majority_ties"] += 1
            if normalize_numeric(initial_majority) != normalize_numeric(final_answer):
                summary_counts["answer_changed"] += 1
            summary_counts[transition] += 1
            summary_counts["valid_appeals"] += sum(1 for item in appeals_by_row[idx] if item["valid_appeal"])

            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row.get("index", idx),
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "cqg": {
                    "quarantine_mode": args.quarantine_mode,
                    "agents": args.agents,
                    "reviewers": args.reviewers,
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
                    "quarantine_decision": {
                        "should_quarantine": decisions[idx].should_quarantine,
                        "reason": decisions[idx].reason,
                        "majority_answer": decisions[idx].majority_answer,
                        "majority_count": decisions[idx].majority_count,
                        "unique_answer_count": decisions[idx].unique_answer_count,
                        "duplicate_reasoning_score": decisions[idx].duplicate_reasoning_score,
                    },
                    "appeals": appeals_by_row[idx],
                    "review_outputs": reviews_by_row[idx],
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
    quarantined = max(1, summary_counts["quarantined_cases"])
    initial_wrong = max(1, summary_counts["MaW_to_C"] + summary_counts["MaW_to_W"])
    initial_correct = max(1, summary_counts["MaC_to_C"] + summary_counts["MaC_to_W"])
    summary = {
        "run_id": args.run_id,
        "model_key": args.model_key,
        "model_path": str(model_path),
        "benchmark": args.benchmark,
        "split": args.split,
        "rows": len(rows),
        "agents": args.agents,
        "reviewers": args.reviewers,
        "quarantine_mode": args.quarantine_mode,
        "temperature": args.temperature,
        "appeal_temperature": args.appeal_temperature,
        "review_temperature": args.review_temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": summary_counts,
        "metrics": {
            "initial_majority_accuracy": summary_counts["initial_majority_correct"] / total,
            "final_accuracy": summary_counts["final_correct"] / total,
            "quarantine_rate": summary_counts["quarantined_cases"] / total,
            "appeals_per_quarantined_case": summary_counts["appeal_prompts"] / quarantined,
            "valid_appeal_rate": summary_counts["valid_appeals"] / max(1, summary_counts["appeal_prompts"]),
            "answer_change_rate": summary_counts["answer_changed"] / total,
            "wrong_majority_recovery_rate": summary_counts["MaW_to_C"] / initial_wrong,
            "correct_majority_preservation_rate": summary_counts["MaC_to_C"] / initial_correct,
            "final_parse_fail_rate": summary_counts["final_parse_fail"] / total,
            "final_majority_tie_rate": summary_counts["final_majority_ties"] / total,
        },
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {args.benchmark}-{args.model_key}-{method_key}\n\n")
        handle.write(f"- Rows: {len(rows)}\n")
        handle.write(f"- Initial majority accuracy: {summary['metrics']['initial_majority_accuracy']:.4f}\n")
        handle.write(f"- Final accuracy: {summary['metrics']['final_accuracy']:.4f}\n")
        handle.write(f"- Quarantine rate: {summary['metrics']['quarantine_rate']:.4f}\n")
        handle.write(f"- Wrong-majority recovery rate: {summary['metrics']['wrong_majority_recovery_rate']:.4f}\n")
        handle.write(
            f"- Correct-majority preservation rate: "
            f"{summary['metrics']['correct_majority_preservation_rate']:.4f}\n"
        )
        handle.write(f"- Final tie rate: {summary['metrics']['final_majority_tie_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
