#!/usr/bin/env python3
"""Build a claim-hygiene packet for MATH200 peer-influence records.

This script does not call a model and does not recompute correctness. It
collects the cases that currently make the slot-level peer-message story hard
to state cleanly: semantic-unknown records, source-label-unreliable source
cases, source-label-sensitive rows, and behavior-changing rows that deserve
field-level labels.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from audit_peer_influence_protocol import CONDITION_META, CONDITIONS, condition_metrics
from peer_probe.io_utils import read_jsonl, write_json, write_jsonl
from peer_probe.math_eval import math_equiv


BEHAVIOR_CHANGING_TRANSITIONS = {"right_to_wrong", "wrong_to_right"}

LABEL_FIELDS = {
    "target_predicate_preserved": None,
    "relation_skeleton_quality": None,
    "numeric_role_slot_quality": None,
    "equation_surface_quality": None,
    "final_answer_authority_visible": None,
    "source_identity_effect": None,
    "target_revision_behavior": None,
    "manual_note": None,
}


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def case_id(record: Dict[str, Any]) -> str:
    return str(record.get("case_index", record.get("instance_id")))


def case_sort_key(value: Any) -> Tuple[int, str]:
    text = str(value)
    return (int(text), text) if text.isdigit() else (10**9, text)


def clip(value: Any, limit: int = 700) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def by_case_condition(records: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    table: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
    for record in records:
        table[case_id(record)][str(record.get("condition"))] = record
    return dict(table)


def condition_post_status(record: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if record is None:
        return {"correct": None, "answer": None, "status": "missing_record", "transition": None}
    post_eval = ((record.get("semantic_eval") or {}).get("post") or {})
    return {
        "correct": record.get("post_exposure_correct"),
        "answer": record.get("post_exposure_answer_raw"),
        "status": post_eval.get("status"),
        "transition": record.get("transition"),
    }


def first_peer_surface(record: Dict[str, Any]) -> Dict[str, Any]:
    exposures = record.get("peer_exposure") or []
    if not exposures:
        return {}
    first = exposures[0]
    return {
        "display_source": first.get("source_agent") or first.get("source") or first.get("agent_id"),
        "original_source": first.get("original_source"),
        "surface": first.get("surface") or first.get("message_type"),
        "text": first.get("message") or first.get("content") or first.get("text") or first.get("rationale"),
    }


def source_case_by_id(source_cases: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(row.get("case_index")): row for row in source_cases}


def source_audit_by_id(audit: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {str(row.get("case_index")): row for row in audit.get("source_case_audit") or []}


def source_reliability_reason(source_audit: Dict[str, Any]) -> str:
    correct_eval = source_audit.get("correct_peer_semantic") or {}
    wrong_eval = source_audit.get("wrong_peer_semantic") or {}
    correct_ok = correct_eval.get("correct")
    wrong_ok = wrong_eval.get("correct")
    if correct_ok is not True and wrong_ok is not False:
        return "both_labels_unreliable"
    if correct_ok is None:
        return "correct_peer_unknown"
    if correct_ok is False:
        return "correct_peer_not_correct"
    if wrong_ok is None:
        return "wrong_peer_unknown"
    if wrong_ok is True:
        return "wrong_peer_not_wrong"
    return "other"


def unknown_records(
    records: List[Dict[str, Any]],
    source_cases: Dict[str, Dict[str, Any]],
    source_audits: Dict[str, Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Counter[str]]:
    rows: List[Dict[str, Any]] = []
    per_case: Dict[str, Dict[str, Any]] = {}
    status_counts: Counter[str] = Counter()
    for record in records:
        if record.get("post_exposure_correct") is not None:
            continue
        cid = case_id(record)
        post_eval = ((record.get("semantic_eval") or {}).get("post") or {})
        status = str(post_eval.get("status"))
        status_counts[status] += 1
        rows.append(
            {
                "case_index": record.get("case_index"),
                "condition": record.get("condition"),
                "gold_answer_raw": record.get("gold_answer_raw"),
                "post_answer_raw": record.get("post_exposure_answer_raw"),
                "semantic_status": status,
                "source_label_reliable": ((record.get("semantic_eval") or {}).get("source_labels_semantically_reliable") is True),
                "transition_numeric": record.get("transition_numeric"),
                "post_output_excerpt": clip(record.get("post_exposure_output")),
            }
        )
        entry = per_case.setdefault(
            cid,
            {
                "case_index": record.get("case_index"),
                "instance_id": record.get("instance_id"),
                "question": record.get("question"),
                "gold_answer_raw": record.get("gold_answer_raw"),
                "source_label_reliable": source_audits.get(cid, {}).get("source_labels_semantically_reliable"),
                "unknown_count": 0,
                "unknown_statuses": Counter(),
                "unknown_conditions": [],
                "baseline_unknown": False,
                "correct_peer_answer_raw": source_audits.get(cid, {}).get("correct_peer_answer_raw"),
                "wrong_peer_answer_raw": source_audits.get(cid, {}).get("wrong_peer_answer_raw"),
            },
        )
        entry["unknown_count"] += 1
        entry["unknown_statuses"][status] += 1
        entry["unknown_conditions"].append(record.get("condition"))
        if record.get("condition") == "no_peer":
            entry["baseline_unknown"] = True

    case_rows = []
    for cid, entry in per_case.items():
        unknown_count = int(entry["unknown_count"])
        source_case = source_cases.get(cid) or {}
        unknown_bucket = "surface_limited"
        if unknown_count >= 8:
            unknown_bucket = "case_heavy"
        if entry["baseline_unknown"]:
            unknown_bucket = "baseline_unknown" if unknown_count < 8 else "case_heavy_with_baseline"
        case_rows.append(
            {
                "case_index": entry["case_index"],
                "instance_id": entry["instance_id"],
                "question": entry["question"] or source_case.get("question"),
                "gold_answer_raw": entry["gold_answer_raw"],
                "source_label_reliable": entry["source_label_reliable"],
                "unknown_bucket": unknown_bucket,
                "unknown_count": unknown_count,
                "unknown_statuses": dict(entry["unknown_statuses"]),
                "unknown_conditions": entry["unknown_conditions"],
                "baseline_unknown": entry["baseline_unknown"],
                "correct_peer_answer_raw": entry["correct_peer_answer_raw"],
                "wrong_peer_answer_raw": entry["wrong_peer_answer_raw"],
            }
        )
    case_rows.sort(key=lambda row: (-row["unknown_count"], case_sort_key(row["case_index"])))
    rows.sort(key=lambda row: (case_sort_key(row["case_index"]), str(row["condition"])))
    return rows, case_rows, status_counts


def source_unreliable_cases(
    source_cases: Dict[str, Dict[str, Any]],
    source_audits: Dict[str, Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Counter[str]]:
    rows: List[Dict[str, Any]] = []
    reasons: Counter[str] = Counter()
    for cid, audit in source_audits.items():
        if audit.get("source_labels_semantically_reliable") is True:
            continue
        reason = source_reliability_reason(audit)
        reasons[reason] += 1
        source = source_cases.get(cid) or {}
        rows.append(
            {
                "case_index": audit.get("case_index"),
                "instance_id": audit.get("instance_id"),
                "question": source.get("question"),
                "gold_answer_raw": audit.get("gold_answer_raw"),
                "stored_gold_answer": audit.get("stored_gold_answer"),
                "reason": reason,
                "correct_peer_answer_raw": audit.get("correct_peer_answer_raw"),
                "correct_peer_semantic": audit.get("correct_peer_semantic"),
                "wrong_peer_answer_raw": audit.get("wrong_peer_answer_raw"),
                "wrong_peer_semantic": audit.get("wrong_peer_semantic"),
            }
        )
    rows.sort(key=lambda row: case_sort_key(row["case_index"]))
    return rows, reasons


def source_label_sensitive_rows(
    mode_tables: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]],
    source_audits: Dict[str, Dict[str, Any]],
    reference_mode: str,
) -> Tuple[List[Dict[str, Any]], Counter[str]]:
    rows: List[Dict[str, Any]] = []
    counts: Counter[str] = Counter()
    reference = mode_tables[reference_mode]
    for mode, table in mode_tables.items():
        if mode == reference_mode:
            continue
        for cid, ref_rows in reference.items():
            if source_audits.get(cid, {}).get("source_labels_semantically_reliable") is not True:
                continue
            for condition, ref_record in ref_rows.items():
                if condition == "no_peer":
                    continue
                other_record = table.get(cid, {}).get(condition)
                if other_record is None:
                    continue
                ref_status = condition_post_status(ref_record)
                other_status = condition_post_status(other_record)
                if ref_status["correct"] == other_status["correct"] and ref_status["transition"] == other_status["transition"]:
                    continue
                counts[f"{mode}:{condition}"] += 1
                category = sensitivity_category(
                    ref_status["transition"],
                    other_status["transition"],
                )
                rows.append(
                    {
                        "case_index": ref_record.get("case_index"),
                        "condition": condition,
                        "mode": mode,
                        "reference_mode": reference_mode,
                        "sensitivity_category": category,
                        "surface": (CONDITION_META.get(condition) or {}).get("surface"),
                        "reference": ref_status,
                        "mode_result": other_status,
                        "question": ref_record.get("question"),
                        "gold_answer_raw": ref_record.get("gold_answer_raw"),
                        "reference_output_excerpt": clip(ref_record.get("post_exposure_output"), limit=500),
                        "mode_output_excerpt": clip(other_record.get("post_exposure_output"), limit=500),
                        "reference_peer_surface_excerpt": clip(first_peer_surface(ref_record).get("text"), limit=500),
                        "mode_peer_surface_excerpt": clip(first_peer_surface(other_record).get("text"), limit=500),
                    }
                )
    rows.sort(key=lambda row: (case_sort_key(row["case_index"]), row["condition"], row["mode"]))
    return rows, counts


def sensitivity_category(reference_transition: Any, mode_transition: Any) -> str:
    pair = (reference_transition, mode_transition)
    if pair == ("right_to_wrong", "stable_right"):
        return "harm_removed"
    if pair == ("stable_right", "right_to_wrong"):
        return "harm_added"
    if pair == ("wrong_to_right", "stable_wrong"):
        return "rescue_lost"
    if pair == ("stable_wrong", "wrong_to_right"):
        return "rescue_added"
    if mode_transition == "unknown":
        return "became_unknown"
    if reference_transition == "unknown":
        return "from_unknown"
    return "other_transition_change"


def baseline_mode_drift_rows(
    mode_tables: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]],
    reference_mode: str,
) -> Tuple[List[Dict[str, Any]], Counter[str]]:
    rows: List[Dict[str, Any]] = []
    counts: Counter[str] = Counter()
    reference = mode_tables[reference_mode]
    for mode, table in mode_tables.items():
        if mode == reference_mode:
            continue
        for cid, ref_rows in reference.items():
            ref_record = ref_rows.get("no_peer")
            other_record = table.get(cid, {}).get("no_peer")
            if ref_record is None or other_record is None:
                continue
            ref_status = condition_post_status(ref_record)
            other_status = condition_post_status(other_record)
            if ref_status == other_status:
                continue
            counts[mode] += 1
            rows.append(
                {
                    "case_index": ref_record.get("case_index"),
                    "mode": mode,
                    "reference_mode": reference_mode,
                    "reference": ref_status,
                    "mode_result": other_status,
                    "question": ref_record.get("question"),
                    "gold_answer_raw": ref_record.get("gold_answer_raw"),
                }
            )
    rows.sort(key=lambda row: (case_sort_key(row["case_index"]), row["mode"]))
    return rows, counts


def source_peer_answer_raw(source_audit: Dict[str, Any], condition: str) -> Optional[str]:
    if condition.startswith("correct_"):
        return source_audit.get("correct_peer_answer_raw")
    if condition.startswith("wrong_"):
        return source_audit.get("wrong_peer_answer_raw")
    return None


def answer_only_surface_rows(
    mode_records: Dict[str, List[Dict[str, Any]]],
    source_audits: Dict[str, Dict[str, Any]],
    clean_case_ids: set[str],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for mode, records in mode_records.items():
        for record in records:
            condition = str(record.get("condition"))
            if condition not in {"correct_answer_only", "wrong_answer_only"}:
                continue
            cid = case_id(record)
            exposure = first_peer_surface(record)
            shown = exposure.get("text")
            shown_answer = None
            raw_exposures = record.get("peer_exposure") or []
            if raw_exposures:
                shown_answer = raw_exposures[0].get("answer")
            source_raw = source_peer_answer_raw(source_audits.get(cid) or {}, condition)
            equiv = math_equiv(shown_answer, source_raw)
            if equiv.correct is True:
                bucket = "equivalent"
            elif equiv.correct is False:
                bucket = "semantic_mismatch"
            else:
                bucket = "unknown_equivalence"
            is_clean = cid in clean_case_ids
            counts[f"{mode}:{bucket}"] += 1
            counts[f"all:{bucket}"] += 1
            if is_clean:
                counts[f"clean:{bucket}"] += 1
            if bucket != "equivalent":
                rows.append(
                    {
                        "case_index": record.get("case_index"),
                        "instance_id": record.get("instance_id"),
                        "mode": mode,
                        "condition": condition,
                        "clean_claim_bearing_case": is_clean,
                        "shown_answer": shown_answer,
                        "source_peer_answer_raw": source_raw,
                        "equivalence_bucket": bucket,
                        "equivalence_status": equiv.status,
                        "post_transition": record.get("transition"),
                        "post_answer_raw": record.get("post_exposure_answer_raw"),
                        "post_correct": record.get("post_exposure_correct"),
                        "gold_answer_raw": record.get("gold_answer_raw"),
                        "peer_surface_text": shown,
                        "question": record.get("question"),
                    }
                )
    rows.sort(
        key=lambda row: (
            case_sort_key(row["case_index"]),
            row["condition"],
            row["mode"],
        )
    )
    return rows, dict(counts)


def label_packet_rows(
    mode_tables: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]],
    sensitive_rows: List[Dict[str, Any]],
    source_audits: Dict[str, Dict[str, Any]],
    reference_mode: str,
) -> List[Dict[str, Any]]:
    selected: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}
    ref_table = mode_tables[reference_mode]
    for cid, rows in ref_table.items():
        if source_audits.get(cid, {}).get("source_labels_semantically_reliable") is not True:
            continue
        for condition, record in rows.items():
            if record.get("transition") not in BEHAVIOR_CHANGING_TRANSITIONS:
                continue
            selected[(reference_mode, cid, condition, "behavior_changing")] = packet_record(
                record,
                mode=reference_mode,
                reason="behavior_changing",
            )
    for row in sensitive_rows:
        cid = str(row["case_index"])
        mode = row["mode"]
        condition = row["condition"]
        record = mode_tables.get(mode, {}).get(cid, {}).get(condition)
        if record:
            selected[(mode, cid, condition, "source_label_sensitive")] = packet_record(
                record,
                mode=mode,
                reason="source_label_sensitive",
                reference=row.get("reference"),
            )
    packet = list(selected.values())
    packet.sort(key=lambda row: (case_sort_key(row["case_index"]), row["condition"], row["mode"], row["reason"]))
    return packet


def packet_record(
    record: Dict[str, Any],
    *,
    mode: str,
    reason: str,
    reference: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    condition = str(record.get("condition"))
    peer_surface = first_peer_surface(record)
    meta = CONDITION_META.get(condition) or {}
    return {
        "case_index": record.get("case_index"),
        "instance_id": record.get("instance_id"),
        "mode": mode,
        "condition": condition,
        "reason": reason,
        "surface": meta.get("surface"),
        "visible_slots": meta.get("visible_slots"),
        "hidden_slots": meta.get("hidden_slots"),
        "gold_answer_raw": record.get("gold_answer_raw"),
        "pre_answer_raw": record.get("pre_exposure_answer_raw"),
        "post_answer_raw": record.get("post_exposure_answer_raw"),
        "pre_correct": record.get("pre_exposure_correct"),
        "post_correct": record.get("post_exposure_correct"),
        "transition": record.get("transition"),
        "reference_result": reference,
        "question": record.get("question"),
        "peer_display_source": peer_surface.get("display_source"),
        "peer_original_source": peer_surface.get("original_source"),
        "peer_surface_excerpt": clip(peer_surface.get("text"), limit=1000),
        "post_output_excerpt": clip(record.get("post_exposure_output"), limit=1000),
        "labels": dict(LABEL_FIELDS),
    }


def markdown_table_row(values: List[Any]) -> str:
    return "| " + " | ".join(str(value).replace("|", "\\|") for value in values) + " |"


def count_conditions(rows: Iterable[Dict[str, Any]], key: str = "condition") -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter[str(row.get(key))] += 1
    return counter


def rate_text(metric: Optional[Dict[str, Any]]) -> str:
    if not metric:
        return "-"
    rate = metric.get("rate")
    if rate is None:
        return "-"
    return f"{metric.get('successes')}/{metric.get('total')}"


def clean_protocol_snapshot(records: List[Dict[str, Any]], clean_case_ids: set[str]) -> List[Dict[str, Any]]:
    clean_records = [record for record in records if case_id(record) in clean_case_ids]
    table = by_case_condition(clean_records)
    present_conditions = [
        condition
        for condition in CONDITIONS
        if any(condition in per_case for per_case in table.values())
    ]
    return [condition_metrics(table, condition) for condition in present_conditions]


def build_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# MATH200 Peer Claim-Hygiene Packet",
        "",
        "This packet reads saved semantic peer-exposure records. It does not run the model or recompute the protocol metrics.",
        "",
        "## Summary",
        "",
        f"- Semantic-unknown records: `{payload['counts']['semantic_unknown_records']}`",
        f"- Semantic-unknown cases: `{payload['counts']['semantic_unknown_cases']}`",
        f"- Source-label-unreliable cases: `{payload['counts']['source_label_unreliable_cases']}`",
        f"- Clean claim-bearing cases: `{payload['counts']['clean_claim_bearing_cases']}`",
        f"- Source-label-sensitive rows: `{payload['counts']['source_label_sensitive_rows']}`",
        f"- Field-label packet rows: `{payload['counts']['field_label_packet_rows']}`",
        "",
        "## Unknown Statuses",
        "",
        "| Status | Records |",
        "| --- | ---: |",
    ]
    for status, count in payload["counts"]["semantic_unknown_statuses"].items():
        lines.append(markdown_table_row([status, count]))
    lines.extend(
        [
            "",
            "## Top Semantic-Unknown Cases",
            "",
            "| Case | Gold | Unknowns | Bucket | Statuses | Conditions |",
            "| ---: | --- | ---: | --- | --- | --- |",
        ]
    )
    for row in payload["semantic_unknown_cases"][:12]:
        lines.append(
            markdown_table_row(
                [
                    row["case_index"],
                    row["gold_answer_raw"],
                    row["unknown_count"],
                    row["unknown_bucket"],
                    json.dumps(row["unknown_statuses"], ensure_ascii=False, sort_keys=True),
                    ", ".join(row["unknown_conditions"]),
                ]
            )
        )
    lines.extend(
        [
            "",
            "## Source-Label-Unreliable Reasons",
            "",
            "| Reason | Cases |",
            "| --- | ---: |",
        ]
    )
    for reason, count in payload["counts"]["source_label_unreliable_reasons"].items():
        lines.append(markdown_table_row([reason, count]))
    lines.extend(
        [
            "",
            "## Source-Label-Sensitive Rows By Condition",
            "",
            "| Mode:Condition | Rows |",
            "| --- | ---: |",
        ]
    )
    for key, count in payload["counts"]["source_label_sensitive_by_mode_condition"].items():
        lines.append(markdown_table_row([key, count]))
    lines.extend(
        [
            "",
            "Clean source-label sensitivity categories:",
            "",
            "| Category | Rows |",
            "| --- | ---: |",
        ]
    )
    for key, count in payload["counts"]["clean_source_label_sensitive_by_category"].items():
        lines.append(markdown_table_row([key, count]))
    lines.extend(
        [
            "",
            "## No-Peer Baseline Drift Across Source Modes",
            "",
            f"- Drift rows: `{payload['counts']['baseline_mode_drift_rows']}`",
            "",
            "| Mode | Rows |",
            "| --- | ---: |",
        ]
    )
    if payload["counts"]["baseline_mode_drift_by_mode"]:
        for key, count in payload["counts"]["baseline_mode_drift_by_mode"].items():
            lines.append(markdown_table_row([key, count]))
    else:
        lines.append(markdown_table_row(["none", 0]))
    lines.extend(
        [
            "",
            "## Answer-Only Surface Audit",
            "",
            "This compares the displayed answer-only slot against the raw semantic peer answer.",
            "",
            "| Bucket | Rows |",
            "| --- | ---: |",
        ]
    )
    for key, count in payload["counts"]["answer_only_surface_counts"].items():
        lines.append(markdown_table_row([key, count]))
    lines.extend(
        [
            "",
            "## Clean Claim-Bearing Subset Snapshot",
            "",
            "Clean means source-label reliable and no semantic-unknown records in the anonymous packet.",
            "",
            "| Condition | Correct / Records | Harm | Utility | Unknown |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in payload["clean_protocol_snapshot"]:
        if row["condition"] == "no_peer":
            continue
        correctness = row["correctness"]
        lines.append(
            markdown_table_row(
                [
                    row["condition"],
                    rate_text(correctness.get("record_accuracy")),
                    rate_text(row.get("harm")),
                    rate_text(row.get("utility")),
                    rate_text(correctness.get("semantic_unknown_rate")),
                ]
            )
        )
    lines.extend(
        [
            "",
            "## Field-Label Packet Preview",
            "",
            "| Case | Mode | Condition | Reason | Transition | Pre -> Post | Surface |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["field_label_packet"][:20]:
        lines.append(
            markdown_table_row(
                [
                    row["case_index"],
                    row["mode"],
                    row["condition"],
                    row["reason"],
                    row["transition"],
                    f"{row['pre_answer_raw']} -> {row['post_answer_raw']}",
                    row["surface"],
                ]
            )
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `semantic_unknown_records.jsonl`: one row per semantic-unknown record.",
            f"- `semantic_unknown_cases.jsonl`: case-level grouping of semantic unknowns.",
            f"- `source_label_unreliable_cases.jsonl`: source cases whose saved correct/wrong peer labels are not semantically reliable.",
            f"- `source_label_sensitive_rows.jsonl`: rows whose outcome changes across displayed source-label modes.",
            f"- `field_label_packet.jsonl`: behavior-changing and source-label-sensitive rows with blank manual label fields.",
            "",
            "## Reading Rule",
            "",
            "The packet is meant to shrink the next manual review surface. It should not be read as a new performance result.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    source_cases_list = read_jsonl(args.source_cases_jsonl)
    source_cases = source_case_by_id(source_cases_list)
    semantic_audit = read_json(args.semantic_audit_json)
    source_audits = source_audit_by_id(semantic_audit)

    mode_records = {
        "anonymous": read_jsonl(args.anonymous_records_jsonl),
        "named": read_jsonl(args.named_records_jsonl),
        "randomized": read_jsonl(args.randomized_records_jsonl),
    }
    mode_tables = {mode: by_case_condition(records) for mode, records in mode_records.items()}
    anonymous_records = mode_records["anonymous"]

    unknown_rows, unknown_case_rows, unknown_status_counts = unknown_records(
        anonymous_records,
        source_cases,
        source_audits,
    )
    unreliable_rows, unreliable_reason_counts = source_unreliable_cases(source_cases, source_audits)
    sensitive_rows, sensitive_counts = source_label_sensitive_rows(
        mode_tables,
        source_audits,
        args.reference_mode,
    )
    baseline_drift_rows, baseline_drift_counts = baseline_mode_drift_rows(
        mode_tables,
        args.reference_mode,
    )
    source_ids = set(source_cases)
    unknown_case_ids = {str(row["case_index"]) for row in unknown_case_rows}
    unreliable_case_ids = {str(row["case_index"]) for row in unreliable_rows}
    clean_case_ids = source_ids - unknown_case_ids - unreliable_case_ids
    packet_rows = label_packet_rows(
        mode_tables,
        sensitive_rows,
        source_audits,
        args.reference_mode,
    )
    clean_sensitive_rows = [
        row for row in sensitive_rows if str(row["case_index"]) in clean_case_ids
    ]
    answer_only_rows, answer_only_counts = answer_only_surface_rows(
        mode_records,
        source_audits,
        clean_case_ids,
    )
    return {
        "inputs": {
            "source_cases_jsonl": str(args.source_cases_jsonl),
            "semantic_audit_json": str(args.semantic_audit_json),
            "anonymous_records_jsonl": str(args.anonymous_records_jsonl),
            "named_records_jsonl": str(args.named_records_jsonl),
            "randomized_records_jsonl": str(args.randomized_records_jsonl),
            "reference_mode": args.reference_mode,
        },
        "counts": {
            "source_cases": len(source_cases_list),
            "records_by_mode": {mode: len(records) for mode, records in mode_records.items()},
            "semantic_unknown_records": len(unknown_rows),
            "semantic_unknown_cases": len(unknown_case_rows),
            "semantic_unknown_statuses": dict(unknown_status_counts),
            "source_label_unreliable_cases": len(unreliable_rows),
            "source_label_unreliable_reasons": dict(unreliable_reason_counts),
            "source_label_sensitive_rows": len(sensitive_rows),
            "source_label_sensitive_by_mode_condition": dict(sensitive_counts),
            "clean_source_label_sensitive_rows": len(clean_sensitive_rows),
            "clean_source_label_sensitive_by_category": dict(
                count_conditions(clean_sensitive_rows, key="sensitivity_category")
            ),
            "baseline_mode_drift_rows": len(baseline_drift_rows),
            "baseline_mode_drift_by_mode": dict(baseline_drift_counts),
            "clean_claim_bearing_cases": len(clean_case_ids),
            "clean_claim_bearing_records": len(clean_case_ids) * len(CONDITIONS),
            "answer_only_surface_issue_rows": len(answer_only_rows),
            "answer_only_surface_counts": answer_only_counts,
            "field_label_packet_rows": len(packet_rows),
            "field_label_reasons": dict(count_conditions(packet_rows, key="reason")),
        },
        "clean_claim_bearing_case_ids": sorted(clean_case_ids, key=case_sort_key),
        "clean_protocol_snapshot": clean_protocol_snapshot(anonymous_records, clean_case_ids),
        "semantic_unknown_cases": unknown_case_rows,
        "source_label_unreliable_cases": unreliable_rows,
        "source_label_sensitive_rows": sensitive_rows,
        "clean_source_label_sensitive_rows": clean_sensitive_rows,
        "answer_only_surface_issue_rows": answer_only_rows,
        "baseline_mode_drift_rows": baseline_drift_rows,
        "field_label_packet": packet_rows,
        "_semantic_unknown_records": unknown_rows,
    }


def write_outputs(payload: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "claim_hygiene_summary.json", {k: v for k, v in payload.items() if not k.startswith("_")})
    write_jsonl(out_dir / "semantic_unknown_records.jsonl", payload["_semantic_unknown_records"])
    write_jsonl(out_dir / "semantic_unknown_cases.jsonl", payload["semantic_unknown_cases"])
    write_jsonl(out_dir / "source_label_unreliable_cases.jsonl", payload["source_label_unreliable_cases"])
    write_jsonl(out_dir / "source_label_sensitive_rows.jsonl", payload["source_label_sensitive_rows"])
    write_jsonl(out_dir / "clean_source_label_sensitive_rows.jsonl", payload["clean_source_label_sensitive_rows"])
    write_jsonl(out_dir / "answer_only_surface_issue_rows.jsonl", payload["answer_only_surface_issue_rows"])
    write_jsonl(out_dir / "baseline_mode_drift_rows.jsonl", payload["baseline_mode_drift_rows"])
    write_jsonl(out_dir / "field_label_packet.jsonl", payload["field_label_packet"])
    (out_dir / "README.md").write_text(build_markdown(payload), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cases-jsonl", type=Path, required=True)
    parser.add_argument("--semantic-audit-json", type=Path, required=True)
    parser.add_argument("--anonymous-records-jsonl", type=Path, required=True)
    parser.add_argument("--named-records-jsonl", type=Path, required=True)
    parser.add_argument("--randomized-records-jsonl", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--reference-mode", default="anonymous", choices=["anonymous", "named", "randomized"])
    args = parser.parse_args()

    payload = build_payload(args)
    write_outputs(payload, args.out_dir)


if __name__ == "__main__":
    main()
