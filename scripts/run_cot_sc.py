#!/usr/bin/env python3
"""Run CoT and self-consistency baselines on prepared JSONL benchmarks."""

from __future__ import annotations

import argparse
import json
import os
import time
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default=os.environ.get("ACR_WORK_DIR", os.getcwd()))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--split", required=True)
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--gpu-id", default=os.environ.get("CUDA_VISIBLE_DEVICES", "0"))
    parser.add_argument("--cot-temperature", type=float, default=0.0)
    parser.add_argument("--sc-temperature", type=float, default=0.7)
    parser.add_argument("--sc-samples", type=int, default=16)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-model-len", type=int, default=4096)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.82)
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    return parser.parse_args()


def cot_prompt(question: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You solve competition math problems. Think step by step, keep the reasoning concise, "
                "and end with exactly 'Final answer: <answer>'."
            ),
        },
        {"role": "user", "content": question},
    ]


def generate_one_texts(llm: Any, prompts: list[str], sampling_params: Any, batch_size: int) -> list[str]:
    outputs: list[str] = []
    for start in range(0, len(prompts), batch_size):
        batch = prompts[start : start + batch_size]
        for result in llm.generate(batch, sampling_params, use_tqdm=True):
            outputs.append(result.outputs[0].text)
    return outputs


def generate_n_texts(llm: Any, prompts: list[str], sampling_params: Any, batch_size: int) -> list[list[str]]:
    outputs: list[list[str]] = []
    for start in range(0, len(prompts), batch_size):
        batch = prompts[start : start + batch_size]
        for result in llm.generate(batch, sampling_params, use_tqdm=True):
            outputs.append([item.text for item in result.outputs])
    return outputs


def main() -> int:
    args = parse_args()
    if args.sc_samples < 1:
        raise SystemExit("--sc-samples must be >= 1")

    work_dir = Path(args.work_dir).expanduser().resolve()
    data_path = resolve_inside(
        work_dir / "data" / "benchmarks" / args.benchmark / args.split / "canonical.jsonl",
        work_dir,
        "benchmark path",
    )
    output_dir = resolve_inside(work_dir / "experiments" / args.run_id / args.model_key, work_dir, "output dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    from vllm import LLM, SamplingParams

    rows = load_rows(data_path, args.limit)
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

    cot_sampling = SamplingParams(
        temperature=args.cot_temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
    )
    sc_sampling = SamplingParams(
        n=args.sc_samples,
        temperature=args.sc_temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
    )

    questions = [str(row.get("question") or "") for row in rows]
    prompts = [prompt_from_messages(tokenizer, cot_prompt(question)) for question in questions]
    cot_outputs = generate_one_texts(llm, prompts, cot_sampling, args.batch_size)
    sc_outputs = generate_n_texts(llm, prompts, sc_sampling, args.batch_size)

    records_path = output_dir / "records.jsonl"
    summary_counts = {
        "total": len(rows),
        "cot_correct": 0,
        "cot_parse_fail": 0,
        "sc_correct": 0,
        "sc_parse_fail": 0,
        "sc_sample_parse_fail": 0,
        "sc_total_samples": len(rows) * args.sc_samples,
        "sc_majority_ties": 0,
    }

    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for idx, row in enumerate(rows):
            gold = row.get("answer")
            cot_answer = find_answer_text(cot_outputs[idx])
            cot_ok = is_correct(cot_answer, gold)
            sc_answers = [find_answer_text(text) for text in sc_outputs[idx]]
            sc_normalized_answers = [normalize_numeric(answer) for answer in sc_answers]
            sc_majority_answer, tied = majority_vote(sc_answers)
            sc_ok = is_correct(sc_majority_answer, gold)

            if cot_ok:
                summary_counts["cot_correct"] += 1
            if normalize_numeric(cot_answer) is None:
                summary_counts["cot_parse_fail"] += 1
            if sc_ok:
                summary_counts["sc_correct"] += 1
            if sc_majority_answer is None:
                summary_counts["sc_parse_fail"] += 1
            if tied:
                summary_counts["sc_majority_ties"] += 1
            summary_counts["sc_sample_parse_fail"] += sum(answer is None for answer in sc_normalized_answers)

            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row.get("index", idx),
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "cot": {
                    "output": cot_outputs[idx],
                    "parsed_answer": cot_answer,
                    "normalized_answer": normalize_numeric(cot_answer),
                    "correct": cot_ok,
                },
                "cot_sc": {
                    "sample_outputs": sc_outputs[idx],
                    "parsed_sample_answers": sc_answers,
                    "normalized_sample_answers": sc_normalized_answers,
                    "majority_answer": sc_majority_answer,
                    "majority_tie": tied,
                    "correct": sc_ok,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    elapsed = time.time() - started_at
    total = max(1, len(rows))
    total_samples = max(1, summary_counts["sc_total_samples"])
    summary = {
        "run_id": args.run_id,
        "model_key": args.model_key,
        "model_path": str(model_path),
        "benchmark": args.benchmark,
        "split": args.split,
        "rows": len(rows),
        "cot_temperature": args.cot_temperature,
        "sc_temperature": args.sc_temperature,
        "sc_samples": args.sc_samples,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": summary_counts,
        "metrics": {
            "cot_accuracy": summary_counts["cot_correct"] / total,
            "cot_parse_fail_rate": summary_counts["cot_parse_fail"] / total,
            "sc_accuracy": summary_counts["sc_correct"] / total,
            "sc_parse_fail_rate": summary_counts["sc_parse_fail"] / total,
            "sc_sample_parse_fail_rate": summary_counts["sc_sample_parse_fail"] / total_samples,
            "sc_majority_tie_rate": summary_counts["sc_majority_ties"] / total,
        },
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {args.model_key}\n\n")
        handle.write(f"- Rows: {len(rows)}\n")
        handle.write(f"- CoT accuracy: {summary['metrics']['cot_accuracy']:.4f}\n")
        handle.write(f"- CoT-SC accuracy: {summary['metrics']['sc_accuracy']:.4f}\n")
        handle.write(f"- CoT-SC samples: {args.sc_samples}\n")
        handle.write(f"- CoT-SC tie rate: {summary['metrics']['sc_majority_tie_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
