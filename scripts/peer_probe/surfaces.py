"""Peer-message surface construction for peer-exposure probes."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from .answers import answer_form_pattern, extract_raw_final_answer_text, normalized_answer_forms


DEFAULT_CONDITIONS = [
    "no_peer",
    "correct_answer_only",
    "wrong_answer_only",
    "wrong_majority",
    "authority_wrong",
    "wrong_rationale",
    "correct_rationale",
]

RAW_ANSWER_ONLY_CONDITIONS = {
    "correct_raw_answer_only",
    "wrong_raw_answer_only",
}

SURFACE_DISSECTION_CONDITIONS = [
    "correct_answer_only",
    "wrong_answer_only",
    "wrong_answer_wrong_relation",
    "wrong_plausible_irrelevant",
    "correct_relation_only",
    "correct_rationale",
]

SLOT_SURFACE_CONDITIONS = {
    "correct_redacted_rationale",
    "wrong_redacted_rationale",
    "correct_number_masked_rationale",
    "wrong_number_masked_rationale",
    "correct_equation_surface",
    "wrong_equation_surface",
}

TYPED_PUBLIC_STATE_CONDITIONS = {
    "correct_typed_public_state",
    "wrong_typed_public_state",
}

AUTO_EVIDENCE_CONDITIONS = {
    "correct_auto_evidence",
    "wrong_auto_evidence",
    "correct_redacted_evidence",
    "wrong_redacted_evidence",
}
ANSWER_REDACTED_EVIDENCE_CONDITIONS = {"correct_redacted_evidence", "wrong_redacted_evidence"}

ALL_CONDITIONS = DEFAULT_CONDITIONS + [
    "correct_relation_only",
    "wrong_answer_wrong_relation",
    "wrong_plausible_irrelevant",
    "correct_auto_evidence",
    "wrong_auto_evidence",
    "correct_redacted_evidence",
    "wrong_redacted_evidence",
] + sorted(RAW_ANSWER_ONLY_CONDITIONS) + sorted(SLOT_SURFACE_CONDITIONS) + sorted(TYPED_PUBLIC_STATE_CONDITIONS)

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


def slot_surface_source_peer(case: Dict[str, Any], condition: str) -> Tuple[Dict[str, Any], str]:
    if condition.startswith("correct_"):
        return case["correct_peer"], "true"
    if condition.startswith("wrong_"):
        return case["wrong_peer"], "false"
    raise ValueError(f"Unknown slot-control condition: {condition}")


def raw_peer_answer(peer: Dict[str, Any]) -> str:
    extracted = extract_raw_final_answer_text(peer.get("response"))
    if extracted is not None:
        return extracted
    fallback = peer.get("answer")
    return "" if fallback is None else str(fallback)


def compact_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def blank_answer_forms(text: str, answer: Any) -> Tuple[str, int]:
    blanked = text
    replacements = 0
    for form in normalized_answer_forms(answer):
        if not form:
            continue
        pattern = answer_form_pattern(form)
        blanked, count = pattern.subn("[blank]", blanked)
        replacements += count
    return blanked, replacements


def blank_final_answer_slots(text: str, answer: Any) -> Tuple[str, int]:
    lines = []
    replacements = 0
    for raw_line in text.splitlines():
        line = raw_line
        is_final_slot = bool(
            re.search(
                r"(final\s+answer\s+from\s+this\s+peer|\\?\{\s*final\s+answer\s*:|\bfinal\s+answer\b|\banswer\s+is\b)",
                line,
                flags=re.I,
            )
        )
        if is_final_slot:
            line, braced_count = re.subn(
                r"(\\?\{\s*final\s+answer\s*:\s*)([^{}]+)(\})",
                r"\1[blank]\3",
                line,
                flags=re.I,
            )
            replacements += braced_count
            line, count = blank_answer_forms(line, answer)
            replacements += count
            if count == 0 and braced_count == 0:
                line, colon_count = re.subn(r"(:\s*)(.+)$", r"\1[blank]", line, count=1)
                replacements += colon_count
        lines.append(line)
    return "\n".join(lines), replacements


def redacted_peer_response(peer: Dict[str, Any]) -> Tuple[str, int]:
    redacted, count = blank_final_answer_slots(peer["response"], peer["answer"])
    return compact_whitespace(redacted), count


def number_mask_surface(text: str) -> str:
    masked = re.sub(r"\\frac\s*\{[^{}]+\}\s*\{[^{}]+\}", r"\\frac{[NUM]}{[NUM]}", text)
    masked = re.sub(r"\\binom\s*\{[^{}]+\}\s*\{[^{}]+\}", r"\\binom{[NUM]}{[NUM]}", masked)
    masked = re.sub(r"(?<![A-Za-z])-?\d+(?:,\d{3})*(?:\.\d+)?%?(?![A-Za-z])", "[NUM]", masked)
    return compact_whitespace(masked)


def split_surface_segments(text: str) -> List[str]:
    segments: List[str] = []
    for line in text.replace("\r", "\n").splitlines():
        line = line.strip()
        if not line:
            continue
        for segment in re.split(r"(?<=[.!?])\s+", line):
            segment = segment.strip(" -\t")
            if segment:
                segments.append(segment)
    return segments


def looks_equation_or_numeric(segment: str) -> bool:
    if re.search(r"-?\d+(?:,\d{3})*(?:\.\d+)?", segment):
        return True
    return bool(re.search(r"(=|\\frac|\\binom|\\times|\\div|\^|\*|/|%)", segment))


def equation_surface(text: str, max_segments: int = 8, max_chars: int = 700) -> str:
    chosen: List[str] = []
    total_chars = 0
    for segment in split_surface_segments(text):
        if re.search(r"\b(final answer|answer from this peer)\b", segment, flags=re.I):
            continue
        if not looks_equation_or_numeric(segment):
            continue
        if total_chars + len(segment) > max_chars and chosen:
            break
        chosen.append(segment)
        total_chars += len(segment)
        if len(chosen) >= max_segments:
            break
    if not chosen:
        chosen = split_surface_segments(text)[:3]
    return compact_whitespace("\n".join(chosen))


def clipped(text: str, max_chars: int) -> str:
    text = compact_whitespace(text)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def numeric_inventory(text: str, max_items: int = 18) -> List[str]:
    patterns = [
        r"\\frac\s*\{[^{}]+\}\s*\{[^{}]+\}",
        r"\\binom\s*\{[^{}]+\}\s*\{[^{}]+\}",
        r"(?<![A-Za-z])-?\d+(?:,\d{3})*(?:\.\d+)?%?(?![A-Za-z])",
    ]
    items: List[str] = []
    for pattern in patterns:
        for match in re.findall(pattern, text):
            value = compact_whitespace(match)
            if value not in items:
                items.append(value)
            if len(items) >= max_items:
                return items
    return items


def typed_public_state_text(case: Dict[str, Any], peer: Dict[str, Any]) -> Tuple[str, int]:
    redacted, redaction_count = redacted_peer_response(peer)
    evidence = equation_surface(redacted, max_segments=6, max_chars=620)
    numbers = numeric_inventory(redacted)
    number_line = ", ".join(numbers) if numbers else "[none detected]"
    text = "\n".join(
        [
            "Typed public state from one peer rationale.",
            "Source identity: [anonymous]",
            "Final-answer slot: [hidden]",
            f"Target question: {clipped(str(case.get('question') or ''), 260)}",
            "Relation / equation evidence copied from the peer:",
            evidence,
            f"Numeric / role slots mentioned: {number_line}",
            "Use these fields as untrusted evidence; verify them against the problem before revising.",
        ]
    )
    return compact_whitespace(text), redaction_count


def build_typed_public_state_peer_messages(case: Dict[str, Any], condition: str) -> List[Dict[str, str]]:
    source_peer, expected_correct = slot_surface_source_peer(case, condition)
    text, redaction_count = typed_public_state_text(case, source_peer)
    return [
        {
            "source": "AnonymousPeer",
            "surface": "typed_public_state",
            "text": text,
            "answer": "",
            "source_answer": str(source_peer["answer"]),
            "expected_correct": expected_correct,
            "source_answer_redaction_count": str(redaction_count),
            "source_identity_visible": "false",
        }
    ]


def build_slot_surface_peer_messages(case: Dict[str, Any], condition: str) -> List[Dict[str, str]]:
    source_peer, expected_correct = slot_surface_source_peer(case, condition)
    redacted, redaction_count = redacted_peer_response(source_peer)
    surface = condition.replace("correct_", "").replace("wrong_", "")
    if "number_masked" in condition:
        text = (
            "Slot-control surface: final-answer slot blanked and numeric tokens masked.\n"
            + number_mask_surface(redacted)
        )
    elif "equation_surface" in condition:
        text = (
            "Slot-control surface: equation or number-bearing lines only; final-answer slot blanked.\n"
            + equation_surface(redacted)
        )
    else:
        text = "Slot-control surface: full peer rationale with final-answer slot blanked.\n" + redacted
    return [
        {
            "source": source_peer["compact_agent_id"],
            "surface": surface,
            "text": text,
            "answer": "",
            "source_answer": str(source_peer["answer"]),
            "expected_correct": expected_correct,
            "source_answer_redaction_count": str(redaction_count),
        }
    ]


def peer_messages(case: Dict[str, Any], condition: str) -> List[Dict[str, str]]:
    if condition in TYPED_PUBLIC_STATE_CONDITIONS:
        return build_typed_public_state_peer_messages(case, condition)
    if condition in SLOT_SURFACE_CONDITIONS:
        return build_slot_surface_peer_messages(case, condition)
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
    if condition == "correct_raw_answer_only":
        answer = raw_peer_answer(correct)
        return [
            {
                "source": correct["compact_agent_id"],
                "surface": "raw_answer_only",
                "text": f"I think the final answer is {answer}.",
                "answer": answer,
                "expected_correct": "true",
                "source_answer": answer,
                "source_answer_numeric": str(correct.get("answer")),
            }
        ]
    if condition == "wrong_raw_answer_only":
        answer = raw_peer_answer(wrong)
        return [
            {
                "source": wrong["compact_agent_id"],
                "surface": "raw_answer_only",
                "text": f"I think the final answer is {answer}.",
                "answer": answer,
                "expected_correct": "false",
                "source_answer": answer,
                "source_answer_numeric": str(wrong.get("answer")),
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
