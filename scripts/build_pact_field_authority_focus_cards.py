#!/usr/bin/env python3
"""Extract compact focus cards from PACT field-bridge audits."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping


DEFAULT_BRIDGE_CASES = Path(
    "experiments/20260615-local-pact-public-state-field-bridge-offset150/bridge_cases.jsonl"
)
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-field-authority-focus-offset150")
DEFAULT_FAMILIES = [
    "public_target_without_question_regression",
    "frozen_question_target_rescue",
    "frozen_question_target_regression",
]


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


def condition(row: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    return (row.get("conditions") or {}).get(name) or {}


def compact_condition(row: Mapping[str, Any], name: str) -> Dict[str, Any]:
    data = condition(row, name)
    return {
        "correct": bool(data.get("correct")),
        "prediction": data.get("prediction"),
        "f1": data.get("f1"),
        "span_error_family": data.get("span_error_family"),
    }


def build_cards(rows: Iterable[Mapping[str, Any]], families: set[str]) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for row in rows:
        if str(row.get("bridge_family")) not in families:
            continue
        event = row.get("source_final_event") or {}
        target_slot = row.get("target_slot_diagnostic") or {}
        cards.append({
            "sample_index": row.get("sample_index"),
            "source_run": row.get("source_run"),
            "bridge_layer": row.get("bridge_layer"),
            "bridge_family": row.get("bridge_family"),
            "question": row.get("question"),
            "gold_answer": row.get("gold_answer"),
            "action_required": event.get("action_required"),
            "environment_state": event.get("environment_state"),
            "action_result": event.get("action_result"),
            "final_answer": event.get("final_answer"),
            "target_slot_drift_candidate": bool(row.get("target_slot_drift_candidate")),
            "candidate_reasons": list(target_slot.get("candidate_reasons") or []),
            "base_public_state_no_final": compact_condition(row, "question_plus_public_state_no_final"),
            "frozen_target_plus_evidence": compact_condition(row, "frozen_target_plus_evidence_no_final"),
            "public_target_only": compact_condition(row, "public_target_plus_evidence_no_question_no_final"),
            "hide_public_target": compact_condition(row, "question_plus_evidence_no_target_no_final"),
        })
    return sorted(cards, key=lambda x: (int(x["sample_index"]), str(x["source_run"]), str(x["bridge_family"])))


def md_cell(value: Any) -> str:
    return " ".join(("" if value is None else str(value)).split()).replace("|", "\\|")


def render_markdown(summary: Mapping[str, Any], cards: List[Mapping[str, Any]], args: argparse.Namespace) -> str:
    lines = [
        "# PACT Field-Authority Focus Cards",
        "",
        "These cards extract target-authority and target-contract focus units from a packet-derived bridge audit.",
        "",
        "## Sources",
        "",
        f"- Bridge cases: `{args.bridge_cases}`",
        "",
        "## Counts",
        "",
        f"- Cards: `{summary['cards']}`",
        f"- Unique samples: `{summary['unique_samples']}`",
        f"- Families: `{summary['family_counts']}`",
        "",
        "## Cards",
        "",
        "| Sample | Source | Family | Gold | Public target | Base | Frozen | Target only |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for card in cards:
        lines.append(
            "| {sample} | {source} | {family} | {gold} | {target} | {base} | {frozen} | {target_only} |".format(
                sample=card["sample_index"],
                source=md_cell(card["source_run"]),
                family=md_cell(card["bridge_family"]),
                gold=md_cell(card["gold_answer"]),
                target=md_cell(card["action_required"]),
                base=md_cell(card["base_public_state_no_final"]["prediction"]),
                frozen=md_cell(card["frozen_target_plus_evidence"]["prediction"]),
                target_only=md_cell(card["public_target_only"]["prediction"]),
            )
        )
    lines.extend([
        "",
        "## Caveat",
        "",
        "These are extraction cards only. Semantic categories, if added in a report, are manual inspection labels.",
        "",
    ])
    return "\n".join(lines)


def build(args: argparse.Namespace) -> Dict[str, Any]:
    families = set(args.family)
    cards = build_cards(load_jsonl(args.bridge_cases), families)
    summary = {
        "cards": len(cards),
        "unique_samples": len({card["sample_index"] for card in cards}),
        "family_counts": dict(sorted(Counter(str(card["bridge_family"]) for card in cards).items())),
        "source_run_counts": dict(sorted(Counter(str(card["source_run"]) for card in cards).items())),
        "target_slot_candidate_counts": dict(
            sorted(Counter(str(card["target_slot_drift_candidate"]) for card in cards).items())
        ),
        "source_paths": {
            "bridge_cases": str(args.bridge_cases),
        },
        "note": "Extraction-only focus cards; semantic labels are manual report work.",
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "focus_cards.jsonl", cards)
    write_text(args.out_dir / "focus_cards.md", render_markdown(summary, cards, args))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-cases", type=Path, default=DEFAULT_BRIDGE_CASES)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--family", action="append", default=list(DEFAULT_FAMILIES))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
