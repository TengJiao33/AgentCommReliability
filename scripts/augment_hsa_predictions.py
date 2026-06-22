#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


TASK_NAME = "hsa_v0_sseac_candidate_units"


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


def parse_json_object_loose(blob: Any) -> tuple[dict[str, Any], str | None]:
    if isinstance(blob, dict):
        return blob, None
    if not isinstance(blob, str):
        return {}, "response_not_object_or_string"
    text = blob.strip()
    fence = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {}, "no_json_object"
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as error:
            return {}, f"json_decode_error: {error}"
    if not isinstance(parsed, dict):
        return {}, "response_not_object"
    return parsed, None


def as_list(blob: Any) -> list[Any]:
    return blob if isinstance(blob, list) else []


def as_str_list(blob: Any) -> list[str]:
    return [item for item in as_list(blob) if isinstance(item, str)]


def visible_verified_blocker(card: dict[str, Any], final_decider: str) -> bool:
    return (
        card.get("evidence_type") == "blocker"
        and card.get("verification_state") == "verified"
        and final_decider in set(as_str_list(card.get("recipient_scope")))
    )


def visible_verified_support(card: dict[str, Any], final_decider: str) -> bool:
    return (
        card.get("evidence_type") == "support"
        and card.get("verification_state") == "verified"
        and final_decider in set(as_str_list(card.get("recipient_scope")))
    )


def normalize_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def card_matches_decision(card: dict[str, Any], decision: str) -> bool:
    normalized_decision = normalize_text(decision)
    if not normalized_decision or normalized_decision == "insufficient evidence":
        return False
    haystack = " ".join(
        normalize_text(card.get(key, ""))
        for key in ("card_id", "content", "source_id")
    )
    if normalized_decision in haystack:
        return True
    decision_tokens = [token for token in normalized_decision.split() if len(token) >= 3]
    if not decision_tokens:
        return False
    return all(token in haystack for token in decision_tokens)


def final_decider_candidate_card_ids(response: dict[str, Any], final_decider: str) -> set[str]:
    seen: set[str] = set()
    for unit in as_list(response.get("candidate_units")):
        if not isinstance(unit, dict):
            continue
        if str(unit.get("recipient", "")) != final_decider:
            continue
        seen.update(as_str_list(unit.get("card_ids")))
    return seen


def ensure_candidate_units(response: dict[str, Any]) -> list[dict[str, Any]]:
    units = response.get("candidate_units")
    if isinstance(units, list):
        return units
    response["candidate_units"] = []
    return response["candidate_units"]


def augment_visible_verified_blockers(packet: dict[str, Any], prediction: dict[str, Any], include_decision_support: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    out = dict(prediction)
    response, parse_error = parse_json_object_loose(prediction.get("response"))
    trace: dict[str, Any] = {
        "strategy": "visible_verified_blocker_and_decision_support_completion" if include_decision_support else "visible_verified_blocker_completion",
        "added_units": [],
        "skipped": [],
    }
    if parse_error:
        trace["parse_error"] = parse_error
        out["augmentation_trace"] = trace
        return out, trace

    response = dict(response)
    units = ensure_candidate_units(response)
    final_decider = str(packet.get("final_decider", "final_decider"))
    existing = final_decider_candidate_card_ids(response, final_decider)
    added_index = 0
    final_decision = str(response.get("final_decision", ""))
    for card in as_list(packet.get("source_cards")):
        if not isinstance(card, dict):
            continue
        card_id = str(card.get("card_id", ""))
        if not card_id or not visible_verified_blocker(card, final_decider):
            continue
        if card_id in existing:
            trace["skipped"].append({"card_id": card_id, "reason": "already_present"})
            continue
        unit_id = f"auto_visible_blocker_{added_index}_{card_id}"
        units.append(
            {
                "unit_id": unit_id,
                "recipient": final_decider,
                "card_ids": [card_id],
                "priority": 9.5,
                "claimed_slots": [f"visible_verified_blocker:{card_id}"],
                "claimed_effect": "Auditable completion: retain a verified blocker card visible to the final decider.",
            }
        )
        existing.add(card_id)
        added_index += 1
        trace["added_units"].append(
            {
                "unit_id": unit_id,
                "card_id": card_id,
                "source_role": card.get("source_role"),
                "evidence_type": card.get("evidence_type"),
                "verification_state": card.get("verification_state"),
                "recipient_scope": card.get("recipient_scope", []),
            }
        )

    if include_decision_support:
        for card in as_list(packet.get("source_cards")):
            if not isinstance(card, dict):
                continue
            card_id = str(card.get("card_id", ""))
            if not card_id or not visible_verified_support(card, final_decider):
                continue
            if not card_matches_decision(card, final_decision):
                trace["skipped"].append({"card_id": card_id, "reason": "support_not_matched_to_model_decision"})
                continue
            if card_id in existing:
                trace["skipped"].append({"card_id": card_id, "reason": "already_present"})
                continue
            unit_id = f"auto_visible_support_{added_index}_{card_id}"
            units.append(
                {
                    "unit_id": unit_id,
                    "recipient": final_decider,
                    "card_ids": [card_id],
                    "priority": 9.0,
                    "claimed_slots": [f"visible_verified_support:{card_id}"],
                    "claimed_effect": "Auditable completion: retain a verified support card visible to the final decider and matching the model decision.",
                }
            )
            existing.add(card_id)
            added_index += 1
            trace["added_units"].append(
                {
                    "unit_id": unit_id,
                    "card_id": card_id,
                    "source_role": card.get("source_role"),
                    "evidence_type": card.get("evidence_type"),
                    "verification_state": card.get("verification_state"),
                    "recipient_scope": card.get("recipient_scope", []),
                    "matched_decision": final_decision,
                }
            )

    out["response"] = response
    out["augmentation_trace"] = trace
    out["task"] = prediction.get("task", TASK_NAME)
    out["status"] = prediction.get("status", "ok")
    return out, trace


def main() -> None:
    parser = argparse.ArgumentParser(description="Add auditable HSA candidate-unit completions to existing model predictions.")
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument(
        "--strategy",
        choices=["visible_verified_blocker_completion", "visible_verified_blocker_and_decision_support_completion"],
        default="visible_verified_blocker_completion",
    )
    args = parser.parse_args()

    packets = {row["packet_id"]: row for row in read_jsonl(args.packet)}
    augmented: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    for prediction in read_jsonl(args.predictions):
        packet_id = prediction.get("packet_id")
        packet = packets.get(packet_id)
        if packet is None:
            out = dict(prediction)
            trace = {"packet_id": packet_id, "strategy": args.strategy, "error": "packet_not_found", "added_units": []}
        else:
            out, trace = augment_visible_verified_blockers(
                packet,
                prediction,
                include_decision_support=args.strategy == "visible_verified_blocker_and_decision_support_completion",
            )
            trace = {"packet_id": packet_id, **trace}
        augmented.append(out)
        traces.append(trace)

    write_jsonl(args.out, augmented)
    summary = {
        "strategy": args.strategy,
        "prediction_rows": len(augmented),
        "rows_with_added_units": sum(1 for trace in traces if trace.get("added_units")),
        "added_unit_count": sum(len(trace.get("added_units", [])) for trace in traces),
        "added_by_packet": {
            str(trace.get("packet_id")): trace.get("added_units", [])
            for trace in traces
            if trace.get("added_units")
        },
        "parse_errors": [
            {"packet_id": trace.get("packet_id"), "parse_error": trace.get("parse_error")}
            for trace in traces
            if trace.get("parse_error")
        ],
    }
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
