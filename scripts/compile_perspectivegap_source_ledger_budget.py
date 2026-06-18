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


def parse_json_object_loose(text: str | None) -> dict[str, Any]:
    if text is None:
        raise ValueError("empty response")
    text = text.strip()
    fence = re.match(r"^```(?:json)?\s*\n(.*?)\n```\s*$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object")
    parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("response is not a JSON object")
    return parsed


def normalize_source_ids(blob: Any) -> list[str]:
    if not isinstance(blob, list):
        return []
    out: list[str] = []
    for item in blob:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict) and isinstance(item.get("source_id"), str):
            out.append(item["source_id"])
        elif isinstance(item, dict) and isinstance(item.get("fragment_id"), str):
            out.append(item["fragment_id"])
    return out


def visibility_from_selected_roles(selected_roles: list[str], all_roles: list[str]) -> str:
    if len(selected_roles) == len(all_roles):
        return "shared_all"
    if len(selected_roles) > 1:
        return "shared_subset"
    return "role_private"


def compile_budgeted(row: dict[str, Any], ledger_response: str | None) -> tuple[str | None, dict[str, Any], str | None]:
    try:
        parsed = parse_json_object_loose(ledger_response)
    except (json.JSONDecodeError, ValueError) as error:
        return None, {}, f"parse: {error}"

    roles = list(row["roles"])
    role_blob = parsed.get("roles", parsed)
    if not isinstance(role_blob, dict):
        role_blob = {}
    fragments_by_source = {fragment["source_id"]: fragment for fragment in row["fragments"]}
    fragments_by_id = {fragment["id"]: fragment for fragment in row["fragments"]}
    ledger_by_source = {
        entry["source_id"]: {
            "fragment_id": entry["fragment_id"],
            "recipients": set(entry.get("recipients", [])),
        }
        for entry in row["source_scope_ledger"]
    }

    def resolve_source(token: str) -> tuple[str, dict[str, Any] | None]:
        if token in fragments_by_source:
            return token, fragments_by_source[token]
        if token in fragments_by_id:
            fragment = fragments_by_id[token]
            return fragment["source_id"], fragment
        return token, None

    selected_by_role: dict[str, list[str]] = {}
    selected_roles_by_source: dict[str, list[str]] = {}
    meta: dict[str, Any] = {
        "budget_compiler": "filter_to_ledger_recipients_then_keep_order_under_budget",
        "raw_parsed": parsed,
        "role_stats": {},
    }
    for role in roles:
        selected_by_role[role] = []
        spent = 0
        seen: set[str] = set()
        role_stats = {
            "budget": row["role_budgets"][role],
            "spent": 0,
            "invalid": [],
            "duplicate": [],
            "wrong_recipient": [],
            "over_budget": [],
        }
        for token in normalize_source_ids(role_blob.get(role, [])):
            source_id, fragment = resolve_source(token)
            if source_id in seen:
                role_stats["duplicate"].append(source_id)
                continue
            seen.add(source_id)
            if fragment is None or source_id not in ledger_by_source:
                role_stats["invalid"].append(source_id)
                continue
            if role not in ledger_by_source[source_id]["recipients"]:
                role_stats["wrong_recipient"].append(source_id)
                continue
            cost = int(fragment["cost"])
            if spent + cost > row["role_budgets"][role]:
                role_stats["over_budget"].append(source_id)
                continue
            selected_by_role[role].append(source_id)
            spent += cost
            selected_roles_by_source.setdefault(source_id, [])
            if role not in selected_roles_by_source[source_id]:
                selected_roles_by_source[source_id].append(role)
        role_stats["spent"] = spent
        meta["role_stats"][role] = role_stats

    compiled: dict[str, Any] = {"roles": {}, "rejected": []}
    for role in roles:
        cards: list[dict[str, Any]] = []
        for source_id in selected_by_role[role]:
            fragment = fragments_by_source[source_id]
            cards.append(
                {
                    "fragment_id": fragment["id"],
                    "source_id": source_id,
                    "visibility": visibility_from_selected_roles(selected_roles_by_source[source_id], roles),
                    "reason": "budget_compiled_from_source_ledger_priority",
                }
            )
        compiled["roles"][role] = cards

    for item in row.get("reference_rejections", []):
        compiled["rejected"].append(
            {
                "fragment_id": item["fragment_id"],
                "source_id": item["source_id"],
                "reason": "budget_compiler_ledger_reject",
            }
        )

    meta["selected_roles_by_source"] = selected_roles_by_source
    return json.dumps(compiled, ensure_ascii=False), meta, None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    packet_rows = read_jsonl(args.packet)
    packet = {row["hard_evaluation_id"]: row for row in packet_rows}
    packet_by_source_id = {
        row.get("source_hard_evaluation_id"): row
        for row in packet_rows
        if row.get("source_hard_evaluation_id")
    }
    packet_by_base_variant = {
        (row.get("base_evaluation_id"), row.get("source_perturbation_variant")): row
        for row in packet_rows
    }
    predictions = read_jsonl(args.predictions)
    out_rows: list[dict[str, Any]] = []
    for prediction in predictions:
        prediction_hard_id = prediction["hard_evaluation_id"]
        row = (
            packet.get(prediction_hard_id)
            or packet_by_source_id.get(prediction_hard_id)
            or packet_by_base_variant.get((prediction.get("base_evaluation_id"), prediction.get("source_perturbation_variant")))
        )
        if row is None:
            raise KeyError(f"prediction does not match packet: {prediction_hard_id}")
        response, meta, error = compile_budgeted(row, prediction.get("ledger_response"))
        out_row = {
            "hard_evaluation_id": row["hard_evaluation_id"],
            "source_prediction_hard_evaluation_id": prediction_hard_id,
            "base_evaluation_id": row.get("base_evaluation_id"),
            "scenario_id": row.get("scenario_id"),
            "shuffle_seed": row.get("shuffle_seed"),
            "source_perturbation_variant": row.get("source_perturbation_variant"),
            "tight_budget_variant": row.get("tight_budget_variant"),
            "task": "source_ledger_budget_compiled",
            "model": prediction.get("model"),
            "provider": prediction.get("provider"),
            "source_prediction_status": prediction.get("status"),
            "budget_compiler_meta": meta,
        }
        if error:
            out_row["status"] = "error"
            out_row["response"] = None
            out_row["error"] = {"type": "BudgetCompileError", "message": error}
        else:
            out_row["status"] = "ok"
            out_row["response"] = response
        out_rows.append(out_row)
    write_jsonl(args.out, out_rows)
    print(json.dumps({"rows": len(out_rows), "out": str(args.out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
