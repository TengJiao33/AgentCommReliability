#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}

ROLE_KEYWORDS = {
    "appellate": {"appeal", "appellate", "court", "brief", "precedent"},
    "archive": {"archive", "catalog", "record", "accession", "provenance"},
    "assessor": {"assess", "impact", "evaluate", "risk", "mitigation"},
    "attorney": {"attorney", "brief", "appeal", "argument", "precedent"},
    "audit": {"audit", "verify", "check", "review", "compliance"},
    "auditor": {"audit", "verify", "check", "review", "compliance"},
    "authentication": {"authentication", "authenticate", "provenance", "forgery"},
    "catalog": {"catalog", "archive", "record", "accession", "report"},
    "chair": {"chair", "coordinate", "approve", "decide", "review"},
    "checker": {"check", "verify", "fact", "source", "claim"},
    "chief": {"coordinate", "plan", "operations", "safety", "report"},
    "code": {"code", "source", "bug", "vulnerability", "patch", "implement"},
    "coder": {"code", "source", "bug", "vulnerability", "patch", "implement"},
    "compliance": {"compliance", "permit", "requirement", "regulation", "inspect"},
    "coordinator": {"coordinate", "dispatch", "assign", "schedule", "report"},
    "counsel": {"counsel", "legal", "court", "defense", "argument"},
    "critic": {"critic", "critique", "review", "check", "evaluate"},
    "curator": {"curate", "provenance", "catalog", "archive", "attribution"},
    "defense": {"defense", "case", "prosecution", "trial", "argument"},
    "director": {"direct", "coordinate", "operations", "schedule", "report"},
    "dispatcher": {"dispatch", "dispatcher", "call", "alternate", "report"},
    "drill": {"drill", "evacuation", "safety", "marshal", "schedule"},
    "editor": {"edit", "editor", "story", "fact", "angle", "skeptical"},
    "examiner": {"examine", "forgery", "risk", "inspect", "verify"},
    "fact": {"fact", "check", "source", "verify", "claim"},
    "fire": {"fire", "evacuation", "incident", "safety", "behavior"},
    "forgery": {"forgery", "risk", "authentication", "provenance"},
    "inspector": {"inspect", "compliance", "permit", "requirement", "verify"},
    "investigation": {"investigate", "source", "question", "lead", "evidence"},
    "investigative": {"investigate", "source", "question", "lead", "evidence"},
    "investigator": {"investigate", "source", "question", "lead", "evidence"},
    "judge": {"judge", "evaluate", "court", "argument", "brief"},
    "journalist": {"journalist", "report", "story", "source", "fact"},
    "lead": {"lead", "coordinate", "assign", "case", "decision"},
    "legal": {"legal", "court", "case", "brief", "precedent"},
    "manager": {"manage", "coordinate", "schedule", "report", "assign"},
    "marshal": {"marshal", "fire", "safety", "evacuation", "inspect"},
    "medical": {"medical", "clinical", "safety", "regulatory", "claim"},
    "mitigation": {"mitigation", "impact", "permit", "requirement", "plan"},
    "officer": {"officer", "coordinate", "incident", "safety", "report"},
    "operations": {"operations", "plan", "coordinate", "schedule", "field"},
    "paralegal": {"legal", "research", "case", "citation", "precedent"},
    "patent": {"patent", "prior", "claim", "invalidity", "search"},
    "permit": {"permit", "agency", "impact", "mitigation", "compliance"},
    "plan": {"plan", "steps", "schedule", "route", "strategy"},
    "planner": {"plan", "steps", "schedule", "route", "strategy"},
    "provenance": {"provenance", "source", "archive", "attribution", "catalog"},
    "prover": {"prove", "proof", "lemma", "theorem", "argument"},
    "red": {"red", "attack", "risk", "review", "adversarial"},
    "referee": {"referee", "proof", "check", "theorem", "review"},
    "regulatory": {"regulatory", "compliance", "requirement", "review", "safety"},
    "report": {"report", "write", "summary", "brief", "section"},
    "reporter": {"report", "story", "source", "fact", "question"},
    "research": {"research", "search", "source", "evidence", "precedent"},
    "researcher": {"research", "search", "source", "evidence", "precedent"},
    "reviewer": {"review", "check", "audit", "verify", "critique"},
    "safety": {"safety", "risk", "incident", "evacuation", "compliance"},
    "scenario": {"scenario", "adapt", "field", "schedule", "plan"},
    "scientific": {"scientific", "evidence", "impact", "study", "review"},
    "scientist": {"scientific", "evidence", "experiment", "analysis", "review"},
    "specialist": {"specialist", "search", "research", "evidence", "source"},
    "story": {"story", "write", "angle", "report", "editor"},
    "strategist": {"strategy", "defense", "plan", "argument", "case"},
    "tactical": {"tactical", "plan", "scenario", "field", "schedule"},
    "theorist": {"theory", "theorem", "argument", "proof", "model"},
    "writer": {"write", "report", "brief", "story", "section"},
}

GENERIC_GLOBAL_CUES = {
    "read the contest rules",
    "read the rules",
    "participating in",
    "when you finish",
    "report to the dispatcher",
    "before starting",
    "must do two things",
    "one by one",
}

FORBIDDEN_FIELDS_NOT_USED = [
    "source_cards.recipient_scope",
    "required_slots",
    "acceptable_card_ids",
    "expected_final_decision",
    "reference_need_sets",
    "candidate_need_sets",
    "role_utilities",
    "fragments.needed_by",
    "fragments.eligible_by",
    "fragments.target_needed_by",
    "fragments.utility_by_recipient",
]


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


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_str_list(value: Any) -> list[str]:
    return [item for item in as_list(value) if isinstance(item, str)]


def card_cost(card: dict[str, Any]) -> int:
    try:
        return max(0, int(card.get("cost", 1)))
    except (TypeError, ValueError):
        return 1


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def role_parts(role: str) -> set[str]:
    parts = {
        token
        for token in words(role.replace("_", " ").replace("-", " "))
        if token and token not in STOPWORDS
    }
    for token in list(parts):
        if token.endswith("s") and len(token) > 3:
            parts.add(token[:-1])
        if token.endswith("er") and len(token) > 5:
            parts.add(token[:-2])
        if token.endswith("or") and len(token) > 5:
            parts.add(token[:-2])
    return parts


def role_keyword_set(role: str) -> set[str]:
    keys = set(role_parts(role))
    for token in list(keys):
        keys.update(ROLE_KEYWORDS.get(token, set()))
    return {key for key in keys if key not in STOPWORDS}


def score_role_card(role: str, card: dict[str, Any], strategy: str, cost_penalty: float) -> tuple[float, dict[str, Any]]:
    content = str(card.get("content", ""))
    text = content.lower()
    text_words = set(words(content))
    parts = role_parts(role)
    keywords = role_keyword_set(role)
    cost = card_cost(card)

    exact_phrase = role.lower().replace("_", " ").replace("-", " ")
    exact_hit = 1 if exact_phrase and exact_phrase in text.replace("_", " ").replace("-", " ") else 0
    part_hits = sorted(part for part in parts if part in text_words)
    keyword_hits = sorted(keyword for keyword in keywords if keyword in text_words)
    global_hits = sorted(cue for cue in GENERIC_GLOBAL_CUES if cue in text)

    if strategy == "cost":
        score = -float(cost)
    elif strategy == "mention":
        score = (5.0 * exact_hit) + (2.0 * len(part_hits)) - (cost_penalty * cost)
    else:
        score = (
            (5.0 * exact_hit)
            + (2.0 * len(part_hits))
            + (0.8 * min(len(keyword_hits), 6))
            + (1.1 * min(len(global_hits), 2))
            - (cost_penalty * cost)
        )
    return score, {
        "exact_phrase_hit": bool(exact_hit),
        "role_part_hits": part_hits,
        "keyword_hits": keyword_hits[:12],
        "global_cue_hits": global_hits,
        "cost": cost,
    }


def build_units_for_role(
    *,
    role: str,
    cards: list[dict[str, Any]],
    budget: int,
    strategy: str,
    prune_to_budget: bool,
    cost_penalty: float,
    min_score: float | None,
    max_cards_per_role: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scored: list[tuple[float, str, dict[str, Any], dict[str, Any]]] = []
    for card in cards:
        card_id = card.get("card_id")
        if not isinstance(card_id, str):
            continue
        score, debug = score_role_card(role, card, strategy, cost_penalty)
        if min_score is not None and score < min_score:
            continue
        scored.append((score, card_id, card, debug))
    scored.sort(key=lambda item: (-item[0], card_cost(item[2]), item[1]))

    spent = 0
    units: list[dict[str, Any]] = []
    considered = 0
    skipped_for_budget = 0
    for rank, (score, card_id, card, debug) in enumerate(scored):
        if max_cards_per_role > 0 and considered >= max_cards_per_role:
            break
        considered += 1
        cost = card_cost(card)
        if prune_to_budget and spent + cost > budget:
            skipped_for_budget += 1
            continue
        if prune_to_budget:
            spent += cost
        units.append(
            {
                "unit_id": f"no_scope::{strategy}::{role}::{rank:03d}::{card_id}",
                "recipient": role,
                "card_ids": [card_id],
                "priority": score,
                "claimed_slots": [f"{role}::{card_id}"],
                "claimed_effect": f"no_scope_{strategy}_role_affinity",
                "selector_debug": {
                    "rank": rank,
                    "score": score,
                    **debug,
                },
            }
        )
    return units, {
        "units": len(units),
        "spent_if_pruned": spent,
        "candidate_pairs_after_threshold": len(scored),
        "skipped_for_budget": skipped_for_budget,
    }


def build_prediction(
    packet: dict[str, Any],
    *,
    strategy: str,
    prune_to_budget: bool,
    cost_penalty: float,
    min_score: float | None,
    max_cards_per_role: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    roles = as_str_list(packet.get("roles"))
    budgets = packet.get("role_budgets", {}) if isinstance(packet.get("role_budgets"), dict) else {}
    cards = [card for card in as_list(packet.get("source_cards")) if isinstance(card, dict)]

    candidate_units: list[dict[str, Any]] = []
    role_stats: dict[str, Any] = {}
    for role in roles:
        budget = int(budgets.get(role, 0))
        units, stats = build_units_for_role(
            role=role,
            cards=cards,
            budget=budget,
            strategy=strategy,
            prune_to_budget=prune_to_budget,
            cost_penalty=cost_penalty,
            min_score=min_score,
            max_cards_per_role=max_cards_per_role,
        )
        candidate_units.extend(units)
        role_stats[role] = stats

    candidate_units.sort(
        key=lambda unit: (
            -float(unit.get("priority", 0.0)),
            str(unit.get("recipient", "")),
            str(unit.get("unit_id", "")),
        )
    )
    supporting_slots = [
        slot
        for unit in candidate_units
        for slot in as_str_list(unit.get("claimed_slots"))
    ]
    response = {
        "option_states": [
            {
                "option": "routing_complete",
                "state": "enabled" if candidate_units else "insufficient",
                "supporting_slots": supporting_slots,
                "blocking_slots": [],
                "missing_slots": [],
            }
        ],
        "candidate_units": candidate_units,
        "proposed_rejections": [],
        "final_decision": "routing_complete" if candidate_units else "insufficient_evidence",
        "selector_strategy": {
            "name": f"no_scope_{strategy}_role_affinity",
            "strategy": strategy,
            "prune_to_budget": prune_to_budget,
            "cost_penalty": cost_penalty,
            "min_score": min_score,
            "max_cards_per_role": max_cards_per_role,
            "visible_fields_used": [
                "packet_id",
                "roles",
                "role_budgets",
                "source_cards.card_id",
                "source_cards.content",
                "source_cards.cost",
                "candidate_options",
            ],
            "forbidden_fields_not_used": FORBIDDEN_FIELDS_NOT_USED,
        },
    }
    diagnostics = {
        "packet_id": packet.get("packet_id"),
        "candidate_units": len(candidate_units),
        "role_stats": role_stats,
    }
    return response, diagnostics


def summarize(diagnostics: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    role_counter: Counter[str] = Counter()
    units_by_role: Counter[str] = Counter()
    for row in diagnostics:
        for role, stats in row.get("role_stats", {}).items():
            role_counter[role] += 1
            units_by_role[role] += int(stats.get("units", 0))
    return {
        "rows": len(diagnostics),
        "strategy": args.strategy,
        "prune_to_budget": args.prune_to_budget,
        "cost_penalty": args.cost_penalty,
        "min_score": args.min_score,
        "max_cards_per_role": args.max_cards_per_role,
        "candidate_units": sum(int(row.get("candidate_units", 0)) for row in diagnostics),
        "avg_candidate_units_per_row": (
            sum(int(row.get("candidate_units", 0)) for row in diagnostics) / len(diagnostics)
            if diagnostics
            else 0.0
        ),
        "avg_units_by_role": {
            role: units_by_role[role] / role_counter[role]
            for role in sorted(role_counter)
        },
        "visible_fields_used": [
            "packet_id",
            "roles",
            "role_budgets",
            "source_cards.card_id",
            "source_cards.content",
            "source_cards.cost",
            "candidate_options",
        ],
        "forbidden_fields_not_used": FORBIDDEN_FIELDS_NOT_USED,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--strategy", choices=["hybrid", "mention", "cost"], default="hybrid")
    parser.add_argument("--prune-to-budget", action="store_true")
    parser.add_argument("--cost-penalty", type=float, default=0.6)
    parser.add_argument("--min-score", type=float)
    parser.add_argument("--max-cards-per-role", type=int, default=0)
    args = parser.parse_args()

    output_rows: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    for packet in read_jsonl(args.packet):
        response, row_diag = build_prediction(
            packet,
            strategy=args.strategy,
            prune_to_budget=args.prune_to_budget,
            cost_penalty=args.cost_penalty,
            min_score=args.min_score,
            max_cards_per_role=args.max_cards_per_role,
        )
        output_rows.append(
            {
                "packet_id": packet.get("packet_id"),
                "model": f"local_no_scope_{args.strategy}_role_affinity",
                "provider": "local",
                "status": "ok",
                "source_prediction_keys": [packet.get("packet_id")],
                "conversion_errors": [],
                "response": response,
            }
        )
        diagnostics.append(row_diag)

    write_jsonl(args.out, output_rows)
    summary = summarize(diagnostics, args)
    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
