#!/usr/bin/env python3
"""Bridge PACT public-state failures into the field/slot hypothesis language."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_RUN_DIR = Path(
    "experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired"
)
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-public-state-field-bridge")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize(text: Any) -> str:
    text = "" if text is None else str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def normalized_contains(haystack: Any, needle: Any) -> bool:
    haystack_norm = normalize(haystack)
    needle_norm = normalize(needle)
    return bool(needle_norm) and needle_norm in haystack_norm


def manual_bridge(manual_family: str) -> Tuple[str, str, str]:
    if manual_family == "missing_required_token_or_qualifier":
        return (
            "final_answer_commitment",
            "missing_required_token_or_qualifier",
            "The public state keeps the core answer, but the final answer drops a required qualifier or token.",
        )
    if manual_family == "wrong_answer_type_or_slot":
        return (
            "target_final_alignment",
            "wrong_answer_type_or_slot",
            "The public state contains nearby evidence, but the final answer commits to the wrong answer type or slot.",
        )
    if manual_family == "over_specific_answer":
        return (
            "final_answer_commitment",
            "over_specific_answer",
            "The final answer includes the desired span plus lower-level or extra material.",
        )
    if manual_family == "alias_or_name_granularity":
        return (
            "final_answer_commitment",
            "alias_or_name_granularity",
            "The final answer is semantically close but uses the wrong name granularity for strict HotpotQA EM.",
        )
    if manual_family == "false_positive_string_signal":
        return (
            "diagnostic_noise",
            "false_positive_string_signal",
            "A mechanical gold-string check overcredited the public state; this is a warning about the diagnostic.",
        )
    return (
        "final_answer_commitment",
        manual_family,
        "Manual label points to a final answer commitment or granularity issue.",
    )


def classify_bridge(
    case: Dict[str, Any],
    manual: Optional[Dict[str, Any]],
    target: Optional[Dict[str, Any]],
) -> Tuple[str, str, str]:
    transition = str(case.get("transition") or "")
    atlas_label = str(case.get("atlas_label") or "")
    target_candidate = bool(target and target.get("target_slot_drift_candidate"))

    if manual:
        return manual_bridge(str(manual.get("manual_family") or "manual_label"))

    if transition == "wrong_to_right":
        if atlas_label == "contract_rescued_verbose_surface":
            return (
                "positive_contract_rescue",
                "contract_rescued_verbose_surface",
                "A stricter final-answer contract converts a verbose or sentence-shaped answer into the required span.",
            )
        return (
            "positive_contract_rescue",
            "contract_rescued_content_or_field",
            "The contract run recovers the final answer, possibly by changing content or field use.",
        )

    if transition == "right_to_wrong":
        if atlas_label == "content_drift_regression" and target_candidate:
            return (
                "target_contract",
                "target_migration_regression",
                "The public target migrates toward a distractor slot, and the final answer follows it.",
            )
        if atlas_label == "content_drift_regression":
            return (
                "evidence_carriage",
                "content_drift_regression",
                "The final public state no longer carries the right content for the original question.",
            )
        if atlas_label == "strict_span_regression" and target_candidate:
            return (
                "final_answer_commitment",
                "strict_span_regression_with_soft_target_shift",
                "The answer remains near the gold span, but the public target also shows a soft lexical shift.",
            )
        return (
            "final_answer_commitment",
            "strict_span_regression",
            "The content is close, but strict span or surface details regress.",
        )

    if transition == "stable_wrong":
        if atlas_label == "recoverable_from_public_state_policy":
            return (
                "final_answer_commitment",
                "recoverable_from_public_state_policy",
                "A simple public-state arbitration policy can recover the answer, suggesting the evidence is already present.",
            )
        if atlas_label == "near_miss_surface_or_span":
            return (
                "final_answer_commitment",
                "near_miss_surface_or_span",
                "The answer is near enough to expose a surface/span contract problem.",
            )
        if target_candidate:
            return (
                "target_contract",
                "target_under_specification_or_anchor_loss",
                "The final Action Required loses anchors or becomes too generic to preserve the original target.",
            )
        if atlas_label == "likely_evidence_or_reasoning_failure":
            return (
                "evidence_carriage",
                "likely_evidence_or_reasoning_failure",
                "The saved public state does not expose enough recoverable evidence for the gold answer.",
            )
        if atlas_label == "final_public_state_contains_gold":
            return (
                "final_answer_commitment",
                "public_state_to_final_answer_failure",
                "The gold string is visible somewhere in the final public state, but the final answer does not commit to it.",
            )

    return (
        "unclassified",
        atlas_label or transition or "unknown",
        "No bridge label was assigned.",
    )


def gold_field_presence(case: Dict[str, Any]) -> Dict[str, bool]:
    event = case.get("final_event") or {}
    gold = case.get("gold_answer")
    return {
        "action_required": normalized_contains(event.get("action_required"), gold),
        "environment_state": normalized_contains(event.get("environment_state"), gold),
        "action_result": normalized_contains(event.get("action_result"), gold),
        "final_answer": normalized_contains(event.get("final_answer"), gold),
    }


def compact_target(target: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not target:
        return {
            "target_slot_drift_candidate": False,
            "candidate_reasons": [],
        }
    keys = [
        "target_slot_drift_candidate",
        "candidate_reasons",
        "baseline_final_action_required",
        "variant_final_action_required",
        "baseline_question_overlap",
        "variant_question_overlap",
        "overlap_delta",
        "newly_lost_anchors",
        "variant_introduced_risk_terms",
        "variant_missing_question_terms",
    ]
    return {key: target.get(key) for key in keys}


def bridge_case(
    case: Dict[str, Any],
    manual: Optional[Dict[str, Any]],
    target: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    bridge_layer, bridge_family, bridge_read = classify_bridge(case, manual, target)
    event = case.get("final_event") or {}
    return {
        "sample_index": case.get("sample_index"),
        "transition": case.get("transition"),
        "atlas_label": case.get("atlas_label"),
        "bridge_layer": bridge_layer,
        "bridge_family": bridge_family,
        "bridge_read": bridge_read,
        "question_contract": case.get("question_contract"),
        "question": case.get("question"),
        "gold_answer": case.get("gold_answer"),
        "baseline_correct": case.get("baseline_correct"),
        "variant_correct": case.get("variant_correct"),
        "baseline_f1": case.get("baseline_f1"),
        "variant_f1": case.get("variant_f1"),
        "f1_delta": case.get("f1_delta"),
        "baseline_final_answer_text": case.get("baseline_final_answer_text"),
        "variant_final_answer_text": case.get("variant_final_answer_text"),
        "gold_field_presence": gold_field_presence(case),
        "manual_family": (manual or {}).get("manual_family"),
        "manual_label": (manual or {}).get("manual_label"),
        "manual_note": (manual or {}).get("note"),
        "target_slot": compact_target(target),
        "final_event": {
            "action_required": event.get("action_required"),
            "environment_state": event.get("environment_state"),
            "action_result": event.get("action_result"),
            "final_answer": event.get("final_answer"),
        },
    }


def counter_by(rows: Iterable[Dict[str, Any]], key: str) -> Dict[str, int]:
    return dict(sorted(Counter(str(row.get(key) or "") for row in rows).items()))


def sample_indices_by(rows: Iterable[Dict[str, Any]], key: str) -> Dict[str, List[int]]:
    buckets: Dict[str, List[int]] = {}
    for row in rows:
        buckets.setdefault(str(row.get(key) or ""), []).append(int(row["sample_index"]))
    return dict(sorted(buckets.items()))


def transition_by_family(rows: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Counter[str]] = {}
    for row in rows:
        family = str(row.get("bridge_family") or "")
        out.setdefault(family, Counter())
        out[family][str(row.get("transition") or "")] += 1
    return {
        family: dict(sorted(counter.items()))
        for family, counter in sorted(out.items())
    }


def render_table(headers: List[str], rows: List[List[Any]]) -> str:
    rendered = ["| " + " | ".join(headers) + " |"]
    rendered.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        rendered.append("| " + " | ".join(str(item) for item in row) + " |")
    return "\n".join(rendered)


def render_packet(summary: Dict[str, Any], rows: List[Dict[str, Any]], args: argparse.Namespace) -> str:
    layer_rows = [
        [layer, count, ", ".join(str(i) for i in summary["sample_indices_by_layer"][layer])]
        for layer, count in summary["bridge_layer_counts"].items()
    ]
    family_rows = [
        [family, count, ", ".join(str(i) for i in summary["sample_indices_by_family"][family])]
        for family, count in summary["bridge_family_counts"].items()
    ]
    target_rows = [
        [
            row["sample_index"],
            row["transition"],
            row["bridge_family"],
            ", ".join(row["target_slot"].get("candidate_reasons") or []),
        ]
        for row in rows
        if row["target_slot"].get("target_slot_drift_candidate")
    ]
    manual_rows = [
        [
            row["sample_index"],
            row["manual_family"],
            row["bridge_layer"],
            row["bridge_family"],
        ]
        for row in rows
        if row.get("manual_family")
    ]

    return "\n".join([
        "# PACT Public-State Field Bridge",
        "",
        "## Reading",
        "",
        "This is an offline bridge audit over the PACT HotpotQA offset50 focus cases.",
        "It reframes older PACT findings in the same field/slot language used by the peer-message work.",
        "",
        "Main read: the object is not typed public state itself. The object is field-level public-state reliability: preserve the target contract, carry evidence without distractor migration, and commit the final answer to the requested slot and granularity.",
        "",
        "## Sources",
        "",
        f"- `{args.atlas_focus}`",
        f"- `{args.manual_public_state_labels}`",
        f"- `{args.target_slot_cases}`",
        "",
        "## Counts",
        "",
        f"- Focus cases: `{summary['records']}`",
        f"- Manual public-state-gold labels merged: `{summary['manual_label_count']}`",
        f"- Target-slot drift candidates merged: `{summary['target_slot_drift_candidate_count']}`",
        "",
        render_table(["Bridge layer", "Count", "Samples"], layer_rows),
        "",
        render_table(["Bridge family", "Count", "Samples"], family_rows),
        "",
        "## Target Candidates",
        "",
        render_table(["Sample", "Transition", "Bridge family", "Reasons"], target_rows),
        "",
        "## Manual Public-State-Gold Cases",
        "",
        render_table(["Sample", "Manual family", "Bridge layer", "Bridge family"], manual_rows),
        "",
        "## Implication",
        "",
        "The useful next move is a communication-necessity benchmark or intervention around field preservation, not another small typed/MATH variant. PACT already gives the larger surface: information is split, public fields are passed across agents, and failures happen at target, evidence, and final-commitment layers.",
        "",
        "## Caveats",
        "",
        "- This is a re-read of one saved 50-sample PACT slice, not a new model result.",
        "- Bridge labels combine mechanical atlas labels, a ten-case manual audit, and a lexical target-slot diagnostic.",
        "- Target-slot candidates remain heuristic; sample-level labels are inspection handles, not final taxonomy.",
        "",
    ])


def build(args: argparse.Namespace) -> Dict[str, Any]:
    focus_cases = load_jsonl(args.atlas_focus)
    manual_by_index = {
        int(row["sample_index"]): row
        for row in load_jsonl(args.manual_public_state_labels)
        if row.get("sample_index") is not None
    }
    target_by_index = {
        int(row["sample_index"]): row
        for row in load_jsonl(args.target_slot_cases)
        if row.get("sample_index") is not None
    }

    rows = [
        bridge_case(
            case,
            manual_by_index.get(int(case["sample_index"])),
            target_by_index.get(int(case["sample_index"])),
        )
        for case in focus_cases
    ]
    target_candidates = [
        row for row in rows
        if row["target_slot"].get("target_slot_drift_candidate")
    ]
    manual_rows = [row for row in rows if row.get("manual_family")]

    summary = {
        "records": len(rows),
        "transition_counts": counter_by(rows, "transition"),
        "atlas_label_counts": counter_by(rows, "atlas_label"),
        "bridge_layer_counts": counter_by(rows, "bridge_layer"),
        "bridge_family_counts": counter_by(rows, "bridge_family"),
        "transition_by_bridge_family": transition_by_family(rows),
        "sample_indices_by_layer": sample_indices_by(rows, "bridge_layer"),
        "sample_indices_by_family": sample_indices_by(rows, "bridge_family"),
        "manual_label_count": len(manual_rows),
        "manual_family_counts": counter_by(manual_rows, "manual_family"),
        "target_slot_drift_candidate_count": len(target_candidates),
        "target_slot_drift_candidate_indices": [
            row["sample_index"] for row in target_candidates
        ],
        "target_slot_drift_candidates_by_transition": counter_by(target_candidates, "transition"),
        "source_paths": {
            "atlas_focus": str(args.atlas_focus),
            "manual_public_state_labels": str(args.manual_public_state_labels),
            "target_slot_cases": str(args.target_slot_cases),
        },
        "interpretation": (
            "Field-level public-state reliability is the larger object: target "
            "contract preservation, evidence carriage, and final-answer "
            "commitment explain the PACT focus cases better than another typed "
            "public-state mini-variant."
        ),
        "note": (
            "Offline re-read only; bridge labels are inspection handles over a "
            "single saved 50-sample HotpotQA offset slice."
        ),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "bridge_cases.jsonl", rows)
    write_text(args.out_dir / "bridge_packet.md", render_packet(summary, rows, args))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--atlas-focus",
        type=Path,
        default=DEFAULT_RUN_DIR / "case_atlas_focus_cases.jsonl",
    )
    parser.add_argument(
        "--manual-public-state-labels",
        type=Path,
        default=DEFAULT_RUN_DIR / "public_state_gold_manual_labels.jsonl",
    )
    parser.add_argument(
        "--target-slot-cases",
        type=Path,
        default=DEFAULT_RUN_DIR / "target_slot_drift_cases.jsonl",
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
