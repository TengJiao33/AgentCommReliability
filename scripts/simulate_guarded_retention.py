#!/usr/bin/env python3
"""Offline guarded-retention simulation over unified communication traces.

This does not rerun any model. It audits already-saved retention decisions and
asks whether a simple post-filter guard would have changed which first-round
messages remained visible.
"""

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


UNPARSEABLE_BUCKET = "__unparseable__"


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


def parse_trace_arg(value: str) -> Tuple[str, Path]:
    if "=" in value:
        label, path = value.split("=", 1)
        return label, Path(path)
    path = Path(value)
    return path.stem, path


def answer_bucket(answer: Any) -> str:
    if answer is None:
        return UNPARSEABLE_BUCKET
    if isinstance(answer, str):
        text = answer.strip()
        if not text:
            return UNPARSEABLE_BUCKET
        return text.lower()
    if isinstance(answer, float) and answer.is_integer():
        return str(int(answer))
    return str(answer)


def compact_agent_id(agent_id: str) -> str:
    if "__" in agent_id:
        tail = agent_id.rsplit("__", 1)[-1]
        if tail:
            return tail
    return agent_id


def first_round_agents(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    rounds = record.get("rounds") or []
    for round_data in rounds:
        if round_data.get("round_index") == 0:
            return round_data.get("agents") or []
    return []


def first_retention_event(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    events = record.get("retention_events") or []
    if not events:
        return None
    event = events[0]
    return event if isinstance(event, dict) else None


def agent_map(agents: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {agent.get("agent_id"): agent for agent in agents if agent.get("agent_id")}


def order_unique(values: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def retained_answer_summary(agent_ids: List[str], agents_by_id: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for agent_id in agent_ids:
        agent = agents_by_id.get(agent_id, {})
        answer = agent.get("answer")
        rows.append(
            {
                "agent_id": compact_agent_id(agent_id),
                "answer": answer,
                "bucket": answer_bucket(answer),
                "correct": agent.get("correct"),
            }
        )
    return rows


def apply_guard(
    agents: List[Dict[str, Any]],
    original_retained_ids: List[str],
    max_retained: int,
) -> Dict[str, Any]:
    agents_by_id = agent_map(agents)
    candidate_ids = [agent.get("agent_id") for agent in agents if agent.get("agent_id")]
    candidate_set = set(candidate_ids)
    retained = [agent_id for agent_id in order_unique(original_retained_ids) if agent_id in candidate_set]

    bucket_to_agents: Dict[str, List[str]] = defaultdict(list)
    for agent in agents:
        agent_id = agent.get("agent_id")
        if not agent_id:
            continue
        bucket_to_agents[answer_bucket(agent.get("answer"))].append(agent_id)

    parseable_buckets = [bucket for bucket in bucket_to_agents if bucket != UNPARSEABLE_BUCKET]
    original_empty = len(retained) == 0
    if original_empty:
        return {
            "guard_mode": "reset",
            "guarded_retained_agent_ids": [],
            "added_agent_ids": [],
            "removed_agent_ids": [],
            "parseable_buckets": parseable_buckets,
            "missing_parseable_buckets": parseable_buckets,
            "notes": ["original_empty_retention_treated_as_reset"],
        }

    notes = []
    removed: List[str] = []
    added: List[str] = []

    def retained_parseable_buckets() -> List[str]:
        return order_unique(
            answer_bucket(agents_by_id[agent_id].get("answer"))
            for agent_id in retained
            if agent_id in agents_by_id and answer_bucket(agents_by_id[agent_id].get("answer")) != UNPARSEABLE_BUCKET
        )

    retained_has_parseable = bool(retained_parseable_buckets())
    retained_unparseable = [
        agent_id
        for agent_id in retained
        if agent_id in agents_by_id and answer_bucket(agents_by_id[agent_id].get("answer")) == UNPARSEABLE_BUCKET
    ]
    if parseable_buckets and not retained_has_parseable and retained_unparseable:
        for agent_id in retained_unparseable:
            retained.remove(agent_id)
            removed.append(agent_id)
        notes.append("replaced_unparseable_only_retention")

    def duplicate_selected_ids() -> List[str]:
        seen_buckets = set()
        duplicates = []
        for agent_id in retained:
            bucket = answer_bucket(agents_by_id.get(agent_id, {}).get("answer"))
            if bucket == UNPARSEABLE_BUCKET:
                continue
            if bucket in seen_buckets:
                duplicates.append(agent_id)
            else:
                seen_buckets.add(bucket)
        return duplicates

    while True:
        selected_buckets = set(retained_parseable_buckets())
        missing = [bucket for bucket in parseable_buckets if bucket not in selected_buckets]
        if not missing:
            break

        if len(retained) >= max_retained:
            removable = duplicate_selected_ids()
            if not removable:
                removable = [
                    agent_id
                    for agent_id in retained
                    if answer_bucket(agents_by_id.get(agent_id, {}).get("answer")) == UNPARSEABLE_BUCKET
                ]
            if removable:
                agent_id = removable[-1]
                retained.remove(agent_id)
                removed.append(agent_id)
            else:
                break

        bucket = missing[0]
        representative = next(
            agent_id for agent_id in bucket_to_agents[bucket] if agent_id not in retained
        )
        retained.append(representative)
        added.append(representative)

    selected_buckets = set(retained_parseable_buckets())
    missing_parseable_buckets = [bucket for bucket in parseable_buckets if bucket not in selected_buckets]
    if added:
        notes.append("added_missing_parseable_answer_bucket")
    if missing_parseable_buckets:
        notes.append("max_retained_prevented_full_answer_diversity")

    return {
        "guard_mode": "guarded",
        "guarded_retained_agent_ids": retained,
        "added_agent_ids": added,
        "removed_agent_ids": removed,
        "parseable_buckets": parseable_buckets,
        "missing_parseable_buckets": missing_parseable_buckets,
        "notes": notes,
    }


def count_correct(agent_ids: List[str], agents_by_id: Dict[str, Dict[str, Any]]) -> int:
    return sum(1 for agent_id in agent_ids if agents_by_id.get(agent_id, {}).get("correct") is True)


def count_parseable(agent_ids: List[str], agents_by_id: Dict[str, Dict[str, Any]]) -> int:
    return sum(
        1
        for agent_id in agent_ids
        if answer_bucket(agents_by_id.get(agent_id, {}).get("answer")) != UNPARSEABLE_BUCKET
    )


def update_counter(counter: Counter, value: Any) -> None:
    counter[str(value)] += 1


def group_key(label: str, record: Dict[str, Any]) -> str:
    return "|".join(
        [
            label,
            str(record.get("method_family")),
            str(record.get("method")),
        ]
    )


def analyze_trace(label: str, path: Path, max_retained: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    groups: Dict[str, Dict[str, Any]] = {}
    changed_cases: List[Dict[str, Any]] = []

    def stats_for(key: str, record: Dict[str, Any]) -> Dict[str, Any]:
        if key not in groups:
            groups[key] = {
                "trace_label": label,
                "method_family": record.get("method_family"),
                "method": record.get("method"),
                "records": 0,
                "records_with_retention": 0,
                "changed_by_guard": 0,
                "reset_modes": 0,
                "original_empty_retention": 0,
                "original_only_unparseable_with_parseable_available": 0,
                "guarded_only_unparseable_with_parseable_available": 0,
                "guard_added_agent": 0,
                "guard_removed_agent": 0,
                "guard_recovered_any_correct": 0,
                "guard_lost_any_correct": 0,
                "any_correct_available": 0,
                "original_retained_any_correct": 0,
                "guarded_retained_any_correct": 0,
                "right_to_wrong": 0,
                "right_to_wrong_changed": 0,
                "right_to_wrong_recovered_any_correct": 0,
                "transition_counts": Counter(),
                "parseable_bucket_count_distribution": Counter(),
                "original_retained_count_distribution": Counter(),
                "guarded_retained_count_distribution": Counter(),
                "original_retained_parseable_count_distribution": Counter(),
                "guarded_retained_parseable_count_distribution": Counter(),
            }
        return groups[key]

    for record in load_jsonl(path):
        key = group_key(label, record)
        stats = stats_for(key, record)
        stats["records"] += 1
        transition = (record.get("transition") or {}).get("type")
        update_counter(stats["transition_counts"], transition)

        event = first_retention_event(record)
        agents = first_round_agents(record)
        if not event or not agents:
            continue

        original_retained = event.get("retained_agent_ids") or []
        if not isinstance(original_retained, list):
            original_retained = []
        agents_by_id = agent_map(agents)
        guard = apply_guard(agents, original_retained, max_retained=max_retained)
        guarded_retained = guard["guarded_retained_agent_ids"]
        parseable_buckets = guard["parseable_buckets"]

        stats["records_with_retention"] += 1
        if guard["guard_mode"] == "reset":
            stats["reset_modes"] += 1
        if not original_retained:
            stats["original_empty_retention"] += 1
        if guard["added_agent_ids"]:
            stats["guard_added_agent"] += 1
        if guard["removed_agent_ids"]:
            stats["guard_removed_agent"] += 1

        original_correct = count_correct(original_retained, agents_by_id)
        guarded_correct = count_correct(guarded_retained, agents_by_id)
        correct_available = sum(1 for agent in agents if agent.get("correct") is True)
        original_parseable = count_parseable(original_retained, agents_by_id)
        guarded_parseable = count_parseable(guarded_retained, agents_by_id)

        update_counter(stats["parseable_bucket_count_distribution"], len(parseable_buckets))
        update_counter(stats["original_retained_count_distribution"], len(original_retained))
        update_counter(stats["guarded_retained_count_distribution"], len(guarded_retained))
        update_counter(stats["original_retained_parseable_count_distribution"], original_parseable)
        update_counter(stats["guarded_retained_parseable_count_distribution"], guarded_parseable)

        if correct_available:
            stats["any_correct_available"] += 1
        if original_correct:
            stats["original_retained_any_correct"] += 1
        if guarded_correct:
            stats["guarded_retained_any_correct"] += 1
        if correct_available and not original_correct and guarded_correct:
            stats["guard_recovered_any_correct"] += 1
        if correct_available and original_correct and not guarded_correct:
            stats["guard_lost_any_correct"] += 1

        original_only_unparseable = bool(parseable_buckets) and bool(original_retained) and original_parseable == 0
        guarded_only_unparseable = bool(parseable_buckets) and bool(guarded_retained) and guarded_parseable == 0
        if original_only_unparseable:
            stats["original_only_unparseable_with_parseable_available"] += 1
        if guarded_only_unparseable:
            stats["guarded_only_unparseable_with_parseable_available"] += 1

        changed = set(original_retained) != set(guarded_retained)
        if changed:
            stats["changed_by_guard"] += 1

        if transition == "right_to_wrong":
            stats["right_to_wrong"] += 1
            if changed:
                stats["right_to_wrong_changed"] += 1
            if correct_available and not original_correct and guarded_correct:
                stats["right_to_wrong_recovered_any_correct"] += 1

        if changed or transition == "right_to_wrong" or (correct_available and not original_correct and guarded_correct):
            case = {
                "trace_label": label,
                "method_family": record.get("method_family"),
                "method": record.get("method"),
                "instance_id": record.get("instance_id"),
                "sample_index": record.get("sample_index"),
                "transition_type": transition,
                "final_correct": (record.get("final") or {}).get("correct"),
                "gold_answer": record.get("gold_answer"),
                "original_retained_agent_ids": [compact_agent_id(x) for x in original_retained],
                "guarded_retained_agent_ids": [compact_agent_id(x) for x in guarded_retained],
                "added_agent_ids": [compact_agent_id(x) for x in guard["added_agent_ids"]],
                "removed_agent_ids": [compact_agent_id(x) for x in guard["removed_agent_ids"]],
                "guard_mode": guard["guard_mode"],
                "guard_notes": guard["notes"],
                "parseable_bucket_count": len(parseable_buckets),
                "missing_parseable_buckets": guard["missing_parseable_buckets"],
                "round0_correct_available": correct_available,
                "original_retained_correct_count": original_correct,
                "guarded_retained_correct_count": guarded_correct,
                "original_retained_answers": retained_answer_summary(original_retained, agents_by_id),
                "guarded_retained_answers": retained_answer_summary(guarded_retained, agents_by_id),
            }
            changed_cases.append(case)

    serializable_groups = {}
    for key, stats in groups.items():
        serializable = {}
        for name, value in stats.items():
            if isinstance(value, Counter):
                serializable[name] = dict(sorted(value.items()))
            else:
                serializable[name] = value
        serializable_groups[key] = serializable

    return serializable_groups, changed_cases


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trace",
        action="append",
        required=True,
        help="Trace JSONL path, optionally as label=path. Can be repeated.",
    )
    parser.add_argument("--max-retained", type=int, default=3)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    combined_groups: Dict[str, Any] = {}
    all_changed_cases: List[Dict[str, Any]] = []
    traces = []
    for value in args.trace:
        label, path = parse_trace_arg(value)
        groups, changed_cases = analyze_trace(label, path, max_retained=args.max_retained)
        combined_groups.update(groups)
        all_changed_cases.extend(changed_cases)
        traces.append({"label": label, "path": str(path)})

    summary = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "max_retained": args.max_retained,
        "rule": {
            "description": "Post-filter guard over first-round retained messages.",
            "steps": [
                "Treat empty retention as reset.",
                "Never keep only unparseable messages when parseable candidates exist.",
                "Add one representative from missing parseable answer buckets until max_retained is reached.",
                "Prefer answer diversity over duplicate retained answer buckets when a replacement is needed.",
            ],
            "uses_oracle_correctness": False,
            "oracle_correctness_only_for_audit_metrics": True,
        },
        "traces": traces,
        "groups": combined_groups,
        "changed_case_count": len(all_changed_cases),
    }
    write_json(args.summary_out, summary)
    if args.cases_out:
        write_jsonl(args.cases_out, all_changed_cases)


if __name__ == "__main__":
    main()
