#!/usr/bin/env python3
"""Synthetic MOC-style role-loss probe.

This is a CPU-only contact object, not a MOC benchmark. It creates small
split-evidence cases where clue, bridge, requested relation, qualifier, answer,
and distractor roles are separated, then compares unmerged multi-hop context
against compressed public-state surfaces.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


SCHEMA_VERSION = "acr.comm_trace.v1.1"
METHOD_FAMILY = "MOCRoleCompressionProbe"
TARGET_AGENT = "FinalTarget"

POLICIES = [
    "hop1_direct_context",
    "hop2_unmerged_context",
    "hop2_role_aware_merge",
    "hop2_flat_entity_merge",
    "hop2_answer_only_merge",
]

ROLE_SLOTS = [
    "answer_type",
    "clue_object",
    "bridge_entity",
    "requested_relation",
    "required_qualifier",
    "forbidden_replacement",
    "source_attribution",
]


@dataclass(frozen=True)
class RoleFact:
    fact_id: str
    owner: str
    role: str
    text: str
    answer_hint: str
    relevant: bool = True


@dataclass(frozen=True)
class RoleCase:
    instance_id: str
    sample_index: int
    question: str
    gold_answer: str
    answer_type: str
    clue_object: str
    bridge_entity: str
    requested_relation: str
    required_qualifier: str
    forbidden_replacement: str
    failure_family: str
    facts: Tuple[RoleFact, ...]
    policy_answers: Dict[str, str]
    policy_lost_slots: Dict[str, Tuple[str, ...]]
    policy_notes: Dict[str, str]


def estimate_tokens(parts: Iterable[str]) -> int:
    total = 0
    for part in parts:
        text = str(part).replace("->", " -> ").replace(";", " ; ")
        total += max(1, len(text.split()))
    return total


def normalize(text: Any) -> str:
    return " ".join(str(text).strip().lower().split())


def is_correct(answer: Any, gold: Any) -> bool:
    return normalize(answer) == normalize(gold)


def transition_type(before: bool, after: bool) -> str:
    if before and after:
        return "stable_right"
    if before and not after:
        return "right_to_wrong"
    if not before and after:
        return "wrong_to_right"
    return "stable_wrong"


def make_cases() -> List[RoleCase]:
    def common_answers(gold: str, flat: str, answer_only: Optional[str] = None, hop1: Optional[str] = None) -> Dict[str, str]:
        return {
            "hop1_direct_context": hop1 or flat,
            "hop2_unmerged_context": gold,
            "hop2_role_aware_merge": gold,
            "hop2_flat_entity_merge": flat,
            "hop2_answer_only_merge": answer_only or flat,
        }

    common_lost = {
        "hop1_direct_context": ("clue_object", "bridge_entity", "requested_relation", "required_qualifier"),
        "hop2_unmerged_context": (),
        "hop2_role_aware_merge": (),
        "hop2_flat_entity_merge": (
            "requested_relation",
            "required_qualifier",
            "forbidden_replacement",
            "source_attribution",
        ),
        "hop2_answer_only_merge": (
            "answer_type",
            "clue_object",
            "bridge_entity",
            "requested_relation",
            "required_qualifier",
            "forbidden_replacement",
            "source_attribution",
        ),
    }

    return [
        RoleCase(
            instance_id="moc-role-city-population",
            sample_index=0,
            question="What was the 2001 census population of the city or town containing Kirton End?",
            gold_answer="35124",
            answer_type="population number",
            clue_object="Kirton End",
            bridge_entity="Boston town",
            requested_relation="2001 census population of the containing city or town",
            required_qualifier="city/town containing the hamlet, not similarly named parish",
            forbidden_replacement="civil parish of Kirton",
            failure_family="granularity_switch",
            facts=(
                RoleFact("city-pop-a1", "Agent1", "clue_to_bridge", "Kirton End is a hamlet in Boston, Lincolnshire.", "Boston"),
                RoleFact("city-pop-a2", "Agent2", "bridge_to_answer", "Boston town had a 2001 census population of 35124.", "35124"),
                RoleFact("city-pop-a3", "Agent3", "distractor", "The civil parish of Kirton had a population of 273.", "273", False),
                RoleFact("city-pop-a4", "Agent4", "qualifier", "The question asks for the containing city or town, not the parish.", "city/town qualifier"),
            ),
            policy_answers=common_answers("35124", "273"),
            policy_lost_slots=common_lost,
            policy_notes={
                "hop2_flat_entity_merge": "keeps population values but loses the city/town-vs-parish guard",
                "hop2_answer_only_merge": "candidate values remain without the granularity role",
            },
        ),
        RoleCase(
            instance_id="moc-role-mentor-instrument",
            sample_index=1,
            question="Which instrument is played by the artist whose mentor wrote Ballad Elm?",
            gold_answer="viola",
            answer_type="instrument",
            clue_object="Ballad Elm",
            bridge_entity="artist Nira Sol",
            requested_relation="instrument played by the artist, not by the mentor",
            required_qualifier="artist reached through the mentor clue",
            forbidden_replacement="mentor's own instrument",
            failure_family="clue_object_replaces_answer_object",
            facts=(
                RoleFact("mentor-inst-a1", "Agent1", "clue_to_bridge", "Ballad Elm was written by mentor Oren Vale.", "Oren Vale"),
                RoleFact("mentor-inst-a2", "Agent2", "bridge_to_answer", "Oren Vale mentored artist Nira Sol.", "Nira Sol"),
                RoleFact("mentor-inst-a3", "Agent3", "answer", "Nira Sol plays the viola.", "viola"),
                RoleFact("mentor-inst-a4", "Agent4", "distractor", "Oren Vale is known for flute performances.", "flute", False),
            ),
            policy_answers=common_answers("viola", "flute"),
            policy_lost_slots=common_lost,
            policy_notes={
                "hop2_flat_entity_merge": "collapses mentor and artist roles into one music-topic summary",
                "hop2_answer_only_merge": "candidate instruments remain but the answer owner is gone",
            },
        ),
        RoleCase(
            instance_id="moc-role-company-headquarters",
            sample_index=2,
            question="In what city is the company founded by Robert Smith headquartered?",
            gold_answer="Riverton",
            answer_type="city",
            clue_object="Robert Smith",
            bridge_entity="Northstar Foods",
            requested_relation="headquarters city",
            required_qualifier="company founded by Robert Smith",
            forbidden_replacement="founding city",
            failure_family="predicate_drift",
            facts=(
                RoleFact("company-hq-a1", "Agent1", "clue_to_bridge", "Robert Smith founded Northstar Foods.", "Northstar Foods"),
                RoleFact("company-hq-a2", "Agent2", "answer", "Northstar Foods is headquartered in Riverton.", "Riverton"),
                RoleFact("company-hq-a3", "Agent3", "distractor", "Northstar Foods was founded in Mason City.", "Mason City", False),
                RoleFact("company-hq-a4", "Agent4", "qualifier", "The requested relation is headquarters, not founding location.", "headquarters relation"),
            ),
            policy_answers=common_answers("Riverton", "Mason City"),
            policy_lost_slots=common_lost,
            policy_notes={
                "hop2_flat_entity_merge": "keeps company and city names but loses founded-vs-headquartered",
                "hop2_answer_only_merge": "city candidates remain without predicate role",
            },
        ),
        RoleCase(
            instance_id="moc-role-archive-collection",
            sample_index=3,
            question="What does the museum that houses works by Hanna Varis hold about 65000 of?",
            gold_answer="drawings",
            answer_type="collection type",
            clue_object="works by Hanna Varis",
            bridge_entity="Albertina Museum",
            requested_relation="collection type with about 65000 items",
            required_qualifier="museum collection, not artist medium",
            forbidden_replacement="artist work title",
            failure_family="useful_bridge_refinement",
            facts=(
                RoleFact("archive-a1", "Agent1", "clue_to_bridge", "Works by Hanna Varis are in the Albertina Museum collection.", "Albertina Museum"),
                RoleFact("archive-a2", "Agent2", "answer", "The Albertina Museum holds about 65000 drawings.", "drawings"),
                RoleFact("archive-a3", "Agent3", "distractor", "Hanna Varis is also associated with woodcuts.", "woodcuts", False),
                RoleFact("archive-a4", "Agent4", "qualifier", "Here the target should move from artist clue to museum collection.", "bridge refinement allowed"),
            ),
            policy_answers=common_answers("drawings", "drawings", answer_only="drawings", hop1="woodcuts"),
            policy_lost_slots={
                **common_lost,
                "hop2_flat_entity_merge": ("source_attribution",),
                "hop2_answer_only_merge": ("clue_object", "bridge_entity", "requested_relation", "source_attribution"),
            },
            policy_notes={
                "hop2_flat_entity_merge": "target motion is useful here; a flat summary still keeps the answer role",
                "hop2_answer_only_merge": "thin but not harmful for this case because only one answer-shaped value dominates",
            },
        ),
        RoleCase(
            instance_id="moc-role-genre-comparison",
            sample_index=4,
            question="Are the films Glass Harbor and Winter Engine from different genres?",
            gold_answer="yes",
            answer_type="yes/no comparison",
            clue_object="two film titles",
            bridge_entity="genre pair",
            requested_relation="compare whether the two genres differ",
            required_qualifier="joint comparison after both genres are known",
            forbidden_replacement="one individual genre",
            failure_family="comparison_aggregation_loss",
            facts=(
                RoleFact("genre-a1", "Agent1", "partial_evidence", "Glass Harbor is a drama film.", "drama"),
                RoleFact("genre-a2", "Agent2", "partial_evidence", "Winter Engine is a comedy film.", "comedy"),
                RoleFact("genre-a3", "Agent3", "comparison", "Drama and comedy are different genres.", "yes"),
                RoleFact("genre-a4", "Agent4", "qualifier", "The answer should be yes/no, not a genre name.", "yes/no qualifier"),
            ),
            policy_answers=common_answers("yes", "drama", answer_only="comedy", hop1="comedy"),
            policy_lost_slots=common_lost,
            policy_notes={
                "hop2_flat_entity_merge": "keeps genre facts but loses the comparison operation",
                "hop2_answer_only_merge": "keeps candidate surface tokens without the yes/no contract",
            },
        ),
        RoleCase(
            instance_id="moc-role-cyclone-film",
            sample_index=5,
            question="Which cyclone had a film made about it in 2007 and was the strongest recorded tropical cyclone in the basin?",
            gold_answer="Cyclone Odra",
            answer_type="cyclone name",
            clue_object="2007 film Kathantara",
            bridge_entity="Cyclone Odra",
            requested_relation="cyclone satisfying film and strongest-recorded constraints",
            required_qualifier="answer is the cyclone, not the film title",
            forbidden_replacement="film title or competing cyclone",
            failure_family="distractor_anchor_switch",
            facts=(
                RoleFact("cyclone-a1", "Agent1", "clue_to_bridge", "The 2007 film Kathantara is about Cyclone Odra.", "Cyclone Odra"),
                RoleFact("cyclone-a2", "Agent2", "answer", "Cyclone Odra is listed as the strongest recorded tropical cyclone in the basin.", "Cyclone Odra"),
                RoleFact("cyclone-a3", "Agent3", "distractor", "Cyclone Vela was another severe storm in the region.", "Cyclone Vela", False),
                RoleFact("cyclone-a4", "Agent4", "qualifier", "The final answer must be a cyclone name, not the film title.", "cyclone qualifier"),
            ),
            policy_answers=common_answers("Cyclone Odra", "Kathantara", answer_only="Cyclone Vela"),
            policy_lost_slots=common_lost,
            policy_notes={
                "hop2_flat_entity_merge": "clue object becomes answer-shaped after film/cyclone roles are flattened",
                "hop2_answer_only_merge": "competing cyclone name survives without the two-constraint role",
            },
        ),
    ]


def facts_for_policy(case: RoleCase, policy: str) -> List[RoleFact]:
    if policy == "hop1_direct_context":
        return [fact for fact in case.facts if fact.owner in {"Agent3", "Agent4"}]
    return list(case.facts)


def preserved_slots(case: RoleCase, policy: str) -> List[str]:
    lost = set(case.policy_lost_slots.get(policy, ()))
    return [slot for slot in ROLE_SLOTS if slot not in lost]


def summary_text(case: RoleCase, policy: str, visible_facts: Sequence[RoleFact]) -> str:
    if policy == "hop1_direct_context":
        return "\n".join(f"{fact.owner}/{fact.role}: {fact.text}" for fact in visible_facts)
    if policy == "hop2_unmerged_context":
        return "\n".join(f"{fact.owner}/{fact.role}: {fact.text}" for fact in visible_facts)
    if policy == "hop2_role_aware_merge":
        return (
            f"answer_type={case.answer_type}; clue={case.clue_object}; bridge={case.bridge_entity}; "
            f"relation={case.requested_relation}; qualifier={case.required_qualifier}; "
            f"forbidden={case.forbidden_replacement}; answer={case.gold_answer}"
        )
    if policy == "hop2_flat_entity_merge":
        values = []
        for fact in visible_facts:
            if fact.answer_hint not in values:
                values.append(fact.answer_hint)
        return "Entities and values: " + "; ".join(values)
    if policy == "hop2_answer_only_merge":
        values = []
        for fact in visible_facts:
            if fact.role in {"answer", "distractor", "comparison", "partial_evidence"} and fact.answer_hint not in values:
                values.append(fact.answer_hint)
        return "Candidate answer surfaces: " + "; ".join(values)
    raise ValueError(f"Unknown policy: {policy}")


def public_state(policy: str) -> Dict[str, str]:
    surfaces = {
        "hop1_direct_context": "direct_neighbor_messages",
        "hop2_unmerged_context": "multi_order_full_messages",
        "hop2_role_aware_merge": "role_preserving_compressed_summary",
        "hop2_flat_entity_merge": "flat_entity_compressed_summary",
        "hop2_answer_only_merge": "answer_surface_compressed_summary",
    }
    policies = {
        "hop1_direct_context": "one_hop_context",
        "hop2_unmerged_context": "multi_order_unmerged_context",
        "hop2_role_aware_merge": "moc_style_structural_merge",
        "hop2_flat_entity_merge": "moc_style_structural_merge",
        "hop2_answer_only_merge": "moc_style_structural_merge",
    }
    return {"surface": surfaces[policy], "communication_policy": policies[policy]}


def round_agents(case: RoleCase, visible_facts: Sequence[RoleFact]) -> List[Dict[str, Any]]:
    agents = []
    for fact in case.facts:
        visible = fact in visible_facts
        agents.append(
            {
                "agent_id": fact.owner,
                "answer": fact.answer_hint,
                "correct": is_correct(fact.answer_hint, case.gold_answer),
                "confidence": 0.82 if fact.relevant else 0.45,
                "retained": visible,
                "tokens": {
                    "input_tokens": estimate_tokens([case.question, fact.text]),
                    "output_tokens": estimate_tokens([fact.answer_hint]),
                    "total_tokens": estimate_tokens([case.question, fact.text, fact.answer_hint]),
                },
                "message_role": fact.role,
                "fact_id": fact.fact_id,
            }
        )
    return agents


def build_record(run_id: str, case: RoleCase, policy: str, include_text: bool) -> Dict[str, Any]:
    visible_facts = facts_for_policy(case, policy)
    summary = summary_text(case, policy, visible_facts)
    answer = case.policy_answers[policy]
    baseline_answer = case.policy_answers["hop2_unmerged_context"]
    final_correct = is_correct(answer, case.gold_answer)
    baseline_correct = is_correct(baseline_answer, case.gold_answer)
    lost_slots = list(case.policy_lost_slots.get(policy, ()))
    kept_slots = preserved_slots(case, policy)
    compression = policy.startswith("hop2_") and policy not in {"hop2_unmerged_context"}

    event: Dict[str, Any] = {
        "stage": "neighbor_summary_ism",
        "mechanism": "structural_merge" if compression else "neighbor_context",
        "scope": "sample",
        "neighbor_hops": 2 if policy.startswith("hop2") else 1,
        "ism_r": 0 if compression else None,
        "initial_message_count": len(visible_facts),
        "final_message_count": 1 if compression else len(visible_facts),
        "original_agent_ids": [fact.owner for fact in visible_facts],
        "represented_agent_ids": [fact.owner for fact in visible_facts],
        "merged_agent_ids": [fact.owner for fact in visible_facts] if compression else [],
        "dropped_direct_agent_ids": [],
        "compression_policy": policy,
        "role_slots_preserved": kept_slots,
        "role_slots_lost": lost_slots,
        "role_loss_detected": bool(lost_slots),
        "failure_family": case.failure_family if lost_slots else None,
        "token_cost": estimate_tokens([summary]),
    }
    if include_text:
        event["summary_text"] = summary

    context_event: Dict[str, Any] = {
        "stage": "recipient_context",
        "agent_id": TARGET_AGENT,
        "context_surface": public_state(policy)["surface"],
        "visible_source_agent_ids": [fact.owner for fact in visible_facts],
        "visible_fact_ids": [fact.fact_id for fact in visible_facts],
        "role_slots_visible": kept_slots,
        "role_slots_missing": lost_slots,
    }
    if include_text:
        context_event["context_text"] = summary

    input_tokens = estimate_tokens([case.question, summary])
    output_tokens = estimate_tokens([answer])
    compressed_tokens = estimate_tokens([summary]) if compression else 0

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "method_family": METHOD_FAMILY,
        "method": policy,
        "instance_id": case.instance_id,
        "sample_index": case.sample_index,
        "question": case.question,
        "gold_answer": case.gold_answer,
        "task_regime": "split_evidence_role_probe",
        "public_state": public_state(policy),
        "final": {"answer": answer, "correct": final_correct},
        "transition": {
            "from_stage": "hop2_unmerged_context",
            "to_stage": policy,
            "type": transition_type(baseline_correct, final_correct),
            "before_answer": baseline_answer,
            "before_correct": baseline_correct,
            "after_answer": answer,
            "after_correct": final_correct,
        },
        "rounds": [
            {
                "round_index": 0,
                "agents": round_agents(case, visible_facts),
                "debate_answer": answer,
                "debate_correct": final_correct,
            }
        ],
        "retention_events": [],
        "communication_events": [event],
        "context_events": [context_event],
        "token_cost": {
            "scope": "sample",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "compressed_prompt_tokens": compressed_tokens if compression else 0,
            "compressed_completion_tokens": 0,
            "compressed_total_tokens": compressed_tokens if compression else 0,
        },
        "method_comparison": {
            "baseline": {
                "method": "hop2_unmerged_context",
                "answer": baseline_answer,
                "correct": baseline_correct,
            },
            "transition_vs_baseline": transition_type(baseline_correct, final_correct),
        },
        "role_probe": {
            "answer_type": case.answer_type,
            "clue_object": case.clue_object,
            "bridge_entity": case.bridge_entity,
            "requested_relation": case.requested_relation,
            "required_qualifier": case.required_qualifier,
            "forbidden_replacement": case.forbidden_replacement,
            "failure_family": case.failure_family,
            "policy_note": case.policy_notes.get(policy),
        },
        "source": {"generator": "scripts/run_moc_role_loss_probe.py"},
    }


def summarize(records: Sequence[Dict[str, Any]], cases: Sequence[RoleCase], run_id: str) -> Dict[str, Any]:
    by_policy: Dict[str, List[Dict[str, Any]]] = {policy: [] for policy in POLICIES}
    for record in records:
        by_policy[record["method"]].append(record)

    policy_rows = []
    for policy in POLICIES:
        group = by_policy[policy]
        correct = sum(1 for record in group if record["final"]["correct"])
        transitions = Counter(record["transition"]["type"] for record in group)
        lost_slot_counter = Counter(
            slot
            for record in group
            for event in record["communication_events"]
            for slot in event.get("role_slots_lost", [])
        )
        policy_rows.append(
            {
                "policy": policy,
                "correct": correct,
                "total": len(group),
                "accuracy": correct / len(group) if group else None,
                "transitions_vs_hop2_unmerged": dict(sorted(transitions.items())),
                "records_with_role_loss": sum(
                    1 for record in group if record["communication_events"][0].get("role_loss_detected")
                ),
                "lost_slot_counts": dict(sorted(lost_slot_counter.items())),
                "avg_total_tokens": sum(record["token_cost"]["total_tokens"] for record in group) / len(group)
                if group
                else None,
                "avg_compressed_tokens": sum(
                    record["token_cost"]["compressed_total_tokens"] or 0 for record in group
                )
                / len(group)
                if group
                else None,
            }
        )

    case_rows = []
    for case in cases:
        row = {
            "instance_id": case.instance_id,
            "sample_index": case.sample_index,
            "failure_family": case.failure_family,
            "gold_answer": case.gold_answer,
            "answers_by_policy": case.policy_answers,
        }
        row["wrong_policies"] = [
            policy for policy, answer in case.policy_answers.items() if not is_correct(answer, case.gold_answer)
        ]
        case_rows.append(row)

    return {
        "run_id": run_id,
        "schema_version": SCHEMA_VERSION,
        "method_family": METHOD_FAMILY,
        "records": len(records),
        "cases": len(cases),
        "policies": POLICIES,
        "policy_rows": policy_rows,
        "case_rows": case_rows,
        "short_reading": [
            "hop2_unmerged_context and hop2_role_aware_merge preserve all six synthetic cases.",
            "flat and answer-only compression create failures exactly where role slots are flattened or replaced.",
            "the useful_bridge_refinement case stays correct under flat compression, so target movement is not automatically drift.",
        ],
        "caveats": [
            "CPU-only synthetic contact; no LLM calls and no MOC paper score.",
            "The compression policies are deterministic stress surfaces, not claims about MOC's actual summarizer behavior.",
            "Token counts are rough word-count proxies.",
        ],
    }


def write_jsonl(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_readme(
    out_dir: Path,
    summary: Dict[str, Any],
    command: str,
    started_at: str,
    ended_at: str,
) -> None:
    policy_rows = "\n".join(
        "| {policy} | {correct}/{total} | {accuracy:.2f} | {records_with_role_loss} | {avg_total_tokens:.1f} | {avg_compressed_tokens:.1f} | {transitions} |".format(
            policy=row["policy"],
            correct=row["correct"],
            total=row["total"],
            accuracy=row["accuracy"],
            records_with_role_loss=row["records_with_role_loss"],
            avg_total_tokens=row["avg_total_tokens"],
            avg_compressed_tokens=row["avg_compressed_tokens"],
            transitions=json.dumps(row["transitions_vs_hop2_unmerged"], sort_keys=True),
        )
        for row in summary["policy_rows"]
    )
    case_rows = "\n".join(
        "| {sample_index} | `{instance_id}` | {failure_family} | `{gold_answer}` | {wrong_policies} |".format(
            sample_index=row["sample_index"],
            instance_id=row["instance_id"],
            failure_family=row["failure_family"],
            gold_answer=row["gold_answer"],
            wrong_policies=", ".join(f"`{policy}`" for policy in row["wrong_policies"]) or "none",
        )
        for row in summary["case_rows"]
    )
    readme = f"""# {summary['run_id']}

## What We Tried

Ran a CPU-only MOC-style role-loss probe over six split-evidence cases. The
probe compares one-hop direct context, two-hop unmerged context, and three
compressed summary surfaces.

## Scope

- Method family: `{METHOD_FAMILY}`
- Model: deterministic synthetic policies
- Dataset: hand-built split-evidence role cases
- Samples: `{summary['cases']}`
- GPU: none
- Evidence level: contact/schema pressure only

## Command

```bash
{command}
```

## Outputs

- `comm_trace_moc_role_probe_v11.jsonl`
- `cases.jsonl`
- `summary.json`
- `manifest.json`

## Result

| Policy | Correct | Accuracy | Role-Loss Records | Avg Total Tokens | Avg Compressed Tokens | Transitions vs Hop2 Unmerged |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
{policy_rows}

## Case Surface

| Sample | Case | Family | Gold | Wrong Policies |
| ---: | --- | --- | --- | --- |
{case_rows}

## Things Noticed

- A role-aware compressed surface preserves all cases in this probe.
- Flat entity compression and answer-only compression fail when they erase the
  distinction between clue object, bridge entity, requested relation, and
  answer object.
- The archive/collection case stays correct under flat compression, which keeps
  the important caveat alive: target movement can be useful bridge refinement,
  not only drift.

## Caveats

- This is not a MOC benchmark or an LLM result.
- The deterministic policies are stress surfaces for trace/schema design.
- The useful output is the role-loss audit shape, not the accuracy number.

## Timeline

- `{started_at}`: launched
- `{ended_at}`: completed
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")


def run(args: argparse.Namespace) -> Dict[str, Any]:
    started_at = datetime.now().isoformat(timespec="seconds")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = make_cases()
    records = [
        build_record(args.run_id, case, policy, include_text=args.include_text)
        for case in cases
        for policy in POLICIES
    ]
    summary = summarize(records, cases, args.run_id)

    trace_path = out_dir / "comm_trace_moc_role_probe_v11.jsonl"
    cases_path = out_dir / "cases.jsonl"
    summary_path = out_dir / "summary.json"
    manifest_path = out_dir / "manifest.json"

    write_jsonl(trace_path, records)
    write_jsonl(
        cases_path,
        [
            {
                "instance_id": case.instance_id,
                "sample_index": case.sample_index,
                "question": case.question,
                "gold_answer": case.gold_answer,
                "answer_type": case.answer_type,
                "clue_object": case.clue_object,
                "bridge_entity": case.bridge_entity,
                "requested_relation": case.requested_relation,
                "required_qualifier": case.required_qualifier,
                "forbidden_replacement": case.forbidden_replacement,
                "failure_family": case.failure_family,
                "facts": [fact.__dict__ for fact in case.facts],
                "policy_answers": case.policy_answers,
                "policy_lost_slots": {key: list(value) for key, value in case.policy_lost_slots.items()},
                "policy_notes": case.policy_notes,
            }
            for case in cases
        ],
    )
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    ended_at = datetime.now().isoformat(timespec="seconds")
    command = "python scripts/run_moc_role_loss_probe.py " + " ".join(args.raw_args)
    manifest = {
        "run_id": args.run_id,
        "status": "completed",
        "method": METHOD_FAMILY,
        "model": "deterministic-synthetic-policies",
        "dataset": "hand-built split-evidence role cases",
        "seed": None,
        "samples": len(cases),
        "machine": "local",
        "gpu_ids": [],
        "timeout_minutes": None,
        "started_at": started_at,
        "ended_at": ended_at,
        "upstream_repo": "https://github.com/yao-guan/MOC",
        "upstream_commit": "9c67c92507570704a7df73e452552a3f49e83897",
        "local_changes": ["scripts/run_moc_role_loss_probe.py"],
        "command": command,
        "log_path": "",
        "result_paths": [str(trace_path), str(cases_path), str(summary_path)],
        "metrics": {
            "accuracy": None,
            "total_tokens": sum(record["token_cost"]["total_tokens"] for record in records),
            "eval_time_seconds": None,
            "wall_time_seconds": None,
        },
        "caveats": summary["caveats"],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    write_readme(out_dir, summary, command, started_at, ended_at)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument(
        "--include-text",
        action="store_true",
        help="Include synthetic summary/context text in trace records for easier manual inspection.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.raw_args = list(argv) if argv is not None else sys.argv[1:]
    summary = run(args)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
