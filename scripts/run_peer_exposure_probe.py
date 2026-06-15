#!/usr/bin/env python3
"""Run a small peer-exposure probe on saved mixed-correctness cases.

The probe reuses first-round peer responses from an existing DAR or MAD-MM
trace. It first asks the target model to solve each problem without peers, then
asks it to revise after controlled peer exposures such as answer-only, full
rationale, auto-evidence, redacted, or slot-control surfaces.

This is a contact artifact, not a benchmark runner.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from peer_probe.answers import (
    contains_answer,
    extract_final_answer,
    is_correct,
    is_numeric_value,
    normalize_gold,
    normalize_number,
    parse_terminal_output,
    redact_answer_mentions,
    transition_type,
)
from peer_probe.io_utils import read_jsonl, write_json, write_jsonl
from peer_probe.run_notes import write_readme
from peer_probe.surfaces import (
    ALL_CONDITIONS,
    ANSWER_REDACTED_EVIDENCE_CONDITIONS,
    AUTO_EVIDENCE_CONDITIONS,
    DEFAULT_CONDITIONS,
    RAW_ANSWER_ONLY_CONDITIONS,
    SLOT_SURFACE_CONDITIONS,
    TYPED_PUBLIC_STATE_CONDITIONS,
    auto_evidence_prompt,
    auto_evidence_source_peer,
    auto_evidence_surface,
    parse_auto_evidence_output,
    peer_messages,
)


SCHEMA_VERSION = "acr.peer_exposure.v0.5"
METHOD = "PeerExposureMiniProbe"

DEFAULT_CASE_ORDER = [20, 78, 4, 8, 37, 65, 5, 22, 13, 14]


def compact_agent_id(agent_id: Optional[str]) -> Optional[str]:
    if not agent_id:
        return agent_id
    if "__" in agent_id:
        return agent_id.rsplit("__", 1)[-1]
    return agent_id


def answer_by_agent(round_data: Dict[str, Any]) -> Dict[str, Any]:
    responses = round_data.get("responses") or {}
    agents = list(responses.keys()) if isinstance(responses, dict) else []
    answers = round_data.get("final_answers") or []
    return {agent: answers[index] if index < len(answers) else None for index, agent in enumerate(agents)}


def correct_by_agent(round_data: Dict[str, Any]) -> Dict[str, Any]:
    responses = round_data.get("responses") or {}
    agents = list(responses.keys()) if isinstance(responses, dict) else []
    correctness = round_data.get("final_answer_iscorr") or []
    return {agent: correctness[index] if index < len(correctness) else None for index, agent in enumerate(agents)}


def strip_uncertainty(text: str) -> str:
    return re.sub(r"\n+\s*Uncertainty score.*$", "", text.strip(), flags=re.I | re.S).strip()


def load_shuffled_gsm8k(path: Path, data_size: int) -> List[Dict[str, Any]]:
    try:
        import pandas as pd  # type: ignore
    except ImportError as exc:
        raise RuntimeError("pandas is required to reproduce DAR's GSM8K fallback shuffle") from exc
    rows = read_jsonl(path)
    frame = pd.DataFrame(rows).sample(frac=1, random_state=0).reset_index(drop=True)
    if data_size:
        frame = frame.head(data_size)
    return [dict(row) for _, row in frame.iterrows()]


def madmm_response_text(agent_row: Dict[str, Any]) -> str:
    response = agent_row.get("response") or {}
    if isinstance(response, dict):
        think = str(response.get("think") or "").strip()
        answer = str(response.get("answer") or "").strip()
        if think and answer:
            return f"{think}\n\nFinal answer from this peer: {answer}"
        return think or answer
    return str(response)


def case_from_madmm_trace(
    *,
    trace_record: Dict[str, Any],
    debate_case: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    case_index = int(trace_record.get("sample_index") or 0)
    instance_id = str(trace_record.get("instance_id"))
    gold = trace_record.get("gold_answer")
    if not is_numeric_value(gold):
        return None

    round0 = next(
        (round_data for round_data in (trace_record.get("rounds") or []) if round_data.get("round_index") == 0),
        {},
    )
    trace_agents = round0.get("agents") or []
    debate_rounds = debate_case.get("rounds") or []
    debate_agents = (debate_rounds[0].get("agents") if debate_rounds else []) or []
    correct_indices = [
        index
        for index, agent in enumerate(trace_agents)
        if agent.get("correct") is True and normalize_number(agent.get("answer")) is not None
    ]
    wrong_indices = [
        index
        for index, agent in enumerate(trace_agents)
        if agent.get("correct") is False and normalize_number(agent.get("answer")) is not None
    ]
    if not correct_indices or not wrong_indices:
        return None

    def peer_from_index(index: int) -> Dict[str, Any]:
        trace_agent = trace_agents[index]
        debate_agent = debate_agents[index] if index < len(debate_agents) else {}
        agent_id = trace_agent.get("agent_id") or f"Agent{index + 1}"
        return {
            "agent_id": agent_id,
            "compact_agent_id": compact_agent_id(agent_id),
            "answer": normalize_number(trace_agent.get("answer")),
            "response": strip_uncertainty(madmm_response_text(debate_agent)),
        }

    return {
        "case_index": case_index,
        "instance_id": instance_id,
        "question": trace_record.get("question") or debate_case.get("question"),
        "gold_answer": normalize_number(gold),
        "gold_rationale": None,
        "source_family": "MAD-MM",
        "source_method": trace_record.get("method"),
        "dar_round0_answers": [
            {
                "agent_id": compact_agent_id(agent.get("agent_id")),
                "raw_agent_id": agent.get("agent_id"),
                "answer": normalize_number(agent.get("answer")),
                "correct": agent.get("correct"),
            }
            for agent in trace_agents
        ],
        "dar_round1_debate_answer": normalize_number((trace_record.get("final") or {}).get("answer")),
        "dar_round1_debate_correct": (trace_record.get("final") or {}).get("correct"),
        "dar_retained_agent_ids": [
            compact_agent_id(agent_id)
            for event in (trace_record.get("retention_events") or [])
            for agent_id in (event.get("retained_agent_ids") or [])
        ],
        "correct_peer": peer_from_index(correct_indices[0]),
        "wrong_peer": peer_from_index(wrong_indices[0]),
    }


def select_from_candidates(
    *,
    candidates: List[Dict[str, Any]],
    case_indices: Optional[List[int]],
    max_cases: int,
    selection_mode: str,
    sample_seed: int,
) -> List[Dict[str, Any]]:
    selected = []
    seen = set()
    if selection_mode not in {"default", "first", "random"}:
        raise ValueError(f"Unknown selection mode: {selection_mode}")

    explicit_indices = case_indices
    if explicit_indices is None and selection_mode == "default":
        explicit_indices = DEFAULT_CASE_ORDER
    explicit_indices = explicit_indices or []

    by_case_index = {int(case["case_index"]): case for case in candidates}
    by_instance_id = {str(case.get("instance_id", case["case_index"])): case for case in candidates}
    for index in explicit_indices:
        case = by_case_index.get(index) or by_instance_id.get(str(index))
        if not case:
            continue
        key = str(case.get("instance_id", case["case_index"]))
        if key in seen:
            continue
        selected.append(case)
        seen.add(key)
        if max_cases and len(selected) >= max_cases:
            return selected

    remaining = [case for case in candidates if str(case.get("instance_id", case["case_index"])) not in seen]
    if selection_mode == "random":
        random.Random(sample_seed).shuffle(remaining)
    for case in remaining:
        key = str(case.get("instance_id", case["case_index"]))
        if key in seen:
            continue
        selected.append(case)
        seen.add(key)
        if max_cases and len(selected) >= max_cases:
            break
    return selected


def load_madmm_math_cases(
    *,
    trace_jsonl: Path,
    debate_log_json: Path,
    case_indices: Optional[List[int]],
    max_cases: int,
    method: str,
    selection_mode: str,
    sample_seed: int,
) -> List[Dict[str, Any]]:
    trace_rows = read_jsonl(trace_jsonl)
    debate_log = json.loads(debate_log_json.read_text(encoding="utf-8"))
    candidates = []
    for record in trace_rows:
        if record.get("method") != method:
            continue
        instance_id = str(record.get("instance_id"))
        debate_case = debate_log.get(instance_id)
        if not debate_case:
            continue
        case = case_from_madmm_trace(trace_record=record, debate_case=debate_case)
        if case:
            candidates.append(case)

    return select_from_candidates(
        candidates=candidates,
        case_indices=case_indices,
        max_cases=max_cases,
        selection_mode=selection_mode,
        sample_seed=sample_seed,
    )


def load_source_cases(
    *,
    source_cases_jsonl: Path,
    case_indices: Optional[List[int]],
    max_cases: int,
    selection_mode: str,
    sample_seed: int,
) -> List[Dict[str, Any]]:
    candidates = read_jsonl(source_cases_jsonl)
    return select_from_candidates(
        candidates=candidates,
        case_indices=case_indices,
        max_cases=max_cases,
        selection_mode=selection_mode,
        sample_seed=sample_seed,
    )


def case_from_history(
    *,
    case_index: int,
    history_record: Dict[str, Any],
    gsm8k_row: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    round0 = history_record.get("0") or {}
    round1 = history_record.get("1") or {}
    responses = round0.get("responses") or {}
    answers = answer_by_agent(round0)
    correctness = correct_by_agent(round0)
    correct_agents = [
        agent for agent in responses if correctness.get(agent) is True and normalize_number(answers.get(agent)) is not None
    ]
    wrong_agents = [
        agent for agent in responses if correctness.get(agent) is False and normalize_number(answers.get(agent)) is not None
    ]
    if not correct_agents or not wrong_agents:
        return None
    event = (round1.get("retention_events") or [{}])[0]
    return {
        "case_index": case_index,
        "instance_id": str(case_index),
        "question": gsm8k_row.get("query") or gsm8k_row.get("question"),
        "gold_answer": normalize_gold(gsm8k_row.get("answer")),
        "gold_rationale": gsm8k_row.get("answer"),
        "source_family": "DAR",
        "source_method": "filter_critical",
        "dar_round0_answers": [
            {
                "agent_id": compact_agent_id(agent),
                "raw_agent_id": agent,
                "answer": normalize_number(answers.get(agent)),
                "correct": correctness.get(agent),
            }
            for agent in responses
        ],
        "dar_round1_debate_answer": normalize_number(round1.get("debate_answer")),
        "dar_round1_debate_correct": round1.get("debate_answer_iscorr"),
        "dar_retained_agent_ids": [compact_agent_id(agent) for agent in event.get("retained_agent_ids") or []],
        "correct_peer": {
            "agent_id": correct_agents[0],
            "compact_agent_id": compact_agent_id(correct_agents[0]),
            "answer": normalize_number(answers.get(correct_agents[0])),
            "response": strip_uncertainty(str(responses.get(correct_agents[0], ""))),
        },
        "wrong_peer": {
            "agent_id": wrong_agents[0],
            "compact_agent_id": compact_agent_id(wrong_agents[0]),
            "answer": normalize_number(answers.get(wrong_agents[0])),
            "response": strip_uncertainty(str(responses.get(wrong_agents[0], ""))),
        },
    }


def select_cases(
    *,
    history_rows: List[Dict[str, Any]],
    gsm8k_rows: List[Dict[str, Any]],
    case_indices: Optional[List[int]],
    max_cases: int,
    selection_mode: str,
    sample_seed: int,
) -> List[Dict[str, Any]]:
    candidates = []
    for index, record in enumerate(history_rows):
        if index >= len(gsm8k_rows):
            continue
        case = case_from_history(case_index=index, history_record=record, gsm8k_row=gsm8k_rows[index])
        if case:
            candidates.append(case)
    return select_from_candidates(
        candidates=candidates,
        case_indices=case_indices,
        max_cases=max_cases,
        selection_mode=selection_mode,
        sample_seed=sample_seed,
    )


def solve_prompt(question: str) -> str:
    return f"""Solve the math word problem carefully.

Problem:
{question}

Give concise reasoning, then end with exactly one line in this format:
{{final answer: <answer>}}"""


def build_auto_evidence_peer_messages(
    *,
    case: Dict[str, Any],
    condition: str,
    base_url: str,
    model: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
    run_id: str,
) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    source_peer, expected_correct = auto_evidence_source_peer(case, condition)
    surface = auto_evidence_surface(condition)
    peer_response = source_peer["response"]
    source_answer_redaction_count = 0
    if surface == "answer_redacted_evidence":
        peer_response, source_answer_redaction_count = redact_answer_mentions(peer_response, source_peer["answer"])
    prompt = auto_evidence_prompt(case["question"], peer_response, source_peer["answer"], surface)
    output, usage = chat_completion(
        base_url=base_url,
        model=model,
        api_key=api_key,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    evidence, parse_source = parse_auto_evidence_output(output)
    extraction_id = f"{run_id}:{case['case_index']}:{condition}:{source_peer['compact_agent_id']}"
    peer = {
        "source": source_peer["compact_agent_id"],
        "surface": surface,
        "text": f"Key evidence: {evidence}",
        "answer": "",
        "source_answer": str(source_peer["answer"]),
        "expected_correct": expected_correct,
        "auto_extraction_id": extraction_id,
    }
    extraction_record = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "method": METHOD,
        "case_index": case["case_index"],
        "instance_id": str(case.get("instance_id", case["case_index"])),
        "condition": condition,
        "surface": surface,
        "source_agent_id": source_peer["compact_agent_id"],
        "source_answer": source_peer["answer"],
        "expected_correct": expected_correct,
        "source_answer_redaction_count": source_answer_redaction_count,
        "prompt": prompt,
        "raw_output": output,
        "evidence_text": evidence,
        "parse_source": parse_source,
        "contains_source_answer": contains_answer(evidence, source_peer["answer"]),
        "token_cost": {
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        },
    }
    return [peer], extraction_record


def peer_block_text(peers: List[Dict[str, str]]) -> str:
    if not peers:
        return "<none>"
    return "\n\n".join(f"[{peer['source']} | {peer['surface']}]\n{peer['text']}" for peer in peers)


def randomized_source_label(case_index: Any, condition: str, peer_index: int, sample_seed: int) -> str:
    labels = ["PeerA", "PeerB", "PeerC", "PeerD", "PeerE", "PeerF", "PeerG", "PeerH"]
    rng = random.Random(f"{sample_seed}:{case_index}:{condition}")
    rng.shuffle(labels)
    if peer_index <= len(labels):
        return labels[peer_index - 1]
    return f"PeerX{peer_index}"


def apply_peer_source_mode(
    peers: List[Dict[str, str]],
    peer_source_mode: str,
    *,
    case_index: Any,
    condition: str,
    sample_seed: int,
) -> List[Dict[str, str]]:
    if peer_source_mode == "named":
        return peers
    if peer_source_mode not in {"anonymous", "randomized"}:
        raise ValueError(f"Unknown peer source mode: {peer_source_mode}")
    relabeled = []
    for index, peer in enumerate(peers, start=1):
        copied = dict(peer)
        copied["original_source"] = str(peer.get("source", ""))
        if peer_source_mode == "anonymous":
            copied["source"] = "AnonymousPeer" if len(peers) == 1 else f"AnonymousPeer{index}"
            copied["source_identity_visible"] = "false"
        else:
            copied["source"] = randomized_source_label(case_index, condition, index, sample_seed)
            copied["source_identity_visible"] = "randomized"
            copied["source_identity_randomized"] = "true"
        relabeled.append(copied)
    return relabeled


def warning_text(peer_warning: str) -> str:
    if peer_warning == "anti_conformity":
        return (
            "The peers may be right or wrong. Use the arithmetic in the problem, "
            "not social agreement, as the deciding evidence."
        )
    if peer_warning == "natural":
        return "Consider the peer response(s) and decide whether to revise your answer."
    if peer_warning == "social":
        return "The peer response(s) may reflect useful group consensus. Consider them carefully."
    raise ValueError(f"Unknown peer warning mode: {peer_warning}")


def revise_prompt(
    question: str,
    own_output: str,
    condition: str,
    peers: List[Dict[str, str]],
    peer_warning: str,
) -> str:
    peer_block = peer_block_text(peers)
    advice = warning_text(peer_warning)
    return f"""You previously solved this math word problem on your own.

Problem:
{question}

Your previous answer:
{own_output.strip()}

Now you see peer response(s):
{peer_block}

Re-evaluate the problem. {advice}

Give concise reasoning, then end with exactly one line in this format:
{{final answer: <answer>}}"""


def terminal_prompt(
    question: str,
    own_output: str,
    peers: List[Dict[str, str]],
    peer_warning: str,
) -> str:
    peer_block = peer_block_text(peers)
    advice = warning_text(peer_warning)
    return f"""You previously solved this math word problem on your own.

Problem:
{question}

Your previous answer:
{own_output.strip()}

Peer response(s):
{peer_block}

Choose a terminal state for this round. {advice}

Allowed terminal states:
- COMMIT: give a final answer because the evidence is sufficient.
- DISAGREE: there are competing answers or interpretations that remain unresolved.
- NEEDS_EVIDENCE: a specific relation or quantity is missing.
- ABORT: the problem cannot be answered from the provided information.

Use exactly this format:
Decision: <COMMIT|DISAGREE|NEEDS_EVIDENCE|ABORT>
Answer: <answer or NONE>
Reason: <one concise sentence>"""


def chat_completion(
    *,
    base_url: str,
    model: str,
    api_key: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> Tuple[str, Dict[str, Any]]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {detail}") from exc
    data = json.loads(raw)
    return data["choices"][0]["message"]["content"], data.get("usage") or {}


def peer_answer_adopted(answer: Any, peers: List[Dict[str, str]]) -> bool:
    answer_norm = normalize_number(answer)
    return any(answer_norm == normalize_number(peer.get("answer")) for peer in peers)


def record_from_output(
    *,
    run_id: str,
    model: str,
    case: Dict[str, Any],
    condition: str,
    prompt: str,
    output: str,
    usage: Dict[str, Any],
    own_answer: Any,
    own_correct: Optional[bool],
    own_output: Optional[str],
    peers: List[Dict[str, str]],
    include_prompt: bool,
    response_mode: str,
) -> Dict[str, Any]:
    terminal = None
    if response_mode == "terminal":
        terminal = parse_terminal_output(output)
        parsed = terminal["answer"]
        parse_source = terminal["parse_source"]
    else:
        parsed, parse_source = extract_final_answer(output)
    correct = is_correct(parsed, case["gold_answer"])
    transition = transition_type(own_correct, correct) if condition != "no_peer" else "baseline"
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "method": METHOD,
        "model": model,
        "response_mode": response_mode,
        "case_index": case["case_index"],
        "instance_id": str(case.get("instance_id", case["case_index"])),
        "question": case["question"],
        "gold_answer": case["gold_answer"],
        "condition": condition,
        "peer_exposure": peers,
        "pre_exposure_answer": own_answer,
        "pre_exposure_correct": own_correct,
        "pre_exposure_output": own_output,
        "post_exposure_answer": parsed,
        "post_exposure_correct": correct,
        "post_exposure_output": output,
        "parse_source": parse_source,
        "terminal_state": terminal,
        "transition": transition,
        "peer_answer_adopted": peer_answer_adopted(parsed, peers) if peers else False,
        "source_trace": {
            "source_family": case.get("source_family"),
            "source_method": case.get("source_method"),
            "round0_answers": case["dar_round0_answers"],
            "round1_debate_answer": case["dar_round1_debate_answer"],
            "round1_debate_correct": case["dar_round1_debate_correct"],
            "retained_agent_ids": case["dar_retained_agent_ids"],
        },
        "token_cost": {
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        },
        "prompt": prompt if include_prompt else None,
    }


def summarize(
    records: List[Dict[str, Any]],
    run_id: str,
    peer_warning: str,
    response_mode: str,
    peer_source_mode: str,
) -> Dict[str, Any]:
    by_condition: Dict[str, Counter] = defaultdict(Counter)
    adoption: Dict[str, Counter] = defaultdict(Counter)
    cases = sorted({row["case_index"] for row in records})
    for row in records:
        condition = row["condition"]
        by_condition[condition]["records"] += 1
        if row["post_exposure_correct"] is True:
            by_condition[condition]["correct"] += 1
        if row["post_exposure_correct"] is None:
            by_condition[condition]["unparseable"] += 1
        if row["pre_exposure_correct"] is True:
            by_condition[condition]["pre_correct"] += 1
        if row["pre_exposure_correct"] is None:
            by_condition[condition]["pre_unparseable"] += 1
        by_condition[condition][row["transition"]] += 1
        terminal = row.get("terminal_state") or {}
        if terminal.get("decision"):
            by_condition[condition][f"decision_{terminal['decision']}"] += 1
        if row["peer_answer_adopted"]:
            adoption[condition]["peer_answer_adopted"] += 1
    condition_summary = {}
    for condition, counter in sorted(by_condition.items()):
        records_count = counter["records"]
        condition_summary[condition] = {
            **dict(counter),
            "accuracy": counter["correct"] / records_count if records_count else None,
            "peer_answer_adoption_rate": (
                adoption[condition]["peer_answer_adopted"] / records_count if records_count else None
            ),
        }
    caveats = [
        "Small controlled probe over saved disagreement cases.",
        "Peer messages come from prior multi-agent round-0 outputs; majority and authority conditions reuse one wrong answer as a controlled social cue.",
        "The no-peer baseline is regenerated by this script and may differ from the original multi-agent round-0 answer because the prompt surface differs.",
    ]
    if peer_warning == "anti_conformity":
        caveats.append(
            "Instruction explicitly warns against social agreement, so measured conformity is a lower-bound style stress signal, not natural unconstrained debate."
        )
    elif peer_warning == "natural":
        caveats.append("No explicit anti-conformity warning is included in the revision prompt.")
    elif peer_warning == "social":
        caveats.append("Prompt text tells the model that peer responses may reflect useful group consensus.")
    if response_mode == "terminal":
        caveats.append("Terminal-state outputs are parsed from simple Decision/Answer/Reason fields and are not a calibrated abstention method.")
    if peer_source_mode == "anonymous":
        caveats.append("Peer source labels are anonymized in prompts, which controls source identity but does not remove content-level peer influence.")
    elif peer_source_mode == "randomized":
        caveats.append("Peer source labels are replaced with deterministic randomized aliases, which tests displayed source labels without changing peer content.")
    if any(row["condition"] in AUTO_EVIDENCE_CONDITIONS for row in records):
        caveats.append(
            "Auto-evidence surfaces are model-compressed from peer rationales; the extraction itself may omit, distort, or leak decisive answer information."
        )
    if any(row["condition"] in ANSWER_REDACTED_EVIDENCE_CONDITIONS for row in records):
        caveats.append(
            "Answer-redacted evidence first removes exact parsed-final-answer mentions from the source rationale, but related intermediate numbers can still leak or reconstruct the answer."
        )
    if any(row["condition"] in RAW_ANSWER_ONLY_CONDITIONS for row in records):
        caveats.append(
            "Raw answer-only surfaces display the final-answer text extracted from the saved peer response instead of the older numeric parser field; saved peer-answer adoption is still numeric-parser based unless a later semantic audit recomputes it."
        )
    if any(row["condition"] in SLOT_SURFACE_CONDITIONS for row in records):
        caveats.append(
            "Slot-control surfaces are deterministic text transforms over saved peer rationales; they separate answer, numeric, and equation-bearing slots only heuristically."
        )
    if any(row["condition"] in TYPED_PUBLIC_STATE_CONDITIONS for row in records):
        caveats.append(
            "Typed-public-state surfaces are deterministic previews, not verified state: source identity and explicit final-answer slots are hidden, but copied relation/equation/numeric fields may still contain wrong or answer-reconstructing evidence."
        )
    return {
        "run_id": run_id,
        "method": METHOD,
        "schema_version": SCHEMA_VERSION,
        "peer_warning": peer_warning,
        "peer_source_mode": peer_source_mode,
        "response_mode": response_mode,
        "cases": cases,
        "num_cases": len(cases),
        "num_records": len(records),
        "conditions": condition_summary,
        "caveats": caveats,
    }


def run(args: argparse.Namespace) -> Dict[str, Any]:
    started_at = datetime.now().isoformat(timespec="seconds")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.source_format == "dar_gsm8k":
        history_rows = read_jsonl(Path(args.history_jsonl))
        gsm8k_rows = load_shuffled_gsm8k(Path(args.gsm8k_jsonl), args.data_size)
        cases = select_cases(
            history_rows=history_rows,
            gsm8k_rows=gsm8k_rows,
            case_indices=args.case_indices,
            max_cases=args.max_cases,
            selection_mode=args.selection_mode,
            sample_seed=args.sample_seed,
        )
        dataset_name = "GSM8K via DAR shuffled MAD-MM fallback"
        upstream_repo = "https://github.com/DA2I2-SLM/DAR"
        upstream_commit = "f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0"
    elif args.source_format == "madmm_math":
        cases = load_madmm_math_cases(
            trace_jsonl=Path(args.madmm_trace_jsonl),
            debate_log_json=Path(args.madmm_debate_log_json),
            case_indices=args.case_indices,
            max_cases=args.max_cases,
            method=args.madmm_method,
            selection_mode=args.selection_mode,
            sample_seed=args.sample_seed,
        )
        dataset_name = f"MATH via MAD-MM {args.madmm_method} trace"
        upstream_repo = "https://github.com/HongduanTian/MAD-MM"
        upstream_commit = "project-local copied checkout"
    elif args.source_format == "source_cases":
        cases = load_source_cases(
            source_cases_jsonl=Path(args.source_cases_jsonl),
            case_indices=args.case_indices,
            max_cases=args.max_cases,
            selection_mode=args.selection_mode,
            sample_seed=args.sample_seed,
        )
        dataset_name = "Saved peer-exposure source_cases pool"
        upstream_repo = "local saved probe artifact"
        upstream_commit = "source_cases_jsonl"
    else:
        raise ValueError(f"Unknown source format: {args.source_format}")
    if not cases:
        raise RuntimeError("No mixed-correctness cases selected")

    write_jsonl(out_dir / "source_cases.jsonl", cases)
    if args.dry_run:
        summary = {
            "run_id": args.run_id,
            "method": METHOD,
            "dry_run": True,
            "num_cases": len(cases),
            "cases": [case["case_index"] for case in cases],
            "selection_mode": args.selection_mode,
            "sample_seed": args.sample_seed,
        }
        write_json(out_dir / "summary.json", summary)
        return summary

    records = []
    extraction_records = []
    for case in cases:
        no_peer_prompt = solve_prompt(case["question"])
        own_output, own_usage = chat_completion(
            base_url=args.base_url,
            model=args.model,
            api_key=args.api_key,
            prompt=no_peer_prompt,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            timeout=args.request_timeout,
        )
        own_answer, _ = extract_final_answer(own_output)
        own_correct = is_correct(own_answer, case["gold_answer"])
        if args.response_mode == "answer":
            no_peer_record = record_from_output(
                run_id=args.run_id,
                model=args.model,
                case=case,
                condition="no_peer",
                prompt=no_peer_prompt,
                output=own_output,
                usage=own_usage,
                own_answer=own_answer,
                own_correct=own_correct,
                own_output=None,
                peers=[],
                include_prompt=args.include_prompts,
                response_mode=args.response_mode,
            )
            records.append(no_peer_record)
            if args.sleep_seconds:
                time.sleep(args.sleep_seconds)

        for condition in args.conditions:
            if args.response_mode == "answer" and condition == "no_peer":
                continue
            if condition == "no_peer":
                peers = []
            elif condition in AUTO_EVIDENCE_CONDITIONS:
                peers, extraction_record = build_auto_evidence_peer_messages(
                    case=case,
                    condition=condition,
                    base_url=args.base_url,
                    model=args.model,
                    api_key=args.api_key,
                    temperature=args.temperature,
                    max_tokens=args.extract_max_tokens,
                    timeout=args.request_timeout,
                    run_id=args.run_id,
                )
                extraction_records.append(extraction_record)
            else:
                peers = peer_messages(case, condition)
            peers = apply_peer_source_mode(
                peers,
                args.peer_source_mode,
                case_index=case["case_index"],
                condition=condition,
                sample_seed=args.sample_seed,
            )
            if args.response_mode == "terminal":
                prompt = terminal_prompt(case["question"], own_output, peers, args.peer_warning)
            else:
                prompt = revise_prompt(case["question"], own_output, condition, peers, args.peer_warning)
            output, usage = chat_completion(
                base_url=args.base_url,
                model=args.model,
                api_key=args.api_key,
                prompt=prompt,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                timeout=args.request_timeout,
            )
            records.append(
                record_from_output(
                    run_id=args.run_id,
                    model=args.model,
                    case=case,
                    condition=condition,
                    prompt=prompt,
                    output=output,
                    usage=usage,
                    own_answer=own_answer,
                    own_correct=own_correct,
                    own_output=own_output,
                    peers=peers,
                    include_prompt=args.include_prompts,
                    response_mode=args.response_mode,
                )
            )
            if args.sleep_seconds:
                time.sleep(args.sleep_seconds)

    summary = summarize(records, args.run_id, args.peer_warning, args.response_mode, args.peer_source_mode)
    summary["selection_mode"] = args.selection_mode
    summary["sample_seed"] = args.sample_seed
    summary["num_auto_evidence_extractions"] = len(extraction_records)
    write_jsonl(out_dir / "peer_exposure_records.jsonl", records)
    if extraction_records:
        write_jsonl(out_dir / "auto_evidence_extractions.jsonl", extraction_records)
    write_json(out_dir / "summary.json", summary)
    ended_at = datetime.now().isoformat(timespec="seconds")
    command = "python scripts/run_peer_exposure_probe.py " + " ".join(args.raw_args)
    manifest = {
        "run_id": args.run_id,
        "status": "completed",
        "method": METHOD,
        "model": args.model,
        "dataset": dataset_name,
        "seed": None,
        "samples": len(cases),
        "machine": args.machine,
        "gpu_ids": args.gpu_ids,
        "started_at": started_at,
        "ended_at": ended_at,
        "upstream_repo": upstream_repo,
        "upstream_commit": upstream_commit,
        "local_changes": ["scripts/run_peer_exposure_probe.py"],
        "command": command,
        "log_path": args.server_log or "",
        "result_paths": [
            str(out_dir / "source_cases.jsonl"),
            str(out_dir / "peer_exposure_records.jsonl"),
            str(out_dir / "summary.json"),
        ],
        "metrics": {
            "records": len(records),
            "auto_evidence_extractions": len(extraction_records),
            "total_tokens": sum((row.get("token_cost") or {}).get("total_tokens") or 0 for row in records),
            "auto_evidence_extraction_tokens": sum(
                (row.get("token_cost") or {}).get("total_tokens") or 0 for row in extraction_records
            ),
        },
        "caveats": summary["caveats"],
    }
    if extraction_records:
        manifest["result_paths"].append(str(out_dir / "auto_evidence_extractions.jsonl"))
    write_json(out_dir / "manifest.json", manifest)
    write_readme(
        out_dir,
        summary,
        command,
        started_at,
        ended_at,
        dataset_name=dataset_name,
        model=args.model,
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-format", choices=["dar_gsm8k", "madmm_math", "source_cases"], default="dar_gsm8k")
    parser.add_argument("--history-jsonl", default="")
    parser.add_argument("--gsm8k-jsonl", default="")
    parser.add_argument("--madmm-trace-jsonl", default="")
    parser.add_argument("--madmm-debate-log-json", default="")
    parser.add_argument("--madmm-method", default="mad_naive")
    parser.add_argument("--source-cases-jsonl", default="")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--base-url", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--api-key", default="EMPTY")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--request-timeout", type=int, default=120)
    parser.add_argument("--extract-max-tokens", type=int, default=180)
    parser.add_argument("--data-size", type=int, default=100)
    parser.add_argument("--max-cases", type=int, default=6)
    parser.add_argument("--case-indices", nargs="*", type=int, default=None)
    parser.add_argument("--selection-mode", choices=["default", "first", "random"], default="default")
    parser.add_argument("--sample-seed", type=int, default=42)
    parser.add_argument("--conditions", nargs="+", default=DEFAULT_CONDITIONS, choices=ALL_CONDITIONS)
    parser.add_argument("--peer-warning", choices=["anti_conformity", "natural", "social"], default="anti_conformity")
    parser.add_argument("--peer-source-mode", choices=["named", "anonymous", "randomized"], default="named")
    parser.add_argument("--response-mode", choices=["answer", "terminal"], default="answer")
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--include-prompts", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--machine", default="local")
    parser.add_argument("--gpu-ids", nargs="*", default=[])
    parser.add_argument("--server-log", default="")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.raw_args = list(argv) if argv is not None else sys.argv[1:]
    if args.source_format == "dar_gsm8k" and (not args.history_jsonl or not args.gsm8k_jsonl):
        parser.error("--history-jsonl and --gsm8k-jsonl are required for --source-format dar_gsm8k")
    if args.source_format == "madmm_math" and (not args.madmm_trace_jsonl or not args.madmm_debate_log_json):
        parser.error("--madmm-trace-jsonl and --madmm-debate-log-json are required for --source-format madmm_math")
    if args.source_format == "source_cases" and not args.source_cases_jsonl:
        parser.error("--source-cases-jsonl is required for --source-format source_cases")
    if not args.dry_run and (not args.base_url or not args.model):
        parser.error("--base-url and --model are required unless --dry-run is set")
    summary = run(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
