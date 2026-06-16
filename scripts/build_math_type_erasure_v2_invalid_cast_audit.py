#!/usr/bin/env python3
"""Build invalid-cast taxonomy cards for the MATH type-erasure v2 run.

The existing evaluator marks base-correct rows that become semantically wrong
as authority violations. This audit adds a narrower seed taxonomy so downstream
sender-receiver packets do not conflate inherited operator state, local
re-solve errors, answer-copy, and final-line glitches.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_RUN_DIR = Path("experiments/20260616-1200-a8002-math-type-erasure-v2-qwen25-14b-full222")
DEFAULT_PACKET = Path(
    "experiments/20260616-local-math-epistemic-type-erasure-v2-packet/math_epistemic_type_erasure_v2_packet.jsonl"
)
DEFAULT_OUT_DIR = Path("experiments/20260616-local-math-type-erasure-v2-invalid-cast-audit")
BASE_VARIANT = "baseline_previous_solution"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def row_key(row: Mapping[str, Any]) -> tuple[str, str]:
    return (str(row.get("case_id")), str(row.get("variant")))


def baseline_key(case_id: Any) -> tuple[str, str]:
    return (str(case_id), BASE_VARIANT)


def compact(value: Any) -> str:
    return " ".join(("" if value is None else str(value)).split())


def compact_for_literal(value: Any) -> str:
    return re.sub(r"\s+", "", "" if value is None else str(value)).lower()


def literal_visible(needle: Any, haystack: Any) -> bool:
    n = compact_for_literal(needle)
    h = compact_for_literal(haystack)
    return bool(n and h and n in h)


def type_meta(row: Mapping[str, Any]) -> dict[str, Any]:
    meta = row.get("type_erasure") or {}
    return dict(meta)


def taxonomy(delta: Mapping[str, Any], evaluated: Mapping[str, Any], packet: Mapping[str, Any]) -> dict[str, Any]:
    meta = type_meta(packet)
    artifact_type = str(delta.get("artifact_type"))
    future_signal = str(delta.get("future_signal"))
    candidate_visibility = str(meta.get("candidate_visibility"))
    prompt = packet.get("prompt")
    wrong_answer = delta.get("wrong_peer_answer")
    wrong_visible = bool(meta.get("wrong_answer_literal_in_prompt") or literal_visible(wrong_answer, prompt))
    artifact_text = (packet.get("math_authority_genesis") or {}).get("artifact_text") or evaluated.get("artifact_text")
    variant_text = compact(evaluated.get("prediction_text"))
    base = compact(delta.get("base_prediction_answer"))
    variant = compact(delta.get("variant_prediction_answer"))

    labels: list[str] = []
    invalid_cast_core = False
    direct_answer_copy = False
    local_re_solve = False
    final_line_or_collision = False

    if delta.get("wrong_answer_uptake") and wrong_visible:
        primary = "direct_visible_answer_uptake"
        direct_answer_copy = True
        labels.append("prediction_matches_visible_wrong_answer")
    elif (
        delta.get("operator_uptake_candidate")
        and future_signal == "type_erased_shared_workspace_entry"
        and artifact_type in {"wrong_equation_surface", "wrong_relation_skeleton", "wrong_numeric_role_binding"}
    ):
        primary = "inherited_operator_state"
        invalid_cast_core = True
        labels.extend(["shared_workspace_admission", "non_copy_operator_shift", f"{artifact_type}_cast"])
    elif not wrong_visible and delta.get("wrong_answer_uptake"):
        primary = "final_answer_contract_glitch_or_hidden_collision"
        final_line_or_collision = True
        labels.extend(["wrong_answer_not_visible", "prediction_matches_hidden_source_answer"])
        if variant_text and base and base in variant_text and variant != base:
            labels.append("reasoning_repeats_base_but_final_line_changes")
    elif artifact_type == "wrong_final_answer" and "candidateanswerremoved" in compact_for_literal(artifact_text):
        primary = "local_re_solve_error_after_empty_typed_artifact"
        local_re_solve = True
        labels.extend(["candidate_removed_placeholder", "no_substantive_visible_artifact"])
    elif delta.get("operator_uptake_candidate"):
        primary = "operator_candidate_needs_manual_review"
        labels.append("non_copy_wrong_shift")
    else:
        primary = "authority_violation_needs_manual_review"

    if candidate_visibility:
        labels.append(f"candidate_visibility:{candidate_visibility}")
    if future_signal:
        labels.append(f"channel:{future_signal}")
    if wrong_visible:
        labels.append("wrong_answer_literal_visible")
    else:
        labels.append("wrong_answer_literal_not_visible")

    return {
        "taxonomy_primary": primary,
        "taxonomy_labels": sorted(set(labels)),
        "invalid_cast_core": invalid_cast_core,
        "direct_visible_answer_copy": direct_answer_copy,
        "local_re_solve_error": local_re_solve,
        "final_answer_contract_or_semantic_collision": final_line_or_collision,
        "wrong_answer_literal_visible": wrong_visible,
        "candidate_visibility": candidate_visibility,
        "taxonomy_status": "deterministic seed label; inspect before citing as manual taxonomy",
    }


def make_card(
    delta: Mapping[str, Any],
    evaluated_by_key: Mapping[tuple[str, str], Mapping[str, Any]],
    packet_by_key: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    evaluated = evaluated_by_key.get(row_key(delta), {})
    packet = packet_by_key.get(row_key(delta), {})
    baseline = evaluated_by_key.get(baseline_key(delta.get("case_id")), {})
    genesis = packet.get("math_authority_genesis") or {}
    meta = type_meta(packet)
    tax = taxonomy(delta, evaluated, packet)
    return {
        "event_type": "math_type_erasure_v2_authority_violation",
        "case_id": delta.get("case_id"),
        "math_case_id": delta.get("math_case_id"),
        "variant": delta.get("variant"),
        "artifact_type": delta.get("artifact_type"),
        "source_surface": delta.get("source_surface"),
        "future_signal": delta.get("future_signal"),
        "candidate_visibility": tax["candidate_visibility"],
        "operator_family": delta.get("operator_family"),
        "gold_answer": delta.get("gold_answer"),
        "wrong_peer_answer": delta.get("wrong_peer_answer"),
        "base_prediction_answer": delta.get("base_prediction_answer"),
        "variant_prediction_answer": delta.get("variant_prediction_answer"),
        "wrong_answer_uptake": delta.get("wrong_answer_uptake"),
        "operator_uptake_candidate": delta.get("operator_uptake_candidate"),
        "artifact_text": genesis.get("artifact_text") or evaluated.get("artifact_text"),
        "visible_artifact_text": meta.get("visible_artifact_text"),
        "source_artifact_text": meta.get("source_artifact_text"),
        "question": packet.get("question"),
        "baseline_prediction_text": baseline.get("prediction_text"),
        "variant_prediction_text": evaluated.get("prediction_text"),
        "prompt": packet.get("prompt"),
        "type_erasure": meta,
        **tax,
    }


def nested_counts(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> dict[str, dict[str, int]]:
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        out[str(row.get(outer))][str(row.get(inner))] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(out.items())}


def card_summary(cards: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "records": len(cards),
        "taxonomy_primary_counts": dict(sorted(Counter(str(row.get("taxonomy_primary")) for row in cards).items())),
        "future_signal_counts": dict(sorted(Counter(str(row.get("future_signal")) for row in cards).items())),
        "artifact_type_counts": dict(sorted(Counter(str(row.get("artifact_type")) for row in cards).items())),
        "candidate_visibility_counts": dict(sorted(Counter(str(row.get("candidate_visibility")) for row in cards).items())),
        "taxonomy_by_future_signal": nested_counts(cards, "future_signal", "taxonomy_primary"),
        "taxonomy_by_artifact_type": nested_counts(cards, "artifact_type", "taxonomy_primary"),
        "invalid_cast_core_count": sum(1 for row in cards if row.get("invalid_cast_core")),
        "direct_visible_answer_copy_count": sum(1 for row in cards if row.get("direct_visible_answer_copy")),
        "local_re_solve_error_count": sum(1 for row in cards if row.get("local_re_solve_error")),
        "final_answer_contract_or_semantic_collision_count": sum(
            1 for row in cards if row.get("final_answer_contract_or_semantic_collision")
        ),
    }


def md_cell(value: Any) -> str:
    return compact(value).replace("|", "\\|")


def count_table(title: str, counts: Mapping[str, int]) -> list[str]:
    lines = [f"## {title}", "", "| Slice | Count |", "| --- | ---: |"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {md_cell(key)} | {value} |")
    lines.append("")
    return lines


def render_cards(cards: list[Mapping[str, Any]]) -> list[str]:
    lines = [
        "## Cards",
        "",
        "| Case | Channel | Artifact | Candidate visibility | Taxonomy | Base -> Variant | Wrong visible |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in cards:
        lines.append(
            "| {case} | {signal} | {artifact} | {visibility} | {tax} | {base} -> {variant} | {visible} |".format(
                case=md_cell(row.get("case_id")),
                signal=md_cell(row.get("future_signal")),
                artifact=md_cell(row.get("artifact_type")),
                visibility=md_cell(row.get("candidate_visibility")),
                tax=md_cell(row.get("taxonomy_primary")),
                base=md_cell(row.get("base_prediction_answer")),
                variant=md_cell(row.get("variant_prediction_answer")),
                visible=md_cell(row.get("wrong_answer_literal_visible")),
            )
        )
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any], cards: list[Mapping[str, Any]]) -> str:
    counts = summary["cards"]
    lines = [
        "# MATH Type-Erasure v2 Invalid-Cast Audit",
        "",
        "This audit re-labels the v2 authority-violation rows with a narrower seed taxonomy.",
        "The purpose is to separate communication-boundary invalid casts from local re-solve and final-line/evaluator collisions before building the sender-receiver protocol.",
        "",
        "## Counts",
        "",
        f"- Violation cards: `{counts['records']}`",
        f"- Invalid-cast core cards: `{counts['invalid_cast_core_count']}`",
        f"- Direct visible answer-copy cards: `{counts['direct_visible_answer_copy_count']}`",
        f"- Local re-solve error cards: `{counts['local_re_solve_error_count']}`",
        f"- Final-answer contract / semantic-collision cards: `{counts['final_answer_contract_or_semantic_collision_count']}`",
        "",
    ]
    lines.extend(count_table("Primary Taxonomy", counts["taxonomy_primary_counts"]))
    lines.extend(count_table("Future Signals", counts["future_signal_counts"]))
    lines.extend(count_table("Artifact Types", counts["artifact_type_counts"]))
    lines.extend(count_table("Candidate Visibility", counts["candidate_visibility_counts"]))
    lines.extend(render_cards(cards))
    lines.extend(
        [
            "## Read",
            "",
            "Only the shared-workspace `math121` rows are clean invalid-cast-core candidates in this seed taxonomy.",
            "The typed no-candidate/hidden-candidate failures are better treated as local validation or final-answer-contract ambiguity, not as visible candidate copying.",
            "",
            "## Caveat",
            "",
            "These are deterministic seed labels. They are appropriate for selecting the next packet and for manual review triage, not for a population claim.",
            "",
        ]
    )
    return "\n".join(lines)


def build(args: argparse.Namespace) -> dict[str, Any]:
    evaluated_path = args.run_dir / "evaluation" / "evaluated_rows.jsonl"
    deltas_path = args.run_dir / "evaluation" / "paired_deltas.jsonl"
    evaluated = load_jsonl(evaluated_path)
    deltas = load_jsonl(deltas_path)
    packet = load_jsonl(args.packet)
    evaluated_by_key = {row_key(row): row for row in evaluated}
    packet_by_key = {row_key(row): row for row in packet}
    violation_deltas = [row for row in deltas if row.get("authority_violation")]
    cards = [make_card(row, evaluated_by_key, packet_by_key) for row in violation_deltas]
    summary = {
        "source_paths": {
            "run_dir": str(args.run_dir),
            "evaluated_rows": str(evaluated_path),
            "paired_deltas": str(deltas_path),
            "packet": str(args.packet),
        },
        "cards": card_summary(cards),
        "note": (
            "Seed taxonomy for v2 only. It separates inherited operator state from "
            "direct answer copy, local re-solve errors, and final-line/semantic collisions."
        ),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "invalid_cast_cards.jsonl", cards)
    write_text(args.out_dir / "invalid_cast_audit.md", render_markdown(summary, cards))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
