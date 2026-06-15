"""Answer parsing and correctness helpers for peer-exposure probes."""

from __future__ import annotations

import math
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple


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


def extract_raw_final_answer_text(text: Any) -> Optional[str]:
    raw = "" if text is None else str(text)
    braced = extract_braced_final_answer(raw)
    if braced is not None:
        return braced.strip()
    patterns = [
        r"final\s+answer\s+from\s+this\s+peer\s*:\s*([^\n]+)",
        r"final\s+answer\s*(?:is|:)\s*([^\n]+)",
        r"answer\s*(?:is|:)\s*([^\n]+)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, raw, flags=re.I)
        if matches:
            return matches[-1].strip().rstrip(".;")
    return None


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


def is_numeric_value(value: Any) -> bool:
    norm = normalize_number(value)
    return isinstance(norm, (int, float))
