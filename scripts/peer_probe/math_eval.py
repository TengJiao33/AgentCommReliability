"""MATH answer extraction and lightweight semantic equivalence helpers.

This module is deliberately conservative. It returns ``None`` when an answer
cannot be compared reliably instead of falling back to "last number wins".
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple

from sympy import Eq, simplify
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

from .answers import extract_braced_final_answer


TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application, convert_xor)


@dataclass(frozen=True)
class EquivalenceResult:
    correct: Optional[bool]
    status: str
    prediction_raw: Optional[str]
    reference_raw: Optional[str]
    prediction_normalized: Optional[str]
    reference_normalized: Optional[str]


def _read_braced(text: str, start: int) -> Optional[Tuple[str, int]]:
    if start >= len(text) or text[start] != "{":
        return None
    depth = 1
    index = start + 1
    while index < len(text):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
        index += 1
    return None


def _last_latex_box(text: str, command: str) -> Optional[str]:
    last: Optional[str] = None
    index = 0
    needle = "\\" + command
    while True:
        found = text.find(needle, index)
        if found < 0:
            return last
        cursor = found + len(needle)
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        braced = _read_braced(text, cursor)
        if braced:
            last = braced[0].strip()
            index = braced[1]
        else:
            index = cursor + 1


def extract_boxed_answer(text: Any) -> Optional[str]:
    raw = "" if text is None else str(text)
    return _last_latex_box(raw, "boxed") or _last_latex_box(raw, "fbox")


def extract_answer_text(text: Any) -> Tuple[Optional[str], str]:
    raw = "" if text is None else str(text)
    braced = extract_braced_final_answer(raw)
    if braced is not None:
        return braced.strip(), "explicit_final_answer"

    patterns = [
        r"final\s+answer\s+from\s+this\s+peer\s*:\s*([^\n]+)",
        r"final\s+answer\s*(?:is|:)\s*([^\n]+)",
        r"answer\s*(?:is|:)\s*([^\n]+)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, raw, flags=re.I)
        if matches:
            return matches[-1].strip().rstrip(".;"), "explicit_final_answer"
    return None, "no_explicit_final_answer"


def _fix_shorthand_latex(text: str) -> str:
    text = re.sub(r"\\sqrt\s*(\w)", r"\\sqrt{\1}", text)
    text = re.sub(r"(?<=\d)\\frac", r"+\\frac", text)
    return text


def normalize_math_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    replacements = {
        "\u2212": "-",
        "\u00d7": "\\times",
        "\u00f7": "/",
        "\u221a": "\\sqrt",
        "\u03c0": "\\pi",
        "\u00b0": "",
        "\\(": "",
        "\\)": "",
        "\\[": "",
        "\\]": "",
        "$": "",
        "\\!": "",
        "\\,": "",
        "\\;": "",
        "\\ ": "",
        "\\left": "",
        "\\right": "",
        "tfrac": "frac",
        "dfrac": "frac",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\\(?:text|mbox)\{([^{}]*)\}", r"\1", text)
    text = text.replace("^{\\circ}", "").replace("^\\circ", "").replace("\\circ", "")
    text = text.replace("\\%", "").replace("%", "")
    if re.fullmatch(r"-?\d{1,3}(?:,\d{3})+(?:\.\d+)?", text.strip()):
        text = text.replace(",", "")
    text = re.sub(
        r"(?<=\d)\s*(?:m|cm|mm|km|in|ft|yd|meters?|metres?|inches?|feet|units?)\s*(?:\^\{?\d+\}?|\d)?\b",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"\b(?:degrees?|degree|units?|unit|meals?|meal|meters?|meter|metres?|metre|m|cm|inches?|inch|feet|foot|ft|seconds?|minutes?|hours?|dollars?)\b",
        "",
        text,
        flags=re.I,
    )
    text = text.replace("\\\\", "\\")
    text = re.sub(r"\s+", "", text)
    text = text.rstrip(".")
    text = _fix_shorthand_latex(text)
    return text or None


def _replace_braced_command(text: str, command: str, fn: Callable[[str], str]) -> str:
    needle = "\\" + command
    index = 0
    result: List[str] = []
    while index < len(text):
        if text.startswith(needle, index):
            cursor = index + len(needle)
            while cursor < len(text) and text[cursor].isspace():
                cursor += 1
            braced = _read_braced(text, cursor)
            if braced:
                result.append(fn(braced[0]))
                index = braced[1]
                continue
        result.append(text[index])
        index += 1
    return "".join(result)


def _replace_frac(text: str) -> str:
    needle = "\\frac"
    index = 0
    result: List[str] = []
    while index < len(text):
        if text.startswith(needle, index):
            cursor = index + len(needle)
            first = _read_braced(text, cursor)
            if first:
                second = _read_braced(text, first[1])
                if second:
                    result.append(f"(({latex_to_sympy_text(first[0])})/({latex_to_sympy_text(second[0])}))")
                    index = second[1]
                    continue
        result.append(text[index])
        index += 1
    return "".join(result)


def latex_to_sympy_text(value: Any) -> Optional[str]:
    text = normalize_math_text(value)
    if text is None:
        return None
    if "\\begin{pmatrix}" in text or "\\begin{matrix}" in text:
        return None
    if re.fullmatch(r"[01]+_2", text):
        return None

    text = _replace_frac(text)
    text = _replace_braced_command(text, "sqrt", lambda arg: f"sqrt({latex_to_sympy_text(arg) or arg})")
    text = text.replace("\\pi", "pi")
    text = text.replace("\\cdot", "*").replace("\\times", "*")
    text = text.replace("\\div", "/")
    text = text.replace("^", "**")
    text = re.sub(r"(?<![A-Za-z])i(?![A-Za-z])", "I", text)
    text = text.replace("{", "(").replace("}", ")")
    text = text.replace("[", "(").replace("]", ")")
    text = re.sub(r"\\[A-Za-z]+", "", text)
    return text or None


def _parse_expr_or_none(value: Any) -> Any:
    text = latex_to_sympy_text(value)
    if text is None:
        return None
    try:
        if "=" in text and text.count("=") == 1:
            left, right = text.split("=", 1)
            return simplify(parse_expr(left, transformations=TRANSFORMATIONS) - parse_expr(right, transformations=TRANSFORMATIONS))
        return parse_expr(text, transformations=TRANSFORMATIONS)
    except Exception:
        return None


def _outer_wrapper(text: str) -> Optional[str]:
    stripped = text.strip()
    if len(stripped) >= 2 and stripped[0] in "([{" and stripped[-1] in ")]}":
        pairs = {"(": ")", "[": "]", "{": "}"}
        if pairs.get(stripped[0]) == stripped[-1]:
            return stripped[0]
    return None


def _split_top_level(text: str) -> List[str]:
    parts: List[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(text):
        if char in "({[":
            depth += 1
        elif char in ")}]":
            depth = max(0, depth - 1)
        elif char in ",;" and depth == 0:
            parts.append(text[start:index])
            start = index + 1
    parts.append(text[start:])
    return [part for part in (p.strip() for p in parts) if part]


def _compare_component_lists(prediction: str, reference: str) -> Optional[bool]:
    pred_norm = normalize_math_text(prediction)
    ref_norm = normalize_math_text(reference)
    if not pred_norm or not ref_norm:
        return None
    pred_parts = _split_top_level(pred_norm.strip("()[]{}"))
    ref_parts = _split_top_level(ref_norm.strip("()[]{}"))
    if len(pred_parts) <= 1 or len(pred_parts) != len(ref_parts):
        return None

    ordered = _outer_wrapper(pred_norm) in {"(", "["} or _outer_wrapper(ref_norm) in {"(", "["}
    if ordered:
        results = [math_equiv(left, right).correct for left, right in zip(pred_parts, ref_parts)]
        if any(result is False for result in results):
            return False
        return True if all(result is True for result in results) else None

    unmatched = list(ref_parts)
    saw_unknown = False
    for pred_part in pred_parts:
        matched_index = None
        for index, ref_part in enumerate(unmatched):
            result = math_equiv(pred_part, ref_part).correct
            if result is True:
                matched_index = index
                break
            if result is None:
                saw_unknown = True
        if matched_index is None:
            return None if saw_unknown else False
        unmatched.pop(matched_index)
    return True


def math_equiv(prediction: Any, reference: Any) -> EquivalenceResult:
    pred_raw = None if prediction is None else str(prediction).strip()
    ref_raw = None if reference is None else str(reference).strip()
    pred_norm = normalize_math_text(pred_raw)
    ref_norm = normalize_math_text(ref_raw)
    base = {
        "prediction_raw": pred_raw,
        "reference_raw": ref_raw,
        "prediction_normalized": pred_norm,
        "reference_normalized": ref_norm,
    }
    if not pred_norm or not ref_norm:
        return EquivalenceResult(None, "missing_answer", **base)

    if pred_norm.lower() == ref_norm.lower():
        return EquivalenceResult(True, "normalized_string_equal", **base)

    list_result = _compare_component_lists(pred_norm, ref_norm)
    if list_result is not None:
        return EquivalenceResult(list_result, "component_list_compare", **base)

    pred_expr = _parse_expr_or_none(pred_norm)
    ref_expr = _parse_expr_or_none(ref_norm)
    if pred_expr is None or ref_expr is None:
        return EquivalenceResult(None, "unknown_semantic_parse", **base)

    try:
        if isinstance(pred_expr, Eq) or isinstance(ref_expr, Eq):
            equal = simplify(pred_expr.lhs - pred_expr.rhs - (ref_expr.lhs - ref_expr.rhs)) == 0
        else:
            diff = simplify(pred_expr - ref_expr)
            if diff == 0:
                equal = True
            elif diff.is_number:
                try:
                    equal = math.isclose(float(diff), 0.0, rel_tol=1e-9, abs_tol=1e-9)
                except (TypeError, ValueError):
                    equal = False
            else:
                equal = False
        return EquivalenceResult(bool(equal), "sympy_compare", **base)
    except Exception:
        return EquivalenceResult(None, "unknown_semantic_compare", **base)


def semantic_correct_from_output(output: Any, reference: Any) -> EquivalenceResult:
    answer, _ = extract_answer_text(output)
    return math_equiv(answer, reference)
