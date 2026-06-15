#!/usr/bin/env python3
"""Recompute peer-exposure correctness with conservative MATH semantics."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from audit_peer_exposure_statistics import (
    by_case_condition,
    condition_rate,
    paired_correctness,
    read_jsonl,
    write_json,
)
from peer_probe.answers import transition_type
from peer_probe.io_utils import write_jsonl
from peer_probe.math_eval import (
    EquivalenceResult,
    extract_answer_text,
    extract_boxed_answer,
    math_equiv,
    semantic_correct_from_output,
)


WRONG_CONDITIONS = [
    "wrong_answer_only",
    "wrong_raw_answer_only",
    "wrong_rationale",
    "wrong_redacted_rationale",
    "wrong_equation_surface",
    "wrong_typed_public_state",
]

CORRECT_CONDITIONS = [
    "correct_answer_only",
    "correct_raw_answer_only",
    "correct_rationale",
    "correct_redacted_rationale",
    "correct_equation_surface",
    "correct_typed_public_state",
]

CONDITIONS = ["no_peer"] + WRONG_CONDITIONS + CORRECT_CONDITIONS

PAIRED_TARGETS = [
    ("wrong_typed_public_state", "wrong_rationale"),
    ("wrong_typed_public_state", "wrong_redacted_rationale"),
    ("wrong_typed_public_state", "wrong_equation_surface"),
    ("wrong_typed_public_state", "wrong_answer_only"),
    ("wrong_raw_answer_only", "wrong_answer_only"),
    ("wrong_raw_answer_only", "wrong_rationale"),
    ("correct_typed_public_state", "correct_rationale"),
    ("correct_typed_public_state", "correct_redacted_rationale"),
    ("correct_typed_public_state", "correct_equation_surface"),
    ("correct_raw_answer_only", "correct_answer_only"),
    ("correct_raw_answer_only", "correct_rationale"),
    ("correct_redacted_rationale", "correct_rationale"),
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


def case_id(record: Dict[str, Any]) -> str:
    return str(record.get("case_index", record.get("instance_id")))


def eval_payload(result: EquivalenceResult) -> Dict[str, Any]:
    return {
        "correct": result.correct,
        "status": result.status,
        "prediction_raw": result.prediction_raw,
        "reference_raw": result.reference_raw,
        "prediction_normalized": result.prediction_normalized,
        "reference_normalized": result.reference_normalized,
    }


def source_peer_answer(peer: Dict[str, Any]) -> Optional[str]:
    answer, _ = extract_answer_text(peer.get("response"))
    if answer is not None:
        return answer
    raw_answer = peer.get("answer")
    return None if raw_answer is None else str(raw_answer)


def build_source_case_audit(
    source_cases: List[Dict[str, Any]],
    math_rows: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    audits: Dict[str, Dict[str, Any]] = {}
    for source in source_cases:
        cid = str(source.get("case_index"))
        math_row = math_rows.get(str(source.get("instance_id"))) or {}
        gold = extract_boxed_answer(math_row.get("answer"))
        correct_peer = source.get("correct_peer") or {}
        wrong_peer = source.get("wrong_peer") or {}
        correct_eval = math_equiv(source_peer_answer(correct_peer), gold)
        wrong_eval = math_equiv(source_peer_answer(wrong_peer), gold)
        audits[cid] = {
            "case_index": source.get("case_index"),
            "instance_id": str(source.get("instance_id")),
            "gold_answer_raw": gold,
            "stored_gold_answer": source.get("gold_answer"),
            "correct_peer_answer_raw": source_peer_answer(correct_peer),
            "wrong_peer_answer_raw": source_peer_answer(wrong_peer),
            "correct_peer_semantic": eval_payload(correct_eval),
            "wrong_peer_semantic": eval_payload(wrong_eval),
            "source_labels_semantically_reliable": correct_eval.correct is True and wrong_eval.correct is False,
        }
    return audits


def semantic_record(record: Dict[str, Any], source_audit: Dict[str, Any]) -> Dict[str, Any]:
    gold = source_audit.get("gold_answer_raw")
    post_eval = semantic_correct_from_output(record.get("post_exposure_output"), gold)
    if record.get("condition") == "no_peer":
        pre_eval = post_eval
    else:
        pre_eval = semantic_correct_from_output(record.get("pre_exposure_output"), gold)
    semantic = dict(record)
    semantic["gold_answer_raw"] = gold
    semantic["stored_gold_answer_numeric"] = record.get("gold_answer")
    semantic["pre_exposure_answer_raw"] = pre_eval.prediction_raw
    semantic["post_exposure_answer_raw"] = post_eval.prediction_raw
    semantic["pre_exposure_correct_numeric"] = record.get("pre_exposure_correct")
    semantic["post_exposure_correct_numeric"] = record.get("post_exposure_correct")
    semantic["transition_numeric"] = record.get("transition")
    semantic["pre_exposure_correct"] = pre_eval.correct
    semantic["post_exposure_correct"] = post_eval.correct
    semantic["transition"] = (
        "baseline"
        if record.get("condition") == "no_peer"
        else transition_type(pre_eval.correct, post_eval.correct)
    )
    semantic["semantic_eval"] = {
        "pre": eval_payload(pre_eval),
        "post": eval_payload(post_eval),
        "source_labels_semantically_reliable": source_audit.get("source_labels_semantically_reliable"),
    }
    return semantic


def rate_payload(table: Dict[str, Dict[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    rates = [
        condition_rate(table, "no_peer", numerator="post_correct", denominator="records"),
        condition_rate(table, "no_peer", numerator="unparseable", denominator="records"),
    ]
    for condition in WRONG_CONDITIONS:
        rates.append(condition_rate(table, condition, numerator="right_to_wrong", denominator="pre_correct"))
        rates.append(condition_rate(table, condition, numerator="stable_right", denominator="pre_correct"))
        rates.append(condition_rate(table, condition, numerator="post_correct", denominator="records"))
        rates.append(condition_rate(table, condition, numerator="unparseable", denominator="records"))
    for condition in CORRECT_CONDITIONS:
        rates.append(condition_rate(table, condition, numerator="wrong_to_right", denominator="pre_wrong"))
        rates.append(condition_rate(table, condition, numerator="post_correct", denominator="records"))
        rates.append(condition_rate(table, condition, numerator="unparseable", denominator="records"))
    return rates


def compare_numeric_semantic(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    counters: Counter[str] = Counter()
    changed = []
    for record in records:
        numeric = record.get("post_exposure_correct_numeric")
        semantic = record.get("post_exposure_correct")
        if isinstance(numeric, bool) and isinstance(semantic, bool):
            key = "same_known" if numeric == semantic else "changed_known"
        elif semantic is None:
            key = "semantic_unknown"
        else:
            key = "numeric_unknown_semantic_known"
        counters[key] += 1
        if key != "same_known":
            changed.append(
                {
                    "case_index": record.get("case_index"),
                    "condition": record.get("condition"),
                    "numeric_correct": numeric,
                    "semantic_correct": semantic,
                    "numeric_answer": record.get("post_exposure_answer"),
                    "raw_answer": record.get("post_exposure_answer_raw"),
                    "gold_raw": record.get("gold_answer_raw"),
                    "semantic_status": (record.get("semantic_eval") or {}).get("post", {}).get("status"),
                }
            )
    return {"counts": dict(counters), "changed_or_unknown_records": changed}


def subset_by_reliable_source(records: List[Dict[str, Any]], reliable_case_ids: Set[str]) -> List[Dict[str, Any]]:
    return [record for record in records if case_id(record) in reliable_case_ids]


def fmt_rate(rate: Dict[str, Any]) -> str:
    return "-" if rate["rate"] is None else f"{rate['rate']:.3f}"


def fmt_ci(rate: Dict[str, Any]) -> str:
    ci = rate["wilson_95"]
    return "-" if ci is None else f"[{ci[0]:.3f}, {ci[1]:.3f}]"


def append_rate_table(lines: List[str], title: str, rates: List[Dict[str, Any]]) -> None:
    lines.extend(
        [
            f"## {title}",
            "",
            "| Condition | Metric | Count | Rate | Wilson 95% |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for rate in rates:
        lines.append(
            "| {condition} | {metric} | {successes}/{total} | {rate} | {ci} |".format(
                condition=rate["condition"],
                metric=f"{rate['numerator']} / {rate['denominator']}",
                successes=rate["successes"],
                total=rate["total"],
                rate=fmt_rate(rate),
                ci=fmt_ci(rate),
            )
        )
    lines.append("")


def append_pair_table(lines: List[str], title: str, pairs: List[Dict[str, Any]]) -> None:
    lines.extend(
        [
            f"## {title}",
            "",
            "| A | B | Known Pairs | Unknown Pairs | A-only | B-only | Delta A-B | Exact p |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in pairs:
        p = row["mcnemar_exact_two_sided_p"]
        delta = row["accuracy_delta_a_minus_b_on_known_pairs"]
        lines.append(
            "| {a} | {b} | {known} | {unknown} | {a_only} | {b_only} | {delta} | {p} |".format(
                a=row["condition_a"],
                b=row["condition_b"],
                known=row["known_pairs"],
                unknown=row["unknown_pairs"],
                a_only=row["a_correct_b_wrong"],
                b_only=row["b_correct_a_wrong"],
                delta="-" if delta is None else f"{delta:+.3f}",
                p="-" if p is None else f"{p:.4f}",
            )
        )
    lines.append("")


def build_markdown(payload: Dict[str, Any]) -> str:
    comparison = payload["numeric_semantic_comparison"]["counts"]
    lines = [
        "# MATH Semantic Correctness Audit",
        "",
        "This audit re-extracts raw final-answer strings from saved peer-exposure outputs and compares them to original MATH boxed answers with conservative symbolic checks. It does not run the model again.",
        "",
        "## Source Surface",
        "",
        f"- Source cases: `{payload['num_cases']}`",
        f"- Records: `{payload['num_records']}`",
        f"- Source-label-reliable cases: `{payload['num_source_label_reliable_cases']}`",
        f"- Source-label-unknown/unreliable cases: `{payload['num_cases'] - payload['num_source_label_reliable_cases']}`",
        "",
        "## Numeric-vs-Semantic Label Changes",
        "",
        "| Bucket | Records |",
        "| --- | ---: |",
    ]
    for key, value in sorted(comparison.items()):
        lines.append(f"| {key} | {value} |")
    lines.append("")
    append_rate_table(lines, "All Source Cases", payload["rates_all_cases"])
    append_pair_table(lines, "All Source Cases Paired Correctness", payload["paired_all_cases"])
    append_rate_table(lines, "Source-Label-Reliable Cases", payload["rates_reliable_source_cases"])
    append_pair_table(lines, "Source-Label-Reliable Paired Correctness", payload["paired_reliable_source_cases"])
    lines.extend(
        [
            "## Notes",
            "",
            "- `unparseable / records` means semantic unknown here, not necessarily missing text.",
            "- Source-label-reliable cases are those where the saved `correct_peer` response is semantically correct and the saved `wrong_peer` response is semantically wrong against the original boxed answer.",
            "- Peer-answer adoption is intentionally not recomputed here because the saved peer answer fields came from the older numeric parser.",
            "- Cases with `unknown_semantic_parse` should be inspected before becoming claim-bearing evidence.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cases-jsonl", type=Path, required=True)
    parser.add_argument("--records-jsonl", type=Path, required=True)
    parser.add_argument("--math-jsonl", type=Path, required=True)
    parser.add_argument("--out-records-jsonl", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    source_cases = read_jsonl(args.source_cases_jsonl)
    records = read_jsonl(args.records_jsonl)
    math_rows = read_math_data(args.math_jsonl)
    source_audit = build_source_case_audit(source_cases, math_rows)
    semantic_records = [semantic_record(record, source_audit[case_id(record)]) for record in records]
    write_jsonl(args.out_records_jsonl, semantic_records)

    reliable_case_ids = {
        cid for cid, audit in source_audit.items() if audit["source_labels_semantically_reliable"]
    }
    reliable_records = subset_by_reliable_source(semantic_records, reliable_case_ids)
    table_all = by_case_condition(semantic_records)
    table_reliable = by_case_condition(reliable_records)
    payload = {
        "source_cases_jsonl": str(args.source_cases_jsonl),
        "records_jsonl": str(args.records_jsonl),
        "math_jsonl": str(args.math_jsonl),
        "out_records_jsonl": str(args.out_records_jsonl),
        "num_cases": len(source_cases),
        "num_records": len(records),
        "num_source_label_reliable_cases": len(reliable_case_ids),
        "source_case_audit": list(source_audit.values()),
        "numeric_semantic_comparison": compare_numeric_semantic(semantic_records),
        "rates_all_cases": rate_payload(table_all),
        "paired_all_cases": [paired_correctness(table_all, a, b) for a, b in PAIRED_TARGETS],
        "rates_reliable_source_cases": rate_payload(table_reliable),
        "paired_reliable_source_cases": [paired_correctness(table_reliable, a, b) for a, b in PAIRED_TARGETS],
    }
    write_json(args.out_json, payload)
    args.out_md.write_text(build_markdown(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
