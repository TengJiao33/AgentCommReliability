#!/usr/bin/env python3
"""Split a JSONL packet into fixed-size shards.

This is intentionally generic so large TypeCastArena packets can be prepared
locally and later run as short single-GPU jobs without changing the packet
schema.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_lines(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig") as f:
        return [line for line in f if line.strip()]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def split(args: argparse.Namespace) -> dict[str, Any]:
    lines = read_lines(args.packet)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    shards: list[dict[str, Any]] = []
    for index, start in enumerate(range(0, len(lines), args.rows_per_shard), start=1):
        shard_lines = lines[start : start + args.rows_per_shard]
        shard_path = args.out_dir / f"{args.prefix}.shard{index:03d}.jsonl"
        with shard_path.open("w", encoding="utf-8") as f:
            f.writelines(shard_lines)
        shards.append(
            {
                "index": index,
                "path": str(shard_path),
                "rows": len(shard_lines),
                "start_row_0based": start,
                "end_row_exclusive_0based": start + len(shard_lines),
            }
        )
    summary = {
        "packet": str(args.packet),
        "rows": len(lines),
        "rows_per_shard": args.rows_per_shard,
        "num_shards": len(shards),
        "shards": shards,
    }
    write_json(args.out_dir / "shards_summary.json", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--rows-per-shard", type=int, default=450)
    parser.add_argument("--prefix", default="packet")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = split(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
