#!/usr/bin/env python3
"""Summarize context_events from communication trace JSONL files."""

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def count_list(value: Any) -> int:
    return len(value) if isinstance(value, list) else 0


def counter_dict(counter: Counter) -> Dict[str, int]:
    return {str(key): value for key, value in sorted(counter.items(), key=lambda item: str(item[0]))}


def summarize_trace(path: Path) -> Dict[str, Any]:
    records = load_jsonl(path)
    method_counts = Counter(record.get("method") for record in records)
    regime_counts = Counter(record.get("task_regime") for record in records)
    transition_counts = Counter((record.get("transition") or {}).get("type") for record in records)
    surface_counts = Counter(
        (
            (record.get("public_state") or {}).get("surface"),
            (record.get("public_state") or {}).get("communication_policy"),
        )
        for record in records
    )

    context_events = []
    event_counts_per_row = Counter()
    rows_with_context = 0
    for record in records:
        events = record.get("context_events") or []
        event_counts_per_row[len(events)] += 1
        rows_with_context += int(bool(events))
        for event in events:
            context_events.append((record, event))

    derivations = Counter(event.get("derivation") for _, event in context_events)
    visible_count = Counter(count_list(event.get("visible_agent_ids")) for _, event in context_events)
    suppressed_count = Counter(count_list(event.get("suppressed_agent_ids")) for _, event in context_events)
    merged_count = Counter(count_list(event.get("merged_agent_ids")) for _, event in context_events)
    transition_by_visible = Counter(
        ((record.get("transition") or {}).get("type"), count_list(event.get("visible_agent_ids")))
        for record, event in context_events
    )
    derivation_by_surface = Counter(
        (
            event.get("derivation"),
            (record.get("public_state") or {}).get("surface"),
            (record.get("public_state") or {}).get("communication_policy"),
        )
        for record, event in context_events
    )

    return {
        "path": str(path),
        "records": len(records),
        "rows_with_context_events": rows_with_context,
        "context_events": len(context_events),
        "methods": counter_dict(method_counts),
        "task_regimes": counter_dict(regime_counts),
        "transitions": counter_dict(transition_counts),
        "public_states": {
            f"{surface}/{policy}": count
            for (surface, policy), count in sorted(surface_counts.items(), key=lambda item: str(item[0]))
        },
        "context_events_per_row": counter_dict(event_counts_per_row),
        "derivations": counter_dict(derivations),
        "visible_agent_count": counter_dict(visible_count),
        "suppressed_agent_count": counter_dict(suppressed_count),
        "merged_agent_count": counter_dict(merged_count),
        "transition_by_visible_agent_count": {
            f"{transition}|visible={visible}": count
            for (transition, visible), count in sorted(transition_by_visible.items(), key=lambda item: str(item[0]))
        },
        "derivation_by_public_state": {
            f"{derivation}|{surface}/{policy}": count
            for (derivation, surface, policy), count in sorted(
                derivation_by_surface.items(), key=lambda item: str(item[0])
            )
        },
    }


def summarize(paths: Iterable[Path]) -> Dict[str, Any]:
    traces = [summarize_trace(path) for path in paths]
    aggregate = {
        "trace_count": len(traces),
        "records": sum(trace["records"] for trace in traces),
        "rows_with_context_events": sum(trace["rows_with_context_events"] for trace in traces),
        "context_events": sum(trace["context_events"] for trace in traces),
    }
    return {"aggregate": aggregate, "traces": traces}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("traces", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    summary = summarize(args.traces)
    text = json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
