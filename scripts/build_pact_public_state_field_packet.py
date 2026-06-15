#!/usr/bin/env python3
"""Build a model-ready PACT public-state field intervention packet."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


DEFAULT_RUN_DIR = Path(
    "experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired"
)
DEFAULT_BRIDGE_DIR = Path("experiments/20260615-local-pact-public-state-field-bridge")
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-public-state-field-packet")


CONDITIONS = [
    {
        "condition": "question_plus_public_state_with_final",
        "axis": "final_answer_commitment",
        "include_question": True,
        "target_source": "public_action_required",
        "include_environment_state": True,
        "include_action_result": True,
        "include_final_answer": True,
        "instruction": (
            "Return only the shortest answer span for the question. "
            "Use the public fields as evidence, and correct the Final Answer "
            "Candidate if it violates the question target or evidence."
        ),
    },
    {
        "condition": "question_plus_public_state_no_final",
        "axis": "evidence_to_answer_commitment",
        "include_question": True,
        "target_source": "public_action_required",
        "include_environment_state": True,
        "include_action_result": True,
        "include_final_answer": False,
        "instruction": (
            "Return only the shortest answer span for the question using the "
            "public target and evidence fields."
        ),
    },
    {
        "condition": "question_plus_evidence_no_target_no_final",
        "axis": "target_field_ablation",
        "include_question": True,
        "target_source": "hidden",
        "include_environment_state": True,
        "include_action_result": True,
        "include_final_answer": False,
        "instruction": (
            "Return only the shortest answer span for the question using the "
            "visible evidence fields."
        ),
    },
    {
        "condition": "frozen_target_plus_evidence_no_final",
        "axis": "frozen_target_contract",
        "include_question": True,
        "target_source": "frozen_question_target",
        "include_environment_state": True,
        "include_action_result": True,
        "include_final_answer": False,
        "instruction": (
            "Return only the shortest answer span. Treat the Frozen Target "
            "Contract as the target that must be preserved."
        ),
    },
    {
        "condition": "public_target_plus_evidence_no_question_no_final",
        "axis": "public_target_sufficiency",
        "include_question": False,
        "target_source": "public_action_required",
        "include_environment_state": True,
        "include_action_result": True,
        "include_final_answer": False,
        "instruction": (
            "Return only the shortest answer span using the public target and "
            "evidence fields. The original question is intentionally hidden."
        ),
    },
]


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


def trace_by_index(path: Path) -> Dict[int, Dict[str, Any]]:
    return {
        int(row["sample_index"]): row
        for row in load_jsonl(path)
        if row.get("sample_index") is not None
    }


def bridge_by_index(path: Path) -> Dict[int, Dict[str, Any]]:
    if not path.exists():
        return {}
    return {
        int(row["sample_index"]): row
        for row in load_jsonl(path)
        if row.get("sample_index") is not None
    }


def target_by_index(path: Path) -> Dict[int, Dict[str, Any]]:
    if not path.exists():
        return {}
    return {
        int(row["sample_index"]): row
        for row in load_jsonl(path)
        if row.get("sample_index") is not None
    }


def final_event(trace: Mapping[str, Any]) -> Dict[str, Any]:
    events = list(trace.get("communication_events") or [])
    if not events:
        return {}
    for event in reversed(events):
        if event.get("is_final") or event.get("final_answer"):
            return dict(event)
    return dict(events[-1])


def field_gold_presence(event: Mapping[str, Any], gold: Any) -> Dict[str, bool]:
    return {
        "action_required": normalized_contains(event.get("action_required"), gold),
        "environment_state": normalized_contains(event.get("environment_state"), gold),
        "action_result": normalized_contains(event.get("action_result"), gold),
        "final_answer": normalized_contains(event.get("final_answer"), gold),
    }


def frozen_target(question: str) -> str:
    return f"Answer the original question exactly: {question}"


def public_state_for_condition(
    *,
    condition: Mapping[str, Any],
    question: str,
    event: Mapping[str, Any],
) -> Dict[str, Optional[str]]:
    target_source = condition["target_source"]
    if target_source == "public_action_required":
        target = event.get("action_required")
    elif target_source == "frozen_question_target":
        target = frozen_target(question)
    elif target_source == "hidden":
        target = None
    else:
        raise ValueError(f"Unknown target source: {target_source}")

    return {
        "question": question if condition["include_question"] else None,
        "action_required": str(target) if target else None,
        "environment_state": (
            str(event.get("environment_state") or "")
            if condition["include_environment_state"]
            else None
        ),
        "action_result": (
            str(event.get("action_result") or "")
            if condition["include_action_result"]
            else None
        ),
        "final_answer_candidate": (
            str(event.get("final_answer") or "")
            if condition["include_final_answer"]
            else None
        ),
    }


def render_prompt(instruction: str, state: Mapping[str, Optional[str]]) -> str:
    lines = [
        instruction,
        "",
        "Visible input:",
    ]
    labels = [
        ("question", "Question"),
        ("action_required", "Action Required"),
        ("environment_state", "Environment State"),
        ("action_result", "Action Result"),
        ("final_answer_candidate", "Final Answer Candidate"),
    ]
    for key, label in labels:
        value = state.get(key)
        if value is not None:
            lines.append(f"{label}: {value}")
    lines.extend(["", "Final answer:"])
    return "\n".join(lines)


def compact_target(target: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if not target:
        return {"target_slot_drift_candidate": False, "candidate_reasons": []}
    return {
        "target_slot_drift_candidate": bool(target.get("target_slot_drift_candidate")),
        "candidate_reasons": list(target.get("candidate_reasons") or []),
        "baseline_final_action_required": target.get("baseline_final_action_required"),
        "variant_final_action_required": target.get("variant_final_action_required"),
        "newly_lost_anchors": list(target.get("newly_lost_anchors") or []),
        "variant_introduced_risk_terms": list(target.get("variant_introduced_risk_terms") or []),
        "overlap_delta": target.get("overlap_delta"),
    }


def make_row(
    *,
    sample_index: int,
    source_run: str,
    trace: Mapping[str, Any],
    condition: Mapping[str, Any],
    bridge: Optional[Mapping[str, Any]],
    target: Optional[Mapping[str, Any]],
    packet_prefix: str,
) -> Dict[str, Any]:
    event = final_event(trace)
    question = str(trace.get("question") or "")
    gold = trace.get("gold_answer")
    public_state = public_state_for_condition(
        condition=condition,
        question=question,
        event=event,
    )
    prompt = render_prompt(str(condition["instruction"]), public_state)
    official = trace.get("final") or {}
    bridge_layer = (bridge or {}).get("bridge_layer") or "stable_right_or_not_focus"
    bridge_family = (bridge or {}).get("bridge_family") or "stable_right_or_not_focus"
    field_presence = field_gold_presence(event, gold)
    visible_field_names = [
        key for key, value in public_state.items()
        if value is not None
    ]
    packet_id = f"{packet_prefix}-{sample_index}-{source_run}-{condition['condition']}"

    return {
        "packet_id": packet_id,
        "sample_index": sample_index,
        "source_run": source_run,
        "condition": condition["condition"],
        "intervention_axis": condition["axis"],
        "visible_field_names": visible_field_names,
        "question": question,
        "gold_answer": gold,
        "official_final_answer": official.get("answer"),
        "official_correct": official.get("correct"),
        "task_regime": trace.get("task_regime"),
        "public_state_surface": (trace.get("public_state") or {}).get("surface"),
        "communication_policy": (trace.get("public_state") or {}).get("communication_policy"),
        "bridge_layer": bridge_layer,
        "bridge_family": bridge_family,
        "transition": (bridge or {}).get("transition"),
        "question_contract": (bridge or {}).get("question_contract"),
        "target_slot_diagnostic": compact_target(target),
        "source_final_event": {
            "action_required": event.get("action_required"),
            "environment_state": event.get("environment_state"),
            "action_result": event.get("action_result"),
            "final_answer": event.get("final_answer"),
        },
        "field_gold_presence_in_source_event": field_presence,
        "public_state_input": public_state,
        "prompt": prompt,
        "evaluation": {
            "gold_answer": gold,
            "expected_output": "short_answer_span_only",
            "primary_metric": "hotpotqa_exact_match_and_f1",
            "secondary_metrics": [
                "target_preservation",
                "evidence_carriage",
                "final_answer_commitment",
                "candidate_copy_or_correction",
            ],
            "gold_is_metadata_not_prompt_input": True,
        },
    }


def counter(rows: Iterable[Mapping[str, Any]], key: str) -> Dict[str, int]:
    return dict(sorted(Counter(str(row.get(key) or "") for row in rows).items()))


def nested_counter(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Counter[str]] = {}
    for row in rows:
        out.setdefault(str(row.get(outer) or ""), Counter())
        out[str(row.get(outer) or "")][str(row.get(inner) or "")] += 1
    return {
        key: dict(sorted(value.items()))
        for key, value in sorted(out.items())
    }


def sample_indices_by(rows: Iterable[Mapping[str, Any]], key: str) -> Dict[str, List[int]]:
    buckets: Dict[str, set[int]] = {}
    for row in rows:
        buckets.setdefault(str(row.get(key) or ""), set()).add(int(row["sample_index"]))
    return {
        key: sorted(values)
        for key, values in sorted(buckets.items())
    }


def render_readme(summary: Mapping[str, Any], args: argparse.Namespace) -> str:
    source_labels = list(summary["source_run_counts"].keys())
    condition_rows = [
        [condition, count, summary["condition_axis_by_condition"][condition]]
        for condition, count in summary["condition_counts"].items()
    ]
    layer_rows = [
        [layer, count, ", ".join(str(i) for i in summary["sample_indices_by_bridge_layer"][layer])]
        for layer, count in summary["bridge_layer_sample_counts"].items()
    ]
    lines = [
        "# PACT Public-State Field Packet",
        "",
        "This packet turns paired PACT HotpotQA traces into model-ready final-answer prompts.",
        "It is a setup artifact, not a model result.",
        "",
        "## Sources",
        "",
        f"- Left source `{args.baseline_source_label}`: `{args.baseline_trace}`",
        f"- Right source `{args.contract_source_label}`: `{args.contract_trace}`",
        f"- Bridge labels: `{args.bridge_cases}`",
        f"- Target diagnostics: `{args.target_slot_cases}`",
        "",
        "## Size",
        "",
        f"- Samples: `{summary['samples']}`",
        f"- Source runs: `{summary['source_run_counts']}`",
        f"- Conditions per source/sample: `{len(CONDITIONS)}`",
        f"- Prompt rows: `{summary['records']}`",
        "",
        "## Conditions",
        "",
        "| Condition | Rows | Axis |",
        "| --- | ---: | --- |",
    ]
    for condition, count, axis in condition_rows:
        lines.append(f"| `{condition}` | {count} | `{axis}` |")
    lines.extend([
        "",
        "## Bridge Coverage",
        "",
        "| Bridge layer | Samples | Sample indices |",
        "| --- | ---: | --- |",
    ])
    for layer, count, samples in layer_rows:
        lines.append(f"| `{layer}` | {count} | {samples} |")
    lines.extend([
        "",
        "## How To Use",
        "",
        "Run a model over `field_packet.jsonl`, feeding each row's `prompt` and writing back the raw output keyed by `packet_id`.",
        "Evaluate against the `evaluation.gold_answer` metadata with HotpotQA exact match/F1, then slice by `condition`, `source_run`, `bridge_layer`, `bridge_family`, and `target_slot_diagnostic.target_slot_drift_candidate`.",
        f"The source-run labels in this packet are: {', '.join(f'`{label}`' for label in source_labels)}.",
        "",
        "The intended comparisons are:",
        "",
        "- `question_plus_public_state_with_final` vs `question_plus_public_state_no_final`: does the final-answer candidate help or mislead?",
        "- `question_plus_public_state_no_final` vs `question_plus_evidence_no_target_no_final`: does the public target field add value when the original question is visible?",
        "- `question_plus_public_state_no_final` vs `frozen_target_plus_evidence_no_final`: does a question-derived frozen target repair drift or granularity failures?",
        "- `question_plus_public_state_no_final` vs `public_target_plus_evidence_no_question_no_final`: can the public target alone preserve the task when the original question is absent?",
        "",
        "## Caveat",
        "",
        "The packet uses saved PACT fields and does not retrieve external evidence. It tests answer extraction/commitment from public-state surfaces, not full HotpotQA solving from scratch.",
        "",
    ])
    return "\n".join(lines)


def render_scoring_plan(source_labels: Iterable[str]) -> str:
    labels = ", ".join(f"`{label}`" for label in source_labels)
    return "\n".join([
        "# Scoring Plan",
        "",
        "Primary score:",
        "",
        "- HotpotQA normalized exact match and token F1 against `evaluation.gold_answer`.",
        "",
        "Required slices:",
        "",
        f"- `source_run`: {labels}.",
        "- `condition`: five field visibility conditions.",
        "- `bridge_layer` and `bridge_family` from the field bridge audit.",
        "- `target_slot_diagnostic.target_slot_drift_candidate`: target-drift candidate vs non-candidate.",
        "- `field_gold_presence_in_source_event`: whether the saved source event has a gold string in action required, environment state, action result, or final answer.",
        "",
        "Secondary labels to compute after model output:",
        "",
        "- `candidate_copy`: output equals the visible `Final Answer Candidate` under normalization.",
        "- `candidate_correction`: candidate is visible, candidate is wrong, and output is correct.",
        "- `candidate_regression`: candidate is visible, candidate is correct, and output is wrong.",
        "- `target_sensitive_delta`: condition difference between public target, hidden target, and frozen target variants for the same sample/source.",
        "- `question_hidden_failure`: output changes from correct to wrong when moving from question-visible public state to public-target-only state.",
        "",
        "Do not treat this packet as a method benchmark until it is run on at least one model and compared against the saved PACT official outputs.",
        "",
    ])


def build(args: argparse.Namespace) -> Dict[str, Any]:
    baseline = trace_by_index(args.baseline_trace)
    contract = trace_by_index(args.contract_trace)
    bridge = bridge_by_index(args.bridge_cases)
    target = target_by_index(args.target_slot_cases)
    sample_indices = sorted(set(baseline) & set(contract))

    rows: List[Dict[str, Any]] = []
    for sample_index in sample_indices:
        for source_run, traces in [
            (args.baseline_source_label, baseline),
            (args.contract_source_label, contract),
        ]:
            for condition in CONDITIONS:
                rows.append(
                    make_row(
                        sample_index=sample_index,
                        source_run=source_run,
                        trace=traces[sample_index],
                        condition=condition,
                        bridge=bridge.get(sample_index),
                        target=target.get(sample_index),
                        packet_prefix=args.packet_prefix,
                    )
                )

    bridge_layer_sample_counts = {
        layer: len(samples)
        for layer, samples in sample_indices_by(rows, "bridge_layer").items()
    }
    condition_axis_by_condition = {
        str(condition["condition"]): str(condition["axis"])
        for condition in CONDITIONS
    }
    summary = {
        "records": len(rows),
        "samples": len(sample_indices),
        "sample_indices": sample_indices,
        "source_run_counts": counter(rows, "source_run"),
        "condition_counts": counter(rows, "condition"),
        "condition_axis_by_condition": condition_axis_by_condition,
        "intervention_axis_counts": counter(rows, "intervention_axis"),
        "bridge_layer_row_counts": counter(rows, "bridge_layer"),
        "bridge_family_row_counts": counter(rows, "bridge_family"),
        "bridge_layer_sample_counts": bridge_layer_sample_counts,
        "sample_indices_by_bridge_layer": sample_indices_by(rows, "bridge_layer"),
        "condition_by_source_run": nested_counter(rows, "source_run", "condition"),
        "target_slot_drift_candidate_rows": sum(
            1 for row in rows
            if row["target_slot_diagnostic"].get("target_slot_drift_candidate")
        ),
        "target_slot_drift_candidate_samples": sorted({
            int(row["sample_index"])
            for row in rows
            if row["target_slot_diagnostic"].get("target_slot_drift_candidate")
        }),
        "field_gold_presence_row_counts": {
            field: sum(
                1 for row in rows
                if row["field_gold_presence_in_source_event"].get(field)
            )
            for field in [
                "action_required",
                "environment_state",
                "action_result",
                "final_answer",
            ]
        },
        "source_paths": {
            "baseline_trace": str(args.baseline_trace),
            "contract_trace": str(args.contract_trace),
            "baseline_source_label": args.baseline_source_label,
            "contract_source_label": args.contract_source_label,
            "bridge_cases": str(args.bridge_cases),
            "target_slot_cases": str(args.target_slot_cases),
        },
        "note": (
            "Model-ready packet only. No model was run and no new accuracy "
            "claim is implied."
        ),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "field_packet.jsonl", rows)
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "README.md", render_readme(summary, args))
    write_text(args.out_dir / "scoring_plan.md", render_scoring_plan(summary["source_run_counts"].keys()))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline-trace",
        type=Path,
        default=DEFAULT_RUN_DIR / "comm_trace_pact_offset50_baseline_v11.jsonl",
    )
    parser.add_argument(
        "--contract-trace",
        type=Path,
        default=DEFAULT_RUN_DIR / "comm_trace_pact_offset50_final_contract_v11.jsonl",
    )
    parser.add_argument(
        "--bridge-cases",
        type=Path,
        default=DEFAULT_BRIDGE_DIR / "bridge_cases.jsonl",
    )
    parser.add_argument(
        "--target-slot-cases",
        type=Path,
        default=DEFAULT_RUN_DIR / "target_slot_drift_cases.jsonl",
    )
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--packet-prefix", default="pact-offset50")
    parser.add_argument("--baseline-source-label", default="baseline")
    parser.add_argument("--contract-source-label", default="final_contract")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
