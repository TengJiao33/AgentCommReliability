#!/usr/bin/env python3
"""Recompute MAD-MM records and summaries with the current evaluator."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from run_basic_mad import is_correct, majority_vote, normalize_numeric


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_root", help="Experiment run root containing MAD-MM strategy subdirectories.")
    parser.add_argument("--dry-run", action="store_true", help="Print recomputed summaries without writing files.")
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def parsed_answer(output: dict[str, Any]) -> Any:
    if "parsed_answer" in output:
        return output.get("parsed_answer")
    parsed = output.get("parsed")
    if isinstance(parsed, dict):
        return parsed.get("answer")
    return None


def label_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        for round_record in record["mad_mm"].get("rounds", []):
            memory_mask = round_record.get("memory_mask")
            if not isinstance(memory_mask, dict):
                continue
            for label in memory_mask.get("labels", []):
                counts[str(label)] += 1
    return dict(sorted(counts.items()))


def recompute_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        raise ValueError("records.jsonl is empty")

    agents = int(records[0]["mad_mm"]["agents"])
    counts = {
        "total": len(records),
        "initial_majority_correct": 0,
        "final_correct": 0,
        "final_parse_fail": 0,
        "final_majority_ties": 0,
        "retained_memories": 0,
        "total_mask_decisions": 0,
    }
    agent_final_correct = [0 for _ in range(agents)]

    for record in records:
        gold = record.get("gold_answer")
        mad_mm = record["mad_mm"]
        rounds = mad_mm.get("rounds", [])
        if not rounds:
            raise ValueError(f"record index {record.get('index')} has no rounds")

        for round_record in rounds:
            outputs = round_record.get("agent_outputs", [])
            answers = [parsed_answer(output) for output in outputs]
            for output, answer in zip(outputs, answers):
                output["normalized_answer"] = normalize_numeric(answer)
            majority_answer, tied = majority_vote(answers)
            round_record["majority_answer"] = majority_answer
            round_record["majority_tie"] = tied

            memory_mask = round_record.get("memory_mask")
            if isinstance(memory_mask, dict):
                counts["retained_memories"] += int(memory_mask.get("retained_count", 0))
                counts["total_mask_decisions"] += int(memory_mask.get("total_memories", 0))

        initial_answer = rounds[0]["majority_answer"]
        final_round = rounds[-1]
        final_answer = final_round["majority_answer"]
        final_answers = [parsed_answer(output) for output in final_round.get("agent_outputs", [])]

        if is_correct(initial_answer, gold):
            counts["initial_majority_correct"] += 1
        if is_correct(final_answer, gold):
            counts["final_correct"] += 1
        if final_answer is None:
            counts["final_parse_fail"] += 1
        if final_round["majority_tie"]:
            counts["final_majority_ties"] += 1
        for agent_idx, answer in enumerate(final_answers):
            if agent_idx < len(agent_final_correct) and is_correct(answer, gold):
                agent_final_correct[agent_idx] += 1

        mad_mm["final_majority_answer"] = final_answer
        mad_mm["final_normalized_answer"] = normalize_numeric(final_answer)
        mad_mm["correct"] = is_correct(final_answer, gold)

    total = max(1, counts["total"])
    mask_total = max(1, counts["total_mask_decisions"])
    return {
        "counts": counts,
        "metrics": {
            "initial_majority_accuracy": counts["initial_majority_correct"] / total,
            "final_accuracy": counts["final_correct"] / total,
            "agent_final_accuracy": [count / total for count in agent_final_correct],
            "final_parse_fail_rate": counts["final_parse_fail"] / total,
            "final_majority_tie_rate": counts["final_majority_ties"] / total,
            "memory_retention_rate": counts["retained_memories"] / mask_total,
        },
        "subjective_label_counts": label_counts(records),
    }


def update_summary(summary_path: Path, recomputed: dict[str, Any]) -> dict[str, Any]:
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["counts"] = recomputed["counts"]
    summary["metrics"] = recomputed["metrics"]
    summary["subjective_label_counts"] = recomputed["subjective_label_counts"]
    return summary


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    handle = path.open("w", encoding="utf-8", newline="\n")
    with handle:
        handle.write(f"# {summary['benchmark']}-{summary['model_key']}-{summary['prune_strategy']}\n\n")
        handle.write(f"- Rows: {summary['rows']}\n")
        handle.write(f"- Initial majority accuracy: {summary['metrics']['initial_majority_accuracy']:.4f}\n")
        handle.write(f"- Final accuracy: {summary['metrics']['final_accuracy']:.4f}\n")
        handle.write(f"- Memory retention rate: {summary['metrics']['memory_retention_rate']:.4f}\n")
        handle.write(f"- Final tie rate: {summary['metrics']['final_majority_tie_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {summary['elapsed_seconds']:.1f}\n")


def main() -> int:
    args = parse_args()
    run_root = Path(args.run_root).resolve()
    if not run_root.is_dir():
        raise SystemExit(f"run root does not exist: {run_root}")

    for summary_path in sorted(run_root.glob("*/summary.json")):
        records_path = summary_path.with_name("records.jsonl")
        summary_md_path = summary_path.with_name("summary.md")
        if not records_path.exists():
            continue
        records = read_jsonl(records_path)
        recomputed = recompute_records(records)
        summary = update_summary(summary_path, recomputed)
        print(
            json.dumps(
                {
                    "summary": str(summary_path),
                    "counts": summary["counts"],
                    "metrics": summary["metrics"],
                    "subjective_label_counts": summary.get("subjective_label_counts", {}),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        if not args.dry_run:
            write_jsonl(records_path, records)
            write_summary(summary_path, summary)
            write_summary_md(summary_md_path, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
