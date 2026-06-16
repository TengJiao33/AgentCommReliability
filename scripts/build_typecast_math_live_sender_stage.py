#!/usr/bin/env python3
"""Build the TypeCastArena MATH live sender-stage packet.

Stage 1 asks Agent A to solve each MATH problem independently and emit a
structured sender artifact. Stage 2, built by
materialize_typecast_math_live_receiver_packet.py, sends those artifacts across
communication boundary regimes to Agent B.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.typecast_arena import FAMILY, render_math_sender_prompt, sha1_text


DEFAULT_SOURCE_ROWS = Path("experiments/20260615-local-math-authority-genesis-ladder-packet/source_rows.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260616-local-typecast-arena-math-live-sender-stage")
PACKET_NAME = "typecast_math_sender_stage_packet.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def select_rows(rows: Sequence[Mapping[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_cases: set[str] = set()
    case_counts: Counter[str] = Counter()

    for row in rows:
        case_id = str(row.get("case_id"))
        math_case_id = str(row.get("math_case_id"))
        if args.case_ids and case_id not in set(args.case_ids):
            continue
        if args.math_case_ids and math_case_id not in {str(value) for value in args.math_case_ids}:
            continue
        if case_id in seen_cases:
            continue
        if case_counts[math_case_id] >= args.max_rows_per_math_case:
            continue
        selected.append(dict(row))
        seen_cases.add(case_id)
        case_counts[math_case_id] += 1
        if args.max_cases and len(selected) >= args.max_cases:
            break
    return selected


def packet_row(source_row: Mapping[str, Any]) -> dict[str, Any]:
    prompt = render_math_sender_prompt(source_row)
    packet_id = f"{source_row['case_id']}::{FAMILY}::live_sender_stage"
    return {
        "packet_id": packet_id,
        "case_id": source_row["case_id"],
        "math_case_id": source_row.get("math_case_id"),
        "condition": source_row.get("condition"),
        "variant": "live_sender_stage",
        "typecast_arena_family": FAMILY,
        "stage": "sender",
        "sender_id": "Agent A",
        "receiver_id": "Agent B",
        "question": source_row.get("question"),
        "gold_answer": source_row.get("gold_answer"),
        "baseline_answer": source_row.get("baseline_answer"),
        "source_surface": source_row.get("source_surface"),
        "source_case_id": source_row.get("case_id"),
        "prompt": prompt,
        "prompt_sha1": sha1_text(prompt),
        "evaluation": {
            "gold_answer": source_row.get("gold_answer"),
            "primary_metric": "math_semantic_equivalence",
            "gold_is_metadata_not_prompt_input": True,
            "stage": "sender_artifact_generation",
        },
    }


def render_readme(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# TypeCastArena MATH Live Sender Stage",
            "",
            "This packet is Stage 1 for a live sender-receiver TypeCastArena run.",
            "Agent A solves each problem independently and emits a structured sender artifact.",
            "",
            "Stage 2 materializes receiver prompts from the model outputs with:",
            "",
            "```bash",
            "python scripts/materialize_typecast_math_live_receiver_packet.py \\",
            "  --sender-packet experiments/20260616-local-typecast-arena-math-live-sender-stage/typecast_math_sender_stage_packet.jsonl \\",
            "  --sender-outputs <sender-run>/outputs.jsonl",
            "```",
            "",
            "## Shape",
            "",
            f"- Source rows: `{summary['source_rows']}`",
            f"- Sender prompt rows: `{summary['packet_rows']}`",
            f"- Rows by source surface: `{summary['rows_by_source_surface']}`",
            f"- Rows by condition: `{summary['rows_by_condition']}`",
            "",
            "## Status",
            "",
            "Setup artifact only. A model run is required before receiver-stage prompts can be materialized from live Agent A outputs.",
            "",
        ]
    )


def build(args: argparse.Namespace) -> dict[str, Any]:
    rows = load_jsonl(args.source_rows)
    selected = select_rows(rows, args)
    packet = [packet_row(row) for row in selected]

    summary = {
        "source_rows_path": str(args.source_rows),
        "source_rows": len(selected),
        "packet_rows": len(packet),
        "rows_by_source_surface": dict(sorted(Counter(str(row.get("source_surface")) for row in selected).items())),
        "rows_by_condition": dict(sorted(Counter(str(row.get("condition")) for row in selected).items())),
        "config": {
            "max_cases": args.max_cases,
            "max_rows_per_math_case": args.max_rows_per_math_case,
            "case_ids": args.case_ids,
            "math_case_ids": args.math_case_ids,
        },
        "outputs": {
            "packet": str(args.out_dir / PACKET_NAME),
            "summary": str(args.out_dir / "summary.json"),
            "README": str(args.out_dir / "README.md"),
        },
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "source_rows.jsonl", selected)
    write_jsonl(args.out_dir / PACKET_NAME, packet)
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "README.md", render_readme(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-rows", type=Path, default=DEFAULT_SOURCE_ROWS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--max-cases", type=int, default=30)
    parser.add_argument("--max-rows-per-math-case", type=int, default=1)
    parser.add_argument("--case-ids", nargs="*")
    parser.add_argument("--math-case-ids", nargs="*")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
