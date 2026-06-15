#!/usr/bin/env python3
"""Preview legacy versus raw answer-only peer surfaces from saved source cases."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from peer_probe.io_utils import read_jsonl, write_json, write_jsonl
from peer_probe.math_eval import math_equiv
from peer_probe.surfaces import peer_messages, raw_peer_answer


POLARITIES = ["correct", "wrong"]


def build_records(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for case in cases:
        for polarity in POLARITIES:
            source_peer = case[f"{polarity}_peer"]
            legacy_condition = f"{polarity}_answer_only"
            raw_condition = f"{polarity}_raw_answer_only"
            legacy_peer = peer_messages(case, legacy_condition)[0]
            raw_peer = peer_messages(case, raw_condition)[0]
            legacy_answer = legacy_peer.get("answer")
            raw_answer = raw_peer_answer(source_peer)
            equivalence = math_equiv(legacy_answer, raw_answer)
            records.append(
                {
                    "case_index": case.get("case_index"),
                    "instance_id": case.get("instance_id"),
                    "polarity": polarity,
                    "legacy_condition": legacy_condition,
                    "raw_condition": raw_condition,
                    "legacy_answer": legacy_answer,
                    "raw_answer": raw_answer,
                    "equivalent": equivalence.correct,
                    "equivalence_status": equivalence.status,
                    "legacy_surface_text": legacy_peer.get("text"),
                    "raw_surface_text": raw_peer.get("text"),
                    "display_changed": legacy_peer.get("text") != raw_peer.get("text"),
                    "question": case.get("question"),
                }
            )
    return records


def summarize(records: List[Dict[str, Any]], source_cases_jsonl: Path) -> Dict[str, Any]:
    counts: Counter[str] = Counter()
    by_polarity: Dict[str, Counter[str]] = {polarity: Counter() for polarity in POLARITIES}
    mismatch_cases = set()
    unknown_cases = set()
    for row in records:
        if row["equivalent"] is True:
            bucket = "equivalent"
        elif row["equivalent"] is False:
            bucket = "semantic_mismatch"
            mismatch_cases.add(row["case_index"])
        else:
            bucket = "unknown_equivalence"
            unknown_cases.add(row["case_index"])
        counts[bucket] += 1
        if row.get("display_changed"):
            counts["display_changed"] += 1
        by_polarity[str(row["polarity"])][bucket] += 1
    return {
        "source_cases_jsonl": str(source_cases_jsonl),
        "records": len(records),
        "counts": dict(counts),
        "by_polarity": {key: dict(value) for key, value in by_polarity.items()},
        "semantic_mismatch_cases": sorted(mismatch_cases),
        "unknown_equivalence_cases": sorted(unknown_cases),
        "notes": [
            "This preview does not call a model; it only compares the legacy numeric answer-only surface with the raw final-answer text extracted from the saved peer response.",
            "The raw answer-only surface is meant for future peer-influence controls on symbolic MATH answers; existing answer-only runs remain reproducible as legacy parser surfaces.",
            "Equivalence is conservative and may remain unknown for forms such as base notation or hard-to-parse generated answer strings.",
        ],
    }


def write_readme(out_dir: Path, summary: Dict[str, Any], command: str) -> None:
    lines = [
        "# Raw Answer-Only Preview",
        "",
        "## What This Is",
        "",
        "A local preview comparing legacy numeric `answer_only` surfaces with",
        "new raw-answer-only surfaces built from saved peer responses. It does",
        "not call a model.",
        "",
        "## Command",
        "",
        "```bash",
        command,
        "```",
        "",
        "## Summary",
        "",
        "| Bucket | Rows |",
        "| --- | ---: |",
    ]
    for key, value in summary["counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "By polarity:",
            "",
            "| Polarity | Equivalent | Semantic mismatch | Unknown |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for polarity, counts in summary["by_polarity"].items():
        lines.append(
            f"| `{polarity}` | {counts.get('equivalent', 0)} | "
            f"{counts.get('semantic_mismatch', 0)} | {counts.get('unknown_equivalence', 0)} |"
        )
    lines += ["", "## Notes", ""]
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    out_dir.joinpath("README.md").write_text("\n".join(lines), encoding="utf-8")


def build(args: argparse.Namespace) -> Dict[str, Any]:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    cases = read_jsonl(args.source_cases_jsonl)
    records = build_records(cases)
    summary = summarize(records, args.source_cases_jsonl)
    summary["num_cases"] = len(cases)
    summary["cases"] = [case.get("case_index") for case in cases]
    write_jsonl(args.out_dir / "raw_answer_only_preview.jsonl", records)
    write_json(args.out_dir / "summary.json", summary)
    write_readme(args.out_dir, summary, "python scripts/build_raw_answer_only_preview.py " + " ".join(args.raw_args))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cases-jsonl", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.raw_args = list(sys.argv[1:])
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
