#!/usr/bin/env python3
"""Materialize TypeCastArena MATH receiver prompts from sender artifacts.

The normal path consumes live Agent A outputs from
build_typecast_math_live_sender_stage.py. A bootstrap mode can reuse the
existing saved peer surfaces so the arena interface can be validated before the
next GPU run.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.typecast_arena import (
    BASE_VARIANT,
    CHANNEL_SPECS,
    FAMILY,
    SELF_REVISION_VARIANT,
    baseline_communication_block,
    channel_specs_as_dicts,
    clip,
    literal_in_text,
    make_math_receiver_row,
    md_cell,
    remove_candidate_answer,
    render_channel_block,
    self_revision_communication_block,
    sender_artifact_from_output,
    sha1_text,
    typecast_meta,
)
from peer_probe.math_eval import extract_answer_text, math_equiv


DEFAULT_SOURCE_ROWS = Path("experiments/20260615-local-math-authority-genesis-ladder-packet/source_rows.jsonl")
DEFAULT_SENDER_PACKET = Path("experiments/20260616-local-typecast-arena-math-live-sender-stage/typecast_math_sender_stage_packet.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260616-local-typecast-arena-math-bootstrap-receiver-packet")
PACKET_NAME = "typecast_math_receiver_packet.jsonl"


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


def output_text(row: Mapping[str, Any]) -> str:
    for key in ("output", "raw_output", "prediction", "answer", "text"):
        if row.get(key) is not None:
            return str(row[key]).strip()
    return ""


def source_rows_for_sender_packet(source_rows: Sequence[Mapping[str, Any]], sender_packet: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_case = {str(row.get("case_id")): dict(row) for row in source_rows}
    selected: list[dict[str, Any]] = []
    for row in sender_packet:
        case_id = str(row.get("case_id"))
        if case_id in by_case:
            selected.append(by_case[case_id])
    return selected


def selected_source_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    all_rows = load_jsonl(args.source_rows)
    if args.sender_packet.exists():
        sender_packet = load_jsonl(args.sender_packet)
        rows = source_rows_for_sender_packet(all_rows, sender_packet)
    else:
        rows = [dict(row) for row in all_rows]
    if args.max_cases:
        rows = rows[: args.max_cases]
    return rows


def live_artifacts(
    source_rows: Sequence[Mapping[str, Any]],
    sender_packet: Sequence[Mapping[str, Any]],
    sender_outputs: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    sources_by_case = {str(row.get("case_id")): dict(row) for row in source_rows}
    packet_by_id = {str(row.get("packet_id")): row for row in sender_packet}
    outputs_by_id = {str(row.get("packet_id")): row for row in sender_outputs if row.get("packet_id") is not None}
    artifacts: list[dict[str, Any]] = []
    for packet_id, packet_row in packet_by_id.items():
        output_row = outputs_by_id.get(packet_id)
        if not output_row:
            continue
        source_row = sources_by_case.get(str(packet_row.get("case_id")))
        if not source_row:
            continue
        text = output_text(output_row)
        answer, parse_source = extract_answer_text(text)
        sender_semantic = math_equiv(answer, source_row.get("gold_answer"))
        artifact = sender_artifact_from_output(text, fallback_answer=answer)
        artifact["parse_source"] = parse_source
        artifact["sender_candidate_correct"] = sender_semantic.correct
        artifact["sender_candidate_semantic_status"] = sender_semantic.status
        artifacts.append(
            {
                "source_row": source_row,
                "source_artifact_id": f"{source_row['case_id']}::live_sender_output",
                "artifact": artifact,
                "artifact_text": artifact["artifact_text"],
                "artifact_type": artifact["artifact_type"],
                "candidate_answer": artifact.get("candidate_answer"),
                "wrong_peer_answer": artifact.get("candidate_answer") if sender_semantic.correct is False else None,
                "sender_candidate_correct": sender_semantic.correct,
                "sender_candidate_semantic_status": sender_semantic.status,
                "sender_output": text,
                "sender_output_row": output_row,
                "source_mode": "live_sender_output",
            }
        )
    return artifacts


def bootstrap_artifacts(source_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for source_row in source_rows:
        text = str(source_row.get("peer_surface_excerpt") or "").strip()
        if not text:
            continue
        artifact_type = f"bootstrap_{source_row.get('source_surface') or 'peer_surface'}"
        artifacts.append(
            {
                "source_row": dict(source_row),
                "source_artifact_id": f"{source_row['case_id']}::{artifact_type}",
                "artifact": {
                    "artifact_text": text,
                    "artifact_type": artifact_type,
                    "source_surface": source_row.get("source_surface"),
                    "epistemic_type": "unknown_saved_peer_surface",
                    "candidate_answer": source_row.get("wrong_peer_answer"),
                },
                "artifact_text": text,
                "artifact_type": artifact_type,
                "candidate_answer": source_row.get("wrong_peer_answer"),
                "wrong_peer_answer": source_row.get("wrong_peer_answer"),
                "sender_candidate_correct": False,
                "sender_candidate_semantic_status": "bootstrap_wrong_by_construction",
                "source_mode": "bootstrap_saved_peer_surface",
            }
        )
    return artifacts


def source_baseline_correct(source_row: Mapping[str, Any]) -> bool:
    source_record = source_row.get("source_record") or {}
    return bool(
        source_record.get("transition_before_correct") is True
        or source_record.get("final_correct") is True and source_record.get("transition_type") == "stable_right"
    )


def candidate_leaks_after_structured_redaction(record: Mapping[str, Any]) -> bool:
    hidden_text, _ = remove_candidate_answer(record.get("artifact_text"), record.get("candidate_answer"))
    return literal_in_text(record.get("candidate_answer"), hidden_text)


def filter_artifacts(
    artifacts: Sequence[Mapping[str, Any]],
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [dict(row) for row in artifacts]
    summary: dict[str, Any] = {
        "input_artifacts": len(rows),
        "only_sender_candidate_wrong": bool(args.only_sender_candidate_wrong),
        "only_source_baseline_correct": bool(args.only_source_baseline_correct),
        "drop_redacted_candidate_leakage": bool(args.drop_redacted_candidate_leakage),
        "limit_artifacts": args.limit_artifacts,
    }

    if args.only_sender_candidate_wrong:
        before = len(rows)
        rows = [row for row in rows if row.get("sender_candidate_correct") is False]
        summary["dropped_sender_not_wrong"] = before - len(rows)

    if args.only_source_baseline_correct:
        before = len(rows)
        rows = [row for row in rows if source_baseline_correct(row.get("source_row") or {})]
        summary["dropped_source_baseline_not_correct"] = before - len(rows)

    if args.drop_redacted_candidate_leakage:
        before = len(rows)
        rows = [row for row in rows if not candidate_leaks_after_structured_redaction(row)]
        summary["dropped_redacted_candidate_leakage"] = before - len(rows)

    if args.limit_artifacts:
        before = len(rows)
        rows = rows[: args.limit_artifacts]
        summary["dropped_limit_artifacts"] = before - len(rows)

    summary["output_artifacts"] = len(rows)
    return rows, summary


def source_rows_matching_artifacts(
    source_rows: Sequence[Mapping[str, Any]],
    artifacts: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    case_ids = {str((row.get("source_row") or {}).get("case_id")) for row in artifacts}
    return [dict(row) for row in source_rows if str(row.get("case_id")) in case_ids]


def baseline_row(source_row: Mapping[str, Any]) -> dict[str, Any]:
    meta = typecast_meta(
        spec=None,
        channel_variant=BASE_VARIANT,
        channel_condition="baseline",
        artifact_text=None,
        visible_artifact_text=None,
        candidate_answer=source_row.get("wrong_peer_answer"),
        wrong_answer=source_row.get("wrong_peer_answer"),
        candidate_removed=False,
        control=False,
        related_to_problem=True,
        extra={
            "delivery_scope": "none",
            "admission_status": "none",
            "persistence": "none",
            "candidate_visibility": "none",
            "candidate_answer_visible_by_protocol": False,
            "epistemic_type_visible": False,
        },
    )
    return make_math_receiver_row(
        source_row=source_row,
        variant=BASE_VARIANT,
        communication_block=baseline_communication_block(),
        future_level=None,
        future_signal="none",
        artifact_type=None,
        artifact_text=None,
        visible_artifact_text=None,
        candidate_answer=source_row.get("wrong_peer_answer"),
        typecast=meta,
    )


def self_revision_row(source_row: Mapping[str, Any]) -> dict[str, Any]:
    meta = typecast_meta(
        spec=None,
        channel_variant=SELF_REVISION_VARIANT,
        channel_condition="control",
        artifact_text=None,
        visible_artifact_text=None,
        candidate_answer=source_row.get("wrong_peer_answer"),
        wrong_answer=source_row.get("wrong_peer_answer"),
        candidate_removed=False,
        control=True,
        related_to_problem=True,
        extra={
            "control_type": "self_revision_no_sender",
            "delivery_scope": "none",
            "admission_status": "none",
            "persistence": "none",
            "candidate_visibility": "none",
            "candidate_answer_visible_by_protocol": False,
            "epistemic_type_visible": False,
        },
    )
    return make_math_receiver_row(
        source_row=source_row,
        variant=SELF_REVISION_VARIANT,
        communication_block=self_revision_communication_block(),
        future_level=-2,
        future_signal=SELF_REVISION_VARIANT,
        artifact_type=None,
        artifact_text=None,
        visible_artifact_text=None,
        candidate_answer=source_row.get("wrong_peer_answer"),
        typecast=meta,
    )


def channel_row(record: Mapping[str, Any], spec_index: int) -> dict[str, Any]:
    spec = CHANNEL_SPECS[spec_index]
    source_row = record["source_row"]
    artifact_text = str(record.get("artifact_text") or "")
    candidate_answer = record.get("candidate_answer")
    wrong_answer = record.get("wrong_peer_answer")
    block, visible_text, removed = render_channel_block(spec, artifact_text, candidate_answer)
    artifact_type = str(record.get("artifact_type"))
    variant = f"{artifact_type}__{spec.channel}"
    meta = typecast_meta(
        spec=spec,
        channel_variant=spec.channel,
        channel_condition=spec.family,
        artifact_text=artifact_text,
        visible_artifact_text=visible_text,
        candidate_answer=candidate_answer,
        wrong_answer=wrong_answer,
        candidate_removed=removed,
        control=spec.family == "control",
        related_to_problem=True,
        extra={
            "source_artifact_id": record.get("source_artifact_id"),
            "source_mode": record.get("source_mode"),
            "spec_index": spec_index,
            "sender_candidate_correct": record.get("sender_candidate_correct"),
            "sender_candidate_semantic_status": record.get("sender_candidate_semantic_status"),
        },
    )
    return make_math_receiver_row(
        source_row=source_row,
        variant=variant,
        communication_block=block,
        future_level=spec.level,
        future_signal=spec.channel,
        artifact_type=artifact_type,
        artifact_text=artifact_text,
        visible_artifact_text=visible_text,
        candidate_answer=candidate_answer,
        typecast=meta,
        wrong_peer_answer=wrong_answer if wrong_answer is not None else "",
        use_source_wrong_answer=False,
    )


def unrelated_control_row(record: Mapping[str, Any], unrelated: Mapping[str, Any]) -> dict[str, Any]:
    source_row = record["source_row"]
    unrelated_source = unrelated["source_row"]
    artifact_text = str(unrelated.get("artifact_text") or "")
    candidate_answer = unrelated.get("candidate_answer")
    wrong_answer = unrelated.get("wrong_peer_answer")
    block = "\n".join(
        [
            "CONTROL: sender message from another MATH thread.",
            "ADMISSION STATUS: not related to the current problem.",
            "Agent A message from another thread:",
            artifact_text,
        ]
    )
    variant = "control_unrelated_sender_message"
    meta = typecast_meta(
        spec=None,
        channel_variant=variant,
        channel_condition="control",
        artifact_text=artifact_text,
        visible_artifact_text=artifact_text,
        candidate_answer=candidate_answer,
        wrong_answer=wrong_answer,
        candidate_removed=False,
        control=True,
        related_to_problem=False,
        extra={
            "control_type": "unrelated_sender_message",
            "delivery_scope": "one_receiver",
            "admission_status": "message_only",
            "persistence": "turn_local",
            "candidate_visibility": "artifact_native_unrelated",
            "candidate_answer_visible_by_protocol": None,
            "epistemic_type_visible": False,
            "control_case_id": unrelated_source.get("case_id"),
            "control_math_case_id": unrelated_source.get("math_case_id"),
            "target_source_artifact_id": record.get("source_artifact_id"),
            "control_source_artifact_id": unrelated.get("source_artifact_id"),
            "target_wrong_peer_answer": source_row.get("wrong_peer_answer"),
            "control_wrong_peer_answer": wrong_answer,
            "control_sender_candidate_answer": candidate_answer,
            "control_sender_candidate_correct": unrelated.get("sender_candidate_correct"),
        },
    )
    return make_math_receiver_row(
        source_row=source_row,
        variant=variant,
        communication_block=block,
        future_level=-1,
        future_signal=variant,
        artifact_type=str(unrelated.get("artifact_type")),
        artifact_text=artifact_text,
        visible_artifact_text=artifact_text,
        candidate_answer=candidate_answer,
        typecast=meta,
        wrong_peer_answer=wrong_answer if wrong_answer is not None else "",
        use_source_wrong_answer=False,
    )


def unrelated_for(record: Mapping[str, Any], records: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    source_case = str((record.get("source_row") or {}).get("case_id"))
    source_math = str((record.get("source_row") or {}).get("math_case_id"))
    for candidate in records:
        row = candidate.get("source_row") or {}
        if str(row.get("case_id")) != source_case and str(row.get("math_case_id")) != source_math:
            return candidate
    return None


def assert_unique_packet_ids(rows: Sequence[Mapping[str, Any]]) -> None:
    counts = Counter(str(row.get("packet_id")) for row in rows)
    duplicates = [key for key, count in counts.items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate packet_id values, first={duplicates[0]}")


def selected_spec_indices(channels: Sequence[str] | None) -> list[int]:
    if not channels:
        return list(range(len(CHANNEL_SPECS)))
    known = {spec.channel: index for index, spec in enumerate(CHANNEL_SPECS)}
    missing = [channel for channel in channels if channel not in known]
    if missing:
        raise ValueError(f"unknown TypeCastArena channels: {missing}")
    return [known[channel] for channel in channels]


def build_rows(
    source_rows: Sequence[Mapping[str, Any]],
    artifacts: Sequence[Mapping[str, Any]],
    *,
    channels: Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_by_case = {str(row.get("case_id")): row for row in source_rows}
    spec_indices = selected_spec_indices(channels)
    for source_row in source_rows:
        rows.append(baseline_row(source_row))
        rows.append(self_revision_row(source_row))
    for artifact in artifacts:
        for index in spec_indices:
            rows.append(channel_row(artifact, index))
        unrelated = unrelated_for(artifact, artifacts)
        if unrelated is not None:
            rows.append(unrelated_control_row(artifact, unrelated))
    assert_unique_packet_ids(rows)
    expected_cases = {str((row.get("source_row") or {}).get("case_id")) for row in artifacts}
    missing_baselines = expected_cases - set(source_by_case)
    if missing_baselines:
        raise ValueError(f"artifacts without source rows: {sorted(missing_baselines)[:3]}")
    return rows


def source_artifact_records(artifacts: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in artifacts:
        source = item["source_row"]
        artifact = item["artifact"]
        records.append(
            {
                "source_artifact_id": item.get("source_artifact_id"),
                "source_mode": item.get("source_mode"),
                "math_case_id": source.get("math_case_id"),
                "case_id": source.get("case_id"),
                "condition": source.get("condition"),
                "source_surface": source.get("source_surface"),
                "artifact_type": item.get("artifact_type"),
                "epistemic_type": artifact.get("epistemic_type"),
                "confidence": artifact.get("confidence"),
                "commitment_status": artifact.get("commitment_status"),
                "candidate_answer": item.get("candidate_answer"),
                "wrong_peer_answer": item.get("wrong_peer_answer"),
                "sender_candidate_correct": item.get("sender_candidate_correct"),
                "sender_candidate_semantic_status": item.get("sender_candidate_semantic_status"),
                "gold_answer": source.get("gold_answer"),
                "baseline_answer": source.get("baseline_answer"),
                "artifact_text_preview": clip(item.get("artifact_text"), limit=280),
                "candidate_answer_literal_in_artifact": literal_in_text(item.get("candidate_answer"), item.get("artifact_text")),
            }
        )
    return records


def summarize(
    *,
    source_rows: Sequence[Mapping[str, Any]],
    artifacts: Sequence[Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
    args: argparse.Namespace,
    artifact_filter: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    typecast_rows = [row.get("typecast_arena") or {} for row in rows]
    artifact_records = source_artifact_records(artifacts)
    return {
        "source_rows": len(source_rows),
        "sender_artifacts": len(artifacts),
        "packet_rows": len(rows),
        "source_mode": "bootstrap_saved_peer_surface" if args.bootstrap_from_source else "live_sender_output",
        "packet_rows_by_channel_condition": dict(sorted(Counter(str(row.get("channel_condition")) for row in typecast_rows).items())),
        "packet_rows_by_admission_status": dict(sorted(Counter(str(row.get("admission_status")) for row in typecast_rows).items())),
        "packet_rows_by_candidate_visibility": dict(sorted(Counter(str(row.get("candidate_visibility")) for row in typecast_rows).items())),
        "packet_rows_by_future_signal": dict(
            sorted(Counter(str((row.get("math_authority_genesis") or {}).get("future_signal")) for row in rows).items())
        ),
        "sender_artifacts_by_type": dict(sorted(Counter(str(row.get("artifact_type")) for row in artifact_records).items())),
        "sender_artifacts_by_math_case_id": dict(sorted(Counter(str(row.get("math_case_id")) for row in artifact_records).items())),
        "sender_artifacts_by_source_surface": dict(sorted(Counter(str(row.get("source_surface")) for row in artifact_records).items())),
        "sender_candidate_correct_counts": dict(sorted(Counter(str(row.get("sender_candidate_correct")) for row in artifact_records).items())),
        "artifact_filter": dict(artifact_filter or {}),
        "communication_rows_with_candidate_literal": sum(
            1 for row in typecast_rows if row.get("wrong_answer_literal_in_prompt")
        ),
        "channel_specs": channel_specs_as_dicts(),
        "config": {
            "source_rows": str(args.source_rows),
            "sender_packet": str(args.sender_packet),
            "sender_outputs": str(args.sender_outputs) if args.sender_outputs else None,
            "bootstrap_from_source": args.bootstrap_from_source,
            "max_cases": args.max_cases,
            "limit_artifacts": args.limit_artifacts,
            "only_sender_candidate_wrong": args.only_sender_candidate_wrong,
            "only_source_baseline_correct": args.only_source_baseline_correct,
            "drop_redacted_candidate_leakage": args.drop_redacted_candidate_leakage,
            "channels": args.channels,
        },
        "outputs": {
            "packet": str(args.out_dir / PACKET_NAME),
            "source_artifacts": str(args.out_dir / "sender_artifacts.jsonl"),
            "summary": str(args.out_dir / "summary.json"),
            "README": str(args.out_dir / "README.md"),
            "scoring_plan": str(args.out_dir / "scoring_plan.md"),
        },
    }


def render_readme(summary: Mapping[str, Any], artifacts: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "# TypeCastArena MATH Receiver Packet",
        "",
        "This packet sends Agent A artifacts through TypeCastArena communication boundary states before Agent B revises.",
        "",
        "## Shape",
        "",
        f"- Source mode: `{summary['source_mode']}`",
        f"- Source rows: `{summary['source_rows']}`",
        f"- Sender artifacts: `{summary['sender_artifacts']}`",
        f"- Receiver prompt rows: `{summary['packet_rows']}`",
        f"- Rows by channel condition: `{summary['packet_rows_by_channel_condition']}`",
        f"- Rows by admission status: `{summary['packet_rows_by_admission_status']}`",
        f"- Rows by candidate visibility: `{summary['packet_rows_by_candidate_visibility']}`",
        f"- Rows with candidate literal in prompt: `{summary['communication_rows_with_candidate_literal']}`",
        f"- Sender candidate correctness: `{summary['sender_candidate_correct_counts']}`",
        "",
        "## Sender Artifacts",
        "",
        "| Artifact | Case | Source mode | Surface | Candidate | Preview |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in source_artifact_records(artifacts):
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                md_cell(row.get("source_artifact_id")),
                md_cell(row.get("math_case_id")),
                md_cell(row.get("source_mode")),
                md_cell(row.get("source_surface")),
                md_cell(row.get("candidate_answer")),
                md_cell(row.get("artifact_text_preview")),
            )
        )
    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- Bootstrap mode reuses saved peer surfaces; live mode should consume actual Agent A outputs from the sender-stage packet.",
            "- The receiver packet is still a prompt packet until a model run produces Agent B outputs.",
            "- Candidate visibility, admission, persistence, and epistemic type are explicit fields so later analysis can separate lifecycle effects from content effects.",
            "",
        ]
    )
    return "\n".join(lines)


def render_scoring_plan(summary: Mapping[str, Any]) -> str:
    channels = summary.get("config", {}).get("channels") or []
    filters = summary.get("artifact_filter") or {}
    return "\n".join(
        [
            "# TypeCastArena Scoring Plan",
            "",
            f"Run the packet `{PACKET_NAME}` through an OpenAI-compatible endpoint, then score with:",
            "",
            "```bash",
            "python scripts/evaluate_math_authority_genesis_ladder.py \\",
            f"  --packet {summary['outputs']['packet']} \\",
            "  --outputs <run-dir>/outputs.jsonl \\",
            "  --prediction-source outputs \\",
            "  --out-dir <run-dir>/evaluation",
            "```",
            "",
            "Packet shaping:",
            "",
            f"- Active channels: `{channels}`",
            f"- Artifact filter: `{filters}`",
            "",
            "Primary contrasts:",
            "",
            "- direct peer message vs no-sender and unrelated-message controls;",
            "- verifier-admitted result vs direct peer message;",
            "- verifier-admitted result vs shared-workspace admitted state;",
            "- typed partial derivation and rejected quarantine vs admitted visible states;",
            "- self-revision and unrelated-message controls.",
            "",
            "Promotion signal:",
            "",
            "- verifier/admitted states add invalid-cast pressure beyond direct peer messages and controls;",
            "- typed or quarantine states reduce inherited operator/candidate casts relative to visible admitted states.",
            "",
            "Retirement signal:",
            "",
            "- receiver failures are mostly self-revision/local re-solve background;",
            "- lifecycle states do not separate once content is held fixed;",
            "- typed channels fail as often as erased/admitted channels for the same artifact class.",
            "",
        ]
    )


def build(args: argparse.Namespace) -> dict[str, Any]:
    source_rows = selected_source_rows(args)
    if args.bootstrap_from_source:
        artifacts = bootstrap_artifacts(source_rows)
    else:
        if args.sender_outputs is None:
            raise SystemExit("--sender-outputs is required unless --bootstrap-from-source is set")
        sender_packet = load_jsonl(args.sender_packet)
        sender_outputs = load_jsonl(args.sender_outputs)
        artifacts = live_artifacts(source_rows, sender_packet, sender_outputs)
    artifacts, artifact_filter = filter_artifacts(artifacts, args)
    if (
        args.only_sender_candidate_wrong
        or args.only_source_baseline_correct
        or args.drop_redacted_candidate_leakage
        or args.limit_artifacts
    ):
        source_rows = source_rows_matching_artifacts(source_rows, artifacts)
    rows = build_rows(source_rows, artifacts, channels=args.channels)
    summary = summarize(source_rows=source_rows, artifacts=artifacts, rows=rows, args=args, artifact_filter=artifact_filter)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "source_rows.jsonl", source_rows)
    write_jsonl(args.out_dir / "sender_artifacts.jsonl", source_artifact_records(artifacts))
    write_jsonl(args.out_dir / PACKET_NAME, rows)
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "README.md", render_readme(summary, artifacts))
    write_text(args.out_dir / "scoring_plan.md", render_scoring_plan(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-rows", type=Path, default=DEFAULT_SOURCE_ROWS)
    parser.add_argument("--sender-packet", type=Path, default=DEFAULT_SENDER_PACKET)
    parser.add_argument("--sender-outputs", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--max-cases", type=int, default=30)
    parser.add_argument("--limit-artifacts", type=int, default=0)
    parser.add_argument("--bootstrap-from-source", action="store_true")
    parser.add_argument("--only-sender-candidate-wrong", action="store_true")
    parser.add_argument(
        "--only-source-baseline-correct",
        action="store_true",
        help=(
            "Filter by the source trace's native baseline-correct label. "
            "Avoid this for lossy MATH traces unless those labels have been audited."
        ),
    )
    parser.add_argument(
        "--drop-redacted-candidate-leakage",
        action="store_true",
        help="Drop artifacts whose candidate answer still appears after structured answer-field redaction.",
    )
    parser.add_argument(
        "--channels",
        nargs="*",
        default=None,
        help="Optional TypeCastArena channel names. Omit to materialize all channels.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
