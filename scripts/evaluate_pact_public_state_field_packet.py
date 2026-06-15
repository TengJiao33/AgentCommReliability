#!/usr/bin/env python3
"""Evaluate model outputs for the PACT public-state field packet."""

from __future__ import annotations

import argparse
import json
import re
import string
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


DEFAULT_PACKET = Path("experiments/20260615-local-pact-public-state-field-packet/field_packet.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-public-state-field-packet/official-final-answer-smoke")


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


def exact_match(prediction: Optional[str], gold: Optional[str]) -> bool:
    return normalize_answer(prediction) == normalize_answer(gold)


def f1_score(prediction: Optional[str], gold: Optional[str]) -> float:
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


def load_outputs(path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
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
    if source == "official_final_answer":
        return str(row.get("official_final_answer") or "").strip()
    if source == "final_answer_candidate":
        public_state = row.get("public_state_input") or {}
        return str(public_state.get("final_answer_candidate") or "").strip()
    raise ValueError(f"Unknown prediction source: {source}")


def evaluate_row(row: Dict[str, Any], outputs: Mapping[str, Mapping[str, Any]], source: str) -> Dict[str, Any]:
    prediction = output_text(row, outputs, source)
    gold = (row.get("evaluation") or {}).get("gold_answer") or row.get("gold_answer")
    candidate = (row.get("public_state_input") or {}).get("final_answer_candidate")
    candidate_visible = candidate is not None
    candidate_correct = exact_match(candidate, gold) if candidate_visible else None
    prediction_correct = exact_match(prediction, gold)
    prediction_equals_candidate = (
        normalize_answer(prediction) == normalize_answer(candidate)
        if candidate_visible
        else False
    )
    return {
        "packet_id": row.get("packet_id"),
        "sample_index": row.get("sample_index"),
        "source_run": row.get("source_run"),
        "condition": row.get("condition"),
        "intervention_axis": row.get("intervention_axis"),
        "bridge_layer": row.get("bridge_layer"),
        "bridge_family": row.get("bridge_family"),
        "target_slot_drift_candidate": bool(
            (row.get("target_slot_diagnostic") or {}).get("target_slot_drift_candidate")
        ),
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
        "candidate_correction": (
            candidate_visible
            and candidate_correct is False
            and prediction_correct
        ),
        "candidate_regression": (
            candidate_visible
            and candidate_correct is True
            and not prediction_correct
        ),
        "prediction_source": source,
    }


def summarize_group(rows: List[Mapping[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    if total == 0:
        return {
            "records": 0,
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


def group_by(rows: List[Mapping[str, Any]], *keys: str) -> Dict[str, Dict[str, Any]]:
    groups: Dict[Tuple[str, ...], List[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[
            tuple(
                "" if row.get(key) is None else str(row.get(key))
                for key in keys
            )
        ].append(row)
    return {
        " | ".join(key): summarize_group(group_rows)
        for key, group_rows in sorted(groups.items())
    }


def render_table(title: str, grouped: Mapping[str, Mapping[str, Any]]) -> List[str]:
    lines = [
        f"## {title}",
        "",
        "| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, row in grouped.items():
        copy_rate = row.get("candidate_copy_rate")
        copy_text = "n/a" if copy_rate is None else f"{copy_rate:.3f}"
        lines.append(
            "| {key} | {records} | {em:.3f} | {f1:.3f} | {copy_rate} | {corrections} | {regressions} |".format(
                key=key,
                records=row["records"],
                em=row["exact_match"],
                f1=row["avg_f1"],
                copy_rate=copy_text,
                corrections=row["candidate_correction_count"],
                regressions=row["candidate_regression_count"],
            )
        )
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# PACT Public-State Field Packet Evaluation",
        "",
        f"- Prediction source: `{summary['prediction_source']}`",
        f"- Records: `{summary['overall']['records']}`",
        f"- Exact match: `{summary['overall']['exact_match']:.3f}`",
        f"- Avg F1: `{summary['overall']['avg_f1']:.3f}`",
        "",
    ]
    lines.extend(render_table("By Source Run", summary["by_source_run"]))
    lines.extend(render_table("By Condition", summary["by_condition"]))
    lines.extend(render_table("By Source Run And Condition", summary["by_source_run_condition"]))
    lines.extend(render_table("By Bridge Layer", summary["by_bridge_layer"]))
    lines.extend(render_table("By Target Drift Candidate", summary["by_target_slot_drift_candidate"]))
    return "\n".join(lines)


def build(args: argparse.Namespace) -> Dict[str, Any]:
    packet = load_jsonl(args.packet)
    outputs = load_outputs(args.outputs)
    if args.prediction_source == "outputs":
        missing = [row["packet_id"] for row in packet if row.get("packet_id") not in outputs]
        if missing:
            raise SystemExit(
                f"Missing outputs for {len(missing)} packet rows; first missing: {missing[0]}"
            )

    evaluated = [
        evaluate_row(row, outputs, args.prediction_source)
        for row in packet
    ]
    summary = {
        "prediction_source": args.prediction_source,
        "packet": str(args.packet),
        "outputs": str(args.outputs) if args.outputs else None,
        "overall": summarize_group(evaluated),
        "by_source_run": group_by(evaluated, "source_run"),
        "by_condition": group_by(evaluated, "condition"),
        "by_source_run_condition": group_by(evaluated, "source_run", "condition"),
        "by_bridge_layer": group_by(evaluated, "bridge_layer"),
        "by_bridge_family": group_by(evaluated, "bridge_family"),
        "by_target_slot_drift_candidate": group_by(evaluated, "target_slot_drift_candidate"),
        "note": (
            "If prediction_source is official_final_answer or final_answer_candidate, "
            "this is a smoke/baseline score rather than a model packet result."
        ),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "evaluated_rows.jsonl", evaluated)
    write_text(args.out_dir / "summary.md", render_markdown(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--outputs", type=Path)
    parser.add_argument(
        "--prediction-source",
        choices=["outputs", "official_final_answer", "final_answer_candidate"],
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
