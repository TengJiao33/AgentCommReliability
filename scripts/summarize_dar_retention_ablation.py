#!/usr/bin/env python3
"""Summarize DAR retention ablations from unified communication traces."""

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def load_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def parse_label_path(value: str) -> Tuple[str, Path]:
    if "=" in value:
        label, path = value.split("=", 1)
        return label, Path(path)
    path = Path(value)
    return path.stem, path


def compact_agent_id(agent_id: Optional[str]) -> Optional[str]:
    if not agent_id:
        return agent_id
    if "__" in agent_id:
        return agent_id.rsplit("__", 1)[-1]
    return agent_id


def counter_to_dict(counter: Counter) -> Dict[str, int]:
    return dict(sorted(counter.items(), key=lambda item: str(item[0])))


def first_round_agents(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    for round_data in record.get("rounds") or []:
        if round_data.get("round_index") == 0:
            return round_data.get("agents") or []
    return []


def round_by_index(record: Dict[str, Any], round_index: int) -> Optional[Dict[str, Any]]:
    for round_data in record.get("rounds") or []:
        if round_data.get("round_index") == round_index:
            return round_data
    return None


def first_retention_event(record: Dict[str, Any]) -> Dict[str, Any]:
    events = record.get("retention_events") or []
    event = events[0] if events else {}
    return event if isinstance(event, dict) else {}


def sum_token_cost(target: Dict[str, int], token_cost: Any) -> None:
    if not isinstance(token_cost, dict):
        return
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        target[key] += int(token_cost.get(key) or 0)


def correctness_counts(agent_ids: List[str], agents: List[Dict[str, Any]]) -> Tuple[int, int]:
    by_id = {agent.get("agent_id"): agent for agent in agents}
    correct = 0
    parseable = 0
    for agent_id in agent_ids:
        agent = by_id.get(agent_id, {})
        if agent.get("correct") is True:
            correct += 1
        answer = agent.get("answer")
        if answer is not None and str(answer).strip() != "":
            parseable += 1
    return correct, parseable


def case_row(label: str, record: Dict[str, Any]) -> Dict[str, Any]:
    event = first_retention_event(record)
    agents = first_round_agents(record)
    retained = event.get("retained_agent_ids") or []
    dropped = event.get("dropped_agent_ids") or []
    return {
        "label": label,
        "sample_index": record.get("sample_index"),
        "instance_id": record.get("instance_id"),
        "transition": (record.get("transition") or {}).get("type"),
        "gold_answer": record.get("gold_answer"),
        "before_answer": (record.get("transition") or {}).get("before_answer"),
        "after_answer": (record.get("transition") or {}).get("after_answer"),
        "final_correct": (record.get("final") or {}).get("correct"),
        "retained_agent_ids": [compact_agent_id(agent_id) for agent_id in retained],
        "dropped_agent_ids": [compact_agent_id(agent_id) for agent_id in dropped],
        "original_retained_agent_ids": [
            compact_agent_id(agent_id) for agent_id in (event.get("original_retained_agent_ids") or [])
        ],
        "guard_added_agent_ids": [
            compact_agent_id(agent_id) for agent_id in (event.get("guard_added_agent_ids") or [])
        ],
        "guard_removed_agent_ids": [
            compact_agent_id(agent_id) for agent_id in (event.get("guard_removed_agent_ids") or [])
        ],
        "guard_notes": event.get("guard_notes"),
        "retention_message_mode": event.get("retention_message_mode"),
        "round0_answers": [
            {
                "agent_id": compact_agent_id(agent.get("agent_id")),
                "answer": agent.get("answer"),
                "correct": agent.get("correct"),
            }
            for agent in agents
        ],
    }


def summarize_records(label: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    transitions = Counter()
    final_correct = Counter()
    round_correct = Counter()
    round_total = Counter()
    retained_count = Counter()
    dropped_count = Counter()
    retained_correct_count = Counter()
    dropped_correct_count = Counter()
    retained_parseable_count = Counter()
    dropped_parseable_count = Counter()
    message_modes = Counter()
    guard_modes = Counter()
    guard_notes = Counter()
    guard_added_count = Counter()
    guard_removed_count = Counter()
    generation_tokens = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    filter_tokens = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    changed_retention_sets = 0
    guard_recovered_any_correct = 0
    guard_lost_any_correct = 0
    right_to_wrong_cases = []
    wrong_to_right_cases = []

    for record in records:
        transition = (record.get("transition") or {}).get("type", "unknown")
        transitions[transition] += 1
        final_correct[str((record.get("final") or {}).get("correct"))] += 1

        for round_data in record.get("rounds") or []:
            idx = str(round_data.get("round_index"))
            if round_data.get("debate_correct") is not None:
                round_total[idx] += 1
                if round_data.get("debate_correct") is True:
                    round_correct[idx] += 1

        sum_token_cost(generation_tokens, record.get("token_cost"))
        event = first_retention_event(record)
        if event:
            sum_token_cost(filter_tokens, event.get("token_cost"))
            agents = first_round_agents(record)
            retained = event.get("retained_agent_ids") or []
            dropped = event.get("dropped_agent_ids") or []
            original = event.get("original_retained_agent_ids") or retained
            added = event.get("guard_added_agent_ids") or []
            removed = event.get("guard_removed_agent_ids") or []
            retained_correct, retained_parseable = correctness_counts(retained, agents)
            dropped_correct, dropped_parseable = correctness_counts(dropped, agents)

            retained_count[str(len(retained))] += 1
            dropped_count[str(len(dropped))] += 1
            retained_correct_count[str(retained_correct)] += 1
            dropped_correct_count[str(dropped_correct)] += 1
            retained_parseable_count[str(retained_parseable)] += 1
            dropped_parseable_count[str(dropped_parseable)] += 1
            message_modes[str(event.get("retention_message_mode"))] += 1
            guard_modes[str(event.get("guard_mode"))] += 1
            guard_added_count[str(len(added))] += 1
            guard_removed_count[str(len(removed))] += 1
            for note in event.get("guard_notes") or []:
                guard_notes[str(note)] += 1

            if set(original) != set(retained):
                changed_retention_sets += 1

            original_correct, _ = correctness_counts(original, agents)
            if original_correct == 0 and retained_correct > 0:
                guard_recovered_any_correct += 1
            if original_correct > 0 and retained_correct == 0:
                guard_lost_any_correct += 1

        if transition == "right_to_wrong":
            right_to_wrong_cases.append(case_row(label, record))
        elif transition == "wrong_to_right":
            wrong_to_right_cases.append(case_row(label, record))

    round_accuracy = {
        idx: (round_correct[idx] / round_total[idx] if round_total[idx] else None)
        for idx in sorted(round_total, key=lambda value: int(value) if str(value).isdigit() else value)
    }
    generation_plus_filter = {
        key: generation_tokens[key] + filter_tokens[key]
        for key in ("input_tokens", "output_tokens", "total_tokens")
    }

    return {
        "rows": len(records),
        "round_accuracy": round_accuracy,
        "transitions": counter_to_dict(transitions),
        "final_correct": counter_to_dict(final_correct),
        "generation_token_total": generation_tokens,
        "filter_token_total": filter_tokens,
        "generation_plus_filter_token_total": generation_plus_filter,
        "retention": {
            "retained_count_distribution": counter_to_dict(retained_count),
            "dropped_count_distribution": counter_to_dict(dropped_count),
            "retained_correct_count_distribution": counter_to_dict(retained_correct_count),
            "dropped_correct_count_distribution": counter_to_dict(dropped_correct_count),
            "retained_parseable_count_distribution": counter_to_dict(retained_parseable_count),
            "dropped_parseable_count_distribution": counter_to_dict(dropped_parseable_count),
            "message_modes": counter_to_dict(message_modes),
            "guard_modes": counter_to_dict(guard_modes),
            "guard_notes": counter_to_dict(guard_notes),
            "guard_added_count_distribution": counter_to_dict(guard_added_count),
            "guard_removed_count_distribution": counter_to_dict(guard_removed_count),
            "changed_retention_sets": changed_retention_sets,
            "guard_recovered_any_correct": guard_recovered_any_correct,
            "guard_lost_any_correct": guard_lost_any_correct,
        },
        "right_to_wrong_cases": right_to_wrong_cases,
        "wrong_to_right_cases": wrong_to_right_cases,
    }


def paired_comparison(
    baseline_label: str,
    baseline_records: List[Dict[str, Any]],
    label: str,
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    baseline_by_sample = {record.get("sample_index"): record for record in baseline_records}
    cases = []
    counts = Counter()
    for record in records:
        sample_index = record.get("sample_index")
        baseline = baseline_by_sample.get(sample_index)
        if not baseline:
            continue
        before = (baseline.get("final") or {}).get("correct")
        after = (record.get("final") or {}).get("correct")
        transition = f"{before}_to_{after}"
        counts[transition] += 1
        if before != after:
            row = case_row(label, record)
            row["baseline_label"] = baseline_label
            row["baseline_after_answer"] = (baseline.get("transition") or {}).get("after_answer")
            row["baseline_final_correct"] = before
            row["baseline_transition"] = (baseline.get("transition") or {}).get("type")
            cases.append(row)
    return {
        "baseline_label": baseline_label,
        "label": label,
        "final_correct_transition_counts": counter_to_dict(counts),
        "changed_final_cases": cases,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", action="append", required=True, help="label=path to unified DAR trace JSONL")
    parser.add_argument("--baseline-label", default=None)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    traces = []
    records_by_label: Dict[str, List[Dict[str, Any]]] = {}
    summaries: Dict[str, Any] = {}
    for trace_arg in args.trace:
        label, path = parse_label_path(trace_arg)
        records = list(load_jsonl(path))
        records_by_label[label] = records
        summaries[label] = summarize_records(label, records)
        traces.append({"label": label, "path": str(path)})

    baseline_label = args.baseline_label or (traces[0]["label"] if traces else None)
    paired = {}
    if baseline_label and baseline_label in records_by_label:
        for label, records in records_by_label.items():
            if label == baseline_label:
                continue
            paired[label] = paired_comparison(
                baseline_label,
                records_by_label[baseline_label],
                label,
                records,
            )

    summary = {
        "traces": traces,
        "baseline_label": baseline_label,
        "summaries": summaries,
        "paired_comparisons": paired,
    }
    write_json(args.summary_out, summary)

    if args.cases_out:
        case_rows = []
        for label, payload in summaries.items():
            case_rows.extend(payload["right_to_wrong_cases"])
            case_rows.extend(payload["wrong_to_right_cases"])
        for comparison in paired.values():
            case_rows.extend(comparison["changed_final_cases"])
        write_jsonl(args.cases_out, case_rows)


if __name__ == "__main__":
    main()
