#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROUTING_COMPLETE = "routing_complete"


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


def normalize_roles(parsed: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    role_blob = parsed.get("roles", parsed)
    if not isinstance(role_blob, dict):
        return {}
    roles: dict[str, list[dict[str, Any]]] = {}
    for role, items in role_blob.items():
        if not isinstance(items, list):
            continue
        normalized: list[dict[str, Any]] = []
        for item in items:
            if isinstance(item, str):
                normalized.append({"fragment_id": item})
            elif isinstance(item, dict):
                normalized.append(dict(item))
        roles[role] = normalized
    return roles


def prediction_keys(row: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    for key in ["hard_evaluation_id", "source_prediction_hard_evaluation_id", "source_hard_evaluation_id", "base_evaluation_id", "packet_id"]:
        value = row.get(key)
        if isinstance(value, str) and value not in keys:
            keys.append(value)
    return keys


def build_prediction_index(predictions: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in predictions:
        for key in prediction_keys(row):
            indexed.setdefault(key, row)
    return indexed


def source_lookup(packet: dict[str, Any]) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    by_source: dict[str, str] = {}
    cards: dict[str, dict[str, Any]] = {}
    for card in packet.get("source_cards", []):
        if not isinstance(card, dict):
            continue
        card_id = card.get("card_id")
        source_id = card.get("source_id")
        if isinstance(card_id, str):
            cards[card_id] = card
        if isinstance(card_id, str) and isinstance(source_id, str):
            by_source[source_id] = card_id
    return by_source, cards


def slot_lookup(packet: dict[str, Any]) -> dict[tuple[str, str], list[str]]:
    lookup: dict[tuple[str, str], list[str]] = {}
    for slot in packet.get("required_slots", []):
        if not isinstance(slot, dict):
            continue
        recipient = slot.get("recipient")
        slot_id = slot.get("slot_id")
        for card_id in slot.get("acceptable_card_ids", []):
            if isinstance(recipient, str) and isinstance(slot_id, str) and isinstance(card_id, str):
                lookup.setdefault((recipient, card_id), []).append(slot_id)
    return lookup


def convert_row(packet: dict[str, Any], prediction: dict[str, Any]) -> dict[str, Any]:
    parsed, parse_error = parse_json_object_loose(prediction.get("response"))
    if parse_error:
        return {
            "packet_id": packet["packet_id"],
            "model": prediction.get("model"),
            "status": "error",
            "response": {},
            "error": parse_error,
        }
    roles = normalize_roles(parsed)
    by_source, cards = source_lookup(packet)
    slots = slot_lookup(packet)
    candidate_units: list[dict[str, Any]] = []
    conversion_errors: list[str] = []
    for role in packet.get("roles", []):
        items = roles.get(role, [])
        for index, item in enumerate(items):
            fragment_id = item.get("fragment_id")
            if not isinstance(fragment_id, str) and isinstance(item.get("source_id"), str):
                fragment_id = by_source.get(item["source_id"])
            if not isinstance(fragment_id, str):
                conversion_errors.append(f"{role}:{index}:missing_fragment_id")
                continue
            card = cards.get(fragment_id)
            if card is None:
                conversion_errors.append(f"{role}:{index}:unknown_fragment:{fragment_id}")
                card_ids = [fragment_id]
            else:
                card_ids = [card["card_id"]]
            claimed_slots = slots.get((role, card_ids[0]), [])
            candidate_units.append(
                {
                    "unit_id": f"pred::{role}::{index:03d}::{fragment_id}",
                    "recipient": role,
                    "card_ids": card_ids,
                    "priority": float(max(0, len(items) - index)),
                    "claimed_slots": claimed_slots,
                    "claimed_effect": item.get("reason", "predicted_role_card"),
                }
            )
    return {
        "packet_id": packet["packet_id"],
        "model": prediction.get("model"),
        "provider": prediction.get("provider"),
        "status": "ok" if not conversion_errors else "converted_with_warnings",
        "source_prediction_keys": prediction_keys(prediction),
        "conversion_errors": conversion_errors,
        "response": {
            "option_states": [
                {
                    "option": ROUTING_COMPLETE,
                    "state": "enabled",
                    "supporting_slots": sorted({slot for unit in candidate_units for slot in unit["claimed_slots"]}),
                    "blocking_slots": [],
                    "missing_slots": [],
                }
            ],
            "candidate_units": candidate_units,
            "proposed_rejections": parsed.get("rejected", []),
            "final_decision": ROUTING_COMPLETE,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sseac-packet", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    packets = read_jsonl(args.sseac_packet)
    predictions = build_prediction_index(read_jsonl(args.predictions))
    out_rows: list[dict[str, Any]] = []
    missing = 0
    for packet in packets:
        prediction = predictions.get(packet["packet_id"])
        if prediction is None:
            missing += 1
            out_rows.append(
                {
                    "packet_id": packet["packet_id"],
                    "status": "error",
                    "response": {},
                    "error": "missing_prediction",
                }
            )
        else:
            out_rows.append(convert_row(packet, prediction))
    write_jsonl(args.out, out_rows)
    print(
        json.dumps(
            {
                "rows": len(out_rows),
                "missing_predictions": missing,
                "warning_rows": sum(1 for row in out_rows if row.get("status") == "converted_with_warnings"),
                "out": str(args.out),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
