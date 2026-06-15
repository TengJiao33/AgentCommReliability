#!/usr/bin/env python3
"""Evaluate outputs for the PACT answer-contract verifier packet."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


DEFAULT_PACKET = Path("experiments/20260615-local-pact-answer-contract-verifier-packet/verifier_packet.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-answer-contract-verifier-packet/evaluation")

ALARM_FIELDS = [
    "answer_contract_alarm",
    "target_authority_alarm",
    "answer_type_relation_alarm",
    "short_span_granularity_alarm",
    "evidence_adequacy_alarm",
    "final_candidate_alarm",
]

PRIMARY_SURFACES = {
    "answer_type_or_relation_mismatch",
    "short_span_or_granularity_mismatch",
    "public_target_misdirection",
    "evidence_sentence_or_distractor_copy",
    "question_root_ambiguity_regression",
    "evidence_or_content_failure",
    "final_candidate_attractor",
    "strict_span_or_granularity_surface",
    "no_answer_contract_failure",
}


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


def load_outputs(path: Optional[Path]) -> Dict[str, Mapping[str, Any]]:
    if path is None:
        return {}
    return {
        str(row["packet_id"]): row
        for row in load_jsonl(path)
        if row.get("packet_id") is not None
    }


def normalize_alarm(value: Any, *, allow_soft: bool = False) -> str:
    text = str(value if value is not None else "").strip().lower()
    if allow_soft and text == "soft":
        return "soft"
    if text in {"yes", "true", "1"}:
        return "yes"
    return "no"


def normalize_surface(value: Any) -> str:
    text = str(value if value is not None else "").strip()
    return text if text in PRIMARY_SURFACES else "no_answer_contract_failure"


def first_json_object(text: str) -> Dict[str, Any]:
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
        return {}
    try:
        value = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def output_text(output_row: Mapping[str, Any]) -> str:
    for key in ("output", "raw_output", "prediction", "answer", "text"):
        if output_row.get(key) is not None:
            return str(output_row[key])
    return ""


def prediction_for_case(case: Mapping[str, Any], outputs: Mapping[str, Mapping[str, Any]], source: str) -> Dict[str, Any]:
    if source == "gold":
        return dict(case["gold_label"])
    if source == "all_no":
        return {
            "answer_contract_alarm": "no",
            "target_authority_alarm": "no",
            "answer_type_relation_alarm": "no",
            "short_span_granularity_alarm": "no",
            "evidence_adequacy_alarm": "no",
            "final_candidate_alarm": "no",
            "primary_failure_surface": "no_answer_contract_failure",
        }
    if source != "outputs":
        raise ValueError(f"Unknown prediction source: {source}")
    output = outputs.get(str(case["packet_id"])) or {}
    parsed = first_json_object(output_text(output))
    return parsed


def normalize_prediction(prediction: Mapping[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for field in ALARM_FIELDS:
        out[field] = normalize_alarm(
            prediction.get(field),
            allow_soft=(field == "target_authority_alarm"),
        )
    out["primary_failure_surface"] = normalize_surface(prediction.get("primary_failure_surface"))
    return out


def positive(value: str) -> bool:
    return value in {"yes", "soft"}


def binary_metrics(pairs: Iterable[Tuple[str, str]]) -> Dict[str, Any]:
    tp = fp = tn = fn = 0
    for gold, pred in pairs:
        gold_pos = positive(gold)
        pred_pos = positive(pred)
        if gold_pos and pred_pos:
            tp += 1
        elif not gold_pos and pred_pos:
            fp += 1
        elif gold_pos and not pred_pos:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    total = tp + fp + tn + fn
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": (tp + tn) / total if total else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def summarize_rows(rows: List[Mapping[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    if not total:
        return {
            "records": 0,
            "primary_surface_accuracy": 0.0,
            "exact_all_fields_accuracy": 0.0,
            "alarm_exact_accuracy": {},
            "alarm_binary_metrics": {},
        }
    exact_all = 0
    primary_correct = 0
    alarm_exact: Dict[str, int] = Counter()
    alarm_pairs: Dict[str, List[Tuple[str, str]]] = {field: [] for field in ALARM_FIELDS}
    for row in rows:
        gold = row["gold_label"]
        pred = row["prediction"]
        all_ok = True
        if gold["primary_failure_surface"] == pred["primary_failure_surface"]:
            primary_correct += 1
        else:
            all_ok = False
        for field in ALARM_FIELDS:
            alarm_pairs[field].append((gold[field], pred[field]))
            if gold[field] == pred[field]:
                alarm_exact[field] += 1
            else:
                all_ok = False
        if all_ok:
            exact_all += 1
    return {
        "records": total,
        "exact_all_fields_accuracy": exact_all / total,
        "primary_surface_accuracy": primary_correct / total,
        "alarm_exact_accuracy": {
            field: alarm_exact[field] / total
            for field in ALARM_FIELDS
        },
        "alarm_binary_metrics": {
            field: binary_metrics(pairs)
            for field, pairs in alarm_pairs.items()
        },
    }


def group_by(rows: Iterable[Mapping[str, Any]], key: str) -> Dict[str, Dict[str, Any]]:
    groups: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key))].append(row)
    return {name: summarize_rows(group_rows) for name, group_rows in sorted(groups.items())}


def primary_confusion(rows: Iterable[Mapping[str, Any]]) -> Dict[str, Dict[str, int]]:
    matrix: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        matrix[row["gold_label"]["primary_failure_surface"]][row["prediction"]["primary_failure_surface"]] += 1
    return {gold: dict(sorted(preds.items())) for gold, preds in sorted(matrix.items())}


def evaluate(args: argparse.Namespace) -> Dict[str, Any]:
    packet = load_jsonl(args.packet)
    outputs = load_outputs(args.outputs)
    if args.prediction_source == "outputs":
        missing = [row["packet_id"] for row in packet if row["packet_id"] not in outputs]
        if missing:
            raise SystemExit(f"Missing outputs for {len(missing)} rows; first missing: {missing[0]}")

    evaluated: List[Dict[str, Any]] = []
    for case in packet:
        prediction = normalize_prediction(prediction_for_case(case, outputs, args.prediction_source))
        gold = normalize_prediction(case["gold_label"])
        evaluated.append({
            "packet_id": case["packet_id"],
            "case_id": case["case_id"],
            "label_source": case["label_source"],
            "slice": case.get("slice"),
            "sample_index": case.get("sample_index"),
            "source_run": case.get("source_run"),
            "gold_label": gold,
            "prediction": prediction,
            "primary_surface_correct": gold["primary_failure_surface"] == prediction["primary_failure_surface"],
            "all_fields_correct": gold == prediction,
        })

    summary = {
        "prediction_source": args.prediction_source,
        "packet": str(args.packet),
        "outputs": str(args.outputs) if args.outputs else None,
        "overall": summarize_rows(evaluated),
        "by_label_source": group_by(evaluated, "label_source"),
        "by_slice": group_by(evaluated, "slice"),
        "primary_confusion": primary_confusion(evaluated),
        "note": (
            "Binary alarm metrics count both yes and soft as positive. Exact "
            "alarm accuracy keeps soft distinct."
        ),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "evaluated_rows.jsonl", evaluated)
    write_text(args.out_dir / "summary.md", render_markdown(summary))
    return summary


def pct(value: float) -> str:
    return f"{value:.3f}"


def render_group_table(title: str, rows: Mapping[str, Mapping[str, Any]]) -> List[str]:
    lines = [
        f"## {title}",
        "",
        "| Group | Records | All fields | Primary surface | Target auth F1 | Answer-contract F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, row in rows.items():
        lines.append(
            "| {name} | {records} | {all_fields} | {surface} | {target_f1} | {contract_f1} |".format(
                name=name,
                records=row["records"],
                all_fields=pct(row["exact_all_fields_accuracy"]),
                surface=pct(row["primary_surface_accuracy"]),
                target_f1=pct(row["alarm_binary_metrics"]["target_authority_alarm"]["f1"]),
                contract_f1=pct(row["alarm_binary_metrics"]["answer_contract_alarm"]["f1"]),
            )
        )
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any]) -> str:
    overall = summary["overall"]
    lines = [
        "# PACT Answer-Contract Verifier Evaluation",
        "",
        f"- Prediction source: `{summary['prediction_source']}`",
        f"- Records: `{overall['records']}`",
        f"- Exact all-fields accuracy: `{overall['exact_all_fields_accuracy']:.3f}`",
        f"- Primary-surface accuracy: `{overall['primary_surface_accuracy']:.3f}`",
        "",
        "## Alarm Metrics",
        "",
        "| Alarm | Exact acc | Precision | Recall | F1 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for field in ALARM_FIELDS:
        metrics = overall["alarm_binary_metrics"][field]
        lines.append(
            f"| `{field}` | {overall['alarm_exact_accuracy'][field]:.3f} | "
            f"{metrics['precision']:.3f} | {metrics['recall']:.3f} | {metrics['f1']:.3f} |"
        )
    lines.append("")
    lines.extend(render_group_table("By Label Source", summary["by_label_source"]))
    lines.extend(render_group_table("By Slice", summary["by_slice"]))
    lines.extend([
        "## Note",
        "",
        "Binary metrics count `soft` as positive; exact alarm accuracy keeps `soft` distinct.",
        "",
    ])
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
