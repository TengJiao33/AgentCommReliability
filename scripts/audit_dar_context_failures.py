#!/usr/bin/env python3
"""Audit DAR context events around right/wrong answer transitions."""

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


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


def compact_ids(agent_ids: Iterable[str]) -> List[str]:
    return [str(compact_agent_id(agent_id)) for agent_id in agent_ids]


def counter_to_dict(counter: Counter) -> Dict[str, int]:
    return {str(key): value for key, value in sorted(counter.items(), key=lambda item: str(item[0]))}


def first_dict(items: Any) -> Dict[str, Any]:
    if isinstance(items, list) and items and isinstance(items[0], dict):
        return items[0]
    return {}


def round_by_index(record: Dict[str, Any], round_index: int) -> Dict[str, Any]:
    for round_data in record.get("rounds") or []:
        if round_data.get("round_index") == round_index:
            return round_data
    return {}


def agent_answer_rows(agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "agent_id": compact_agent_id(agent.get("agent_id")),
            "answer": agent.get("answer"),
            "correct": agent.get("correct"),
        }
        for agent in agents
    ]


def answer_is_parseable(answer: Any) -> bool:
    return answer is not None and str(answer).strip() != ""


def source_stats(agent_ids: List[str], agents: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_id = {agent.get("agent_id"): agent for agent in agents}
    correct_ids = []
    parseable_ids = []
    answers = []
    for agent_id in agent_ids:
        agent = by_id.get(agent_id, {})
        answer = agent.get("answer")
        if agent.get("correct") is True:
            correct_ids.append(agent_id)
        if answer_is_parseable(answer):
            parseable_ids.append(agent_id)
        answers.append(
            {
                "agent_id": compact_agent_id(agent_id),
                "answer": answer,
                "correct": agent.get("correct"),
                "parseable": answer_is_parseable(answer),
            }
        )
    return {
        "count": len(agent_ids),
        "correct_count": len(correct_ids),
        "parseable_count": len(parseable_ids),
        "correct_agent_ids": compact_ids(correct_ids),
        "parseable_agent_ids": compact_ids(parseable_ids),
        "answers": answers,
    }


def classify_transition(transition: str, visible_stats: Dict[str, Any], suppressed_stats: Dict[str, Any]) -> str:
    visible_correct = int(visible_stats["correct_count"])
    suppressed_correct = int(suppressed_stats["correct_count"])
    visible_parseable = int(visible_stats["parseable_count"])
    suppressed_parseable = int(suppressed_stats["parseable_count"])

    if transition == "right_to_wrong":
        if visible_correct == 0 and suppressed_correct > 0:
            return "selection_dropped_all_correct"
        if visible_correct > 0:
            return "correct_context_retained_but_lost_after_update"
        if visible_parseable == 0 and suppressed_parseable > 0:
            return "selection_kept_unparseable"
        return "no_visible_correct_or_unclear"

    if transition == "wrong_to_right":
        if visible_correct > 0:
            return "correct_context_visible_and_recovered"
        if visible_parseable > 0:
            return "visible_noncorrect_scaffold_or_resampling"
        return "recovered_without_parseable_visible_answer"

    if transition == "stable_wrong":
        if visible_correct > 0:
            return "correct_context_visible_but_not_recovered"
        if suppressed_correct > 0:
            return "correct_context_suppressed_and_not_recovered"
        return "no_correct_first_round_agent"

    return "not_failure_transition"


def record_profile(label: str, record: Dict[str, Any]) -> Dict[str, Any]:
    context_event = first_dict(record.get("context_events"))
    retention_event = first_dict(record.get("retention_events"))
    round0_agents = round_by_index(record, 0).get("agents") or []
    round1_agents = round_by_index(record, 1).get("agents") or []

    visible_ids = context_event.get("visible_agent_ids") or retention_event.get("retained_agent_ids") or []
    suppressed_ids = context_event.get("suppressed_agent_ids") or retention_event.get("dropped_agent_ids") or []
    candidate_ids = context_event.get("candidate_agent_ids") or retention_event.get("candidate_agent_ids") or []
    original_visible_ids = (
        context_event.get("original_visible_agent_ids")
        or retention_event.get("original_retained_agent_ids")
        or []
    )

    visible_stats = source_stats(visible_ids, round0_agents)
    suppressed_stats = source_stats(suppressed_ids, round0_agents)
    transition = record.get("transition") or {}
    transition_type = transition.get("type", "unknown")
    public_state = record.get("public_state") or {}
    failure_mode = classify_transition(transition_type, visible_stats, suppressed_stats)

    return {
        "label": label,
        "run_id": record.get("run_id"),
        "sample_index": record.get("sample_index"),
        "instance_id": record.get("instance_id"),
        "gold_answer": record.get("gold_answer"),
        "method": record.get("method"),
        "task_regime": record.get("task_regime"),
        "surface": public_state.get("surface"),
        "communication_policy": public_state.get("communication_policy"),
        "transition": transition_type,
        "before_answer": transition.get("before_answer"),
        "before_correct": transition.get("before_correct"),
        "after_answer": transition.get("after_answer"),
        "after_correct": transition.get("after_correct"),
        "final_answer": (record.get("final") or {}).get("answer"),
        "final_correct": (record.get("final") or {}).get("correct"),
        "failure_mode": failure_mode,
        "context_event_derivation": context_event.get("derivation"),
        "visible_agent_ids": compact_ids(visible_ids),
        "suppressed_agent_ids": compact_ids(suppressed_ids),
        "candidate_agent_ids": compact_ids(candidate_ids),
        "original_visible_agent_ids": compact_ids(original_visible_ids),
        "visible_stats": visible_stats,
        "suppressed_stats": suppressed_stats,
        "retention_message_mode": (
            context_event.get("retention_message_mode")
            or retention_event.get("retention_message_mode")
        ),
        "guard_mode": context_event.get("guard_mode") or retention_event.get("guard_mode"),
        "guard_added_agent_ids": compact_ids(
            context_event.get("guard_added_agent_ids") or retention_event.get("guard_added_agent_ids") or []
        ),
        "guard_removed_agent_ids": compact_ids(
            context_event.get("guard_removed_agent_ids") or retention_event.get("guard_removed_agent_ids") or []
        ),
        "guard_notes": retention_event.get("guard_notes"),
        "round0_answers": agent_answer_rows(round0_agents),
        "round1_answers": agent_answer_rows(round1_agents),
    }


def add_profile_counts(counters: Dict[str, Counter], profile: Dict[str, Any]) -> None:
    transition = profile["transition"]
    visible = profile["visible_stats"]
    suppressed = profile["suppressed_stats"]
    counters["transitions"][transition] += 1
    counters["failure_modes"][profile["failure_mode"]] += 1
    counters["public_states"][f"{profile['surface']}/{profile['communication_policy']}"] += 1
    counters["visible_count"][visible["count"]] += 1
    counters["visible_correct_count"][visible["correct_count"]] += 1
    counters["suppressed_correct_count"][suppressed["correct_count"]] += 1
    counters["visible_parseable_count"][visible["parseable_count"]] += 1
    counters["suppressed_parseable_count"][suppressed["parseable_count"]] += 1
    counters["transition_by_visible_count"][f"{transition}|visible={visible['count']}"] += 1
    counters["transition_by_visible_correct"][f"{transition}|visible_correct={visible['correct_count']}"] += 1
    counters["transition_by_suppressed_correct"][f"{transition}|suppressed_correct={suppressed['correct_count']}"] += 1
    counters["transition_by_failure_mode"][f"{transition}|{profile['failure_mode']}"] += 1


def empty_counters() -> Dict[str, Counter]:
    return {
        "transitions": Counter(),
        "failure_modes": Counter(),
        "public_states": Counter(),
        "visible_count": Counter(),
        "visible_correct_count": Counter(),
        "suppressed_correct_count": Counter(),
        "visible_parseable_count": Counter(),
        "suppressed_parseable_count": Counter(),
        "transition_by_visible_count": Counter(),
        "transition_by_visible_correct": Counter(),
        "transition_by_suppressed_correct": Counter(),
        "transition_by_failure_mode": Counter(),
    }


def materialize_counters(counters: Dict[str, Counter]) -> Dict[str, Dict[str, int]]:
    return {key: counter_to_dict(counter) for key, counter in counters.items()}


def summarize_trace(label: str, records: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    profiles = [record_profile(label, record) for record in records]
    counters = empty_counters()
    case_rows = []
    final_correct = 0
    for profile in profiles:
        add_profile_counts(counters, profile)
        if profile["final_correct"] is True:
            final_correct += 1
        if profile["transition"] in {"right_to_wrong", "wrong_to_right"}:
            row = dict(profile)
            row["case_type"] = "transition_case"
            case_rows.append(row)

    summary = {
        "records": len(records),
        "final_correct": final_correct,
        "final_accuracy": final_correct / len(records) if records else None,
        **materialize_counters(counters),
        "right_to_wrong_cases": [
            profile["sample_index"] for profile in profiles if profile["transition"] == "right_to_wrong"
        ],
        "wrong_to_right_cases": [
            profile["sample_index"] for profile in profiles if profile["transition"] == "wrong_to_right"
        ],
    }
    return summary, case_rows


def paired_comparison(
    baseline_label: str,
    baseline_records: List[Dict[str, Any]],
    label: str,
    records: List[Dict[str, Any]],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    baseline_by_sample = {record.get("sample_index"): record for record in baseline_records}
    counters = Counter()
    changed_cases = []
    for record in records:
        sample_index = record.get("sample_index")
        baseline = baseline_by_sample.get(sample_index)
        if not baseline:
            continue
        baseline_profile = record_profile(baseline_label, baseline)
        profile = record_profile(label, record)
        before = baseline_profile["final_correct"]
        after = profile["final_correct"]
        counters[f"{before}_to_{after}"] += 1
        if before != after:
            changed_cases.append(
                {
                    "case_type": "paired_changed_final",
                    "sample_index": sample_index,
                    "instance_id": profile["instance_id"],
                    "gold_answer": profile["gold_answer"],
                    "baseline_label": baseline_label,
                    "label": label,
                    "baseline_final_correct": before,
                    "final_correct": after,
                    "baseline_transition": baseline_profile["transition"],
                    "transition": profile["transition"],
                    "baseline_failure_mode": baseline_profile["failure_mode"],
                    "failure_mode": profile["failure_mode"],
                    "baseline_after_answer": baseline_profile["after_answer"],
                    "after_answer": profile["after_answer"],
                    "baseline_surface": baseline_profile["surface"],
                    "surface": profile["surface"],
                    "baseline_communication_policy": baseline_profile["communication_policy"],
                    "communication_policy": profile["communication_policy"],
                    "baseline_visible_agent_ids": baseline_profile["visible_agent_ids"],
                    "visible_agent_ids": profile["visible_agent_ids"],
                    "baseline_visible_correct_count": baseline_profile["visible_stats"]["correct_count"],
                    "visible_correct_count": profile["visible_stats"]["correct_count"],
                    "baseline_suppressed_correct_count": baseline_profile["suppressed_stats"]["correct_count"],
                    "suppressed_correct_count": profile["suppressed_stats"]["correct_count"],
                    "guard_added_agent_ids": profile["guard_added_agent_ids"],
                    "guard_removed_agent_ids": profile["guard_removed_agent_ids"],
                    "guard_notes": profile["guard_notes"],
                    "round0_answers": profile["round0_answers"],
                    "round1_answers": profile["round1_answers"],
                }
            )
    summary = {
        "baseline_label": baseline_label,
        "label": label,
        "final_correct_transition_counts": counter_to_dict(counters),
        "changed_final_cases": [
            {"sample_index": row["sample_index"], "from_to": f"{row['baseline_final_correct']}_to_{row['final_correct']}"}
            for row in changed_cases
        ],
    }
    return summary, changed_cases


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", action="append", required=True, help="label=path to a DAR v1.1 trace")
    parser.add_argument("--baseline-label", default=None)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()

    trace_specs = [parse_label_path(trace_arg) for trace_arg in args.trace]
    records_by_label = {label: load_jsonl(path) for label, path in trace_specs}
    baseline_label = args.baseline_label or trace_specs[0][0]

    aggregate_counters = empty_counters()
    trace_summaries = {}
    cases = []
    total_records = 0
    total_final_correct = 0
    for label, path in trace_specs:
        records = records_by_label[label]
        summary, trace_cases = summarize_trace(label, records)
        trace_summaries[label] = {"path": str(path), **summary}
        cases.extend(trace_cases)
        total_records += summary["records"]
        total_final_correct += summary["final_correct"]
        for key, value in summary.items():
            if key in aggregate_counters:
                aggregate_counters[key].update(value)

    paired = {}
    if baseline_label in records_by_label:
        for label, _ in trace_specs:
            if label == baseline_label:
                continue
            summary, changed_cases = paired_comparison(
                baseline_label,
                records_by_label[baseline_label],
                label,
                records_by_label[label],
            )
            paired[label] = summary
            cases.extend(changed_cases)

    payload = {
        "baseline_label": baseline_label,
        "aggregate": {
            "trace_count": len(trace_specs),
            "records": total_records,
            "final_correct": total_final_correct,
            "final_accuracy": total_final_correct / total_records if total_records else None,
            **materialize_counters(aggregate_counters),
        },
        "traces": trace_summaries,
        "paired_comparisons": paired,
    }
    write_json(args.summary_out, payload)
    write_jsonl(args.cases_out, cases)


if __name__ == "__main__":
    main()
