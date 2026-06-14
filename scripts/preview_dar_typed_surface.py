#!/usr/bin/env python3
"""Preview typed retained-message surfaces from existing DAR histories."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


CALC_HINTS = (
    "=",
    "\\times",
    "\\frac",
    "\\div",
    " div ",
    "times",
    "subtract",
    "add",
    "cost",
    "total",
    "therefore",
    "so,",
    "thus",
)


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


def answer_only_surface(parsed_answer: Any) -> str:
    return f"Previous parsed final answer: {parsed_answer}"


def normalize_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"^\s*[-*]\s*", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def candidate_lines(text: str) -> List[Dict[str, Any]]:
    lines = [normalize_line(line) for line in text.splitlines()]
    rows = []
    for index, line in enumerate(lines):
        if not line:
            continue
        lower = line.lower()
        if "uncertainty score" in lower:
            continue
        if "{final answer" in lower:
            continue
        has_digit = any(char.isdigit() for char in line)
        if not has_digit:
            continue
        score = 0
        for hint in CALC_HINTS:
            if hint in lower:
                score += 2
        if "=" in line:
            score += 3
        if "$" in line:
            score += 1
        if "final" in lower or "total" in lower:
            score += 1
        if score <= 0:
            continue
        rows.append({"index": index, "line": line, "score": score})
    return rows


def select_evidence_lines(text: str, limit: int) -> List[Dict[str, Any]]:
    rows = candidate_lines(text)
    if not rows:
        return []
    # Keep the last calculation line because these DAR responses often put the
    # decisive subtotal or final computation just before the final-answer marker.
    selected = [rows[-1]]
    ranked = sorted(rows[:-1], key=lambda row: (row["score"], row["index"]), reverse=True)
    for row in ranked:
        if len(selected) >= limit:
            break
        selected.append(row)
    selected = sorted(selected, key=lambda row: row["index"])
    return selected


def typed_surface(agent_id: str, parsed_answer: Any, evidence_lines: List[Dict[str, Any]]) -> str:
    compact = compact_agent_id(agent_id)
    lines = [
        f"source_agent: {compact}",
        f"parsed_final_answer: {parsed_answer}",
    ]
    if evidence_lines:
        lines.append("evidence:")
        for row in evidence_lines:
            lines.append(f"- {row['line']}")
    else:
        lines.append("evidence: <none extracted>")
    return "\n".join(lines)


def public_state(trace_record: Dict[str, Any]) -> Dict[str, Any]:
    state = trace_record.get("public_state") or {}
    return {
        "surface": state.get("surface"),
        "communication_policy": state.get("communication_policy"),
    }


def preview_variant(
    label: str,
    case_index: int,
    history_record: Dict[str, Any],
    trace_record: Dict[str, Any],
    evidence_lines_per_agent: int,
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
        mode = "answer_only" if public_state(trace_record).get("surface") == "retained_answer_only" else "full"

    responses = round0.get("responses") or {}
    parsed_answers = answer_by_agent(round0)
    parsed_correct = correct_by_agent(round0)
    transition = trace_record.get("transition") or {}
    preview_rows = []
    for agent_id in retained_ids:
        full_response = responses.get(agent_id, "")
        parsed_answer = parsed_answers.get(agent_id)
        evidence = select_evidence_lines(full_response, evidence_lines_per_agent)
        answer_surface = answer_only_surface(parsed_answer)
        typed = typed_surface(agent_id, parsed_answer, evidence)
        preview_rows.append(
            {
                "case_index": case_index,
                "label": label,
                "agent_id": compact_agent_id(agent_id),
                "parsed_answer": parsed_answer,
                "parsed_correct": parsed_correct.get(agent_id),
                "original_message_mode": mode,
                "full_response_chars": len(full_response),
                "answer_only_chars": len(answer_surface),
                "typed_surface_chars": len(typed),
                "answer_only_surface": answer_surface,
                "typed_surface": typed,
                "evidence_lines": evidence,
            }
        )

    summary = {
        "label": label,
        "case_index": case_index,
        "instance_id": trace_record.get("instance_id"),
        "gold_answer": trace_record.get("gold_answer") or round0.get("answer"),
        "public_state": public_state(trace_record),
        "transition": transition.get("type"),
        "before_answer": transition.get("before_answer"),
        "after_answer": transition.get("after_answer"),
        "final_correct": (trace_record.get("final") or {}).get("correct", round1.get("debate_answer_iscorr")),
        "original_message_mode": mode,
        "retained_agent_ids": compact_ids(retained_ids),
        "original_retained_agent_ids": compact_ids(original_retained_ids),
        "dropped_agent_ids": compact_ids(dropped_ids),
        "guard_added_agent_ids": compact_ids(guard_added_ids),
        "guard_notes": event.get("guard_notes") or trace_event.get("guard_notes"),
        "round0_answers": round_answers(round0),
        "round1_answers": round_answers(round1),
        "typed_surface_preview": [
            {
                "agent_id": row["agent_id"],
                "parsed_answer": row["parsed_answer"],
                "parsed_correct": row["parsed_correct"],
                "typed_surface_chars": row["typed_surface_chars"],
                "answer_only_chars": row["answer_only_chars"],
                "full_response_chars": row["full_response_chars"],
                "evidence_lines": row["evidence_lines"],
            }
            for row in preview_rows
        ],
    }
    return summary, preview_rows


def summarize(preview_rows: List[Dict[str, Any]], case_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    counters = Counter()
    full_chars = 0
    answer_chars = 0
    typed_chars = 0
    evidence_line_counts = Counter()
    retained_message_count = 0
    for row in preview_rows:
        retained_message_count += 1
        full_chars += row["full_response_chars"]
        answer_chars += row["answer_only_chars"]
        typed_chars += row["typed_surface_chars"]
        evidence_line_counts[len(row["evidence_lines"])] += 1
        counters[f"{row['label']}|{row['original_message_mode']}"] += 1

    case_count = sum(len(case["variants"]) for case in case_summaries)
    return {
        "case_variant_count": case_count,
        "retained_message_count": retained_message_count,
        "retained_messages_by_label_and_original_mode": dict(sorted(counters.items())),
        "avg_full_response_chars": full_chars / retained_message_count if retained_message_count else None,
        "avg_answer_only_chars": answer_chars / retained_message_count if retained_message_count else None,
        "avg_typed_surface_chars": typed_chars / retained_message_count if retained_message_count else None,
        "evidence_line_count_distribution": {str(key): value for key, value in sorted(evidence_line_counts.items())},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-index", action="append", type=int, required=True)
    parser.add_argument("--history", action="append", required=True, help="label=history_jsonl")
    parser.add_argument("--trace", action="append", default=[], help="label=comm_trace_jsonl")
    parser.add_argument("--evidence-lines-per-agent", type=int, default=2)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--preview-out", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.evidence_lines_per_agent < 1:
        raise ValueError("--evidence-lines-per-agent must be positive")

    history_specs = [parse_label_path(value) for value in args.history]
    trace_specs = dict(parse_label_path(value) for value in args.trace)
    histories = {label: load_jsonl(path) for label, path in history_specs}
    traces = {label: load_jsonl(path) for label, path in trace_specs.items()}

    cases = []
    preview_rows = []
    for case_index in args.case_index:
        case_payload = {"case_index": case_index, "variants": {}}
        for label, history_path in history_specs:
            history_rows = histories[label]
            if case_index >= len(history_rows):
                raise IndexError(f"{label} has {len(history_rows)} history rows, cannot read case {case_index}")
            trace_rows = traces.get(label, [])
            trace_record = find_trace_record(trace_rows, case_index) if trace_rows else {}
            summary, rows = preview_variant(
                label,
                case_index,
                history_rows[case_index],
                trace_record,
                args.evidence_lines_per_agent,
            )
            summary["history_path"] = str(history_path)
            summary["trace_path"] = str(trace_specs.get(label)) if label in trace_specs else None
            case_payload["variants"][label] = summary
            preview_rows.extend(rows)
        cases.append(case_payload)

    payload = {
        "case_indices": args.case_index,
        "variant_count": len(history_specs),
        "evidence_lines_per_agent": args.evidence_lines_per_agent,
        "aggregate": summarize(preview_rows, cases),
        "cases": cases,
    }
    write_json(args.summary_out, payload)
    write_jsonl(args.preview_out, preview_rows)


if __name__ == "__main__":
    main()
