#!/usr/bin/env python3
"""Prepare benchmark snapshots for reproducible remote evaluation.

The script downloads benchmark datasets through Hugging Face Datasets and writes
both raw and lightly-normalized JSONL files under a project-local data folder.
All cache and output paths are constrained to the configured work directory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class DatasetCandidate:
    repo_id: str
    config: str | None = None


@dataclass(frozen=True)
class BenchmarkSpec:
    key: str
    display_name: str
    candidates: tuple[DatasetCandidate, ...]
    expected_min_rows: int | None = None
    expected_exact_rows: int | None = None


BENCHMARKS: dict[str, BenchmarkSpec] = {
    "mmlu_pro": BenchmarkSpec(
        key="mmlu_pro",
        display_name="MMLU-Pro",
        candidates=(DatasetCandidate("TIGER-Lab/MMLU-Pro"),),
        expected_min_rows=12000,
    ),
    "gsm8k": BenchmarkSpec(
        key="gsm8k",
        display_name="GSM8K",
        candidates=(DatasetCandidate("openai/gsm8k", "main"),),
        expected_exact_rows=8792,
    ),
    "math500": BenchmarkSpec(
        key="math500",
        display_name="MATH-500",
        candidates=(DatasetCandidate("HuggingFaceH4/MATH-500"),),
        expected_exact_rows=500,
    ),
    "aime24": BenchmarkSpec(
        key="aime24",
        display_name="AIME 2024",
        candidates=(
            DatasetCandidate("HuggingFaceH4/aime_2024"),
            DatasetCandidate("math-ai/aime24"),
            DatasetCandidate("MathArena/aime_2024"),
        ),
        expected_exact_rows=30,
    ),
    "aime25": BenchmarkSpec(
        key="aime25",
        display_name="AIME 2025",
        candidates=(
            DatasetCandidate("math-ai/aime25"),
            DatasetCandidate("MathArena/aime_2025"),
            DatasetCandidate("opencompass/AIME2025"),
            DatasetCandidate("yentinglin/aime_2025"),
        ),
        expected_exact_rows=30,
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work-dir",
        default=os.environ.get("ACR_WORK_DIR", os.getcwd()),
        help="Project work directory. Output and caches must stay inside it.",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Benchmark output directory. Defaults to <work-dir>/data/benchmarks.",
    )
    parser.add_argument(
        "--hf-home",
        default=None,
        help="Hugging Face cache root. Defaults to <work-dir>/hf_home.",
    )
    parser.add_argument(
        "--benchmarks",
        nargs="+",
        default=sorted(BENCHMARKS),
        choices=sorted(BENCHMARKS),
        help="Benchmark keys to prepare.",
    )
    parser.add_argument(
        "--local-dataset",
        action="append",
        default=[],
        metavar="KEY=PATH",
        help=(
            "Load a benchmark from a local dataset repo/path instead of the "
            "configured online candidates. Can be repeated."
        ),
    )
    parser.add_argument(
        "--local-dataset-source",
        action="append",
        default=[],
        metavar="KEY=SOURCE",
        help="Record SOURCE in manifests for a local dataset override.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when row counts do not match the known benchmark size checks.",
    )
    return parser.parse_args()


def parse_local_overrides(items: Iterable[str], work_dir: Path) -> dict[str, Path]:
    overrides: dict[str, Path] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"--local-dataset must be KEY=PATH, got: {item}")
        key, raw_path = item.split("=", 1)
        if key not in BENCHMARKS:
            raise SystemExit(f"Unknown local dataset key: {key}")
        path = Path(raw_path).expanduser().resolve()
        if not path.exists():
            raise SystemExit(f"Local dataset path does not exist: {path}")
        overrides[key] = path
    return overrides


def parse_local_sources(items: Iterable[str]) -> dict[str, str]:
    sources: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise SystemExit(f"--local-dataset-source must be KEY=SOURCE, got: {item}")
        key, source = item.split("=", 1)
        if key not in BENCHMARKS:
            raise SystemExit(f"Unknown local dataset source key: {key}")
        sources[key] = source
    return sources


def resolve_inside(path: str | Path, work_dir: Path, label: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    try:
        resolved.relative_to(work_dir)
    except ValueError as exc:
        raise SystemExit(f"{label} must stay inside work-dir: {resolved}") from exc
    return resolved


def configure_hf_cache(work_dir: Path, hf_home_arg: str | None) -> Path:
    hf_home = resolve_inside(hf_home_arg or work_dir / "hf_home", work_dir, "hf-home")
    hf_home.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(hf_home)
    os.environ["HF_DATASETS_CACHE"] = str(hf_home / "datasets")
    os.environ["HF_HUB_CACHE"] = str(hf_home / "hub")
    os.environ["TRANSFORMERS_CACHE"] = str(hf_home / "transformers")
    return hf_home


def import_datasets() -> Any:
    try:
        from datasets import DatasetDict, load_dataset
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency 'datasets'. Install it in a project-local env, "
            "for example: python -m pip install datasets pyarrow huggingface_hub"
        ) from exc
    return DatasetDict, load_dataset


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def first_present(record: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in record and record[key] is not None:
            return record[key]
    return None


def normalize_choices(value: Any) -> list[Any] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, dict):
        return [value[k] for k in sorted(value)]
    return None


def extract_gsm8k_answer(answer: Any) -> tuple[str | None, str | None]:
    if not isinstance(answer, str):
        return None, None
    match = re.search(r"####\s*(.+?)\s*$", answer, flags=re.DOTALL)
    if not match:
        return None, answer
    return match.group(1).strip(), answer


def normalize_record(
    benchmark: str,
    source_repo: str,
    source_config: str | None,
    split: str,
    index: int,
    record: dict[str, Any],
) -> dict[str, Any]:
    raw = json_ready(record)
    raw_id = first_present(raw, ("id", "question_id", "unique_id", "problem_id", "problem_idx"))
    question = first_present(raw, ("question", "problem", "prompt", "input"))
    choices = normalize_choices(first_present(raw, ("options", "choices", "choice", "multiple_choice_targets")))
    answer = first_present(raw, ("answer", "final_answer", "target", "label", "gold"))
    answer_index = first_present(raw, ("answer_index", "label_index", "correct_index"))
    solution = first_present(raw, ("solution", "rationale", "explanation"))

    if benchmark == "gsm8k":
        final_answer, solution_text = extract_gsm8k_answer(answer)
        if final_answer is not None:
            answer = final_answer
            solution = solution_text

    return {
        "id": str(raw_id) if raw_id is not None else f"{benchmark}:{split}:{index}",
        "benchmark": benchmark,
        "source_dataset": source_repo,
        "source_config": source_config,
        "split": split,
        "index": index,
        "question": question,
        "choices": choices,
        "answer": answer,
        "answer_index": answer_index,
        "subject": first_present(raw, ("subject", "category", "domain")),
        "level": first_present(raw, ("level", "difficulty")),
        "solution": solution,
        "metadata": {
            "source_id": raw_id,
            "columns": sorted(raw.keys()),
        },
        "raw": raw,
    }


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(json_ready(row), ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            count += 1
    return count


def load_first_available(
    load_dataset: Any,
    spec: BenchmarkSpec,
    local_overrides: dict[str, Path],
    local_sources: dict[str, str],
) -> tuple[DatasetCandidate, Any]:
    if spec.key in local_overrides:
        path = local_overrides[spec.key]
        source = local_sources.get(spec.key, f"local:{path.name}")
        return DatasetCandidate(source), load_dataset(str(path))

    errors: list[str] = []
    for candidate in spec.candidates:
        try:
            if candidate.config:
                dataset = load_dataset(candidate.repo_id, candidate.config)
            else:
                dataset = load_dataset(candidate.repo_id)
            return candidate, dataset
        except Exception as exc:
            errors.append(f"{candidate.repo_id}: {exc}")
    joined = "\n  - ".join(errors)
    raise RuntimeError(f"All candidates failed for {spec.key}:\n  - {joined}")


def iter_splits(dataset_dict_cls: Any, dataset: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(dataset, dataset_dict_cls):
        for split, data in dataset.items():
            yield split, data
    else:
        yield "default", dataset


def prepare_one(
    load_dataset: Any,
    dataset_dict_cls: Any,
    spec: BenchmarkSpec,
    data_dir: Path,
    strict: bool,
    local_overrides: dict[str, Path],
    local_sources: dict[str, str],
) -> dict[str, Any]:
    candidate, dataset = load_first_available(load_dataset, spec, local_overrides, local_sources)
    bench_dir = data_dir / spec.key
    if bench_dir.exists():
        try:
            bench_dir.resolve().relative_to(data_dir.resolve())
        except ValueError as exc:
            raise RuntimeError(f"Refusing to remove output outside data dir: {bench_dir}") from exc
        shutil.rmtree(bench_dir)
    bench_dir.mkdir(parents=True, exist_ok=True)

    split_entries: list[dict[str, Any]] = []
    total_rows = 0
    for split, split_data in iter_splits(dataset_dict_cls, dataset):
        split_dir = bench_dir / split
        split_dir.mkdir(parents=True, exist_ok=True)

        raw_rows = [json_ready(row) for row in split_data]
        canonical_rows = [
            normalize_record(spec.key, candidate.repo_id, candidate.config, split, idx, row)
            for idx, row in enumerate(raw_rows)
        ]
        raw_path = split_dir / "raw.jsonl"
        canonical_path = split_dir / "canonical.jsonl"
        row_count = write_jsonl(raw_path, raw_rows)
        canonical_count = write_jsonl(canonical_path, canonical_rows)
        if row_count != canonical_count:
            raise RuntimeError(f"Raw/canonical count mismatch for {spec.key}:{split}")

        total_rows += row_count
        split_entries.append(
            {
                "split": split,
                "rows": row_count,
                "columns": list(split_data.column_names),
                "raw_jsonl": str(raw_path.relative_to(data_dir)),
                "canonical_jsonl": str(canonical_path.relative_to(data_dir)),
            }
        )

    status = "ok"
    warnings: list[str] = []
    if spec.expected_exact_rows is not None and total_rows != spec.expected_exact_rows:
        status = "warning"
        warnings.append(f"expected exactly {spec.expected_exact_rows} rows, got {total_rows}")
    if spec.expected_min_rows is not None and total_rows < spec.expected_min_rows:
        status = "warning"
        warnings.append(f"expected at least {spec.expected_min_rows} rows, got {total_rows}")
    if strict and warnings:
        raise RuntimeError(f"{spec.key} failed size check: {'; '.join(warnings)}")

    manifest = {
        "benchmark": spec.key,
        "display_name": spec.display_name,
        "status": status,
        "warnings": warnings,
        "source_dataset": candidate.repo_id,
        "source_config": candidate.config,
        "total_rows": total_rows,
        "splits": split_entries,
    }
    with (bench_dir / "manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return manifest


def main() -> int:
    args = parse_args()
    work_dir = Path(args.work_dir).expanduser().resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    data_dir = resolve_inside(args.data_dir or work_dir / "data" / "benchmarks", work_dir, "data-dir")
    data_dir.mkdir(parents=True, exist_ok=True)
    hf_home = configure_hf_cache(work_dir, args.hf_home)
    local_overrides = parse_local_overrides(args.local_dataset, work_dir)
    local_sources = parse_local_sources(args.local_dataset_source)
    dataset_dict_cls, load_dataset = import_datasets()

    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    manifests = []
    failures = []
    for key in args.benchmarks:
        spec = BENCHMARKS[key]
        print(f"[prepare] {spec.display_name} ({key})", flush=True)
        try:
            manifest = prepare_one(
                load_dataset,
                dataset_dict_cls,
                spec,
                data_dir,
                args.strict,
                local_overrides,
                local_sources,
            )
            manifests.append(manifest)
            print(
                f"[ok] {key}: {manifest['total_rows']} rows from {manifest['source_dataset']}",
                flush=True,
            )
            for warning in manifest["warnings"]:
                print(f"[warning] {key}: {warning}", file=sys.stderr, flush=True)
        except Exception as exc:
            failures.append({"benchmark": key, "error": str(exc)})
            print(f"[failed] {key}: {exc}", file=sys.stderr, flush=True)

    global_manifest = {
        "created_at_utc": started_at,
        "work_dir": str(work_dir),
        "data_dir": str(data_dir),
        "hf_home": str(hf_home),
        "benchmarks": manifests,
        "failures": failures,
    }
    with (data_dir / "manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(global_manifest, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    if failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
