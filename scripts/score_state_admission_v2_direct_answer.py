#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalize_answer(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.lower().strip().split())


def parse_response(row: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    try:
        response = row.get("response")
        parsed = json.loads(response) if isinstance(response, str) else response
        if not isinstance(parsed, dict):
            return {}, "response_not_object"
        return parsed, None
    except Exception as error:  # noqa: BLE001
        return {}, f"{type(error).__name__}: {error}"


def final_state(parsed: dict[str, Any]) -> dict[str, Any]:
    state = parsed.get("final_decider_state", {})
    return state if isinstance(state, dict) else {}


def gold_answer_ok(packet: dict[str, Any], parsed: dict[str, Any]) -> bool:
    answer = normalize_answer(final_state(parsed).get("answer"))
    gold = normalize_answer(packet.get("gold_answer"))
    return bool(gold) and answer == gold


def admissible_downstream_ok(packet: dict[str, Any], parsed: dict[str, Any]) -> bool:
    state = final_state(parsed)
    expected = str(packet.get("expected_downstream_state", "")).lower()
    status = str(state.get("status", "")).lower()
    answer = normalize_answer(state.get("answer"))
    gold = normalize_answer(packet.get("gold_answer"))
    expects_insufficient = any(token in expected for token in ["insufficient", "cannot", "should not", "not count"])
    if expects_insufficient:
        return "insufficient" in status or answer in {"", "null", "none"}
    return bool(gold) and answer == gold


def score_row(packet: dict[str, Any], prediction: dict[str, Any]) -> dict[str, Any]:
    parsed, parse_error = parse_response(prediction)
    status = prediction.get("status", "missing")
    if not prediction:
        status = "missing"
        parse_error = "missing_prediction"
    metrics = {
        "gold_answer_ok": 0.0 if parse_error else float(gold_answer_ok(packet, parsed)),
        "admissible_downstream_ok": 0.0 if parse_error else float(admissible_downstream_ok(packet, parsed)),
    }
    return {
        "packet_id": packet["packet_id"],
        "sketch_id": packet["sketch_id"],
        "variant_id": packet["variant_id"],
        "condition": packet["condition"],
        "prompt_style": prediction.get("prompt_style"),
        "prediction_status": status,
        "parse_error": parse_error,
        "metrics": metrics,
    }


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metric_names = ["gold_answer_ok", "admissible_downstream_ok"]
    summary = {
        "rows": len(rows),
        "metrics": {name: mean([float(row["metrics"][name]) for row in rows]) for name in metric_names},
        "by_condition": {},
    }
    for condition in sorted({row["condition"] for row in rows}):
        subset = [row for row in rows if row["condition"] == condition]
        summary["by_condition"][condition] = {
            name: mean([float(row["metrics"][name]) for row in subset]) for name in metric_names
        }
    return summary


def format_summary(summary: dict[str, Any]) -> str:
    lines = [f"rows: {summary['rows']}"]
    for name, value in summary["metrics"].items():
        lines.append(f"{name}: {value:.4f}")
    for condition, metrics in summary["by_condition"].items():
        joined = ", ".join(f"{name}={value:.4f}" for name, value in metrics.items())
        lines.append(f"{condition}: {joined}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    args = parser.parse_args()

    packet = {row["packet_id"]: row for row in read_jsonl(args.packet)}
    predictions = {row["packet_id"]: row for row in read_jsonl(args.predictions)}
    scored = [score_row(row, predictions.get(packet_id, {})) for packet_id, row in packet.items()]
    write_jsonl(args.out, scored)
    summary = summarize(scored)
    args.summary_out.write_text(format_summary(summary) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
