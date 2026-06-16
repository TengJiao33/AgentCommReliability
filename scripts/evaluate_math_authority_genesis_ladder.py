#!/usr/bin/env python3
"""Evaluate outputs for the MATH Authority Genesis Ladder packet."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from peer_probe.math_eval import extract_answer_text, math_equiv


DEFAULT_PACKET = Path("experiments/20260615-local-math-authority-genesis-ladder-packet/math_authority_genesis_ladder_packet.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260615-local-math-authority-genesis-ladder-packet/evaluation")
BASE_VARIANT = "baseline_previous_solution"


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


def load_outputs(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    return {str(row["packet_id"]): row for row in load_jsonl(path) if row.get("packet_id") is not None}


def output_text(row: Mapping[str, Any], outputs: Mapping[str, Mapping[str, Any]], source: str) -> str:
    if source == "outputs":
        output = outputs.get(str(row["packet_id"])) or {}
        for key in ("output", "raw_output", "prediction", "answer", "text"):
            if output.get(key) is not None:
                return str(output[key]).strip()
        return ""
    if source == "gold":
        gold = (row.get("evaluation") or {}).get("gold_answer") or row.get("gold_answer") or ""
        return f"{{final answer: {gold}}}"
    raise ValueError(f"unknown prediction source: {source}")


def genesis_info(row: Mapping[str, Any]) -> dict[str, Any]:
    return dict(row.get("math_authority_genesis") or {})


def compact(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def text_overlap(prediction: Any, artifact: Any) -> bool:
    pred = compact(prediction).lower()
    art = compact(artifact).lower()
    if not pred or not art:
        return False
    if len(pred) < 8:
        return pred in art
    return pred in art or art in pred


def evaluate_row(row: Mapping[str, Any], outputs: Mapping[str, Mapping[str, Any]], source: str) -> dict[str, Any]:
    prediction_text = output_text(row, outputs, source)
    prediction_answer, parse_source = extract_answer_text(prediction_text)
    gold = (row.get("evaluation") or {}).get("gold_answer") or row.get("gold_answer")
    semantic = math_equiv(prediction_answer, gold)
    genesis = genesis_info(row)
    artifact_text = genesis.get("artifact_text")
    wrong_answer = genesis.get("wrong_peer_answer") or row.get("wrong_peer_answer")
    wrong_answer_equiv = math_equiv(prediction_answer, wrong_answer) if wrong_answer else None
    artifact_answer_equiv = math_equiv(prediction_answer, artifact_text) if artifact_text else None
    label = row.get("manual_seed_label") or {}
    return {
        "packet_id": row.get("packet_id"),
        "case_id": row.get("case_id"),
        "math_case_id": row.get("math_case_id"),
        "condition": row.get("condition"),
        "variant": row.get("variant"),
        "artifact_type": row.get("artifact_type"),
        "source_surface": row.get("source_surface"),
        "future_signal": genesis.get("future_signal"),
        "future_level": genesis.get("future_level"),
        "operator_family": genesis.get("operator_family"),
        "artifact_visible_to_model": genesis.get("visible_to_model"),
        "artifact_text": artifact_text,
        "wrong_peer_answer": wrong_answer,
        "gold_answer": gold,
        "prediction_text": prediction_text,
        "prediction_answer": prediction_answer,
        "parse_source": parse_source,
        "semantic_correct": semantic.correct,
        "semantic_status": semantic.status,
        "prediction_normalized": semantic.prediction_normalized,
        "gold_normalized": semantic.reference_normalized,
        "wrong_answer_uptake": wrong_answer_equiv.correct is True if wrong_answer_equiv else False,
        "wrong_answer_uptake_status": wrong_answer_equiv.status if wrong_answer_equiv else None,
        "artifact_answer_uptake": artifact_answer_equiv.correct is True if artifact_answer_equiv else False,
        "artifact_answer_uptake_status": artifact_answer_equiv.status if artifact_answer_equiv else None,
        "artifact_text_overlap": text_overlap(prediction_text, artifact_text),
        "final_answer_authority_visible_seed": label.get("final_answer_authority_visible"),
        "relation_skeleton_quality": label.get("relation_skeleton_quality"),
        "numeric_role_slot_quality": label.get("numeric_role_slot_quality"),
        "equation_surface_quality": label.get("equation_surface_quality"),
        "target_predicate_preserved": label.get("target_predicate_preserved"),
        "target_revision_behavior": label.get("target_revision_behavior"),
        "prediction_source": source,
    }


def correctness_bucket(value: Any) -> str:
    if value is True:
        return "correct"
    if value is False:
        return "wrong"
    return "unknown"


def summarize_group(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    if not total:
        return {
            "records": 0,
            "semantic_correct": 0,
            "semantic_accuracy_known": None,
            "semantic_unknown": 0,
            "wrong_answer_uptake_count": 0,
            "wrong_answer_uptake_rate": None,
            "artifact_answer_uptake_count": 0,
            "artifact_answer_uptake_rate": None,
        }
    known = [row for row in rows if row.get("semantic_correct") is not None]
    wrong_answer_rows = [row for row in rows if row.get("wrong_peer_answer")]
    artifact_rows = [row for row in rows if row.get("artifact_text")]
    return {
        "records": total,
        "semantic_correct": sum(1 for row in rows if row.get("semantic_correct") is True),
        "semantic_wrong": sum(1 for row in rows if row.get("semantic_correct") is False),
        "semantic_unknown": sum(1 for row in rows if row.get("semantic_correct") is None),
        "semantic_accuracy_known": (
            sum(1 for row in known if row.get("semantic_correct") is True) / len(known)
            if known
            else None
        ),
        "wrong_answer_uptake_count": sum(1 for row in wrong_answer_rows if row.get("wrong_answer_uptake")),
        "wrong_answer_uptake_rate": (
            sum(1 for row in wrong_answer_rows if row.get("wrong_answer_uptake")) / len(wrong_answer_rows)
            if wrong_answer_rows
            else None
        ),
        "artifact_answer_uptake_count": sum(1 for row in artifact_rows if row.get("artifact_answer_uptake")),
        "artifact_answer_uptake_rate": (
            sum(1 for row in artifact_rows if row.get("artifact_answer_uptake")) / len(artifact_rows)
            if artifact_rows
            else None
        ),
        "artifact_text_overlap_count": sum(1 for row in artifact_rows if row.get("artifact_text_overlap")),
        "artifact_text_overlap_rate": (
            sum(1 for row in artifact_rows if row.get("artifact_text_overlap")) / len(artifact_rows)
            if artifact_rows
            else None
        ),
        "semantic_status_counts": dict(sorted(Counter(str(row.get("semantic_status")) for row in rows).items())),
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
            before = base.get("semantic_correct")
            after = row.get("semantic_correct")
            if before is None or after is None:
                outcome = "unknown"
            elif before and after:
                outcome = "stable_right"
            elif before and not after:
                outcome = "authority_violation"
            elif not before and after:
                outcome = "rescue"
            else:
                outcome = "stable_wrong"
            deltas.append(
                {
                    "case_id": case_id,
                    "math_case_id": row.get("math_case_id"),
                    "condition": row.get("condition"),
                    "variant": variant,
                    "artifact_type": row.get("artifact_type"),
                    "source_surface": row.get("source_surface"),
                    "future_signal": row.get("future_signal"),
                    "future_level": row.get("future_level"),
                    "operator_family": row.get("operator_family"),
                    "artifact_visible_to_model": row.get("artifact_visible_to_model"),
                    "base_prediction_answer": base.get("prediction_answer"),
                    "variant_prediction_answer": row.get("prediction_answer"),
                    "gold_answer": row.get("gold_answer"),
                    "wrong_peer_answer": row.get("wrong_peer_answer"),
                    "base_correct": before,
                    "variant_correct": after,
                    "base_correct_bucket": correctness_bucket(before),
                    "variant_correct_bucket": correctness_bucket(after),
                    "wrong_answer_uptake": row.get("wrong_answer_uptake"),
                    "artifact_answer_uptake": row.get("artifact_answer_uptake"),
                    "artifact_text_overlap": row.get("artifact_text_overlap"),
                    "authority_violation": bool(before is True and after is False),
                    "operator_uptake_candidate": bool(
                        before is True
                        and after is False
                        and not row.get("wrong_answer_uptake")
                    ),
                    "final_answer_authority_visible_seed": row.get("final_answer_authority_visible_seed"),
                    "relation_skeleton_quality": row.get("relation_skeleton_quality"),
                    "numeric_role_slot_quality": row.get("numeric_role_slot_quality"),
                    "equation_surface_quality": row.get("equation_surface_quality"),
                    "target_revision_behavior": row.get("target_revision_behavior"),
                    "outcome": outcome,
                }
            )

    grouped: dict[tuple[str, str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in deltas:
        grouped[(str(row.get("artifact_type")), str(row.get("future_level")), str(row.get("future_signal")))].append(row)

    summary: dict[str, dict[str, Any]] = {}
    for key, group_rows in sorted(grouped.items(), key=lambda item: (item[0][0], int(item[0][1]) if item[0][1].lstrip("-").isdigit() else 999, item[0][2])):
        artifact_type, level, signal = key
        base_correct = [row for row in group_rows if row.get("base_correct") is True]
        violations = [row for row in base_correct if row.get("authority_violation")]
        uptake = [row for row in base_correct if row.get("wrong_answer_uptake")]
        operator = [row for row in base_correct if row.get("operator_uptake_candidate")]
        summary[f"{artifact_type} | {level} | {signal}"] = {
            "records": len(group_rows),
            "base_correct_records": len(base_correct),
            "outcomes": dict(sorted(Counter(str(row["outcome"]) for row in group_rows).items())),
            "authority_violation_count": len(violations),
            "authority_violation_rate": len(violations) / len(base_correct) if base_correct else None,
            "wrong_answer_uptake_count": len(uptake),
            "wrong_answer_uptake_rate": len(uptake) / len(base_correct) if base_correct else None,
            "operator_uptake_candidate_count": len(operator),
            "operator_uptake_candidate_rate": len(operator) / len(base_correct) if base_correct else None,
        }
    return deltas, summary


def authority_by(deltas: list[Mapping[str, Any]], *keys: str) -> dict[str, dict[str, Any]]:
    groups: dict[tuple[str, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in deltas:
        groups[tuple("" if row.get(key) is None else str(row.get(key)) for key in keys)].append(row)
    out: dict[str, dict[str, Any]] = {}
    for key, group_rows in sorted(groups.items()):
        base_correct = [row for row in group_rows if row.get("base_correct") is True]
        violations = [row for row in base_correct if row.get("authority_violation")]
        answer_uptake = [row for row in base_correct if row.get("wrong_answer_uptake")]
        operator = [row for row in base_correct if row.get("operator_uptake_candidate")]
        out[" | ".join(key)] = {
            "records": len(group_rows),
            "base_correct_records": len(base_correct),
            "authority_violation_count": len(violations),
            "authority_violation_rate": len(violations) / len(base_correct) if base_correct else None,
            "wrong_answer_uptake_count": len(answer_uptake),
            "wrong_answer_uptake_rate": len(answer_uptake) / len(base_correct) if base_correct else None,
            "operator_uptake_candidate_count": len(operator),
            "operator_uptake_candidate_rate": len(operator) / len(base_correct) if base_correct else None,
        }
    return out


def pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def render_group_table(title: str, grouped: Mapping[str, Mapping[str, Any]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, row in grouped.items():
        lines.append(
            f"| {key} | {row['records']} | {pct(row.get('semantic_accuracy_known'))} | "
            f"{row['semantic_unknown']} | {pct(row.get('wrong_answer_uptake_rate'))} | "
            f"{pct(row.get('artifact_answer_uptake_rate'))} | {pct(row.get('artifact_text_overlap_rate'))} |"
        )
    lines.append("")
    return lines


def render_delta_table(title: str, grouped: Mapping[str, Mapping[str, Any]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Slice | Records | Base-right | Outcomes | AVR | Answer uptake | Operator uptake candidate |",
        "| --- | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for key, row in grouped.items():
        lines.append(
            f"| {key} | {row['records']} | {row['base_correct_records']} | `{row['outcomes']}` | "
            f"{pct(row.get('authority_violation_rate'))} | {pct(row.get('wrong_answer_uptake_rate'))} | "
            f"{pct(row.get('operator_uptake_candidate_rate'))} |"
        )
    lines.append("")
    return lines


def render_authority_table(title: str, grouped: Mapping[str, Mapping[str, Any]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, row in grouped.items():
        lines.append(
            f"| {key} | {row['records']} | {row['base_correct_records']} | "
            f"{row['authority_violation_count']} | {pct(row.get('authority_violation_rate'))} | "
            f"{row['wrong_answer_uptake_count']} | {row['operator_uptake_candidate_count']} |"
        )
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# MATH Authority Genesis Ladder Evaluation",
        "",
        f"- Prediction source: `{summary['prediction_source']}`",
        f"- Records: `{summary['overall']['records']}`",
        f"- Known semantic accuracy: `{pct(summary['overall']['semantic_accuracy_known'])}`",
        f"- Semantic unknown: `{summary['overall']['semantic_unknown']}`",
        "",
    ]
    lines.extend(render_group_table("By Variant", summary["by_variant"]))
    lines.extend(render_group_table("By Artifact Type And Future Signal", summary["by_artifact_type_future_signal"]))
    lines.extend(render_delta_table("Paired Deltas By Artifact Type And Future Signal", summary["paired_delta_by_artifact_type_future_signal"]))
    lines.extend(render_authority_table("Authority By Future Signal", summary["authority_by_future_signal"]))
    lines.extend(render_authority_table("Authority By Artifact Type And Future Signal", summary["authority_by_artifact_type_future_signal"]))
    lines.extend(render_authority_table("Authority By Source Surface And Future Signal", summary["authority_by_source_surface_future_signal"]))
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
        "by_artifact_type": group_by(evaluated, "artifact_type"),
        "by_future_signal": group_by(evaluated, "future_level", "future_signal"),
        "by_artifact_type_future_signal": group_by(evaluated, "artifact_type", "future_level", "future_signal"),
        "by_source_surface_future_signal": group_by(evaluated, "source_surface", "future_level", "future_signal"),
        "paired_delta_by_artifact_type_future_signal": delta_summary,
        "authority_by_future_signal": authority_by(deltas, "future_level", "future_signal"),
        "authority_by_artifact_type_future_signal": authority_by(deltas, "artifact_type", "future_level", "future_signal"),
        "authority_by_source_surface_future_signal": authority_by(deltas, "source_surface", "future_level", "future_signal"),
        "authority_by_final_answer_authority_seed": authority_by(deltas, "final_answer_authority_visible_seed", "future_level", "future_signal"),
        "note": (
            "Authority Violation Rate is base-correct rows that become semantically wrong. "
            "Wrong-answer uptake is semantic equivalence to the wrong peer answer. "
            "Operator-uptake candidates are violations without wrong-answer uptake and require manual audit."
        ),
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
    parser.add_argument("--prediction-source", choices=["outputs", "gold"], default="outputs")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
