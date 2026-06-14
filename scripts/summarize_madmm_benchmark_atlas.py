#!/usr/bin/env python3
"""Summarize MAD-MM benchmark result directories into a benchmark atlas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


METHOD_FILES = {
    "cot": "cot_seed41.json",
    "mad_naive": "mad_3agents_2rounds_seed41.json",
    "mad_objective": "mad_objective_3agents_2rounds_seed41.json",
    "mad_subjective": "mad_subjective_3agents_2rounds_seed41.json",
}

METHOD_LABELS = {
    "cot": "CoT",
    "mad_naive": "MAD naive",
    "mad_objective": "MAD-MM objective",
    "mad_subjective": "MAD-MM subjective",
}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def find_result_dirs(roots: Iterable[Path]) -> List[Path]:
    result_dirs = set()
    for root in roots:
        if not root.exists():
            continue
        if any((root / filename).exists() for filename in METHOD_FILES.values()):
            result_dirs.add(root)
            continue
        for filename in METHOD_FILES.values():
            for path in root.rglob(filename):
                result_dirs.add(path.parent)
    return sorted(result_dirs)


def infer_benchmark(path: Path, sample: Optional[Dict[str, Any]]) -> str:
    if sample:
        dataset = sample.get("dataset")
        if dataset:
            return str(dataset)
    return path.name


def method_summary(path: Path, method: str, filename: str) -> Optional[Dict[str, Any]]:
    result_path = path / filename
    if not result_path.exists():
        return None
    data = load_json(result_path)
    results = data.get("results") or []
    usage = data.get("token_usage_summary") or {}
    total_tokens = usage.get("total_tokens")
    sample_count = len(results)
    return {
        "method": method,
        "label": METHOD_LABELS.get(method, method),
        "accuracy": data.get("accuracy"),
        "sample_count": sample_count,
        "total_tokens": total_tokens,
        "tokens_per_sample": (
            float(total_tokens) / sample_count
            if isinstance(total_tokens, (int, float)) and sample_count
            else None
        ),
        "input_tokens": usage.get("total_input_tokens", usage.get("input_tokens")),
        "output_tokens": usage.get("total_output_tokens", usage.get("output_tokens")),
        "call_count": usage.get("call_count"),
        "file": str(result_path),
    }


def summarize_dir(path: Path) -> Dict[str, Any]:
    methods = {
        method: summary
        for method, filename in METHOD_FILES.items()
        if (summary := method_summary(path, method, filename)) is not None
    }
    first_method = next(iter(methods.values()), None)
    benchmark = infer_benchmark(path, first_method)
    cot = methods.get("cot")
    cot_acc = cot.get("accuracy") if cot else None
    cot_tokens = cot.get("total_tokens") if cot else None

    for summary in methods.values():
        acc = summary.get("accuracy")
        tokens = summary.get("total_tokens")
        summary["accuracy_delta_vs_cot"] = (
            acc - cot_acc if isinstance(acc, (int, float)) and isinstance(cot_acc, (int, float)) else None
        )
        summary["token_ratio_vs_cot"] = (
            tokens / cot_tokens
            if isinstance(tokens, (int, float)) and isinstance(cot_tokens, (int, float)) and cot_tokens
            else None
        )

    accuracies = [
        summary["accuracy"]
        for summary in methods.values()
        if isinstance(summary.get("accuracy"), (int, float))
    ]
    sample_counts = {
        summary["sample_count"]
        for summary in methods.values()
        if summary.get("sample_count") is not None
    }
    return {
        "benchmark": benchmark,
        "result_dir": str(path),
        "sample_count": next(iter(sample_counts)) if len(sample_counts) == 1 else sorted(sample_counts),
        "method_count": len(methods),
        "accuracy_spread": max(accuracies) - min(accuracies) if accuracies else None,
        "methods": methods,
    }


def fmt_acc(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.3f}"
    return "-"


def fmt_delta(value: Any) -> str:
    if isinstance(value, (int, float)):
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.3f}"
    return "-"


def fmt_tokens(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{int(value):,}"
    return "-"


def fmt_ratio(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.2f}x"
    return "-"


def method_cell(methods: Dict[str, Dict[str, Any]], method: str) -> str:
    summary = methods.get(method)
    if not summary:
        return "-"
    return (
        f"{fmt_acc(summary.get('accuracy'))}"
        f" / {fmt_delta(summary.get('accuracy_delta_vs_cot'))}"
        f" / {fmt_tokens(summary.get('total_tokens'))}"
        f" / {fmt_ratio(summary.get('token_ratio_vs_cot'))}"
    )


def build_markdown(rows: List[Dict[str, Any]]) -> str:
    lines = [
        "# MAD-MM Benchmark Atlas",
        "",
        "Cells are `accuracy / delta_vs_CoT / total_tokens / token_ratio_vs_CoT`.",
        "",
        "| Benchmark | Samples | CoT | MAD naive | MAD-MM objective | MAD-MM subjective | Accuracy spread | Result dir |",
        "| --- | ---: | --- | --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        methods = row["methods"]
        lines.append(
            "| {benchmark} | {samples} | {cot} | {naive} | {objective} | {subjective} | {spread} | `{result_dir}` |".format(
                benchmark=row["benchmark"],
                samples=row["sample_count"],
                cot=method_cell(methods, "cot"),
                naive=method_cell(methods, "mad_naive"),
                objective=method_cell(methods, "mad_objective"),
                subjective=method_cell(methods, "mad_subjective"),
                spread=fmt_acc(row.get("accuracy_spread")),
                result_dir=row["result_dir"],
            )
        )
    lines.append("")
    lines.append("Caveat: this atlas reports short-run reproduction probes, not benchmark-scale claims.")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", type=Path, help="Result directories or roots to scan.")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    args = parser.parse_args()

    result_dirs = find_result_dirs(args.roots)
    rows = [summarize_dir(path) for path in result_dirs]
    rows.sort(key=lambda row: (str(row["benchmark"]), str(row["result_dir"])))

    payload = {"result_count": len(rows), "results": rows}
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(build_markdown(rows), encoding="utf-8")


if __name__ == "__main__":
    main()
