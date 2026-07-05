#!/usr/bin/env python3
"""Run Candidate-Pool Adaptive Consensus with a DCAC minority branch.

CPAC first diagnoses the observed candidate pool. DCAC is only used for the
minority-bearing state, where one answer has majority support and one answer is
a live challenger. A challenger may overturn the majority only when certificate
reviewers produce enough admissible answer-delta checks.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from run_basic_mad import (
    ROLE_NAMES,
    extract_boxed_answer,
    is_correct,
    load_rows,
    majority_vote,
    normalize_numeric,
    prompt_from_messages,
    resolve_inside,
)
from run_consensus_quarantine import (
    CandidateCard,
    build_candidate_cards,
    duplicate_reasoning_score,
    generate_outputs,
    generate_plain_texts,
    independent_prompt,
    reshape,
    transition_label,
)
from run_mad_mm import cot_prompt, prepare_question


CLAIM_FORMAT = (
    "\n\nReply with exactly one XML tag named claim. "
    "Put only the directional defect claim inside the tag. "
    "If the challenger has no concrete condition-level objection, put exactly "
    "NO_ADMISSIBLE_CLAIM inside the tag."
)

CERTIFICATE_FORMAT = (
    "\n\nReply with exactly one XML tag named certificate containing these child tags: "
    "<condition>, <majority>, <challenger>, <calculation>, and <decision>. "
    "The <majority> and <challenger> tags must be one of pass, fail, unknown. "
    "The <decision> tag must be flip or keep. Use keep unless the calculation explicitly "
    "supports the challenger answer and contradicts the majority answer."
)


@dataclass(frozen=True)
class CPACDecision:
    pool_state: str
    action: str
    reason: str
    majority_answer: str | None
    majority_count: int
    unique_answer_count: int
    support_vector: tuple[int, ...]
    duplicate_reasoning_score: float
    representation_risks: tuple[str, ...]


@dataclass(frozen=True)
class ParsedCertificate:
    condition: str
    majority_status: str
    challenger_status: str
    calculation: str
    decision: str
    admissible_flip: bool


_DCAC_BLOCKING_REPRESENTATION_RISKS = frozenset(
    {
        "base_notation",
        "matrix_or_vector",
    }
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default=os.environ.get("ACR_WORK_DIR", os.getcwd()))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--split", default="test")
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--gpu-id", default=os.environ.get("CUDA_VISIBLE_DEVICES", "0"))
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--reviewers", type=int, default=3)
    parser.add_argument("--overlap-threshold", type=float, default=0.72)
    parser.add_argument(
        "--no-majority-action",
        choices=("listwise", "keep"),
        default="listwise",
        help="How CPAC handles no-majority candidate pools.",
    )
    parser.add_argument(
        "--initial-prompt-style",
        choices=("cpac", "standard-mad"),
        default="cpac",
        help="Prompt family for newly sampled initial answers.",
    )
    parser.add_argument("--dcac-min-flip-certificates", type=int, default=2)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--claim-temperature", type=float, default=0.2)
    parser.add_argument("--certificate-temperature", type=float, default=0.2)
    parser.add_argument("--listwise-temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--claim-max-tokens", type=int, default=512)
    parser.add_argument("--certificate-max-tokens", type=int, default=1024)
    parser.add_argument("--listwise-max-tokens", type=int, default=1536)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.85)
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    parser.add_argument(
        "--disable-tqdm",
        action="store_true",
        help="Disable vLLM progress bars; useful for remote nohup/CI runs.",
    )
    return parser.parse_args()


def detect_representation_risks(cards: list[CandidateCard]) -> tuple[str, ...]:
    risks: set[str] = set()
    for card in cards:
        text = " ".join(str(value or "") for value in (card.parsed_answer, card.normalized_answer))
        if re.search(r"(_\{?\d+\}?|base[-\s]?\d+)", text, flags=re.IGNORECASE):
            risks.add("base_notation")
        if re.search(r"(\\begin\{p?matrix\}|Matrix\(|\\left\[|\\right\])", text):
            risks.add("matrix_or_vector")
        if re.search(r"(\\pi|\bpi\b)", text):
            risks.add("symbolic_constant")
        if re.search(r"(\\(?:sin|cos|tan|cot|sec|csc|log|ln)\b|\b(?:sin|cos|tan|cot|sec|csc|log|ln)\()", text):
            risks.add("symbolic_function")
        if re.search(r"(\\sqrt|sqrt\(|\\frac|/)", text):
            risks.add("symbolic_expression")
        if re.search(r"(\([^)]*,[^)]*\)|\{[^}]*,[^}]*\}|\\cup|\\cap|interval)", text, flags=re.IGNORECASE):
            risks.add("compound_answer")
    return tuple(sorted(risks))


def analyze_candidate_pool(
    agent_outputs: list[dict[str, Any]],
    cards: list[CandidateCard],
    *,
    no_majority_action: str,
    overlap_threshold: float,
) -> CPACDecision:
    normalized_answers = [card.normalized_answer for card in cards for _ in card.source_indices]
    counts = Counter(answer for answer in normalized_answers if answer is not None)
    if not counts:
        return CPACDecision(
            pool_state="no_parseable_answer",
            action="keep_initial",
            reason="no_parseable_initial_answer",
            majority_answer=None,
            majority_count=0,
            unique_answer_count=0,
            support_vector=(),
            duplicate_reasoning_score=0.0,
            representation_risks=(),
        )

    majority_answer, tied = majority_vote([output.get("parsed_answer") for output in agent_outputs])
    majority_count = counts.get(majority_answer, 0) if majority_answer is not None else 0
    majority_outputs = [
        str(agent_outputs[idx].get("output") or "")
        for card in cards
        if card.normalized_answer == majority_answer
        for idx in card.source_indices
    ]
    overlap = duplicate_reasoning_score(majority_outputs)
    support_vector = tuple(sorted(counts.values(), reverse=True))
    unique_count = len(counts)
    risks = detect_representation_risks(cards)
    parseable_count = sum(counts.values())

    if unique_count == 1:
        reason = "single_candidate"
        if risks:
            reason = "single_candidate_with_representation_risk"
        elif overlap >= overlap_threshold and parseable_count > 1:
            reason = "single_candidate_high_reasoning_overlap"
        return CPACDecision(
            pool_state="collapse",
            action="keep_initial",
            reason=reason,
            majority_answer=majority_answer,
            majority_count=majority_count,
            unique_answer_count=unique_count,
            support_vector=support_vector,
            duplicate_reasoning_score=overlap,
            representation_risks=risks,
        )

    if tied or majority_count <= parseable_count / 2:
        action = "listwise_discriminant" if no_majority_action == "listwise" else "keep_initial"
        return CPACDecision(
            pool_state="no_majority_conflict",
            action=action,
            reason="no_strict_majority",
            majority_answer=majority_answer,
            majority_count=majority_count,
            unique_answer_count=unique_count,
            support_vector=support_vector,
            duplicate_reasoning_score=overlap,
            representation_risks=risks,
        )

    if unique_count == 2:
        return CPACDecision(
            pool_state="minority_bearing",
            action="dcac",
            reason="strict_majority_with_single_challenger",
            majority_answer=majority_answer,
            majority_count=majority_count,
            unique_answer_count=unique_count,
            support_vector=support_vector,
            duplicate_reasoning_score=overlap,
            representation_risks=risks,
        )

    return CPACDecision(
        pool_state="plurality_conflict",
        action="listwise_discriminant" if no_majority_action == "listwise" else "keep_initial",
        reason="strict_plurality_with_multiple_challengers",
        majority_answer=majority_answer,
        majority_count=majority_count,
        unique_answer_count=unique_count,
        support_vector=support_vector,
        duplicate_reasoning_score=overlap,
        representation_risks=risks,
    )


def dcac_claim_prompt(question: str, majority: CandidateCard, challenger: CandidateCard) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You write directional admissibility claims for a math reasoning audit. "
                "The claim must support the challenger answer and identify a concrete condition "
                "that the majority answer appears to violate. Do not vote by style or confidence."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                "Majority candidate answer:\n"
                f"{majority.parsed_answer}\n\n"
                "Majority candidate reasoning:\n"
                f"{majority.representative_output}\n\n"
                "Challenger candidate answer:\n"
                f"{challenger.parsed_answer}\n\n"
                "Challenger candidate reasoning:\n"
                f"{challenger.representative_output}\n\n"
                "Write the strongest answer-delta claim for why the challenger should remain admissible. "
                "A valid claim must point to a checkable condition, constraint, representation issue, "
                "or calculation split between the two answers."
                f"{CLAIM_FORMAT}"
            ),
        },
    ]


def extract_claim(text: str) -> str:
    match = re.search(r"<claim>(.*?)</claim>", text, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return text.strip()
    return match.group(1).strip()


def is_directional_claim_text(text: str) -> bool:
    compact = re.sub(r"[^a-z0-9]+", "", text.lower())
    if compact in {"", "noadmissibleclaim", "none", "noconcreteclaim", "novalidclaim"}:
        return False
    if "noadmissibleclaim" in compact or "novalidclaim" in compact:
        return False
    if compact in {"yourdirectionaldefectclaim", "directionaldefectclaim"}:
        return False
    lower = text.lower()
    consensus_support = (
        "majority is correct",
        "consensus is correct",
        "challenger is wrong",
        "alternative is wrong",
        "keep the majority",
    )
    if any(phrase in lower for phrase in consensus_support):
        return False
    return len(re.findall(r"[A-Za-z0-9]+", text)) >= 6


def dcac_certificate_prompt(
    question: str,
    reviewer_index: int,
    majority: CandidateCard,
    challenger: CandidateCard,
    claim: str,
) -> list[dict[str, str]]:
    role = ROLE_NAMES[reviewer_index % len(ROLE_NAMES)]
    return [
        {
            "role": "system",
            "content": (
                f"You are certificate reviewer {reviewer_index + 1}, a {role}. "
                "You decide whether a minority challenger is admissible, not whether it sounds persuasive. "
                "A flip is allowed only if the majority fails a checkable condition and the challenger "
                "passes the same condition. Otherwise keep the majority."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                "Majority candidate answer:\n"
                f"{majority.parsed_answer}\n\n"
                "Majority candidate reasoning:\n"
                f"{majority.representative_output}\n\n"
                "Challenger candidate answer:\n"
                f"{challenger.parsed_answer}\n\n"
                "Challenger candidate reasoning:\n"
                f"{challenger.representative_output}\n\n"
                "Directional challenger claim:\n"
                f"{claim}\n\n"
                "Fill the certificate using one minimal discriminant condition induced by the answer delta. "
                "If the condition cannot be checked, use unknown and keep."
                f"{CERTIFICATE_FORMAT}"
            ),
        },
    ]


def _extract_tag(text: str, tag: str) -> str:
    match = re.search(fr"<{tag}>(.*?)</{tag}>", text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _normalize_status(value: str) -> str:
    compact = re.sub(r"[^a-z]+", "", value.lower())
    if compact.startswith("pass"):
        return "pass"
    if compact.startswith("fail"):
        return "fail"
    return "unknown"


def _normalize_decision(value: str) -> str:
    compact = re.sub(r"[^a-z]+", "", value.lower())
    return "flip" if compact.startswith("flip") else "keep"


def _compact_text(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "").lower())


def _answer_surface_forms(card: CandidateCard) -> tuple[str, ...]:
    forms: set[str] = set()
    for value in (card.parsed_answer, card.normalized_answer):
        if not value:
            continue
        raw = str(value).strip()
        if raw:
            forms.add(raw)
        boxed = extract_boxed_answer(raw)
        if boxed:
            forms.add(boxed.strip())
        if raw.startswith("expr:") or raw.startswith("str:"):
            forms.add(raw.split(":", 1)[1])

    expanded: set[str] = set()
    for form in forms:
        cleaned = form.strip()
        if not cleaned:
            continue
        expanded.add(cleaned)
        expanded.add(cleaned.strip("$"))
        expanded.add(cleaned.replace(",", ""))
        expanded.add(cleaned.replace("\\left", "").replace("\\right", ""))
        expanded.add(re.sub(r"\s+", "", cleaned))
        expanded.add(re.sub(r"[{}\\\s,$]", "", cleaned.lower()))
    return tuple(sorted(form for form in expanded if form))


def _mentions_answer(text: str, card: CandidateCard) -> bool:
    if not text:
        return False
    compact = _compact_text(text)
    for form in _answer_surface_forms(card):
        compact_form = _compact_text(form)
        if not compact_form:
            continue
        if len(compact_form) == 1 and compact_form.isdigit():
            if re.search(rf"(?<!\d){re.escape(compact_form)}(?!\d)", compact):
                return True
            continue
        if compact_form in compact:
            return True
    normalized_text = normalize_numeric(text)
    return normalized_text is not None and normalized_text == card.normalized_answer


def _has_label_text_contradiction(certificate: ParsedCertificate) -> bool:
    text = f"{certificate.condition}\n{certificate.calculation}".lower()
    majority_pass_text = re.search(
        r"majority[^.\n]{0,120}\b(satisf(?:y|ies|ied)|pass(?:es|ed)?|is correct)\b",
        text,
    )
    challenger_fail_text = re.search(
        r"challenger[^.\n]{0,120}\b(does not|doesn't|fail(?:s|ed)?|not satisf(?:y|ies)|violat(?:es|ed)?)\b",
        text,
    )
    return bool(
        (certificate.majority_status == "fail" and majority_pass_text)
        or (certificate.challenger_status == "pass" and challenger_fail_text)
    )


def _simple_numeric_value(text: str) -> float | None:
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def _satisfies_inequality(value: float, operator: str, bound: float) -> bool:
    if operator == ">":
        return value > bound
    if operator == "<":
        return value < bound
    if operator == ">=":
        return value >= bound
    if operator == "<=":
        return value <= bound
    return False


def _has_simple_inequality_contradiction(certificate: ParsedCertificate) -> bool:
    condition = certificate.condition.lower()
    match = re.search(r"\b([a-z])\s*(>=|<=|>|<)\s*(-?\d+(?:\.\d+)?)\b", condition)
    if not match:
        return False
    variable, operator, bound_text = match.groups()
    bound = _simple_numeric_value(bound_text)
    if bound is None:
        return False
    text = f"{certificate.condition}\n{certificate.calculation}".lower()
    for label, status in (("majority", certificate.majority_status), ("challenger", certificate.challenger_status)):
        assignment = re.search(
            rf"{label}[^.\n]{{0,120}}\b{re.escape(variable)}\s*=\s*(-?\d+(?:\.\d+)?)\b",
            text,
        )
        if not assignment:
            continue
        value = _simple_numeric_value(assignment.group(1))
        if value is None:
            continue
        satisfies = _satisfies_inequality(value, operator, bound)
        if status == "fail" and satisfies:
            return True
        if status == "pass" and not satisfies:
            return True
    return False


def _has_negated_challenger_text_answer(certificate: ParsedCertificate, challenger: CandidateCard) -> bool:
    if not challenger.normalized_answer or not challenger.normalized_answer.startswith("str:"):
        return False
    candidate = re.sub(r"[^a-z]+", "", challenger.normalized_answer.split(":", 1)[1].lower())
    if len(candidate) < 4:
        return False
    text = f"{certificate.condition}\n{certificate.calculation}".lower()
    if re.search(rf"\bnot\b[^.\n]{{0,120}}\b{re.escape(candidate)}\b", text):
        return True
    if re.search(rf"\b{re.escape(candidate)}\b[^.\n]{{0,120}}\bnot\b", text):
        return True
    return False


def _latex_numeric_text(text: str) -> str:
    value = text.replace(",", "")
    value = value.replace("\\times", "*").replace("\\cdot", "*").replace("×", "*")
    value = value.replace("\\left", "").replace("\\right", "")
    value = value.replace("{,}", "")
    frac_pattern = re.compile(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}")
    while True:
        next_value = frac_pattern.sub(r"(\1/\2)", value)
        if next_value == value:
            break
        value = next_value
    return value


def _eval_arithmetic_expr(expr: str) -> float | None:
    compact = expr.strip()
    if not compact or not re.fullmatch(r"[0-9+\-*/().\s]+", compact):
        return None
    try:
        tree = ast.parse(compact, mode="eval")
    except SyntaxError:
        return None

    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -visit(node.operand)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            return visit(node.operand)
        if isinstance(node, ast.BinOp):
            left = visit(node.left)
            right = visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError
                return left / right
        raise ValueError

    try:
        return visit(tree)
    except Exception:
        return None


def _has_arithmetic_mismatch(text: str) -> bool:
    value = _latex_numeric_text(text)
    expression = r"[-+]?\d[\d\s+\-*/().]*"
    for match in re.finditer(fr"({expression})\s*=\s*({expression})", value):
        if match.start() > 0 and value[match.start() - 1] in "^_":
            continue
        left = _eval_arithmetic_expr(match.group(1))
        right = _eval_arithmetic_expr(match.group(2))
        if left is None or right is None:
            continue
        if abs(left - right) > 1e-9:
            return True
    return False


def parse_dcac_certificate(text: str) -> ParsedCertificate:
    condition = _extract_tag(text, "condition")
    majority_status = _normalize_status(_extract_tag(text, "majority"))
    challenger_status = _normalize_status(_extract_tag(text, "challenger"))
    calculation = _extract_tag(text, "calculation")
    decision = _normalize_decision(_extract_tag(text, "decision"))
    admissible_flip = decision == "flip" and majority_status == "fail" and challenger_status == "pass"
    return ParsedCertificate(
        condition=condition,
        majority_status=majority_status,
        challenger_status=challenger_status,
        calculation=calculation,
        decision=decision,
        admissible_flip=admissible_flip,
    )


def dcac_certificate_rejection_reasons(
    certificate: ParsedCertificate,
    majority: CandidateCard,
    challenger: CandidateCard,
    representation_risks: tuple[str, ...] = (),
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not certificate.admissible_flip:
        reasons.append("certificate_tags_do_not_admit_flip")
    if not certificate.condition:
        reasons.append("missing_condition")
    if not certificate.calculation:
        reasons.append("missing_calculation")
    blocking_risks = sorted(set(representation_risks) & _DCAC_BLOCKING_REPRESENTATION_RISKS)
    for risk in blocking_risks:
        reasons.append(f"blocked_representation_risk:{risk}")
    combined = f"{certificate.condition}\n{certificate.calculation}"
    if certificate.admissible_flip and not _mentions_answer(combined, challenger):
        reasons.append("challenger_answer_not_supported_by_certificate_text")
    if _has_label_text_contradiction(certificate):
        reasons.append("label_text_contradiction")
    if _has_simple_inequality_contradiction(certificate):
        reasons.append("simple_inequality_contradiction")
    if _has_negated_challenger_text_answer(certificate, challenger):
        reasons.append("negated_challenger_text_answer")
    if _has_arithmetic_mismatch(certificate.calculation):
        reasons.append("arithmetic_mismatch_in_calculation")
    return tuple(reasons)


def is_guarded_dcac_flip(
    certificate: ParsedCertificate,
    majority: CandidateCard,
    challenger: CandidateCard,
    representation_risks: tuple[str, ...] = (),
) -> bool:
    return not dcac_certificate_rejection_reasons(certificate, majority, challenger, representation_risks)


def dcac_final_answer(
    majority: CandidateCard,
    challenger: CandidateCard,
    certificates: list[ParsedCertificate],
    min_flip_certificates: int,
    representation_risks: tuple[str, ...] = (),
) -> tuple[str | None, str, int, int]:
    required = min(max(1, min_flip_certificates), max(1, len(certificates)))
    flip_count = sum(
        1
        for certificate in certificates
        if is_guarded_dcac_flip(certificate, majority, challenger, representation_risks)
    )
    if certificates and flip_count >= required:
        return challenger.normalized_answer or challenger.parsed_answer, "flip", flip_count, required
    return majority.normalized_answer or majority.parsed_answer, "keep", flip_count, required


def listwise_discriminant_prompt(
    question: str,
    reviewer_index: int,
    cards: list[CandidateCard],
) -> list[dict[str, str]]:
    card_text = "\n\n".join(
        (
            f"Card {card.card_id}\n"
            f"Proposed answer: {card.parsed_answer}\n"
            f"Reasoning:\n{card.representative_output}"
        )
        for card in cards
    )
    role = ROLE_NAMES[reviewer_index % len(ROLE_NAMES)]
    return [
        {
            "role": "system",
            "content": (
                f"You are listwise discriminant reviewer {reviewer_index + 1}, a {role}. "
                "You are not told how many agents supported each card. Compare the candidate answers "
                "by checkable conditions, not by style or repetition."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                "Anonymous candidate cards:\n"
                f"{card_text}\n\n"
                "Re-solve only as needed. State the discriminant checks between the candidates, "
                "then choose the best final answer."
                "\n\nEnd with exactly one XML tag named answer. "
                "Put only the final answer between the opening and closing answer tags."
            ),
        },
    ]


def card_payload(card: CandidateCard) -> dict[str, Any]:
    return {
        "card_id": card.card_id,
        "parsed_answer": card.parsed_answer,
        "normalized_answer": card.normalized_answer,
        "supporter_count_hidden_from_prompt": card.supporter_count,
        "source_indices": list(card.source_indices),
        "representative_output": card.representative_output,
    }


def decision_payload(decision: CPACDecision) -> dict[str, Any]:
    return {
        "pool_state": decision.pool_state,
        "action": decision.action,
        "reason": decision.reason,
        "majority_answer": decision.majority_answer,
        "majority_count": decision.majority_count,
        "unique_answer_count": decision.unique_answer_count,
        "support_vector": list(decision.support_vector),
        "duplicate_reasoning_score": decision.duplicate_reasoning_score,
        "representation_risks": list(decision.representation_risks),
    }


def main() -> int:
    args = parse_args()
    if args.agents < 2:
        raise SystemExit("--agents must be >= 2")
    if args.reviewers < 1:
        raise SystemExit("--reviewers must be >= 1")
    if args.dcac_min_flip_certificates < 1:
        raise SystemExit("--dcac-min-flip-certificates must be >= 1")

    work_dir = Path(args.work_dir).expanduser().resolve()
    data_path = resolve_inside(
        work_dir / "data" / "benchmarks" / args.benchmark / args.split / "canonical.jsonl",
        work_dir,
        "benchmark path",
    )
    method_key = "cpac-dcac"
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-{method_key}",
        work_dir,
        "output dir",
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    from vllm import LLM, SamplingParams

    rows = load_rows(data_path, args.limit)
    questions = [prepare_question(str(row.get("question") or ""), args.benchmark) for row in rows]
    started_at = time.time()
    model_path = Path(args.model_path).expanduser().resolve()
    llm = LLM(
        model=str(model_path),
        trust_remote_code=True,
        dtype=args.dtype,
        max_model_len=args.max_model_len,
        gpu_memory_utilization=args.gpu_memory_utilization,
        tensor_parallel_size=1,
        seed=args.seed,
    )
    tokenizer = llm.get_tokenizer()

    initial_sampling = SamplingParams(
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        logprobs=1,
    )
    claim_sampling = SamplingParams(
        temperature=args.claim_temperature,
        top_p=args.top_p,
        max_tokens=args.claim_max_tokens,
    )
    certificate_sampling = SamplingParams(
        temperature=args.certificate_temperature,
        top_p=args.top_p,
        max_tokens=args.certificate_max_tokens,
    )
    listwise_sampling = SamplingParams(
        temperature=args.listwise_temperature,
        top_p=args.top_p,
        max_tokens=args.listwise_max_tokens,
        logprobs=1,
    )
    use_tqdm = not args.disable_tqdm

    initial_prompts = []
    for question in questions:
        for agent_idx in range(args.agents):
            if args.initial_prompt_style == "standard-mad":
                initial_prompts.append(prompt_from_messages(tokenizer, [{"role": "user", "content": cot_prompt(question)}]))
            else:
                initial_prompts.append(prompt_from_messages(tokenizer, independent_prompt(question, agent_idx)))
    initial_flat = generate_outputs(llm, initial_prompts, initial_sampling, args.batch_size, use_tqdm=use_tqdm)
    initial_by_row = reshape(initial_flat, len(rows), args.agents)

    cards_by_row = [build_candidate_cards(outputs) for outputs in initial_by_row]
    cpac_decisions = [
        analyze_candidate_pool(
            outputs,
            cards,
            no_majority_action=args.no_majority_action,
            overlap_threshold=args.overlap_threshold,
        )
        for outputs, cards in zip(initial_by_row, cards_by_row)
    ]

    claim_prompts: list[str] = []
    claim_owners: list[tuple[int, str]] = []
    for row_idx, (question, cards, decision) in enumerate(zip(questions, cards_by_row, cpac_decisions)):
        if decision.action != "dcac" or decision.majority_answer is None:
            continue
        majority = next((card for card in cards if card.normalized_answer == decision.majority_answer), None)
        if majority is None:
            continue
        for challenger in cards:
            if challenger.normalized_answer == decision.majority_answer:
                continue
            claim_prompts.append(prompt_from_messages(tokenizer, dcac_claim_prompt(question, majority, challenger)))
            claim_owners.append((row_idx, challenger.card_id))

    claim_texts = (
        generate_plain_texts(llm, claim_prompts, claim_sampling, args.batch_size, use_tqdm=use_tqdm)
        if claim_prompts
        else []
    )
    claims_by_row: list[list[dict[str, Any]]] = [[] for _ in rows]
    for (row_idx, challenger_card_id), claim_output in zip(claim_owners, claim_texts):
        parsed_claim = extract_claim(claim_output)
        claims_by_row[row_idx].append(
            {
                "challenger_card_id": challenger_card_id,
                "claim_output": claim_output,
                "parsed_claim": parsed_claim,
                "valid_directional_claim": is_directional_claim_text(parsed_claim),
            }
        )

    certificate_prompts: list[str] = []
    certificate_owners: list[tuple[int, str]] = []
    for row_idx, (question, cards, decision) in enumerate(zip(questions, cards_by_row, cpac_decisions)):
        if decision.action != "dcac" or decision.majority_answer is None:
            continue
        majority = next((card for card in cards if card.normalized_answer == decision.majority_answer), None)
        if majority is None:
            continue
        for claim in claims_by_row[row_idx]:
            if not claim["valid_directional_claim"]:
                continue
            challenger = next((card for card in cards if card.card_id == claim["challenger_card_id"]), None)
            if challenger is None:
                continue
            for reviewer_idx in range(args.reviewers):
                certificate_prompts.append(
                    prompt_from_messages(
                        tokenizer,
                        dcac_certificate_prompt(
                            question,
                            reviewer_idx,
                            majority,
                            challenger,
                            str(claim["parsed_claim"]),
                        ),
                    )
                )
                certificate_owners.append((row_idx, challenger.card_id))

    certificate_texts = (
        generate_plain_texts(llm, certificate_prompts, certificate_sampling, args.batch_size, use_tqdm=use_tqdm)
        if certificate_prompts
        else []
    )
    certificates_by_row: list[list[dict[str, Any]]] = [[] for _ in rows]
    for (row_idx, challenger_card_id), certificate_output in zip(certificate_owners, certificate_texts):
        parsed = parse_dcac_certificate(certificate_output)
        decision = cpac_decisions[row_idx]
        majority = next(
            (card for card in cards_by_row[row_idx] if card.normalized_answer == decision.majority_answer),
            None,
        )
        challenger = next((card for card in cards_by_row[row_idx] if card.card_id == challenger_card_id), None)
        guard_rejection_reasons = (
            dcac_certificate_rejection_reasons(parsed, majority, challenger, decision.representation_risks)
            if majority is not None and challenger is not None
            else ("missing_majority_or_challenger_card",)
        )
        certificates_by_row[row_idx].append(
            {
                "challenger_card_id": challenger_card_id,
                "certificate_output": certificate_output,
                "parsed_certificate": {
                    "condition": parsed.condition,
                    "majority_status": parsed.majority_status,
                    "challenger_status": parsed.challenger_status,
                    "calculation": parsed.calculation,
                    "decision": parsed.decision,
                    "admissible_flip": parsed.admissible_flip,
                    "guarded_admissible_flip": not guard_rejection_reasons,
                    "guard_rejection_reasons": list(guard_rejection_reasons),
                },
            }
        )

    listwise_prompts: list[str] = []
    listwise_owners: list[int] = []
    for row_idx, (question, cards, decision) in enumerate(zip(questions, cards_by_row, cpac_decisions)):
        if decision.action != "listwise_discriminant":
            continue
        for reviewer_idx in range(args.reviewers):
            listwise_prompts.append(prompt_from_messages(tokenizer, listwise_discriminant_prompt(question, reviewer_idx, cards)))
            listwise_owners.append(row_idx)

    listwise_flat = (
        generate_outputs(llm, listwise_prompts, listwise_sampling, args.batch_size, use_tqdm=use_tqdm)
        if listwise_prompts
        else []
    )
    listwise_by_row: list[list[dict[str, Any]]] = [[] for _ in rows]
    for row_idx, output in zip(listwise_owners, listwise_flat):
        listwise_by_row[row_idx].append(output)

    records_path = output_dir / "records.jsonl"
    summary_counts: dict[str, int] = {
        "total": len(rows),
        "initial_majority_correct": 0,
        "final_correct": 0,
        "final_parse_fail": 0,
        "final_majority_ties": 0,
        "answer_changed": 0,
        "dcac_cases": 0,
        "valid_directional_claims": 0,
        "dcac_certificate_prompts": len(certificate_prompts),
        "dcac_flips": 0,
        "dcac_guard_rejected_certificates": 0,
        "dcac_guard_blocked_flips": 0,
        "listwise_cases": 0,
        "representation_risk_cases": 0,
        "MaC_to_C": 0,
        "MaC_to_W": 0,
        "MaW_to_C": 0,
        "MaW_to_W": 0,
    }
    pool_state_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()

    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for idx, row in enumerate(rows):
            gold = row.get("answer")
            initial_answers = [output.get("parsed_answer") for output in initial_by_row[idx]]
            initial_majority, initial_tie = majority_vote(initial_answers)
            decision = cpac_decisions[idx]
            pool_state_counts[decision.pool_state] += 1
            action_counts[decision.action] += 1
            final_answer = initial_majority
            final_tie = initial_tie
            branch_result: dict[str, Any] = {"decision": "keep_initial"}

            if decision.action == "dcac" and decision.majority_answer is not None:
                summary_counts["dcac_cases"] += 1
                majority = next((card for card in cards_by_row[idx] if card.normalized_answer == decision.majority_answer), None)
                valid_claims = [claim for claim in claims_by_row[idx] if claim["valid_directional_claim"]]
                summary_counts["valid_directional_claims"] += len(valid_claims)
                if majority is not None and valid_claims:
                    active_claim = valid_claims[0]
                    challenger = next(
                        (card for card in cards_by_row[idx] if card.card_id == active_claim["challenger_card_id"]),
                        None,
                    )
                    if challenger is not None:
                        parsed_certs = [
                            parse_dcac_certificate(item["certificate_output"])
                            for item in certificates_by_row[idx]
                            if item["challenger_card_id"] == challenger.card_id
                        ]
                        raw_flip_count = sum(1 for certificate in parsed_certs if certificate.admissible_flip)
                        final_answer, dcac_decision, flip_count, required = dcac_final_answer(
                            majority,
                            challenger,
                            parsed_certs,
                            args.dcac_min_flip_certificates,
                            decision.representation_risks,
                        )
                        guard_rejected = [
                            reason
                            for certificate in parsed_certs
                            for reason in dcac_certificate_rejection_reasons(
                                certificate,
                                majority,
                                challenger,
                                decision.representation_risks,
                            )
                        ]
                        summary_counts["dcac_guard_rejected_certificates"] += sum(
                            1
                            for certificate in parsed_certs
                            if dcac_certificate_rejection_reasons(
                                certificate,
                                majority,
                                challenger,
                                decision.representation_risks,
                            )
                        )
                        if raw_flip_count >= required and dcac_decision != "flip":
                            summary_counts["dcac_guard_blocked_flips"] += 1
                        final_tie = False
                        if dcac_decision == "flip":
                            summary_counts["dcac_flips"] += 1
                        branch_result = {
                            "decision": dcac_decision,
                            "active_challenger_card_id": challenger.card_id,
                            "admissible_flip_certificates": flip_count,
                            "raw_admissible_flip_certificates": raw_flip_count,
                            "required_flip_certificates": required,
                            "guard_rejection_reasons": sorted(set(guard_rejected)),
                        }
            elif decision.action == "listwise_discriminant":
                summary_counts["listwise_cases"] += 1
                if listwise_by_row[idx]:
                    review_answers = [output.get("parsed_answer") for output in listwise_by_row[idx]]
                    final_answer, final_tie = majority_vote(review_answers)
                    branch_result = {"decision": "listwise_majority"}

            initial_ok = is_correct(initial_majority, gold)
            final_ok = is_correct(final_answer, gold)
            transition = transition_label(initial_ok, final_ok)
            if initial_ok:
                summary_counts["initial_majority_correct"] += 1
            if final_ok:
                summary_counts["final_correct"] += 1
            if normalize_numeric(final_answer) is None:
                summary_counts["final_parse_fail"] += 1
            if final_tie:
                summary_counts["final_majority_ties"] += 1
            if normalize_numeric(initial_majority) != normalize_numeric(final_answer):
                summary_counts["answer_changed"] += 1
            if decision.representation_risks:
                summary_counts["representation_risk_cases"] += 1
            summary_counts[transition] += 1

            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row.get("index", idx),
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "cpac": {
                    "protocol": method_key,
                    "agents": args.agents,
                    "reviewers": args.reviewers,
                    "initial_outputs": initial_by_row[idx],
                    "initial_majority_answer": initial_majority,
                    "initial_majority_tie": initial_tie,
                    "candidate_cards": [card_payload(card) for card in cards_by_row[idx]],
                    "candidate_pool_decision": decision_payload(decision),
                    "dcac_claims": claims_by_row[idx],
                    "dcac_certificates": certificates_by_row[idx],
                    "listwise_outputs": listwise_by_row[idx],
                    "branch_result": branch_result,
                    "final_majority_answer": final_answer,
                    "final_normalized_answer": normalize_numeric(final_answer),
                    "final_majority_tie": final_tie,
                    "correct": final_ok,
                    "transition": transition,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    elapsed = time.time() - started_at
    total = max(1, len(rows))
    initial_wrong = max(1, summary_counts["MaW_to_C"] + summary_counts["MaW_to_W"])
    initial_correct = max(1, summary_counts["MaC_to_C"] + summary_counts["MaC_to_W"])
    dcac_cases = max(1, summary_counts["dcac_cases"])
    summary = {
        "run_id": args.run_id,
        "model_key": args.model_key,
        "model_path": str(model_path),
        "benchmark": args.benchmark,
        "split": args.split,
        "rows": len(rows),
        "protocol": method_key,
        "agents": args.agents,
        "reviewers": args.reviewers,
        "no_majority_action": args.no_majority_action,
        "dcac_min_flip_certificates": args.dcac_min_flip_certificates,
        "temperature": args.temperature,
        "claim_temperature": args.claim_temperature,
        "certificate_temperature": args.certificate_temperature,
        "listwise_temperature": args.listwise_temperature,
        "initial_prompt_style": args.initial_prompt_style,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": {
            **summary_counts,
            "pool_states": dict(sorted(pool_state_counts.items())),
            "actions": dict(sorted(action_counts.items())),
        },
        "metrics": {
            "initial_majority_accuracy": summary_counts["initial_majority_correct"] / total,
            "final_accuracy": summary_counts["final_correct"] / total,
            "answer_change_rate": summary_counts["answer_changed"] / total,
            "dcac_case_rate": summary_counts["dcac_cases"] / total,
            "dcac_valid_claim_rate": summary_counts["valid_directional_claims"] / dcac_cases,
            "dcac_flip_rate": summary_counts["dcac_flips"] / dcac_cases,
            "listwise_case_rate": summary_counts["listwise_cases"] / total,
            "representation_risk_rate": summary_counts["representation_risk_cases"] / total,
            "wrong_majority_recovery_rate": summary_counts["MaW_to_C"] / initial_wrong,
            "correct_majority_preservation_rate": summary_counts["MaC_to_C"] / initial_correct,
            "final_parse_fail_rate": summary_counts["final_parse_fail"] / total,
            "final_majority_tie_rate": summary_counts["final_majority_ties"] / total,
        },
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {args.benchmark}-{args.model_key}-{method_key}\n\n")
        handle.write(f"- Rows: {len(rows)}\n")
        handle.write(f"- Initial majority accuracy: {summary['metrics']['initial_majority_accuracy']:.4f}\n")
        handle.write(f"- Final accuracy: {summary['metrics']['final_accuracy']:.4f}\n")
        handle.write(f"- DCAC case rate: {summary['metrics']['dcac_case_rate']:.4f}\n")
        handle.write(f"- DCAC valid claim rate: {summary['metrics']['dcac_valid_claim_rate']:.4f}\n")
        handle.write(f"- DCAC flip rate: {summary['metrics']['dcac_flip_rate']:.4f}\n")
        handle.write(f"- Listwise case rate: {summary['metrics']['listwise_case_rate']:.4f}\n")
        handle.write(f"- Final tie rate: {summary['metrics']['final_majority_tie_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
