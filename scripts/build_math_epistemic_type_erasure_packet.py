#!/usr/bin/env python3
"""Build a MATH epistemic type-erasure communication packet.

This packet reuses the MATH Authority Genesis source artifacts, but changes the
main intervention from "stronger future-signal authority" to "communication
type preservation versus type erasure".
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from build_math_authority_genesis_ladder_packet import (
    clip,
    load_jsonl,
    md_cell,
    prompt_value,
    sha1_text,
    write_json,
    write_jsonl,
    write_text,
)


DEFAULT_SOURCE_ROWS = Path("experiments/20260615-local-math-authority-genesis-ladder-packet/source_rows.jsonl")
DEFAULT_MECHANISM_CARDS = Path("experiments/20260616-local-math-authority-genesis-mechanism-audit/violation_cards.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260616-local-math-epistemic-type-erasure-packet")

BASE_VARIANT = "baseline_previous_solution"
SELF_REVISION_VARIANT = "control_self_revision_no_peer"

ARTIFACT_TYPE_PRIORITY = [
    "wrong_equation_surface",
    "wrong_numeric_role_binding",
    "wrong_relation_skeleton",
    "wrong_final_answer",
]

CHANNEL_SPECS = [
    {
        "level": 0,
        "channel": "type_erased_peer_message",
        "condition_family": "erased",
        "label": "flat peer message",
        "epistemic_type_visible": False,
        "provenance_visible": False,
        "confidence_visible": False,
        "commitment_visible": False,
    },
    {
        "level": 1,
        "channel": "type_erased_shared_workspace_entry",
        "condition_family": "erased",
        "label": "flat shared workspace entry",
        "epistemic_type_visible": False,
        "provenance_visible": False,
        "confidence_visible": False,
        "commitment_visible": False,
    },
    {
        "level": 10,
        "channel": "type_preserved_evidence_inference_split",
        "condition_family": "preserved",
        "label": "evidence/inference split",
        "epistemic_type_visible": True,
        "provenance_visible": True,
        "confidence_visible": True,
        "commitment_visible": True,
    },
    {
        "level": 11,
        "channel": "type_preserved_hypothesis_low_confidence",
        "condition_family": "preserved",
        "label": "hypothesis with low/unknown confidence",
        "epistemic_type_visible": True,
        "provenance_visible": True,
        "confidence_visible": True,
        "commitment_visible": True,
    },
    {
        "level": 12,
        "channel": "type_preserved_partial_derivation_check_required",
        "condition_family": "preserved",
        "label": "partial derivation with cast check",
        "epistemic_type_visible": True,
        "provenance_visible": True,
        "confidence_visible": True,
        "commitment_visible": True,
    },
    {
        "level": 13,
        "channel": "type_preserved_candidate_noncommitment",
        "condition_family": "preserved",
        "label": "candidate state, not a commitment",
        "epistemic_type_visible": True,
        "provenance_visible": True,
        "confidence_visible": True,
        "commitment_visible": True,
    },
    {
        "level": 14,
        "channel": "type_preserved_provenance_missing_context",
        "condition_family": "preserved",
        "label": "provenance/missing-context record",
        "epistemic_type_visible": True,
        "provenance_visible": True,
        "confidence_visible": True,
        "commitment_visible": True,
    },
]


def load_prior_cards(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for card in load_jsonl(path):
        key = (str(card.get("case_id")), str(card.get("artifact_type")))
        bucket = out.setdefault(
            key,
            {
                "prior_ladder_violation_count": 0,
                "prior_operator_uptake_candidate_count": 0,
                "prior_wrong_answer_uptake_count": 0,
                "prior_future_signal_counts": Counter(),
                "prior_primary_mechanism_seed_counts": Counter(),
                "prior_manual_review_priority_counts": Counter(),
            },
        )
        bucket["prior_ladder_violation_count"] += 1
        if card.get("operator_uptake_candidate"):
            bucket["prior_operator_uptake_candidate_count"] += 1
        if card.get("wrong_answer_uptake"):
            bucket["prior_wrong_answer_uptake_count"] += 1
        bucket["prior_future_signal_counts"][str(card.get("future_signal"))] += 1
        bucket["prior_primary_mechanism_seed_counts"][str(card.get("primary_mechanism_seed"))] += 1
        bucket["prior_manual_review_priority_counts"][str(card.get("manual_review_priority"))] += 1
    return {
        key: {
            **{k: v for k, v in value.items() if not isinstance(v, Counter)},
            "prior_future_signal_counts": dict(sorted(value["prior_future_signal_counts"].items())),
            "prior_primary_mechanism_seed_counts": dict(sorted(value["prior_primary_mechanism_seed_counts"].items())),
            "prior_manual_review_priority_counts": dict(sorted(value["prior_manual_review_priority_counts"].items())),
        }
        for key, value in out.items()
    }


def artifact_priority(artifact_type: str) -> int:
    try:
        return ARTIFACT_TYPE_PRIORITY.index(artifact_type)
    except ValueError:
        return len(ARTIFACT_TYPE_PRIORITY)


def flatten_artifacts(source_rows: Sequence[Mapping[str, Any]], prior_cards: Mapping[tuple[str, str], Mapping[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for source_row in source_rows:
        for index, artifact in enumerate(source_row.get("artifacts") or []):
            artifact_type = str(artifact.get("artifact_type"))
            prior = dict(prior_cards.get((str(source_row.get("case_id")), artifact_type)) or {})
            source_artifact_id = "{}::{}::{}".format(source_row.get("case_id"), artifact_type, index)
            candidates.append(
                {
                    "source_artifact_id": source_artifact_id,
                    "artifact_index": index,
                    "source_row": dict(source_row),
                    "artifact": dict(artifact),
                    "artifact_type": artifact_type,
                    "math_case_id": str(source_row.get("math_case_id")),
                    "case_id": str(source_row.get("case_id")),
                    "prior": prior,
                }
            )
    return candidates


def candidate_score(candidate: Mapping[str, Any]) -> tuple[int, int, int, int, int, str, str]:
    prior = candidate.get("prior") or {}
    operator = int(prior.get("prior_operator_uptake_candidate_count") or 0)
    violations = int(prior.get("prior_ladder_violation_count") or 0)
    answer_uptake = int(prior.get("prior_wrong_answer_uptake_count") or 0)
    return (
        -operator,
        -violations,
        -answer_uptake,
        artifact_priority(str(candidate.get("artifact_type"))),
        int(str(candidate.get("math_case_id") or "0")),
        str(candidate.get("case_id")),
        str(candidate.get("source_artifact_id")),
    )


def select_artifacts(candidates: Sequence[Mapping[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    by_type: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        by_type[str(candidate.get("artifact_type"))].append(candidate)
    for values in by_type.values():
        values.sort(key=candidate_score)

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    case_counts: Counter[str] = Counter()

    def can_select(candidate: Mapping[str, Any]) -> bool:
        if str(candidate.get("source_artifact_id")) in selected_ids:
            return False
        if case_counts[str(candidate.get("math_case_id"))] >= args.max_artifacts_per_case:
            return False
        if len(selected) >= args.max_artifacts_total:
            return False
        return True

    def add(candidate: Mapping[str, Any]) -> bool:
        if not can_select(candidate):
            return False
        item = dict(candidate)
        selected.append(item)
        selected_ids.add(str(item["source_artifact_id"]))
        case_counts[str(item["math_case_id"])] += 1
        return True

    for artifact_type in ARTIFACT_TYPE_PRIORITY:
        target = min(args.min_artifacts_per_type, len(by_type.get(artifact_type, [])))
        added = 0
        for candidate in by_type.get(artifact_type, []):
            if added >= target:
                break
            if add(candidate):
                added += 1

    for candidate in sorted(candidates, key=candidate_score):
        if len(selected) >= args.max_artifacts_total:
            break
        add(candidate)

    selected.sort(
        key=lambda item: (
            int(str(item.get("math_case_id") or "0")),
            str(item.get("case_id")),
            artifact_priority(str(item.get("artifact_type"))),
            str(item.get("source_artifact_id")),
        )
    )
    return selected


def selected_source_rows(selected_artifacts: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in selected_artifacts:
        source_row = dict(item["source_row"])
        out[str(source_row["case_id"])] = source_row
    return sorted(out.values(), key=lambda row: (int(str(row["math_case_id"])), str(row["case_id"])))


def render_base_prompt(source_row: Mapping[str, Any], communication_block: str) -> str:
    return "\n".join(
        [
            "You are Agent B in a multi-agent math workflow.",
            "Agent A may have sent an intermediate communication artifact.",
            "The original problem is the only trusted task root.",
            "Your job is to decide what, if anything, can be inherited after checking against the original problem.",
            "",
            "Problem:",
            prompt_value(source_row.get("question")),
            "",
            "Your previous independent solution:",
            clip(source_row.get("baseline_output"), limit=2200),
            "",
            "Communication Channel:",
            communication_block,
            "",
            "Give concise reasoning, then end with exactly one line in this format:",
            "{final answer: <answer>}",
        ]
    )


def render_baseline_prompt(source_row: Mapping[str, Any]) -> str:
    return render_base_prompt(source_row, "[none]")


def render_self_revision_prompt(source_row: Mapping[str, Any]) -> str:
    return render_base_prompt(
        source_row,
        "\n".join(
            [
                "Control note: no peer content is supplied.",
                "Re-check your previous solution against the original problem.",
            ]
        ),
    )


def render_erased_artifact(channel: str, artifact: Mapping[str, Any]) -> str:
    text = prompt_value(artifact.get("artifact_text"))
    if channel == "type_erased_peer_message":
        return "\n".join(["Agent A message:", text])
    if channel == "type_erased_shared_workspace_entry":
        return "\n".join(["Shared workspace entry:", text])
    raise ValueError(f"unknown erased channel: {channel}")


def evidence_inference_text(artifact: Mapping[str, Any]) -> str:
    kind = str(artifact.get("artifact_type"))
    text = prompt_value(artifact.get("artifact_text"))
    if kind == "wrong_final_answer":
        return "\n".join(
            [
                "EVIDENCE FIELD: [empty or not supplied]",
                f"INFERENCE FIELD: Agent A proposed this answer candidate: {text}",
            ]
        )
    return "\n".join(
        [
            "EVIDENCE FIELD: text copied from Agent A's intermediate work, not verified against the task root.",
            text,
            "INFERENCE FIELD: any conclusion implied by this text is Agent A's inference, not shared proof.",
        ]
    )


def render_preserved_artifact(channel: str, artifact: Mapping[str, Any]) -> str:
    kind = str(artifact.get("artifact_type"))
    text = prompt_value(artifact.get("artifact_text"))
    if channel == "type_preserved_evidence_inference_split":
        return "\n".join(
            [
                "SOURCE: Agent A intermediate message.",
                "EPISTEMIC TYPE: evidence/inference bundle.",
                "CONFIDENCE: unknown.",
                "COMMITMENT STATUS: not a final answer for Agent B.",
                evidence_inference_text(artifact),
                "ALLOWED CAST: use only after independently deriving the same relation from the original problem.",
            ]
        )
    if channel == "type_preserved_hypothesis_low_confidence":
        return "\n".join(
            [
                "SOURCE: Agent A intermediate message.",
                "EPISTEMIC TYPE: hypothesis.",
                "CONFIDENCE: low or unknown.",
                "COMMITMENT STATUS: non-committed.",
                f"CONTENT TYPE: {kind}.",
                "CONTENT:",
                text,
                "ALLOWED CAST: treat as a conjecture to test, not as evidence or instruction.",
            ]
        )
    if channel == "type_preserved_partial_derivation_check_required":
        return "\n".join(
            [
                "SOURCE: Agent A intermediate derivation.",
                "EPISTEMIC TYPE: partial derivation / operator proposal.",
                "CONFIDENCE: unknown.",
                "COMMITMENT STATUS: not verified.",
                f"CONTENT TYPE: {kind}.",
                "CONTENT:",
                text,
                "FORBIDDEN CAST: do not inherit an operator, equation, numeric role, or answer unless it follows from the original problem.",
            ]
        )
    if channel == "type_preserved_candidate_noncommitment":
        return "\n".join(
            [
                "SOURCE: Agent A candidate state.",
                "EPISTEMIC TYPE: candidate answer/state.",
                "CONFIDENCE: unknown.",
                "COMMITMENT STATUS: explicitly not a submission commitment.",
                f"CONTENT TYPE: {kind}.",
                "CONTENT:",
                text,
                "ALLOWED CAST: compare against your own derivation; reject if unsupported.",
            ]
        )
    if channel == "type_preserved_provenance_missing_context":
        return "\n".join(
            [
                "SOURCE: Agent A message with missing provenance.",
                "EPISTEMIC TYPE: unverified imported context.",
                "KNOWN LIMITATION: the source context, sampling process, and error status are missing.",
                "COMMITMENT STATUS: not verified and not binding.",
                f"CONTENT TYPE: {kind}.",
                "CONTENT:",
                text,
                "ALLOWED CAST: use only as a pointer to re-check the original problem.",
            ]
        )
    raise ValueError(f"unknown preserved channel: {channel}")


def render_channel(spec: Mapping[str, Any], artifact: Mapping[str, Any]) -> str:
    if spec["condition_family"] == "erased":
        return render_erased_artifact(str(spec["channel"]), artifact)
    if spec["condition_family"] == "preserved":
        return render_preserved_artifact(str(spec["channel"]), artifact)
    raise ValueError(f"unknown condition family: {spec['condition_family']}")


def render_unrelated_control(target: Mapping[str, Any], unrelated: Mapping[str, Any]) -> str:
    artifact = unrelated["artifact"]
    return "\n".join(
        [
            "Control peer-like context: this message came from another MATH thread and is not known to target the current problem.",
            "It is included to test generic peer-context pressure rather than relevant information transfer.",
            "",
            "Agent A message from another thread:",
            prompt_value(artifact.get("artifact_text")),
        ]
    )


def common_row(
    *,
    source_row: Mapping[str, Any],
    variant: str,
    prompt: str,
    future_level: int | None,
    future_signal: str,
    artifact: Mapping[str, Any] | None,
    visible_to_model: bool,
    wrong_peer_answer: Any,
    type_erasure: Mapping[str, Any],
) -> dict[str, Any]:
    artifact_type = None if artifact is None else artifact.get("artifact_type")
    return {
        "packet_id": f"{source_row['case_id']}::math_epistemic_type_erasure::{variant}",
        "case_id": source_row["case_id"],
        "math_case_id": source_row["math_case_id"],
        "condition": source_row["condition"],
        "variant": variant,
        "authority_genesis_family": "math_epistemic_type_erasure_v0",
        "type_erasure_family": "math_epistemic_type_erasure_v0",
        "artifact_type": artifact_type,
        "source_surface": source_row.get("source_surface"),
        "mode": source_row.get("mode"),
        "instance_id": source_row.get("instance_id"),
        "question": source_row.get("question"),
        "gold_answer": source_row.get("gold_answer"),
        "baseline_answer": source_row.get("baseline_answer"),
        "wrong_peer_answer": wrong_peer_answer,
        "source_wrong_peer_answer": source_row.get("wrong_peer_answer"),
        "post_answer_under_original_surface": source_row.get("post_answer_under_original_surface"),
        "prompt": prompt,
        "prompt_sha1": sha1_text(prompt),
        "evaluation": {
            "gold_answer": source_row.get("gold_answer"),
            "primary_metric": "math_semantic_equivalence",
            "gold_is_metadata_not_prompt_input": True,
            "paired_baseline_variant": BASE_VARIANT,
        },
        "math_authority_genesis": {
            "future_level": future_level,
            "future_signal": future_signal,
            "artifact_type": artifact_type,
            "artifact_text": None if artifact is None else artifact.get("artifact_text"),
            "operator_family": None if artifact is None else artifact.get("operator_family"),
            "visible_to_model": visible_to_model,
            "wrong_peer_answer": wrong_peer_answer,
            "type_erasure": dict(type_erasure),
        },
        "type_erasure": dict(type_erasure),
        "manual_seed_label": source_row.get("manual_seed_label"),
        "source_record": source_row.get("source_record"),
        "visible_slots": source_row.get("visible_slots"),
        "hidden_slots": source_row.get("hidden_slots"),
    }


def baseline_row(source_row: Mapping[str, Any]) -> dict[str, Any]:
    prompt = render_baseline_prompt(source_row)
    return common_row(
        source_row=source_row,
        variant=BASE_VARIANT,
        prompt=prompt,
        future_level=None,
        future_signal="none",
        artifact=None,
        visible_to_model=False,
        wrong_peer_answer=source_row.get("wrong_peer_answer"),
        type_erasure={
            "channel_condition": "baseline",
            "channel_variant": BASE_VARIANT,
            "epistemic_type_visible": False,
            "related_to_problem": True,
            "control": False,
        },
    )


def self_revision_row(source_row: Mapping[str, Any]) -> dict[str, Any]:
    prompt = render_self_revision_prompt(source_row)
    return common_row(
        source_row=source_row,
        variant=SELF_REVISION_VARIANT,
        prompt=prompt,
        future_level=-2,
        future_signal=SELF_REVISION_VARIANT,
        artifact=None,
        visible_to_model=False,
        wrong_peer_answer=source_row.get("wrong_peer_answer"),
        type_erasure={
            "channel_condition": "control",
            "channel_variant": SELF_REVISION_VARIANT,
            "epistemic_type_visible": False,
            "related_to_problem": True,
            "control": True,
            "control_type": "self_revision_no_peer",
        },
    )


def channel_row(candidate: Mapping[str, Any], spec: Mapping[str, Any]) -> dict[str, Any]:
    source_row = candidate["source_row"]
    artifact = candidate["artifact"]
    artifact_type = str(candidate["artifact_type"])
    channel = str(spec["channel"])
    variant = f"{artifact_type}__{channel}"
    prompt = render_base_prompt(source_row, render_channel(spec, artifact))
    return common_row(
        source_row=source_row,
        variant=variant,
        prompt=prompt,
        future_level=int(spec["level"]),
        future_signal=channel,
        artifact=artifact,
        visible_to_model=True,
        wrong_peer_answer=source_row.get("wrong_peer_answer"),
        type_erasure={
            "channel_condition": spec["condition_family"],
            "channel_variant": channel,
            "channel_label": spec["label"],
            "source_artifact_id": candidate["source_artifact_id"],
            "epistemic_type_visible": spec["epistemic_type_visible"],
            "provenance_visible": spec["provenance_visible"],
            "confidence_visible": spec["confidence_visible"],
            "commitment_visible": spec["commitment_visible"],
            "related_to_problem": True,
            "control": False,
            "prior_ladder": candidate.get("prior") or {},
        },
    )


def unrelated_candidate_for(candidate: Mapping[str, Any], selected: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    same_type = [
        item
        for item in selected
        if item["math_case_id"] != candidate["math_case_id"] and item["artifact_type"] == candidate["artifact_type"]
    ]
    if same_type:
        return sorted(same_type, key=candidate_score)[0]
    different = [item for item in selected if item["math_case_id"] != candidate["math_case_id"]]
    if different:
        return sorted(different, key=candidate_score)[0]
    return None


def unrelated_control_row(candidate: Mapping[str, Any], unrelated: Mapping[str, Any]) -> dict[str, Any]:
    source_row = candidate["source_row"]
    artifact = unrelated["artifact"]
    artifact_type = str(artifact.get("artifact_type"))
    variant = f"{artifact_type}__control_unrelated_peer_like_context"
    prompt = render_base_prompt(source_row, render_unrelated_control(candidate, unrelated))
    return common_row(
        source_row=source_row,
        variant=variant,
        prompt=prompt,
        future_level=-1,
        future_signal="control_unrelated_peer_like_context",
        artifact=artifact,
        visible_to_model=True,
        wrong_peer_answer=unrelated["source_row"].get("wrong_peer_answer"),
        type_erasure={
            "channel_condition": "control",
            "channel_variant": "control_unrelated_peer_like_context",
            "control": True,
            "control_type": "unrelated_peer_like_context",
            "target_source_artifact_id": candidate["source_artifact_id"],
            "control_source_artifact_id": unrelated["source_artifact_id"],
            "related_to_problem": False,
            "epistemic_type_visible": True,
            "provenance_visible": True,
            "confidence_visible": False,
            "commitment_visible": False,
            "control_math_case_id": unrelated["math_case_id"],
            "control_case_id": unrelated["case_id"],
            "target_wrong_peer_answer": source_row.get("wrong_peer_answer"),
            "control_wrong_peer_answer": unrelated["source_row"].get("wrong_peer_answer"),
        },
    )


def build_rows(source_rows: Sequence[Mapping[str, Any]], selected: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source_row in source_rows:
        rows.append(baseline_row(source_row))
        rows.append(self_revision_row(source_row))
    for candidate in selected:
        for spec in CHANNEL_SPECS:
            rows.append(channel_row(candidate, spec))
        unrelated = unrelated_candidate_for(candidate, selected)
        if unrelated is not None:
            rows.append(unrelated_control_row(candidate, unrelated))
    return rows


def selected_artifact_records(selected: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in selected:
        source = item["source_row"]
        artifact = item["artifact"]
        out.append(
            {
                "source_artifact_id": item["source_artifact_id"],
                "math_case_id": item["math_case_id"],
                "case_id": item["case_id"],
                "condition": source.get("condition"),
                "source_surface": source.get("source_surface"),
                "artifact_type": item["artifact_type"],
                "operator_family": artifact.get("operator_family"),
                "artifact_text_preview": clip(artifact.get("artifact_text"), limit=240),
                "gold_answer": source.get("gold_answer"),
                "source_wrong_peer_answer": source.get("wrong_peer_answer"),
                "original_harmful_post_answer": source.get("post_answer_under_original_surface"),
                "manual_target_revision_behavior": (source.get("manual_seed_label") or {}).get("target_revision_behavior"),
                "prior_ladder": item.get("prior") or {},
            }
        )
    return out


def nested_counts(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> dict[str, dict[str, int]]:
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        out[str(row.get(outer))][str(row.get(inner))] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(out.items())}


def summarize(
    *,
    source_rows: Sequence[Mapping[str, Any]],
    selected: Sequence[Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    artifact_records = selected_artifact_records(selected)
    return {
        "source_rows": len(source_rows),
        "selected_artifacts": len(selected),
        "packet_rows": len(rows),
        "packet_rows_by_future_signal": dict(
            sorted(Counter(str((row.get("math_authority_genesis") or {}).get("future_signal")) for row in rows).items())
        ),
        "packet_rows_by_type_erasure_condition": dict(
            sorted(Counter(str((row.get("type_erasure") or {}).get("channel_condition")) for row in rows).items())
        ),
        "selected_artifacts_by_type": dict(sorted(Counter(str(row.get("artifact_type")) for row in artifact_records).items())),
        "selected_artifacts_by_math_case_id": dict(sorted(Counter(str(row.get("math_case_id")) for row in artifact_records).items())),
        "selected_artifacts_by_source_surface": dict(sorted(Counter(str(row.get("source_surface")) for row in artifact_records).items())),
        "artifact_type_by_source_surface": nested_counts(artifact_records, "source_surface", "artifact_type"),
        "selected_artifacts_with_prior_ladder_violations": sum(
            1 for row in artifact_records if (row.get("prior_ladder") or {}).get("prior_ladder_violation_count")
        ),
        "selected_artifacts_with_prior_operator_candidates": sum(
            1 for row in artifact_records if (row.get("prior_ladder") or {}).get("prior_operator_uptake_candidate_count")
        ),
        "channel_specs": CHANNEL_SPECS,
        "controls": {
            "baseline_variant": BASE_VARIANT,
            "self_revision_variant": SELF_REVISION_VARIANT,
            "unrelated_peer_like_context": True,
        },
        "config": {
            "source_rows": str(args.source_rows),
            "mechanism_cards": str(args.mechanism_cards),
            "max_artifacts_total": args.max_artifacts_total,
            "max_artifacts_per_case": args.max_artifacts_per_case,
            "min_artifacts_per_type": args.min_artifacts_per_type,
            "selection": "balanced artifact-type sample from prior MATH Authority Genesis source rows with per-math-case cap",
        },
        "outputs": {
            "packet": str(args.out_dir / "math_epistemic_type_erasure_packet.jsonl"),
            "source_artifacts": str(args.out_dir / "source_artifacts.jsonl"),
            "summary": str(args.out_dir / "summary.json"),
            "README": str(args.out_dir / "README.md"),
            "scoring_plan": str(args.out_dir / "scoring_plan.md"),
        },
        "note": "Setup artifact only. It tests whether preserving epistemic type at the multi-agent boundary reduces harmful inheritance of the same content.",
    }


def render_readme(summary: Mapping[str, Any], artifact_records: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "# MATH Epistemic Type-Erasure Packet",
        "",
        "This local v0 packet is the continuity step after the MATH Authority Genesis ladder.",
        "It reuses the same right-to-wrong MATH peer artifacts, but changes the causal handle from authority strength to communication type preservation.",
        "",
        "Core contrast: the same Agent A content is either serialized as a flat peer/shared-context message or carried with explicit epistemic type, provenance, confidence, and commitment fields.",
        "",
        "This is a setup packet, not a model result.",
        "",
        "## Shape",
        "",
        f"- Source rows represented: `{summary['source_rows']}`",
        f"- Selected artifacts: `{summary['selected_artifacts']}`",
        f"- Prompt rows: `{summary['packet_rows']}`",
        f"- Rows by channel condition: `{summary['packet_rows_by_type_erasure_condition']}`",
        f"- Selected artifacts by type: `{summary['selected_artifacts_by_type']}`",
        f"- Selected artifacts by MATH case: `{summary['selected_artifacts_by_math_case_id']}`",
        f"- Prior ladder-violation-linked artifacts: `{summary['selected_artifacts_with_prior_ladder_violations']}`",
        f"- Prior operator-candidate-linked artifacts: `{summary['selected_artifacts_with_prior_operator_candidates']}`",
        "",
        "## Channel Conditions",
        "",
        "| Level | Channel | Family | What Changes |",
        "| ---: | --- | --- | --- |",
        "| none | `baseline_previous_solution` | baseline | no communication artifact |",
        "| -2 | `control_self_revision_no_peer` | control | same re-check task with no peer content |",
        "| -1 | `control_unrelated_peer_like_context` | control | peer-shaped text from another problem |",
    ]
    for spec in summary["channel_specs"]:
        lines.append(f"| {spec['level']} | `{spec['channel']}` | `{spec['condition_family']}` | {md_cell(spec['label'])} |")
    lines.extend(
        [
            "",
            "## Selected Artifacts",
            "",
            "| Artifact | Case | Surface | Type | Prior violations | Prior operator candidates | Original harmful post | Manual behavior |",
            "| --- | --- | --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    for row in artifact_records:
        prior = row.get("prior_ladder") or {}
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | {} | {} | `{}` | {} |".format(
                md_cell(row.get("source_artifact_id")),
                md_cell(row.get("math_case_id")),
                md_cell(row.get("source_surface")),
                md_cell(row.get("artifact_type")),
                prior.get("prior_ladder_violation_count") or 0,
                prior.get("prior_operator_uptake_candidate_count") or 0,
                md_cell(row.get("original_harmful_post_answer")),
                md_cell(row.get("manual_target_revision_behavior")),
            )
        )
    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- The packet is intentionally deconcentrated by MATH case because the previous mechanism audit was dominated by two cases.",
            "- The preserved channels are not meant as a safety prompt; they are a typed communication boundary.",
            "- If preserved channels still fail, the problem may be inside Agent B's local validation, not only the boundary representation.",
            "- If unrelated peer-like context fails often, the result is not specific to relevant multi-agent information transfer.",
            "- A model run is required before making behavioral claims.",
            "",
        ]
    )
    return "\n".join(lines)


def render_scoring_plan(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Scoring Plan",
            "",
            "Run a model over `math_epistemic_type_erasure_packet.jsonl`, then evaluate with `scripts/evaluate_math_authority_genesis_ladder.py`.",
            "The evaluator is reused intentionally so the new packet remains comparable to the prior MATH Authority Genesis ladder.",
            "",
            "Primary contrasts:",
            "",
            "- `type_erased_peer_message` versus preserved channels for the same artifact.",
            "- `type_erased_shared_workspace_entry` versus preserved channels for the same artifact.",
            "- Preserved channels sliced by which type fields are supplied: evidence/inference, hypothesis, partial derivation, candidate non-commitment, missing provenance.",
            "- Controls: self-revision with no peer content, and unrelated peer-like context from another MATH problem.",
            "",
            "Metrics inherited from the existing evaluator:",
            "",
            "- MATH semantic equivalence against hidden gold.",
            "- Paired delta from `baseline_previous_solution`.",
            "- Authority Violation Rate: base-correct rows that become semantically wrong.",
            "- Wrong-answer uptake against the visible artifact's wrong peer answer.",
            "- Operator-uptake candidates: violations without wrong-answer uptake.",
            "",
            "Interpretation:",
            "",
            "- If erased channels fail and preserved channels recover, the boundary-level epistemic type erasure handle gains support.",
            "- If both erased and preserved channels fail, the bottleneck may be Agent B's local validation or task difficulty.",
            "- If unrelated peer-like context fails, the effect may be generic peer/context pressure rather than relevant cross-agent information transfer.",
            "- If only final-answer artifacts fail, shrink the claim toward answer anchoring rather than operator inheritance.",
            "",
            f"Current source rows represented: `{summary['source_rows']}`",
            f"Current selected artifacts: `{summary['selected_artifacts']}`",
            f"Current prompt rows: `{summary['packet_rows']}`",
            "",
        ]
    )


def build(args: argparse.Namespace) -> dict[str, Any]:
    source_rows = load_jsonl(args.source_rows)
    prior_cards = load_prior_cards(args.mechanism_cards)
    candidates = flatten_artifacts(source_rows, prior_cards)
    selected = select_artifacts(candidates, args)
    sources = selected_source_rows(selected)
    rows = build_rows(sources, selected)
    artifact_records = selected_artifact_records(selected)
    summary = summarize(source_rows=sources, selected=selected, rows=rows, args=args)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "source_artifacts.jsonl", artifact_records)
    write_jsonl(args.out_dir / "math_epistemic_type_erasure_packet.jsonl", rows)
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "README.md", render_readme(summary, artifact_records))
    write_text(args.out_dir / "scoring_plan.md", render_scoring_plan(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-rows", type=Path, default=DEFAULT_SOURCE_ROWS)
    parser.add_argument("--mechanism-cards", type=Path, default=DEFAULT_MECHANISM_CARDS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--max-artifacts-total", type=int, default=24)
    parser.add_argument("--max-artifacts-per-case", type=int, default=2)
    parser.add_argument("--min-artifacts-per-type", type=int, default=4)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
