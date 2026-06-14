#!/usr/bin/env python3
"""Deterministic communication-regime harness.

This is a toy contact object, not a model benchmark. It creates small
distributed-evidence tasks and runs fixed communication protocols so the
project can inspect task-regime and public-state fields without launching a
GPU job.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


SCHEMA_VERSION = "acr.comm_trace.v1.1"
METHOD_FAMILY = "CommunicationRegimeHarness"

AGENTS = ["Agent1", "Agent2", "Agent3"]
REGIMES = [
    "recall",
    "state_tracking",
    "k_hop",
    "conflict_evidence",
    "saturated_arithmetic",
]
PROTOCOLS = [
    "single_agent",
    "independent_majority",
    "full_broadcast",
    "evidence_state",
    "route_or_silence",
]


@dataclass(frozen=True)
class Fact:
    fact_id: str
    owner: str
    kind: str
    text: str
    value: Any
    relevant: bool = True
    confidence: Optional[float] = None
    order: Optional[int] = None


@dataclass(frozen=True)
class Instance:
    instance_id: str
    sample_index: int
    regime: str
    question: str
    gold_answer: Any
    facts: Tuple[Fact, ...]


def estimate_tokens(parts: Iterable[str]) -> int:
    tokens = 0
    for part in parts:
        words = str(part).replace("=", " = ").replace("->", " -> ").split()
        tokens += max(1, len(words))
    return tokens


def is_correct(answer: Any, gold: Any) -> bool:
    return str(answer).strip().lower() == str(gold).strip().lower()


def transition_type(before: bool, after: bool) -> str:
    if before and after:
        return "stable_right"
    if before and not after:
        return "right_to_wrong"
    if not before and after:
        return "wrong_to_right"
    return "stable_wrong"


def majority_answer(answers: Sequence[Any]) -> Any:
    counts = Counter(str(answer) for answer in answers)
    if not counts:
        return "unknown"
    top_count = counts.most_common(1)[0][1]
    for answer in answers:
        if counts[str(answer)] == top_count:
            return answer
    return "unknown"


def owner_facts(instance: Instance, agent_id: str) -> List[Fact]:
    return [fact for fact in instance.facts if fact.owner == agent_id]


def relevant_facts(instance: Instance) -> List[Fact]:
    return [fact for fact in instance.facts if fact.relevant]


def all_facts(instance: Instance) -> List[Fact]:
    return list(instance.facts)


def unique_facts(facts: Iterable[Fact]) -> List[Fact]:
    seen = set()
    unique = []
    for fact in facts:
        if fact.fact_id in seen:
            continue
        seen.add(fact.fact_id)
        unique.append(fact)
    return unique


def answer_from_facts(instance: Instance, visible_facts: Sequence[Fact]) -> Any:
    if instance.regime == "recall":
        answers = [fact.value for fact in visible_facts if fact.kind == "answer"]
        if answers:
            return answers[0]
        distractors = [fact.value for fact in visible_facts if fact.kind == "distractor"]
        return distractors[0] if distractors else "unknown"

    if instance.regime == "saturated_arithmetic":
        if any(fact.kind == "equation" for fact in visible_facts):
            return instance.gold_answer
        return "unknown"

    if instance.regime == "k_hop":
        required = {"link_1", "link_2", "value"}
        visible_kinds = {fact.kind for fact in visible_facts}
        if required.issubset(visible_kinds):
            return instance.gold_answer
        if "value" in visible_kinds:
            return next(fact.value for fact in visible_facts if fact.kind == "value")
        if "link_2" in visible_kinds:
            return "node_c"
        if "link_1" in visible_kinds:
            return "node_b"
        return "unknown"

    if instance.regime == "state_tracking":
        init = [fact.value for fact in visible_facts if fact.kind == "init"]
        if not init:
            return "unknown"
        state = int(init[0])
        for fact in sorted(
            [fact for fact in visible_facts if fact.kind == "operation"],
            key=lambda item: item.order or 0,
        ):
            op, amount = fact.value
            if op == "add":
                state += amount
            elif op == "sub":
                state -= amount
            elif op == "mul":
                state *= amount
        return state

    if instance.regime == "conflict_evidence":
        evidence = [fact for fact in visible_facts if fact.kind == "label_evidence"]
        if not evidence:
            return "unknown"
        best = max(evidence, key=lambda fact: fact.confidence or 0.0)
        return best.value

    raise ValueError(f"Unknown regime: {instance.regime}")


def fact_payload(facts: Sequence[Fact]) -> List[Dict[str, Any]]:
    return [
        {
            "fact_id": fact.fact_id,
            "owner": fact.owner,
            "kind": fact.kind,
            "text": fact.text,
            "value": fact.value,
            "relevant": fact.relevant,
            "confidence": fact.confidence,
            "order": fact.order,
        }
        for fact in facts
    ]


def round_from_visibility(instance: Instance, visible_by_agent: Dict[str, List[Fact]]) -> Dict[str, Any]:
    agents = []
    for agent_id in AGENTS:
        visible = visible_by_agent.get(agent_id, [])
        answer = answer_from_facts(instance, visible)
        agents.append(
            {
                "agent_id": agent_id,
                "answer": answer,
                "correct": is_correct(answer, instance.gold_answer),
                "confidence": confidence_from_facts(instance, visible),
                "visible_fact_ids": [fact.fact_id for fact in visible],
                "tokens": {
                    "input_tokens": estimate_tokens([instance.question, *[fact.text for fact in visible]]),
                    "output_tokens": estimate_tokens([str(answer)]),
                    "total_tokens": estimate_tokens([instance.question, *[fact.text for fact in visible], str(answer)]),
                },
            }
        )
    debate_answer = majority_answer([agent["answer"] for agent in agents])
    return {
        "round_index": 0,
        "agents": agents,
        "debate_answer": debate_answer,
        "debate_correct": is_correct(debate_answer, instance.gold_answer),
    }


def confidence_from_facts(instance: Instance, visible_facts: Sequence[Fact]) -> Optional[float]:
    if instance.regime == "conflict_evidence":
        evidence = [fact for fact in visible_facts if fact.kind == "label_evidence"]
        if evidence:
            return max(fact.confidence or 0.0 for fact in evidence)
    if answer_from_facts(instance, visible_facts) == instance.gold_answer:
        return 0.9
    if visible_facts:
        return 0.45
    return 0.0


def base_record(
    *,
    run_id: str,
    instance: Instance,
    protocol: str,
    public_state_surface: str,
    communication_policy: str,
    source: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "method_family": METHOD_FAMILY,
        "method": protocol,
        "instance_id": instance.instance_id,
        "sample_index": instance.sample_index,
        "question": instance.question,
        "gold_answer": instance.gold_answer,
        "task_regime": instance.regime,
        "public_state": {
            "surface": public_state_surface,
            "communication_policy": communication_policy,
        },
        "final": {"answer": None, "correct": None},
        "transition": {
            "from_stage": "independent_majority",
            "to_stage": "final",
            "type": "unknown",
            "before_answer": None,
            "before_correct": None,
            "after_answer": None,
            "after_correct": None,
        },
        "rounds": [],
        "retention_events": [],
        "communication_events": [],
        "context_events": [],
        "token_cost": {
            "scope": "sample",
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "compressed_prompt_tokens": None,
            "compressed_completion_tokens": None,
            "compressed_total_tokens": None,
        },
        "method_comparison": None,
        "source": source,
    }


def add_context_events(record: Dict[str, Any], visible_by_agent: Dict[str, List[Fact]], instruction: str) -> None:
    for agent_id in AGENTS:
        record["context_events"].append(
            {
                "stage": "round_0_context",
                "agent_id": agent_id,
                "context_instruction": instruction,
                "visible_fact_ids": [fact.fact_id for fact in visible_by_agent.get(agent_id, [])],
            }
        )


def finalize_record(
    record: Dict[str, Any],
    *,
    instance: Instance,
    rounds: List[Dict[str, Any]],
    final_answer: Any,
    baseline_answer: Any,
    extra_input_tokens: int = 0,
    extra_output_tokens: int = 0,
) -> Dict[str, Any]:
    final_correct = is_correct(final_answer, instance.gold_answer)
    baseline_correct = is_correct(baseline_answer, instance.gold_answer)
    round_input = sum(
        int(agent["tokens"]["input_tokens"])
        for round_data in rounds
        for agent in round_data.get("agents", [])
    )
    round_output = sum(
        int(agent["tokens"]["output_tokens"])
        for round_data in rounds
        for agent in round_data.get("agents", [])
    )
    input_tokens = round_input + extra_input_tokens
    output_tokens = round_output + extra_output_tokens
    record["rounds"] = rounds
    record["final"] = {"answer": final_answer, "correct": final_correct}
    record["transition"] = {
        "from_stage": "independent_majority",
        "to_stage": "final",
        "type": transition_type(baseline_correct, final_correct),
        "before_answer": baseline_answer,
        "before_correct": baseline_correct,
        "after_answer": final_answer,
        "after_correct": final_correct,
    }
    record["token_cost"] = {
        "scope": "sample",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "compressed_prompt_tokens": None,
        "compressed_completion_tokens": None,
        "compressed_total_tokens": None,
    }
    return record


def run_protocol(run_id: str, instance: Instance, protocol: str) -> Dict[str, Any]:
    private_visibility = {agent_id: owner_facts(instance, agent_id) for agent_id in AGENTS}
    private_round = round_from_visibility(instance, private_visibility)
    baseline_answer = private_round["debate_answer"]

    source = {"generator": "harness/communication_regimes.py"}

    if protocol == "single_agent":
        visible = {"Agent1": owner_facts(instance, "Agent1"), "Agent2": [], "Agent3": []}
        round_data = round_from_visibility(instance, visible)
        final_answer = round_data["agents"][0]["answer"]
        record = base_record(
            run_id=run_id,
            instance=instance,
            protocol=protocol,
            public_state_surface="private_context",
            communication_policy="none",
            source=source,
        )
        add_context_events(record, visible, "Answer from Agent1 private context only.")
        return finalize_record(
            record,
            instance=instance,
            rounds=[round_data],
            final_answer=final_answer,
            baseline_answer=baseline_answer,
        )

    if protocol == "independent_majority":
        record = base_record(
            run_id=run_id,
            instance=instance,
            protocol=protocol,
            public_state_surface="none",
            communication_policy="none",
            source=source,
        )
        add_context_events(record, private_visibility, "Answer from private context; no peer state is visible.")
        return finalize_record(
            record,
            instance=instance,
            rounds=[private_round],
            final_answer=baseline_answer,
            baseline_answer=baseline_answer,
        )

    if protocol == "full_broadcast":
        visible = {agent_id: all_facts(instance) for agent_id in AGENTS}
        round_data = round_from_visibility(instance, visible)
        final_answer = round_data["debate_answer"]
        broadcast_facts = all_facts(instance)
        record = base_record(
            run_id=run_id,
            instance=instance,
            protocol=protocol,
            public_state_surface="full_reasoning",
            communication_policy="broadcast",
            source=source,
        )
        record["communication_events"].append(
            {
                "stage": "pre_round_broadcast",
                "mechanism": "broadcast_all_facts",
                "source_agent_ids": AGENTS,
                "routed_agent_ids": AGENTS,
                "fact_ids": [fact.fact_id for fact in broadcast_facts],
                "token_cost": estimate_tokens(fact.text for fact in broadcast_facts),
            }
        )
        add_context_events(record, visible, "Answer after receiving all peer facts and distractors.")
        return finalize_record(
            record,
            instance=instance,
            rounds=[round_data],
            final_answer=final_answer,
            baseline_answer=baseline_answer,
            extra_input_tokens=estimate_tokens(fact.text for fact in broadcast_facts),
        )

    if protocol == "evidence_state":
        public_facts = relevant_facts(instance)
        visible = {agent_id: public_facts for agent_id in AGENTS}
        round_data = round_from_visibility(instance, visible)
        final_answer = answer_from_facts(instance, public_facts)
        record = base_record(
            run_id=run_id,
            instance=instance,
            protocol=protocol,
            public_state_surface="structured_evidence",
            communication_policy="public_state_update",
            source=source,
        )
        record["communication_events"].append(
            {
                "stage": "public_state_build",
                "mechanism": "oracle_structured_evidence_state",
                "source_agent_ids": sorted({fact.owner for fact in public_facts}),
                "routed_agent_ids": AGENTS,
                "fact_ids": [fact.fact_id for fact in public_facts],
                "token_cost": estimate_tokens(fact.text for fact in public_facts),
            }
        )
        add_context_events(record, visible, "Answer from structured public evidence state.")
        return finalize_record(
            record,
            instance=instance,
            rounds=[round_data],
            final_answer=final_answer,
            baseline_answer=baseline_answer,
            extra_input_tokens=estimate_tokens(fact.text for fact in public_facts),
        )

    if protocol == "route_or_silence":
        routed = routed_facts(instance)
        visible = {agent_id: unique_facts([*owner_facts(instance, agent_id), *routed]) for agent_id in AGENTS}
        round_data = round_from_visibility(instance, visible)
        final_answer = round_data["debate_answer"]
        silent_agents = [agent_id for agent_id in AGENTS if not any(fact.owner == agent_id for fact in routed)]
        record = base_record(
            run_id=run_id,
            instance=instance,
            protocol=protocol,
            public_state_surface="routed_evidence",
            communication_policy="route_or_silence",
            source=source,
        )
        record["communication_events"].append(
            {
                "stage": "pre_round_routing",
                "mechanism": "oracle_route_relevant_facts",
                "source_agent_ids": sorted({fact.owner for fact in routed}),
                "silent_agent_ids": silent_agents,
                "routed_agent_ids": AGENTS,
                "fact_ids": [fact.fact_id for fact in routed],
                "token_cost": estimate_tokens(fact.text for fact in routed),
            }
        )
        add_context_events(record, visible, "Answer from private context plus routed relevant public facts.")
        return finalize_record(
            record,
            instance=instance,
            rounds=[round_data],
            final_answer=final_answer,
            baseline_answer=baseline_answer,
            extra_input_tokens=estimate_tokens(fact.text for fact in routed),
        )

    raise ValueError(f"Unknown protocol: {protocol}")


def routed_facts(instance: Instance) -> List[Fact]:
    if instance.regime == "saturated_arithmetic":
        return []
    return relevant_facts(instance)


def make_recall(sample_index: int, rng: random.Random) -> Instance:
    code = rng.choice(["blue-17", "green-42", "amber-09", "violet-31"])
    distractors = [item for item in ["red-12", "silver-28", "black-03"] if item != code]
    facts = (
        Fact(f"recall-{sample_index}-a1", "Agent1", "distractor", "Old case code = " + distractors[0], distractors[0], False),
        Fact(f"recall-{sample_index}-a2", "Agent2", "answer", "Current case access_code = " + code, code, True),
        Fact(f"recall-{sample_index}-a3", "Agent3", "distractor", "Nearby case code = " + distractors[1], distractors[1], False),
    )
    return Instance(
        instance_id=f"recall-{sample_index}",
        sample_index=sample_index,
        regime="recall",
        question=f"What is the current access code for case {sample_index}?",
        gold_answer=code,
        facts=facts,
    )


def make_state_tracking(sample_index: int, rng: random.Random) -> Instance:
    init = rng.randint(2, 8)
    add_amount = rng.randint(2, 5)
    mul_amount = rng.randint(2, 4)
    sub_amount = rng.randint(1, 4)
    gold = (init + add_amount) * mul_amount - sub_amount
    facts = (
        Fact(f"state-{sample_index}-a1", "Agent1", "init", f"Initial counter = {init}; then add {add_amount}.", init, True, order=0),
        Fact(f"state-{sample_index}-a1-op", "Agent1", "operation", f"Operation 1: add {add_amount}.", ("add", add_amount), True, order=1),
        Fact(f"state-{sample_index}-a2-op", "Agent2", "operation", f"Operation 2: multiply by {mul_amount}.", ("mul", mul_amount), True, order=2),
        Fact(f"state-{sample_index}-a3-op", "Agent3", "operation", f"Operation 3: subtract {sub_amount}.", ("sub", sub_amount), True, order=3),
    )
    return Instance(
        instance_id=f"state-{sample_index}",
        sample_index=sample_index,
        regime="state_tracking",
        question=f"After all distributed updates for counter {sample_index}, what is the final value?",
        gold_answer=gold,
        facts=facts,
    )


def make_k_hop(sample_index: int, rng: random.Random) -> Instance:
    node_b = rng.choice(["room_b", "case_b", "item_b"])
    node_c = rng.choice(["room_c", "case_c", "item_c"])
    value = rng.choice(["north", "south", "east", "west"])
    facts = (
        Fact(f"khop-{sample_index}-a1", "Agent1", "link_1", f"start -> {node_b}.", node_b, True),
        Fact(f"khop-{sample_index}-a2", "Agent2", "link_2", f"{node_b} -> {node_c}.", node_c, True),
        Fact(f"khop-{sample_index}-a3", "Agent3", "value", f"{node_c} has label {value}.", value, True),
        Fact(f"khop-{sample_index}-d", "Agent1", "distractor", "Unrelated node has label center.", "center", False),
    )
    return Instance(
        instance_id=f"khop-{sample_index}",
        sample_index=sample_index,
        regime="k_hop",
        question=f"Follow the distributed links for sample {sample_index}; what label is at the final node?",
        gold_answer=value,
        facts=facts,
    )


def make_conflict_evidence(sample_index: int, rng: random.Random) -> Instance:
    gold = rng.choice(["approve", "reject"])
    wrong = "reject" if gold == "approve" else "approve"
    facts = (
        Fact(
            f"conflict-{sample_index}-a1",
            "Agent1",
            "label_evidence",
            f"Weak surface cue suggests {wrong}.",
            wrong,
            True,
            confidence=0.54,
        ),
        Fact(
            f"conflict-{sample_index}-a2",
            "Agent2",
            "label_evidence",
            f"Another weak cue also suggests {wrong}.",
            wrong,
            True,
            confidence=0.57,
        ),
        Fact(
            f"conflict-{sample_index}-a3",
            "Agent3",
            "label_evidence",
            f"High-specificity evidence supports {gold}.",
            gold,
            True,
            confidence=0.91,
        ),
    )
    return Instance(
        instance_id=f"conflict-{sample_index}",
        sample_index=sample_index,
        regime="conflict_evidence",
        question=f"Resolve the conflicting label for item {sample_index}.",
        gold_answer=gold,
        facts=facts,
    )


def make_saturated_arithmetic(sample_index: int, rng: random.Random) -> Instance:
    left = rng.randint(4, 12)
    right = rng.randint(3, 9)
    gold = left + right
    facts = tuple(
        Fact(
            f"arith-{sample_index}-{agent.lower()}",
            agent,
            "equation",
            f"Everyone sees {left} + {right}.",
            (left, right),
            True,
        )
        for agent in AGENTS
    )
    return Instance(
        instance_id=f"arith-{sample_index}",
        sample_index=sample_index,
        regime="saturated_arithmetic",
        question=f"What is {left} + {right}?",
        gold_answer=gold,
        facts=facts,
    )


def make_instances(samples_per_regime: int, seed: int) -> List[Instance]:
    rng = random.Random(seed)
    makers = {
        "recall": make_recall,
        "state_tracking": make_state_tracking,
        "k_hop": make_k_hop,
        "conflict_evidence": make_conflict_evidence,
        "saturated_arithmetic": make_saturated_arithmetic,
    }
    instances = []
    sample_index = 0
    for regime in REGIMES:
        for _ in range(samples_per_regime):
            instances.append(makers[regime](sample_index, rng))
            sample_index += 1
    return instances


def summarize(records: Sequence[Dict[str, Any]], run_id: str, samples_per_regime: int, seed: int) -> Dict[str, Any]:
    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for record in records:
        key = (record["task_regime"], record["method"])
        groups.setdefault(key, []).append(record)

    rows = []
    for (regime, protocol), group in sorted(groups.items()):
        correct = sum(1 for record in group if record["final"]["correct"])
        total_tokens = sum(int(record["token_cost"]["total_tokens"] or 0) for record in group)
        communication_tokens = sum(
            int(event.get("token_cost") or 0)
            for record in group
            for event in record.get("communication_events", [])
        )
        changed_by_communication = sum(
            1
            for record in group
            if record["transition"]["type"] in {"wrong_to_right", "right_to_wrong"}
        )
        rows.append(
            {
                "task_regime": regime,
                "protocol": protocol,
                "correct": correct,
                "total": len(group),
                "accuracy": correct / len(group) if group else None,
                "avg_total_tokens": total_tokens / len(group) if group else None,
                "avg_communication_tokens": communication_tokens / len(group) if group else None,
                "changed_by_communication": changed_by_communication,
            }
        )

    return {
        "run_id": run_id,
        "schema_version": SCHEMA_VERSION,
        "seed": seed,
        "samples_per_regime": samples_per_regime,
        "regimes": REGIMES,
        "protocols": PROTOCOLS,
        "records": len(records),
        "summary_rows": rows,
        "caveats": [
            "Deterministic toy harness; not LLM behavior.",
            "evidence_state and route_or_silence use oracle relevance to expose the communication variable.",
            "Token counts are rough word-count proxies.",
        ],
    }


def write_jsonl(path: Path, records: Sequence[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_readme(out_dir: Path, summary: Dict[str, Any], command: str, started_at: str, ended_at: str) -> None:
    rows = "\n".join(
        "| {task_regime} | {protocol} | {correct}/{total} | {accuracy:.2f} | {avg_total_tokens:.1f} | {avg_communication_tokens:.1f} | {changed_by_communication} |".format(
            **row
        )
        for row in summary["summary_rows"]
    )
    readme = f"""# {summary['run_id']}

## What We Tried

Ran the deterministic communication-regime harness as a CPU-only smoke check.

## Scope

- Method: CommunicationRegimeHarness
- Model: deterministic symbolic agents
- Dataset: generated toy regimes
- Seed: {summary['seed']}
- Samples: {summary['samples_per_regime']} per regime
- Comparison target: protocol differences across task regimes

## Resource Notes

- Machine: local Windows workspace
- GPU IDs: none
- Timeout: none
- Started by: Codex

## Code

- Upstream repo: local project harness
- Commit: local working tree
- Local changes: `harness/communication_regimes.py`

## Environment

- Env path: local default Python
- Backend: CPU-only Python standard library

## Data

- Data path: generated in memory
- Regimes: `{', '.join(summary['regimes'])}`
- Sampling: deterministic seed `{summary['seed']}`

## Command

```bash
{command}
```

## Outputs

- Records: `communication_regime_records.jsonl`
- Summary: `summary.json`
- Manifest: `manifest.json`

## Result

| Regime | Protocol | Correct | Accuracy | Avg Total Tokens | Avg Communication Tokens | Changed vs Independent |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
{rows}

## Notes

- This is a contact harness, not benchmark evidence.
- `evidence_state` and `route_or_silence` use oracle relevance so we can inspect the communication variable before adding model noise.
- `context_events` are populated for every record, unlike the current extracted MAD-MM/DAR/MOC traces.

## Status Timeline

- `{started_at}`: launched
- `{ended_at}`: completed

## Caveats

- Symbolic agents are not LLM agents.
- Token counts are rough word-count proxies.
- This run is useful for schema pressure and regime separation, not method superiority.

## Loose Threads

- Add a non-oracle router later, or map one real baseline trace into the same regime labels.
- Decide whether the next model run should target k-hop/conflict evidence rather than saturated arithmetic.
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")


def run(args: argparse.Namespace) -> Dict[str, Any]:
    started_at = datetime.now().isoformat(timespec="seconds")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    instances = make_instances(args.samples_per_regime, args.seed)
    records = [
        run_protocol(args.run_id, instance, protocol)
        for instance in instances
        for protocol in PROTOCOLS
    ]
    summary = summarize(records, args.run_id, args.samples_per_regime, args.seed)

    records_path = out_dir / "communication_regime_records.jsonl"
    summary_path = out_dir / "summary.json"
    manifest_path = out_dir / "manifest.json"

    write_jsonl(records_path, records)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    ended_at = datetime.now().isoformat(timespec="seconds")
    command = "python harness/communication_regimes.py " + " ".join(args.raw_args)
    manifest = {
        "run_id": args.run_id,
        "status": "completed",
        "method": METHOD_FAMILY,
        "model": "deterministic-symbolic-agents",
        "dataset": "generated-communication-regimes",
        "seed": args.seed,
        "samples": len(records),
        "machine": "local",
        "gpu_ids": [],
        "timeout_minutes": None,
        "started_at": started_at,
        "ended_at": ended_at,
        "upstream_repo": "",
        "upstream_commit": "",
        "local_changes": ["harness/communication_regimes.py"],
        "command": command,
        "log_path": "",
        "result_paths": [str(records_path), str(summary_path)],
        "metrics": {
            "accuracy": None,
            "total_tokens": sum(int(record["token_cost"]["total_tokens"] or 0) for record in records),
            "eval_time_seconds": None,
            "wall_time_seconds": None,
        },
        "caveats": summary["caveats"],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    write_readme(out_dir, summary, command, started_at, ended_at)
    return summary


def build_parser(argv: Optional[Sequence[str]] = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--samples-per-regime", type=int, default=4)
    parser.add_argument("--seed", type=int, default=7)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser(argv)
    args = parser.parse_args(argv)
    args.raw_args = list(argv) if argv is not None else []
    if not args.raw_args:
        import sys

        args.raw_args = sys.argv[1:]
    summary = run(args)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
