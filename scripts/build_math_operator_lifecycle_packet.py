#!/usr/bin/env python3
"""Build a focused MATH operator-lifecycle packet.

The packet reuses the strongest local evidence source, the MATH authority
genesis ladder rows with real Agent B baselines, and varies one sender object
across a small set of communication lifecycle states.
"""

from __future__ import annotations

import argparse
import json
import re
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
from build_math_epistemic_type_erasure_v2_packet import remove_candidate_answer


DEFAULT_SOURCE_ROWS = Path("experiments/20260615-local-math-authority-genesis-ladder-packet/source_rows.jsonl")
DEFAULT_AUTHORITY_CARDS = Path("experiments/20260616-local-math-authority-genesis-mechanism-audit/violation_cards.jsonl")
DEFAULT_V2_CARDS = Path("experiments/20260616-local-math-type-erasure-v2-invalid-cast-audit/invalid_cast_cards.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260617-local-math-operator-lifecycle-v1-packet")

PACKET_NAME = "math_operator_lifecycle_v1_packet.jsonl"
FAMILY = "math_operator_lifecycle_v1"

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
        "level": -4,
        "channel": "metadata_only_hidden_control",
        "family": "control",
        "label": "sender object metadata only; content withheld",
        "delivery_scope": "metadata_only",
        "admission_status": "withheld",
        "persistence": "none",
        "epistemic_type_visible": True,
        "candidate_visibility": "none",
        "hard_gate": True,
        "stress": False,
    },
    {
        "level": -3,
        "channel": "visible_inert_archived_content",
        "family": "visibility_stress",
        "label": "visible archived sender text; not admitted",
        "delivery_scope": "not_delivered",
        "admission_status": "not_admitted",
        "persistence": "none",
        "epistemic_type_visible": False,
        "candidate_visibility": "artifact_native",
        "hard_gate": False,
        "stress": True,
    },
    {
        "level": 0,
        "channel": "peer_message_direct",
        "family": "erased",
        "label": "direct peer message",
        "delivery_scope": "one_receiver",
        "admission_status": "message_only",
        "persistence": "turn_local",
        "epistemic_type_visible": False,
        "candidate_visibility": "artifact_native",
        "hard_gate": False,
        "stress": False,
    },
    {
        "level": 2,
        "channel": "shared_workspace_admitted",
        "family": "admitted",
        "label": "admitted shared workspace entry",
        "delivery_scope": "all_agents",
        "admission_status": "admitted_shared_workspace",
        "persistence": "shared_state",
        "epistemic_type_visible": False,
        "candidate_visibility": "artifact_native",
        "hard_gate": False,
        "stress": False,
    },
    {
        "level": 5,
        "channel": "verifier_admitted_result",
        "family": "admitted",
        "label": "verifier-admitted sender result",
        "delivery_scope": "one_receiver",
        "admission_status": "verifier_admitted",
        "persistence": "turn_local",
        "epistemic_type_visible": False,
        "candidate_visibility": "artifact_native",
        "hard_gate": False,
        "stress": False,
    },
    {
        "level": 4,
        "channel": "quarantine_withheld",
        "family": "quarantine",
        "label": "rejected by boundary; content withheld",
        "delivery_scope": "metadata_only",
        "admission_status": "rejected",
        "persistence": "none",
        "epistemic_type_visible": True,
        "candidate_visibility": "none",
        "hard_gate": True,
        "stress": False,
    },
    {
        "level": 10,
        "channel": "typed_inference_metadata_only",
        "family": "typed",
        "label": "typed inference object; content absent",
        "delivery_scope": "metadata_only",
        "admission_status": "typed_message",
        "persistence": "turn_local",
        "epistemic_type_visible": True,
        "candidate_visibility": "none",
        "hard_gate": True,
        "stress": False,
    },
    {
        "level": 11,
        "channel": "typed_partial_derivation_dependency_check",
        "family": "typed",
        "label": "typed derivation content visible; answer removed",
        "delivery_scope": "one_receiver",
        "admission_status": "typed_message",
        "persistence": "turn_local",
        "epistemic_type_visible": True,
        "candidate_visibility": "answer_removed",
        "hard_gate": False,
        "stress": True,
    },
]


def compact(value: Any) -> str:
    return re.sub(r"\s+", "", "" if value is None else str(value)).strip().lower()


def literal_in_text(needle: Any, haystack: Any) -> bool:
    n = compact(needle)
    h = compact(haystack)
    return bool(n and h and n in h)


def artifact_priority(artifact_type: str) -> int:
    try:
        return ARTIFACT_TYPE_PRIORITY.index(artifact_type)
    except ValueError:
        return len(ARTIFACT_TYPE_PRIORITY)


def safe_id(value: Any, limit: int = 80) -> str:
    text = re.sub(r"[^0-9A-Za-z]+", "_", str(value)).strip("_").lower()
    return text[:limit] or "item"


def counter_to_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items()))


def load_authority_prior(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for card in load_jsonl(path):
        key = (str(card.get("case_id")), str(card.get("artifact_type")))
        bucket = out.setdefault(
            key,
            {
                "authority_violation_count": 0,
                "operator_uptake_candidate_count": 0,
                "wrong_answer_uptake_count": 0,
                "future_signal_counts": Counter(),
                "primary_mechanism_counts": Counter(),
                "manual_review_priority_counts": Counter(),
            },
        )
        bucket["authority_violation_count"] += 1
        if card.get("operator_uptake_candidate"):
            bucket["operator_uptake_candidate_count"] += 1
        if card.get("wrong_answer_uptake"):
            bucket["wrong_answer_uptake_count"] += 1
        bucket["future_signal_counts"][str(card.get("future_signal"))] += 1
        bucket["primary_mechanism_counts"][str(card.get("primary_mechanism_seed"))] += 1
        bucket["manual_review_priority_counts"][str(card.get("manual_review_priority"))] += 1
    return {
        key: {
            **{k: v for k, v in value.items() if not isinstance(v, Counter)},
            "future_signal_counts": counter_to_dict(value["future_signal_counts"]),
            "primary_mechanism_counts": counter_to_dict(value["primary_mechanism_counts"]),
            "manual_review_priority_counts": counter_to_dict(value["manual_review_priority_counts"]),
        }
        for key, value in out.items()
    }


def load_v2_prior(path: Path) -> tuple[dict[str, dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    by_artifact_id: dict[str, dict[str, Any]] = {}
    by_case_type: dict[tuple[str, str], dict[str, Any]] = {}
    if not path.exists():
        return by_artifact_id, by_case_type

    def merge(bucket: dict[str, Any], card: Mapping[str, Any]) -> None:
        bucket["v2_violation_count"] += 1
        if card.get("invalid_cast_core"):
            bucket["v2_invalid_cast_core_count"] += 1
        if card.get("operator_uptake_candidate"):
            bucket["v2_operator_uptake_candidate_count"] += 1
        if card.get("direct_visible_answer_copy"):
            bucket["v2_direct_visible_answer_copy_count"] += 1
        if card.get("local_re_solve_error"):
            bucket["v2_local_re_solve_error_count"] += 1
        if card.get("final_answer_contract_or_semantic_collision"):
            bucket["v2_final_answer_contract_or_semantic_collision_count"] += 1
        bucket["v2_future_signal_counts"][str(card.get("future_signal"))] += 1
        bucket["v2_taxonomy_primary_counts"][str(card.get("taxonomy_primary"))] += 1

    def new_bucket() -> dict[str, Any]:
        return {
            "v2_violation_count": 0,
            "v2_invalid_cast_core_count": 0,
            "v2_operator_uptake_candidate_count": 0,
            "v2_direct_visible_answer_copy_count": 0,
            "v2_local_re_solve_error_count": 0,
            "v2_final_answer_contract_or_semantic_collision_count": 0,
            "v2_future_signal_counts": Counter(),
            "v2_taxonomy_primary_counts": Counter(),
        }

    for card in load_jsonl(path):
        meta = card.get("type_erasure") or {}
        source_artifact_id = meta.get("source_artifact_id")
        if source_artifact_id:
            merge(by_artifact_id.setdefault(str(source_artifact_id), new_bucket()), card)
        key = (str(card.get("case_id")), str(card.get("artifact_type")))
        merge(by_case_type.setdefault(key, new_bucket()), card)

    def freeze(bucket: Mapping[str, Any]) -> dict[str, Any]:
        return {
            **{k: v for k, v in bucket.items() if not isinstance(v, Counter)},
            "v2_future_signal_counts": counter_to_dict(bucket["v2_future_signal_counts"]),
            "v2_taxonomy_primary_counts": counter_to_dict(bucket["v2_taxonomy_primary_counts"]),
        }

    return (
        {key: freeze(value) for key, value in by_artifact_id.items()},
        {key: freeze(value) for key, value in by_case_type.items()},
    )


def flatten_artifacts(
    source_rows: Sequence[Mapping[str, Any]],
    authority_prior: Mapping[tuple[str, str], Mapping[str, Any]],
    v2_by_artifact_id: Mapping[str, Mapping[str, Any]],
    v2_by_case_type: Mapping[tuple[str, str], Mapping[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for source_row in source_rows:
        for index, artifact in enumerate(source_row.get("artifacts") or []):
            artifact_type = str(artifact.get("artifact_type"))
            source_artifact_id = f"{source_row.get('case_id')}::{artifact_type}::{index}"
            key = (str(source_row.get("case_id")), artifact_type)
            candidates.append(
                {
                    "source_artifact_id": source_artifact_id,
                    "artifact_index": index,
                    "source_row": dict(source_row),
                    "artifact": dict(artifact),
                    "artifact_type": artifact_type,
                    "math_case_id": str(source_row.get("math_case_id")),
                    "case_id": str(source_row.get("case_id")),
                    "prior": {
                        "authority": dict(authority_prior.get(key) or {}),
                        "v2": dict(v2_by_artifact_id.get(source_artifact_id) or v2_by_case_type.get(key) or {}),
                    },
                }
            )
    return candidates


def candidate_score(candidate: Mapping[str, Any]) -> tuple[int, int, int, int, int, str, str]:
    prior = candidate.get("prior") or {}
    authority = prior.get("authority") or {}
    v2 = prior.get("v2") or {}
    return (
        -int(v2.get("v2_invalid_cast_core_count") or 0),
        -int(v2.get("v2_operator_uptake_candidate_count") or 0),
        -int(authority.get("operator_uptake_candidate_count") or 0),
        -int(authority.get("authority_violation_count") or 0),
        artifact_priority(str(candidate.get("artifact_type"))),
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
        added = 0
        for candidate in by_type.get(artifact_type, []):
            if added >= args.min_artifacts_per_type:
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
            int(str(item.get("artifact_index") or 0)),
        )
    )
    for index, item in enumerate(selected, start=1):
        item["packet_artifact_id"] = f"a{index:02d}_{safe_id(item.get('artifact_type'))}"
    return selected


def selected_source_rows(selected: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in selected:
        source = dict(item["source_row"])
        out[str(source["case_id"])] = source
    return sorted(out.values(), key=lambda row: (int(str(row["math_case_id"])), str(row["case_id"])))


def artifact_text(candidate: Mapping[str, Any]) -> str:
    return prompt_value((candidate.get("artifact") or {}).get("artifact_text"))


def sanitized_artifact_text(candidate: Mapping[str, Any]) -> tuple[str, bool]:
    return remove_candidate_answer(artifact_text(candidate), (candidate.get("source_row") or {}).get("wrong_peer_answer"))


def render_receiver_prompt(source_row: Mapping[str, Any], communication_block: str) -> str:
    return "\n".join(
        [
            "You are Agent B in a sender-receiver MATH workflow.",
            "The original problem and your previous independent solution are the only trusted task roots.",
            "A communication layer may expose metadata, deliver a peer message, admit a shared state, quarantine content, or type an object as non-committed.",
            "",
            "Problem:",
            prompt_value(source_row.get("question")),
            "",
            "Your previous independent solution:",
            clip(source_row.get("baseline_output"), limit=2200),
            "",
            "Communication Lifecycle Event:",
            communication_block,
            "",
            "Task for Agent B:",
            "Decide what can be inherited only after re-deriving from the original problem.",
            "If the communication object is withheld, quarantined, inert, metadata-only, or non-committed, do not use it as evidence.",
            "",
            "Give concise reasoning, then end with exactly one line in this format:",
            "{final answer: <answer>}",
        ]
    )


def render_baseline_prompt(source_row: Mapping[str, Any]) -> str:
    return render_receiver_prompt(
        source_row,
        "\n".join(
            [
                "STATE: no Agent A object was delivered.",
                "ADMISSION STATUS: none.",
                "RECEIVER ACTION: re-check your previous independent solution only.",
            ]
        ),
    )


def render_self_revision_prompt(source_row: Mapping[str, Any]) -> str:
    return render_receiver_prompt(
        source_row,
        "\n".join(
            [
                "CONTROL: no sender message is supplied.",
                "This row preserves the receiver task format without cross-agent content.",
            ]
        ),
    )


def render_channel(spec: Mapping[str, Any], candidate: Mapping[str, Any]) -> tuple[str, str, bool, bool]:
    channel = str(spec["channel"])
    kind = str(candidate.get("artifact_type"))
    text = artifact_text(candidate)
    sanitized, removed = sanitized_artifact_text(candidate)

    if channel == "metadata_only_hidden_control":
        block = [
            "SENDER OBJECT METADATA:",
            "A boundary event exists for the current problem, but the object content is hidden from Agent B.",
            f"Content type: {kind}.",
            "Candidate answer field: not visible.",
            "Artifact content: [not visible].",
            "Receiver action: use only the original problem and your previous independent solution.",
        ]
        return "\n".join(block), "", False, False

    if channel == "visible_inert_archived_content":
        block = [
            "ARCHIVED SENDER RECORD:",
            "Delivery status: not delivered as a message.",
            "Admission status: not admitted to shared state.",
            "Receiver cast: visible diagnostic text only.",
            "Archived content:",
            text,
        ]
        return "\n".join(block), text, False, True

    if channel == "peer_message_direct":
        block = [
            "DELIVERY: direct message from Agent A to Agent B.",
            "Agent A says:",
            text,
        ]
        return "\n".join(block), text, False, True

    if channel == "shared_workspace_admitted":
        block = [
            "ADMISSION STATUS: admitted into the shared workspace for this problem.",
            "Shared workspace entry:",
            text,
        ]
        return "\n".join(block), text, False, True

    if channel == "verifier_admitted_result":
        block = [
            "ADMISSION STATUS: verifier-admitted sender result for this problem.",
            "Verifier-admitted content:",
            text,
        ]
        return "\n".join(block), text, False, True

    if channel == "quarantine_withheld":
        block = [
            "ADMISSION STATUS: rejected by the communication boundary.",
            "Reason: the sender object was unverified and was not admitted to Agent B's working state.",
            "Visible content: [withheld by quarantine policy].",
            "Receiver cast: no task evidence is available from this object.",
        ]
        return "\n".join(block), "", False, False

    if channel == "typed_inference_metadata_only":
        block = [
            "SOURCE: Agent A intermediate object.",
            "EPISTEMIC TYPE: inference or hypothesis, not evidence.",
            "CONTENT DELIVERY: metadata only; reasoning content absent.",
            "CANDIDATE ANSWER FIELD: absent.",
            f"Content type: {kind}.",
            "Allowed cast: at most a pointer that a sender object existed; no mathematical content is available.",
        ]
        return "\n".join(block), "", False, False

    if channel == "typed_partial_derivation_dependency_check":
        block = [
            "SOURCE: Agent A partial work.",
            "EPISTEMIC TYPE: partial derivation / operator proposal.",
            "COMMITMENT STATUS: not verified.",
            "ANSWER OR CANDIDATE FIELD: removed before delivery.",
            f"Content type: {kind}.",
            "Visible derivation content:",
            sanitized,
            "Boundary rule: do not inherit an operator, role binding, equation, or answer unless it follows from the original problem.",
        ]
        return "\n".join(block), sanitized, removed, True

    raise ValueError(f"unknown channel: {channel}")


def common_row(
    *,
    source_row: Mapping[str, Any],
    variant: str,
    prompt: str,
    future_level: int | None,
    future_signal: str,
    artifact: Mapping[str, Any] | None,
    visible_artifact_text: str | None,
    artifact_visible_to_model: bool,
    wrong_peer_answer: Any,
    lifecycle: Mapping[str, Any],
) -> dict[str, Any]:
    artifact_type = None if artifact is None else artifact.get("artifact_type")
    meta = dict(lifecycle)
    return {
        "packet_id": f"{source_row['case_id']}::{FAMILY}::{variant}",
        "case_id": source_row["case_id"],
        "math_case_id": source_row["math_case_id"],
        "condition": source_row["condition"],
        "variant": variant,
        "authority_genesis_family": FAMILY,
        "type_erasure_family": FAMILY,
        "sender_receiver_family": FAMILY,
        "typecast_arena_family": FAMILY,
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
            "artifact_text": visible_artifact_text,
            "operator_family": None if artifact is None else artifact.get("operator_family"),
            "visible_to_model": artifact_visible_to_model,
            "wrong_peer_answer": wrong_peer_answer,
            "sender_receiver": meta,
        },
        "sender_receiver": meta,
        "typecast_arena": meta,
        "type_erasure": meta,
        "manual_seed_label": source_row.get("manual_seed_label"),
        "source_record": source_row.get("source_record"),
        "visible_slots": source_row.get("visible_slots"),
        "hidden_slots": source_row.get("hidden_slots"),
    }


def baseline_row(source_row: Mapping[str, Any]) -> dict[str, Any]:
    prompt = render_baseline_prompt(source_row)
    lifecycle = {
        "channel_condition": "baseline",
        "channel_variant": BASE_VARIANT,
        "control": False,
        "delivery_scope": "none",
        "admission_status": "none",
        "persistence": "none",
        "candidate_visibility": "none",
        "candidate_answer_visible_by_protocol": False,
        "epistemic_type_visible": False,
        "related_to_problem": True,
        "hard_gate": False,
        "stress_condition": False,
        "wrong_answer_literal_in_communication": False,
        "wrong_answer_literal_in_prompt": literal_in_text(source_row.get("wrong_peer_answer"), prompt),
        "visible_artifact_text": "",
        "source_artifact_text": "",
        "candidate_answer": None,
    }
    return common_row(
        source_row=source_row,
        variant=BASE_VARIANT,
        prompt=prompt,
        future_level=None,
        future_signal="none",
        artifact=None,
        visible_artifact_text=None,
        artifact_visible_to_model=False,
        wrong_peer_answer=source_row.get("wrong_peer_answer"),
        lifecycle=lifecycle,
    )


def self_revision_row(source_row: Mapping[str, Any]) -> dict[str, Any]:
    prompt = render_self_revision_prompt(source_row)
    lifecycle = {
        "channel_condition": "control",
        "channel_variant": SELF_REVISION_VARIANT,
        "control": True,
        "control_type": "self_revision_no_sender",
        "delivery_scope": "none",
        "admission_status": "none",
        "persistence": "none",
        "candidate_visibility": "none",
        "candidate_answer_visible_by_protocol": False,
        "epistemic_type_visible": False,
        "related_to_problem": True,
        "hard_gate": True,
        "stress_condition": False,
        "wrong_answer_literal_in_communication": False,
        "wrong_answer_literal_in_prompt": literal_in_text(source_row.get("wrong_peer_answer"), prompt),
        "visible_artifact_text": "",
        "source_artifact_text": "",
        "candidate_answer": None,
    }
    return common_row(
        source_row=source_row,
        variant=SELF_REVISION_VARIANT,
        prompt=prompt,
        future_level=-5,
        future_signal=SELF_REVISION_VARIANT,
        artifact=None,
        visible_artifact_text=None,
        artifact_visible_to_model=False,
        wrong_peer_answer=source_row.get("wrong_peer_answer"),
        lifecycle=lifecycle,
    )


def channel_row(candidate: Mapping[str, Any], spec: Mapping[str, Any]) -> dict[str, Any]:
    source_row = candidate["source_row"]
    artifact = candidate["artifact"]
    artifact_type = str(candidate["artifact_type"])
    channel = str(spec["channel"])
    variant = f"{candidate['packet_artifact_id']}__{channel}"
    block, visible_artifact_text, candidate_removed, artifact_visible = render_channel(spec, candidate)
    prompt = render_receiver_prompt(source_row, block)
    wrong_peer_answer = source_row.get("wrong_peer_answer")
    lifecycle = {
        "channel_condition": spec["family"],
        "channel_variant": channel,
        "channel_label": spec["label"],
        "source_artifact_id": candidate["source_artifact_id"],
        "packet_artifact_id": candidate["packet_artifact_id"],
        "delivery_scope": spec["delivery_scope"],
        "admission_status": spec["admission_status"],
        "persistence": spec["persistence"],
        "epistemic_type_visible": spec["epistemic_type_visible"],
        "candidate_visibility": spec["candidate_visibility"],
        "candidate_answer_visible_by_protocol": False if spec["candidate_visibility"] in {"none", "answer_removed"} else None,
        "candidate_removed_from_visible_content": candidate_removed,
        "wrong_answer_literal_in_communication": literal_in_text(wrong_peer_answer, block),
        "wrong_answer_literal_in_prompt": literal_in_text(wrong_peer_answer, prompt),
        "source_artifact_text": artifact_text(candidate),
        "visible_artifact_text": visible_artifact_text,
        "candidate_answer": wrong_peer_answer,
        "hidden_candidate_answer": wrong_peer_answer if spec["candidate_visibility"] == "none" else None,
        "related_to_problem": True,
        "control": spec["family"] == "control",
        "hard_gate": bool(spec["hard_gate"]),
        "stress_condition": bool(spec["stress"]),
        "prior": candidate.get("prior") or {},
    }
    return common_row(
        source_row=source_row,
        variant=variant,
        prompt=prompt,
        future_level=int(spec["level"]),
        future_signal=channel,
        artifact=artifact,
        visible_artifact_text=visible_artifact_text,
        artifact_visible_to_model=artifact_visible,
        wrong_peer_answer=wrong_peer_answer,
        lifecycle=lifecycle,
    )


def unrelated_candidate_for(candidate: Mapping[str, Any], selected: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    for other in selected:
        if other.get("math_case_id") != candidate.get("math_case_id"):
            return other
    return None


def unrelated_control_row(candidate: Mapping[str, Any], unrelated: Mapping[str, Any]) -> dict[str, Any]:
    source_row = candidate["source_row"]
    artifact = unrelated["artifact"]
    artifact_type = str(artifact.get("artifact_type"))
    variant = f"{candidate['packet_artifact_id']}__control_unrelated_sender_message"
    communication = "\n".join(
        [
            "CONTROL: sender message from another MATH thread.",
            "Admission status: not related to the current problem.",
            "Unrelated Agent A message:",
            prompt_value(artifact.get("artifact_text")),
        ]
    )
    prompt = render_receiver_prompt(source_row, communication)
    wrong_peer_answer = unrelated["source_row"].get("wrong_peer_answer")
    lifecycle = {
        "channel_condition": "control",
        "channel_variant": "control_unrelated_sender_message",
        "control": True,
        "control_type": "unrelated_sender_message",
        "delivery_scope": "one_receiver",
        "admission_status": "message_only",
        "persistence": "turn_local",
        "candidate_visibility": "artifact_native_unrelated",
        "candidate_answer_visible_by_protocol": None,
        "epistemic_type_visible": False,
        "wrong_answer_literal_in_communication": literal_in_text(wrong_peer_answer, communication),
        "wrong_answer_literal_in_prompt": literal_in_text(wrong_peer_answer, prompt),
        "source_artifact_text": prompt_value(artifact.get("artifact_text")),
        "visible_artifact_text": prompt_value(artifact.get("artifact_text")),
        "candidate_answer": wrong_peer_answer,
        "related_to_problem": False,
        "hard_gate": False,
        "control_visibility": "visible_unrelated",
        "stress_condition": False,
        "target_source_artifact_id": candidate["source_artifact_id"],
        "control_source_artifact_id": unrelated["source_artifact_id"],
        "target_packet_artifact_id": candidate["packet_artifact_id"],
        "control_packet_artifact_id": unrelated["packet_artifact_id"],
        "control_math_case_id": unrelated["math_case_id"],
        "control_case_id": unrelated["case_id"],
        "target_wrong_peer_answer": source_row.get("wrong_peer_answer"),
        "control_wrong_peer_answer": wrong_peer_answer,
    }
    return common_row(
        source_row=source_row,
        variant=variant,
        prompt=prompt,
        future_level=-1,
        future_signal="control_unrelated_sender_message",
        artifact=artifact,
        visible_artifact_text=prompt_value(artifact.get("artifact_text")),
        artifact_visible_to_model=True,
        wrong_peer_answer=wrong_peer_answer,
        lifecycle=lifecycle,
    )


def assert_unique_packet_ids(rows: Sequence[Mapping[str, Any]]) -> None:
    counts = Counter(str(row.get("packet_id")) for row in rows)
    duplicates = [key for key, count in counts.items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate packet_id values, first={duplicates[0]}")


def assert_real_baselines(source_rows: Sequence[Mapping[str, Any]]) -> None:
    bad = []
    for row in source_rows:
        baseline = str(row.get("baseline_output") or "")
        if not baseline.strip() or "No prior independent Agent B solution is supplied" in baseline:
            bad.append(str(row.get("case_id")))
    if bad:
        raise ValueError(f"source rows without real baselines: {bad[:5]}")


def build_rows(source_rows: Sequence[Mapping[str, Any]], selected: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    assert_real_baselines(source_rows)
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
    assert_unique_packet_ids(rows)
    return rows


def artifact_records(selected: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in selected:
        source = item["source_row"]
        artifact = item["artifact"]
        sanitized, changed = sanitized_artifact_text(item)
        records.append(
            {
                "packet_artifact_id": item["packet_artifact_id"],
                "source_artifact_id": item["source_artifact_id"],
                "math_case_id": item["math_case_id"],
                "case_id": item["case_id"],
                "condition": source.get("condition"),
                "source_surface": source.get("source_surface"),
                "artifact_type": item["artifact_type"],
                "operator_family": artifact.get("operator_family"),
                "artifact_text_preview": clip(artifact.get("artifact_text"), limit=260),
                "gold_answer": source.get("gold_answer"),
                "source_wrong_peer_answer": source.get("wrong_peer_answer"),
                "candidate_answer_removed_by_sanitizer": changed,
                "sanitized_artifact_preview": clip(sanitized, limit=260),
                "original_harmful_post_answer": source.get("post_answer_under_original_surface"),
                "target_revision_behavior": (source.get("manual_seed_label") or {}).get("target_revision_behavior"),
                "prior": item.get("prior") or {},
            }
        )
    return records


def prompt_audit(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_channel: dict[str, Counter[str]] = defaultdict(Counter)
    hard_gate_leaks: list[str] = []
    for row in rows:
        meta = row.get("sender_receiver") or {}
        channel = str(meta.get("channel_variant"))
        by_channel[channel]["rows"] += 1
        if meta.get("visible_artifact_text"):
            by_channel[channel]["rows_with_visible_artifact_text"] += 1
        if meta.get("wrong_answer_literal_in_communication"):
            by_channel[channel]["wrong_answer_literal_in_communication"] += 1
        if meta.get("wrong_answer_literal_in_prompt"):
            by_channel[channel]["wrong_answer_literal_in_prompt"] += 1
        if meta.get("hard_gate"):
            by_channel[channel]["hard_gate_rows"] += 1
            if meta.get("wrong_answer_literal_in_communication") or (
                meta.get("visible_artifact_text") and channel != "control_unrelated_sender_message"
            ):
                hard_gate_leaks.append(str(row.get("packet_id")))
    return {
        "by_channel": {key: dict(sorted(value.items())) for key, value in sorted(by_channel.items())},
        "hard_gate_leak_count": len(hard_gate_leaks),
        "hard_gate_leak_packet_ids": hard_gate_leaks[:20],
    }


def nested_counts(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> dict[str, dict[str, int]]:
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        out[str(row.get(outer))][str(row.get(inner))] += 1
    return {key: counter_to_dict(value) for key, value in sorted(out.items())}


def summarize(
    *,
    source_rows: Sequence[Mapping[str, Any]],
    selected: Sequence[Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    records = artifact_records(selected)
    lifecycle_rows = [row.get("sender_receiver") or {} for row in rows]
    return {
        "status": "packet_materialized_local_only",
        "purpose": "Test whether the same wrong sender operator artifact becomes more harmful when it is directly messaged, admitted, verifier-admitted, withheld, or typed.",
        "unit": "sender artifact x lifecycle channel, paired against a real prior Agent B solution",
        "source_rows_represented": len(source_rows),
        "selected_artifacts": len(selected),
        "packet_rows": len(rows),
        "selected_artifacts_by_type": counter_to_dict(Counter(str(row.get("artifact_type")) for row in records)),
        "selected_artifacts_by_math_case_id": counter_to_dict(Counter(str(row.get("math_case_id")) for row in records)),
        "selected_artifacts_by_source_surface": counter_to_dict(Counter(str(row.get("source_surface")) for row in records)),
        "artifact_type_by_source_surface": nested_counts(records, "source_surface", "artifact_type"),
        "selected_artifacts_with_authority_operator_prior": sum(
            1 for row in records if ((row.get("prior") or {}).get("authority") or {}).get("operator_uptake_candidate_count")
        ),
        "selected_artifacts_with_v2_invalid_cast_core_prior": sum(
            1 for row in records if ((row.get("prior") or {}).get("v2") or {}).get("v2_invalid_cast_core_count")
        ),
        "packet_rows_by_future_signal": counter_to_dict(
            Counter(str((row.get("math_authority_genesis") or {}).get("future_signal")) for row in rows)
        ),
        "packet_rows_by_channel_condition": counter_to_dict(Counter(str(row.get("channel_condition")) for row in lifecycle_rows)),
        "packet_rows_by_admission_status": counter_to_dict(Counter(str(row.get("admission_status")) for row in lifecycle_rows)),
        "packet_rows_by_candidate_visibility": counter_to_dict(Counter(str(row.get("candidate_visibility")) for row in lifecycle_rows)),
        "prompt_audit": prompt_audit(rows),
        "channel_specs": CHANNEL_SPECS,
        "primary_contrast": [
            "peer_message_direct",
            "shared_workspace_admitted",
            "verifier_admitted_result",
            "quarantine_withheld",
            "typed_inference_metadata_only",
            "typed_partial_derivation_dependency_check",
        ],
        "controls": [
            BASE_VARIANT,
            SELF_REVISION_VARIANT,
            "metadata_only_hidden_control",
            "control_unrelated_sender_message",
        ],
        "config": {
            "source_rows": str(args.source_rows),
            "authority_cards": str(args.authority_cards),
            "v2_cards": str(args.v2_cards),
            "max_artifacts_total": args.max_artifacts_total,
            "max_artifacts_per_case": args.max_artifacts_per_case,
            "min_artifacts_per_type": args.min_artifacts_per_type,
        },
        "outputs": {
            "packet": str(args.out_dir / PACKET_NAME),
            "source_artifacts": str(args.out_dir / "source_artifacts.jsonl"),
            "summary": str(args.out_dir / "summary.json"),
            "README": str(args.out_dir / "README.md"),
            "scoring_plan": str(args.out_dir / "scoring_plan.md"),
        },
    }


def render_readme(summary: Mapping[str, Any], records: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "# MATH Operator Lifecycle V1 Packet",
        "",
        "Status: local packet only. No GPU run has been launched from this materialization step.",
        "",
        "## Purpose",
        "",
        str(summary["purpose"]),
        "",
        "## Shape",
        "",
        f"- Source rows represented: `{summary['source_rows_represented']}`",
        f"- Selected sender artifacts: `{summary['selected_artifacts']}`",
        f"- Prompt rows: `{summary['packet_rows']}`",
        f"- Selected artifacts by type: `{summary['selected_artifacts_by_type']}`",
        f"- Selected artifacts by MATH case: `{summary['selected_artifacts_by_math_case_id']}`",
        f"- Rows by channel condition: `{summary['packet_rows_by_channel_condition']}`",
        f"- Rows by candidate visibility: `{summary['packet_rows_by_candidate_visibility']}`",
        f"- Prompt-audit hard-gate leaks: `{summary['prompt_audit']['hard_gate_leak_count']}`",
        "",
        "## Lifecycle Channels",
        "",
        "| Level | Channel | Family | Admission | Candidate visibility | Gate role |",
        "| ---: | --- | --- | --- | --- | --- |",
        "| none | `baseline_previous_solution` | baseline | none | none | baseline |",
        "| -5 | `control_self_revision_no_peer` | control | none | none | hard control |",
    ]
    for spec in summary["channel_specs"]:
        role = "hard control" if spec["hard_gate"] else ("stress" if spec["stress"] else "target")
        lines.append(
            f"| {spec['level']} | `{spec['channel']}` | `{spec['family']}` | "
            f"`{spec['admission_status']}` | `{spec['candidate_visibility']}` | {role} |"
        )
    lines.extend(
        [
            "| -1 | `control_unrelated_sender_message` | control | message_only | artifact_native_unrelated | hard control |",
            "",
            "## Selected Artifacts",
            "",
            "| Packet id | Case | Surface | Type | Prior invalid-cast core | Prior operator cards | Sanitized changed |",
            "| --- | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in records:
        prior = row.get("prior") or {}
        authority = prior.get("authority") or {}
        v2 = prior.get("v2") or {}
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | {} | {} | `{}` |".format(
                md_cell(row.get("packet_artifact_id")),
                md_cell(row.get("math_case_id")),
                md_cell(row.get("source_surface")),
                md_cell(row.get("artifact_type")),
                v2.get("v2_invalid_cast_core_count") or 0,
                authority.get("operator_uptake_candidate_count") or 0,
                md_cell(row.get("candidate_answer_removed_by_sanitizer")),
            )
        )
    lines.extend(
        [
            "",
            "## Remote Launch Template",
            "",
            "Use the generic TypeCastArena runner after copying this packet to A800_2.",
            "",
            "```bash",
            "PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl \\",
            "RUN_ID=<stamp>-a8002-math-operator-lifecycle-v1-qwen25-14b \\",
            "MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \\",
            "SERVED_MODEL=qwen2.5-14b-math-operator-lifecycle-v1 \\",
            "GPU_ID=<free-gpu> PORT=<free-port> EVALUATE=1 BOUNDARY_ANALYZE=1 \\",
            "bash scripts/run_typecast_arena_packet_a8002.sh",
            "```",
            "",
            "## Caveats",
            "",
            "- The sender artifacts are saved objects from prior MATH rows; this packet tests lifecycle casting around those objects.",
            "- `visible_inert_archived_content` is a visibility stress condition because it deliberately shows sender content.",
            "- `typed_partial_derivation_dependency_check` removes candidate-answer strings, but it still exposes operator content by design.",
            "- A model run and case audit are required before making behavioral claims.",
            "",
        ]
    )
    return "\n".join(lines)


def render_scoring_plan(summary: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Scoring Plan",
            "",
            "## Preflight Contract",
            "",
            f"Purpose: {summary['purpose']}",
            f"Unit: {summary['unit']}",
            "Primary contrast: compare the same sender artifact across direct peer, shared workspace, verifier-admitted, quarantine, typed metadata, and typed partial-derivation channels.",
            "Secondary contrasts: baseline previous solution, self revision with no sender, unrelated sender message, and metadata-only hidden control.",
            "Success signal: admitted or verifier-admitted channels produce more base-right to wrong deltas and more operator-uptake candidates than hard controls.",
            "Failure signal: hard controls show comparable failures, or most failures are direct candidate copies, parser artifacts, local re-solve noise, or final-line formatting errors.",
            "Invalidation conditions: hidden controls leak sender content, baseline rows lack real previous solutions, evaluator gold differs from original MATH gold, or duplicate variants collapse paired deltas.",
            "",
            "## Commands",
            "",
            "Gold smoke:",
            "",
            "```bash",
            "python scripts/evaluate_math_authority_genesis_ladder.py \\",
            "  --packet experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl \\",
            "  --prediction-source gold \\",
            "  --out-dir experiments/20260617-local-math-operator-lifecycle-v1-packet/gold_smoke",
            "```",
            "",
            "Boundary audit after a real run:",
            "",
            "```bash",
            "python scripts/analyze_typecast_boundary_obedience.py \\",
            "  --packet experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl \\",
            "  --run-dir <run>/evaluation \\",
            "  --out-dir <run>/boundary_obedience",
            "```",
            "",
            "## Required Readouts",
            "",
            "- `evaluation/summary.json` and `evaluation/paired_deltas.jsonl`",
            "- boundary-obedience cards by channel",
            "- artifact-family cards for inherited operator state vs answer copy",
            "- leave-one-case-out sensitivity for MATH case concentration",
            "",
        ]
    )


def build(args: argparse.Namespace) -> dict[str, Any]:
    source_rows = load_jsonl(args.source_rows)
    authority_prior = load_authority_prior(args.authority_cards)
    v2_by_artifact_id, v2_by_case_type = load_v2_prior(args.v2_cards)
    candidates = flatten_artifacts(source_rows, authority_prior, v2_by_artifact_id, v2_by_case_type)
    selected = select_artifacts(candidates, args)
    sources = selected_source_rows(selected)
    rows = build_rows(sources, selected)
    records = artifact_records(selected)
    summary = summarize(source_rows=sources, selected=selected, rows=rows, args=args)

    if summary["prompt_audit"]["hard_gate_leak_count"]:
        raise ValueError(f"hard-gate audit failed: {summary['prompt_audit']['hard_gate_leak_packet_ids'][:5]}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "source_artifacts.jsonl", records)
    write_jsonl(args.out_dir / PACKET_NAME, rows)
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "README.md", render_readme(summary, records))
    write_text(args.out_dir / "scoring_plan.md", render_scoring_plan(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-rows", type=Path, default=DEFAULT_SOURCE_ROWS)
    parser.add_argument("--authority-cards", type=Path, default=DEFAULT_AUTHORITY_CARDS)
    parser.add_argument("--v2-cards", type=Path, default=DEFAULT_V2_CARDS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--max-artifacts-total", type=int, default=16)
    parser.add_argument("--max-artifacts-per-case", type=int, default=2)
    parser.add_argument("--min-artifacts-per-type", type=int, default=3)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
