#!/usr/bin/env python3
"""CPU-only loader smoke for the RuleArena submodule.

This script intentionally does not import RuleArena's model clients or call any
LLM API. It only verifies that the benchmark data files are present and readable.
"""

import argparse
import json
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def summarize_airline(root: Path) -> list[dict]:
    rows = []
    for path in sorted((root / "airline" / "synthesized_problems").glob("comp_*.jsonl")):
        data = read_jsonl(path)
        first = data[0] if data else {}
        rows.append(
            {
                "domain": "airline",
                "file": str(path.relative_to(root)),
                "count": len(data),
                "sample_keys": sorted(first.keys()),
            }
        )
    return rows


def summarize_nba(root: Path) -> list[dict]:
    rows = []
    for path in sorted((root / "nba" / "annotated_problems").glob("comp_*.json")):
        data = read_json(path)
        first = data[0] if isinstance(data, list) and data else {}
        rows.append(
            {
                "domain": "nba",
                "file": str(path.relative_to(root)),
                "count": len(data) if isinstance(data, list) else None,
                "sample_keys": sorted(first.keys()) if isinstance(first, dict) else [],
            }
        )
    return rows


def summarize_tax(root: Path) -> list[dict]:
    rows = []
    for path in sorted((root / "tax" / "synthesized_problems").glob("comp_*.json")):
        data = read_json(path)
        first = data[0] if isinstance(data, list) and data else {}
        rows.append(
            {
                "domain": "tax",
                "file": str(path.relative_to(root)),
                "count": len(data) if isinstance(data, list) else None,
                "sample_keys": sorted(first.keys()) if isinstance(first, dict) else [],
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("baselines/RuleArena/upstream"))
    args = parser.parse_args()

    root = args.root.resolve()
    required = [root / "README.md", root / "airline", root / "nba", root / "tax"]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing RuleArena files: " + ", ".join(missing))

    summaries = []
    summaries.extend(summarize_airline(root))
    summaries.extend(summarize_nba(root))
    summaries.extend(summarize_tax(root))

    print(json.dumps({"root": str(root), "files": summaries}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
