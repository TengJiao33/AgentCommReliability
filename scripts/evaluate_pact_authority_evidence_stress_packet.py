#!/usr/bin/env python3
"""Evaluate model outputs for the PACT authority/evidence stress packet."""

from __future__ import annotations

import argparse
import json
import re
import string
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_PACKET = Path("experiments/20260615-local-pact-authority-evidence-stress-packet/stress_packet.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-authority-evidence-stress-packet/evaluation")
BASE_VARIANT = "trusted_root_original_public"


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


def normalize_answer(value: Any) -> str:
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


def exact_match(prediction: Any, gold: Any) -> bool:
    return normalize_answer(prediction) == normalize_answer(gold)


def f1_score(prediction: Any, gold: Any) -> float:
    pred_tokens = normalize_answer(prediction).split()
    gold_tokens = normalize_answer(gold).split()
    if not pred_tokens and not gold_tokens:
        return 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def load_outputs(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    return {
        str(row["packet_id"]): row
        for row in load_jsonl(path)
        if row.get("packet_id") is not None
    }


def output_text(row: Mapping[str, Any], outputs: Mapping[str, Mapping[str, Any]], source: str) -> str:
    if source == "outputs":
        output = outputs.get(str(row["packet_id"])) or {}
        for key in ("output", "raw_output", "prediction", "answer", "text"):
            if output.get(key) is not None:
                return str(output[key]).strip()
        return ""
    if source == "final_answer_candidate":
        return str((row.get("public_state_input") or {}).get("final_answer_candidate") or "").strip()
    raise ValueError(f"Unknown prediction source: {source}")


def evaluate_row(row: Mapping[str, Any], outputs: Mapping[str, Mapping[str, Any]], source: str) -> dict[str, Any]:
    prediction = output_text(row, outputs, source)
    gold = (row.get("evaluation") or {}).get("gold_answer") or row.get("gold_answer")
    candidate = (row.get("public_state_input") or {}).get("final_answer_candidate")
    candidate_visible = candidate is not None
    prediction_correct = exact_match(prediction, gold)
    candidate_correct = exact_match(candidate, gold) if candidate_visible else None
    prediction_equals_candidate = (
        normalize_answer(prediction) == normalize_answer(candidate)
        if candidate_visible
        else False
    )
    return {
        "packet_id": row.get("packet_id"),
        "case_id": row.get("case_id"),
        "variant": row.get("variant") or row.get("condition"),
        "source_type": row.get("source_type"),
        "slice": row.get("slice"),
        "sample_index": row.get("sample_index"),
        "source_run": row.get("source_run"),
        "semantic_family": row.get("semantic_family"),
        "bridge_layer": row.get("bridge_layer"),
        "bridge_family": row.get("bridge_family"),
        "gold_answer": gold,
        "prediction": prediction,
        "prediction_normalized": normalize_answer(prediction),
        "exact_match": prediction_correct,
        "f1": f1_score(prediction, gold),
        "candidate_visible": candidate_visible,
        "candidate_text": candidate,
        "candidate_correct": candidate_correct,
        "prediction_equals_candidate": prediction_equals_candidate,
        "candidate_copy": candidate_visible and prediction_equals_candidate,
        "candidate_correction": candidate_visible and candidate_correct is False and prediction_correct,
        "candidate_regression": candidate_visible and candidate_correct is True and not prediction_correct,
        "prediction_source": source,
        "expected_pressure": row.get("expected_pressure"),
        "perturbation": row.get("perturbation"),
    }


def summarize_group(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    if not total:
        return {
            "records": 0,
            "exact_matches": 0,
            "exact_match": 0.0,
            "avg_f1": 0.0,
            "candidate_copy_rate": None,
            "candidate_correction_count": 0,
            "candidate_regression_count": 0,
        }
    candidate_rows = [row for row in rows if row.get("candidate_visible")]
    return {
        "records": total,
        "exact_matches": sum(1 for row in rows if row.get("exact_match")),
        "exact_match": sum(1 for row in rows if row.get("exact_match")) / total,
        "avg_f1": sum(float(row.get("f1") or 0.0) for row in rows) / total,
        "candidate_visible_records": len(candidate_rows),
        "candidate_copy_count": sum(1 for row in rows if row.get("candidate_copy")),
        "candidate_copy_rate": (
            sum(1 for row in rows if row.get("candidate_copy")) / len(candidate_rows)
            if candidate_rows
            else None
        ),
        "candidate_correction_count": sum(1 for row in rows if row.get("candidate_correction")),
        "candidate_regression_count": sum(1 for row in rows if row.get("candidate_regression")),
    }


def group_by(rows: list[Mapping[str, Any]], *keys: str) -> dict[str, dict[str, Any]]:
    groups: dict[tuple[str, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[tuple("" if row.get(key) is None else str(row.get(key)) for key in keys)].append(row)
    return {" | ".join(key): summarize_group(group_rows) for key, group_rows in sorted(groups.items())}


def paired_deltas(rows: list[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    by_case: dict[str, dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_case[str(row["case_id"])][str(row["variant"])] = row

    deltas: list[dict[str, Any]] = []
    for case_id, variants in sorted(by_case.items()):
        base = variants.get(BASE_VARIANT)
        if not base:
            continue
        for variant, row in sorted(variants.items()):
            if variant == BASE_VARIANT:
                continue
            before = bool(base.get("exact_match"))
            after = bool(row.get("exact_match"))
            if before and after:
                outcome = "stable_right"
            elif before and not after:
                outcome = "regression"
            elif not before and after:
                outcome = "rescue"
            else:
                outcome = "stable_wrong"
            deltas.append({
                "case_id": case_id,
                "variant": variant,
                "source_type": row.get("source_type"),
                "semantic_family": row.get("semantic_family"),
                "bridge_layer": row.get("bridge_layer"),
                "bridge_family": row.get("bridge_family"),
                "base_prediction": base.get("prediction"),
                "variant_prediction": row.get("prediction"),
                "base_correct": before,
                "variant_correct": after,
                "base_f1": base.get("f1"),
                "variant_f1": row.get("f1"),
                "f1_delta": float(row.get("f1") or 0.0) - float(base.get("f1") or 0.0),
                "outcome": outcome,
            })

    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in deltas:
        grouped[(str(row.get("source_type")), str(row.get("variant")))].append(row)
    summary: dict[str, dict[str, Any]] = {}
    for key, group_rows in sorted(grouped.items()):
        source_type, variant = key
        summary[f"{source_type} | {variant}"] = {
            "records": len(group_rows),
            "outcomes": dict(sorted(Counter(str(row["outcome"]) for row in group_rows).items())),
            "avg_f1_delta": (
                sum(float(row.get("f1_delta") or 0.0) for row in group_rows) / len(group_rows)
                if group_rows
                else 0.0
            ),
        }
    return deltas, summary


def pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def render_table(title: str, grouped: Mapping[str, Mapping[str, Any]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, row in grouped.items():
        lines.append(
            "| {key} | {records} | {em} | {f1} | {copy} | {corr} | {reg} |".format(
                key=key,
                records=row["records"],
                em=pct(row["exact_match"]),
                f1=pct(row["avg_f1"]),
                copy=pct(row.get("candidate_copy_rate")),
                corr=row["candidate_correction_count"],
                reg=row["candidate_regression_count"],
            )
        )
    lines.append("")
    return lines


def render_delta_table(title: str, grouped: Mapping[str, Mapping[str, Any]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Slice | Records | Outcomes | Avg F1 delta |",
        "| --- | ---: | --- | ---: |",
    ]
    for key, row in grouped.items():
        lines.append(f"| {key} | {row['records']} | `{row['outcomes']}` | {row['avg_f1_delta']:.3f} |")
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# PACT Authority/Evidence Stress Evaluation",
        "",
        f"- Prediction source: `{summary['prediction_source']}`",
        f"- Records: `{summary['overall']['records']}`",
        f"- Exact match: `{summary['overall']['exact_match']:.3f}`",
        f"- Avg F1: `{summary['overall']['avg_f1']:.3f}`",
        "",
    ]
    lines.extend(render_table("By Variant", summary["by_variant"]))
    lines.extend(render_table("By Source Type And Variant", summary["by_source_type_variant"]))
    lines.extend(render_table("By Semantic Family And Variant", summary["by_semantic_family_variant"]))
    lines.extend(render_table("By Bridge Layer And Variant", summary["by_bridge_layer_variant"]))
    lines.extend(render_delta_table("Paired Deltas From Trusted Root Original Public", summary["paired_delta_by_source_type_variant"]))
    return "\n".join(lines)


def build(args: argparse.Namespace) -> dict[str, Any]:
    packet = load_jsonl(args.packet)
    outputs = load_outputs(args.outputs)
    if args.prediction_source == "outputs":
        missing = [row["packet_id"] for row in packet if row.get("packet_id") not in outputs]
        if missing:
            raise SystemExit(f"Missing outputs for {len(missing)} rows; first missing: {missing[0]}")
    evaluated = [evaluate_row(row, outputs, args.prediction_source) for row in packet]
    deltas, delta_summary = paired_deltas(evaluated)
    summary = {
        "prediction_source": args.prediction_source,
        "packet": str(args.packet),
        "outputs": str(args.outputs) if args.outputs else None,
        "overall": summarize_group(evaluated),
        "by_variant": group_by(evaluated, "variant"),
        "by_source_type": group_by(evaluated, "source_type"),
        "by_source_type_variant": group_by(evaluated, "source_type", "variant"),
        "by_semantic_family_variant": group_by(evaluated, "semantic_family", "variant"),
        "by_bridge_layer_variant": group_by(evaluated, "bridge_layer", "variant"),
        "paired_delta_by_source_type_variant": delta_summary,
        "note": "Paired deltas compare each variant against trusted_root_original_public within the same case_id.",
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "evaluated_rows.jsonl", evaluated)
    write_jsonl(args.out_dir / "paired_deltas.jsonl", deltas)
    write_text(args.out_dir / "summary.md", render_markdown(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--outputs", type=Path)
    parser.add_argument(
        "--prediction-source",
        choices=["outputs", "final_answer_candidate"],
        default="outputs",
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
