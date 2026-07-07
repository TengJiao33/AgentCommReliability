"""Build MCA diagnostic benchmark packets from archived run records."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from run_basic_mad import is_correct, resolve_inside


DEFAULT_STANDARD_RECORDS = (
    "experiments/standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/"
    "math500-qwen25-7b-instruct-naive/records.jsonl"
)
DEFAULT_PREP_RUN_ID = "20260707-mca-packet-matrix-prep"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default=os.environ.get("ACR_WORK_DIR", os.getcwd()))
    parser.add_argument("--benchmark", default="math500")
    parser.add_argument("--standard-records", default=DEFAULT_STANDARD_RECORDS)
    parser.add_argument("--label-free-split", default="mca_disagreement_v1")
    parser.add_argument("--gold-split", default="mca_gold_contrast_v1")
    parser.add_argument("--prep-run-id", default=DEFAULT_PREP_RUN_ID)
    parser.add_argument("--limit", type=int, default=0, help="0 means all records.")
    return parser.parse_args()


def load_jsonl(path: Path, limit: int = 0) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
            if limit and len(rows) >= limit:
                break
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def first_round(record: dict[str, Any]) -> dict[str, Any]:
    rounds = record.get("mad_mm", {}).get("rounds") or []
    if not rounds:
        raise ValueError(f"record has no mad_mm rounds: {record.get('id')}")
    return rounds[0]


def agent_outputs(record: dict[str, Any]) -> list[dict[str, Any]]:
    outputs = first_round(record).get("agent_outputs") or []
    if not outputs:
        raise ValueError(f"record has no first-round agent outputs: {record.get('id')}")
    return outputs


def normalized_answers(record: dict[str, Any]) -> list[str | None]:
    answers: list[str | None] = []
    for output in agent_outputs(record):
        normalized = output.get("normalized_answer")
        answers.append(str(normalized) if normalized is not None else None)
    return answers


def nonempty_answer_counts(record: dict[str, Any]) -> Counter[str]:
    return Counter(answer for answer in normalized_answers(record) if answer)


def label_free_stratum(record: dict[str, Any]) -> str | None:
    answers = normalized_answers(record)
    counts = nonempty_answer_counts(record)
    if len(counts) < 2:
        return None
    if any(answer is None for answer in answers):
        return "parse_gap"
    if len(counts) >= 3:
        return "no_majority_conflict"
    if sorted(counts.values(), reverse=True) == [2, 1]:
        return "minority_bearing"
    return "disagreement_other"


def agent_correctness(record: dict[str, Any]) -> list[bool]:
    gold = record.get("gold_answer")
    return [bool(is_correct(output.get("parsed_answer"), gold)) for output in agent_outputs(record)]


def gold_stratum(record: dict[str, Any]) -> str | None:
    correctness = agent_correctness(record)
    correct_count = sum(correctness)
    if correct_count == 0 or correct_count == len(correctness):
        return None

    majority_answer = first_round(record).get("majority_answer")
    majority_correct = bool(is_correct(majority_answer, record.get("gold_answer")))
    counts = nonempty_answer_counts(record)

    if len(counts) >= 3:
        return "no_majority_mixed"
    if majority_correct:
        return "majority_correct_minority_wrong"
    if correct_count >= 1:
        return "majority_wrong_minority_correct"
    return "mixed_other"


def packet_row(record: dict[str, Any], *, split: str, packet_type: str, stratum: str) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "benchmark": record.get("benchmark"),
        "split": split,
        "index": record.get("index"),
        "question": record.get("question"),
        "answer": record.get("gold_answer"),
        "answer_index": None,
        "metadata": {
            "source_record_id": record.get("id"),
            "source_record_index": record.get("index"),
            "source_split": record.get("split"),
            "packet_type": packet_type,
            "packet_stratum": stratum,
            "standard_mad_initial_majority_answer": first_round(record).get("majority_answer"),
            "standard_mad_initial_majority_tie": first_round(record).get("majority_tie"),
            "standard_mad_initial_unique_answers": sorted(nonempty_answer_counts(record).keys()),
        },
    }


def build_packet(records: list[dict[str, Any]], *, split: str, packet_type: str) -> tuple[list[dict[str, Any]], Counter[str]]:
    rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    selector = label_free_stratum if packet_type == "label_free_disagreement" else gold_stratum

    for record in records:
        counts["source_records"] += 1
        stratum = selector(record)
        if stratum is None:
            counts["dropped"] += 1
            continue
        counts[stratum] += 1
        rows.append(packet_row(record, split=split, packet_type=packet_type, stratum=stratum))

    counts["selected"] = len(rows)
    return rows, counts


def packet_manifest(
    *,
    split: str,
    packet_type: str,
    benchmark: str,
    records_path: Path,
    rows: list[dict[str, Any]],
    counts: Counter[str],
) -> dict[str, Any]:
    return {
        "benchmark": benchmark,
        "split": split,
        "packet_type": packet_type,
        "source_records": str(records_path),
        "rows": len(rows),
        "counts": dict(counts),
        "selection_uses_gold": packet_type != "label_free_disagreement",
        "selection_uses_mca_outputs": False,
        "row_key": ["id", "index"],
        "canonical_jsonl": f"data/benchmarks/{benchmark}/{split}/canonical.jsonl",
    }


def write_packet_readme(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        f"# {manifest['benchmark']} {manifest['split']}",
        "",
        f"- Packet type: `{manifest['packet_type']}`",
        f"- Rows: {manifest['rows']}",
        f"- Source records: `{manifest['source_records']}`",
        f"- Selection uses gold: `{str(manifest['selection_uses_gold']).lower()}`",
        f"- Selection uses MCA outputs: `{str(manifest['selection_uses_mca_outputs']).lower()}`",
        "",
        "## Counts",
        "",
    ]
    for key, value in sorted(manifest["counts"].items()):
        lines.append(f"- `{key}`: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_prep_summary(path: Path, manifests: list[dict[str, Any]]) -> None:
    lines = [
        "# MCA packet matrix prep",
        "",
        "This prep run materializes benchmark splits for the next MCA matrix diagnostics.",
        "",
    ]
    for manifest in manifests:
        lines.extend(
            [
                f"## {manifest['split']}",
                "",
                f"- Type: `{manifest['packet_type']}`",
                f"- Rows: {manifest['rows']}",
                f"- Selection uses gold: `{str(manifest['selection_uses_gold']).lower()}`",
                "- Counts:",
            ]
        )
        for key, value in sorted(manifest["counts"].items()):
            lines.append(f"  - `{key}`: {value}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    work_dir = Path(args.work_dir).resolve()
    records_path = resolve_inside(Path(args.standard_records), work_dir, "standard records")
    records = load_jsonl(records_path, args.limit)

    packet_specs = [
        (args.label_free_split, "label_free_disagreement"),
        (args.gold_split, "gold_stratified_diagnostic"),
    ]

    manifests: list[dict[str, Any]] = []
    for split, packet_type in packet_specs:
        rows, counts = build_packet(records, split=split, packet_type=packet_type)
        packet_dir = resolve_inside(work_dir / "data" / "benchmarks" / args.benchmark / split, work_dir, "packet dir")
        write_jsonl(packet_dir / "canonical.jsonl", rows)
        manifest = packet_manifest(
            split=split,
            packet_type=packet_type,
            benchmark=args.benchmark,
            records_path=records_path,
            rows=rows,
            counts=counts,
        )
        write_json(packet_dir / "manifest.json", manifest)
        write_packet_readme(packet_dir / "README.md", manifest)
        manifests.append(manifest)

    prep_dir = resolve_inside(work_dir / "experiments" / args.prep_run_id, work_dir, "prep dir")
    write_json(
        prep_dir / "manifest.json",
        {
            "run_id": args.prep_run_id,
            "benchmark": args.benchmark,
            "source_records": str(records_path),
            "packets": manifests,
        },
    )
    write_prep_summary(prep_dir / "summary.md", manifests)
    print(json.dumps({"packets": manifests}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

