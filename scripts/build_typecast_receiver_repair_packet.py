#!/usr/bin/env python3
"""Build a repaired TypeCastArena receiver packet from a diagnosed run.

The first 315-row inert-control receiver run showed that the packet did not
pass the control gate: too many rows were not receiver-baseline-stable, and
many outputs missed the final-answer contract. This script keeps the original
communication contrasts but filters to cases that were correct under required
control variants, then strengthens the final-answer instruction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_PACKET = Path(
    "experiments/20260617-local-typecast-arena-math200-rawgold-candidatewrong-inert-receiver-packet/typecast_math_receiver_packet.jsonl"
)
DEFAULT_EVALUATION = Path(
    "experiments/20260617-0033-a8002-typecast-math200-inert-receiver315-qwen25-14b/evaluation/evaluated_rows.jsonl"
)
DEFAULT_OUT_DIR = Path("experiments/20260617-local-typecast-arena-math200-repaired-controlstable-receiver-packet")
DEFAULT_REQUIRED_VARIANTS = [
    "baseline_previous_solution",
    "control_self_revision_no_sender",
    "control_unrelated_sender_message",
]
PACKET_NAME = "typecast_math_receiver_packet.jsonl"


FINAL_CONTRACT = """Output contract:
- Write concise reasoning.
- The final line is mandatory.
- The final line must be exactly this schema, with no text after it:
{final answer: <answer>}
- Put units, ordered pairs, sets, radicals, or text labels inside <answer>."""


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def by_case_variant(rows: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, Mapping[str, Any]]]:
    out: dict[str, dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in rows:
        out[str(row.get("case_id"))][str(row.get("variant"))] = row
    return dict(out)


def select_cases(
    evaluated_rows: list[Mapping[str, Any]],
    required_variants: list[str],
) -> tuple[list[str], list[dict[str, Any]]]:
    cases = by_case_variant(evaluated_rows)
    selected: list[str] = []
    excluded: list[dict[str, Any]] = []
    for case_id, variants in sorted(cases.items()):
        failed: list[dict[str, Any]] = []
        for variant in required_variants:
            row = variants.get(variant)
            if row is None:
                failed.append({"variant": variant, "reason": "missing_evaluation_row"})
            elif row.get("semantic_correct") is not True:
                failed.append(
                    {
                        "variant": variant,
                        "reason": "not_semantic_correct",
                        "semantic_correct": row.get("semantic_correct"),
                        "semantic_status": row.get("semantic_status"),
                        "prediction_answer": row.get("prediction_answer"),
                        "gold_answer": row.get("gold_answer"),
                    }
                )
        if failed:
            excluded.append({"case_id": case_id, "failed_requirements": failed})
        else:
            selected.append(case_id)
    return selected, excluded


def strengthen_final_contract(prompt: str) -> str:
    pattern = re.compile(
        r"Give concise reasoning, then end with exactly one line:\s*\n\{final answer: <answer>\}\s*$",
        flags=re.MULTILINE,
    )
    if pattern.search(prompt):
        return pattern.sub(FINAL_CONTRACT, prompt)
    return prompt.rstrip() + "\n\n" + FINAL_CONTRACT


def repair_row(row: Mapping[str, Any], *, args: argparse.Namespace) -> dict[str, Any]:
    repaired = dict(row)
    original_packet_id = str(row.get("packet_id"))
    repaired["original_packet_id"] = original_packet_id
    repaired["packet_id"] = f"{original_packet_id}::repair::{args.repair_tag}"
    if args.strict_final_answer_contract:
        repaired["prompt"] = strengthen_final_contract(str(row.get("prompt") or ""))
    repaired["prompt_sha1"] = sha1_text(str(repaired.get("prompt") or ""))
    repair_meta = {
        "schema_version": "acr.typecast_receiver_repair.v0.1",
        "repair_tag": args.repair_tag,
        "source_packet": str(args.packet),
        "source_evaluation": str(args.evaluation),
        "required_correct_variants": args.required_variants,
        "strict_final_answer_contract": bool(args.strict_final_answer_contract),
        "original_packet_id": original_packet_id,
    }
    repaired["typecast_receiver_repair"] = repair_meta
    for key in ("typecast_arena", "sender_receiver", "type_erasure"):
        meta = dict(repaired.get(key) or {})
        meta["receiver_repair_tag"] = args.repair_tag
        meta["strict_final_answer_contract"] = bool(args.strict_final_answer_contract)
        repaired[key] = meta
    genesis = dict(repaired.get("math_authority_genesis") or {})
    genesis["receiver_repair"] = repair_meta
    repaired["math_authority_genesis"] = genesis
    return repaired


def summarize_packet(rows: list[Mapping[str, Any]], selected_cases: list[str], excluded: list[Mapping[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    metas = [row.get("typecast_arena") or {} for row in rows]
    return {
        "packet_rows": len(rows),
        "selected_cases": len(selected_cases),
        "selected_case_ids": selected_cases,
        "excluded_cases": len(excluded),
        "required_correct_variants": args.required_variants,
        "strict_final_answer_contract": bool(args.strict_final_answer_contract),
        "repair_tag": args.repair_tag,
        "rows_by_variant": dict(sorted(Counter(str(row.get("variant")) for row in rows).items())),
        "rows_by_channel_condition": dict(sorted(Counter(str(meta.get("channel_condition")) for meta in metas).items())),
        "rows_by_future_signal": dict(sorted(Counter(str((row.get("math_authority_genesis") or {}).get("future_signal")) for row in rows).items())),
        "rows_by_candidate_visibility": dict(sorted(Counter(str(meta.get("candidate_visibility")) for meta in metas).items())),
        "source_paths": {
            "packet": str(args.packet),
            "evaluation": str(args.evaluation),
        },
        "outputs": {
            "packet": str(args.out_dir / PACKET_NAME),
            "summary": str(args.out_dir / "summary.json"),
            "selected_cases": str(args.out_dir / "selected_cases.jsonl"),
            "excluded_cases": str(args.out_dir / "excluded_cases.jsonl"),
            "README": str(args.out_dir / "README.md"),
            "scoring_plan": str(args.out_dir / "scoring_plan.md"),
        },
    }


def render_readme(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# TypeCastArena Repaired Receiver Packet",
            "",
            "This packet is derived from the 315-row inert-control receiver run after it failed the control gate.",
            "It keeps the same communication contrasts but filters to receiver-control-stable cases and strengthens the final-answer contract.",
            "",
            "## Shape",
            "",
            f"- Repair tag: `{summary['repair_tag']}`",
            f"- Selected cases: `{summary['selected_cases']}`",
            f"- Excluded cases: `{summary['excluded_cases']}`",
            f"- Receiver prompt rows: `{summary['packet_rows']}`",
            f"- Required correct variants: `{summary['required_correct_variants']}`",
            f"- Strict final-answer contract: `{summary['strict_final_answer_contract']}`",
            f"- Rows by channel condition: `{summary['rows_by_channel_condition']}`",
            f"- Rows by candidate visibility: `{summary['rows_by_candidate_visibility']}`",
            "",
            "## Purpose",
            "",
            "The next GPU run should answer a narrower diagnostic question: after receiver baseline, self-revision, and unrelated-message controls are already correct, do admitted/verifier channels separate from inert, quarantine, and typed-rederive controls?",
            "",
            "## Gate",
            "",
            "- This packet is still setup evidence until a model run is completed.",
            "- A future run is not claim-bearing if inert, unrelated, quarantine, or typed-rederive controls fail at rates comparable to admitted/verifier channels.",
            "- If the strict final-answer contract still yields many missing-answer rows, repair the prompt before running a larger packet.",
            "",
        ]
    )


def render_scoring_plan(summary: Mapping[str, Any]) -> str:
    packet = summary["outputs"]["packet"]
    return "\n".join(
        [
            "# TypeCastArena Repaired Packet Scoring Plan",
            "",
            "Run outputs with the TypeCastArena A800_2 runner, then score with:",
            "",
            "```bash",
            "python scripts/evaluate_math_authority_genesis_ladder.py \\",
            f"  --packet {packet} \\",
            "  --outputs <run-dir>/outputs.jsonl \\",
            "  --prediction-source outputs \\",
            "  --out-dir <run-dir>/evaluation",
            "",
            "python scripts/analyze_typecast_boundary_obedience.py \\",
            f"  --packet {packet} \\",
            "  --run-dir <run-dir>/evaluation \\",
            "  --out-dir <run-dir>/boundary_obedience",
            "```",
            "",
            "Primary gate:",
            "",
            "- baseline, self-revision, and unrelated controls should stay clean;",
            "- inert visible scratch should not behave like peer/shared/verifier channels;",
            "- quarantine and typed-rederive rows should not show hidden/removed candidate uptake.",
            "",
        ]
    )


def build(args: argparse.Namespace) -> dict[str, Any]:
    packet = load_jsonl(args.packet)
    evaluated = load_jsonl(args.evaluation)
    selected_cases, excluded = select_cases(evaluated, args.required_variants)
    if args.max_cases:
        selected_cases = selected_cases[: args.max_cases]
    selected_set = set(selected_cases)
    rows = [repair_row(row, args=args) for row in packet if str(row.get("case_id")) in selected_set]
    summary = summarize_packet(rows, selected_cases, excluded, args)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / PACKET_NAME, rows)
    write_jsonl(args.out_dir / "selected_cases.jsonl", ({"case_id": case_id} for case_id in selected_cases))
    write_jsonl(args.out_dir / "excluded_cases.jsonl", excluded)
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "README.md", render_readme(summary))
    write_text(args.out_dir / "scoring_plan.md", render_scoring_plan(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--evaluation", type=Path, default=DEFAULT_EVALUATION)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--required-variants", nargs="+", default=DEFAULT_REQUIRED_VARIANTS)
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--repair-tag", default="controlstable_v1")
    parser.add_argument("--strict-final-answer-contract", action="store_true", default=True)
    parser.add_argument("--no-strict-final-answer-contract", dest="strict_final_answer_contract", action="store_false")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
