#!/usr/bin/env python3
"""Compare repeated redacted peer-exposure records across runs.

This local helper aligns saved peer-exposure records by task family, case index,
and condition. It is useful when the same evidence surface appears in multiple
runs but the target model's response changes.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


DEFAULT_CONDITIONS = ("correct_redacted_evidence", "wrong_redacted_evidence")


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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def norm_answer(value: Any) -> str:
    if value is None:
        return "None"
    return str(value).strip()


def infer_source_family(run_dir: Path, record: Dict[str, Any]) -> str:
    explicit = record.get("source_family") or record.get("source_format") or record.get("dataset")
    if explicit:
        return str(explicit)
    name = run_dir.name.lower()
    if "math" in name or "madmm" in name:
        return "MAD-MM"
    if "dar" in name or "gsm8k" in name:
        return "DAR"
    return "unknown"


def record_key(record: Dict[str, Any], run_dir: Path) -> Tuple[str, str, str]:
    return (
        infer_source_family(run_dir, record),
        str(record.get("case_index")),
        str(record.get("condition")),
    )


def compact_record(record: Dict[str, Any], run_dir: Path) -> Dict[str, Any]:
    peer_exposure = record.get("peer_exposure") or []
    peer = peer_exposure[0] if peer_exposure else {}
    return {
        "run_id": record.get("run_id") or run_dir.name,
        "run_dir": str(run_dir),
        "case_index": record.get("case_index"),
        "source_family": infer_source_family(run_dir, record),
        "condition": record.get("condition"),
        "pre_exposure_answer": record.get("pre_exposure_answer"),
        "post_exposure_answer": record.get("post_exposure_answer"),
        "source_answer": record.get("source_answer"),
        "gold_answer": record.get("gold_answer"),
        "pre_exposure_correct": record.get("pre_exposure_correct"),
        "post_exposure_correct": record.get("post_exposure_correct"),
        "transition": record.get("transition"),
        "target_behavior": record.get("target_behavior"),
        "peer_answer_adopted": record.get("peer_answer_adopted"),
        "evidence_text": peer.get("text"),
    }


def load_records(run_dirs: Iterable[Path], conditions: set[str]) -> Dict[Tuple[str, str, str], List[Dict[str, Any]]]:
    groups: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = {}
    for run_dir in run_dirs:
        for record in load_jsonl(run_dir / "peer_exposure_records.jsonl"):
            if record.get("condition") not in conditions:
                continue
            key = record_key(record, run_dir)
            groups.setdefault(key, []).append(compact_record(record, run_dir))
    return groups


def build_cases(groups: Dict[Tuple[str, str, str], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for (source_family, case_index, condition), records in groups.items():
        if len(records) < 2:
            continue
        records.sort(key=lambda row: str(row["run_id"]))
        post_answers = sorted({norm_answer(row.get("post_exposure_answer")) for row in records})
        transitions = sorted({str(row.get("transition")) for row in records})
        target_behaviors = sorted({str(row.get("target_behavior")) for row in records})
        evidence_texts = sorted({str(row.get("evidence_text")) for row in records})
        cases.append(
            {
                "case_key": f"{source_family}::{case_index}::{condition}",
                "source_family": source_family,
                "case_index": int(case_index),
                "condition": condition,
                "runs": len(records),
                "post_answer_values": post_answers,
                "transition_values": transitions,
                "target_behavior_values": target_behaviors,
                "evidence_text_values": evidence_texts,
                "post_answer_varies": len(post_answers) > 1,
                "transition_varies": len(transitions) > 1,
                "target_behavior_varies": len(target_behaviors) > 1,
                "evidence_text_varies": len(evidence_texts) > 1,
                "records": records,
            }
        )
    cases.sort(key=lambda row: (not (row["post_answer_varies"] or row["transition_varies"] or row["target_behavior_varies"]), row["source_family"], row["case_index"], row["condition"]))
    return cases


def summarize(cases: List[Dict[str, Any]], args: argparse.Namespace) -> Dict[str, Any]:
    repeated = len(cases)
    variable = [row for row in cases if row["post_answer_varies"] or row["transition_varies"] or row["target_behavior_varies"]]
    return {
        "run_dirs": [str(path) for path in args.run_dirs],
        "conditions": list(args.conditions),
        "repeated_case_conditions": repeated,
        "variable_case_conditions": len(variable),
        "post_answer_variable": sum(1 for row in cases if row["post_answer_varies"]),
        "transition_variable": sum(1 for row in cases if row["transition_varies"]),
        "target_behavior_variable": sum(1 for row in cases if row["target_behavior_varies"]),
        "evidence_text_variable": sum(1 for row in cases if row["evidence_text_varies"]),
        "variable_by_condition": dict(Counter(row["condition"] for row in variable)),
        "variable_case_keys": [row["case_key"] for row in variable],
    }


def write_markdown(path: Path, cases: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    variable = [row for row in cases if row["post_answer_varies"] or row["transition_varies"] or row["target_behavior_varies"]]
    lines = [
        "# Peer Redacted Repeat Variability",
        "",
        f"- Repeated case/conditions: `{summary['repeated_case_conditions']}`",
        f"- Variable case/conditions: `{summary['variable_case_conditions']}`",
        f"- Variable keys: `{summary['variable_case_keys']}`",
        "",
    ]
    for row in variable:
        lines += [
            f"## {row['case_key']}",
            "",
            f"- Post answers: `{row['post_answer_values']}`",
            f"- Transitions: `{row['transition_values']}`",
            f"- Target behaviors: `{row['target_behavior_values']}`",
            f"- Evidence text varies: `{row['evidence_text_varies']}`",
            "",
        ]
        for record in row["records"]:
            lines += [
                f"### {record['run_id']}",
                "",
                f"- pre -> post: `{record['pre_exposure_answer']}` -> `{record['post_exposure_answer']}`",
                f"- transition: `{record['transition']}`",
                f"- target behavior: `{record['target_behavior']}`",
                f"- source/gold: `{record['source_answer']}` / `{record['gold_answer']}`",
                "",
                "Evidence:",
                "",
                str(record.get("evidence_text") or ""),
                "",
            ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dirs", type=Path, nargs="+", required=True)
    parser.add_argument("--conditions", nargs="*", default=list(DEFAULT_CONDITIONS))
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    groups = load_records(args.run_dirs, set(args.conditions))
    cases = build_cases(groups)
    summary = summarize(cases, args)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "repeat_cases.jsonl", cases)
    write_markdown(args.out_dir / "repeat_variability.md", cases, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
