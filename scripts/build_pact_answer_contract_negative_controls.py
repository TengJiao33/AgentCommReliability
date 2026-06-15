#!/usr/bin/env python3
"""Build negative-control cards for the PACT answer-contract audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


DEFAULT_BRIDGE_INPUTS = [
    (
        "offset100",
        Path("experiments/20260615-local-pact-public-state-field-bridge-offset100/bridge_cases.jsonl"),
    ),
    (
        "offset150",
        Path("experiments/20260615-local-pact-public-state-field-bridge-offset150/bridge_cases.jsonl"),
    ),
]
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-answer-contract-negative-controls")
DEFAULT_CONTROL_LAYERS = [
    "stable_answer",
    "evidence_or_content",
    "final_answer_commitment",
]

CONDITION_NAMES = {
    "base_public_state_no_final": "question_plus_public_state_no_final",
    "frozen_question_target": "frozen_target_plus_evidence_no_final",
    "hide_public_target": "question_plus_evidence_no_target_no_final",
    "public_target_only": "public_target_plus_evidence_no_question_no_final",
    "with_final_candidate": "question_plus_public_state_with_final",
}

LAYER_EXPECTATIONS = {
    "stable_answer": {
        "primary_control_read": (
            "Stable-right public-state unit. A selective answer-contract audit "
            "should usually stay quiet here."
        ),
        "expected_primary_surface": "no_answer_contract_failure",
        "target_authority_alarm_expected": False,
        "short_span_alarm_expected": False,
        "evidence_adequacy_alarm_expected": False,
    },
    "evidence_or_content": {
        "primary_control_read": (
            "Evidence/content mismatch unit. A target-answer-contract audit may "
            "need an evidence adequacy guard, but should not explain the case as "
            "target authority by default."
        ),
        "expected_primary_surface": "evidence_or_content_failure",
        "target_authority_alarm_expected": False,
        "short_span_alarm_expected": False,
        "evidence_adequacy_alarm_expected": True,
    },
    "final_answer_commitment": {
        "primary_control_read": (
            "Final-answer commitment or strict-span unit. This is an adjacent "
            "answer-surface control; target-authority checks should not claim it "
            "unless the public target itself is wrong."
        ),
        "expected_primary_surface": "final_answer_commitment_or_span_surface",
        "target_authority_alarm_expected": False,
        "short_span_alarm_expected": "family_dependent",
        "evidence_adequacy_alarm_expected": False,
    },
}

FAMILY_EXPECTATIONS = {
    "strict_span_or_granularity_failure": {
        "expected_primary_surface": "strict_span_or_granularity_surface",
        "short_span_alarm_expected": True,
    },
    "final_candidate_attractor_regression": {
        "expected_primary_surface": "final_candidate_attractor",
        "short_span_alarm_expected": False,
    },
    "final_candidate_rescue": {
        "expected_primary_surface": "final_candidate_helpful_commitment",
        "short_span_alarm_expected": False,
    },
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


def parse_bridge_inputs(items: Sequence[str] | None) -> List[Tuple[str, Path]]:
    if not items:
        return list(DEFAULT_BRIDGE_INPUTS)
    parsed: List[Tuple[str, Path]] = []
    for item in items:
        if "=" not in item:
            raise ValueError(f"Expected --bridge-cases slice=path, got: {item}")
        label, raw_path = item.split("=", 1)
        label = label.strip()
        if not label:
            raise ValueError(f"Empty slice label in --bridge-cases: {item}")
        parsed.append((label, Path(raw_path)))
    return parsed


def condition(row: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    return (row.get("conditions") or {}).get(name) or {}


def compact_condition(row: Mapping[str, Any], name: str) -> Dict[str, Any]:
    data = condition(row, name)
    return {
        "correct": bool(data.get("correct")),
        "prediction": data.get("prediction"),
        "f1": data.get("f1"),
        "span_error_family": data.get("span_error_family"),
    }


def compact_signals(row: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    signals: Dict[str, Dict[str, Any]] = {}
    for signal in row.get("signals") or []:
        name = str(signal.get("name"))
        signals[name] = {
            "outcome": signal.get("outcome"),
            "before_prediction": signal.get("before_prediction"),
            "after_prediction": signal.get("after_prediction"),
            "before_correct": bool(signal.get("before_correct")),
            "after_correct": bool(signal.get("after_correct")),
        }
    return signals


def selectivity_expectation(row: Mapping[str, Any]) -> Dict[str, Any]:
    layer = str(row.get("bridge_layer"))
    family = str(row.get("bridge_family"))
    expectation = dict(LAYER_EXPECTATIONS.get(layer, {}))
    expectation.update(FAMILY_EXPECTATIONS.get(family, {}))
    return expectation


def make_card(row: Mapping[str, Any], current_slice: str) -> Dict[str, Any]:
    event = row.get("source_final_event") or {}
    target_slot = row.get("target_slot_diagnostic") or {}
    return {
        "card_id": f"{current_slice}:{row.get('sample_index')}:{row.get('source_run')}",
        "slice": current_slice,
        "sample_index": row.get("sample_index"),
        "source_run": row.get("source_run"),
        "control_layer": row.get("bridge_layer"),
        "control_family": row.get("bridge_family"),
        "bridge_read": row.get("bridge_read"),
        "question": row.get("question"),
        "gold_answer": row.get("gold_answer"),
        "source_final_event": {
            "action_required": event.get("action_required"),
            "environment_state": event.get("environment_state"),
            "action_result": event.get("action_result"),
            "final_answer": event.get("final_answer"),
        },
        "conditions": {
            label: compact_condition(row, source_name)
            for label, source_name in CONDITION_NAMES.items()
        },
        "signals": compact_signals(row),
        "target_slot_drift_candidate": bool(row.get("target_slot_drift_candidate")),
        "target_slot_candidate_reasons": list(target_slot.get("candidate_reasons") or []),
        "selectivity_expectation": selectivity_expectation(row),
        "manual_label_template": {
            "answer_contract_alarm": None,
            "target_authority_alarm": None,
            "short_span_alarm": None,
            "evidence_adequacy_alarm": None,
            "primary_failure_surface": None,
            "note": "",
        },
    }


def build_cards(bridge_inputs: Iterable[Tuple[str, Path]], control_layers: set[str]) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for current_slice, path in bridge_inputs:
        for row in load_jsonl(path):
            if str(row.get("bridge_layer")) in control_layers:
                cards.append(make_card(row, current_slice))
    return sorted(
        cards,
        key=lambda row: (
            str(row["slice"]),
            str(row["control_layer"]),
            int(row["sample_index"]),
            str(row["source_run"]),
            str(row["control_family"]),
        ),
    )


def build_seed(cards: Iterable[Mapping[str, Any]], per_layer_per_slice: int) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str], List[Mapping[str, Any]]] = defaultdict(list)
    for card in cards:
        grouped[(str(card["slice"]), str(card["control_layer"]))].append(card)

    seed: List[Dict[str, Any]] = []
    for key in sorted(grouped):
        rows = sorted(
            grouped[key],
            key=lambda row: (int(row["sample_index"]), str(row["source_run"]), str(row["control_family"])),
        )
        seed.extend(dict(row) for row in rows[:per_layer_per_slice])
    return seed


def nested_counts(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        out[str(row.get(outer))][str(row.get(inner))] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(out.items())}


def expectation_counts(rows: Iterable[Mapping[str, Any]], key: str) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        expectation = row.get("selectivity_expectation") or {}
        counter[str(expectation.get(key))] += 1
    return dict(sorted(counter.items()))


def summarize(
    cards: List[Mapping[str, Any]],
    seed: List[Mapping[str, Any]],
    bridge_inputs: Sequence[Tuple[str, Path]],
    control_layers: Sequence[str],
    per_layer_per_slice: int,
) -> Dict[str, Any]:
    return {
        "cards": len(cards),
        "seed_cards": len(seed),
        "unique_sample_units": len(
            {
                (str(card["slice"]), int(card["sample_index"]), str(card["source_run"]))
                for card in cards
            }
        ),
        "slices": dict(sorted(Counter(str(card["slice"]) for card in cards).items())),
        "control_layer_counts": dict(sorted(Counter(str(card["control_layer"]) for card in cards).items())),
        "control_family_counts": dict(sorted(Counter(str(card["control_family"]) for card in cards).items())),
        "control_family_by_layer": nested_counts(cards, "control_layer", "control_family"),
        "control_layer_by_slice": nested_counts(cards, "slice", "control_layer"),
        "seed_layer_by_slice": nested_counts(seed, "slice", "control_layer"),
        "target_slot_candidate_counts": dict(
            sorted(Counter(str(card["target_slot_drift_candidate"]) for card in cards).items())
        ),
        "expected_primary_surface_counts": expectation_counts(cards, "expected_primary_surface"),
        "target_authority_alarm_expected_counts": expectation_counts(cards, "target_authority_alarm_expected"),
        "short_span_alarm_expected_counts": expectation_counts(cards, "short_span_alarm_expected"),
        "evidence_adequacy_alarm_expected_counts": expectation_counts(cards, "evidence_adequacy_alarm_expected"),
        "config": {
            "control_layers": list(control_layers),
            "seed_per_layer_per_slice": per_layer_per_slice,
        },
        "source_paths": {
            "bridge_cases": {label: str(path) for label, path in bridge_inputs},
        },
        "note": (
            "Matched negative-control cards for the answer-contract audit. "
            "These are built from non-target bridge layers and carry selectivity "
            "expectations, not manual verifier labels."
        ),
    }


def md_cell(value: Any) -> str:
    return " ".join(("" if value is None else str(value)).split()).replace("|", "\\|")


def render_cards_markdown(summary: Mapping[str, Any], seed: List[Mapping[str, Any]]) -> str:
    lines = [
        "# PACT Answer-Contract Negative Controls",
        "",
        "These cards are matched controls for the positive answer-contract audit seed.",
        "They come from non-target bridge layers and test whether the audit is selective.",
        "",
        "## Counts",
        "",
        f"- Cards: `{summary['cards']}`",
        f"- Seed cards: `{summary['seed_cards']}`",
        f"- Slices: `{summary['slices']}`",
        f"- Control layers: `{summary['control_layer_counts']}`",
        f"- Control families: `{summary['control_family_counts']}`",
        f"- Expected primary surfaces: `{summary['expected_primary_surface_counts']}`",
        "",
        "## Seed Cards",
        "",
        "| Slice | Sample | Source | Layer | Family | Expected surface | Gold | Public target | Base | Frozen | Target-only |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for card in seed:
        event = card["source_final_event"]
        conditions = card["conditions"]
        expectation = card["selectivity_expectation"]
        lines.append(
            "| {slice} | {sample} | {source} | {layer} | {family} | {surface} | {gold} | {target} | {base} | {frozen} | {target_only} |".format(
                slice=md_cell(card["slice"]),
                sample=card["sample_index"],
                source=md_cell(card["source_run"]),
                layer=md_cell(card["control_layer"]),
                family=md_cell(card["control_family"]),
                surface=md_cell(expectation.get("expected_primary_surface")),
                gold=md_cell(card["gold_answer"]),
                target=md_cell(event.get("action_required")),
                base=md_cell(conditions["base_public_state_no_final"]["prediction"]),
                frozen=md_cell(conditions["frozen_question_target"]["prediction"]),
                target_only=md_cell(conditions["public_target_only"]["prediction"]),
            )
        )
    lines.extend([
        "",
        "## Boundary",
        "",
        "The seed is a labeling packet, not a specificity result. A real verifier still needs manual or model-judged labels over these controls.",
        "",
    ])
    return "\n".join(lines)


def render_seed_markdown(seed: List[Mapping[str, Any]]) -> str:
    lines = [
        "# Negative-Control Manual Seed",
        "",
        "Fill the label template for each card before treating the answer-contract audit as selective.",
        "",
    ]
    for card in seed:
        event = card["source_final_event"]
        conditions = card["conditions"]
        expectation = card["selectivity_expectation"]
        lines.extend([
            f"## {card['card_id']}",
            "",
            f"- Layer: `{card['control_layer']}`",
            f"- Family: `{card['control_family']}`",
            f"- Expected primary surface: `{expectation.get('expected_primary_surface')}`",
            f"- Question: {card['question']}",
            f"- Gold: `{card['gold_answer']}`",
            f"- Public target: {event.get('action_required')}",
            f"- Public result: {event.get('action_result')}",
            f"- Final answer: `{event.get('final_answer')}`",
            f"- Base prediction: `{conditions['base_public_state_no_final']['prediction']}`",
            f"- Frozen prediction: `{conditions['frozen_question_target']['prediction']}`",
            f"- Target-only prediction: `{conditions['public_target_only']['prediction']}`",
            f"- With-final prediction: `{conditions['with_final_candidate']['prediction']}`",
            "",
            "Manual label:",
            "",
            "- answer_contract_alarm:",
            "- target_authority_alarm:",
            "- short_span_alarm:",
            "- evidence_adequacy_alarm:",
            "- primary_failure_surface:",
            "- note:",
            "",
        ])
    return "\n".join(lines)


def build(args: argparse.Namespace) -> Dict[str, Any]:
    bridge_inputs = parse_bridge_inputs(args.bridge_cases)
    control_layers = list(args.control_layer or DEFAULT_CONTROL_LAYERS)
    cards = build_cards(bridge_inputs, set(control_layers))
    seed = build_seed(cards, args.seed_per_layer_per_slice)
    summary = summarize(cards, seed, bridge_inputs, control_layers, args.seed_per_layer_per_slice)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "negative_control_cards.jsonl", cards)
    write_jsonl(args.out_dir / "negative_control_seed.jsonl", seed)
    write_text(args.out_dir / "negative_control_cards.md", render_cards_markdown(summary, seed))
    write_text(args.out_dir / "negative_control_seed.md", render_seed_markdown(seed))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bridge-cases",
        action="append",
        default=None,
        help="Bridge input as slice_label=path. Defaults to offset100 and offset150 bridge cases.",
    )
    parser.add_argument("--control-layer", action="append", default=None)
    parser.add_argument("--seed-per-layer-per-slice", type=int, default=4)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
