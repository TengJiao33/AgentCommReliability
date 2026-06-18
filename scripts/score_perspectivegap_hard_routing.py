from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_json_response(text: str | None) -> Any:
    if text is None:
        raise ValueError("empty response")
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def parse_json_object_loose(text: str | None) -> dict[str, Any]:
    if text is None:
        raise ValueError("empty response")
    try:
        parsed = parse_json_response(text)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, ValueError):
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("response is not a JSON object")
    return parsed


def normalize_response(response: dict[str, Any]) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    role_blob = response.get("roles", response)
    if not isinstance(role_blob, dict):
        role_blob = {}
    roles: dict[str, list[dict[str, Any]]] = {}
    for role, items in role_blob.items():
        if not isinstance(items, list):
            continue
        normalized_items: list[dict[str, Any]] = []
        for item in items:
            if isinstance(item, str):
                normalized_items.append({"fragment_id": item})
            elif isinstance(item, dict):
                normalized_items.append(dict(item))
        roles[role] = normalized_items
    rejected_blob = response.get("rejected", [])
    rejected: list[dict[str, Any]] = []
    if isinstance(rejected_blob, list):
        for item in rejected_blob:
            if isinstance(item, str):
                rejected.append({"fragment_id": item})
            elif isinstance(item, dict):
                rejected.append(dict(item))
    return roles, rejected


def metric_values(strict_pass: bool, tp: int, fp: int, fn: int, distractor_leak: int) -> dict[str, float]:
    expected = tp + fn
    predicted = tp + fp
    return {
        "strict_pass": float(strict_pass),
        "net_match_score": max(0.0, (tp - fp - fn) / expected) if expected else 0.0,
        "required_coverage": tp / expected if expected else 0.0,
        "boundary_precision": tp / predicted if predicted else 0.0,
        "distractor_leakage": float(distractor_leak),
    }


def score_packet_row(row: dict[str, Any], response_text: str | None) -> dict[str, Any]:
    roles = row["roles"]
    reference_need_sets = {role: set(items) for role, items in row["reference_need_sets"].items()}
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    distractor_ids = {fragment["id"] for fragment in row["fragments"] if fragment.get("is_distractor")}
    expected_rejects = {item["fragment_id"] for item in row.get("reference_rejections", [])}
    reference_event_count = sum(len(items) for items in reference_need_sets.values())
    try:
        parsed = parse_json_object_loose(response_text)
        normalized_roles, rejected = normalize_response(parsed)
        parse_error = None
    except (json.JSONDecodeError, ValueError) as error:
        parsed = None
        normalized_roles = {}
        rejected = []
        parse_error = f"parse: {error}"

    tp = fp = fn = distractor_leak = 0
    source_checked = source_correct = 0
    visibility_checked = visibility_correct = 0
    budget_overrun = 0
    selected_needed_rejected = 0
    per_role: dict[str, Any] = {}
    for role in roles:
        expected = reference_need_sets.get(role, set())
        items = normalized_roles.get(role, [])
        raw_predicted_ids = {
            item.get("fragment_id")
            for item in items
            if isinstance(item.get("fragment_id"), str)
        }
        predicted_ids = {fragment_id for fragment_id in raw_predicted_ids if fragment_id in fragments}
        invalid_ids = raw_predicted_ids - set(fragments)
        extra = (predicted_ids - expected) | invalid_ids
        missing = expected - predicted_ids
        tp += len(predicted_ids & expected)
        fp += len(extra)
        fn += len(missing)
        distractor_leak += len(extra & distractor_ids)
        spent = sum(fragments[fragment_id]["cost"] for fragment_id in predicted_ids)
        budget = row["role_budgets"][role]
        budget_overrun += max(0, spent - budget)
        item_by_fragment = {
            item.get("fragment_id"): item
            for item in items
            if isinstance(item.get("fragment_id"), str)
        }
        role_source_checked = role_source_correct = 0
        role_visibility_checked = role_visibility_correct = 0
        for fragment_id in predicted_ids & expected:
            item = item_by_fragment.get(fragment_id, {})
            fragment = fragments[fragment_id]
            role_source_checked += 1
            source_checked += 1
            if item.get("source_id") == fragment["source_id"]:
                role_source_correct += 1
                source_correct += 1
            role_visibility_checked += 1
            visibility_checked += 1
            if item.get("visibility") == fragment["visibility_gold"]:
                role_visibility_correct += 1
                visibility_correct += 1
        per_role[role] = {
            "expected": sorted(expected),
            "predicted": sorted(raw_predicted_ids),
            "missing": sorted(missing),
            "extra": sorted(extra),
            "spent": spent,
            "budget": budget,
            "budget_pass": spent <= budget,
            "source_accuracy_on_tp": role_source_correct / role_source_checked if role_source_checked else 0.0,
            "visibility_accuracy_on_tp": (
                role_visibility_correct / role_visibility_checked if role_visibility_checked else 0.0
            ),
        }

    rejected_ids = {
        item.get("fragment_id")
        for item in rejected
        if isinstance(item.get("fragment_id"), str)
    }
    rejected_ids = {fragment_id for fragment_id in rejected_ids if fragment_id in fragments}
    for fragment_id in rejected_ids:
        needed_anywhere = any(fragment_id in expected for expected in reference_need_sets.values())
        if needed_anywhere:
            selected_needed_rejected += 1
    hard_pass = (
        parse_error is None
        and tp == reference_event_count
        and fp == 0
        and fn == 0
        and distractor_leak == 0
        and budget_overrun == 0
        and selected_needed_rejected == 0
        and expected_rejects.issubset(rejected_ids)
        and source_checked == reference_event_count
        and source_correct == source_checked
        and visibility_checked == reference_event_count
        and visibility_correct == visibility_checked
    )
    counts = {"tp": tp, "fp": fp, "fn": fn, "distractor_leak": distractor_leak}
    return {
        "hard_evaluation_id": row["hard_evaluation_id"],
        "base_evaluation_id": row["base_evaluation_id"],
        "scenario_id": row["scenario_id"],
        "shuffle_seed": row["shuffle_seed"],
        "pass": hard_pass,
        "metrics": {
            **metric_values(hard_pass, **counts),
            "budget_overrun": float(budget_overrun),
            "budget_pass": float(budget_overrun == 0),
            "source_accuracy_on_tp": source_correct / source_checked if source_checked else 0.0,
            "visibility_accuracy_on_tp": visibility_correct / visibility_checked if visibility_checked else 0.0,
            "reject_recall": len(expected_rejects & rejected_ids) / len(expected_rejects) if expected_rejects else 1.0,
            "needed_rejected": float(selected_needed_rejected),
        },
        "counts": counts,
        "aux_counts": {
            "source_checked": source_checked,
            "source_correct": source_correct,
            "visibility_checked": visibility_checked,
            "visibility_correct": visibility_correct,
        },
        "rejected": sorted(rejected_ids),
        "expected_rejections": sorted(expected_rejects),
        "per_role": per_role,
        "error": parse_error,
    }


def baseline_response(row: dict[str, Any], name: str) -> str:
    roles = row["roles"]
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    if name == "oracle":
        role_sets = {role: list(row["reference_need_sets"][role]) for role in roles}
        rejected = list(row.get("reference_rejections", []))
    elif name == "all_to_all":
        role_sets = {role: list(fragments) for role in roles}
        rejected = []
    elif name == "no_distractor_all_to_all":
        allowed = [fragment_id for fragment_id, fragment in fragments.items() if not fragment.get("is_distractor")]
        role_sets = {role: allowed for role in roles}
        rejected = [
            {"fragment_id": fragment_id, "source_id": fragment["source_id"], "reason": "distractor"}
            for fragment_id, fragment in fragments.items()
            if fragment.get("is_distractor")
        ]
    elif name == "shared_only":
        role_sets = {}
        for role in roles:
            role_sets[role] = [
                fragment_id
                for fragment_id, fragment in fragments.items()
                if fragment["visibility_gold"] == "shared_all"
            ]
        rejected = [
            {"fragment_id": fragment_id, "source_id": fragment["source_id"], "reason": "not_shared_all"}
            for fragment_id, fragment in fragments.items()
            if fragment["visibility_gold"] != "shared_all"
        ]
    elif name == "budget_cheapest":
        role_sets = {}
        for role in roles:
            budget = row["role_budgets"][role]
            spent = 0
            selected: list[str] = []
            for fragment_id, fragment in sorted(fragments.items(), key=lambda item: (item[1]["cost"], item[0])):
                if spent + fragment["cost"] <= budget:
                    selected.append(fragment_id)
                    spent += fragment["cost"]
            role_sets[role] = selected
        rejected = []
    else:
        raise ValueError(f"unknown baseline: {name}")
    response = {"roles": {}, "rejected": rejected}
    for role, fragment_ids in role_sets.items():
        response["roles"][role] = [
            {
                "fragment_id": fragment_id,
                "source_id": fragments[fragment_id]["source_id"],
                "visibility": fragments[fragment_id]["visibility_gold"]
                if fragments[fragment_id]["visibility_gold"] != "reject"
                else "role_private",
                "reason": name,
            }
            for fragment_id in fragment_ids
        ]
    return json.dumps(response, ensure_ascii=False)


def legacy_role_assignment_to_cards(row: dict[str, Any], response_text: str | None) -> str:
    parsed = parse_json_object_loose(response_text)
    fragments = {fragment["id"]: fragment for fragment in row["fragments"]}
    out: dict[str, Any] = {"roles": {}, "rejected": []}
    for role in row["roles"]:
        items = parsed.get(role, [])
        if not isinstance(items, list):
            items = []
        cards: list[dict[str, Any]] = []
        for fragment_id in items:
            if not isinstance(fragment_id, str):
                continue
            if fragment_id not in fragments:
                cards.append(
                    {
                        "fragment_id": fragment_id,
                        "reason": "projected_invalid_legacy_role_assignment",
                    }
                )
                continue
            fragment = fragments[fragment_id]
            visibility = fragment["visibility_gold"]
            if visibility == "reject":
                visibility = "role_private"
            cards.append(
                {
                    "fragment_id": fragment_id,
                    "source_id": fragment["source_id"],
                    "visibility": visibility,
                    "reason": "projected_from_legacy_role_assignment",
                }
            )
        out["roles"][role] = cards
    return json.dumps(out, ensure_ascii=False)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    strict_pass = sum(1 for row in rows if row["pass"])
    tp = sum(row["counts"]["tp"] for row in rows)
    fp = sum(row["counts"]["fp"] for row in rows)
    fn = sum(row["counts"]["fn"] for row in rows)
    leak = sum(row["counts"]["distractor_leak"] for row in rows)
    source_checked = sum(row.get("aux_counts", {}).get("source_checked", 0) for row in rows)
    source_correct = sum(row.get("aux_counts", {}).get("source_correct", 0) for row in rows)
    visibility_checked = sum(row.get("aux_counts", {}).get("visibility_checked", 0) for row in rows)
    visibility_correct = sum(row.get("aux_counts", {}).get("visibility_correct", 0) for row in rows)
    metric_names = [
        "budget_overrun",
        "budget_pass",
        "reject_recall",
        "needed_rejected",
    ]
    return {
        "evaluations": n,
        "strict_pass_count": strict_pass,
        "metrics": {
            "strict_pass": strict_pass / n if n else 0.0,
            "required_coverage": tp / (tp + fn) if tp + fn else 0.0,
            "boundary_precision": tp / (tp + fp) if tp + fp else 0.0,
            "distractor_leakage": leak / n if n else 0.0,
            "source_accuracy_on_tp": source_correct / source_checked if source_checked else 0.0,
            "visibility_accuracy_on_tp": (
                visibility_correct / visibility_checked if visibility_checked else 0.0
            ),
            **{name: sum(row["metrics"][name] for row in rows) / n if n else 0.0 for name in metric_names},
        },
        "counts": {"tp": tp, "fp": fp, "fn": fn, "distractor_leak": leak},
        "aux_counts": {
            "source_checked": source_checked,
            "source_correct": source_correct,
            "visibility_checked": visibility_checked,
            "visibility_correct": visibility_correct,
        },
    }


def format_summary(summary: dict[str, Any]) -> str:
    metrics = summary["metrics"]
    lines = [
        f"evaluations: {summary['evaluations']}",
        f"strict_pass: {metrics['strict_pass']:.4f} ({summary['strict_pass_count']}/{summary['evaluations']})",
        f"required_coverage: {metrics['required_coverage']:.4f}",
        f"boundary_precision: {metrics['boundary_precision']:.4f}",
        f"distractor_leakage: {metrics['distractor_leakage']:.4f}",
        f"budget_pass: {metrics['budget_pass']:.4f}",
        f"budget_overrun: {metrics['budget_overrun']:.4f}",
        f"source_accuracy_on_tp: {metrics['source_accuracy_on_tp']:.4f}",
        f"visibility_accuracy_on_tp: {metrics['visibility_accuracy_on_tp']:.4f}",
        f"reject_recall: {metrics['reject_recall']:.4f}",
        f"needed_rejected: {metrics['needed_rejected']:.4f}",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--baseline", choices=["oracle", "all_to_all", "no_distractor_all_to_all", "shared_only", "budget_cheapest"])
    parser.add_argument("--legacy-role-assignment", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    args = parser.parse_args()

    packet = read_jsonl(args.packet)
    predictions_by_id: dict[str, dict[str, Any]] = {}
    if args.predictions:
        for row in read_jsonl(args.predictions):
            if "hard_evaluation_id" in row:
                predictions_by_id[row["hard_evaluation_id"]] = row
            if "base_evaluation_id" in row:
                predictions_by_id[row["base_evaluation_id"]] = row
    if not args.baseline and not args.predictions:
        raise SystemExit("provide --baseline or --predictions")

    scored: list[dict[str, Any]] = []
    for row in packet:
        if args.baseline:
            response = baseline_response(row, args.baseline)
        else:
            prediction = predictions_by_id.get(row["hard_evaluation_id"]) or predictions_by_id.get(row["base_evaluation_id"], {})
            if args.legacy_role_assignment and prediction.get("response") is not None:
                try:
                    response = legacy_role_assignment_to_cards(row, prediction.get("response"))
                except (json.JSONDecodeError, ValueError):
                    response = prediction.get("response")
            else:
                response = prediction.get("response")
        scored.append(score_packet_row(row, response))
    write_jsonl(args.out, scored)
    summary = summarize(scored)
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(format_summary(summary) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
