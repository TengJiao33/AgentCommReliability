#!/usr/bin/env python3
"""Audit strict-span and granularity errors in evaluated PACT field packets."""

from __future__ import annotations

import argparse
import json
import re
import string
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


DEFAULT_EVALUATED = Path(
    "experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/evaluation/evaluated_rows.jsonl"
)
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-final-span-granularity")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize_answer(value: Optional[str]) -> str:
    if value is None:
        return ""

    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text: str) -> str:
        return " ".join(text.split())

    def remove_punc(text: str) -> str:
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    return white_space_fix(remove_articles(remove_punc(str(value).lower())))


def token_counter(text: Optional[str]) -> Counter[str]:
    return Counter(normalize_answer(text).split())


def token_count(counter: Counter[str]) -> int:
    return sum(counter.values())


def is_subset(left: Counter[str], right: Counter[str]) -> bool:
    return bool(left) and all(right[token] >= count for token, count in left.items())


def classify_span(prediction: Optional[str], gold: Optional[str], exact_match: bool, f1: float) -> str:
    if exact_match:
        return "exact"
    pred = token_counter(prediction)
    gold_counter = token_counter(gold)
    pred_len = token_count(pred)
    gold_len = token_count(gold_counter)
    if pred_len == 0:
        return "empty_prediction"
    if gold_len == 0:
        return "empty_gold"
    if is_subset(pred, gold_counter) and f1 >= 0.45:
        return "missing_required_token_or_qualifier"
    if is_subset(gold_counter, pred) and f1 >= 0.45:
        return "over_specific_or_sentence_expansion"
    if f1 >= 0.75:
        return "high_overlap_strict_span_mismatch"
    if f1 >= 0.45:
        return "partial_overlap_possible_alias_or_type"
    return "content_mismatch"


def group_by(rows: Iterable[Mapping[str, Any]], *keys: str) -> Dict[str, Dict[str, int]]:
    grouped: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        key = " | ".join(str(row.get(key_name)) for key_name in keys)
        grouped[key][str(row["span_error_family"])] += 1
    return {key: dict(sorted(counter.items())) for key, counter in sorted(grouped.items())}


def summarize_numeric(rows: List[Mapping[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    exact = sum(1 for row in rows if row["span_error_family"] == "exact")
    strictish = [
        row for row in rows
        if row["span_error_family"]
        in {
            "missing_required_token_or_qualifier",
            "over_specific_or_sentence_expansion",
            "high_overlap_strict_span_mismatch",
        }
    ]
    return {
        "records": total,
        "exact": exact,
        "exact_match": exact / total if total else 0.0,
        "strict_span_or_granularity_errors": len(strictish),
        "strict_span_or_granularity_error_rate": len(strictish) / total if total else 0.0,
        "avg_f1": sum(float(row.get("f1") or 0.0) for row in rows) / total if total else 0.0,
    }


def md_cell(value: Any) -> str:
    return " ".join(("" if value is None else str(value)).split()).replace("|", "\\|")


def render_family_table(title: str, rows: Mapping[str, Mapping[str, int]]) -> List[str]:
    families = sorted({family for counter in rows.values() for family in counter})
    lines = [
        f"## {title}",
        "",
        "| Slice | " + " | ".join(families) + " |",
        "| --- | " + " | ".join("---:" for _ in families) + " |",
    ]
    for key, counter in rows.items():
        lines.append(
            "| {key} | {values} |".format(
                key=md_cell(key),
                values=" | ".join(str(counter.get(family, 0)) for family in families),
            )
        )
    lines.append("")
    return lines


def render_examples(title: str, rows: List[Mapping[str, Any]]) -> List[str]:
    lines = [
        f"## {title}",
        "",
        "| Sample | Source | Condition | Family | F1 | Gold | Prediction |",
        "| ---: | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows[:30]:
        lines.append(
            "| {sample} | {source} | {condition} | {family} | {f1:.3f} | {gold} | {pred} |".format(
                sample=row["sample_index"],
                source=md_cell(row["source_run"]),
                condition=md_cell(row["condition"]),
                family=md_cell(row["span_error_family"]),
                f1=float(row.get("f1") or 0.0),
                gold=md_cell(row.get("gold_answer")),
                pred=md_cell(row.get("prediction")),
            )
        )
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# PACT Final-Span And Granularity Audit",
        "",
        f"- Label: `{summary['label']}`",
        f"- Evaluated rows: `{summary['overall']['records']}`",
        f"- Exact match: `{summary['overall']['exact_match']:.3f}`",
        f"- Avg F1: `{summary['overall']['avg_f1']:.3f}`",
        f"- Strict-span/granularity errors: `{summary['overall']['strict_span_or_granularity_errors']}`",
        "",
    ]
    lines.extend(render_family_table("By Condition", summary["by_condition"]))
    lines.extend(render_family_table("By Bridge Layer", summary["by_bridge_layer"]))
    lines.extend(render_family_table("By Source Run", summary["by_source_run"]))
    lines.extend(render_examples("Highest-F1 Non-Exact Rows", summary["high_f1_non_exact_rows"]))
    lines.extend([
        "## Caveat",
        "",
        "This audit uses gold answers and is an evaluation diagnostic, not a runtime verifier.",
        "It separates strict-span and granularity pressure from clear content errors before another behavioral run.",
        "",
    ])
    return "\n".join(lines)


def annotate(rows: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    annotated: List[Dict[str, Any]] = []
    for row in rows:
        f1 = float(row.get("f1") or 0.0)
        exact_match = bool(row.get("exact_match"))
        family = classify_span(
            row.get("prediction"),
            row.get("gold_answer"),
            exact_match,
            f1,
        )
        annotated.append({
            **dict(row),
            "span_error_family": family,
            "prediction_token_count": token_count(token_counter(row.get("prediction"))),
            "gold_token_count": token_count(token_counter(row.get("gold_answer"))),
        })
    return annotated


def build(args: argparse.Namespace) -> Dict[str, Any]:
    rows = annotate(load_jsonl(args.evaluated))
    high_f1_non_exact = sorted(
        [row for row in rows if row["span_error_family"] != "exact"],
        key=lambda row: (-float(row.get("f1") or 0.0), int(row["sample_index"]), str(row["source_run"])),
    )
    summary = {
        "label": args.label,
        "evaluated": str(args.evaluated),
        "overall": summarize_numeric(rows),
        "family_counts": dict(sorted(Counter(row["span_error_family"] for row in rows).items())),
        "by_condition": group_by(rows, "condition"),
        "by_bridge_layer": group_by(rows, "bridge_layer"),
        "by_source_run": group_by(rows, "source_run"),
        "high_f1_non_exact_rows": high_f1_non_exact[:30],
        "note": (
            "Gold answers are used for evaluation-family labels only; do not use this as "
            "a runtime answer verifier."
        ),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "span_granularity_rows.jsonl", rows)
    write_jsonl(args.out_dir / "high_f1_non_exact_rows.jsonl", high_f1_non_exact)
    write_text(args.out_dir / "summary.md", render_markdown(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluated", type=Path, default=DEFAULT_EVALUATED)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--label", default="pact-field-contract-quarantine")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
