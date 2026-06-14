#!/usr/bin/env python3
"""Merge redacted peer-evidence records with manual relation-slot labels.

This is a local audit helper. It does not call a model. It keeps the manual
semantic labels separate from mechanical audit fields so later reports can see
which claims are hand-inspected and which rows are still only mechanically
bucketed.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_CONDITIONS = ("correct_redacted_evidence", "wrong_redacted_evidence")
ANSWER_CHANGING_TRANSITIONS = ("right_to_wrong", "wrong_to_right")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def card_id(row: Dict[str, Any]) -> str:
    return f"{row.get('case_index')}::{row.get('condition')}"


def load_label_index(paths: Optional[List[Path]]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for path in paths or []:
        for row in load_jsonl(path):
            cid = str(row.get("card_id"))
            if cid and cid != "None":
                index[cid] = row
    return index


def semantic_family(relation_label: Optional[Dict[str, Any]], contrast_label: Optional[Dict[str, Any]]) -> str:
    if relation_label:
        skeleton = str(relation_label.get("relation_skeleton"))
        if skeleton == "correct":
            return "manual_correct_relation_surface"
        if skeleton == "wrong":
            return "manual_wrong_relation_surface"
        if skeleton == "mixed":
            return "manual_mixed_relation_surface"
        if skeleton == "recoverable_wrong":
            return "manual_recoverable_wrong_surface"
        return "manual_relation_other"
    if contrast_label:
        status = str(contrast_label.get("peer_surface_status"))
        response = str(contrast_label.get("target_response"))
        if response in {"rejected_wrong_slot", "repaired_from_units", "repaired_from_question"}:
            return "contrast_wrong_slot_rejected_or_repaired"
        if response in {"adopted_wrong_slot", "adopted_wrong_relation", "followed_wrong_solution_slot", "preserved_missing_role_solution"}:
            return "contrast_wrong_surface_preserved_wrong_answer"
        if response in {"arithmetic_or_parse_drift", "post_unparseable_after_dense_surface", "post_unparseable_after_abstract_method"}:
            return "contrast_dense_or_abstract_surface_parse_drift"
        if response in {"overrode_correct_slot_with_prior_error", "preserved_flawed_pre_solution"}:
            return "contrast_correct_surface_not_rescued"
        if status in {"correct_partial_method", "correct_method_wrong_parsed_answer", "generic_correct_method", "correct_method_wrong_final", "correct_relation_wrong_final"}:
            return "contrast_wrong_final_removed_or_correct_surface"
        if status in {"correct_surface_too_thin", "correct_slot_ignored", "correct_surface_parse_unknown"}:
            return "contrast_correct_surface_nonrescue_or_unknown"
        if status in {"wrong_answer_leak_preserved_wrong", "wrong_slot_preserved_wrong"}:
            return "contrast_wrong_surface_preserved_wrong"
        if status == "wrong_surface_parse_unknown":
            return "contrast_wrong_surface_parse_unknown"
        if response in {"preserved_pre_answer_contract", "preserved_target_predicate"}:
            return "contrast_target_contract_or_predicate_guard"
        if status == "partial_correct_relation":
            return "contrast_partial_relation_filled"
        return "contrast_other"
    return "unlabeled"


def merge_record(row: Dict[str, Any], relation_labels: Dict[str, Dict[str, Any]], contrast_labels: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    cid = card_id(row)
    relation_label = relation_labels.get(cid)
    contrast_label = contrast_labels.get(cid)
    family = semantic_family(relation_label, contrast_label)
    merged = {
        "card_id": cid,
        "case_index": row.get("case_index"),
        "run_id": row.get("run_id"),
        "source_family": row.get("source_family"),
        "condition": row.get("condition"),
        "expected_correct": row.get("expected_correct"),
        "transition": row.get("transition"),
        "target_behavior": row.get("target_behavior"),
        "contact_label": row.get("contact_label"),
        "leakage_label": row.get("leakage_label"),
        "has_blank_final_slot": row.get("has_blank_final_slot"),
        "has_final_answer_phrase": row.get("has_final_answer_phrase"),
        "source_answer_redaction_count": row.get("source_answer_redaction_count"),
        "numeric_token_count": row.get("numeric_token_count"),
        "pre_exposure_answer": row.get("pre_exposure_answer"),
        "post_exposure_answer": row.get("post_exposure_answer"),
        "source_answer": row.get("source_answer"),
        "gold_answer": row.get("gold_answer"),
        "evidence_text": row.get("evidence_text"),
        "manual_label_source": "relation_slot" if relation_label else "contrast" if contrast_label else "none",
        "semantic_family": family,
        "relation_slot_label": (relation_label or {}).get("relation_slot_label"),
        "relation_skeleton": (relation_label or {}).get("relation_skeleton"),
        "numeric_slots": (relation_label or {}).get("numeric_slots"),
        "final_slot": (relation_label or {}).get("final_slot"),
        "answer_copy": (relation_label or {}).get("answer_copy"),
        "target_predicate_preserved": (relation_label or {}).get("target_predicate_preserved"),
        "contrast_label": (contrast_label or {}).get("contrast_label"),
        "peer_surface_status": (contrast_label or {}).get("peer_surface_status"),
        "target_response": (contrast_label or {}).get("target_response"),
        "semantic_note": (relation_label or contrast_label or {}).get("semantic_note"),
    }
    return merged


def count_by(rows: Iterable[Dict[str, Any]], field: str) -> Dict[str, int]:
    return dict(Counter(str(row.get(field)) for row in rows))


def nested_count(rows: Iterable[Dict[str, Any]], outer: str, inner: str) -> Dict[str, Dict[str, int]]:
    buckets: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        buckets[str(row.get(outer))][str(row.get(inner))] += 1
    return {key: dict(counter) for key, counter in sorted(buckets.items())}


def write_unlabeled_packet(path: Path, rows: List[Dict[str, Any]], limit: int) -> None:
    lines = [
        "# Unlabeled Redacted Peer Evidence Records",
        "",
        f"Rows shown: `{min(limit, len(rows))}` of `{len(rows)}`",
        "",
    ]
    for row in rows[:limit]:
        lines += [
            f"## {row['card_id']}",
            "",
            f"- Condition: `{row['condition']}`",
            f"- Transition: `{row['transition']}`",
            f"- Target behavior: `{row['target_behavior']}`",
            f"- Contact label: `{row['contact_label']}`",
            f"- Answers: pre `{row['pre_exposure_answer']}` -> post `{row['post_exposure_answer']}`; source `{row['source_answer']}`; gold `{row['gold_answer']}`",
            f"- Leakage: `{row['leakage_label']}`; blank slot `{row['has_blank_final_slot']}`",
            "",
            "Evidence:",
            "",
            str(row.get("evidence_text") or ""),
            "",
        ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_labeling_rubric(path: Path) -> None:
    lines = [
        "# Peer Relation-Slot Labeling Rubric",
        "",
        "Use this as a compact checklist for the next redacted peer-evidence slice.",
        "Labels are semantic notes over saved traces, not model judgments.",
        "",
        "## Relation-Slot Labels",
        "",
        "| Field | Suggested values | Question |",
        "| --- | --- | --- |",
        "| `relation_skeleton` | `correct`, `wrong`, `mixed`, `recoverable_wrong` | Does the evidence preserve the right relation among quantities, roles, or theorem objects? |",
        "| `numeric_slots` | `correct`, `wrong`, `mixed`, `abstract`, `missing_required_role` | Are the numbers and role bindings right, wrong, mixed, absent, or missing a needed multiplicative/additive role? |",
        "| `final_slot` | `absent`, `blank`, `derivable`, `leaked` | Is the final answer absent, explicitly blanked, reconstructable from the surface, or directly present? |",
        "| `answer_copy` | `relation_derived`, `relation_derived_not_source_copy`, `source_answer_copied_or_derived`, `repaired`, `none` | Did the target copy, derive, repair, or ignore the source answer? |",
        "",
        "## Contrast / Non-Rescue Labels",
        "",
        "| Field | Suggested values | Question |",
        "| --- | --- | --- |",
        "| `peer_surface_status` | `correct_partial_method`, `correct_method_wrong_final`, `correct_relation_wrong_final`, `wrong_numeric_slot`, `wrong_numeric_role`, `wrong_relation_surface`, `wrong_solution_slot`, `missing_multiplicative_role`, `underspecified_correct_relation`, `dense_correct_condition`, `abstract_correct_method` | What kind of surface did the extractor leave behind? |",
        "| `target_response` | `adopted_correct_surface`, `completed_correct_method`, `rejected_wrong_slot`, `repaired_from_question`, `repaired_from_units`, `adopted_wrong_slot`, `adopted_wrong_relation`, `preserved_missing_role_solution`, `overrode_correct_slot_with_prior_error`, `preserved_flawed_pre_solution`, `post_unparseable_after_dense_surface` | How did the target respond to that surface? |",
        "",
        "## Minimal Note",
        "",
        "Each row should include one short `semantic_note` tying the label to a concrete slot in the evidence text and to the target's post-exposure output.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def summarize(rows: List[Dict[str, Any]], args: argparse.Namespace) -> Dict[str, Any]:
    labeled = [row for row in rows if row["manual_label_source"] != "none"]
    unlabeled = [row for row in rows if row["manual_label_source"] == "none"]
    answer_changing = [row for row in rows if row.get("transition") in ANSWER_CHANGING_TRANSITIONS]
    answer_changing_unlabeled = [row for row in answer_changing if row["manual_label_source"] == "none"]
    return {
        "audit_cases_jsonl": str(args.audit_cases_jsonl),
        "conditions": list(args.conditions),
        "records": len(rows),
        "manual_labeled_records": len(labeled),
        "unlabeled_records": len(unlabeled),
        "answer_changing_transition_labels": list(ANSWER_CHANGING_TRANSITIONS),
        "answer_changing_records": len(answer_changing),
        "answer_changing_manual_labeled_records": len(answer_changing) - len(answer_changing_unlabeled),
        "answer_changing_unlabeled_records": len(answer_changing_unlabeled),
        "answer_changing_manual_coverage_complete": len(answer_changing_unlabeled) == 0,
        "answer_changing_unlabeled_card_ids": [str(row["card_id"]) for row in answer_changing_unlabeled],
        "unlabeled_all_preserved_correct_stable_right": all(
            row.get("transition") == "stable_right" and row.get("target_behavior") == "preserved_correct_answer"
            for row in unlabeled
        ),
        "manual_label_source_counts": count_by(rows, "manual_label_source"),
        "semantic_family_counts": count_by(rows, "semantic_family"),
        "condition_counts": count_by(rows, "condition"),
        "transition_counts": count_by(rows, "transition"),
        "target_behavior_counts": count_by(rows, "target_behavior"),
        "contact_label_counts": count_by(rows, "contact_label"),
        "semantic_family_by_target_behavior": nested_count(rows, "semantic_family", "target_behavior"),
        "semantic_family_by_transition": nested_count(rows, "semantic_family", "transition"),
        "manual_coverage_by_condition": nested_count(rows, "condition", "manual_label_source"),
        "unlabeled_transition_counts": count_by(unlabeled, "transition"),
        "unlabeled_condition_counts": count_by(unlabeled, "condition"),
        "unlabeled_by_target_behavior": count_by(unlabeled, "target_behavior"),
        "unlabeled_by_contact_label": count_by(unlabeled, "contact_label"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-cases-jsonl", type=Path, required=True)
    parser.add_argument("--manual-labels", type=Path, nargs="*", default=[])
    parser.add_argument("--manual-contrast-labels", type=Path, nargs="*", default=[])
    parser.add_argument("--conditions", nargs="*", default=list(DEFAULT_CONDITIONS))
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--unlabeled-packet-limit", type=int, default=60)
    args = parser.parse_args()

    relation_labels = load_label_index(args.manual_labels)
    contrast_labels = load_label_index(args.manual_contrast_labels)
    conditions = set(args.conditions)
    audit_rows = [row for row in load_jsonl(args.audit_cases_jsonl) if row.get("condition") in conditions]
    merged = [merge_record(row, relation_labels, contrast_labels) for row in audit_rows]
    merged.sort(key=lambda row: (str(row["condition"]), str(row["target_behavior"]), int(row["case_index"])))
    unlabeled = [row for row in merged if row["manual_label_source"] == "none"]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "redacted_relation_slot_records.jsonl", merged)
    write_jsonl(args.out_dir / "unlabeled_redacted_records.jsonl", unlabeled)
    write_unlabeled_packet(args.out_dir / "unlabeled_packet.md", unlabeled, args.unlabeled_packet_limit)
    write_labeling_rubric(args.out_dir / "labeling_rubric.md")
    summary = summarize(merged, args)
    write_json(args.out_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
