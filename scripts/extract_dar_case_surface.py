#!/usr/bin/env python3
"""Extract DAR raw retained-message surfaces for selected cases."""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


SNIPPET_TERMS = ("7.00", "$7.00", "0.30", "$0.30", "0.80", "$0.80", "120", "700")


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
    if "=" not in value:
        raise ValueError(f"Expected label=path, got: {value}")
    label, path = value.split("=", 1)
    return label, Path(path)


def compact_agent_id(agent_id: Optional[str]) -> Optional[str]:
    if not agent_id:
        return agent_id
    if "__" in agent_id:
        return agent_id.rsplit("__", 1)[-1]
    return agent_id


def compact_ids(agent_ids: Iterable[str]) -> List[str]:
    return [str(compact_agent_id(agent_id)) for agent_id in agent_ids]


def first_dict(items: Any) -> Dict[str, Any]:
    if isinstance(items, list) and items and isinstance(items[0], dict):
        return items[0]
    return {}


def history_round(record: Dict[str, Any], round_index: int) -> Dict[str, Any]:
    return record.get(str(round_index)) or {}


def response_order(round_data: Dict[str, Any]) -> List[str]:
    responses = round_data.get("responses") or {}
    if isinstance(responses, dict):
        return list(responses.keys())
    return []


def answer_by_agent(round_data: Dict[str, Any]) -> Dict[str, Any]:
    answers = round_data.get("final_answers") or []
    agents = response_order(round_data)
    return {agent: answers[index] if index < len(answers) else None for index, agent in enumerate(agents)}


def correct_by_agent(round_data: Dict[str, Any]) -> Dict[str, Any]:
    correctness = round_data.get("final_answer_iscorr") or []
    agents = response_order(round_data)
    return {agent: correctness[index] if index < len(correctness) else None for index, agent in enumerate(agents)}


def round_answers(round_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    answers = answer_by_agent(round_data)
    correctness = correct_by_agent(round_data)
    return [
        {
            "agent_id": compact_agent_id(agent),
            "answer": answers.get(agent),
            "correct": correctness.get(agent),
        }
        for agent in response_order(round_data)
    ]


def find_trace_record(trace_rows: List[Dict[str, Any]], case_index: int) -> Dict[str, Any]:
    for row in trace_rows:
        if row.get("sample_index") == case_index or str(row.get("instance_id")) == str(case_index):
            return row
    if case_index < len(trace_rows):
        return trace_rows[case_index]
    return {}


def compact_public_state(trace_record: Dict[str, Any]) -> Dict[str, Any]:
    public_state = trace_record.get("public_state") or {}
    return {
        "surface": public_state.get("surface"),
        "communication_policy": public_state.get("communication_policy"),
    }


def snippet(text: str, term: str, radius: int = 140) -> Optional[str]:
    lower_text = text.lower()
    lower_term = term.lower()
    index = lower_text.find(lower_term)
    if index < 0:
        return None
    start = max(0, index - radius)
    end = min(len(text), index + len(term) + radius)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return prefix + text[start:end].replace("\n", "\\n") + suffix


def term_snippets(text: str) -> Dict[str, str]:
    hits = {}
    for term in SNIPPET_TERMS:
        hit = snippet(text, term)
        if hit:
            hits[term] = hit
    return hits


def constructed_surface(mode: Optional[str], parsed_answer: Any, full_response: str) -> str:
    if mode == "answer_only":
        return f"Previous parsed final answer: {parsed_answer}"
    return full_response


def extract_variant(
    label: str,
    case_index: int,
    history_record: Dict[str, Any],
    trace_record: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    round0 = history_round(history_record, 0)
    round1 = history_round(history_record, 1)
    event = first_dict(round1.get("retention_events"))
    trace_event = first_dict(trace_record.get("retention_events"))
    context_event = first_dict(trace_record.get("context_events"))
    retained_ids = event.get("retained_agent_ids") or trace_event.get("retained_agent_ids") or []
    original_retained_ids = event.get("original_retained_agent_ids") or trace_event.get("original_retained_agent_ids") or []
    dropped_ids = event.get("dropped_agent_ids") or trace_event.get("dropped_agent_ids") or []
    guard_added_ids = event.get("guard_added_agent_ids") or trace_event.get("guard_added_agent_ids") or []
    mode = event.get("retention_message_mode") or trace_event.get("retention_message_mode")
    if not mode:
        mode = context_event.get("retention_message_mode")
    if not mode:
        surface = (trace_record.get("public_state") or {}).get("surface")
        mode = "answer_only" if surface == "retained_answer_only" else "full"

    responses = round0.get("responses") or {}
    parsed_answers = answer_by_agent(round0)
    parsed_correct = correct_by_agent(round0)
    message_rows = []
    retained_summary = []
    for agent_id in retained_ids:
        full_response = responses.get(agent_id, "")
        parsed_answer = parsed_answers.get(agent_id)
        surface_text = constructed_surface(mode, parsed_answer, full_response)
        message_rows.append(
            {
                "case_index": case_index,
                "label": label,
                "agent_id": compact_agent_id(agent_id),
                "retention_message_mode": mode,
                "parsed_answer": parsed_answer,
                "parsed_correct": parsed_correct.get(agent_id),
                "full_response": full_response,
                "constructed_surface": surface_text,
            }
        )
        retained_summary.append(
            {
                "agent_id": compact_agent_id(agent_id),
                "parsed_answer": parsed_answer,
                "parsed_correct": parsed_correct.get(agent_id),
                "full_response_chars": len(full_response),
                "constructed_surface_chars": len(surface_text),
                "constructed_surface_excerpt": surface_text[:500].replace("\n", "\\n"),
                "term_snippets_from_full_response": term_snippets(full_response),
            }
        )

    transition = trace_record.get("transition") or {}
    summary = {
        "label": label,
        "case_index": case_index,
        "instance_id": trace_record.get("instance_id"),
        "gold_answer": trace_record.get("gold_answer") or round0.get("answer"),
        "public_state": compact_public_state(trace_record),
        "transition": transition.get("type"),
        "before_answer": transition.get("before_answer"),
        "after_answer": transition.get("after_answer"),
        "final_correct": (trace_record.get("final") or {}).get("correct", round1.get("debate_answer_iscorr")),
        "retention_message_mode": mode,
        "retained_agent_ids": compact_ids(retained_ids),
        "original_retained_agent_ids": compact_ids(original_retained_ids),
        "dropped_agent_ids": compact_ids(dropped_ids),
        "guard_added_agent_ids": compact_ids(guard_added_ids),
        "guard_notes": event.get("guard_notes") or trace_event.get("guard_notes"),
        "raw_filter_response": event.get("raw_filter_response") or trace_event.get("raw_filter_response"),
        "round0_answers": round_answers(round0),
        "round1_answers": round_answers(round1),
        "retained_messages": retained_summary,
    }
    return summary, message_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-index", action="append", type=int, required=True)
    parser.add_argument("--history", action="append", required=True, help="label=history_jsonl")
    parser.add_argument("--trace", action="append", default=[], help="label=comm_trace_jsonl")
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--messages-out", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    history_specs = [parse_label_path(value) for value in args.history]
    trace_specs = dict(parse_label_path(value) for value in args.trace)
    histories = {label: load_jsonl(path) for label, path in history_specs}
    traces = {label: load_jsonl(path) for label, path in trace_specs.items()}

    cases = []
    messages = []
    for case_index in args.case_index:
        case_payload = {"case_index": case_index, "variants": {}}
        for label, history_path in history_specs:
            history_rows = histories[label]
            if case_index >= len(history_rows):
                raise IndexError(f"{label} has {len(history_rows)} history rows, cannot read case {case_index}")
            trace_rows = traces.get(label, [])
            trace_record = find_trace_record(trace_rows, case_index) if trace_rows else {}
            summary, message_rows = extract_variant(label, case_index, history_rows[case_index], trace_record)
            summary["history_path"] = str(history_path)
            summary["trace_path"] = str(trace_specs.get(label)) if label in trace_specs else None
            case_payload["variants"][label] = summary
            messages.extend(message_rows)
        cases.append(case_payload)

    payload = {
        "case_indices": args.case_index,
        "variant_count": len(history_specs),
        "cases": cases,
    }
    write_json(args.summary_out, payload)
    write_jsonl(args.messages_out, messages)


if __name__ == "__main__":
    main()
