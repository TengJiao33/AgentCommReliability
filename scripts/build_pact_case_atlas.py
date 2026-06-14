#!/usr/bin/env python3
"""Build a compact case atlas for paired PACT runs."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
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


def normalize(text: Any) -> str:
    text = "" if text is None else str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def final_event_contains_gold(arbitration_case: Dict[str, Any]) -> bool:
    gold = normalize(arbitration_case.get("gold_answer"))
    if not gold:
        return False
    event = arbitration_case.get("final_event") or {}
    haystack = normalize(" ".join(str(event.get(key) or "") for key in (
        "action_required",
        "environment_state",
        "action_result",
        "final_answer",
    )))
    return gold in haystack


def public_policy_correct(arbitration_case: Dict[str, Any]) -> bool:
    return any(
        bool(arbitration_case.get(key))
        for key in (
            "question_aware_policy_correct",
            "final_event_arbitration_policy_correct",
            "all_public_state_arbitration_policy_correct",
            "guarded_final_event_arbitration_policy_correct",
            "guarded_all_public_state_arbitration_policy_correct",
        )
    )


def label_case(change: Dict[str, Any], arbitration_case: Dict[str, Any]) -> str:
    transition = change.get("transition")
    base_f1 = float(change.get("baseline_f1") or 0.0)
    variant_f1 = float(change.get("variant_f1") or 0.0)
    base_words = int(change.get("baseline_final_answer_word_count") or 0)
    variant_words = int(change.get("variant_final_answer_word_count") or 0)

    if transition == "wrong_to_right":
        if base_f1 > 0 and variant_words < base_words:
            return "contract_rescued_verbose_surface"
        return "contract_rescued_content_or_field"

    if transition == "right_to_wrong":
        if variant_f1 >= 0.85:
            return "strict_span_regression"
        return "content_drift_regression"

    if transition == "stable_wrong":
        if public_policy_correct(arbitration_case):
            return "recoverable_from_public_state_policy"
        if final_event_contains_gold(arbitration_case):
            return "final_public_state_contains_gold"
        if variant_f1 >= 0.7 or variant_f1 - base_f1 >= 0.15:
            return "near_miss_surface_or_span"
        return "likely_evidence_or_reasoning_failure"

    return "stable_right"


def compact_case(change: Dict[str, Any], arbitration_case: Dict[str, Any]) -> Dict[str, Any]:
    label = label_case(change, arbitration_case)
    event = arbitration_case.get("final_event") or {}
    return {
        "sample_index": change.get("sample_index"),
        "transition": change.get("transition"),
        "atlas_label": label,
        "question": change.get("question"),
        "gold_answer": change.get("gold_answer"),
        "baseline_final_answer_text": change.get("baseline_final_answer_text"),
        "variant_final_answer_text": change.get("variant_final_answer_text"),
        "baseline_correct": change.get("baseline_correct"),
        "variant_correct": change.get("variant_correct"),
        "baseline_f1": change.get("baseline_f1"),
        "variant_f1": change.get("variant_f1"),
        "f1_delta": change.get("f1_delta"),
        "baseline_final_answer_word_count": change.get("baseline_final_answer_word_count"),
        "variant_final_answer_word_count": change.get("variant_final_answer_word_count"),
        "question_contract": arbitration_case.get("question_contract"),
        "final_event_contains_gold": final_event_contains_gold(arbitration_case),
        "question_aware_policy_correct": arbitration_case.get("question_aware_policy_correct"),
        "final_event_arbitration_policy_correct": arbitration_case.get("final_event_arbitration_policy_correct"),
        "all_public_state_arbitration_policy_correct": arbitration_case.get("all_public_state_arbitration_policy_correct"),
        "guarded_final_event_arbitration_policy_correct": arbitration_case.get("guarded_final_event_arbitration_policy_correct"),
        "final_event": {
            "action_required": event.get("action_required"),
            "environment_state": event.get("environment_state"),
            "action_result": event.get("action_result"),
            "final_answer": event.get("final_answer"),
        },
    }


def build(args: argparse.Namespace) -> Dict[str, Any]:
    analysis = load_json(args.analysis_summary)
    changes = load_jsonl(args.changed_cases)
    arbitration_cases = {
        row["sample_index"]: row
        for row in load_jsonl(args.arbitration_cases)
    }
    atlas_cases = [
        compact_case(change, arbitration_cases.get(change.get("sample_index"), {}))
        for change in changes
    ]
    focus_cases = [
        row for row in atlas_cases
        if row["transition"] != "stable_right"
    ]
    labels = Counter(row["atlas_label"] for row in atlas_cases)
    focus_labels = Counter(row["atlas_label"] for row in focus_cases)
    transitions_by_label: Dict[str, Counter[str]] = {}
    for row in atlas_cases:
        transitions_by_label.setdefault(row["atlas_label"], Counter())
        transitions_by_label[row["atlas_label"]][row["transition"]] += 1

    summary = {
        "analysis_summary": analysis.get("summary", {}),
        "records": len(atlas_cases),
        "focus_records": len(focus_cases),
        "label_counts": dict(sorted(labels.items())),
        "focus_label_counts": dict(sorted(focus_labels.items())),
        "transitions_by_label": {
            label: dict(sorted(counter.items()))
            for label, counter in sorted(transitions_by_label.items())
        },
        "sample_indices_by_label": {
            label: [row["sample_index"] for row in atlas_cases if row["atlas_label"] == label]
            for label in sorted(labels)
        },
        "note": (
            "Labels are rough mechanical buckets for inspection. They are not "
            "ground-truth error taxonomy."
        ),
    }
    write_json(args.summary_out, summary)
    write_jsonl(args.cases_out, atlas_cases)
    write_jsonl(args.focus_out, focus_cases)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-summary", type=Path, required=True)
    parser.add_argument("--changed-cases", type=Path, required=True)
    parser.add_argument("--arbitration-cases", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, required=True)
    parser.add_argument("--focus-out", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
