#!/usr/bin/env python3
"""Run a minimal multi-agent debate baseline on prepared JSONL benchmarks."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ModelSpec:
    key: str
    path: Path


ROLE_NAMES = (
    "careful arithmetic solver",
    "skeptical checker",
    "concise verifier",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default=os.environ.get("ACR_WORK_DIR", os.getcwd()))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--benchmark", default="gsm8k")
    parser.add_argument("--split", default="test")
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--gpu-id", default=os.environ.get("CUDA_VISIBLE_DEVICES", "0"))
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--direct-temperature", type=float, default=0.0)
    parser.add_argument("--debate-temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-model-len", type=int, default=4096)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.82)
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    return parser.parse_args()


def resolve_inside(path: Path, root: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SystemExit(f"{label} must stay inside work-dir: {resolved}") from exc
    return resolved


def load_rows(path: Path, limit: int) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
            if limit and len(rows) >= limit:
                break
    return rows


def prompt_from_messages(tokenizer: Any, messages: list[dict[str, str]]) -> str:
    template = getattr(tokenizer, "chat_template", None)
    if template:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    rendered = []
    for message in messages:
        role = message["role"].upper()
        rendered.append(f"{role}: {message['content']}")
    rendered.append("ASSISTANT:")
    return "\n\n".join(rendered)


def direct_prompt(question: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "You solve grade-school math problems. Show concise reasoning and end with exactly 'Final answer: <answer>'.",
        },
        {"role": "user", "content": question},
    ]


def initial_agent_prompt(question: str, agent_index: int) -> list[dict[str, str]]:
    role = ROLE_NAMES[agent_index % len(ROLE_NAMES)]
    return [
        {
            "role": "system",
            "content": (
                f"You are agent {agent_index + 1}, a {role}. Solve independently. "
                "Show concise reasoning and end with exactly 'Final answer: <answer>'."
            ),
        },
        {"role": "user", "content": question},
    ]


def revision_prompt(
    question: str,
    agent_index: int,
    own_answer: str,
    peer_answers: list[tuple[int, str]],
) -> list[dict[str, str]]:
    peer_text = "\n\n".join(f"Agent {idx + 1} said:\n{text}" for idx, text in peer_answers)
    return [
        {
            "role": "system",
            "content": (
                f"You are agent {agent_index + 1}. Reconsider your solution after reading the other agents. "
                "If another answer is better, switch. End with exactly 'Final answer: <answer>'."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                f"Your previous answer:\n{own_answer}\n\n"
                f"Other agents:\n{peer_text}\n\n"
                "Give your revised solution."
            ),
        },
    ]


def find_answer_text(text: str) -> str | None:
    final_matches = re.findall(r"Final answer\s*:\s*(.+)", text, flags=re.IGNORECASE)
    if final_matches:
        return final_matches[-1].strip()
    gsm_matches = re.findall(r"####\s*(.+)", text)
    if gsm_matches:
        return gsm_matches[-1].strip()
    number_matches = re.findall(r"-?\d[\d,]*(?:\.\d+)?(?:\s*/\s*-?\d[\d,]*(?:\.\d+)?)?", text)
    if number_matches:
        return number_matches[-1].strip()
    return None


def normalize_numeric(answer: Any) -> str | None:
    if answer is None:
        return None
    text = str(answer).strip()
    if not text:
        return None
    if "####" in text:
        text = text.split("####")[-1].strip()
    final = find_answer_text(text)
    if final is not None:
        text = final
    text = text.replace(",", "").replace("$", "").strip()
    text = re.sub(r"\\boxed\{([^{}]+)\}", r"\1", text)
    match = re.search(r"-?\d+(?:\.\d+)?(?:\s*/\s*-?\d+(?:\.\d+)?)?", text)
    if not match:
        return None
    value = match.group(0).replace(" ", "")
    try:
        return str(Fraction(value))
    except Exception:
        try:
            return str(Fraction(float(value)).limit_denominator(1000000))
        except Exception:
            return value


def is_correct(prediction: Any, gold: Any) -> bool:
    pred_norm = normalize_numeric(prediction)
    gold_norm = normalize_numeric(gold)
    return pred_norm is not None and gold_norm is not None and pred_norm == gold_norm


def majority_vote(agent_answers: list[str | None]) -> tuple[str | None, bool]:
    normalized = [normalize_numeric(answer) for answer in agent_answers]
    normalized = [answer for answer in normalized if answer is not None]
    if not normalized:
        return None, False
    counts = Counter(normalized)
    best_count = max(counts.values())
    winners = [answer for answer, count in counts.items() if count == best_count]
    if len(winners) == 1:
        return winners[0], False
    for answer in normalized:
        if answer in winners:
            return answer, True
    return winners[0], True


def generate_texts(llm: Any, prompts: list[str], sampling_params: Any, batch_size: int) -> list[str]:
    outputs: list[str] = []
    for start in range(0, len(prompts), batch_size):
        batch = prompts[start : start + batch_size]
        for result in llm.generate(batch, sampling_params, use_tqdm=True):
            outputs.append(result.outputs[0].text)
    return outputs


def main() -> int:
    args = parse_args()
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

    direct_sampling = SamplingParams(
        temperature=args.direct_temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
    )
    debate_sampling = SamplingParams(
        temperature=args.debate_temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
    )

    questions = [str(row.get("question") or "") for row in rows]
    direct_prompts = [prompt_from_messages(tokenizer, direct_prompt(question)) for question in questions]
    direct_outputs = generate_texts(llm, direct_prompts, direct_sampling, args.batch_size)

    initial_prompts = []
    for question in questions:
        for agent_idx in range(args.agents):
            initial_prompts.append(prompt_from_messages(tokenizer, initial_agent_prompt(question, agent_idx)))
    initial_flat = generate_texts(llm, initial_prompts, debate_sampling, args.batch_size)
    initial_by_row = [
        initial_flat[i * args.agents : (i + 1) * args.agents]
        for i in range(len(rows))
    ]

    current_by_row = initial_by_row
    for _round_idx in range(args.rounds):
        revision_prompts = []
        for row_idx, question in enumerate(questions):
            for agent_idx in range(args.agents):
                peer_answers = [
                    (other_idx, current_by_row[row_idx][other_idx])
                    for other_idx in range(args.agents)
                    if other_idx != agent_idx
                ]
                revision_prompts.append(
                    prompt_from_messages(
                        tokenizer,
                        revision_prompt(question, agent_idx, current_by_row[row_idx][agent_idx], peer_answers),
                    )
                )
        revised_flat = generate_texts(llm, revision_prompts, debate_sampling, args.batch_size)
        current_by_row = [
            revised_flat[i * args.agents : (i + 1) * args.agents]
            for i in range(len(rows))
        ]

    records_path = output_dir / "records.jsonl"
    summary_counts = {
        "total": len(rows),
        "direct_correct": 0,
        "mad_correct": 0,
        "direct_parse_fail": 0,
        "mad_parse_fail": 0,
        "majority_ties": 0,
    }
    agent_correct = [0 for _ in range(args.agents)]
    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for idx, row in enumerate(rows):
            gold = row.get("answer")
            direct_answer = find_answer_text(direct_outputs[idx])
            final_agent_answers = [find_answer_text(text) for text in current_by_row[idx]]
            majority_answer, tied = majority_vote(final_agent_answers)
            direct_ok = is_correct(direct_answer, gold)
            mad_ok = is_correct(majority_answer, gold)
            if direct_ok:
                summary_counts["direct_correct"] += 1
            if mad_ok:
                summary_counts["mad_correct"] += 1
            if normalize_numeric(direct_answer) is None:
                summary_counts["direct_parse_fail"] += 1
            if majority_answer is None:
                summary_counts["mad_parse_fail"] += 1
            if tied:
                summary_counts["majority_ties"] += 1
            for agent_idx, answer in enumerate(final_agent_answers):
                if is_correct(answer, gold):
                    agent_correct[agent_idx] += 1
            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row.get("index", idx),
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "direct": {
                    "output": direct_outputs[idx],
                    "parsed_answer": direct_answer,
                    "normalized_answer": normalize_numeric(direct_answer),
                    "correct": direct_ok,
                },
                "mad": {
                    "initial_outputs": initial_by_row[idx],
                    "final_outputs": current_by_row[idx],
                    "parsed_agent_answers": final_agent_answers,
                    "normalized_agent_answers": [normalize_numeric(answer) for answer in final_agent_answers],
                    "majority_answer": majority_answer,
                    "majority_tie": tied,
                    "correct": mad_ok,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    elapsed = time.time() - started_at
    total = max(1, len(rows))
    summary = {
        "run_id": args.run_id,
        "model_key": args.model_key,
        "model_path": str(model_path),
        "benchmark": args.benchmark,
        "split": args.split,
        "rows": len(rows),
        "agents": args.agents,
        "rounds": args.rounds,
        "direct_temperature": args.direct_temperature,
        "debate_temperature": args.debate_temperature,
        "max_tokens": args.max_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": summary_counts,
        "metrics": {
            "direct_accuracy": summary_counts["direct_correct"] / total,
            "mad_accuracy": summary_counts["mad_correct"] / total,
            "agent_final_accuracy": [count / total for count in agent_correct],
            "direct_parse_fail_rate": summary_counts["direct_parse_fail"] / total,
            "mad_parse_fail_rate": summary_counts["mad_parse_fail"] / total,
            "majority_tie_rate": summary_counts["majority_ties"] / total,
        },
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {args.model_key}\n\n")
        handle.write(f"- Rows: {len(rows)}\n")
        handle.write(f"- Direct accuracy: {summary['metrics']['direct_accuracy']:.4f}\n")
        handle.write(f"- MAD accuracy: {summary['metrics']['mad_accuracy']:.4f}\n")
        handle.write(f"- Majority tie rate: {summary['metrics']['majority_tie_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
