#!/usr/bin/env python3
"""Build a structured verifier packet for PACT answer-contract auditing."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


DEFAULT_POSITIVE_SEED = Path(
    "experiments/20260615-local-pact-answer-contract-audit-seed/audit_seed_records.jsonl"
)
DEFAULT_NEGATIVE_SEED = Path(
    "experiments/20260615-local-pact-answer-contract-negative-controls/negative_control_seed.jsonl"
)
DEFAULT_NEGATIVE_LABELS = Path(
    "experiments/20260615-local-pact-answer-contract-negative-controls/manual_seed_labels.jsonl"
)
DEFAULT_FOCUS_DIRS = [
    Path("experiments/20260615-local-pact-field-authority-focus-offset100"),
    Path("experiments/20260615-local-pact-field-authority-focus-offset150"),
]
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-answer-contract-verifier-packet")

PRIMARY_SURFACES = [
    "answer_type_or_relation_mismatch",
    "short_span_or_granularity_mismatch",
    "public_target_misdirection",
    "evidence_sentence_or_distractor_copy",
    "question_root_ambiguity_regression",
    "evidence_or_content_failure",
    "final_candidate_attractor",
    "strict_span_or_granularity_surface",
    "no_answer_contract_failure",
]

CONTRACT_RISK_TO_SURFACE = {
    "answer_type_or_relation_mismatch": "answer_type_or_relation_mismatch",
    "short_span_or_granularity_mismatch": "short_span_or_granularity_mismatch",
    "public_target_misdirects_relation": "public_target_misdirection",
    "evidence_sentence_or_distractor_copy": "evidence_sentence_or_distractor_copy",
    "question_root_can_reopen_ambiguity": "question_root_ambiguity_regression",
}


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


def slice_name(path: Path) -> str:
    if path.name.endswith("offset100"):
        return "offset100"
    if path.name.endswith("offset150"):
        return "offset150"
    return path.name


def focus_key(row: Mapping[str, Any], current_slice: Optional[str] = None) -> Tuple[str, int, str, str]:
    return (
        str(current_slice if current_slice is not None else row.get("slice")),
        int(row["sample_index"]),
        str(row["source_run"]),
        str(row["bridge_family"]),
    )


def load_focus_cards(focus_dirs: Iterable[Path]) -> Dict[Tuple[str, int, str, str], Mapping[str, Any]]:
    cards: Dict[Tuple[str, int, str, str], Mapping[str, Any]] = {}
    for focus_dir in focus_dirs:
        current_slice = slice_name(focus_dir)
        for row in load_jsonl(focus_dir / "focus_cards.jsonl"):
            cards[focus_key(row, current_slice)] = row
    return cards


def yes_no(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"yes", "true", "1"}:
        return "yes"
    if text in {"soft"}:
        return "soft"
    return "no"


def positive_gold(row: Mapping[str, Any]) -> Dict[str, str]:
    risk = str((row.get("answer_contract_audit") or {}).get("contract_risk"))
    surface = CONTRACT_RISK_TO_SURFACE[risk]
    target_authority = "yes" if surface in {
        "answer_type_or_relation_mismatch",
        "short_span_or_granularity_mismatch",
        "public_target_misdirection",
    } else "no"
    return {
        "answer_contract_alarm": "yes",
        "target_authority_alarm": target_authority,
        "answer_type_relation_alarm": (
            "yes" if surface in {"answer_type_or_relation_mismatch", "public_target_misdirection"} else "no"
        ),
        "short_span_granularity_alarm": (
            "yes" if surface == "short_span_or_granularity_mismatch" else "no"
        ),
        "evidence_adequacy_alarm": (
            "yes" if surface in {"evidence_sentence_or_distractor_copy", "question_root_ambiguity_regression"} else "no"
        ),
        "final_candidate_alarm": "no",
        "primary_failure_surface": surface,
    }


def negative_gold(label: Mapping[str, Any]) -> Dict[str, str]:
    surface = str(label["primary_failure_surface"])
    return {
        "answer_contract_alarm": yes_no(label.get("answer_contract_alarm")),
        "target_authority_alarm": yes_no(label.get("target_authority_alarm")),
        "answer_type_relation_alarm": "no",
        "short_span_granularity_alarm": yes_no(label.get("short_span_alarm")),
        "evidence_adequacy_alarm": yes_no(label.get("evidence_adequacy_alarm")),
        "final_candidate_alarm": "yes" if surface == "final_candidate_attractor" else "no",
        "primary_failure_surface": surface,
    }


def prompt_value(value: Any) -> str:
    if value is None:
        return "[missing]"
    text = str(value).strip()
    return text if text else "[missing]"


def render_prompt(fields: Mapping[str, Any]) -> str:
    surfaces = ", ".join(PRIMARY_SURFACES)
    return "\n".join([
        "You are auditing public state fields in a multi-agent QA handoff.",
        "",
        "Decide whether the public fields are safe to use as task authority for answering the original question.",
        "Return exactly one JSON object and no extra text.",
        "",
        "Allowed JSON fields:",
        "{",
        '  "answer_contract_alarm": "yes|no",',
        '  "target_authority_alarm": "yes|no|soft",',
        '  "answer_type_relation_alarm": "yes|no",',
        '  "short_span_granularity_alarm": "yes|no",',
        '  "evidence_adequacy_alarm": "yes|no",',
        '  "final_candidate_alarm": "yes|no",',
        f'  "primary_failure_surface": "{surfaces}",',
        '  "rationale": "one short sentence"',
        "}",
        "",
        "Definitions:",
        "- answer_contract_alarm: yes if any public field can mislead answer type, relation, span, evidence adequacy, or final-answer commitment.",
        "- target_authority_alarm: yes if Action Required itself changes, narrows, or misstates the original question contract; soft if it is secondary contamination; no otherwise.",
        "- answer_type_relation_alarm: yes for wrong answer type, wrong relation, or yes/no-vs-entity mismatch.",
        "- short_span_granularity_alarm: yes for missing qualifier, over-specific sentence, or wrong requested granularity.",
        "- evidence_adequacy_alarm: yes when public evidence/result is missing, contradictory, distractor-like, or not enough for the original question.",
        "- final_candidate_alarm: yes when the final-answer candidate encourages copying, over-commitment, or wrong brevity.",
        "- primary_failure_surface must be one of the allowed surface strings.",
        "",
        "Visible public-state input:",
        f"Original Question: {prompt_value(fields.get('question'))}",
        f"Action Required: {prompt_value(fields.get('action_required'))}",
        f"Environment State: {prompt_value(fields.get('environment_state'))}",
        f"Action Result: {prompt_value(fields.get('action_result'))}",
        f"Final Answer Candidate: {prompt_value(fields.get('final_answer_candidate'))}",
    ])


def make_positive_case(row: Mapping[str, Any], focus_cards: Mapping[Tuple[str, int, str, str], Mapping[str, Any]]) -> Dict[str, Any]:
    key = focus_key(row)
    focus = focus_cards.get(key) or {}
    fields = {
        "question": row.get("question"),
        "action_required": row.get("action_required"),
        "environment_state": focus.get("environment_state"),
        "action_result": row.get("action_result"),
        "final_answer_candidate": focus.get("final_answer"),
    }
    sample_index = int(row["sample_index"])
    source_run = str(row["source_run"])
    case_id = f"positive:{row['slice']}:{sample_index}:{source_run}:{row['bridge_family']}"
    return {
        "packet_id": f"pact-answer-contract-verifier-{case_id}",
        "case_id": case_id,
        "label_source": "positive_target_layer_seed",
        "slice": row.get("slice"),
        "sample_index": sample_index,
        "source_run": source_run,
        "bridge_family": row.get("bridge_family"),
        "semantic_family": row.get("semantic_family"),
        "question": fields["question"],
        "public_state_fields": {
            "action_required": fields["action_required"],
            "environment_state": fields["environment_state"],
            "action_result": fields["action_result"],
            "final_answer_candidate": fields["final_answer_candidate"],
        },
        "prompt": render_prompt(fields),
        "gold_label": positive_gold(row),
        "gold_note": row.get("manual_note"),
        "metadata": {
            "gold_answer_hidden_from_prompt": row.get("gold_answer"),
            "contract_risk": (row.get("answer_contract_audit") or {}).get("contract_risk"),
            "observed_behavior_hidden_from_prompt": row.get("observed_behavior"),
        },
    }


def make_negative_cases(cards: List[Mapping[str, Any]], labels: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    card_by_id = {str(card["card_id"]): card for card in cards}
    cases: List[Dict[str, Any]] = []
    for label in labels:
        card_id = str(label["card_id"])
        card = card_by_id[card_id]
        event = card.get("source_final_event") or {}
        fields = {
            "question": card.get("question"),
            "action_required": event.get("action_required"),
            "environment_state": event.get("environment_state"),
            "action_result": event.get("action_result"),
            "final_answer_candidate": event.get("final_answer"),
        }
        case_id = f"negative:{card_id}:{card['control_family']}"
        cases.append({
            "packet_id": f"pact-answer-contract-verifier-{case_id}",
            "case_id": case_id,
            "label_source": "negative_control_seed",
            "slice": card.get("slice"),
            "sample_index": card.get("sample_index"),
            "source_run": card.get("source_run"),
            "control_layer": card.get("control_layer"),
            "control_family": card.get("control_family"),
            "question": fields["question"],
            "public_state_fields": {
                "action_required": fields["action_required"],
                "environment_state": fields["environment_state"],
                "action_result": fields["action_result"],
                "final_answer_candidate": fields["final_answer_candidate"],
            },
            "prompt": render_prompt(fields),
            "gold_label": negative_gold(label),
            "gold_note": label.get("note"),
            "metadata": {
                "gold_answer_hidden_from_prompt": card.get("gold_answer"),
                "conditions_hidden_from_prompt": card.get("conditions"),
                "manual_label": label,
            },
        })
    return cases


def nested_counts(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        out[str(row.get(outer))][str(row.get(inner))] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(out.items())}


def label_counts(cases: Iterable[Mapping[str, Any]], key: str) -> Dict[str, int]:
    return dict(sorted(Counter(str((case.get("gold_label") or {}).get(key)) for case in cases).items()))


def summarize(cases: List[Mapping[str, Any]], args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "records": len(cases),
        "label_source_counts": dict(sorted(Counter(str(case["label_source"]) for case in cases).items())),
        "records_by_slice": dict(sorted(Counter(str(case.get("slice")) for case in cases).items())),
        "primary_failure_surface_counts": label_counts(cases, "primary_failure_surface"),
        "answer_contract_alarm_counts": label_counts(cases, "answer_contract_alarm"),
        "target_authority_alarm_counts": label_counts(cases, "target_authority_alarm"),
        "answer_type_relation_alarm_counts": label_counts(cases, "answer_type_relation_alarm"),
        "short_span_granularity_alarm_counts": label_counts(cases, "short_span_granularity_alarm"),
        "evidence_adequacy_alarm_counts": label_counts(cases, "evidence_adequacy_alarm"),
        "final_candidate_alarm_counts": label_counts(cases, "final_candidate_alarm"),
        "primary_surface_by_label_source": nested_counts(
            [
                {
                    "label_source": case["label_source"],
                    "surface": (case.get("gold_label") or {}).get("primary_failure_surface"),
                }
                for case in cases
            ],
            "label_source",
            "surface",
        ),
        "schema": {
            "alarm_values": ["yes", "no"],
            "target_authority_values": ["yes", "no", "soft"],
            "primary_surfaces": list(PRIMARY_SURFACES),
        },
        "source_paths": {
            "positive_seed": str(args.positive_seed),
            "negative_seed": str(args.negative_seed),
            "negative_labels": str(args.negative_labels),
            "focus_dirs": [str(path) for path in args.focus_dir],
        },
        "outputs": {
            "verifier_packet": str(args.out_dir / "verifier_packet.jsonl"),
            "gold_labels": str(args.out_dir / "gold_labels.jsonl"),
            "summary": str(args.out_dir / "summary.json"),
            "scoring_plan": str(args.out_dir / "scoring_plan.md"),
        },
        "note": (
            "Prompts hide gold answers and observed behavior. Gold labels are "
            "manual/oracle labels for verifier scoring, not runtime decisions."
        ),
    }


def md_cell(value: Any) -> str:
    return " ".join(("" if value is None else str(value)).split()).replace("|", "\\|")


def render_scoring_plan(summary: Mapping[str, Any]) -> str:
    surfaces = ", ".join(f"`{item}`" for item in PRIMARY_SURFACES)
    return "\n".join([
        "# PACT Answer-Contract Verifier Packet",
        "",
        "This packet turns the positive answer-contract audit seed and the negative-control seed into model-ready verifier prompts.",
        "The prompt does not include gold answers or observed downstream behavior.",
        "",
        "## Size",
        "",
        f"- Records: `{summary['records']}`",
        f"- Label sources: `{summary['label_source_counts']}`",
        f"- Primary surfaces: `{summary['primary_failure_surface_counts']}`",
        "",
        "## Output Schema",
        "",
        "The verifier must emit one JSON object with these fields:",
        "",
        "- `answer_contract_alarm`: `yes` or `no`",
        "- `target_authority_alarm`: `yes`, `no`, or `soft`",
        "- `answer_type_relation_alarm`: `yes` or `no`",
        "- `short_span_granularity_alarm`: `yes` or `no`",
        "- `evidence_adequacy_alarm`: `yes` or `no`",
        "- `final_candidate_alarm`: `yes` or `no`",
        f"- `primary_failure_surface`: one of {surfaces}",
        "- `rationale`: one short sentence",
        "",
        "## Scoring",
        "",
        "Use `scripts/evaluate_pact_answer_contract_verifier.py` to score model outputs.",
        "Primary checks:",
        "",
        "- exact accuracy for every alarm field;",
        "- binary precision/recall/F1 where `yes` and `soft` count as positive;",
        "- primary-surface accuracy and confusion matrix;",
        "- separate positive-seed and negative-control scores.",
        "",
        "## Caveat",
        "",
        "This is a verifier benchmark packet, not evidence that a verifier works.",
        "",
    ])


def build(args: argparse.Namespace) -> Dict[str, Any]:
    focus_cards = load_focus_cards(args.focus_dir)
    positive_cases = [
        make_positive_case(row, focus_cards)
        for row in load_jsonl(args.positive_seed)
    ]
    negative_cases = make_negative_cases(
        cards=load_jsonl(args.negative_seed),
        labels=load_jsonl(args.negative_labels),
    )
    cases = sorted(
        positive_cases + negative_cases,
        key=lambda row: (
            str(row["label_source"]),
            str(row.get("slice")),
            int(row["sample_index"]),
            str(row["source_run"]),
            str(row["case_id"]),
        ),
    )
    summary = summarize(cases, args)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "verifier_packet.jsonl", cases)
    write_jsonl(
        args.out_dir / "gold_labels.jsonl",
        [
            {
                "packet_id": case["packet_id"],
                "case_id": case["case_id"],
                "label_source": case["label_source"],
                "slice": case.get("slice"),
                "sample_index": case.get("sample_index"),
                "source_run": case.get("source_run"),
                "gold_label": case["gold_label"],
                "gold_note": case.get("gold_note"),
            }
            for case in cases
        ],
    )
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "scoring_plan.md", render_scoring_plan(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--positive-seed", type=Path, default=DEFAULT_POSITIVE_SEED)
    parser.add_argument("--negative-seed", type=Path, default=DEFAULT_NEGATIVE_SEED)
    parser.add_argument("--negative-labels", type=Path, default=DEFAULT_NEGATIVE_LABELS)
    parser.add_argument("--focus-dir", type=Path, action="append", default=list(DEFAULT_FOCUS_DIRS))
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
