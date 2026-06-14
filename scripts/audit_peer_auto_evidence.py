#!/usr/bin/env python3
"""Audit auto-compressed peer evidence against downstream revisions.

This is a local contact script: it reads saved peer-exposure outputs and the
auto-evidence sidecar records, then joins each short evidence note to the target
model's post-exposure behavior. It does not call a model.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple


AUTO_CONDITIONS = {"correct_auto_evidence", "wrong_auto_evidence"}


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


def normalize_number(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return str(int(number)) if number.is_integer() else str(number)
    text = str(value).replace(",", "").strip()
    if not text:
        return None
    fraction = parse_fraction_value(text)
    if fraction is not None:
        number = float(fraction)
        return str(int(number)) if number.is_integer() else str(number)
    matches = re.findall(r"-?\d+(?:\.\d+)?", text)
    if not matches:
        return None
    number = float(matches[-1])
    return str(int(number)) if number.is_integer() else str(number)


def parse_fraction_value(text: str) -> Optional[Fraction]:
    latex_matches = re.findall(
        r"\\frac\s*\{\s*(-?\d+)\s*\}\s*\{\s*(-?\d+)\s*\}",
        text,
    )
    if latex_matches:
        numerator, denominator = latex_matches[-1]
        if int(denominator) != 0:
            return Fraction(int(numerator), int(denominator))

    plain_matches = re.findall(r"(?<![\d.])-?\d+\s*/\s*-?\d+(?![\d.])", text)
    if plain_matches:
        numerator, denominator = re.split(r"\s*/\s*", plain_matches[-1])
        if int(denominator) != 0:
            return Fraction(int(numerator), int(denominator))
    return None


def normalized_answer_forms(value: Any) -> List[str]:
    forms: List[str] = []
    text = "" if value is None else str(value).strip()
    if text:
        forms.append(text)
        forms.append(text.replace(",", ""))
        number = normalize_number(text)
        if number:
            forms.append(number)
    number = normalize_number(value)
    if number:
        forms.append(number)
    return sorted({form for form in forms if form}, key=len, reverse=True)


def contains_answer(text: str, answer: Any) -> bool:
    haystack = text.replace(",", "")
    haystack_lower = haystack.lower()
    for form in normalized_answer_forms(answer):
        needle = form.replace(",", "")
        if not needle:
            continue
        if re.fullmatch(r"-?\d+(?:\.\d+)?", needle):
            if re.search(rf"(?<![\d.]){re.escape(needle)}(?![\d.])", haystack):
                return True
        elif needle.lower() in haystack_lower:
            return True
    return False


def number_tokens(text: str) -> List[str]:
    simple_numbers = re.findall(r"(?<![A-Za-z])-?\d+(?:,\d{3})*(?:\.\d+)?(?![A-Za-z])", text)
    fractions = re.findall(r"\\frac\{[^{}]+\}\{[^{}]+\}", text)
    factorials = re.findall(r"\d+!", text)
    return sorted(set(simple_numbers + fractions + factorials))


def has_equation_or_formula(text: str) -> bool:
    return bool(
        re.search(r"(=|\\times|\\div|\\frac|\^|\*|/|\bAM-GM\b|\bequation\b|\bfactor\b|\bproportional\b)", text)
    )


def relation_keywords(text: str) -> List[str]:
    keywords = [
        "relation",
        "because",
        "since",
        "if",
        "then",
        "multiply",
        "divide",
        "subtract",
        "add",
        "arrange",
        "blocks",
        "proportional",
        "minimum",
        "constraint",
        "per",
        "rate",
        "total",
    ]
    lower = text.lower()
    return [word for word in keywords if re.search(rf"\b{re.escape(word)}\b", lower)]


def leakage_label(evidence: Dict[str, Any], post_record: Optional[Dict[str, Any]]) -> str:
    text = str(evidence.get("evidence_text") or "")
    source_answer = evidence.get("source_answer")
    gold_answer = (post_record or {}).get("gold_answer")
    source_leak = bool(evidence.get("contains_source_answer")) or contains_answer(text, source_answer)
    gold_leak = contains_answer(text, gold_answer)
    finalish = bool(re.search(r"\b(final answer|answer is|minimum value is|the answer)\b", text, flags=re.I))
    if source_leak and finalish:
        return "explicit_answer_like_leak"
    if source_leak:
        return "source_answer_number_present"
    if gold_leak:
        return "gold_answer_number_present"
    if finalish:
        return "answer_like_phrase_without_source_number"
    return "no_obvious_answer_leak"


def auto_extraction_key(row: Dict[str, Any]) -> Tuple[str, str, str, str]:
    return (
        str(row.get("run_id")),
        str(row.get("case_index")),
        str(row.get("condition")),
        str(row.get("source_agent_id")),
    )


def post_record_key(row: Dict[str, Any]) -> Optional[Tuple[str, str, str, str]]:
    if row.get("condition") not in AUTO_CONDITIONS:
        return None
    peers = row.get("peer_exposure") or []
    if not peers:
        return None
    peer = peers[0]
    return (
        str(row.get("run_id")),
        str(row.get("case_index")),
        str(row.get("condition")),
        str(peer.get("source")),
    )


def classify_case(evidence: Dict[str, Any], post_record: Optional[Dict[str, Any]], run_dir: Path) -> Dict[str, Any]:
    text = str(evidence.get("evidence_text") or "")
    nums = number_tokens(text)
    keywords = relation_keywords(text)
    leak = leakage_label(evidence, post_record)
    expected_correct = str(evidence.get("expected_correct") or "")
    transition = (post_record or {}).get("transition")
    post_correct = (post_record or {}).get("post_exposure_correct")
    pre_correct = (post_record or {}).get("pre_exposure_correct")
    source_family = ((post_record or {}).get("source_trace") or {}).get("source_family")
    source_method = ((post_record or {}).get("source_trace") or {}).get("source_method")

    if expected_correct == "false" and transition == "wrong_to_right":
        contact_label = "wrong_evidence_recoverable_skeleton"
    elif expected_correct == "false" and transition == "right_to_wrong":
        contact_label = "wrong_evidence_harmful_relation"
    elif expected_correct == "true" and transition == "wrong_to_right":
        contact_label = "correct_evidence_rescue"
    elif leak != "no_obvious_answer_leak":
        contact_label = "answer_leak_audit"
    elif has_equation_or_formula(text) and len(nums) >= 2:
        contact_label = "dense_formula_surface"
    else:
        contact_label = "plain_relation_surface"

    return {
        "run_dir": str(run_dir),
        "run_id": evidence.get("run_id"),
        "case_index": evidence.get("case_index"),
        "instance_id": evidence.get("instance_id"),
        "source_family": source_family,
        "source_method": source_method,
        "condition": evidence.get("condition"),
        "expected_correct": expected_correct,
        "source_agent_id": evidence.get("source_agent_id"),
        "source_answer": evidence.get("source_answer"),
        "gold_answer": (post_record or {}).get("gold_answer"),
        "pre_exposure_answer": (post_record or {}).get("pre_exposure_answer"),
        "post_exposure_answer": (post_record or {}).get("post_exposure_answer"),
        "pre_exposure_correct": pre_correct,
        "post_exposure_correct": post_correct,
        "transition": transition,
        "peer_answer_adopted": (post_record or {}).get("peer_answer_adopted"),
        "leakage_label": leak,
        "contains_source_answer_recorded": bool(evidence.get("contains_source_answer")),
        "contains_source_answer_recomputed": contains_answer(text, evidence.get("source_answer")),
        "contains_gold_answer_recomputed": contains_answer(text, (post_record or {}).get("gold_answer")),
        "has_equation_or_formula": has_equation_or_formula(text),
        "numeric_token_count": len(nums),
        "numeric_tokens": nums,
        "relation_keywords": keywords,
        "word_count": len(text.split()),
        "evidence_text": text,
        "contact_label": contact_label,
        "joined_post_record": post_record is not None,
    }


def summarize(cases: List[Dict[str, Any]], run_dirs: List[Path]) -> Dict[str, Any]:
    total = len(cases)
    by_family: Dict[str, Counter[str]] = defaultdict(Counter)
    by_condition: Dict[str, Counter[str]] = defaultdict(Counter)
    leakage_by_condition: Dict[str, Counter[str]] = defaultdict(Counter)
    contact_labels = Counter(case["contact_label"] for case in cases)
    transition_by_condition: Dict[str, Counter[str]] = defaultdict(Counter)
    examples: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for case in cases:
        family = str(case.get("source_family") or "unknown")
        condition = str(case.get("condition") or "unknown")
        leak = str(case.get("leakage_label"))
        transition = str(case.get("transition") or "missing")
        by_family[family]["records"] += 1
        by_family[family][leak] += 1
        by_condition[condition]["records"] += 1
        by_condition[condition][transition] += 1
        leakage_by_condition[condition][leak] += 1
        transition_by_condition[condition][transition] += 1
        label = str(case.get("contact_label"))
        if len(examples[label]) < 5:
            examples[label].append(
                {
                    "run_id": case.get("run_id"),
                    "case_index": case.get("case_index"),
                    "condition": condition,
                    "transition": transition,
                    "leakage_label": leak,
                    "source_answer": case.get("source_answer"),
                    "post_exposure_answer": case.get("post_exposure_answer"),
                    "evidence_text": case.get("evidence_text"),
                }
            )

    answer_leak_count = sum(
        1 for case in cases if case["leakage_label"] != "no_obvious_answer_leak"
    )
    recorded_source_leaks = sum(1 for case in cases if case["contains_source_answer_recorded"])
    recomputed_source_leaks = sum(1 for case in cases if case["contains_source_answer_recomputed"])

    return {
        "run_dirs": [str(path) for path in run_dirs],
        "records": total,
        "joined_post_records": sum(1 for case in cases if case["joined_post_record"]),
        "recorded_source_answer_leaks": recorded_source_leaks,
        "recomputed_source_answer_leaks": recomputed_source_leaks,
        "answer_like_or_numeric_leak_count": answer_leak_count,
        "answer_like_or_numeric_leak_rate": answer_leak_count / total if total else None,
        "avg_word_count": mean(case["word_count"] for case in cases) if cases else None,
        "avg_numeric_token_count": mean(case["numeric_token_count"] for case in cases) if cases else None,
        "contact_label_counts": dict(sorted(contact_labels.items())),
        "by_family": {key: dict(sorted(value.items())) for key, value in sorted(by_family.items())},
        "by_condition_transitions": {
            key: dict(sorted(value.items())) for key, value in sorted(transition_by_condition.items())
        },
        "by_condition_leakage": {
            key: dict(sorted(value.items())) for key, value in sorted(leakage_by_condition.items())
        },
        "examples_by_contact_label": dict(sorted(examples.items())),
        "note": (
            "Leakage is heuristic: numeric containment can count legitimate intermediate "
            "quantities as answer leaks, while fractions and aliases can be missed."
        ),
    }


def build(args: argparse.Namespace) -> Dict[str, Any]:
    cases: List[Dict[str, Any]] = []
    for run_dir in args.run_dirs:
        extraction_path = run_dir / "auto_evidence_extractions.jsonl"
        records_path = run_dir / "peer_exposure_records.jsonl"
        post_by_key: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}
        for row in load_jsonl(records_path):
            key = post_record_key(row)
            if key:
                post_by_key[key] = row
        for evidence in load_jsonl(extraction_path):
            cases.append(classify_case(evidence, post_by_key.get(auto_extraction_key(evidence)), run_dir))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize(cases, args.run_dirs)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "cases.jsonl", cases)

    postcards = []
    for label in [
        "correct_evidence_rescue",
        "wrong_evidence_harmful_relation",
        "wrong_evidence_recoverable_skeleton",
        "answer_leak_audit",
    ]:
        postcards.extend(summary["examples_by_contact_label"].get(label, []))
    write_jsonl(args.out_dir / "postcards.jsonl", postcards)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dirs", type=Path, nargs="+", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
