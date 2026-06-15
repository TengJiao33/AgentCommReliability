#!/usr/bin/env python3
"""Build paired comparison cards for the PACT typed-boundary split run."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_EVALUATED = Path(
    "experiments/20260615-2223-a8002-pact-typed-boundary-split-qwen25-14b/evaluation/evaluated_rows.jsonl"
)
DEFAULT_OUT_DIR = Path("experiments/20260615-2223-a8002-pact-typed-boundary-split-qwen25-14b/typed_boundary_audit")

BASE_VARIANT = "original_untyped_public"
ANCHORS = ["wrong_contract_public_task", "forged_final_commitment"]
COMPARISONS = [
    ("typed_no_candidate", "typed_candidate_hidden", "no_candidate_vs_hidden"),
    ("typed_no_candidate", "typed_candidate_visible", "no_candidate_vs_visible"),
    ("typed_candidate_visible", "typed_candidate_visible_extract_first", "visible_vs_extract_first"),
    (
        "typed_wrong_contract_no_candidate",
        "typed_wrong_contract_candidate_hidden",
        "wrong_contract_no_candidate_vs_hidden",
    ),
    (
        "typed_wrong_contract_no_candidate",
        "typed_wrong_contract_candidate_visible",
        "wrong_contract_no_candidate_vs_visible",
    ),
    (
        "typed_wrong_contract_candidate_visible",
        "typed_wrong_contract_candidate_visible_extract_first",
        "wrong_contract_visible_vs_extract_first",
    ),
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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


def outcome(left_correct: bool, right_correct: bool) -> str:
    if left_correct and right_correct:
        return "both_right"
    if left_correct and not right_correct:
        return "right_regression"
    if not left_correct and right_correct:
        return "right_repair"
    return "both_wrong"


def pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def summarize_group(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "records": 0,
            "base_correct_records": 0,
            "outcomes": {},
            "right_regression_rate_on_left_correct": None,
            "right_repair_rate_on_left_wrong": None,
            "right_candidate_copy_count": 0,
        }
    left_correct = [row for row in rows if row.get("left_correct")]
    left_wrong = [row for row in rows if not row.get("left_correct")]
    right_regressions = [row for row in left_correct if not row.get("right_correct")]
    right_repairs = [row for row in left_wrong if row.get("right_correct")]
    return {
        "records": len(rows),
        "base_correct_records": sum(1 for row in rows if row.get("base_correct")),
        "outcomes": dict(sorted(Counter(str(row["comparison_outcome"]) for row in rows).items())),
        "avg_right_minus_left_f1": (
            sum(float(row["right_f1"]) - float(row["left_f1"]) for row in rows) / len(rows)
        ),
        "right_regression_count_on_left_correct": len(right_regressions),
        "right_regression_rate_on_left_correct": (
            len(right_regressions) / len(left_correct) if left_correct else None
        ),
        "right_repair_count_on_left_wrong": len(right_repairs),
        "right_repair_rate_on_left_wrong": len(right_repairs) / len(left_wrong) if left_wrong else None,
        "right_candidate_copy_count": sum(1 for row in rows if row.get("right_visible_candidate_copy")),
        "right_candidate_copy_rate": (
            sum(1 for row in rows if row.get("right_visible_candidate_copy")) / len(rows)
        ),
    }


def make_cards(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_case: dict[str, dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_case[str(row["case_id"])][str(row["variant"])] = row

    cards: list[dict[str, Any]] = []
    for case_id, variants in sorted(by_case.items()):
        base = variants.get(BASE_VARIANT)
        if not base:
            continue
        anchor_failures = {
            anchor: bool(base.get("exact_match")) and not bool(variants.get(anchor, {}).get("exact_match"))
            for anchor in ANCHORS
        }
        for left_variant, right_variant, comparison in COMPARISONS:
            left = variants.get(left_variant)
            right = variants.get(right_variant)
            if not left or not right:
                continue
            left_correct = bool(left.get("exact_match"))
            right_correct = bool(right.get("exact_match"))
            cards.append({
                "case_id": case_id,
                "comparison": comparison,
                "source_type": right.get("source_type"),
                "semantic_family": right.get("semantic_family"),
                "bridge_layer": right.get("bridge_layer"),
                "gold_answer": right.get("gold_answer"),
                "base_correct": bool(base.get("exact_match")),
                "anchor_failures": anchor_failures,
                "left_variant": left_variant,
                "left_prediction": left.get("prediction"),
                "left_correct": left_correct,
                "left_f1": left.get("f1"),
                "right_variant": right_variant,
                "right_prediction": right.get("prediction"),
                "right_correct": right_correct,
                "right_f1": right.get("f1"),
                "right_candidate_text": right.get("candidate_text"),
                "right_visible_candidate_copy": bool(right.get("visible_candidate_copy")),
                "right_hidden_candidate_match": bool(right.get("hidden_candidate_match")),
                "comparison_outcome": outcome(left_correct, right_correct),
            })
    return cards


def group_by(cards: list[Mapping[str, Any]], *keys: str) -> dict[str, dict[str, Any]]:
    groups: dict[tuple[str, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in cards:
        groups[tuple("" if row.get(key) is None else str(row.get(key)) for key in keys)].append(row)
    return {" | ".join(key): summarize_group(group_rows) for key, group_rows in sorted(groups.items())}


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# PACT Typed Boundary Split Audit",
        "",
        f"- Records: `{summary['records']}`",
        "",
        "## By Comparison",
        "",
        "| Comparison | Records | Outcomes | Avg F1 delta | Regression | Repair | Copy |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for key, row in summary["by_comparison"].items():
        lines.append(
            f"| {key} | {row['records']} | `{row['outcomes']}` | "
            f"{row['avg_right_minus_left_f1']:.3f} | "
            f"{pct(row.get('right_regression_rate_on_left_correct'))} | "
            f"{pct(row.get('right_repair_rate_on_left_wrong'))} | "
            f"{pct(row.get('right_candidate_copy_rate'))} |"
        )
    lines.extend([
        "",
        "## Positive Target-Focus Comparisons",
        "",
        "| Comparison | Records | Outcomes | Avg F1 delta | Regression | Repair | Copy |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
    ])
    for key, row in summary["by_source_type_comparison"].items():
        if not key.startswith("positive_target_focus"):
            continue
        comparison = key.split(" | ", 1)[1]
        lines.append(
            f"| {comparison} | {row['records']} | `{row['outcomes']}` | "
            f"{row['avg_right_minus_left_f1']:.3f} | "
            f"{pct(row.get('right_regression_rate_on_left_correct'))} | "
            f"{pct(row.get('right_repair_rate_on_left_wrong'))} | "
            f"{pct(row.get('right_candidate_copy_rate'))} |"
        )
    lines.append("")
    return "\n".join(lines)


def build(args: argparse.Namespace) -> dict[str, Any]:
    rows = load_jsonl(args.evaluated)
    cards = make_cards(rows)
    summary = {
        "evaluated": str(args.evaluated),
        "records": len(cards),
        "by_comparison": group_by(cards, "comparison"),
        "by_source_type_comparison": group_by(cards, "source_type", "comparison"),
        "by_semantic_family_comparison": group_by(cards, "semantic_family", "comparison"),
        "note": (
            "Pairwise cards compare no-candidate, hidden-candidate, visible-candidate, "
            "and extract-first typed-boundary arms within each case."
        ),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "typed_boundary_delta_cards.jsonl", cards)
    write_json(args.out_dir / "typed_boundary_delta_summary.json", summary)
    write_text(args.out_dir / "typed_boundary_delta_summary.md", render_markdown(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluated", type=Path, default=DEFAULT_EVALUATED)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
