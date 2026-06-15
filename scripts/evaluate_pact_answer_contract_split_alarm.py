#!/usr/bin/env python3
"""Evaluate model outputs for the PACT split-alarm verifier packet."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_PACKET = Path("experiments/20260615-local-pact-answer-contract-split-alarm-packet/split_alarm_packet.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-answer-contract-split-alarm-packet/evaluation")


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


def first_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        return {}
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        label_match = re.search(r'"label"\s*:\s*"([^"]+)"', text, flags=re.IGNORECASE)
        if label_match:
            return {"label": label_match.group(1)}
        return {}
    try:
        value = json.loads(match.group(0))
    except json.JSONDecodeError:
        label_match = re.search(r'"label"\s*:\s*"([^"]+)"', text, flags=re.IGNORECASE)
        if label_match:
            return {"label": label_match.group(1)}
        return {}
    return value if isinstance(value, dict) else {}


def normalize_label(value: Any, *, allow_soft: bool) -> str:
    text = str(value if value is not None else "").strip().lower()
    if allow_soft and text == "soft":
        return "soft"
    if text in {"yes", "true", "1"}:
        return "yes"
    return "no"


def output_text(row: Mapping[str, Any]) -> str:
    for key in ("output", "raw_output", "prediction", "answer", "text"):
        if row.get(key) is not None:
            return str(row[key])
    return ""


def load_outputs(path: Path | None) -> dict[str, Mapping[str, Any]]:
    if path is None:
        return {}
    return {str(row["packet_id"]): row for row in load_jsonl(path)}


def positive(label: str) -> bool:
    return label in {"yes", "soft"}


def binary_metrics(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    for row in rows:
        gold = positive(str(row["gold_label"]))
        pred = positive(str(row["prediction"]))
        if gold and pred:
            tp += 1
        elif not gold and pred:
            fp += 1
        elif gold and not pred:
            fn += 1
        else:
            tn += 1
    total = tp + fp + tn + fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {
        "records": total,
        "accuracy": (tp + tn) / total if total else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def group_metrics(rows: Iterable[Mapping[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key))].append(row)
    return {name: binary_metrics(group_rows) for name, group_rows in sorted(groups.items())}


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    packet = load_jsonl(args.packet)
    outputs = load_outputs(args.outputs)
    if args.prediction_source == "outputs":
        missing = [row["packet_id"] for row in packet if row["packet_id"] not in outputs]
        if missing:
            raise SystemExit(f"Missing outputs for {len(missing)} rows; first missing: {missing[0]}")

    evaluated: list[dict[str, Any]] = []
    parse_failures = 0
    for row in packet:
        task = str(row["task"])
        allow_soft = task == "target_authority_alarm"
        if args.prediction_source == "gold":
            pred = str(row["gold_label"])
            parsed = {"label": pred}
        elif args.prediction_source == "all_no":
            pred = "no"
            parsed = {"label": pred}
        else:
            output = outputs.get(str(row["packet_id"])) or {}
            parsed = first_json_object(output_text(output))
            if not parsed:
                parse_failures += 1
            pred = normalize_label(parsed.get("label"), allow_soft=allow_soft)
        gold = normalize_label(row["gold_label"], allow_soft=allow_soft)
        evaluated.append({
            "packet_id": row["packet_id"],
            "base_packet_id": row.get("base_packet_id"),
            "case_id": row.get("case_id"),
            "task": task,
            "label_source": row.get("label_source"),
            "slice": row.get("slice"),
            "sample_index": row.get("sample_index"),
            "source_run": row.get("source_run"),
            "gold_label": gold,
            "prediction": pred,
            "correct": gold == pred,
            "positive_correct": positive(gold) == positive(pred),
            "parsed_output": parsed,
        })

    exact_correct = sum(1 for row in evaluated if row["correct"])
    positive_correct = sum(1 for row in evaluated if row["positive_correct"])
    summary = {
        "prediction_source": args.prediction_source,
        "packet": str(args.packet),
        "outputs": str(args.outputs) if args.outputs else None,
        "records": len(evaluated),
        "parse_failures": parse_failures,
        "exact_accuracy": exact_correct / len(evaluated) if evaluated else 0.0,
        "positive_accuracy": positive_correct / len(evaluated) if evaluated else 0.0,
        "overall_binary_metrics": binary_metrics(evaluated),
        "by_task": group_metrics(evaluated, "task"),
        "by_label_source": group_metrics(evaluated, "label_source"),
        "by_slice": group_metrics(evaluated, "slice"),
        "prediction_counts_by_task": {
            task: dict(sorted(Counter(row["prediction"] for row in evaluated if row["task"] == task).items()))
            for task in sorted({str(row["task"]) for row in evaluated})
        },
        "gold_counts_by_task": {
            task: dict(sorted(Counter(row["gold_label"] for row in evaluated if row["task"] == task).items()))
            for task in sorted({str(row["task"]) for row in evaluated})
        },
        "note": "Binary metrics count soft as positive for target_authority_alarm.",
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "evaluated_rows.jsonl", evaluated)
    write_text(args.out_dir / "summary.md", render_markdown(summary))
    return summary


def pct(value: float) -> str:
    return f"{value:.3f}"


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# PACT Split-Alarm Verifier Evaluation",
        "",
        f"- Prediction source: `{summary['prediction_source']}`",
        f"- Records: `{summary['records']}`",
        f"- Parse failures: `{summary['parse_failures']}`",
        f"- Exact label accuracy: `{pct(summary['exact_accuracy'])}`",
        f"- Positive/negative accuracy: `{pct(summary['positive_accuracy'])}`",
        "",
        "## By Task",
        "",
        "| Task | Records | Acc | Precision | Recall | F1 | TP | FP | TN | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for task, metrics in summary["by_task"].items():
        lines.append(
            f"| `{task}` | {metrics['records']} | {pct(metrics['accuracy'])} | "
            f"{pct(metrics['precision'])} | {pct(metrics['recall'])} | {pct(metrics['f1'])} | "
            f"{metrics['tp']} | {metrics['fp']} | {metrics['tn']} | {metrics['fn']} |"
        )
    lines.extend([
        "",
        "## Prediction Counts",
        "",
        "| Task | Gold | Predicted |",
        "| --- | --- | --- |",
    ])
    for task in summary["gold_counts_by_task"]:
        lines.append(
            f"| `{task}` | `{summary['gold_counts_by_task'][task]}` | "
            f"`{summary['prediction_counts_by_task'].get(task, {})}` |"
        )
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--outputs", type=Path)
    parser.add_argument("--prediction-source", choices=["outputs", "gold", "all_no"], default="outputs")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = evaluate(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
