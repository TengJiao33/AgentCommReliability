#!/usr/bin/env python3
"""Build standalone field-authority projection packets for PACT public state."""

from __future__ import annotations

import argparse
import json
import re
import string
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


DEFAULT_PACKET = Path("experiments/20260615-local-pact-public-state-field-packet/field_packet.jsonl")
DEFAULT_EVALUATED = Path(
    "experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/evaluation/evaluated_rows.jsonl"
)
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-field-authority-projection")

SOURCE_CONDITION = "question_plus_public_state_with_final"
BASE_CONDITION = "question_plus_public_state_no_final"
HIDE_TARGET_CONDITION = "question_plus_evidence_no_target_no_final"
FREEZE_TARGET_CONDITION = "frozen_target_plus_evidence_no_final"

SECURITY_PROJECTION_CONDITION = "security_projection_question_root_no_final"
STANDALONE_QUARANTINE_CONDITION = "standalone_authority_quarantine_no_final"

STOPWORDS = {
    "about",
    "after",
    "also",
    "among",
    "and",
    "answer",
    "are",
    "based",
    "been",
    "being",
    "both",
    "but",
    "can",
    "city",
    "did",
    "does",
    "for",
    "from",
    "give",
    "had",
    "has",
    "have",
    "his",
    "how",
    "information",
    "into",
    "its",
    "located",
    "name",
    "of",
    "on",
    "only",
    "or",
    "original",
    "provide",
    "question",
    "record",
    "required",
    "result",
    "same",
    "the",
    "their",
    "this",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "whose",
    "with",
    "year",
}

GENERIC_TARGET_RE = re.compile(
    r"\b("
    r"provide (the )?(answer|information|response)|"
    r"answer (the )?(question|based)|"
    r"final answer|"
    r"confirm|"
    r"based on (the )?(information|received|gathered)"
    r")\b",
    re.IGNORECASE,
)

AUTHORITY_VERB_RE = re.compile(
    r"\b(answer|compare|confirm|determine|find|identify|list|name|provide|state)\b",
    re.IGNORECASE,
)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
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


def normalize_answer(value: Optional[str]) -> str:
    if value is None:
        return ""

    def remove_articles(text: str) -> str:
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text: str) -> str:
        return " ".join(text.split())

    def remove_punc(text: str) -> str:
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    return white_space_fix(remove_articles(remove_punc(str(value).lower())))


def tokens(text: Any) -> List[str]:
    return re.findall(r"[a-z0-9]+", normalize_answer("" if text is None else str(text)))


def content_tokens(text: Any) -> List[str]:
    return [
        token
        for token in tokens(text)
        if token not in STOPWORDS and (len(token) >= 4 or any(ch.isdigit() for ch in token))
    ]


def token_set(text: Any) -> set[str]:
    return set(content_tokens(text))


def overlap_rate(left: set[str], right: set[str]) -> float:
    if not left:
        return 0.0
    return len(left & right) / len(left)


def frozen_target(question: str) -> str:
    return f"Answer the original question exactly: {question}"


def field_text(row: Mapping[str, Any], field: str) -> str:
    state = row.get("public_state_input") or {}
    value = state.get(field)
    return "" if value is None else str(value)


def grouped_packet(rows: Iterable[Mapping[str, Any]]) -> Dict[Tuple[int, str], Dict[str, Mapping[str, Any]]]:
    grouped: Dict[Tuple[int, str], Dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in rows:
        key = (int(row["sample_index"]), str(row["source_run"]))
        grouped[key][str(row["condition"])] = row
    return grouped


def evaluated_table(rows: Iterable[Mapping[str, Any]]) -> Dict[Tuple[int, str, str], Mapping[str, Any]]:
    return {
        (int(row["sample_index"]), str(row["source_run"]), str(row["condition"])): row
        for row in rows
    }


def authority_detector(row: Mapping[str, Any]) -> Dict[str, Any]:
    """Classify public target authority without paired target-slot diagnostics."""
    question = str(row.get("question") or "")
    action_required = field_text(row, "action_required")
    environment_state = field_text(row, "environment_state")
    action_result = field_text(row, "action_result")
    evidence_text = "\n".join([environment_state, action_result]).strip()

    question_terms = token_set(question)
    target_terms = token_set(action_required)
    evidence_terms = token_set(evidence_text)
    target_overlap = overlap_rate(question_terms, target_terms)
    evidence_anchor_overlap = overlap_rate(question_terms, evidence_terms)
    target_supported_by_evidence = overlap_rate(target_terms, evidence_terms)
    target_extra_terms = sorted(target_terms - question_terms - evidence_terms)

    reasons: List[str] = []
    if not action_required.strip():
        reasons.append("target_missing")
    if bool(GENERIC_TARGET_RE.search(action_required)) and target_overlap < 0.18:
        reasons.append("generic_low_overlap_target")
    if len(target_terms) <= 2:
        reasons.append("under_specified_target")
    if target_overlap < 0.12 and evidence_anchor_overlap < 0.12:
        reasons.append("low_question_anchor_support")
    if target_extra_terms and target_overlap < 0.24 and target_supported_by_evidence < 0.34:
        reasons.append("unsupported_target_terms")
    if not AUTHORITY_VERB_RE.search(action_required):
        reasons.append("no_explicit_answer_authority_verb")

    action = "hide" if reasons else "project_question_root"
    return {
        "target_action": action,
        "target_reasons": reasons,
        "target_overlap_with_question": round(target_overlap, 4),
        "evidence_anchor_overlap_with_question": round(evidence_anchor_overlap, 4),
        "target_overlap_with_evidence": round(target_supported_by_evidence, 4),
        "unsupported_target_terms": target_extra_terms,
        "uses_gold": False,
        "uses_target_slot_diagnostic": False,
        "trusted_root": "original_question",
        "blocked_authority_field": "public_action_required",
    }


def visible_names(state: Mapping[str, Optional[str]]) -> List[str]:
    return [
        key
        for key in [
            "question",
            "action_required",
            "environment_state",
            "action_result",
            "final_answer_candidate",
        ]
        if state.get(key) is not None
    ]


def render_prompt(instruction: str, state: Mapping[str, Optional[str]]) -> str:
    labels = [
        ("question", "Question"),
        ("action_required", "Action Required"),
        ("environment_state", "Environment State"),
        ("action_result", "Action Result"),
        ("final_answer_candidate", "Final Answer Candidate"),
    ]
    lines = [instruction, "", "Visible input:"]
    for key, label in labels:
        value = state.get(key)
        if value is not None:
            lines.append(f"{label}: {value}")
    lines.extend(["", "Final answer:"])
    return "\n".join(lines)


def make_state(
    source_row: Mapping[str, Any],
    detector: Mapping[str, Any],
    condition: str,
) -> Dict[str, Optional[str]]:
    source_state = source_row.get("public_state_input") or {}
    question = str(source_row.get("question") or "")
    if condition == SECURITY_PROJECTION_CONDITION:
        target: Optional[str] = frozen_target(question)
    elif condition == STANDALONE_QUARANTINE_CONDITION:
        target = None if detector["target_action"] == "hide" else frozen_target(question)
    else:
        raise ValueError(f"Unknown condition: {condition}")

    return {
        "question": question,
        "action_required": target,
        "environment_state": str(source_state.get("environment_state") or ""),
        "action_result": str(source_state.get("action_result") or ""),
        "final_answer_candidate": None,
    }


def make_row(
    *,
    source_row: Mapping[str, Any],
    detector: Mapping[str, Any],
    condition: str,
    instruction: str,
    axis: str,
) -> Dict[str, Any]:
    state = make_state(source_row, detector, condition)
    sample_index = int(source_row["sample_index"])
    source_run = str(source_row["source_run"])
    return {
        "packet_id": f"pact-field-authority-{sample_index}-{source_run}-{condition}",
        "source_packet_id": source_row.get("packet_id"),
        "sample_index": sample_index,
        "source_run": source_run,
        "condition": condition,
        "intervention_axis": axis,
        "task_regime": source_row.get("task_regime"),
        "communication_policy": source_row.get("communication_policy"),
        "public_state_surface": "field_authority_projection",
        "question": source_row.get("question"),
        "question_contract": source_row.get("question_contract"),
        "bridge_layer": source_row.get("bridge_layer"),
        "bridge_family": source_row.get("bridge_family"),
        "transition": source_row.get("transition"),
        "gold_answer": source_row.get("gold_answer"),
        "official_final_answer": source_row.get("official_final_answer"),
        "official_correct": source_row.get("official_correct"),
        "source_final_event": source_row.get("source_final_event"),
        "field_gold_presence_in_source_event": source_row.get("field_gold_presence_in_source_event"),
        "target_slot_diagnostic": source_row.get("target_slot_diagnostic"),
        "authority_detector": detector,
        "public_state_input": state,
        "visible_field_names": visible_names(state),
        "prompt": render_prompt(instruction, state),
        "evaluation": {
            "gold_answer": source_row.get("gold_answer"),
            "expected_output": "short_answer_span_only",
            "primary_metric": "hotpotqa_exact_match_and_f1",
            "secondary_metrics": [
                "standalone_target_authority_detector",
                "security_style_projection",
                "hotpotqa_exact_match_and_f1",
            ],
            "gold_is_metadata_not_prompt_input": True,
        },
    }


def summarize_eval_rows(rows: List[Mapping[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    exact = sum(1 for row in rows if row.get("exact_match"))
    return {
        "records": total,
        "exact_matches": exact,
        "exact_match": exact / total if total else 0.0,
        "avg_f1": sum(float(row.get("f1") or 0.0) for row in rows) / total if total else 0.0,
    }


def route_condition(strategy: str, detector: Mapping[str, Any]) -> str:
    risky = detector["target_action"] == "hide"
    if strategy == "always_base_public_state":
        return BASE_CONDITION
    if strategy == "always_hide_public_target":
        return HIDE_TARGET_CONDITION
    if strategy == "always_security_projection":
        return FREEZE_TARGET_CONDITION
    if strategy == "standalone_hide_risky_else_project":
        return HIDE_TARGET_CONDITION if risky else FREEZE_TARGET_CONDITION
    raise ValueError(f"Unknown strategy: {strategy}")


def offline_routing(
    *,
    detector_records: List[Mapping[str, Any]],
    evaluated: Mapping[Tuple[int, str, str], Mapping[str, Any]],
) -> Dict[str, Any]:
    strategies = [
        "always_base_public_state",
        "always_hide_public_target",
        "always_security_projection",
        "standalone_hide_risky_else_project",
    ]
    out: Dict[str, Any] = {}
    for strategy in strategies:
        chosen_rows: List[Mapping[str, Any]] = []
        condition_counts: Counter[str] = Counter()
        for record in detector_records:
            condition = route_condition(strategy, record["authority_detector"])
            key = (int(record["sample_index"]), str(record["source_run"]), condition)
            chosen = evaluated.get(key)
            if chosen is None:
                continue
            condition_counts[condition] += 1
            chosen_rows.append(chosen)
        out[strategy] = {
            **summarize_eval_rows(chosen_rows),
            "chosen_condition_counts": dict(sorted(condition_counts.items())),
        }
    return out


def counter(rows: Iterable[Mapping[str, Any]], key: str) -> Dict[str, int]:
    return dict(sorted(Counter(str(row.get(key) or "") for row in rows).items()))


def nested_counter(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> Dict[str, Dict[str, int]]:
    nested: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        nested[str(row.get(outer) or "")][str(row.get(inner) or "")] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(nested.items())}


def render_table(title: str, rows: Mapping[str, Mapping[str, Any]]) -> List[str]:
    lines = [
        f"## {title}",
        "",
        "| Slice | Records | EM | Avg F1 | Chosen conditions |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for key, row in rows.items():
        chosen = ", ".join(
            f"`{condition}`={count}"
            for condition, count in (row.get("chosen_condition_counts") or {}).items()
        )
        lines.append(
            "| {key} | {records} | {em:.3f} | {f1:.3f} | {chosen} |".format(
                key=key,
                records=row["records"],
                em=row["exact_match"],
                f1=row["avg_f1"],
                chosen=chosen or "n/a",
            )
        )
    lines.append("")
    return lines


def render_summary_md(summary: Mapping[str, Any]) -> str:
    lines = [
        "# PACT Field-Authority Projection Packet",
        "",
        "This artifact removes the old paired target-slot diagnostic from the gating decision.",
        "The detector uses only the original question and current public fields, then builds a security-style projection condition and a standalone quarantine condition.",
        "",
        f"- Source units: `{summary['source_units']}`",
        f"- Generated packet rows: `{summary['records']}`",
        f"- Detector actions: `{summary['detector_action_counts']}`",
        "",
    ]
    if summary["offline_routing"]:
        lines.extend(render_table("Offline Routing Scores", summary["offline_routing"]))
    else:
        lines.extend([
            "## Offline Routing Scores",
            "",
            "No evaluated rows were provided for this packet, so no offline routing audit was run.",
            "",
        ])
    lines.extend([
        "## Condition Counts",
        "",
        "| Condition | Rows |",
        "| --- | ---: |",
    ])
    for condition, count in summary["condition_counts"].items():
        lines.append(f"| `{condition}` | {count} |")
    lines.extend([
        "",
        "## Detector Reasons",
        "",
        "| Reason | Count |",
        "| --- | ---: |",
    ])
    for reason, count in summary["detector_reason_counts"].items():
        lines.append(f"| `{reason}` | {count} |")
    lines.extend([
        "",
        "## Caveats",
        "",
        "- Offline routing rows, when present, reuse already-run field-packet outputs and are diagnostic only.",
        "- `always_security_projection` maps to the earlier frozen-target condition because both use a question-derived target plus evidence.",
        "- The detector is deliberately conservative and lexical; it is a pressure object, not a semantic entailment verifier.",
        "",
    ])
    return "\n".join(lines)


def build(args: argparse.Namespace) -> Dict[str, Any]:
    packet_rows = load_jsonl(args.packet)
    packet_grouped = grouped_packet(packet_rows)
    evaluated = evaluated_table(load_jsonl(args.evaluated)) if args.evaluated.exists() else {}

    detector_records: List[Dict[str, Any]] = []
    projection_rows: List[Dict[str, Any]] = []
    for (sample_index, source_run), by_condition in sorted(packet_grouped.items()):
        source_row = by_condition.get(SOURCE_CONDITION)
        if source_row is None:
            continue
        detector = authority_detector(source_row)
        detector_records.append({
            "sample_index": sample_index,
            "source_run": source_run,
            "question": source_row.get("question"),
            "bridge_layer": source_row.get("bridge_layer"),
            "bridge_family": source_row.get("bridge_family"),
            "action_required": field_text(source_row, "action_required"),
            "environment_state": field_text(source_row, "environment_state"),
            "action_result": field_text(source_row, "action_result"),
            "authority_detector": detector,
            "old_target_slot_drift_candidate": bool(
                (source_row.get("target_slot_diagnostic") or {}).get("target_slot_drift_candidate")
            ),
        })
        projection_rows.append(
            make_row(
                source_row=source_row,
                detector=detector,
                condition=SECURITY_PROJECTION_CONDITION,
                axis="security_style_question_root_projection",
                instruction=(
                    "Return only the shortest answer span for the trusted question. "
                    "Treat the question-derived Action Required field as the only "
                    "authority field; use Environment State and Action Result only "
                    "as observations."
                ),
            )
        )
        projection_rows.append(
            make_row(
                source_row=source_row,
                detector=detector,
                condition=STANDALONE_QUARANTINE_CONDITION,
                axis="standalone_field_authority_quarantine",
                instruction=(
                    "Return only the shortest answer span for the trusted question. "
                    "If Action Required is visible, treat it as a question-derived "
                    "contract; otherwise use only the trusted question and evidence "
                    "observations."
                ),
            )
        )

    reason_counts: Counter[str] = Counter()
    for record in detector_records:
        reason_counts.update(record["authority_detector"].get("target_reasons") or ["projected"])
    offline = offline_routing(detector_records=detector_records, evaluated=evaluated) if evaluated else {}

    summary = {
        "source_units": len(detector_records),
        "records": len(projection_rows),
        "condition_counts": counter(projection_rows, "condition"),
        "condition_by_source_run": nested_counter(projection_rows, "source_run", "condition"),
        "detector_action_counts": dict(sorted(Counter(
            record["authority_detector"]["target_action"] for record in detector_records
        ).items())),
        "detector_reason_counts": dict(sorted(reason_counts.items())),
        "detector_action_by_bridge_layer": nested_counter(
            [
                {
                    "bridge_layer": record["bridge_layer"],
                    "target_action": record["authority_detector"]["target_action"],
                }
                for record in detector_records
            ],
            "bridge_layer",
            "target_action",
        ),
        "old_target_slot_candidate_by_detector_action": nested_counter(
            [
                {
                    "old_target_slot_drift_candidate": record["old_target_slot_drift_candidate"],
                    "target_action": record["authority_detector"]["target_action"],
                }
                for record in detector_records
            ],
            "old_target_slot_drift_candidate",
            "target_action",
        ),
        "offline_routing": offline,
        "paths": {
            "packet": str(args.packet),
        "evaluated": str(args.evaluated) if args.evaluated.exists() else None,
            "detector_records": str(args.out_dir / "detector_records.jsonl"),
            "projection_packet": str(args.out_dir / "projection_packet.jsonl"),
            "security_projection_packet": str(args.out_dir / "security_projection_packet.jsonl"),
            "standalone_quarantine_packet": str(args.out_dir / "standalone_quarantine_packet.jsonl"),
        },
        "note": (
            "Detector decisions use no gold answer and no paired target-slot diagnostic. "
            "Offline routing scores reuse previous pressure-run outputs."
        ),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "detector_records.jsonl", detector_records)
    write_jsonl(args.out_dir / "projection_packet.jsonl", projection_rows)
    write_jsonl(
        args.out_dir / "security_projection_packet.jsonl",
        [row for row in projection_rows if row["condition"] == SECURITY_PROJECTION_CONDITION],
    )
    write_jsonl(
        args.out_dir / "standalone_quarantine_packet.jsonl",
        [row for row in projection_rows if row["condition"] == STANDALONE_QUARANTINE_CONDITION],
    )
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "summary.md", render_summary_md(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--evaluated", type=Path, default=DEFAULT_EVALUATED)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
