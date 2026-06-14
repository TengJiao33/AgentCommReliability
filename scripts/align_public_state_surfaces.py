#!/usr/bin/env python3
"""Align DAR typed-surface previews with PACT action-state records."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


FIELD_NAMES = ("Action Required", "Environment State", "Action Result", "Final Answer")


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


def extract_field(text: str, field_name: str) -> Optional[str]:
    pattern = rf"(?m)^{re.escape(field_name)}:\s*(.*)$"
    match = re.search(pattern, text)
    if not match:
        return None
    return match.group(1).strip()


def strip_think(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"</?think>", "", text)
    return text.strip()


def compact_agent_id(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value)
    if "__" in text:
        return text.rsplit("__", 1)[-1]
    return text


def state_text_from_fields(fields: Dict[str, Optional[str]]) -> str:
    lines = []
    for field_name in ("Action Required", "Environment State", "Action Result"):
        value = fields.get(field_name)
        if value:
            lines.append(f"{field_name}: {value}")
    final = fields.get("Final Answer")
    if final:
        lines.append(f"Final Answer: {final}")
    return "\n".join(lines)


def pact_records(path: Path) -> List[Dict[str, Any]]:
    rows = []
    for sample in load_jsonl(path):
        for agent in sample.get("agents") or []:
            output = agent.get("output") or ""
            public_output = strip_think(output)
            fields = {field_name: extract_field(public_output, field_name) for field_name in FIELD_NAMES}
            rows.append(
                {
                    "schema_version": "acr.public_state_surface.v0",
                    "source_family": "PACT",
                    "source_path": str(path),
                    "sample_id": sample.get("id"),
                    "case_index": None,
                    "actor": agent.get("name"),
                    "turn": agent.get("turn"),
                    "is_final": agent.get("is_final"),
                    "surface": "action_state",
                    "communication_policy": "alternating_action_state",
                    "field_source": "generated_public_message",
                    "private_reasoning_policy": "strip_think_tags_before_shared_history",
                    "has_think_span": "<think>" in output or "</think>" in output,
                    "action_required": fields["Action Required"],
                    "environment_state": fields["Environment State"],
                    "action_result": fields["Action Result"],
                    "final_answer": fields["Final Answer"],
                    "state_text": state_text_from_fields(fields),
                    "state_chars": len(public_output),
                    "raw_output_chars": len(output),
                    "field_presence": {
                        field_name: fields[field_name] is not None for field_name in FIELD_NAMES
                    },
                    "gold": sample.get("gold"),
                    "prediction": sample.get("prediction"),
                    "correct": sample.get("correct"),
                }
            )
    return rows


def dar_records(path: Path) -> List[Dict[str, Any]]:
    rows = []
    for row in load_jsonl(path):
        evidence_lines = row.get("evidence_lines") or []
        evidence = " ".join(str(item.get("line", "")).strip() for item in evidence_lines).strip()
        action_result = f"parsed_final_answer: {row.get('parsed_answer')}"
        state_text = row.get("typed_surface") or ""
        rows.append(
            {
                "schema_version": "acr.public_state_surface.v0",
                "source_family": "DAR",
                "source_path": str(path),
                "sample_id": None,
                "case_index": row.get("case_index"),
                "actor": compact_agent_id(row.get("agent_id")),
                "turn": 1,
                "is_final": False,
                "surface": "typed_answer_evidence_preview",
                "communication_policy": "retained_subset_or_guarded_retained_subset",
                "field_source": "heuristic_from_retained_response",
                "private_reasoning_policy": "full_response_not_forwarded_in_preview",
                "has_think_span": False,
                "action_required": "Use this retained peer state as evidence while revising the answer.",
                "environment_state": evidence or None,
                "action_result": action_result,
                "final_answer": None,
                "state_text": state_text,
                "state_chars": row.get("typed_surface_chars"),
                "raw_output_chars": row.get("full_response_chars"),
                "field_presence": {
                    "Action Required": True,
                    "Environment State": bool(evidence),
                    "Action Result": row.get("parsed_answer") is not None,
                    "Final Answer": False,
                },
                "parsed_answer": row.get("parsed_answer"),
                "parsed_correct": row.get("parsed_correct"),
                "original_label": row.get("label"),
                "original_message_mode": row.get("original_message_mode"),
            }
        )
    return rows


def average(values: List[int]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_family = Counter(record["source_family"] for record in records)
    by_surface = Counter(record["surface"] for record in records)
    think_spans = Counter(str(record["has_think_span"]) for record in records)
    field_presence = {field_name: Counter() for field_name in FIELD_NAMES}
    state_chars_by_family: Dict[str, List[int]] = {}
    raw_chars_by_family: Dict[str, List[int]] = {}
    for record in records:
        family = record["source_family"]
        state_chars_by_family.setdefault(family, []).append(int(record.get("state_chars") or 0))
        raw_chars_by_family.setdefault(family, []).append(int(record.get("raw_output_chars") or 0))
        presence = record.get("field_presence") or {}
        for field_name in FIELD_NAMES:
            field_presence[field_name][str(bool(presence.get(field_name)))] += 1

    return {
        "records": len(records),
        "by_family": dict(sorted(by_family.items())),
        "by_surface": dict(sorted(by_surface.items())),
        "has_think_span": dict(sorted(think_spans.items())),
        "field_presence": {
            field_name: dict(sorted(counter.items())) for field_name, counter in field_presence.items()
        },
        "avg_state_chars_by_family": {
            family: average(values) for family, values in sorted(state_chars_by_family.items())
        },
        "avg_raw_output_chars_by_family": {
            family: average(values) for family, values in sorted(raw_chars_by_family.items())
        },
        "alignment_gaps": [
            "DAR typed previews map parsed answers to Action Result and selected calculation lines to Environment State, but Action Required is synthetic rather than generated or task-specific.",
            "PACT Environment State is intended to be a verbatim evidence sentence from private context; DAR Environment State is heuristic text extracted from a generated retained response.",
            "PACT has an explicit strip-think public-history rule; DAR typed preview currently has only an offline promise not to forward the full response.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dar-preview", type=Path, required=True)
    parser.add_argument("--pact-result", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--records-out", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    records = dar_records(args.dar_preview) + pact_records(args.pact_result)
    payload = {
        "inputs": {
            "dar_preview": str(args.dar_preview),
            "pact_result": str(args.pact_result),
        },
        "summary": summarize(records),
    }
    write_json(args.summary_out, payload)
    write_jsonl(args.records_out, records)


if __name__ == "__main__":
    main()
