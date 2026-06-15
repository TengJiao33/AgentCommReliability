#!/usr/bin/env python3
"""Compare peer-influence protocol audits across source-label modes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


KEY_CONDITIONS = [
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


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_mode_arg(value: str) -> Tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Expected MODE=PATH")
    mode, raw_path = value.split("=", 1)
    mode = mode.strip()
    if not mode:
        raise argparse.ArgumentTypeError("Mode cannot be empty")
    return mode, Path(raw_path)


def rate(metric: Optional[Dict[str, Any]]) -> Optional[float]:
    if not metric:
        return None
    return metric.get("rate")


def count_text(metric: Optional[Dict[str, Any]]) -> str:
    if not metric:
        return "-"
    value = metric.get("rate")
    if value is None:
        return "-"
    return f"{metric['successes']}/{metric['total']} ({value:.3f})"


def subset_by_name(audit: Dict[str, Any], name: str) -> Dict[str, Any]:
    for subset in audit.get("subsets") or []:
        if subset.get("name") == name:
            return subset
    raise KeyError(f"Subset not found: {name}")


def condition_by_name(subset: Dict[str, Any], condition: str) -> Optional[Dict[str, Any]]:
    for row in subset.get("conditions") or []:
        if row.get("condition") == condition:
            return row
    return None


def condition_summary(mode: str, subset_name: str, row: Dict[str, Any]) -> Dict[str, Any]:
    correctness = row["correctness"]
    robustness = row["robustness"]
    return {
        "mode": mode,
        "subset": subset_name,
        "condition": row["condition"],
        "peer_polarity": row["meta"]["peer_polarity"],
        "surface": row["meta"]["surface"],
        "record_accuracy": correctness["record_accuracy"],
        "known_accuracy": correctness["known_accuracy"],
        "semantic_unknown_rate": correctness["semantic_unknown_rate"],
        "utility": row.get("utility"),
        "resistance": row.get("resistance"),
        "harm": row.get("harm"),
        "robustness_delta": robustness.get("delta_condition_minus_no_peer"),
        "peer_answer_adoption": row.get("peer_answer_adoption"),
    }


def build_payload(mode_paths: List[Tuple[str, Path]], reference_mode: str) -> Dict[str, Any]:
    audits = {mode: read_json(path) for mode, path in mode_paths}
    rows: List[Dict[str, Any]] = []
    for mode, audit in audits.items():
        for subset_name in ["All Source Cases", "Source-Label-Reliable Cases"]:
            subset = subset_by_name(audit, subset_name)
            for condition in KEY_CONDITIONS:
                row = condition_by_name(subset, condition)
                if row:
                    rows.append(condition_summary(mode, subset_name, row))

    deltas: List[Dict[str, Any]] = []
    by_key = {(row["mode"], row["subset"], row["condition"]): row for row in rows}
    for row in rows:
        if row["mode"] == reference_mode:
            continue
        ref = by_key.get((reference_mode, row["subset"], row["condition"]))
        if not ref:
            continue
        deltas.append(
            {
                "mode": row["mode"],
                "reference_mode": reference_mode,
                "subset": row["subset"],
                "condition": row["condition"],
                "surface": row["surface"],
                "harm_delta": none_delta(rate(row.get("harm")), rate(ref.get("harm"))),
                "utility_delta": none_delta(rate(row.get("utility")), rate(ref.get("utility"))),
                "resistance_delta": none_delta(rate(row.get("resistance")), rate(ref.get("resistance"))),
                "adoption_delta": none_delta(
                    rate(row.get("peer_answer_adoption")),
                    rate(ref.get("peer_answer_adoption")),
                ),
                "robustness_delta_delta": none_delta(
                    row.get("robustness_delta"),
                    ref.get("robustness_delta"),
                ),
            }
        )
    return {
        "reference_mode": reference_mode,
        "mode_paths": {mode: str(path) for mode, path in mode_paths},
        "rows": rows,
        "deltas": deltas,
    }


def none_delta(left: Optional[float], right: Optional[float]) -> Optional[float]:
    if left is None or right is None:
        return None
    return left - right


def fmt_delta(value: Optional[float]) -> str:
    return "-" if value is None else f"{value:+.3f}"


def build_markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# Peer Source-Label Packet Audit",
        "",
        f"Reference mode: `{payload['reference_mode']}`.",
        "",
        "This compares protocol-audit outputs across source-label modes. It does not rerun semantic evaluation or the model.",
        "",
        "## Source-Label-Reliable Metrics",
        "",
        "| Mode | Condition | Surface | Utility | Resistance | Harm | Robustness | Adoption | Unknown |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["rows"]:
        if row["subset"] != "Source-Label-Reliable Cases":
            continue
        lines.append(
            "| {mode} | {condition} | {surface} | {utility} | {resistance} | {harm} | {robustness} | {adoption} | {unknown} |".format(
                mode=row["mode"],
                condition=row["condition"],
                surface=row["surface"],
                utility=count_text(row.get("utility")),
                resistance=count_text(row.get("resistance")),
                harm=count_text(row.get("harm")),
                robustness=fmt_delta(row.get("robustness_delta")),
                adoption=count_text(row.get("peer_answer_adoption")),
                unknown=count_text(row.get("semantic_unknown_rate")),
            )
        )
    lines.extend(
        [
            "",
            "## Deltas Vs Reference",
            "",
            "| Mode | Subset | Condition | Harm delta | Utility delta | Resistance delta | Adoption delta | Robustness delta-delta |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in payload["deltas"]:
        if row["subset"] != "Source-Label-Reliable Cases":
            continue
        lines.append(
            "| {mode} | {subset} | {condition} | {harm} | {utility} | {resistance} | {adoption} | {robustness} |".format(
                mode=row["mode"],
                subset=row["subset"],
                condition=row["condition"],
                harm=fmt_delta(row["harm_delta"]),
                utility=fmt_delta(row["utility_delta"]),
                resistance=fmt_delta(row["resistance_delta"]),
                adoption=fmt_delta(row["adoption_delta"]),
                robustness=fmt_delta(row["robustness_delta_delta"]),
            )
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Large deltas here indicate source-label sensitivity; stable rows support content-field rather than identity-label influence.",
            "- Adoption is the saved peer-answer adoption flag from each protocol audit, not semantic recomputation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", action="append", type=parse_mode_arg, required=True, help="MODE=protocol_audit.json")
    parser.add_argument("--reference-mode", default="anonymous")
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    payload = build_payload(args.audit, args.reference_mode)
    write_json(args.out_json, payload)
    args.out_md.write_text(build_markdown(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
