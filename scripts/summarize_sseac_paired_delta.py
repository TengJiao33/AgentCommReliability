#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PG40_METRICS = [
    "strict_pass",
    "required_coverage",
    "boundary_precision",
    "distractor_leakage",
    "budget_pass",
    "budget_overrun",
    "utility_ratio",
    "exact_target_role_rate",
]

HSA_METRICS = [
    "strict",
    "slot_recall",
    "extra_final_card_count",
    "forced_commitment_detected",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, blob: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def row_id(row: dict[str, Any], benchmark: str) -> str:
    if benchmark == "pg40":
        return str(row.get("hard_evaluation_id", ""))
    return str(row.get("packet_id", ""))


def metric_value(row: dict[str, Any], metric: str, benchmark: str) -> float | None:
    value: Any
    if benchmark == "pg40":
        value = row.get("metrics", {}).get(metric)
        if value is None:
            value = row.get("tight_budget", {}).get(metric)
    else:
        value = row.get(metric)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def summarize_pair(
    no_compiler_rows: list[dict[str, Any]],
    compiled_rows: list[dict[str, Any]],
    benchmark: str,
) -> dict[str, Any]:
    metrics = PG40_METRICS if benchmark == "pg40" else HSA_METRICS
    no_by_id = {row_id(row, benchmark): row for row in no_compiler_rows}
    compiled_by_id = {row_id(row, benchmark): row for row in compiled_rows}
    paired_ids = sorted(set(no_by_id) & set(compiled_by_id))
    paired_ids = [item for item in paired_ids if item]
    missing_no_compiler = sorted((set(compiled_by_id) - set(no_by_id)) - {""})
    missing_compiled = sorted((set(no_by_id) - set(compiled_by_id)) - {""})

    metric_summary: dict[str, Any] = {}
    for metric in metrics:
        no_values: list[float] = []
        compiled_values: list[float] = []
        deltas: list[float] = []
        improved = 0
        worsened = 0
        tied = 0
        for item in paired_ids:
            no_value = metric_value(no_by_id[item], metric, benchmark)
            compiled_value = metric_value(compiled_by_id[item], metric, benchmark)
            if no_value is None or compiled_value is None:
                continue
            delta = compiled_value - no_value
            no_values.append(no_value)
            compiled_values.append(compiled_value)
            deltas.append(delta)
            if delta > 0:
                improved += 1
            elif delta < 0:
                worsened += 1
            else:
                tied += 1
        metric_summary[metric] = {
            "paired_values": len(deltas),
            "structured_no_compiler_mean": mean(no_values),
            "compiled_mean": mean(compiled_values),
            "delta_mean": mean(deltas),
            "improved_rows": improved,
            "worsened_rows": worsened,
            "tied_rows": tied,
        }

    return {
        "benchmark": benchmark,
        "paired_rows": len(paired_ids),
        "no_compiler_rows": len(no_compiler_rows),
        "compiled_rows": len(compiled_rows),
        "missing_no_compiler": missing_no_compiler,
        "missing_compiled": missing_compiled,
        "metrics": metric_summary,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def format_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# SSEAC Paired Delta Summary",
        "",
        f"- benchmark: `{summary['benchmark']}`",
        f"- paired_rows: `{summary['paired_rows']}`",
        f"- structured_no_compiler_rows: `{summary['no_compiler_rows']}`",
        f"- compiled_rows: `{summary['compiled_rows']}`",
        "",
        "| metric | structured_no_compiler | compiled | delta | improved | worsened | tied |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for metric, stats in summary["metrics"].items():
        lines.append(
            "| {metric} | {no} | {compiled} | {delta} | {improved} | {worsened} | {tied} |".format(
                metric=metric,
                no=fmt(stats["structured_no_compiler_mean"]),
                compiled=fmt(stats["compiled_mean"]),
                delta=fmt(stats["delta_mean"]),
                improved=stats["improved_rows"],
                worsened=stats["worsened_rows"],
                tied=stats["tied_rows"],
            )
        )
    if summary["missing_no_compiler"] or summary["missing_compiled"]:
        lines.extend(
            [
                "",
                "## Pairing Warnings",
                "",
                f"- missing_no_compiler: `{len(summary['missing_no_compiler'])}`",
                f"- missing_compiled: `{len(summary['missing_compiled'])}`",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize paired SSEAC structured_no_compiler vs compiled score deltas.")
    parser.add_argument("--benchmark", choices=["pg40", "hsa"], required=True)
    parser.add_argument("--no-compiler-scores", type=Path, required=True)
    parser.add_argument("--compiled-scores", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--summary-out", type=Path)
    args = parser.parse_args()

    summary = summarize_pair(
        read_jsonl(args.no_compiler_scores),
        read_jsonl(args.compiled_scores),
        args.benchmark,
    )
    if args.out:
        write_json(args.out, summary)
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(format_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
