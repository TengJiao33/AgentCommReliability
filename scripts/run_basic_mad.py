#!/usr/bin/env python3
"""Run a minimal multi-agent debate baseline on prepared JSONL benchmarks."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ModelSpec:
    key: str
    path: Path


ROLE_NAMES = (
    "careful arithmetic solver",
    "skeptical checker",
    "concise verifier",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default=os.environ.get("ACR_WORK_DIR", os.getcwd()))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--benchmark", default="gsm8k")
    parser.add_argument("--split", default="test")
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--gpu-id", default=os.environ.get("CUDA_VISIBLE_DEVICES", "0"))
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--direct-temperature", type=float, default=0.0)
    parser.add_argument("--debate-temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-model-len", type=int, default=4096)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.82)
    parser.add_argument("--dtype", default="auto")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    parser.add_argument(
        "--disable-tqdm",
        action="store_true",
        help="Disable vLLM progress bars; useful for remote nohup/CI runs.",
    )
    return parser.parse_args()


def resolve_inside(path: Path, root: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SystemExit(f"{label} must stay inside work-dir: {resolved}") from exc
    return resolved


def load_rows(path: Path, limit: int) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
            if limit and len(rows) >= limit:
                break
    return rows


def prompt_from_messages(tokenizer: Any, messages: list[dict[str, str]]) -> str:
    template = getattr(tokenizer, "chat_template", None)
    if template:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    rendered = []
    for message in messages:
        role = message["role"].upper()
        rendered.append(f"{role}: {message['content']}")
    rendered.append("ASSISTANT:")
    return "\n\n".join(rendered)


def direct_prompt(question: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "You solve grade-school math problems. Show concise reasoning and end with exactly 'Final answer: <answer>'.",
        },
        {"role": "user", "content": question},
    ]


def initial_agent_prompt(question: str, agent_index: int) -> list[dict[str, str]]:
    role = ROLE_NAMES[agent_index % len(ROLE_NAMES)]
    return [
        {
            "role": "system",
            "content": (
                f"You are agent {agent_index + 1}, a {role}. Solve independently. "
                "Show concise reasoning and end with exactly 'Final answer: <answer>'."
            ),
        },
        {"role": "user", "content": question},
    ]


def revision_prompt(
    question: str,
    agent_index: int,
    own_answer: str,
    peer_answers: list[tuple[int, str]],
) -> list[dict[str, str]]:
    peer_text = "\n\n".join(f"Agent {idx + 1} said:\n{text}" for idx, text in peer_answers)
    return [
        {
            "role": "system",
            "content": (
                f"You are agent {agent_index + 1}. Reconsider your solution after reading the other agents. "
                "If another answer is better, switch. End with exactly 'Final answer: <answer>'."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                f"Your previous answer:\n{own_answer}\n\n"
                f"Other agents:\n{peer_text}\n\n"
                "Give your revised solution."
            ),
        },
    ]


def find_answer_text(text: str) -> str | None:
    final_matches = re.findall(r"Final answer\s*:\s*(.+)", text, flags=re.IGNORECASE)
    if final_matches:
        return final_matches[-1].strip()
    gsm_matches = re.findall(r"####\s*(.+)", text)
    if gsm_matches:
        return gsm_matches[-1].strip()
    boxed = extract_boxed_answer(text)
    if boxed is not None:
        return boxed.strip()
    number_matches = re.findall(r"-?\d[\d,]*(?:\.\d+)?(?:\s*/\s*-?\d[\d,]*(?:\.\d+)?)?", text)
    if number_matches:
        return number_matches[-1].strip()
    return None


_LATEX2SYMPY_LOADED = False
_LATEX2SYMPY: Any = None
_CANONICAL_PREFIXES = ("expr:", "str:")
_PLACEHOLDER_STRINGS = {
    "yourfinalansweronly",
    "yourfinalansweronlynoothertext",
    "thefinalanswer",
    "finalanswer",
    "youranswer",
    "answer",
}


def _get_latex2sympy() -> Any:
    global _LATEX2SYMPY_LOADED, _LATEX2SYMPY
    if not _LATEX2SYMPY_LOADED:
        _LATEX2SYMPY_LOADED = True
        try:
            from latex2sympy2 import latex2sympy

            _LATEX2SYMPY = latex2sympy
        except Exception:
            _LATEX2SYMPY = None
    return _LATEX2SYMPY


def _command_contents(text: str, command: str) -> list[str]:
    marker = f"\\{command}" + "{"
    contents: list[str] = []
    start = 0
    while True:
        pos = text.find(marker, start)
        if pos < 0:
            break
        brace_pos = pos + len(marker) - 1
        depth = 0
        for idx in range(brace_pos, len(text)):
            char = text[idx]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    contents.append(text[brace_pos + 1 : idx])
                    start = idx + 1
                    break
        else:
            break
    return contents


def extract_boxed_answer(text: Any) -> str | None:
    if text is None:
        return None
    raw = str(text)
    for command in ("boxed", "fbox"):
        contents = _command_contents(raw, command)
        if contents:
            return contents[-1]
    return None


def _replace_text_commands(text: str) -> str:
    previous = None
    current = text
    pattern = re.compile(r"\\(?:text|mathrm|operatorname)\{([^{}]*)\}")
    while previous != current:
        previous = current
        current = pattern.sub(r"\1", current)
    return current


def _replace_latex_fracs(text: str) -> str:
    previous = None
    current = text
    pattern = re.compile(r"\\(?:dfrac|tfrac|frac)\{([^{}]+)\}\{([^{}]+)\}")
    while previous != current:
        previous = current
        current = pattern.sub(r"((\1)/(\2))", current)
    return current


def _expand_latex_frac_shorthand(text: str) -> str:
    return re.sub(r"\\(?:dfrac|tfrac|frac)\s*([+-]?\d+)\s*([+-]?\d+)", r"\\frac{\1}{\2}", text)


def _replace_latex_mixed_fracs(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        whole = match.group(1)
        numerator = match.group(2)
        denominator = match.group(3)
        if whole.startswith("-"):
            return f"(-{whole[1:]} - (({numerator})/({denominator})))"
        return f"(({whole}) + (({numerator})/({denominator})))"

    pattern = re.compile(r"(?<![\w.])(-?\d+)\s+\\(?:dfrac|tfrac|frac)\{([^{}]+)\}\{([^{}]+)\}")
    return pattern.sub(replace, text)


def _replace_latex_sqrts(text: str) -> str:
    previous = None
    current = text
    pattern = re.compile(r"\\sqrt\{([^{}]+)\}")
    while previous != current:
        previous = current
        current = pattern.sub(r"sqrt(\1)", current)
    return re.sub(r"\\sqrt\s*([A-Za-z0-9]+)", r"sqrt(\1)", current)


def _clean_answer_text(answer: Any) -> str | None:
    if answer is None:
        return None
    text = str(answer).strip()
    if not text:
        return None
    if "####" in text:
        text = text.split("####")[-1].strip()
    boxed = extract_boxed_answer(text)
    if boxed is not None:
        text = boxed.strip()
    elif re.search(r"Final answer\s*:", text, flags=re.IGNORECASE):
        final = find_answer_text(text)
        if final is not None and final.strip() != text:
            text = final.strip()
    text = text.strip().strip("$").strip()
    text = re.sub(r"^\\\(|\\\)$", "", text).strip()
    text = re.sub(r"^\\\[|\\\]$", "", text).strip()
    text = _replace_text_commands(text)
    text = text.replace("\\left", "").replace("\\right", "")
    text = text.replace("\\,", "").replace("\\!", "").replace("\\;", "").replace("\\:", "")
    text = text.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    text = re.sub(r"\^\s*\{?\\*circ\}?", "", text)
    text = text.replace("°", "")
    text = text.replace("\\$", "")
    text = text.replace("%", "").replace("\\%", "")
    text = text.replace("$", "").strip()
    text = text.rstrip(".")
    return text.strip() or None


def _ascii_math_text(text: str) -> str:
    value = _expand_latex_frac_shorthand(text)
    value = _replace_latex_mixed_fracs(value)
    value = _replace_latex_sqrts(value)
    value = _replace_latex_fracs(value)
    value = value.replace("\\pi", "pi")
    value = value.replace("\\infty", "oo")
    value = value.replace("\\cdot", "*").replace("\\times", "*")
    value = value.replace("^", "**")
    value = value.replace("{", "(").replace("}", ")")
    value = value.replace("\\", "")
    value = value.replace(",", ", ")
    value = re.sub(r"(?<=\d)i\b", "*I", value)
    value = re.sub(r"\bi\b", "I", value) if re.search(r"\d\s*\*?I\b", value) else value
    return value.strip()


def _already_canonical(text: str) -> str | None:
    stripped = text.strip()
    if not stripped.startswith(_CANONICAL_PREFIXES):
        return None
    prefix, payload = stripped.split(":", 1)
    payload = payload.strip()
    if not payload:
        return None
    if prefix == "expr" and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", payload) and payload not in {"E", "I", "oo", "pi"}:
        return "str:" + payload.lower()
    if prefix == "str":
        return "str:" + re.sub(r"\s+", "", payload.lower())
    if prefix == "expr":
        simple_numeric = _simple_numeric_canonical(payload)
        if simple_numeric is not None:
            return simple_numeric
        symbolic = _sympy_canonical(payload)
        return symbolic or stripped
    return None


def _simple_numeric_canonical(text: str) -> str | None:
    value = text.replace("\\$", "").replace("$", "").strip()
    match = re.fullmatch(
        r"(-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:\s*/\s*-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)?)"
        r"(?:\s+[A-Za-z][A-Za-z\s]*)?",
        value,
    )
    if not match:
        return None
    token = match.group(1).replace(",", "").replace(" ", "")
    try:
        return "expr:" + str(Fraction(token))
    except Exception:
        try:
            return "expr:" + str(Fraction(float(token)).limit_denominator(1000000))
        except Exception:
            return None


def _mixed_fraction_canonical(text: str) -> str | None:
    expanded = _expand_latex_frac_shorthand(text)
    mixed = _replace_latex_mixed_fracs(expanded)
    if mixed == expanded:
        return None
    return _sympy_canonical(mixed)


def _looks_like_symbolic_math(text: str) -> bool:
    return bool(re.search(r"sqrt\(|\b(?:pi|oo|I)\b|[+\-*/^(),]", text))


def _has_non_math_words(text: str) -> bool:
    allowed_words = {"sqrt", "pi", "oo", "I"}
    return any(len(word) > 1 and word not in allowed_words for word in re.findall(r"[A-Za-z_]+", text))


def _sympy_canonical(text: str) -> str | None:
    try:
        import sympy as sp
        from sympy.parsing.sympy_parser import (
            convert_xor,
            implicit_multiplication_application,
            parse_expr,
            standard_transformations,
        )
    except Exception:
        return None

    ascii_text = _ascii_math_text(text)
    candidates = [ascii_text]
    if ascii_text != text:
        candidates.append(text)
    latex2sympy = _get_latex2sympy()
    if latex2sympy is not None and "\\" in text:
        try:
            expr = latex2sympy(text)
            return "expr:" + sp.sstr(sp.simplify(expr))
        except Exception:
            pass
    transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
    local_dict = {"sqrt": sp.sqrt, "pi": sp.pi, "oo": sp.oo, "I": sp.I}
    for candidate in candidates:
        if not candidate:
            continue
        if not _looks_like_symbolic_math(candidate):
            continue
        if _has_non_math_words(candidate):
            continue
        try:
            expr = parse_expr(
                candidate,
                local_dict=local_dict,
                transformations=transformations,
                evaluate=True,
            )
        except Exception:
            try:
                expr = sp.sympify(candidate, evaluate=True)
            except Exception:
                continue
        try:
            expr = sp.simplify(expr)
        except Exception:
            pass
        if getattr(expr, "is_number", False):
            try:
                expr = sp.nsimplify(expr)
            except Exception:
                pass
        return "expr:" + sp.sstr(expr)
    return None


def _numeric_canonical(text: str) -> str | None:
    value = text.replace(",", "").replace("$", "").strip()
    value = _expand_latex_frac_shorthand(value)
    value = _replace_latex_mixed_fracs(value)
    value = _replace_latex_fracs(value)
    matches = re.findall(r"-?\d+(?:\.\d+)?(?:\s*/\s*-?\d+(?:\.\d+)?)?", value)
    if not matches:
        return None
    token = matches[-1].replace(" ", "")
    try:
        return "expr:" + str(Fraction(token))
    except Exception:
        try:
            return "expr:" + str(Fraction(float(token)).limit_denominator(1000000))
        except Exception:
            return "str:" + token


def _string_canonical(text: str) -> str | None:
    value = text.lower().strip()
    value = _replace_text_commands(value)
    value = value.replace("\\left", "").replace("\\right", "")
    value = value.replace("\\,", "").replace("\\!", "")
    value = re.sub(r"\s+", "", value)
    value = value.strip("$")
    value = value.rstrip(".")
    if value in _PLACEHOLDER_STRINGS:
        return None
    if not re.search(r"[a-z0-9]", value):
        return None
    return ("str:" + value) if value else None


def normalize_numeric(answer: Any) -> str | None:
    text = _clean_answer_text(answer)
    if not text:
        return None
    canonical = _already_canonical(text)
    if canonical is not None:
        return canonical
    simple_numeric = _simple_numeric_canonical(text)
    if simple_numeric is not None:
        return simple_numeric
    mixed_fraction = _mixed_fraction_canonical(text)
    if mixed_fraction is not None:
        return mixed_fraction
    return _sympy_canonical(text) or _numeric_canonical(text) or _string_canonical(text)


def is_correct(prediction: Any, gold: Any) -> bool:
    pred_norm = normalize_numeric(prediction)
    gold_norm = normalize_numeric(gold)
    return pred_norm is not None and gold_norm is not None and pred_norm == gold_norm


def majority_vote(agent_answers: list[str | None]) -> tuple[str | None, bool]:
    normalized = [normalize_numeric(answer) for answer in agent_answers]
    normalized = [answer for answer in normalized if answer is not None]
    if not normalized:
        return None, False
    counts = Counter(normalized)
    best_count = max(counts.values())
    winners = [answer for answer, count in counts.items() if count == best_count]
    if len(winners) == 1:
        return winners[0], False
    for answer in normalized:
        if answer in winners:
            return answer, True
    return winners[0], True


def generate_texts(
    llm: Any,
    prompts: list[str],
    sampling_params: Any,
    batch_size: int,
    *,
    use_tqdm: bool,
) -> list[str]:
    outputs: list[str] = []
    for start in range(0, len(prompts), batch_size):
        batch = prompts[start : start + batch_size]
        for result in llm.generate(batch, sampling_params, use_tqdm=use_tqdm):
            outputs.append(result.outputs[0].text)
    return outputs


def main() -> int:
    args = parse_args()
    work_dir = Path(args.work_dir).expanduser().resolve()
    data_path = resolve_inside(
        work_dir / "data" / "benchmarks" / args.benchmark / args.split / "canonical.jsonl",
        work_dir,
        "benchmark path",
    )
    output_dir = resolve_inside(work_dir / "experiments" / args.run_id / args.model_key, work_dir, "output dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    from vllm import LLM, SamplingParams

    rows = load_rows(data_path, args.limit)
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

    direct_sampling = SamplingParams(
        temperature=args.direct_temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
    )
    debate_sampling = SamplingParams(
        temperature=args.debate_temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
    )

    questions = [str(row.get("question") or "") for row in rows]
    direct_prompts = [prompt_from_messages(tokenizer, direct_prompt(question)) for question in questions]
    use_tqdm = not args.disable_tqdm
    direct_outputs = generate_texts(llm, direct_prompts, direct_sampling, args.batch_size, use_tqdm=use_tqdm)

    initial_prompts = []
    for question in questions:
        for agent_idx in range(args.agents):
            initial_prompts.append(prompt_from_messages(tokenizer, initial_agent_prompt(question, agent_idx)))
    initial_flat = generate_texts(llm, initial_prompts, debate_sampling, args.batch_size, use_tqdm=use_tqdm)
    initial_by_row = [
        initial_flat[i * args.agents : (i + 1) * args.agents]
        for i in range(len(rows))
    ]

    current_by_row = initial_by_row
    for _round_idx in range(args.rounds):
        revision_prompts = []
        for row_idx, question in enumerate(questions):
            for agent_idx in range(args.agents):
                peer_answers = [
                    (other_idx, current_by_row[row_idx][other_idx])
                    for other_idx in range(args.agents)
                    if other_idx != agent_idx
                ]
                revision_prompts.append(
                    prompt_from_messages(
                        tokenizer,
                        revision_prompt(question, agent_idx, current_by_row[row_idx][agent_idx], peer_answers),
                    )
                )
        revised_flat = generate_texts(llm, revision_prompts, debate_sampling, args.batch_size, use_tqdm=use_tqdm)
        current_by_row = [
            revised_flat[i * args.agents : (i + 1) * args.agents]
            for i in range(len(rows))
        ]

    records_path = output_dir / "records.jsonl"
    summary_counts = {
        "total": len(rows),
        "direct_correct": 0,
        "mad_correct": 0,
        "direct_parse_fail": 0,
        "mad_parse_fail": 0,
        "majority_ties": 0,
    }
    agent_correct = [0 for _ in range(args.agents)]
    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for idx, row in enumerate(rows):
            gold = row.get("answer")
            direct_answer = find_answer_text(direct_outputs[idx])
            final_agent_answers = [find_answer_text(text) for text in current_by_row[idx]]
            majority_answer, tied = majority_vote(final_agent_answers)
            direct_ok = is_correct(direct_answer, gold)
            mad_ok = is_correct(majority_answer, gold)
            if direct_ok:
                summary_counts["direct_correct"] += 1
            if mad_ok:
                summary_counts["mad_correct"] += 1
            if normalize_numeric(direct_answer) is None:
                summary_counts["direct_parse_fail"] += 1
            if majority_answer is None:
                summary_counts["mad_parse_fail"] += 1
            if tied:
                summary_counts["majority_ties"] += 1
            for agent_idx, answer in enumerate(final_agent_answers):
                if is_correct(answer, gold):
                    agent_correct[agent_idx] += 1
            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row.get("index", idx),
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "direct": {
                    "output": direct_outputs[idx],
                    "parsed_answer": direct_answer,
                    "normalized_answer": normalize_numeric(direct_answer),
                    "correct": direct_ok,
                },
                "mad": {
                    "initial_outputs": initial_by_row[idx],
                    "final_outputs": current_by_row[idx],
                    "parsed_agent_answers": final_agent_answers,
                    "normalized_agent_answers": [normalize_numeric(answer) for answer in final_agent_answers],
                    "majority_answer": majority_answer,
                    "majority_tie": tied,
                    "correct": mad_ok,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    elapsed = time.time() - started_at
    total = max(1, len(rows))
    summary = {
        "run_id": args.run_id,
        "model_key": args.model_key,
        "model_path": str(model_path),
        "benchmark": args.benchmark,
        "split": args.split,
        "rows": len(rows),
        "agents": args.agents,
        "rounds": args.rounds,
        "direct_temperature": args.direct_temperature,
        "debate_temperature": args.debate_temperature,
        "max_tokens": args.max_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": summary_counts,
        "metrics": {
            "direct_accuracy": summary_counts["direct_correct"] / total,
            "mad_accuracy": summary_counts["mad_correct"] / total,
            "agent_final_accuracy": [count / total for count in agent_correct],
            "direct_parse_fail_rate": summary_counts["direct_parse_fail"] / total,
            "mad_parse_fail_rate": summary_counts["mad_parse_fail"] / total,
            "majority_tie_rate": summary_counts["majority_ties"] / total,
        },
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {args.model_key}\n\n")
        handle.write(f"- Rows: {len(rows)}\n")
        handle.write(f"- Direct accuracy: {summary['metrics']['direct_accuracy']:.4f}\n")
        handle.write(f"- MAD accuracy: {summary['metrics']['mad_accuracy']:.4f}\n")
        handle.write(f"- Majority tie rate: {summary['metrics']['majority_tie_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
