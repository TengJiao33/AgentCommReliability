#!/usr/bin/env python3
"""Run MAD-M2-style memory masking on prepared JSONL benchmarks."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

from run_basic_mad import (
    find_answer_text,
    is_correct,
    load_rows,
    majority_vote,
    normalize_numeric,
    prompt_from_messages,
    resolve_inside,
)


COT_PROMPT = "Please solve the problem step by step."

RESPONSE_FORMAT = (
    "\n\n### Response format (MUST be strictly followed) "
    "(DO NOT include any other formats except for the given XML format): \n"
    "<think>YOUR THINKING HERE</think>\n"
    "<answer>YOUR FINAL ANSWER ONLY, NO OTHER TEXT</answer>."
)

DEBATE_PROMPT = """These are the potential solutions to the problem:
{context}
Use the potential solutions as additional information for the following question.

Question:{question}
Please think step by step and solve the problem."""

PRUNE_PROMPT = """Evaluate the given solutions based on the question. ** Your response MUST end with the following format: <label>YES</label> or <label>NO</label> or <label>NOT SURE</label>. ** Return YES if the solution is completely correct, NO if any part of the solution is incorrect, and NOT SURE if you are unsure.

Question: {question}

Solutions: {solution}"""


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
    parser.add_argument("--rounds", type=int, default=2, help="Total debate rounds, including the initial CoT round.")
    parser.add_argument("--prune-strategy", choices=("naive", "subjective", "objective"), default="subjective")
    parser.add_argument("--strict", action="store_true", help="Treat NOT SURE as masked for subjective pruning.")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-model-len", type=int, default=24064)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.85)
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    return parser.parse_args()


def prepare_question(question: str, benchmark: str) -> str:
    if benchmark in {"math", "math500", "aime24", "aime25"}:
        return "### Please provide your final answer in the format of \\boxed{} format. ###\n" + question
    if benchmark == "mmlu_pro":
        return "### Please DIRECTLY provide the option letter in your final answer. ###\n" + question
    return question


def cot_prompt(question: str) -> str:
    return f"{question}\n{COT_PROMPT}{RESPONSE_FORMAT}"


def debate_prompt(question: str, contexts: list[dict[str, Any]]) -> str:
    if not contexts:
        return cot_prompt(question)
    context_text = "\n".join(str(memory_payload(context)) for context in contexts)
    return DEBATE_PROMPT.format(question=question, context=context_text) + RESPONSE_FORMAT


def prune_prompt(question: str, context: dict[str, Any]) -> str:
    return PRUNE_PROMPT.format(question=question, solution=str(memory_payload(context)))


def memory_payload(context: dict[str, Any]) -> dict[str, Any]:
    parsed = context.get("parsed")
    if isinstance(parsed, dict):
        return parsed
    return {
        "think": context.get("output", ""),
        "answer": context.get("parsed_answer"),
    }


def extract_xml_answer(text: str) -> str | None:
    matches = re.findall(r"<answer>(.*?)</answer>", text, flags=re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[-1].strip()
    return find_answer_text(text)


def extract_label(text: str) -> str:
    match = re.search(r"<label>(.*?)</label>", text, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return "not sure"
    label = match.group(1).strip().lower()
    label = re.sub(r"[^a-z ]", "", label)
    if label in {"yes", "no", "not sure"}:
        return label
    if "yes" in label:
        return "yes"
    if "no" in label:
        return "no"
    return "not sure"


def selected_token_logprobs(output: Any) -> list[float]:
    token_ids = list(getattr(output, "token_ids", []) or [])
    token_logprobs = list(getattr(output, "logprobs", []) or [])
    values: list[float] = []
    for token_id, logprob_map in zip(token_ids, token_logprobs):
        selected = logprob_map.get(token_id) if isinstance(logprob_map, dict) else None
        if selected is None and isinstance(logprob_map, dict):
            selected = next((item for item in logprob_map.values() if getattr(item, "rank", None) == 1), None)
        if selected is not None:
            value = getattr(selected, "logprob", None)
            if value is not None and value != float("-inf"):
                values.append(float(value))
    return values


def sequence_score(logprobs: list[float]) -> float:
    if not logprobs:
        return float("-inf")
    return math.exp(sum(logprobs) / len(logprobs))


def generate_outputs(llm: Any, prompts: list[str], sampling_params: Any, batch_size: int) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for start in range(0, len(prompts), batch_size):
        batch = prompts[start : start + batch_size]
        for result in llm.generate(batch, sampling_params, use_tqdm=True):
            completion = result.outputs[0]
            logprobs = selected_token_logprobs(completion)
            text = completion.text
            answer = extract_xml_answer(text)
            outputs.append(
                {
                    "output": text,
                    "parsed": {
                        "think": text,
                        "answer": answer,
                    },
                    "parsed_answer": answer,
                    "normalized_answer": normalize_numeric(answer),
                    "mean_selected_logprob": (sum(logprobs) / len(logprobs)) if logprobs else None,
                    "sequence_score": sequence_score(logprobs),
                    "output_tokens": len(getattr(completion, "token_ids", []) or []),
                    "prompt_tokens": len(getattr(result, "prompt_token_ids", []) or []),
                }
            )
    return outputs


def generate_plain_texts(llm: Any, prompts: list[str], sampling_params: Any, batch_size: int) -> list[str]:
    texts: list[str] = []
    for start in range(0, len(prompts), batch_size):
        batch = prompts[start : start + batch_size]
        for result in llm.generate(batch, sampling_params, use_tqdm=True):
            texts.append(result.outputs[0].text)
    return texts


def reshape(flat: list[Any], rows: int, width: int) -> list[list[Any]]:
    return [flat[i * width : (i + 1) * width] for i in range(rows)]


def subjective_mask(
    llm: Any,
    tokenizer: Any,
    questions: list[str],
    contexts_by_row: list[list[dict[str, Any]]],
    sampling_params: Any,
    batch_size: int,
    strict: bool,
) -> tuple[list[list[dict[str, Any]]], list[dict[str, Any]]]:
    prompts: list[str] = []
    owners: list[tuple[int, int]] = []
    for row_idx, (question, contexts) in enumerate(zip(questions, contexts_by_row)):
        for memory_idx, context in enumerate(contexts):
            prompts.append(prompt_from_messages(tokenizer, [{"role": "user", "content": prune_prompt(question, context)}]))
            owners.append((row_idx, memory_idx))

    label_outputs = generate_plain_texts(llm, prompts, sampling_params, batch_size)
    masks_by_row = [
        {
            "strategy": "subjective",
            "strict": strict,
            "labels": [],
            "mask": [],
            "raw_outputs": [],
        }
        for _ in contexts_by_row
    ]
    selected_by_row: list[list[dict[str, Any]]] = [[] for _ in contexts_by_row]

    for (row_idx, memory_idx), output in zip(owners, label_outputs):
        label = extract_label(output)
        keep = label == "yes" or (label == "not sure" and not strict)
        masks_by_row[row_idx]["labels"].append(label)
        masks_by_row[row_idx]["mask"].append(keep)
        masks_by_row[row_idx]["raw_outputs"].append(output)
        if keep:
            selected_by_row[row_idx].append(contexts_by_row[row_idx][memory_idx])

    return selected_by_row, masks_by_row


def objective_mask(contexts_by_row: list[list[dict[str, Any]]]) -> tuple[list[list[dict[str, Any]]], list[dict[str, Any]]]:
    selected_by_row: list[list[dict[str, Any]]] = []
    masks_by_row: list[dict[str, Any]] = []
    for contexts in contexts_by_row:
        scores = [float(context.get("sequence_score", float("-inf"))) for context in contexts]
        sorted_scores = sorted(scores, reverse=True)
        threshold = sorted_scores[len(sorted_scores) // 2] if sorted_scores else float("inf")
        mask = [score > threshold for score in scores]
        selected = [context for context, keep in zip(contexts, mask) if keep]
        selected_by_row.append(selected)
        masks_by_row.append(
            {
                "strategy": "objective",
                "score_name": "exp(mean selected-token logprob)",
                "scores": scores,
                "threshold": threshold,
                "mask": mask,
            }
        )
    return selected_by_row, masks_by_row


def naive_mask(contexts_by_row: list[list[dict[str, Any]]]) -> tuple[list[list[dict[str, Any]]], list[dict[str, Any]]]:
    masks_by_row = [
        {
            "strategy": "naive",
            "mask": [True for _ in contexts],
        }
        for contexts in contexts_by_row
    ]
    return contexts_by_row, masks_by_row


def answer_list(outputs: list[dict[str, Any]]) -> list[str | None]:
    return [output.get("parsed_answer") for output in outputs]


def label_counts(mask_records: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in mask_records:
        for label in record.get("labels", []):
            counts[str(label)] += 1
    return dict(sorted(counts.items()))


def main() -> int:
    args = parse_args()
    if args.agents < 1:
        raise SystemExit("--agents must be >= 1")
    if args.rounds < 1:
        raise SystemExit("--rounds must be >= 1")

    work_dir = Path(args.work_dir).expanduser().resolve()
    data_path = resolve_inside(
        work_dir / "data" / "benchmarks" / args.benchmark / args.split / "canonical.jsonl",
        work_dir,
        "benchmark path",
    )
    method_key = args.prune_strategy + ("-strict" if args.strict and args.prune_strategy == "subjective" else "")
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

    sampling = SamplingParams(
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        logprobs=1,
    )
    label_sampling = SamplingParams(
        temperature=0.0,
        top_p=1.0,
        max_tokens=32,
    )

    initial_prompts = []
    for question in questions:
        rendered = prompt_from_messages(tokenizer, [{"role": "user", "content": cot_prompt(question)}])
        for _agent_idx in range(args.agents):
            initial_prompts.append(rendered)
    initial_flat = generate_outputs(llm, initial_prompts, sampling, args.batch_size)
    current_by_row = reshape(initial_flat, len(rows), args.agents)
    rounds_by_row: list[list[dict[str, Any]]] = [
        [
            {
                "round": 1,
                "agent_outputs": current_by_row[row_idx],
                "majority_answer": majority_vote(answer_list(current_by_row[row_idx]))[0],
                "majority_tie": majority_vote(answer_list(current_by_row[row_idx]))[1],
            }
        ]
        for row_idx in range(len(rows))
    ]

    all_mask_records: list[list[dict[str, Any]]] = [[] for _ in rows]
    for round_idx in range(2, args.rounds + 1):
        if args.prune_strategy == "subjective":
            selected_by_row, masks_by_row = subjective_mask(
                llm,
                tokenizer,
                questions,
                current_by_row,
                label_sampling,
                args.batch_size,
                args.strict,
            )
        elif args.prune_strategy == "objective":
            selected_by_row, masks_by_row = objective_mask(current_by_row)
        else:
            selected_by_row, masks_by_row = naive_mask(current_by_row)

        debate_prompts = [
            prompt_from_messages(tokenizer, [{"role": "user", "content": debate_prompt(question, contexts)}])
            for question, contexts in zip(questions, selected_by_row)
        ]
        flat_prompts = []
        for prompt in debate_prompts:
            for _agent_idx in range(args.agents):
                flat_prompts.append(prompt)
        revised_flat = generate_outputs(llm, flat_prompts, sampling, args.batch_size)
        current_by_row = reshape(revised_flat, len(rows), args.agents)

        for row_idx, mask_record in enumerate(masks_by_row):
            mask_record = {
                **mask_record,
                "round": round_idx,
                "retained_count": len(selected_by_row[row_idx]),
                "total_memories": len(mask_record.get("mask", [])),
            }
            all_mask_records[row_idx].append(mask_record)
            majority_answer, tied = majority_vote(answer_list(current_by_row[row_idx]))
            rounds_by_row[row_idx].append(
                {
                    "round": round_idx,
                    "memory_mask": mask_record,
                    "agent_outputs": current_by_row[row_idx],
                    "majority_answer": majority_answer,
                    "majority_tie": tied,
                }
            )

    records_path = output_dir / "records.jsonl"
    summary_counts = {
        "total": len(rows),
        "initial_majority_correct": 0,
        "final_correct": 0,
        "final_parse_fail": 0,
        "final_majority_ties": 0,
        "retained_memories": 0,
        "total_mask_decisions": 0,
    }
    agent_final_correct = [0 for _ in range(args.agents)]

    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for idx, row in enumerate(rows):
            gold = row.get("answer")
            initial_answer = rounds_by_row[idx][0]["majority_answer"]
            final_round = rounds_by_row[idx][-1]
            final_answers = answer_list(final_round["agent_outputs"])
            final_answer = final_round["majority_answer"]
            final_ok = is_correct(final_answer, gold)
            if is_correct(initial_answer, gold):
                summary_counts["initial_majority_correct"] += 1
            if final_ok:
                summary_counts["final_correct"] += 1
            if final_answer is None:
                summary_counts["final_parse_fail"] += 1
            if final_round["majority_tie"]:
                summary_counts["final_majority_ties"] += 1
            for mask_record in all_mask_records[idx]:
                summary_counts["retained_memories"] += int(mask_record.get("retained_count", 0))
                summary_counts["total_mask_decisions"] += int(mask_record.get("total_memories", 0))
            for agent_idx, answer in enumerate(final_answers):
                if is_correct(answer, gold):
                    agent_final_correct[agent_idx] += 1

            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row.get("index", idx),
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "mad_mm": {
                    "prune_strategy": args.prune_strategy,
                    "strict": args.strict,
                    "agents": args.agents,
                    "rounds": rounds_by_row[idx],
                    "final_majority_answer": final_answer,
                    "final_normalized_answer": normalize_numeric(final_answer),
                    "correct": final_ok,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    elapsed = time.time() - started_at
    total = max(1, len(rows))
    mask_total = max(1, summary_counts["total_mask_decisions"])
    mask_records_flat = [record for records in all_mask_records for record in records]
    summary = {
        "run_id": args.run_id,
        "model_key": args.model_key,
        "model_path": str(model_path),
        "benchmark": args.benchmark,
        "split": args.split,
        "rows": len(rows),
        "agents": args.agents,
        "rounds": args.rounds,
        "prune_strategy": args.prune_strategy,
        "strict": args.strict,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": summary_counts,
        "subjective_label_counts": label_counts(mask_records_flat),
        "metrics": {
            "initial_majority_accuracy": summary_counts["initial_majority_correct"] / total,
            "final_accuracy": summary_counts["final_correct"] / total,
            "agent_final_accuracy": [count / total for count in agent_final_correct],
            "final_parse_fail_rate": summary_counts["final_parse_fail"] / total,
            "final_majority_tie_rate": summary_counts["final_majority_ties"] / total,
            "memory_retention_rate": summary_counts["retained_memories"] / mask_total,
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
        handle.write(f"- Memory retention rate: {summary['metrics']['memory_retention_rate']:.4f}\n")
        handle.write(f"- Final tie rate: {summary['metrics']['final_majority_tie_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
