#!/usr/bin/env python3
"""Run one Standard MAD debate round on top of MCA-Pre-KV receiver outputs."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from run_basic_mad import is_correct, majority_vote, normalize_numeric, prompt_from_messages, resolve_inside
from run_mad_mm import answer_list, debate_prompt, extract_xml_answer, generate_outputs, prepare_question


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default=os.environ.get("ACR_WORK_DIR", os.getcwd()))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--input-records", required=True)
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--gpu-id", default=os.environ.get("CUDA_VISIBLE_DEVICES", "0"))
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-model-len", type=int, default=24064)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.85)
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="0 means all input records.")
    return parser.parse_args()


def load_pre_records(path: Path, limit: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
            if limit and len(records) >= limit:
                break
    return records


def pre_receiver_outputs(record: dict[str, Any], agents: int) -> list[dict[str, Any]]:
    outputs = list(record.get("mca_pre", {}).get("receiver_outputs") or [])
    if len(outputs) < agents:
        raise ValueError(f"record index={record.get('index')} has only {len(outputs)} receiver outputs")
    return outputs[:agents]


def transition_label(before_ok: bool, after_ok: bool) -> str:
    if before_ok and after_ok:
        return "PKC_to_C"
    if before_ok and not after_ok:
        return "PKC_to_W"
    if not before_ok and after_ok:
        return "PKW_to_C"
    return "PKW_to_W"


def main() -> int:
    args = parse_args()
    if args.agents < 1:
        raise SystemExit("--agents must be >= 1")

    work_dir = Path(args.work_dir).expanduser().resolve()
    input_records = resolve_inside(Path(args.input_records), work_dir, "input records")
    run_root = resolve_inside(work_dir / "experiments" / args.run_id, work_dir, "run root")
    output_dir = run_root / f"math500-{args.model_key}-mca-pre-kv-standard-mad"
    output_dir.mkdir(parents=True, exist_ok=True)

    records = load_pre_records(input_records, args.limit)
    if not records:
        raise SystemExit("no input records loaded")

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_id)

    from vllm import LLM, SamplingParams

    started_at = time.time()
    model_path = str(Path(args.model_path).expanduser().resolve())
    llm = LLM(
        model=model_path,
        trust_remote_code=True,
        dtype=args.dtype,
        max_model_len=args.max_model_len,
        gpu_memory_utilization=args.gpu_memory_utilization,
        seed=args.seed,
    )
    tokenizer = llm.get_tokenizer()
    sampling = SamplingParams(
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        logprobs=1,
    )

    debate_prompts: list[str] = []
    owners: list[tuple[int, int]] = []
    for row_idx, record in enumerate(records):
        question = prepare_question(str(record.get("question") or ""), str(record.get("benchmark") or "math500"))
        contexts = pre_receiver_outputs(record, args.agents)
        prompt = prompt_from_messages(tokenizer, [{"role": "user", "content": debate_prompt(question, contexts)}])
        for agent_idx in range(args.agents):
            debate_prompts.append(prompt)
            owners.append((row_idx, agent_idx))

    flat_outputs = generate_outputs(llm, debate_prompts, sampling, args.batch_size)
    debate_by_row = [[None for _ in range(args.agents)] for _ in records]
    for owner, output in zip(owners, flat_outputs):
        row_idx, agent_idx = owner
        debate_by_row[row_idx][agent_idx] = output

    output_records_path = output_dir / "records.jsonl"
    counts = {
        "total": len(records),
        "pre_baseline_correct": 0,
        "pre_kv_correct": 0,
        "debate_correct": 0,
        "debate_parse_fail": 0,
        "debate_majority_ties": 0,
        "PKC_to_C": 0,
        "PKC_to_W": 0,
        "PKW_to_C": 0,
        "PKW_to_W": 0,
    }
    agent_correct = [0 for _ in range(args.agents)]

    with output_records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row_idx, record in enumerate(records):
            mca_pre = record.get("mca_pre", {})
            gold = record.get("gold_answer")
            pre_baseline_answer = mca_pre.get("baseline_majority_answer")
            pre_kv_answer = mca_pre.get("final_majority_answer")
            debate_outputs = [item for item in debate_by_row[row_idx] if item is not None]
            debate_answers = answer_list(debate_outputs)
            debate_answer, debate_tie = majority_vote(debate_answers)

            pre_baseline_ok = is_correct(pre_baseline_answer, gold)
            pre_kv_ok = is_correct(pre_kv_answer, gold)
            debate_ok = is_correct(debate_answer, gold)
            trans = transition_label(pre_kv_ok, debate_ok)

            if pre_baseline_ok:
                counts["pre_baseline_correct"] += 1
            if pre_kv_ok:
                counts["pre_kv_correct"] += 1
            if debate_ok:
                counts["debate_correct"] += 1
            if normalize_numeric(debate_answer) is None:
                counts["debate_parse_fail"] += 1
            if debate_tie:
                counts["debate_majority_ties"] += 1
            counts[trans] += 1
            for agent_idx, answer in enumerate(debate_answers):
                if is_correct(answer, gold):
                    agent_correct[agent_idx] += 1

            handle.write(
                json.dumps(
                    {
                        "run_id": args.run_id,
                        "source_run_id": record.get("run_id"),
                        "model_key": args.model_key,
                        "benchmark": record.get("benchmark"),
                        "split": record.get("split"),
                        "index": record.get("index", row_idx),
                        "id": record.get("id"),
                        "question": record.get("question"),
                        "gold_answer": gold,
                        "mca_pre_kv_standard_mad": {
                            "source": "mca_pre_kv_receiver_outputs",
                            "agents": args.agents,
                            "pre_baseline_majority_answer": pre_baseline_answer,
                            "pre_kv_majority_answer": pre_kv_answer,
                            "pre_kv_receiver_outputs": mca_pre.get("receiver_outputs"),
                            "debate_outputs": debate_outputs,
                            "debate_majority_answer": debate_answer,
                            "debate_majority_tie": debate_tie,
                            "debate_correct": debate_ok,
                            "transition_from_pre_kv": trans,
                        },
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            handle.write("\n")

    elapsed = time.time() - started_at
    total = max(1, counts["total"])
    pre_wrong = max(1, counts["PKW_to_C"] + counts["PKW_to_W"])
    pre_correct = max(1, counts["PKC_to_C"] + counts["PKC_to_W"])
    summary = {
        "run_id": args.run_id,
        "input_records": str(input_records),
        "model_key": args.model_key,
        "model_path": model_path,
        "rows": len(records),
        "agents": args.agents,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "max_model_len": args.max_model_len,
        "counts": counts,
        "metrics": {
            "pre_baseline_accuracy": counts["pre_baseline_correct"] / total,
            "pre_kv_accuracy": counts["pre_kv_correct"] / total,
            "debate_accuracy": counts["debate_correct"] / total,
            "debate_delta_vs_pre_baseline": counts["debate_correct"] - counts["pre_baseline_correct"],
            "debate_delta_vs_pre_kv": counts["debate_correct"] - counts["pre_kv_correct"],
            "pre_kv_correct_harm_rate": counts["PKC_to_W"] / pre_correct,
            "pre_kv_wrong_recovery_rate": counts["PKW_to_C"] / pre_wrong,
            "debate_parse_fail_rate": counts["debate_parse_fail"] / total,
            "debate_majority_tie_rate": counts["debate_majority_ties"] / total,
            "agent_debate_accuracy": [count / total for count in agent_correct],
        },
        "elapsed_seconds": elapsed,
        "records_path": str(output_records_path),
    }

    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {output_dir.name}\n\n")
        handle.write(f"- Rows: {len(records)}\n")
        handle.write(f"- Pre baseline accuracy: {summary['metrics']['pre_baseline_accuracy']:.4f}\n")
        handle.write(f"- Pre-KV one-round accuracy: {summary['metrics']['pre_kv_accuracy']:.4f}\n")
        handle.write(f"- Pre-KV + Standard MAD accuracy: {summary['metrics']['debate_accuracy']:.4f}\n")
        handle.write(f"- Delta vs pre baseline: {summary['metrics']['debate_delta_vs_pre_baseline']:+d}\n")
        handle.write(f"- Delta vs pre-KV one-round: {summary['metrics']['debate_delta_vs_pre_kv']:+d}\n")
        handle.write(f"- Pre-KV-correct harm rate: {summary['metrics']['pre_kv_correct_harm_rate']:.4f}\n")
        handle.write(f"- Pre-KV-wrong recovery rate: {summary['metrics']['pre_kv_wrong_recovery_rate']:.4f}\n")
        handle.write(f"- Debate tie rate: {summary['metrics']['debate_majority_tie_rate']:.4f}\n")
        handle.write(f"- Debate parse fail rate: {summary['metrics']['debate_parse_fail_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
