#!/usr/bin/env python3
"""Preview typed-public-state peer surfaces from saved source cases."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

from peer_probe.answers import contains_answer
from peer_probe.io_utils import read_jsonl, write_json, write_jsonl
from peer_probe.surfaces import TYPED_PUBLIC_STATE_CONDITIONS, peer_messages


def build_preview_records(cases: List[Dict[str, Any]], conditions: List[str]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for case in cases:
        for condition in conditions:
            peers = peer_messages(case, condition)
            for peer in peers:
                text = peer.get("text") or ""
                source_answer = peer.get("source_answer") or peer.get("answer")
                records.append(
                    {
                        "case_index": case.get("case_index"),
                        "instance_id": case.get("instance_id"),
                        "condition": condition,
                        "surface": peer.get("surface"),
                        "expected_correct": peer.get("expected_correct"),
                        "source": peer.get("source"),
                        "source_identity_visible": peer.get("source_identity_visible", "true"),
                        "source_answer": source_answer,
                        "gold_answer": case.get("gold_answer"),
                        "contains_source_answer": contains_answer(text, source_answer),
                        "source_answer_redaction_count": peer.get("source_answer_redaction_count"),
                        "char_len": len(text),
                        "text": text,
                    }
                )
    return records


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_condition: Dict[str, Counter[str]] = defaultdict(Counter)
    char_lengths: Dict[str, List[int]] = defaultdict(list)
    for row in records:
        condition = str(row["condition"])
        by_condition[condition]["records"] += 1
        if row.get("contains_source_answer"):
            by_condition[condition]["contains_source_answer"] += 1
        if row.get("source_identity_visible") == "false":
            by_condition[condition]["anonymous_source"] += 1
        char_lengths[condition].append(int(row.get("char_len") or 0))
    condition_summary = {}
    for condition, counts in sorted(by_condition.items()):
        lengths = char_lengths[condition]
        condition_summary[condition] = {
            **dict(counts),
            "avg_chars": sum(lengths) / len(lengths) if lengths else 0,
            "max_chars": max(lengths) if lengths else 0,
        }
    return {
        "records": len(records),
        "conditions": condition_summary,
        "notes": [
            "This preview does not call a model; it only checks the deterministic surface shown to a future target model.",
            "contains_source_answer is a mechanical containment check, not semantic leakage judging.",
            "Typed-public-state surfaces hide source identity and explicit final-answer slots, but intentionally preserve copied equation/numeric fields for diagnostic pressure.",
        ],
    }


def write_readme(out_dir: Path, summary: Dict[str, Any], command: str) -> None:
    lines = [
        "# Typed Public-State Preview",
        "",
        "## What This Is",
        "",
        "A local preview of deterministic typed-public-state peer surfaces built from",
        "saved mixed-correctness source cases. It does not call a model.",
        "",
        "## Command",
        "",
        "```bash",
        command,
        "```",
        "",
        "## Summary",
        "",
        "| Condition | Records | Contains Source Answer | Anonymous Source | Avg Chars | Max Chars |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition, stats in summary["conditions"].items():
        lines.append(
            f"| `{condition}` | {stats.get('records', 0)} | "
            f"{stats.get('contains_source_answer', 0)} | "
            f"{stats.get('anonymous_source', 0)} | "
            f"{stats.get('avg_chars', 0):.1f} | {stats.get('max_chars', 0)} |"
        )
    lines += ["", "## Notes", ""]
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")
    out_dir.joinpath("README.md").write_text("\n".join(lines), encoding="utf-8")


def build(args: argparse.Namespace) -> Dict[str, Any]:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    cases = read_jsonl(args.source_cases_jsonl)
    records = build_preview_records(cases, args.conditions)
    summary = summarize(records)
    summary["source_cases_jsonl"] = str(args.source_cases_jsonl)
    summary["num_cases"] = len(cases)
    summary["cases"] = [case.get("case_index") for case in cases]
    write_jsonl(args.out_dir / "typed_public_state_preview.jsonl", records)
    write_json(args.out_dir / "summary.json", summary)
    write_readme(args.out_dir, summary, "python scripts/build_typed_public_state_preview.py " + " ".join(args.raw_args))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cases-jsonl", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--conditions",
        nargs="+",
        choices=sorted(TYPED_PUBLIC_STATE_CONDITIONS),
        default=sorted(TYPED_PUBLIC_STATE_CONDITIONS),
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.raw_args = list(sys.argv[1:])
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
