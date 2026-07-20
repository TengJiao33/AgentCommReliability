#!/usr/bin/env python3
"""Merge independent question-token anchored delta row shards."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from run_basic_mad import load_rows, resolve_inside
from run_mca_natural_search_delta import _condition_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--base-run-id", required=True)
    parser.add_argument("--shard-count", type=int, required=True)
    parser.add_argument("--expected-rows", type=int, default=0)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def _interleave_shard_records(shards: list[list[dict[str, Any]]]) -> list[tuple[int, dict[str, Any]]]:
    merged: list[tuple[int, dict[str, Any]]] = []
    max_rows = max((len(records) for records in shards), default=0)
    for row_offset in range(max_rows):
        for shard_index, records in enumerate(shards):
            if row_offset < len(records):
                merged.append((shard_index, records[row_offset]))
    return merged


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_records(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"invalid JSON in {path}:{line_number}: {exc}") from exc
    return records


def main() -> int:
    args = parse_args()
    if args.shard_count < 1:
        raise SystemExit("--shard-count must be >= 1")

    work_dir = Path(args.work_dir).expanduser().resolve()
    experiments_dir = resolve_inside(work_dir / "experiments", work_dir, "experiments dir")
    summaries: list[dict[str, Any]] = []
    records_by_shard: list[list[dict[str, Any]]] = []
    experiment_name: str | None = None

    for shard_index in range(args.shard_count):
        shard_label = f"{shard_index:02d}-of-{args.shard_count:02d}"
        shard_run_id = f"{args.base_run_id}-shard{shard_label}"
        shard_dir = resolve_inside(experiments_dir / shard_run_id, work_dir, "shard dir")
        candidates = [path.parent for path in shard_dir.glob("*/summary.json")]
        if len(candidates) != 1:
            raise SystemExit(f"expected one completed result directory in {shard_dir}, found {len(candidates)}")
        result_dir = candidates[0]
        if experiment_name is None:
            experiment_name = result_dir.name
        elif result_dir.name != experiment_name:
            raise SystemExit(f"experiment directory mismatch: {result_dir.name} != {experiment_name}")

        summary = _load_json(result_dir / "summary.json")
        records = _load_records(result_dir / "records.jsonl")
        if summary.get("run_id") != shard_run_id:
            raise SystemExit(f"run id mismatch in shard {shard_index}")
        if summary.get("shard_count") != args.shard_count or summary.get("shard_index") != shard_index:
            raise SystemExit(f"shard metadata mismatch in shard {shard_index}")
        if summary.get("rows") != len(records):
            raise SystemExit(f"row count mismatch in shard {shard_index}")
        summaries.append(summary)
        records_by_shard.append(records)

    assert experiment_name is not None
    comparable_keys = (
        "model_key",
        "model_path",
        "benchmark",
        "split",
        "agents",
        "layers",
        "conditions",
        "span_tokens",
        "max_payloads",
        "max_question_anchors",
        "attribution_method",
        "steering_scale",
        "message_max_norm",
        "temperature",
        "top_p",
        "max_new_tokens",
        "max_model_len",
        "state_source",
        "anchor_source",
        "sender_prompt_intervention",
        "receiver_prompt_intervention",
        "uses_peer_past_key_values",
    )
    reference = summaries[0]
    for shard_index, summary in enumerate(summaries[1:], start=1):
        for key in comparable_keys:
            if summary.get(key) != reference.get(key):
                raise SystemExit(f"{key} mismatch in shard {shard_index}")

    interleaved = _interleave_shard_records(records_by_shard)
    if args.expected_rows and len(interleaved) != args.expected_rows:
        raise SystemExit(f"expected {args.expected_rows} rows, found {len(interleaved)}")
    identities = [record.get("id") or f"index:{record.get('index')}" for _, record in interleaved]
    if len(set(identities)) != len(identities):
        raise SystemExit("duplicate record identities found across shards")

    data_path = resolve_inside(
        work_dir / "data" / "benchmarks" / reference["benchmark"] / reference["split"] / "canonical.jsonl",
        work_dir,
        "benchmark path",
    )
    source_rows = load_rows(data_path, len(interleaved))
    source_identities = [row.get("id") or f"index:{row.get('index')}" for row in source_rows]
    if identities != source_identities:
        raise SystemExit("merged record order does not match the source benchmark")

    output_dir = resolve_inside(experiments_dir / args.base_run_id / experiment_name, work_dir, "merged output dir")
    if output_dir.exists() and any(output_dir.iterdir()):
        existing_names = {path.name for path in output_dir.iterdir()}
        expected_names = {"records.jsonl", "summary.json", "summary.md"}
        if not args.overwrite or not existing_names.issubset(expected_names):
            raise SystemExit(f"merged output directory is not safely overwritable: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    records_path = output_dir / "records.jsonl"
    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for shard_index, record in interleaved:
            record["source_run_id"] = record.get("run_id")
            record["source_shard_index"] = shard_index
            record["run_id"] = args.base_run_id
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    counts: Counter[str] = Counter()
    for summary in summaries:
        counts.update({key: int(value) for key, value in summary["counts"].items()})
    total = counts["total"]
    conditions = reference["conditions"]
    metrics = {
        "baseline_accuracy": counts["baseline_correct"] / max(1, total),
        "baseline_majority_tie_rate": counts["baseline_majority_tie"] / max(1, total),
        "conditions": {condition: _condition_metrics(counts, condition) for condition in conditions},
    }
    elapsed_values = [float(summary["elapsed_seconds"]) for summary in summaries]
    peak_values = [float(summary["peak_cuda_memory_gib"]) for summary in summaries]
    merged_summary = {
        **{key: reference[key] for key in comparable_keys},
        "run_id": args.base_run_id,
        "rows": total,
        "shard_count": args.shard_count,
        "shard_index": None,
        "merged_shards": args.shard_count,
        "counts": dict(counts),
        "metrics": metrics,
        "elapsed_seconds": max(elapsed_values),
        "elapsed_seconds_max_shard": max(elapsed_values),
        "elapsed_seconds_sum_shards": sum(elapsed_values),
        "peak_cuda_memory_gib": max(peak_values),
        "records_path": str(records_path),
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(merged_summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"# {experiment_name}\n\n")
        handle.write(f"- Rows: {total}\n")
        handle.write(f"- Merged shards: {args.shard_count}\n")
        handle.write(f"- Baseline accuracy: {metrics['baseline_accuracy']:.4f}\n")
        for condition in conditions:
            item = metrics["conditions"][condition]
            handle.write(
                f"- {condition}: accuracy={item['accuracy']:.4f}, delta={item['delta_vs_baseline']:+d}, "
                f"recovery={item['recovery_rate']:.4f}, harm={item['harm_rate']:.4f}, "
                f"change={item['answer_change_rate']:.4f}\n"
            )
        handle.write(f"- Slowest shard seconds: {max(elapsed_values):.1f}\n")
        handle.write(f"- Sum of shard seconds: {sum(elapsed_values):.1f}\n")
        handle.write(f"- Peak CUDA memory GiB: {max(peak_values):.2f}\n")

    print(json.dumps(merged_summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
