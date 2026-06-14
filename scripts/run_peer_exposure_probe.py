#!/usr/bin/env python3
"""Run a small peer-exposure probe on saved DAR GSM8K disagreement cases.

The probe reuses first-round peer responses from an existing DAR history. It
first asks the target model to solve each problem without peers, then asks it to
revise after controlled peer exposures such as wrong answer-only, wrong
majority, authority-labeled wrong answer, or full peer rationale.

This is a contact artifact, not a benchmark runner.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


SCHEMA_VERSION = "acr.peer_exposure.v0.4"
METHOD = "PeerExposureMiniProbe"

DEFAULT_CONDITIONS = [
    "no_peer",
    "correct_answer_only",
    "wrong_answer_only",
    "wrong_majority",
    "authority_wrong",
    "wrong_rationale",
    "correct_rationale",
]

SURFACE_DISSECTION_CONDITIONS = [
    "correct_answer_only",
    "wrong_answer_only",
    "wrong_answer_wrong_relation",
    "wrong_plausible_irrelevant",
    "correct_relation_only",
    "correct_rationale",
]

ALL_CONDITIONS = DEFAULT_CONDITIONS + [
    "correct_relation_only",
    "wrong_answer_wrong_relation",
    "wrong_plausible_irrelevant",
    "correct_auto_evidence",
    "wrong_auto_evidence",
    "correct_redacted_evidence",
    "wrong_redacted_evidence",
]

AUTO_EVIDENCE_CONDITIONS = {
    "correct_auto_evidence",
    "wrong_auto_evidence",
    "correct_redacted_evidence",
    "wrong_redacted_evidence",
}
ANSWER_REDACTED_EVIDENCE_CONDITIONS = {"correct_redacted_evidence", "wrong_redacted_evidence"}

DEFAULT_CASE_ORDER = [20, 78, 4, 8, 37, 65, 5, 22, 13, 14]

RELATION_NOTES = {
    8: {
        "correct_relation": (
            "Key relation: Digimon came out 20 years ago. If Jim was J then, "
            "John was 2J then, and John's current age is 2J + 20 = 28."
        ),
        "wrong_relation": (
            "Wrong relation: use John's current age directly as twice Jim's age, "
            "so Jim is about 14 now."
        ),
        "irrelevant": (
            "Irrelevant note: anniversary problems often ask for the age gap "
            "between two people rather than their current ages."
        ),
    },
    37: {
        "correct_relation": (
            "Key relation: the headphone set cost 48 - 4 = 44 dollars. "
            "The question asks how many more CDs the headphone money could buy, "
            "so compare against the CD already bought and compute 44 / 4."
        ),
        "wrong_relation": (
            "Wrong relation: if Tom skips the headphones, he has the full 48 "
            "dollars for CDs, so compute 48 / 4."
        ),
        "irrelevant": (
            "Irrelevant note: the CD price is 4 dollars and the total receipt "
            "was 48 dollars, so there are twelve 4-dollar units in the receipt."
        ),
    },
    78: {
        "correct_relation": (
            "Key relation: 90 people form 10 groups of 9. Three fifths of the "
            "groups is 6 groups. In each selected group, members each bring 2 "
            "seashells, so multiply 6 groups by 9 members by 2 shells."
        ),
        "wrong_relation": (
            "Wrong relation: three fifths of 10 groups is 6 groups, and each "
            "selected group brings 2 seashells total, so compute 6 * 2."
        ),
        "irrelevant": (
            "Irrelevant note: the group leaders split people into smaller groups "
            "for the competition to begin."
        ),
    },
}


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_number(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return int(value) if float(value).is_integer() else float(value)
    text = str(value).replace(",", "")
    fraction = parse_fraction_value(text)
    if fraction is not None:
        number = float(fraction)
        return int(number) if number.is_integer() else number
    matches = re.findall(r"-?\d+(?:\.\d+)?", text)
    if not matches:
        stripped = str(value).strip()
        return stripped if stripped else None
    number = float(matches[-1])
    return int(number) if number.is_integer() else number


def parse_fraction_value(text: str) -> Optional[Fraction]:
    latex_matches = re.findall(
        r"\\frac\s*\{\s*(-?\d+)\s*\}\s*\{\s*(-?\d+)\s*\}",
        text,
    )
    if latex_matches:
        numerator, denominator = latex_matches[-1]
        if int(denominator) != 0:
            return Fraction(int(numerator), int(denominator))

    plain_matches = re.findall(r"(?<![\d.])-?\d+\s*/\s*-?\d+(?![\d.])", text)
    if plain_matches:
        numerator, denominator = re.split(r"\s*/\s*", plain_matches[-1])
        if int(denominator) != 0:
            return Fraction(int(numerator), int(denominator))
    return None


def normalize_gold(value: Any) -> Any:
    text = str(value)
    if "####" in text:
        text = text.split("####")[-1]
    return normalize_number(text)


def normalized_answer_forms(value: Any) -> List[str]:
    forms: List[str] = []
    text = "" if value is None else str(value).strip()
    if text:
        forms.append(text)
        forms.append(text.replace(",", ""))
    number = normalize_number(value)
    if number is not None:
        forms.append(str(number))
        if isinstance(number, int):
            forms.append(f"{number}.0")
    return sorted({form for form in forms if form}, key=len, reverse=True)


def answer_form_pattern(form: str) -> re.Pattern[str]:
    escaped = re.escape(form)
    if re.fullmatch(r"-?\d+(?:\.\d+)?", form.replace(",", "")):
        return re.compile(rf"(?<![\d.]){escaped}(?!\d)(?!\.\d)")
    return re.compile(escaped, flags=re.I)


def contains_answer(text: str, answer: Any) -> bool:
    haystack = text.replace(",", "")
    for form in normalized_answer_forms(answer):
        needle = form.replace(",", "")
        if answer_form_pattern(needle).search(haystack):
            return True
    return False


def redact_answer_mentions(text: str, answer: Any) -> Tuple[str, int]:
    redacted = text
    replacements = 0
    for form in normalized_answer_forms(answer):
        if not form:
            continue
        pattern = answer_form_pattern(form)
        redacted, count = pattern.subn("[REDACTED_FINAL]", redacted)
        replacements += count
    return redacted, replacements


def is_correct(pred: Any, gold: Any) -> Optional[bool]:
    pred_norm = normalize_number(pred)
    gold_norm = normalize_gold(gold)
    if pred_norm is None or gold_norm is None:
        return None
    if isinstance(pred_norm, (int, float)) and isinstance(gold_norm, (int, float)):
        return abs(float(pred_norm) - float(gold_norm)) < 1e-9
    return str(pred_norm).strip().lower() == str(gold_norm).strip().lower()


def transition_type(before: Optional[bool], after: Optional[bool]) -> str:
    if before is None or after is None:
        return "unknown"
    if before and after:
        return "stable_right"
    if before and not after:
        return "right_to_wrong"
    if not before and after:
        return "wrong_to_right"
    return "stable_wrong"


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


def extract_final_answer(text: str) -> Tuple[Any, str]:
    braced = extract_braced_final_answer(text)
    if braced is not None:
        return normalize_number(braced), "explicit_final_answer"
    patterns = [
        r"final\s+answer\s*(?:is|:)\s*([^\n]+)",
        r"answer\s*(?:is|:)\s*([^\n]+)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.I)
        if matches:
            candidate = matches[-1].strip().rstrip(".;")
            return normalize_number(candidate), "explicit_final_answer"
    return None, "no_explicit_final_answer"


def extract_braced_final_answer(text: str) -> Optional[str]:
    starts = list(re.finditer(r"\\?\{\s*final\s+answer\s*:", text, flags=re.I))
    if not starts:
        return None
    match = starts[-1]
    start = match.end()
    depth = 1
    index = start
    while index < len(text):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index].strip()
        index += 1
    return None


def parse_terminal_output(text: str) -> Dict[str, Any]:
    decision_match = re.search(
        r"decision\s*:\s*(COMMIT|DISAGREE|NEEDS_EVIDENCE|ABORT)",
        text,
        flags=re.I,
    )
    answer_match = re.search(r"answer\s*:\s*([^\n]+)", text, flags=re.I)
    reason_match = re.search(r"reason\s*:\s*([^\n]+)", text, flags=re.I)
    decision = decision_match.group(1).upper() if decision_match else None
    answer_text = answer_match.group(1).strip() if answer_match else ""
    if answer_text.upper() in {"", "NONE", "N/A", "NA"}:
        answer = None
    else:
        answer = normalize_number(answer_text)
    return {
        "decision": decision,
        "answer": answer,
        "reason": reason_match.group(1).strip() if reason_match else None,
        "parse_source": "terminal_fields" if decision_match else "no_terminal_decision",
    }


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


def is_numeric_value(value: Any) -> bool:
    norm = normalize_number(value)
    return isinstance(norm, (int, float))


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


def peer_messages(case: Dict[str, Any], condition: str) -> List[Dict[str, str]]:
    correct = case["correct_peer"]
    wrong = case["wrong_peer"]
    relation = RELATION_NOTES.get(int(case["case_index"]), {})
    if condition == "correct_answer_only":
        return [
            {
                "source": correct["compact_agent_id"],
                "surface": "answer_only",
                "text": f"I think the final answer is {correct['answer']}.",
                "answer": str(correct["answer"]),
                "expected_correct": "true",
            }
        ]
    if condition == "wrong_answer_only":
        return [
            {
                "source": wrong["compact_agent_id"],
                "surface": "answer_only",
                "text": f"I think the final answer is {wrong['answer']}.",
                "answer": str(wrong["answer"]),
                "expected_correct": "false",
            }
        ]
    if condition == "correct_relation_only":
        return [
            {
                "source": correct["compact_agent_id"],
                "surface": "relation_only",
                "text": relation.get(
                    "correct_relation",
                    "Key relation: the peer provides a correct relation from the problem, without a final answer.",
                ),
                "answer": "",
                "expected_correct": "true",
            }
        ]
    if condition == "wrong_answer_wrong_relation":
        wrong_relation = relation.get(
            "wrong_relation",
            "Wrong relation: the peer gives a plausible but incorrect relation and answer.",
        )
        return [
            {
                "source": wrong["compact_agent_id"],
                "surface": "answer_plus_wrong_relation",
                "text": f"I think the final answer is {wrong['answer']}. {wrong_relation}",
                "answer": str(wrong["answer"]),
                "expected_correct": "false",
            }
        ]
    if condition == "wrong_plausible_irrelevant":
        return [
            {
                "source": wrong["compact_agent_id"],
                "surface": "plausible_irrelevant",
                "text": relation.get(
                    "irrelevant",
                    "Plausible but irrelevant note: focus on a nearby fact that does not decide the answer.",
                ),
                "answer": "",
                "expected_correct": "false",
            }
        ]
    if condition == "wrong_majority":
        return [
            {
                "source": f"Peer{idx}",
                "surface": "answer_only_majority",
                "text": f"My final answer is {wrong['answer']}.",
                "answer": str(wrong["answer"]),
                "expected_correct": "false",
            }
            for idx in range(1, 4)
        ]
    if condition == "authority_wrong":
        return [
            {
                "source": "SeniorVerifier",
                "surface": "authority_answer_only",
                "text": (
                    "I am the senior verifier for this round and I am confident "
                    f"the final answer is {wrong['answer']}."
                ),
                "answer": str(wrong["answer"]),
                "expected_correct": "false",
            }
        ]
    if condition == "wrong_rationale":
        return [
            {
                "source": wrong["compact_agent_id"],
                "surface": "full_rationale",
                "text": wrong["response"],
                "answer": str(wrong["answer"]),
                "expected_correct": "false",
            }
        ]
    if condition == "correct_rationale":
        return [
            {
                "source": correct["compact_agent_id"],
                "surface": "full_rationale",
                "text": correct["response"],
                "answer": str(correct["answer"]),
                "expected_correct": "true",
            }
        ]
    raise ValueError(f"Unknown peer condition: {condition}")


def auto_evidence_source_peer(case: Dict[str, Any], condition: str) -> Tuple[Dict[str, Any], str]:
    if condition in {"correct_auto_evidence", "correct_redacted_evidence"}:
        return case["correct_peer"], "true"
    if condition in {"wrong_auto_evidence", "wrong_redacted_evidence"}:
        return case["wrong_peer"], "false"
    raise ValueError(f"Unknown auto-evidence condition: {condition}")


def auto_evidence_surface(condition: str) -> str:
    if condition in ANSWER_REDACTED_EVIDENCE_CONDITIONS:
        return "answer_redacted_evidence"
    return "auto_evidence"


def auto_evidence_prompt(question: str, peer_response: str, peer_answer: Any, surface: str) -> str:
    if surface == "answer_redacted_evidence":
        return f"""Compress one peer solution into a short evidence note for another solver.

Problem:
{question}

Peer solution with exact parsed-final-answer mentions replaced by [REDACTED_FINAL]:
{peer_response.strip()}

Parsed peer final answer, shown only so you can avoid reconstructing it:
{peer_answer}

Write exactly one line in this format:
Evidence: <one sentence under 45 words containing the key relation, constraint, or reusable intermediate calculation. Do not include [REDACTED_FINAL], do not state or reconstruct the final answer, and if a final-result slot is needed write [blank].>"""

    return f"""Compress one peer solution into a short evidence note for another solver.

Problem:
{question}

Peer solution:
{peer_response.strip()}

Parsed peer final answer, shown only so you can avoid repeating it:
{peer_answer}

Write exactly one line in this format:
Evidence: <one sentence under 45 words containing the key relation, constraint, or calculation the peer used. Do not state "the final answer is ..." and do not mention correctness, confidence, or the peer.>"""


def parse_auto_evidence_output(output: str) -> Tuple[str, str]:
    text = output.strip()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^(?:Evidence|Key evidence|Key relation|Relation)\s*:\s*(.+)$", line, re.I)
        if match:
            return match.group(1).strip().strip('"'), "evidence_field"
    first = next((line.strip() for line in text.splitlines() if line.strip()), text)
    first = re.sub(r"^(?:Evidence|Key evidence|Key relation|Relation)\s*:\s*", "", first, flags=re.I)
    return first.strip().strip('"'), "first_nonempty_line"


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


def summarize(records: List[Dict[str, Any]], run_id: str, peer_warning: str, response_mode: str) -> Dict[str, Any]:
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
    if any(row["condition"] in AUTO_EVIDENCE_CONDITIONS for row in records):
        caveats.append(
            "Auto-evidence surfaces are model-compressed from peer rationales; the extraction itself may omit, distort, or leak decisive answer information."
        )
    if any(row["condition"] in ANSWER_REDACTED_EVIDENCE_CONDITIONS for row in records):
        caveats.append(
            "Answer-redacted evidence first removes exact parsed-final-answer mentions from the source rationale, but related intermediate numbers can still leak or reconstruct the answer."
        )
    return {
        "run_id": run_id,
        "method": METHOD,
        "schema_version": SCHEMA_VERSION,
        "peer_warning": peer_warning,
        "response_mode": response_mode,
        "cases": cases,
        "num_cases": len(cases),
        "num_records": len(records),
        "conditions": condition_summary,
        "caveats": caveats,
    }


def write_readme(out_dir: Path, summary: Dict[str, Any], command: str, started_at: str, ended_at: str) -> None:
    lines = [
        "# Peer Exposure Mini-Probe",
        "",
        "## What We Tried",
        "",
        "A small controlled peer-exposure probe over saved DAR GSM8K disagreement cases.",
        "Each case first gets a no-peer answer, then the same model revises after",
        "seeing controlled peer surfaces derived from real DAR round-0 peers.",
        "",
        "## Command",
        "",
        "```bash",
        command,
        "```",
        "",
        "## What Happened",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Cases: `{summary['num_cases']}`",
        f"- Records: `{summary['num_records']}`",
        f"- Started: `{started_at}`",
        f"- Ended: `{ended_at}`",
        "",
        "| Condition | Records | Accuracy | Right->Wrong | Wrong->Right | Stable Right | Stable Wrong | Peer Adoption |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition, stats in summary["conditions"].items():
        lines.append(
            f"| `{condition}` | {stats.get('records', 0)} | "
            f"{stats.get('accuracy', 0):.3f} | {stats.get('right_to_wrong', 0)} | "
            f"{stats.get('wrong_to_right', 0)} | {stats.get('stable_right', 0)} | "
            f"{stats.get('stable_wrong', 0)} | {stats.get('peer_answer_adoption_rate', 0):.3f} |"
        )
    lines += [
        "",
        "## Caveats",
        "",
    ]
    for caveat in summary["caveats"]:
        lines.append(f"- {caveat}")
    lines.append("")
    out_dir.joinpath("README.md").write_text("\n".join(lines), encoding="utf-8")


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

    summary = summarize(records, args.run_id, args.peer_warning, args.response_mode)
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
    write_readme(out_dir, summary, command, started_at, ended_at)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source-format", choices=["dar_gsm8k", "madmm_math"], default="dar_gsm8k")
    parser.add_argument("--history-jsonl", default="")
    parser.add_argument("--gsm8k-jsonl", default="")
    parser.add_argument("--madmm-trace-jsonl", default="")
    parser.add_argument("--madmm-debate-log-json", default="")
    parser.add_argument("--madmm-method", default="mad_naive")
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
    if not args.dry_run and (not args.base_url or not args.model):
        parser.error("--base-url and --model are required unless --dry-run is set")
    summary = run(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
