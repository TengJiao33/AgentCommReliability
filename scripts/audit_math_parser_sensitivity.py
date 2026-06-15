#!/usr/bin/env python3
"""Audit MATH parser-sensitive cases in a peer-exposure run."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from audit_peer_exposure_statistics import (
    by_case_condition,
    condition_rate,
    exact_binomial_two_sided,
    paired_correctness,
    read_jsonl,
    wilson_interval,
    write_json,
)


WRONG_CONDITIONS = [
    "wrong_answer_only",
    "wrong_rationale",
    "wrong_redacted_rationale",
    "wrong_equation_surface",
    "wrong_typed_public_state",
]

CORRECT_CONDITIONS = [
    "correct_answer_only",
    "correct_rationale",
    "correct_redacted_rationale",
    "correct_equation_surface",
    "correct_typed_public_state",
]

PAIRED_TARGETS = [
    ("wrong_typed_public_state", "wrong_rationale"),
    ("wrong_typed_public_state", "wrong_redacted_rationale"),
    ("wrong_typed_public_state", "wrong_equation_surface"),
    ("wrong_typed_public_state", "wrong_answer_only"),
    ("correct_typed_public_state", "correct_rationale"),
    ("correct_typed_public_state", "correct_redacted_rationale"),
    ("correct_typed_public_state", "correct_equation_surface"),
]


def read_math_data(path: Path) -> Dict[str, Dict[str, Any]]:
    rows = {}
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            rows[str(row.get("id"))] = row
    return rows


def extract_boxed_answer(text: str) -> Optional[str]:
    marker = r"\boxed{"
    start = text.rfind(marker)
    if start < 0:
        return None
    index = start + len(marker)
    depth = 1
    while index < len(text):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start + len(marker) : index].strip()
        index += 1
    return None


def compact_latex(text: str) -> str:
    cleaned = str(text).strip()
    replacements = {
        "$": "",
        r"\left": "",
        r"\right": "",
        r"\!": "",
        r"\,": "",
        r"\ ": "",
        " ": "",
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    return cleaned


def is_plain_numeric_answer(answer: Optional[str]) -> bool:
    if answer is None:
        return False
    text = compact_latex(answer)
    if not text:
        return False
    thousands = re.fullmatch(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?", text)
    if thousands:
        text = text.replace(",", "")
    elif "," in text:
        return False
    if re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        return True
    if re.fullmatch(r"-?\\frac\{-?\d+\}\{-?\d+\}", text):
        return True
    if re.fullmatch(r"-?\d+/-?\d+", text):
        return True
    return False


def sensitivity_reasons(answer: Optional[str]) -> List[str]:
    if answer is None:
        return ["missing_boxed_answer"]
    text = compact_latex(answer)
    reasons = []
    if is_plain_numeric_answer(answer):
        return reasons
    if re.search(r"\\sqrt|√|sqrt", text, flags=re.I):
        reasons.append("radical")
    if re.search(r"(?<![A-Za-z])i(?![A-Za-z])|\\mathrm\{i\}", text):
        reasons.append("complex")
    if re.search(r"\\pi|π", text):
        reasons.append("pi")
    if "," in text or ";" in text:
        reasons.append("multi_value_or_comma")
    if re.search(r"\\pm|±", text):
        reasons.append("plus_minus")
    if re.search(r"\\infty|∞|\\cup|\\cap", text):
        reasons.append("set_or_interval")
    if re.search(r"[\[\]\(\)]", text):
        reasons.append("bracketed_structure")
    non_fraction_commands = re.findall(r"\\([A-Za-z]+)", text)
    non_fraction_commands = [cmd for cmd in non_fraction_commands if cmd not in {"frac"}]
    if non_fraction_commands:
        reasons.append("latex_non_fraction")
    without_commands = re.sub(r"\\[A-Za-z]+", "", text)
    if re.search(r"[A-Za-z]", without_commands):
        reasons.append("symbolic_letter")
    if re.search(r"(?<!^)[+\-*^=]", text):
        reasons.append("expression_not_single_number")
    if not reasons:
        reasons.append("non_plain_numeric")
    return sorted(set(reasons))


def case_id(record: Dict[str, Any]) -> str:
    return str(record.get("case_index", record.get("instance_id")))


def build_case_audit(source_cases: List[Dict[str, Any]], math_rows: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    audits = []
    for source in source_cases:
        instance_id = str(source.get("instance_id"))
        math_row = math_rows.get(instance_id)
        boxed = extract_boxed_answer((math_row or {}).get("answer", ""))
        reasons = sensitivity_reasons(boxed)
        audits.append(
            {
                "case_index": source.get("case_index"),
                "instance_id": instance_id,
                "question": source.get("question"),
                "boxed_answer": boxed,
                "stored_gold_answer": source.get("gold_answer"),
                "parser_sensitive": bool(reasons),
                "sensitivity_reasons": reasons,
            }
        )
    return audits


def rate_payload(table: Dict[str, Dict[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    rates = [
        condition_rate(table, "no_peer", numerator="post_correct", denominator="records"),
        condition_rate(table, "no_peer", numerator="unparseable", denominator="records"),
    ]
    for condition in WRONG_CONDITIONS:
        rates.append(condition_rate(table, condition, numerator="right_to_wrong", denominator="pre_correct"))
        rates.append(condition_rate(table, condition, numerator="post_correct", denominator="records"))
    for condition in CORRECT_CONDITIONS:
        rates.append(condition_rate(table, condition, numerator="wrong_to_right", denominator="pre_wrong"))
        rates.append(condition_rate(table, condition, numerator="post_correct", denominator="records"))
    return rates


def format_rate(rate: Dict[str, Any]) -> str:
    value = rate["rate"]
    return "-" if value is None else f"{value:.3f}"


def format_ci(rate: Dict[str, Any]) -> str:
    ci = rate["wilson_95"]
    return "-" if ci is None else f"[{ci[0]:.3f}, {ci[1]:.3f}]"


def build_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# MATH Parser-Sensitivity Audit",
        "",
        "This audit joins peer-exposure source cases back to original MATH boxed answers, flags answers that are not plain numeric values under the current project normalizer, and recomputes key rates after excluding those parser-sensitive source cases.",
        "",
        "## Case Surface",
        "",
        f"- Total source cases: `{payload['num_cases']}`",
        f"- Plain numeric source cases: `{payload['num_plain_numeric_cases']}`",
        f"- Parser-sensitive source cases: `{payload['num_parser_sensitive_cases']}`",
        "",
        "| Reason | Cases |",
        "| --- | ---: |",
    ]
    for reason, count in payload["sensitivity_reason_counts"].items():
        lines.append(f"| {reason} | {count} |")
    lines.extend(
        [
            "",
            "Parser-sensitive case IDs:",
            "",
            "`" + ", ".join(map(str, payload["parser_sensitive_case_ids"])) + "`",
            "",
            "## Plain-Numeric Subset Rates",
            "",
            "| Condition | Metric | Count | Rate | Wilson 95% |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for rate in payload["plain_numeric_rates"]:
        lines.append(
            "| {condition} | {metric} | {successes}/{total} | {rate} | {ci} |".format(
                condition=rate["condition"],
                metric=f"{rate['numerator']} / {rate['denominator']}",
                successes=rate["successes"],
                total=rate["total"],
                rate=format_rate(rate),
                ci=format_ci(rate),
            )
        )
    lines.extend(
        [
            "",
            "## Plain-Numeric Paired Correctness",
            "",
            "| A | B | Known Pairs | A-only | B-only | Delta A-B | Exact p |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for cmp_row in payload["plain_numeric_paired_correctness"]:
        p = cmp_row["mcnemar_exact_two_sided_p"]
        delta = cmp_row["accuracy_delta_a_minus_b_on_known_pairs"]
        lines.append(
            "| {a} | {b} | {known} | {a_only} | {b_only} | {delta} | {p} |".format(
                a=cmp_row["condition_a"],
                b=cmp_row["condition_b"],
                known=cmp_row["known_pairs"],
                a_only=cmp_row["a_correct_b_wrong"],
                b_only=cmp_row["b_correct_a_wrong"],
                delta="-" if delta is None else f"{delta:+.3f}",
                p="-" if p is None else f"{p:.4f}",
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This is a conservative exclusion audit, not a semantic MATH evaluator.",
            "- A parser-sensitive source answer can still be correctly solved by the model; the flag only says the current numeric normalizer is not trustworthy enough for strong semantic claims on that case.",
            "- Plain-numeric rates are useful as a robustness check for the main statistical audit.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cases-jsonl", type=Path, required=True)
    parser.add_argument("--records-jsonl", type=Path, required=True)
    parser.add_argument("--math-jsonl", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    source_cases = read_jsonl(args.source_cases_jsonl)
    records = read_jsonl(args.records_jsonl)
    math_rows = read_math_data(args.math_jsonl)
    case_audit = build_case_audit(source_cases, math_rows)

    parser_sensitive_ids: Set[str] = {str(row["case_index"]) for row in case_audit if row["parser_sensitive"]}
    plain_numeric_ids: Set[str] = {str(row["case_index"]) for row in case_audit if not row["parser_sensitive"]}
    plain_records = [row for row in records if case_id(row) in plain_numeric_ids]
    plain_table = by_case_condition(plain_records)

    reason_counts: Counter[str] = Counter()
    for row in case_audit:
        for reason in row["sensitivity_reasons"]:
            reason_counts[reason] += 1

    payload = {
        "source_cases_jsonl": str(args.source_cases_jsonl),
        "records_jsonl": str(args.records_jsonl),
        "math_jsonl": str(args.math_jsonl),
        "num_cases": len(case_audit),
        "num_records": len(records),
        "num_plain_numeric_cases": len(plain_numeric_ids),
        "num_plain_numeric_records": len(plain_records),
        "num_parser_sensitive_cases": len(parser_sensitive_ids),
        "parser_sensitive_case_ids": sorted(parser_sensitive_ids, key=lambda value: int(value) if value.isdigit() else value),
        "plain_numeric_case_ids": sorted(plain_numeric_ids, key=lambda value: int(value) if value.isdigit() else value),
        "sensitivity_reason_counts": dict(sorted(reason_counts.items())),
        "case_audit": case_audit,
        "plain_numeric_rates": rate_payload(plain_table),
        "plain_numeric_paired_correctness": [paired_correctness(plain_table, a, b) for a, b in PAIRED_TARGETS],
    }
    write_json(args.out_json, payload)
    args.out_md.write_text(build_markdown(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
