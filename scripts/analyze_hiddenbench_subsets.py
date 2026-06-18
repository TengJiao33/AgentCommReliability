#!/usr/bin/env python3
"""Build clean-information subset summaries for HiddenBench probe records."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


DEFAULT_PAIRS = [
    ("fact_only_exchange", "exchange_then_decide"),
    ("no_recommendation_exchange", "exchange_then_decide"),
    ("no_shared_repeat_exchange", "exchange_then_decide"),
    ("fact_only_exchange", "no_recommendation_exchange"),
    ("fact_only_exchange", "no_shared_repeat_exchange"),
    ("fact_only_exchange", "fact_only_with_options_exchange"),
    ("blind_exchange", "exchange_then_decide"),
    ("blind_minimal_exchange", "exchange_then_decide"),
    ("blind_minimal_exchange", "private_plus_task_minimal_exchange"),
    ("blind_minimal_exchange", "private_plus_options_minimal_exchange"),
    ("blind_minimal_exchange", "private_plus_shared_minimal_exchange"),
    ("blind_minimal_exchange", "full_visibility_minimal_exchange"),
    ("fact_only_exchange", "blind_exchange"),
    ("fact_only_exchange", "blind_minimal_exchange"),
    ("fact_only_exchange", "full_visibility_minimal_exchange"),
    ("blind_minimal_exchange", "blind_exchange"),
    ("full_visibility_minimal_exchange", "exchange_then_decide"),
    ("fact_only_constraint_decide", "fact_only_exchange"),
]


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def is_correct(row: Mapping[str, Any]) -> bool:
    if "rescored_correct" in row:
        return bool(row.get("rescored_correct"))
    return bool(row.get("correct"))


def parsed_answer(row: Mapping[str, Any]) -> Any:
    if "rescored_answer" in row:
        return row.get("rescored_answer")
    return row.get("parsed_answer")


def parse_source(row: Mapping[str, Any]) -> str:
    if "rescored_parse_source" in row:
        return str(row.get("rescored_parse_source"))
    return str(row.get("parse_source"))


def task_info(task_rows: Mapping[str, Mapping[str, Any]], task_id: int) -> Dict[str, Any]:
    row = next(iter(task_rows.values()))
    return {
        "task_id": task_id,
        "task_name": row.get("task_name"),
        "gold_answer": row.get("gold_answer"),
    }


def summarize_conditions(
    by_task: Mapping[int, Mapping[str, Mapping[str, Any]]],
    task_ids: Sequence[int],
    conditions: Sequence[str],
) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for condition in conditions:
        rows = [by_task[task_id][condition] for task_id in task_ids if condition in by_task[task_id]]
        total = len(rows)
        correct = sum(1 for row in rows if is_correct(row))
        unparsed = sum(1 for row in rows if parse_source(row) == "unparsed")
        out[condition] = {
            "records": total,
            "correct": correct,
            "accuracy": correct / total if total else None,
            "unparsed": unparsed,
        }
    return out


def pair_summary(
    by_task: Mapping[int, Mapping[str, Mapping[str, Any]]],
    task_ids: Sequence[int],
    left: str,
    right: str,
) -> Dict[str, Any]:
    paired = [task_id for task_id in task_ids if left in by_task[task_id] and right in by_task[task_id]]
    left_only = [
        task_id for task_id in paired if is_correct(by_task[task_id][left]) and not is_correct(by_task[task_id][right])
    ]
    right_only = [
        task_id for task_id in paired if is_correct(by_task[task_id][right]) and not is_correct(by_task[task_id][left])
    ]
    both_correct = [
        task_id for task_id in paired if is_correct(by_task[task_id][left]) and is_correct(by_task[task_id][right])
    ]
    both_wrong = [
        task_id for task_id in paired if not is_correct(by_task[task_id][left]) and not is_correct(by_task[task_id][right])
    ]
    return {
        "paired_tasks": len(paired),
        "left_correct_right_wrong": len(left_only),
        "right_correct_left_wrong": len(right_only),
        "both_correct": len(both_correct),
        "both_wrong": len(both_wrong),
        "left_only_tasks": [
            {
                **task_info(by_task[task_id], task_id),
                "left_answer": parsed_answer(by_task[task_id][left]),
                "right_answer": parsed_answer(by_task[task_id][right]),
            }
            for task_id in left_only
        ],
        "right_only_tasks": [
            {
                **task_info(by_task[task_id], task_id),
                "left_answer": parsed_answer(by_task[task_id][left]),
                "right_answer": parsed_answer(by_task[task_id][right]),
            }
            for task_id in right_only
        ],
    }


def parse_pairs(values: Iterable[str]) -> List[Tuple[str, str]]:
    pairs = []
    for value in values:
        if ":" not in value:
            raise SystemExit(f"Pair must be LEFT:RIGHT, got {value!r}")
        left, right = value.split(":", 1)
        pairs.append((left, right))
    return pairs


def build(args: argparse.Namespace) -> Dict[str, Any]:
    rows = load_jsonl(args.records)
    by_task: Dict[int, Dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_task[int(row["task_id"])][str(row["condition"])] = row

    all_task_ids = sorted(by_task)
    conditions = sorted({str(row["condition"]) for row in rows})
    full_info_task_ids = [
        task_id
        for task_id in all_task_ids
        if args.full_condition in by_task[task_id] and is_correct(by_task[task_id][args.full_condition])
    ]
    clean_task_ids = [
        task_id
        for task_id in full_info_task_ids
        if args.oracle_condition in by_task[task_id] and is_correct(by_task[task_id][args.oracle_condition])
    ]
    unstable_task_ids = [task_id for task_id in all_task_ids if task_id not in set(clean_task_ids)]
    pairs = parse_pairs(args.pair) if args.pair else DEFAULT_PAIRS

    subsets = {
        "all": all_task_ids,
        f"{args.full_condition}_correct": full_info_task_ids,
        f"{args.full_condition}_and_{args.oracle_condition}_correct": clean_task_ids,
        "clean_info_unstable": unstable_task_ids,
    }
    payload = {
        "records": str(args.records),
        "conditions": conditions,
        "subsets": {
            name: {
                "tasks": len(task_ids),
                "conditions": summarize_conditions(by_task, task_ids, conditions),
            }
            for name, task_ids in subsets.items()
        },
        "primary_pairs": {
            f"{subset_name}:{left}_vs_{right}": pair_summary(by_task, task_ids, left, right)
            for subset_name, task_ids in subsets.items()
            for left, right in pairs
            if any(left in by_task[task_id] and right in by_task[task_id] for task_id in task_ids)
        },
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "subset_summary.json", payload)
    write_text(args.out_dir / "subset_summary.md", render_markdown(payload))
    return payload


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = ["# HiddenBench Subset Summary", "", f"- Records: `{summary['records']}`", ""]
    conditions = list(summary["conditions"])
    for subset_name, subset in summary["subsets"].items():
        lines.extend(
            [
                f"## {subset_name}",
                "",
                f"- Tasks: `{subset['tasks']}`",
                "",
                "| Condition | Correct | Records | Accuracy | Unparsed |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for condition in conditions:
            row = subset["conditions"][condition]
            accuracy = row["accuracy"]
            accuracy_text = "n/a" if accuracy is None else f"{accuracy:.3f}"
            lines.append(
                f"| `{condition}` | `{row['correct']}` | `{row['records']}` | "
                f"`{accuracy_text}` | `{row['unparsed']}` |"
            )
        lines.append("")

    lines.extend(["## Primary Pairs", ""])
    for key, row in summary["primary_pairs"].items():
        lines.append(
            f"- `{key}`: paired `{row['paired_tasks']}`, left-only `{row['left_correct_right_wrong']}`, "
            f"right-only `{row['right_correct_left_wrong']}`, both-correct `{row['both_correct']}`, "
            f"both-wrong `{row['both_wrong']}`"
        )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--full-condition", default="full_info")
    parser.add_argument("--oracle-condition", default="oracle_public_facts")
    parser.add_argument("--pair", action="append", help="Paired contrast in LEFT:RIGHT form; may be repeated.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    compact = {
        "records": summary["records"],
        "subsets": {name: subset["tasks"] for name, subset in summary["subsets"].items()},
        "primary_pairs": {
            key: {field: row[field] for field in ["paired_tasks", "left_correct_right_wrong", "right_correct_left_wrong", "both_correct", "both_wrong"]}
            for key, row in summary["primary_pairs"].items()
        },
    }
    print(json.dumps(compact, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
