#!/usr/bin/env python3
"""Build paired statistics for peer-exposure probe records."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> Optional[List[float]]:
    if total <= 0:
        return None
    phat = successes / total
    denom = 1 + z * z / total
    center = (phat + z * z / (2 * total)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return [max(0.0, center - margin), min(1.0, center + margin)]


def exact_binomial_two_sided(k: int, n: int, p: float = 0.5) -> Optional[float]:
    """Two-sided exact binomial p-value for small n by probability ordering."""
    if n <= 0:
        return None
    probs = [math.comb(n, i) * (p**i) * ((1 - p) ** (n - i)) for i in range(n + 1)]
    observed = probs[k]
    return min(1.0, sum(prob for prob in probs if prob <= observed + 1e-15))


def norm_case_id(record: Dict[str, Any]) -> str:
    return str(record.get("case_index", record.get("instance_id")))


def by_case_condition(rows: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    table: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        table[norm_case_id(row)][str(row["condition"])] = row
    return dict(table)


def is_known_bool(value: Any) -> bool:
    return isinstance(value, bool)


def condition_rate(
    table: Dict[str, Dict[str, Dict[str, Any]]],
    condition: str,
    *,
    numerator: str,
    denominator: str,
) -> Dict[str, Any]:
    total = 0
    successes = 0
    case_ids: List[str] = []
    for case_id, rows in table.items():
        row = rows.get(condition)
        if not row:
            continue
        pre = row.get("pre_exposure_correct")
        post = row.get("post_exposure_correct")
        if denominator == "records":
            eligible = True
        elif denominator == "pre_correct":
            eligible = pre is True
        elif denominator == "pre_wrong":
            eligible = pre is False
        elif denominator == "post_known":
            eligible = is_known_bool(post)
        else:
            raise ValueError(f"Unknown denominator: {denominator}")
        if not eligible:
            continue
        if numerator == "post_correct":
            success = post is True
        elif numerator == "right_to_wrong":
            success = pre is True and post is False
        elif numerator == "wrong_to_right":
            success = pre is False and post is True
        elif numerator == "stable_right":
            success = pre is True and post is True
        elif numerator == "unparseable":
            success = post is None
        elif numerator == "peer_answer_adopted":
            success = row.get("peer_answer_adopted") is True
        else:
            raise ValueError(f"Unknown numerator: {numerator}")
        total += 1
        if success:
            successes += 1
            case_ids.append(case_id)
    return {
        "condition": condition,
        "numerator": numerator,
        "denominator": denominator,
        "successes": successes,
        "total": total,
        "rate": successes / total if total else None,
        "wilson_95": wilson_interval(successes, total),
        "case_ids": case_ids,
    }


def paired_correctness(
    table: Dict[str, Dict[str, Dict[str, Any]]],
    condition_a: str,
    condition_b: str,
) -> Dict[str, Any]:
    a_only = []
    b_only = []
    both = []
    neither = []
    unknown = []
    for case_id, rows in table.items():
        a = rows.get(condition_a)
        b = rows.get(condition_b)
        if not a or not b:
            continue
        a_correct = a.get("post_exposure_correct")
        b_correct = b.get("post_exposure_correct")
        if not is_known_bool(a_correct) or not is_known_bool(b_correct):
            unknown.append(case_id)
            continue
        if a_correct and b_correct:
            both.append(case_id)
        elif a_correct and not b_correct:
            a_only.append(case_id)
        elif b_correct and not a_correct:
            b_only.append(case_id)
        else:
            neither.append(case_id)
    discordant = len(a_only) + len(b_only)
    return {
        "condition_a": condition_a,
        "condition_b": condition_b,
        "known_pairs": len(a_only) + len(b_only) + len(both) + len(neither),
        "unknown_pairs": len(unknown),
        "both_correct": len(both),
        "neither_correct": len(neither),
        "a_correct_b_wrong": len(a_only),
        "b_correct_a_wrong": len(b_only),
        "accuracy_delta_a_minus_b_on_known_pairs": (
            (len(a_only) - len(b_only)) / (len(a_only) + len(b_only) + len(both) + len(neither))
            if (len(a_only) + len(b_only) + len(both) + len(neither))
            else None
        ),
        "mcnemar_exact_two_sided_p": exact_binomial_two_sided(len(a_only), discordant),
        "a_only_case_ids": a_only,
        "b_only_case_ids": b_only,
        "unknown_case_ids": unknown,
    }


def build_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# Peer Exposure Statistical Audit",
        "",
        "Rates use Wilson 95% intervals. Paired correctness tests use an exact two-sided binomial sign test over discordant case pairs.",
        "",
        "## Key Rates",
        "",
        "| Condition | Metric | Count | Rate | Wilson 95% |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for rate in payload["rates"]:
        ci = rate["wilson_95"]
        ci_text = "-" if ci is None else f"[{ci[0]:.3f}, {ci[1]:.3f}]"
        lines.append(
            "| {condition} | {metric} | {successes}/{total} | {rate} | {ci} |".format(
                condition=rate["condition"],
                metric=f"{rate['numerator']} / {rate['denominator']}",
                successes=rate["successes"],
                total=rate["total"],
                rate="-" if rate["rate"] is None else f"{rate['rate']:.3f}",
                ci=ci_text,
            )
        )
    lines.extend(["", "## Paired Correctness", "", "| A | B | Known Pairs | A-only | B-only | Delta A-B | Exact p |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"])
    for cmp_row in payload["paired_correctness"]:
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
    lines.append("")
    lines.append("Case IDs for discordant pairs are in the JSON sidecar.")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records-jsonl", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    rows = read_jsonl(args.records_jsonl)
    table = by_case_condition(rows)

    conditions = [
        "no_peer",
        "wrong_answer_only",
        "wrong_raw_answer_only",
        "wrong_rationale",
        "wrong_redacted_rationale",
        "wrong_equation_surface",
        "wrong_typed_public_state",
        "correct_answer_only",
        "correct_raw_answer_only",
        "correct_rationale",
        "correct_redacted_rationale",
        "correct_equation_surface",
        "correct_typed_public_state",
    ]
    rates = []
    for condition in conditions:
        if condition.startswith("wrong_"):
            rates.append(condition_rate(table, condition, numerator="right_to_wrong", denominator="pre_correct"))
            rates.append(condition_rate(table, condition, numerator="stable_right", denominator="pre_correct"))
        if condition.startswith("correct_"):
            rates.append(condition_rate(table, condition, numerator="wrong_to_right", denominator="pre_wrong"))
        rates.append(condition_rate(table, condition, numerator="post_correct", denominator="records"))
        rates.append(condition_rate(table, condition, numerator="unparseable", denominator="records"))
        if condition != "no_peer":
            rates.append(condition_rate(table, condition, numerator="peer_answer_adopted", denominator="records"))

    paired_targets = [
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
    payload = {
        "records_jsonl": str(args.records_jsonl),
        "num_cases": len(table),
        "num_records": len(rows),
        "rates": rates,
        "paired_correctness": [paired_correctness(table, a, b) for a, b in paired_targets],
    }
    write_json(args.out_json, payload)
    args.out_md.write_text(build_markdown(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
