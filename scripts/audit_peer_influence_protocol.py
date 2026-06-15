#!/usr/bin/env python3
"""Build a KAIROS-style protocol readout for peer-influence records."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from audit_peer_exposure_statistics import wilson_interval
from peer_probe.io_utils import read_jsonl, write_json


CONDITIONS = [
    "no_peer",
    "correct_answer_only",
    "wrong_answer_only",
    "correct_raw_answer_only",
    "wrong_raw_answer_only",
    "correct_rationale",
    "wrong_rationale",
    "correct_redacted_rationale",
    "wrong_redacted_rationale",
    "correct_equation_surface",
    "wrong_equation_surface",
    "correct_typed_public_state",
    "wrong_typed_public_state",
]

CONDITION_META: Dict[str, Dict[str, Any]] = {
    "no_peer": {
        "peer_polarity": "none",
        "surface": "no_peer",
        "visible_slots": [],
        "hidden_slots": [],
    },
    "correct_answer_only": {
        "peer_polarity": "correct",
        "surface": "answer_only",
        "visible_slots": ["final_answer_authority"],
        "hidden_slots": ["relation_skeleton", "numeric_role_slots", "equation_surface"],
    },
    "wrong_answer_only": {
        "peer_polarity": "wrong",
        "surface": "answer_only",
        "visible_slots": ["final_answer_authority"],
        "hidden_slots": ["relation_skeleton", "numeric_role_slots", "equation_surface"],
    },
    "correct_raw_answer_only": {
        "peer_polarity": "correct",
        "surface": "raw_answer_only",
        "visible_slots": ["final_answer_authority"],
        "hidden_slots": ["relation_skeleton", "numeric_role_slots", "equation_surface"],
    },
    "wrong_raw_answer_only": {
        "peer_polarity": "wrong",
        "surface": "raw_answer_only",
        "visible_slots": ["final_answer_authority"],
        "hidden_slots": ["relation_skeleton", "numeric_role_slots", "equation_surface"],
    },
    "correct_rationale": {
        "peer_polarity": "correct",
        "surface": "full_rationale",
        "visible_slots": [
            "final_answer_authority",
            "relation_skeleton",
            "numeric_role_slots",
            "equation_surface",
            "natural_language_rationale",
        ],
        "hidden_slots": [],
    },
    "wrong_rationale": {
        "peer_polarity": "wrong",
        "surface": "full_rationale",
        "visible_slots": [
            "final_answer_authority",
            "relation_skeleton",
            "numeric_role_slots",
            "equation_surface",
            "natural_language_rationale",
        ],
        "hidden_slots": [],
    },
    "correct_redacted_rationale": {
        "peer_polarity": "correct",
        "surface": "redacted_rationale",
        "visible_slots": ["relation_skeleton", "numeric_role_slots", "equation_surface"],
        "hidden_slots": ["explicit_final_answer_slot"],
    },
    "wrong_redacted_rationale": {
        "peer_polarity": "wrong",
        "surface": "redacted_rationale",
        "visible_slots": ["relation_skeleton", "numeric_role_slots", "equation_surface"],
        "hidden_slots": ["explicit_final_answer_slot"],
    },
    "correct_equation_surface": {
        "peer_polarity": "correct",
        "surface": "equation_surface",
        "visible_slots": ["numeric_role_slots", "equation_surface"],
        "hidden_slots": ["explicit_final_answer_slot", "full_natural_language_rationale"],
    },
    "wrong_equation_surface": {
        "peer_polarity": "wrong",
        "surface": "equation_surface",
        "visible_slots": ["numeric_role_slots", "equation_surface"],
        "hidden_slots": ["explicit_final_answer_slot", "full_natural_language_rationale"],
    },
    "correct_typed_public_state": {
        "peer_polarity": "correct",
        "surface": "typed_public_state",
        "visible_slots": ["target_predicate", "relation_or_equation_evidence", "numeric_role_slots"],
        "hidden_slots": ["source_identity", "explicit_final_answer_slot"],
    },
    "wrong_typed_public_state": {
        "peer_polarity": "wrong",
        "surface": "typed_public_state",
        "visible_slots": ["target_predicate", "relation_or_equation_evidence", "numeric_role_slots"],
        "hidden_slots": ["source_identity", "explicit_final_answer_slot"],
    },
}


def case_id(record: Dict[str, Any]) -> str:
    return str(record.get("case_index", record.get("instance_id")))


def by_case_condition(rows: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    table: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        table[case_id(row)][str(row["condition"])] = row
    return dict(table)


def is_known(value: Any) -> bool:
    return isinstance(value, bool)


def source_label_reliable(record: Dict[str, Any]) -> bool:
    semantic = record.get("semantic_eval") or {}
    return semantic.get("source_labels_semantically_reliable") is True


def rate_payload(successes: int, total: int) -> Dict[str, Any]:
    return {
        "successes": successes,
        "total": total,
        "rate": successes / total if total else None,
        "wilson_95": wilson_interval(successes, total),
    }


def correctness_counts(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    correct = sum(1 for row in rows if row.get("post_exposure_correct") is True)
    wrong = sum(1 for row in rows if row.get("post_exposure_correct") is False)
    unknown = sum(1 for row in rows if not is_known(row.get("post_exposure_correct")))
    known = correct + wrong
    return {
        "records": len(rows),
        "post_correct_records": correct,
        "post_wrong_records": wrong,
        "semantic_unknown_records": unknown,
        "post_known_records": known,
        "record_accuracy": rate_payload(correct, len(rows)),
        "known_accuracy": rate_payload(correct, known),
        "semantic_unknown_rate": rate_payload(unknown, len(rows)),
    }


def transition_metric(
    table: Dict[str, Dict[str, Dict[str, Any]]],
    condition: str,
    *,
    baseline_value: bool,
    target_value: Optional[bool],
) -> Dict[str, Any]:
    successes: List[str] = []
    denominator: List[str] = []
    unknowns: List[str] = []
    for cid, rows in table.items():
        baseline = rows.get("no_peer")
        row = rows.get(condition)
        if baseline is None or row is None:
            continue
        if baseline.get("post_exposure_correct") is not baseline_value:
            continue
        denominator.append(cid)
        post = row.get("post_exposure_correct")
        if post is target_value:
            successes.append(cid)
        elif not is_known(post):
            unknowns.append(cid)
    payload = rate_payload(len(successes), len(denominator))
    payload.update({"case_ids": successes, "unknown_case_ids": unknowns})
    return payload


def adoption_metric(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    eligible = [row for row in rows if row.get("condition") != "no_peer"]
    successes = [case_id(row) for row in eligible if row.get("peer_answer_adopted") is True]
    payload = rate_payload(len(successes), len(eligible))
    payload["case_ids"] = successes
    return payload


def condition_rows(table: Dict[str, Dict[str, Dict[str, Any]]], condition: str) -> List[Dict[str, Any]]:
    return [rows[condition] for rows in table.values() if condition in rows]


def paired_record_accuracy_delta(
    table: Dict[str, Dict[str, Dict[str, Any]]],
    condition: str,
) -> Dict[str, Any]:
    baseline_successes = 0
    condition_successes = 0
    total = 0
    for rows in table.values():
        baseline = rows.get("no_peer")
        row = rows.get(condition)
        if baseline is None or row is None:
            continue
        total += 1
        if baseline.get("post_exposure_correct") is True:
            baseline_successes += 1
        if row.get("post_exposure_correct") is True:
            condition_successes += 1
    baseline_rate = baseline_successes / total if total else None
    condition_rate = condition_successes / total if total else None
    return {
        "baseline_successes": baseline_successes,
        "condition_successes": condition_successes,
        "total": total,
        "baseline_record_accuracy": baseline_rate,
        "condition_record_accuracy": condition_rate,
        "delta_condition_minus_no_peer": (
            condition_rate - baseline_rate
            if baseline_rate is not None and condition_rate is not None
            else None
        ),
    }


def condition_metrics(
    table: Dict[str, Dict[str, Dict[str, Any]]],
    condition: str,
) -> Dict[str, Any]:
    rows = condition_rows(table, condition)
    metrics = {
        "condition": condition,
        "meta": CONDITION_META[condition],
        "correctness": correctness_counts(rows),
        "robustness": paired_record_accuracy_delta(table, condition),
    }
    if condition == "no_peer":
        metrics.update(
            {
                "utility": None,
                "resistance": None,
                "harm": None,
                "unknown_after_baseline_correct": None,
                "unknown_after_baseline_wrong": None,
                "peer_answer_adoption": None,
            }
        )
        return metrics
    metrics.update(
        {
            "utility": transition_metric(
                table,
                condition,
                baseline_value=False,
                target_value=True,
            ),
            "resistance": transition_metric(
                table,
                condition,
                baseline_value=True,
                target_value=True,
            ),
            "harm": transition_metric(
                table,
                condition,
                baseline_value=True,
                target_value=False,
            ),
            "unknown_after_baseline_correct": transition_metric(
                table,
                condition,
                baseline_value=True,
                target_value=None,
            ),
            "unknown_after_baseline_wrong": transition_metric(
                table,
                condition,
                baseline_value=False,
                target_value=None,
            ),
            "peer_answer_adoption": adoption_metric(rows),
        }
    )
    return metrics


def sort_key_for_condition(condition: str) -> Tuple[int, str]:
    try:
        return CONDITIONS.index(condition), condition
    except ValueError:
        return len(CONDITIONS), condition


def subset_payload(name: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    table = by_case_condition(rows)
    case_ids = sorted(table, key=lambda value: int(value) if value.isdigit() else value)
    present_conditions = sorted(
        {condition for per_case in table.values() for condition in per_case},
        key=sort_key_for_condition,
    )
    metrics = [condition_metrics(table, condition) for condition in present_conditions]
    return {
        "name": name,
        "num_cases": len(table),
        "num_records": len(rows),
        "case_ids": case_ids,
        "conditions": metrics,
        "readout": build_readout(metrics),
    }


def metric_rate(metric: Optional[Dict[str, Any]]) -> Optional[float]:
    if not metric:
        return None
    return metric.get("rate")


def find_metric(metrics: List[Dict[str, Any]], condition: str) -> Optional[Dict[str, Any]]:
    return next((row for row in metrics if row["condition"] == condition), None)


def build_readout(metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    wrong = [row for row in metrics if row["meta"]["peer_polarity"] == "wrong"]
    correct = [row for row in metrics if row["meta"]["peer_polarity"] == "correct"]
    wrong_harm_rank = sorted(
        (
            {
                "condition": row["condition"],
                "surface": row["meta"]["surface"],
                "harm": row["harm"],
                "resistance": row["resistance"],
            }
            for row in wrong
            if row.get("harm")
        ),
        key=lambda item: (-1 if metric_rate(item["harm"]) is None else -metric_rate(item["harm"]), item["condition"]),
    )
    correct_utility_rank = sorted(
        (
            {
                "condition": row["condition"],
                "surface": row["meta"]["surface"],
                "utility": row["utility"],
                "record_accuracy": row["correctness"]["record_accuracy"],
            }
            for row in correct
            if row.get("utility")
        ),
        key=lambda item: (-1 if metric_rate(item["utility"]) is None else -metric_rate(item["utility"]), item["condition"]),
    )
    typed_wrong = find_metric(metrics, "wrong_typed_public_state")
    equation_wrong = find_metric(metrics, "wrong_equation_surface")
    rationale_wrong = find_metric(metrics, "wrong_rationale")
    typed_correct = find_metric(metrics, "correct_typed_public_state")
    rationale_correct = find_metric(metrics, "correct_rationale")
    raw_wrong = find_metric(metrics, "wrong_raw_answer_only")
    legacy_wrong = find_metric(metrics, "wrong_answer_only")
    raw_correct = find_metric(metrics, "correct_raw_answer_only")
    legacy_correct = find_metric(metrics, "correct_answer_only")
    return {
        "wrong_harm_rank": wrong_harm_rank,
        "correct_utility_rank": correct_utility_rank,
        "typed_vs_full_rationale_harm_delta": delta_metric(typed_wrong, rationale_wrong, "harm"),
        "typed_vs_equation_harm_delta": delta_metric(typed_wrong, equation_wrong, "harm"),
        "typed_vs_full_rationale_utility_delta": delta_metric(
            typed_correct,
            rationale_correct,
            "utility",
        ),
        "raw_vs_legacy_answer_harm_delta": delta_metric(raw_wrong, legacy_wrong, "harm"),
        "raw_vs_legacy_answer_utility_delta": delta_metric(raw_correct, legacy_correct, "utility"),
        "flags": build_flags(metrics),
    }


def delta_metric(
    left: Optional[Dict[str, Any]],
    right: Optional[Dict[str, Any]],
    metric_name: str,
) -> Optional[Dict[str, Any]]:
    if left is None or right is None:
        return None
    left_rate = metric_rate(left.get(metric_name))
    right_rate = metric_rate(right.get(metric_name))
    return {
        "left_condition": left["condition"],
        "right_condition": right["condition"],
        "metric": metric_name,
        "left_rate": left_rate,
        "right_rate": right_rate,
        "delta_left_minus_right": (
            left_rate - right_rate if left_rate is not None and right_rate is not None else None
        ),
    }


def build_flags(metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    flags: List[Dict[str, Any]] = []
    for row in metrics:
        polarity = row["meta"]["peer_polarity"]
        harm_rate = metric_rate(row.get("harm"))
        utility_rate = metric_rate(row.get("utility"))
        unknown_rate = metric_rate(row["correctness"]["semantic_unknown_rate"])
        if polarity == "wrong" and harm_rate is not None and harm_rate >= 0.20:
            flags.append(
                {
                    "condition": row["condition"],
                    "flag": "high_harm",
                    "rate": harm_rate,
                    "threshold": 0.20,
                }
            )
        if polarity == "correct" and utility_rate is not None and utility_rate <= 0.15:
            flags.append(
                {
                    "condition": row["condition"],
                    "flag": "low_utility",
                    "rate": utility_rate,
                    "threshold": 0.15,
                }
            )
        if unknown_rate is not None and unknown_rate >= 0.20:
            flags.append(
                {
                    "condition": row["condition"],
                    "flag": "unknown_heavy",
                    "rate": unknown_rate,
                    "threshold": 0.20,
                }
            )
    return flags


def fmt_rate(metric: Optional[Dict[str, Any]]) -> str:
    if metric is None:
        return "-"
    rate = metric.get("rate")
    if rate is None:
        return "-"
    return f"{metric['successes']}/{metric['total']} ({rate:.3f})"


def fmt_plain_rate(value: Optional[float]) -> str:
    return "-" if value is None else f"{value:+.3f}"


def fmt_metric_count(metric: Optional[Dict[str, Any]]) -> str:
    if metric is None:
        return "-"
    return f"{metric['successes']}/{metric['total']}"


def append_protocol_table(lines: List[str], subset: Dict[str, Any]) -> None:
    lines.extend(
        [
            f"## {subset['name']}",
            "",
            f"- Cases: `{subset['num_cases']}`",
            f"- Records: `{subset['num_records']}`",
            "",
            "| Condition | Peer | Surface | Correct / records | Known acc | Unknown | Utility | Resistance | Harm | Robustness | Adoption |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in subset["conditions"]:
        correctness = row["correctness"]
        robustness = row["robustness"]["delta_condition_minus_no_peer"]
        lines.append(
            "| {condition} | {peer} | {surface} | {record_acc} | {known_acc} | {unknown} | {utility} | {resistance} | {harm} | {robustness} | {adoption} |".format(
                condition=row["condition"],
                peer=row["meta"]["peer_polarity"],
                surface=row["meta"]["surface"],
                record_acc=fmt_rate(correctness["record_accuracy"]),
                known_acc=fmt_rate(correctness["known_accuracy"]),
                unknown=fmt_rate(correctness["semantic_unknown_rate"]),
                utility=fmt_rate(row.get("utility")),
                resistance=fmt_rate(row.get("resistance")),
                harm=fmt_rate(row.get("harm")),
                robustness=fmt_plain_rate(robustness),
                adoption=fmt_rate(row.get("peer_answer_adoption")),
            )
        )
    lines.append("")


def append_readout(lines: List[str], subset: Dict[str, Any]) -> None:
    readout = subset["readout"]
    lines.extend([f"## {subset['name']} Readout", ""])
    harm_rank = readout["wrong_harm_rank"][:5]
    utility_rank = readout["correct_utility_rank"][:5]
    if harm_rank:
        lines.append("Wrong-peer harm ranking:")
        for item in harm_rank:
            lines.append(
                f"- `{item['condition']}` / `{item['surface']}`: harm {fmt_rate(item['harm'])}; resistance {fmt_rate(item['resistance'])}"
            )
        lines.append("")
    if utility_rank:
        lines.append("Correct-peer utility ranking:")
        for item in utility_rank:
            lines.append(
                f"- `{item['condition']}` / `{item['surface']}`: utility {fmt_rate(item['utility'])}"
            )
        lines.append("")
    for key in [
        "typed_vs_full_rationale_harm_delta",
        "typed_vs_equation_harm_delta",
        "typed_vs_full_rationale_utility_delta",
        "raw_vs_legacy_answer_harm_delta",
        "raw_vs_legacy_answer_utility_delta",
    ]:
        delta = readout.get(key)
        if not delta:
            continue
        lines.append(
            "- `{left}` vs `{right}` {metric} delta: {delta}".format(
                left=delta["left_condition"],
                right=delta["right_condition"],
                metric=delta["metric"],
                delta=fmt_plain_rate(delta["delta_left_minus_right"]),
            )
        )
    if readout["flags"]:
        lines.append("")
        lines.append("Protocol flags:")
        for flag in readout["flags"]:
            lines.append(
                f"- `{flag['condition']}`: `{flag['flag']}` {flag['rate']:.3f} (threshold {flag['threshold']:.2f})"
            )
    lines.append("")


def build_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# Slot-Level Peer Influence Protocol Audit",
        "",
        "This is a protocol readout over saved semantic peer-exposure records. It does not run the model again.",
        "",
        "## Metric Definitions",
        "",
        "- `Utility`: among no-peer-known-wrong cases, the peer-exposed answer becomes correct.",
        "- `Resistance`: among no-peer-known-correct cases, the peer-exposed answer stays correct.",
        "- `Harm`: among no-peer-known-correct cases, the peer-exposed answer becomes wrong.",
        "- `Robustness`: record-level accuracy delta versus the paired no-peer baseline, with semantic unknown counted as not correct.",
        "- `Adoption`: saved peer-answer adoption flag from the original probe; this is not recomputed by semantic equivalence.",
        "- Semantic unknowns remain in denominators for utility/resistance/harm, so these rates are conservative.",
        "",
    ]
    for subset in payload["subsets"]:
        append_protocol_table(lines, subset)
        append_readout(lines, subset)
    lines.extend(
        [
            "## Field Inventory",
            "",
            "| Condition | Visible slots | Hidden slots |",
            "| --- | --- | --- |",
        ]
    )
    for condition in CONDITIONS:
        meta = CONDITION_META[condition]
        visible = ", ".join(meta["visible_slots"]) if meta["visible_slots"] else "-"
        hidden = ", ".join(meta["hidden_slots"]) if meta["hidden_slots"] else "-"
        lines.append(f"| `{condition}` | {visible} | {hidden} |")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- MATH here should be read as a peer-influence diagnostic on math reasoning cases, not a general multi-agent communication benchmark.",
            "- Typed public state is treated as one diagnostic surface in the field inventory, not as a method claim.",
            "- Source-label-reliable cases require the saved correct peer to be semantically correct and the saved wrong peer to be semantically wrong against the original boxed answer.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_payload(records_path: Path, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    reliable_rows = [row for row in rows if source_label_reliable(row)]
    payload = {
        "records_jsonl": str(records_path),
        "num_records": len(rows),
        "num_cases": len(by_case_condition(rows)),
        "condition_meta": CONDITION_META,
        "subsets": [
            subset_payload("All Source Cases", rows),
            subset_payload("Source-Label-Reliable Cases", reliable_rows),
        ],
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records-jsonl", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    rows = read_jsonl(args.records_jsonl)
    payload = build_payload(args.records_jsonl, rows)
    write_json(args.out_json, payload)
    args.out_md.write_text(build_markdown(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
