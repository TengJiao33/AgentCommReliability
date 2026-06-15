#!/usr/bin/env python3
"""Build a manual answer-contract audit seed from PACT focus cards."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple


DEFAULT_FOCUS_DIRS = [
    Path("experiments/20260615-local-pact-field-authority-focus-offset100"),
    Path("experiments/20260615-local-pact-field-authority-focus-offset150"),
]
DEFAULT_OUT_DIR = Path("experiments/20260615-local-pact-answer-contract-audit-seed")


SEMANTIC_PROTOCOL = {
    "answer_type_projection": {
        "required_checks": [
            "question_answer_type_or_relation",
            "public_target_answer_contract_alignment",
            "public_result_answers_question_contract",
        ],
        "contract_risk": "answer_type_or_relation_mismatch",
        "recommended_action": "keep_question_root_or_freeze_question_target",
        "protocol_read": (
            "The original question is needed to recover the requested answer type "
            "or relation before using public fields as task authority."
        ),
    },
    "short_span_or_granularity": {
        "required_checks": [
            "question_short_span_contract",
            "public_result_span_granularity",
            "qualifier_or_sentence_expansion",
        ],
        "contract_risk": "short_span_or_granularity_mismatch",
        "recommended_action": "keep_question_root_and_short_span_constraint",
        "protocol_read": (
            "The public fields may contain the right semantic answer while failing "
            "the required short-answer span or qualifier contract."
        ),
    },
    "public_target_misdirection": {
        "required_checks": [
            "public_target_relation_matches_question",
            "public_result_distractor_or_wrong_relation",
            "evidence_adequacy_for_question_root",
        ],
        "contract_risk": "public_target_misdirects_relation",
        "recommended_action": "hide_public_target_or_freeze_question_target",
        "protocol_read": (
            "The public target points at a related but wrong relation or entity; "
            "the downstream answerer should not treat it as task authority."
        ),
    },
    "evidence_sentence_or_distractor": {
        "required_checks": [
            "question_attended_evidence_extraction",
            "avoid_evidence_sentence_copy",
            "distractor_entity_guard",
        ],
        "contract_risk": "evidence_sentence_or_distractor_copy",
        "recommended_action": "question_attended_short_answer_extraction",
        "protocol_read": (
            "The public fields contain a related sentence, but the answerer needs "
            "question-attended extraction instead of sentence copying."
        ),
    },
    "question_root_boundary_regression": {
        "required_checks": [
            "evidence_adequacy_for_question_root",
            "question_root_ambiguity_guard",
            "outside_prior_guard",
        ],
        "contract_risk": "question_root_can_reopen_ambiguity",
        "recommended_action": "do_not_freeze_without_evidence_adequacy_check",
        "protocol_read": (
            "The trusted question root is not automatically safe; if saved evidence "
            "is underspecified, freezing to the question can reopen ambiguity."
        ),
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


def card_key(row: Mapping[str, Any]) -> Tuple[int, str, str]:
    return (int(row["sample_index"]), str(row["source_run"]), str(row["bridge_family"]))


def slice_name(focus_dir: Path) -> str:
    name = focus_dir.name
    if name.endswith("offset100"):
        return "offset100"
    if name.endswith("offset150"):
        return "offset150"
    return name


def condition_correct(card: Mapping[str, Any], key: str) -> bool:
    return bool((card.get(key) or {}).get("correct"))


def condition_prediction(card: Mapping[str, Any], key: str) -> Any:
    return (card.get(key) or {}).get("prediction")


def make_record(card: Mapping[str, Any], label: Mapping[str, Any], current_slice: str) -> Dict[str, Any]:
    semantic_family = str(label["semantic_family"])
    protocol = SEMANTIC_PROTOCOL[semantic_family]
    public_target_only_correct = condition_correct(card, "public_target_only")
    frozen_correct = condition_correct(card, "frozen_target_plus_evidence")
    base_correct = condition_correct(card, "base_public_state_no_final")
    return {
        "slice": current_slice,
        "sample_index": card["sample_index"],
        "source_run": card["source_run"],
        "bridge_family": card["bridge_family"],
        "semantic_family": semantic_family,
        "question": card["question"],
        "gold_answer": card["gold_answer"],
        "action_required": card["action_required"],
        "action_result": card["action_result"],
        "manual_note": label.get("note"),
        "answer_contract_audit": {
            "required_checks": list(protocol["required_checks"]),
            "contract_risk": protocol["contract_risk"],
            "recommended_action": protocol["recommended_action"],
            "protocol_read": protocol["protocol_read"],
        },
        "observed_behavior": {
            "base_public_state_no_final_correct": base_correct,
            "base_public_state_no_final_prediction": condition_prediction(card, "base_public_state_no_final"),
            "frozen_target_correct": frozen_correct,
            "frozen_target_prediction": condition_prediction(card, "frozen_target_plus_evidence"),
            "public_target_only_correct": public_target_only_correct,
            "public_target_only_prediction": condition_prediction(card, "public_target_only"),
            "hide_public_target_correct": condition_correct(card, "hide_public_target"),
            "hide_public_target_prediction": condition_prediction(card, "hide_public_target"),
        },
        "audit_expectation": {
            "public_target_only_unsafe": not public_target_only_correct,
            "frozen_question_target_sufficient": frozen_correct,
            "needs_evidence_adequacy_guard": semantic_family == "question_root_boundary_regression",
        },
    }


def build_records(focus_dirs: Iterable[Path]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for focus_dir in focus_dirs:
        cards = {card_key(row): row for row in load_jsonl(focus_dir / "focus_cards.jsonl")}
        labels = load_jsonl(focus_dir / "manual_semantic_labels.jsonl")
        missing = [card_key(label) for label in labels if card_key(label) not in cards]
        if missing:
            raise ValueError(f"Manual labels without focus cards in {focus_dir}: {missing[:5]}")
        for label in labels:
            records.append(make_record(cards[card_key(label)], label, slice_name(focus_dir)))
    return sorted(records, key=lambda row: (str(row["slice"]), int(row["sample_index"]), str(row["source_run"])))


def nested_counts(rows: Iterable[Mapping[str, Any]], outer: str, inner: str) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        out[str(row.get(outer))][str(row.get(inner))] += 1
    return {key: dict(sorted(value.items())) for key, value in sorted(out.items())}


def protocol_counts(rows: Iterable[Mapping[str, Any]], key: str) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        counter[str((row.get("answer_contract_audit") or {}).get(key))] += 1
    return dict(sorted(counter.items()))


def summarize(records: List[Mapping[str, Any]], focus_dirs: List[Path]) -> Dict[str, Any]:
    return {
        "records": len(records),
        "slices": dict(sorted(Counter(str(row["slice"]) for row in records).items())),
        "semantic_family_counts": dict(sorted(Counter(str(row["semantic_family"]) for row in records).items())),
        "bridge_family_counts": dict(sorted(Counter(str(row["bridge_family"]) for row in records).items())),
        "semantic_family_by_slice": nested_counts(records, "slice", "semantic_family"),
        "semantic_family_by_bridge_family": nested_counts(records, "bridge_family", "semantic_family"),
        "contract_risk_counts": protocol_counts(records, "contract_risk"),
        "recommended_action_counts": protocol_counts(records, "recommended_action"),
        "public_target_only_unsafe_count": sum(
            1 for row in records
            if (row.get("audit_expectation") or {}).get("public_target_only_unsafe")
        ),
        "frozen_question_target_sufficient_count": sum(
            1 for row in records
            if (row.get("audit_expectation") or {}).get("frozen_question_target_sufficient")
        ),
        "needs_evidence_adequacy_guard_count": sum(
            1 for row in records
            if (row.get("audit_expectation") or {}).get("needs_evidence_adequacy_guard")
        ),
        "source_paths": {
            "focus_dirs": [str(path) for path in focus_dirs],
        },
        "note": (
            "Manual/oracle audit seed over focus cards. This is a protocol sketch "
            "and positive-control audit surface, not a runtime verifier."
        ),
    }


def md_cell(value: Any) -> str:
    return " ".join(("" if value is None else str(value)).split()).replace("|", "\\|")


def render_markdown(summary: Mapping[str, Any], records: List[Mapping[str, Any]]) -> str:
    lines = [
        "# PACT Answer-Contract Audit Seed",
        "",
        "This is a manual/oracle audit seed over target-layer focus cards. It converts semantic labels into protocol fields.",
        "It is not a runtime verifier.",
        "",
        "## Counts",
        "",
        f"- Records: `{summary['records']}`",
        f"- Slices: `{summary['slices']}`",
        f"- Semantic families: `{summary['semantic_family_counts']}`",
        f"- Contract risks: `{summary['contract_risk_counts']}`",
        f"- Recommended actions: `{summary['recommended_action_counts']}`",
        f"- Public-target-only unsafe: `{summary['public_target_only_unsafe_count']}`",
        f"- Frozen question target sufficient: `{summary['frozen_question_target_sufficient_count']}`",
        f"- Needs evidence-adequacy guard: `{summary['needs_evidence_adequacy_guard_count']}`",
        "",
        "## Audit Records",
        "",
        "| Slice | Sample | Source | Semantic family | Contract risk | Recommended action | Gold | Public target | Target-only | Frozen |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in records:
        audit = row["answer_contract_audit"]
        observed = row["observed_behavior"]
        lines.append(
            "| {slice} | {sample} | {source} | {semantic} | {risk} | {action} | {gold} | {target} | {target_only} | {frozen} |".format(
                slice=md_cell(row["slice"]),
                sample=row["sample_index"],
                source=md_cell(row["source_run"]),
                semantic=md_cell(row["semantic_family"]),
                risk=md_cell(audit["contract_risk"]),
                action=md_cell(audit["recommended_action"]),
                gold=md_cell(row["gold_answer"]),
                target=md_cell(row["action_required"]),
                target_only=md_cell(observed["public_target_only_prediction"]),
                frozen=md_cell(observed["frozen_target_prediction"]),
            )
        )
    lines.extend([
        "",
        "## Boundary",
        "",
        "The records with `question_root_can_reopen_ambiguity` are the current warning cases: question-root projection can hurt when evidence adequacy is weak.",
        "",
    ])
    return "\n".join(lines)


def build(args: argparse.Namespace) -> Dict[str, Any]:
    focus_dirs = list(args.focus_dir or DEFAULT_FOCUS_DIRS)
    records = build_records(focus_dirs)
    summary = summarize(records, focus_dirs)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "audit_seed_records.jsonl", records)
    write_text(args.out_dir / "audit_seed.md", render_markdown(summary, records))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--focus-dir", type=Path, action="append", default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
