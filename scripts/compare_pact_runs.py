#!/usr/bin/env python3
"""Compare two PACT per-sample JSONL runs on the same sample order."""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


FINAL_ANSWER_RE = re.compile(r"[Ff]inal [Aa]nswer\s*[:\-]\s*(.+)")


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


def final_answer_text(row: Dict[str, Any]) -> str:
    raw = row.get("raw_prediction") or ""
    matches = FINAL_ANSWER_RE.findall(raw)
    if matches:
        return matches[-1].strip().rstrip(".")
    return str(row.get("prediction") or "")


def transition(base_correct: bool, variant_correct: bool) -> str:
    if base_correct and variant_correct:
        return "stable_right"
    if base_correct and not variant_correct:
        return "right_to_wrong"
    if (not base_correct) and variant_correct:
        return "wrong_to_right"
    return "stable_wrong"


def mean(values: List[float]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def output_tokens_per_turn(row: Dict[str, Any]) -> List[int]:
    return [int(agent.get("output_tokens", 0)) for agent in row.get("agents", [])]


def compare_case(index: int, base: Dict[str, Any], variant: Dict[str, Any]) -> Dict[str, Any]:
    sample_index = base.get("sample_index", index)
    variant_sample_index = variant.get("sample_index", sample_index)
    if variant_sample_index != sample_index:
        raise ValueError(
            f"sample_index mismatch at row {index}: baseline={sample_index} variant={variant_sample_index}"
        )
    base_correct = bool(base.get("correct"))
    variant_correct = bool(variant.get("correct"))
    base_final = final_answer_text(base)
    variant_final = final_answer_text(variant)
    return {
        "sample_index": sample_index,
        "instance_id": base.get("id"),
        "question": base.get("question"),
        "gold_answer": base.get("gold"),
        "type": base.get("type"),
        "level": base.get("level"),
        "transition": transition(base_correct, variant_correct),
        "baseline_prediction": base.get("prediction"),
        "variant_prediction": variant.get("prediction"),
        "baseline_final_answer_text": base_final,
        "variant_final_answer_text": variant_final,
        "baseline_correct": base_correct,
        "variant_correct": variant_correct,
        "baseline_f1": base.get("f1"),
        "variant_f1": variant.get("f1"),
        "f1_delta": (variant.get("f1", 0.0) or 0.0) - (base.get("f1", 0.0) or 0.0),
        "baseline_final_answer_word_count": len(base_final.split()),
        "variant_final_answer_word_count": len(variant_final.split()),
        "baseline_communication_tokens": base.get("communication_tokens", 0),
        "variant_communication_tokens": variant.get("communication_tokens", 0),
        "communication_token_delta": variant.get("communication_tokens", 0)
        - base.get("communication_tokens", 0),
        "baseline_total_tokens": base.get("total_tokens", 0),
        "variant_total_tokens": variant.get("total_tokens", 0),
        "total_token_delta": variant.get("total_tokens", 0) - base.get("total_tokens", 0),
        "baseline_output_tokens_per_turn": output_tokens_per_turn(base),
        "variant_output_tokens_per_turn": output_tokens_per_turn(variant),
    }


def summarize(cases: List[Dict[str, Any]], focus_indices: List[int]) -> Dict[str, Any]:
    total = len(cases)
    transitions = Counter(case["transition"] for case in cases)
    type_transitions: Dict[str, Counter[str]] = defaultdict(Counter)
    focus_set = set(focus_indices)
    focus_transitions = Counter()

    for case in cases:
        type_transitions[str(case.get("type"))][case["transition"]] += 1
        if case["sample_index"] in focus_set:
            focus_transitions[case["transition"]] += 1

    base_correct = sum(1 for case in cases if case["baseline_correct"])
    variant_correct = sum(1 for case in cases if case["variant_correct"])
    base_f1 = mean([float(case.get("baseline_f1") or 0.0) for case in cases])
    variant_f1 = mean([float(case.get("variant_f1") or 0.0) for case in cases])

    return {
        "records": total,
        "baseline_correct": base_correct,
        "baseline_em": base_correct / total if total else None,
        "variant_correct": variant_correct,
        "variant_em": variant_correct / total if total else None,
        "correct_delta": variant_correct - base_correct,
        "baseline_avg_f1": base_f1,
        "variant_avg_f1": variant_f1,
        "avg_f1_delta": (variant_f1 - base_f1) if base_f1 is not None and variant_f1 is not None else None,
        "transitions": dict(sorted(transitions.items())),
        "type_transitions": {
            key: dict(sorted(value.items())) for key, value in sorted(type_transitions.items())
        },
        "focus_indices": focus_indices,
        "focus_transitions": dict(sorted(focus_transitions.items())),
        "wrong_to_right_cases": [
            case["sample_index"] for case in cases if case["transition"] == "wrong_to_right"
        ],
        "right_to_wrong_cases": [
            case["sample_index"] for case in cases if case["transition"] == "right_to_wrong"
        ],
        "stable_wrong_cases": [
            case["sample_index"] for case in cases if case["transition"] == "stable_wrong"
        ],
        "avg_baseline_final_answer_words": mean(
            [case["baseline_final_answer_word_count"] for case in cases]
        ),
        "avg_variant_final_answer_words": mean(
            [case["variant_final_answer_word_count"] for case in cases]
        ),
        "avg_communication_token_delta": mean(
            [case["communication_token_delta"] for case in cases]
        ),
        "avg_total_token_delta": mean([case["total_token_delta"] for case in cases]),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--variant", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument("--cases-out", type=Path, required=True)
    parser.add_argument("--focus-indices", type=int, nargs="*", default=[])
    return parser


def main() -> None:
    args = build_parser().parse_args()
    baseline = load_jsonl(args.baseline)
    variant = load_jsonl(args.variant)
    if len(baseline) != len(variant):
        raise ValueError(f"run lengths differ: {len(baseline)} vs {len(variant)}")

    cases = [compare_case(index, base, var) for index, (base, var) in enumerate(zip(baseline, variant))]
    write_json(
        args.summary_out,
        {
            "baseline": str(args.baseline),
            "variant": str(args.variant),
            "summary": summarize(cases, args.focus_indices),
        },
    )
    write_jsonl(args.cases_out, cases)


if __name__ == "__main__":
    main()
