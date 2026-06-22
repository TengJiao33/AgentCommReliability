#!/usr/bin/env python
"""Merge two HSA packet directories and matching transparent-control artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


ARTIFACTS = [
    "hsa_v0_packet.jsonl",
    "predictions_oracle_admissible_facts.jsonl",
    "predictions_shared_only_verified.jsonl",
    "predictions_all_scoped_verified.jsonl",
]


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSONL") from exc
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=False))
            f.write("\n")
            count += 1
    return count


def packet_id(row: dict, path: Path) -> str:
    value = row.get("packet_id")
    if not isinstance(value, str) or not value:
        raise ValueError(f"{path}: row missing string packet_id")
    return value


def assert_no_duplicates(rows: list[dict], path: Path) -> None:
    seen: set[str] = set()
    duplicates: list[str] = []
    for row in rows:
        pid = packet_id(row, path)
        if pid in seen:
            duplicates.append(pid)
        seen.add(pid)
    if duplicates:
        sample = ", ".join(duplicates[:5])
        raise ValueError(f"{path}: duplicate packet_id(s): {sample}")


def assert_same_packet_ids(packet_rows: list[dict], prediction_rows: list[dict], artifact: str) -> None:
    packet_ids = [packet_id(row, Path("packet")) for row in packet_rows]
    prediction_ids = [packet_id(row, Path(artifact)) for row in prediction_rows]
    if packet_ids != prediction_ids:
        packet_set = set(packet_ids)
        prediction_set = set(prediction_ids)
        missing = sorted(packet_set - prediction_set)
        extra = sorted(prediction_set - packet_set)
        raise ValueError(
            f"{artifact}: packet_id order/content mismatch; "
            f"missing={missing[:5]}, extra={extra[:5]}"
        )


def merge_artifact(left_dir: Path, right_dir: Path, out_dir: Path, artifact: str) -> dict:
    left_path = left_dir / artifact
    right_path = right_dir / artifact
    if not left_path.exists():
        raise FileNotFoundError(left_path)
    if not right_path.exists():
        raise FileNotFoundError(right_path)

    left_rows = read_jsonl(left_path)
    right_rows = read_jsonl(right_path)
    merged = left_rows + right_rows
    assert_no_duplicates(merged, out_dir / artifact)

    out_path = out_dir / artifact
    out_count = write_jsonl(out_path, merged)
    return {
        "artifact": artifact,
        "left_rows": len(left_rows),
        "right_rows": len(right_rows),
        "merged_rows": out_count,
        "path": str(out_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left-dir", required=True, type=Path)
    parser.add_argument("--right-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summaries = [
        merge_artifact(args.left_dir, args.right_dir, args.out_dir, artifact)
        for artifact in ARTIFACTS
    ]

    packet_rows = read_jsonl(args.out_dir / "hsa_v0_packet.jsonl")
    for artifact in ARTIFACTS[1:]:
        prediction_rows = read_jsonl(args.out_dir / artifact)
        assert_same_packet_ids(packet_rows, prediction_rows, artifact)

    condition_counts: dict[str, int] = {}
    task_counts: dict[str, int] = {}
    for row in packet_rows:
        meta = row.get("hsa_meta") or {}
        condition = str(meta.get("condition", "unknown"))
        task_id = str(row.get("task_id", "unknown")).split("::", 1)[0]
        condition_counts[condition] = condition_counts.get(condition, 0) + 1
        task_counts[task_id] = task_counts.get(task_id, 0) + 1

    summary = {
        "left_dir": str(args.left_dir),
        "right_dir": str(args.right_dir),
        "out_dir": str(args.out_dir),
        "artifacts": summaries,
        "packet_rows": len(packet_rows),
        "condition_counts": condition_counts,
        "task_counts": task_counts,
    }
    summary_path = args.out_dir / "merge_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
