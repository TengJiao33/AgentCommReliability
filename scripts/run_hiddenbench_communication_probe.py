#!/usr/bin/env python3
"""Run a communication-necessity probe on HiddenBench.

This runner keeps the task object external and simple: every HiddenBench
instance has shared facts, private facts, answer options, and one gold answer.
The probe compares partial-information agents with full-information and
exchange-then-decide conditions.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import string
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


DEFAULT_BENCHMARK = Path("data/external/hiddenbench/benchmark.json")
DEFAULT_OUT_ROOT = Path("experiments/20260617-local-hiddenbench-communication-probe")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def append_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize_answer(value: Optional[str]) -> str:
    if value is None:
        return ""
    text = str(value).lower()
    text = "".join(ch for ch in text if ch not in set(string.punctuation))
    return " ".join(text.split())


def choices_block(task: Mapping[str, Any]) -> str:
    return "\n".join(f"- {choice}" for choice in task["possible_answers"])


def facts_block(title: str, facts: Sequence[str]) -> str:
    if not facts:
        return f"{title}\n<none>"
    return title + "\n" + "\n".join(f"- {fact}" for fact in facts)


def redacted_task_description(task: Mapping[str, Any]) -> str:
    text = str(task["description"])
    for index, choice in enumerate(task["possible_answers"], start=1):
        replacement = f"[answer option {index}]"
        text = text.replace(str(choice), replacement)
        if ":" in str(choice):
            text = text.replace(str(choice).split(":", 1)[0].strip(), replacement)
    return text


def answer_prompt(task: Mapping[str, Any], *, visible_facts: Sequence[str], condition_note: str) -> str:
    return f"""You are solving a HiddenBench decision task.

Task description:
{task["description"]}

{facts_block("Visible shared information:", task["shared_information"])}

{facts_block("Additional information visible to you:", list(visible_facts))}

Decision constraint:
{condition_note}

Possible answers:
{choices_block(task)}

Choose exactly one possible answer.
Your first line must be exactly:
Answer: <one possible answer>

Then add at most three short bullets explaining the decisive facts."""


def agent_message_prompt(task: Mapping[str, Any], *, private_fact: str, agent_index: int) -> str:
    return f"""You are Agent {agent_index} in a HiddenBench group decision task.

Task description:
{task["description"]}

{facts_block("Shared information visible to everyone:", task["shared_information"])}

Your private information:
- {private_fact}

Possible answers:
{choices_block(task)}

Write a short public message for the group. Include only decision-relevant facts
you can justify from your visible information and, if useful, a tentative
recommendation. Do not invent facts. Use at most four bullets."""


def no_recommendation_agent_message_prompt(
    task: Mapping[str, Any], *, private_fact: str, agent_index: int
) -> str:
    return f"""You are Agent {agent_index} in a HiddenBench group decision task.

Task description:
{task["description"]}

{facts_block("Shared information visible to everyone:", task["shared_information"])}

Your private information:
- {private_fact}

Possible answers:
{choices_block(task)}

Write a short public message for the group. Include decision-relevant facts you
can justify from your visible information.

Rules:
- Do not recommend an answer.
- Do not rank, compare, or eliminate possible answers.
- Do not say which option seems best or safest.
- Do not invent facts.

Use at most four bullets."""


def no_shared_repeat_agent_message_prompt(
    task: Mapping[str, Any], *, private_fact: str, agent_index: int
) -> str:
    return f"""You are Agent {agent_index} in a HiddenBench group decision task.

Task description:
{task["description"]}

{facts_block("Shared information visible to everyone:", task["shared_information"])}

Your private information:
- {private_fact}

Possible answers:
{choices_block(task)}

Write a short public message for the group. Include your private information and,
if useful, a tentative recommendation.

Rules:
- Do not repeat shared information.
- Do not use shared information as a reason for your recommendation.
- Do not invent facts.

Use at most four bullets."""


def fact_only_agent_message_prompt(task: Mapping[str, Any], *, private_fact: str, agent_index: int) -> str:
    return f"""You are Agent {agent_index} in a HiddenBench group decision task.

Task description:
{task["description"]}

Your private information:
- {private_fact}

Write a public message that reports only your private information.

Rules:
- Do not recommend an answer.
- Do not rank, compare, or eliminate possible answers.
- Do not repeat shared information.
- Do not infer beyond your private information.
- Do not add facts that are not in your private information.

Use exactly this format:
Private fact report:
- <your private fact>"""


def fact_only_with_options_agent_message_prompt(
    task: Mapping[str, Any], *, private_fact: str, agent_index: int
) -> str:
    return f"""You are Agent {agent_index} in a HiddenBench group decision task.

Task description:
{task["description"]}

Your private information:
- {private_fact}

Possible answers:
{choices_block(task)}

Write a public message that reports only your private information.

Rules:
- Do not recommend an answer.
- Do not rank, compare, or eliminate possible answers.
- Do not repeat shared information.
- Do not infer beyond your private information.
- Do not add facts that are not in your private information.

Use exactly this format:
Private fact report:
- <your private fact>"""


def blind_agent_message_prompt(task: Mapping[str, Any], *, private_fact: str, agent_index: int) -> str:
    return f"""You are Agent {agent_index} in a group study.

You do not know the final task, answer options, or shared background seen by
the group. You only have one local observation:
- {private_fact}

Write a short public message for the group that preserves what you observed.
Do not guess the final task, recommend an action, rank options, or invent
background details. Use at most two bullets."""


def blind_minimal_agent_message_prompt(task: Mapping[str, Any], *, private_fact: str, agent_index: int) -> str:
    return f"""You are Agent {agent_index} in a group study.

You do not know the final task, answer options, or shared background seen by
the group. You only have one local observation:
- {private_fact}

Report the observation without interpreting it.

Use exactly this format:
Local observation:
- <your observation>"""


def private_plus_task_minimal_agent_message_prompt(
    task: Mapping[str, Any], *, private_fact: str, agent_index: int
) -> str:
    return f"""You are Agent {agent_index} in a group study.

Task description with answer options redacted:
{redacted_task_description(task)}

Your local observation:
- {private_fact}

You do not know the answer option names or shared background seen by the group.

Report only the local observation without interpreting it.

Use exactly this format:
Local observation:
- <your observation>"""


def private_plus_options_minimal_agent_message_prompt(
    task: Mapping[str, Any], *, private_fact: str, agent_index: int
) -> str:
    return f"""You are Agent {agent_index} in a group study.

Possible answers:
{choices_block(task)}

Your local observation:
- {private_fact}

You do not know the final task or shared background seen by the group.

Report only the local observation without interpreting it.

Use exactly this format:
Local observation:
- <your observation>"""


def private_plus_shared_minimal_agent_message_prompt(
    task: Mapping[str, Any], *, private_fact: str, agent_index: int
) -> str:
    return f"""You are Agent {agent_index} in a group study.

{facts_block("Shared information visible to everyone:", task["shared_information"])}

Your local observation:
- {private_fact}

You do not know the final task or answer options.

Report only the local observation without interpreting it.

Use exactly this format:
Local observation:
- <your observation>"""


def full_visibility_minimal_agent_message_prompt(
    task: Mapping[str, Any], *, private_fact: str, agent_index: int
) -> str:
    return f"""You are Agent {agent_index} in a HiddenBench group decision task.

Task description:
{task["description"]}

{facts_block("Shared information visible to everyone:", task["shared_information"])}

Your local observation:
- {private_fact}

Possible answers:
{choices_block(task)}

Report only the local observation without interpreting it.

Use exactly this format:
Local observation:
- <your observation>"""


def exchange_decide_prompt(task: Mapping[str, Any], *, messages: Sequence[Mapping[str, Any]]) -> str:
    message_block = "\n\n".join(
        f"[Agent {message['agent_index']}]\n{message['message']}" for message in messages
    )
    return f"""You are the final decision maker for a HiddenBench group decision task.

Task description:
{task["description"]}

{facts_block("Shared information visible to everyone:", task["shared_information"])}

Public messages from agents:
{message_block}

Possible answers:
{choices_block(task)}

Choose exactly one possible answer based only on the shared information and
public messages.
Your first line must be exactly:
Answer: <one possible answer>

Then add at most three short bullets explaining the decisive facts."""


def constraint_decide_prompt(task: Mapping[str, Any], *, messages: Sequence[Mapping[str, Any]]) -> str:
    message_block = "\n\n".join(
        f"[Agent {message['agent_index']}]\n{message['message']}" for message in messages
    )
    return f"""You are the final decision maker for a HiddenBench group decision task.

Task description:
{task["description"]}

{facts_block("Shared information visible to everyone:", task["shared_information"])}

Public private-fact reports from agents:
{message_block}

Possible answers:
{choices_block(task)}

Choose exactly one possible answer based only on the shared information and
public private-fact reports.

Your first line must be exactly:
Answer: <one possible answer>

Then write a compact option evidence table with one row per possible answer:
option | supporting facts | blocking facts | unknowns.

Treat a single hard blocking fact as decisive unless another public fact directly
overrides it. Do not use facts that are absent from the task or public reports."""


def oracle_public_facts_prompt(task: Mapping[str, Any]) -> str:
    messages = [
        {"agent_index": index, "message": f"- Private fact reported: {fact}"}
        for index, fact in enumerate(task["hidden_information"], start=1)
    ]
    return exchange_decide_prompt(task, messages=messages)


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


def parse_choice(output: str, choices: Sequence[str]) -> Tuple[Optional[str], str]:
    answer_match = re.search(r"(?im)^\s*answer\s*:\s*(.+?)\s*$", output)
    candidates = [answer_match.group(1).strip()] if answer_match else []
    candidates.append(output.strip().splitlines()[-1].strip() if output.strip() else "")
    normalized_choices = {normalize_answer(choice): choice for choice in choices}
    normalized_prefixes: Dict[str, List[str]] = defaultdict(list)
    for choice in choices:
        if ":" in choice:
            normalized_prefixes[normalize_answer(choice.split(":", 1)[0].strip())].append(choice)

    for candidate in candidates:
        candidate_norm = normalize_answer(candidate)
        if candidate_norm in normalized_choices:
            return normalized_choices[candidate_norm], "answer_line_exact"
        if len(normalized_prefixes.get(candidate_norm, [])) == 1:
            return normalized_prefixes[candidate_norm][0], "answer_line_unique_prefix"

    found = []
    output_norm = normalize_answer(output)
    for choice in choices:
        choice_norm = normalize_answer(choice)
        prefix_norm = normalize_answer(choice.split(":", 1)[0].strip()) if ":" in choice else ""
        if choice_norm and re.search(rf"\b{re.escape(choice_norm)}\b", output_norm):
            found.append(choice)
        elif prefix_norm and re.search(rf"\b{re.escape(prefix_norm)}\b", output_norm):
            found.append(choice)
    unique = sorted(set(found))
    if len(unique) == 1:
        return unique[0], "unique_choice_mention"
    return None, "unparsed"


TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "about",
    "above",
    "after",
    "again",
    "against",
    "agent",
    "answer",
    "because",
    "before",
    "being",
    "below",
    "between",
    "could",
    "facts",
    "from",
    "have",
    "into",
    "only",
    "option",
    "public",
    "report",
    "shared",
    "should",
    "that",
    "their",
    "there",
    "these",
    "this",
    "those",
    "with",
    "would",
    "your",
}
RECOMMENDATION_RE = re.compile(
    r"\b(recommend|choose|select|prefer|best|better|rank|eliminate|safest|"
    r"should|would pick|final answer|tentative)\b",
    re.IGNORECASE,
)


def content_tokens(text: str) -> set[str]:
    return {
        token
        for token in TOKEN_RE.findall(text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def token_overlap_ratio(needle: str, haystack: str) -> float:
    needle_tokens = content_tokens(needle)
    if not needle_tokens:
        return 0.0
    return len(needle_tokens & content_tokens(haystack)) / len(needle_tokens)


def fact_is_covered(message: str, fact: str, *, threshold: float = 0.75) -> bool:
    fact_norm = normalize_answer(fact)
    message_norm = normalize_answer(message)
    if fact_norm and fact_norm in message_norm:
        return True
    return token_overlap_ratio(fact, message) >= threshold


def mentioned_choices(message: str, choices: Sequence[str]) -> List[str]:
    message_norm = normalize_answer(message)
    found = []
    for choice in choices:
        choice_norm = normalize_answer(choice)
        prefix_norm = normalize_answer(choice.split(":", 1)[0].strip()) if ":" in choice else ""
        if choice_norm and re.search(rf"\b{re.escape(choice_norm)}\b", message_norm):
            found.append(choice)
        elif prefix_norm and re.search(rf"\b{re.escape(prefix_norm)}\b", message_norm):
            found.append(choice)
    return sorted(set(found))


def audit_public_messages(
    task: Mapping[str, Any],
    messages: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    hidden_by_agent = {
        index: fact for index, fact in enumerate(task.get("hidden_information") or [], start=1)
    }
    per_message = []
    for message in messages:
        agent_index = int(message.get("agent_index") or 0)
        text = str(message.get("message") or "")
        private_fact = str(message.get("private_fact") or hidden_by_agent.get(agent_index, ""))
        private_fact_norm = normalize_answer(private_fact)
        message_norm = normalize_answer(text)
        private_exact = bool(private_fact_norm and private_fact_norm in message_norm)
        shared_mentions = [
            fact for fact in task.get("shared_information") or [] if fact_is_covered(text, str(fact))
        ]
        answer_mentions = mentioned_choices(text, task.get("possible_answers") or [])
        private_overlap = token_overlap_ratio(private_fact, text)
        per_message.append(
            {
                "agent_index": agent_index,
                "message_chars": len(text),
                "private_fact_exact": private_exact,
                "private_fact_token_overlap": round(private_overlap, 3),
                "recommendation_leakage": bool(RECOMMENDATION_RE.search(text)),
                "shared_fact_overtalk": bool(shared_mentions),
                "shared_fact_mentions": shared_mentions,
                "possible_answer_mentions": answer_mentions,
                "possible_answer_mention_count": len(answer_mentions),
                "low_private_overlap_proxy": private_overlap < 0.25 and not private_exact,
            }
        )

    total_messages = len(per_message)
    return {
        "messages": per_message,
        "aggregate": {
            "messages": total_messages,
            "private_fact_exact_count": sum(1 for row in per_message if row["private_fact_exact"]),
            "recommendation_leakage_count": sum(1 for row in per_message if row["recommendation_leakage"]),
            "shared_fact_overtalk_count": sum(1 for row in per_message if row["shared_fact_overtalk"]),
            "possible_answer_mention_count": sum(
                1 for row in per_message if row["possible_answer_mention_count"]
            ),
            "low_private_overlap_proxy_count": sum(
                1 for row in per_message if row["low_private_overlap_proxy"]
            ),
            "avg_private_fact_token_overlap": round(
                sum(row["private_fact_token_overlap"] for row in per_message) / total_messages,
                3,
            )
            if total_messages
            else None,
        },
    }


def score_record(
    *,
    run_id: str,
    model: str,
    task: Mapping[str, Any],
    condition: str,
    prompt: str,
    output: str,
    usage: Mapping[str, Any],
    latency_seconds: float,
    agent_index: Optional[int] = None,
    exchange_messages: Optional[Sequence[Mapping[str, Any]]] = None,
    include_prompt: bool = False,
) -> Dict[str, Any]:
    parsed, parse_source = parse_choice(output, task["possible_answers"])
    gold = task["correct_answer"]
    message_audit = audit_public_messages(task, exchange_messages) if exchange_messages else None
    return {
        "run_id": run_id,
        "model": model,
        "benchmark": "HiddenBench",
        "task_id": task["id"],
        "task_name": task["name"],
        "condition": condition,
        "agent_index": agent_index,
        "gold_answer": gold,
        "parsed_answer": parsed,
        "correct": normalize_answer(parsed) == normalize_answer(gold) if parsed is not None else False,
        "parse_source": parse_source,
        "possible_answers": task["possible_answers"],
        "output": output.strip(),
        "usage": dict(usage),
        "latency_seconds": round(latency_seconds, 3),
        "exchange_messages": list(exchange_messages) if exchange_messages else None,
        "message_audit": message_audit,
        "prompt": prompt if include_prompt else None,
    }


def run_call(
    *,
    args: argparse.Namespace,
    prompt: str,
) -> Tuple[str, Dict[str, Any], float]:
    started = time.time()
    output, usage = chat_completion(
        base_url=args.base_url,
        model=args.model,
        api_key=args.api_key,
        prompt=prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.request_timeout,
    )
    return output, usage, time.time() - started


def selected_tasks(tasks: Sequence[Mapping[str, Any]], args: argparse.Namespace) -> List[Mapping[str, Any]]:
    rows = list(tasks)
    if args.task_ids:
        allowed = {int(task_id) for task_id in args.task_ids}
        rows = [task for task in rows if int(task["id"]) in allowed]
    if args.limit is not None:
        rows = rows[: args.limit]
    return rows


PAIRED_CONDITION_PAIRS = [
    ("full_info", "shared_only"),
    ("oracle_public_facts", "shared_only"),
    ("oracle_public_facts", "exchange_then_decide"),
    ("no_recommendation_exchange", "exchange_then_decide"),
    ("no_shared_repeat_exchange", "exchange_then_decide"),
    ("fact_only_exchange", "no_recommendation_exchange"),
    ("fact_only_exchange", "no_shared_repeat_exchange"),
    ("oracle_public_facts", "fact_only_exchange"),
    ("fact_only_exchange", "fact_only_with_options_exchange"),
    ("blind_exchange", "exchange_then_decide"),
    ("blind_minimal_exchange", "exchange_then_decide"),
    ("blind_minimal_exchange", "private_plus_task_minimal_exchange"),
    ("blind_minimal_exchange", "private_plus_options_minimal_exchange"),
    ("blind_minimal_exchange", "private_plus_shared_minimal_exchange"),
    ("blind_minimal_exchange", "full_visibility_minimal_exchange"),
    ("fact_only_exchange", "blind_exchange"),
    ("fact_only_exchange", "blind_minimal_exchange"),
    ("fact_only_exchange", "full_visibility_minimal_exchange"),
    ("blind_minimal_exchange", "blind_exchange"),
    ("full_visibility_minimal_exchange", "exchange_then_decide"),
    ("fact_only_exchange", "exchange_then_decide"),
    ("fact_only_constraint_decide", "fact_only_exchange"),
    ("fact_only_constraint_decide", "exchange_then_decide"),
    ("full_info", "fact_only_constraint_decide"),
]


def paired_contrasts(records: Sequence[Mapping[str, Any]], *, correctness_key: str = "correct") -> Dict[str, Any]:
    by_task: Dict[int, Dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in records:
        condition = str(row.get("condition"))
        if condition != "single_private_agent":
            by_task[int(row["task_id"])][condition] = row

    out = {}
    for left, right in PAIRED_CONDITION_PAIRS:
        paired = [task_rows for task_rows in by_task.values() if left in task_rows and right in task_rows]
        if not paired:
            continue
        left_correct_right_wrong = sum(
            1 for task_rows in paired if task_rows[left].get(correctness_key) and not task_rows[right].get(correctness_key)
        )
        right_correct_left_wrong = sum(
            1 for task_rows in paired if task_rows[right].get(correctness_key) and not task_rows[left].get(correctness_key)
        )
        both_correct = sum(
            1 for task_rows in paired if task_rows[left].get(correctness_key) and task_rows[right].get(correctness_key)
        )
        out[f"{left}_vs_{right}"] = {
            "paired_tasks": len(paired),
            "left_correct_right_wrong": left_correct_right_wrong,
            "right_correct_left_wrong": right_correct_left_wrong,
            "both_correct": both_correct,
            "both_wrong": len(paired) - left_correct_right_wrong - right_correct_left_wrong - both_correct,
        }
    return out


def message_audit_summary(records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    totals: Dict[str, Counter] = defaultdict(Counter)
    overlap_sums: Dict[str, float] = defaultdict(float)
    for row in records:
        audit = row.get("message_audit") or {}
        aggregate = audit.get("aggregate") or {}
        if not aggregate:
            continue
        condition = str(row.get("condition"))
        message_count = int(aggregate.get("messages") or 0)
        totals[condition]["records"] += 1
        totals[condition]["messages"] += message_count
        totals[condition]["private_fact_exact_count"] += int(aggregate.get("private_fact_exact_count") or 0)
        totals[condition]["recommendation_leakage_count"] += int(aggregate.get("recommendation_leakage_count") or 0)
        totals[condition]["shared_fact_overtalk_count"] += int(aggregate.get("shared_fact_overtalk_count") or 0)
        totals[condition]["possible_answer_mention_count"] += int(aggregate.get("possible_answer_mention_count") or 0)
        totals[condition]["low_private_overlap_proxy_count"] += int(
            aggregate.get("low_private_overlap_proxy_count") or 0
        )
        avg_overlap = aggregate.get("avg_private_fact_token_overlap")
        if avg_overlap is not None:
            overlap_sums[condition] += float(avg_overlap) * message_count

    out = {}
    for condition, counter in sorted(totals.items()):
        messages = counter["messages"]
        out[condition] = {
            **dict(counter),
            "private_fact_exact_rate": counter["private_fact_exact_count"] / messages if messages else None,
            "recommendation_leakage_rate": counter["recommendation_leakage_count"] / messages if messages else None,
            "shared_fact_overtalk_rate": counter["shared_fact_overtalk_count"] / messages if messages else None,
            "possible_answer_mention_rate": counter["possible_answer_mention_count"] / messages if messages else None,
            "low_private_overlap_proxy_rate": counter["low_private_overlap_proxy_count"] / messages if messages else None,
            "avg_private_fact_token_overlap": round(overlap_sums[condition] / messages, 3) if messages else None,
        }
    return out


def summarize(records: Sequence[Mapping[str, Any]], tasks: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    by_condition: Dict[str, Counter] = defaultdict(Counter)
    by_task: Dict[Tuple[int, str], List[Mapping[str, Any]]] = defaultdict(list)
    for row in records:
        condition = str(row["condition"])
        by_condition[condition]["records"] += 1
        if row.get("correct"):
            by_condition[condition]["correct"] += 1
        if row.get("parse_source") == "unparsed":
            by_condition[condition]["unparsed"] += 1
        by_task[(int(row["task_id"]), condition)].append(row)

    condition_summary = {}
    for condition, counter in sorted(by_condition.items()):
        records_count = counter["records"]
        condition_summary[condition] = {
            **dict(counter),
            "accuracy": counter["correct"] / records_count if records_count else None,
        }

    private_by_task = {}
    for task in tasks:
        private_rows = by_task.get((int(task["id"]), "single_private_agent"), [])
        if not private_rows:
            continue
        votes = Counter(str(row.get("parsed_answer")) for row in private_rows if row.get("parsed_answer"))
        majority_answer = votes.most_common(1)[0][0] if votes else None
        private_by_task[str(task["id"])] = {
            "task_name": task["name"],
            "gold_answer": task["correct_answer"],
            "private_agent_records": len(private_rows),
            "private_any_correct": any(row.get("correct") for row in private_rows),
            "private_all_correct": all(row.get("correct") for row in private_rows),
            "private_majority_answer": majority_answer,
            "private_majority_correct": normalize_answer(majority_answer) == normalize_answer(task["correct_answer"])
            if majority_answer is not None
            else False,
        }

    if private_by_task:
        private_task_values = list(private_by_task.values())
        condition_summary["single_private_task_any"] = {
            "records": len(private_task_values),
            "correct": sum(1 for row in private_task_values if row["private_any_correct"]),
            "accuracy": sum(1 for row in private_task_values if row["private_any_correct"]) / len(private_task_values),
        }
        condition_summary["single_private_task_majority"] = {
            "records": len(private_task_values),
            "correct": sum(1 for row in private_task_values if row["private_majority_correct"]),
            "accuracy": sum(1 for row in private_task_values if row["private_majority_correct"]) / len(private_task_values),
        }

    return {
        "benchmark": "HiddenBench",
        "num_tasks": len(tasks),
        "num_records": len(records),
        "conditions": condition_summary,
        "private_by_task": private_by_task,
        "paired_contrasts": paired_contrasts(records),
        "message_audit": message_audit_summary(records),
    }


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# HiddenBench Communication Necessity Probe",
        "",
        f"- Tasks: `{summary['num_tasks']}`",
        f"- Records: `{summary['num_records']}`",
        "",
        "| Condition | Records | Correct | Accuracy | Unparsed |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for condition, row in summary["conditions"].items():
        accuracy = row.get("accuracy")
        accuracy_text = "n/a" if accuracy is None else f"{accuracy:.3f}"
        lines.append(
            f"| {condition} | {row.get('records', 0)} | {row.get('correct', 0)} | "
            f"{accuracy_text} | {row.get('unparsed', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Readout Contract",
            "",
            "- `shared_only` estimates the no-private-information floor.",
            "- `single_private_agent` estimates individual partial-information behavior.",
            "- `oracle_public_facts` gives the final model all private facts as clean public messages.",
            "- `full_info` gives the final model all facts directly.",
            "- `exchange_then_decide` first asks partial agents to emit public messages, then asks a final model to decide from those messages.",
            "- `no_recommendation_exchange` keeps the old sender context but forbids answer recommendations and option ranking.",
            "- `no_shared_repeat_exchange` keeps recommendations allowed but forbids repeating shared information.",
            "- `fact_only_exchange` uses the same final decision prompt as exchange, but agents may only report their private fact.",
            "- `fact_only_with_options_exchange` is fact-only while explicitly showing the possible answer list to senders.",
            "- `blind_exchange` hides task description, shared facts, and answer options from senders; agents only report one local observation.",
            "- `blind_minimal_exchange` uses the same blind sender visibility but asks for a minimal observation-note format.",
            "- `private_plus_task_minimal_exchange` shows senders the task but keeps the minimal observation-note format.",
            "- `private_plus_options_minimal_exchange` shows senders the answer options but keeps the minimal observation-note format.",
            "- `private_plus_shared_minimal_exchange` shows senders shared facts but keeps the minimal observation-note format.",
            "- `full_visibility_minimal_exchange` shows senders task, shared facts, and options while keeping the minimal observation-note format.",
            "- `fact_only_constraint_decide` reuses the fact-only messages and changes only the final integration prompt.",
            "",
            "A communication-necessity signal requires a clear gap from partial-information conditions to full/public-fact conditions. "
            "An exchange protocol is useful only if it closes part of that gap without simply revealing hidden gold labels.",
            "",
        ]
    )
    if summary.get("paired_contrasts"):
        lines.extend(["## Paired Contrasts", ""])
        for key, row in summary["paired_contrasts"].items():
            lines.append(
                f"- `{key}`: paired `{row['paired_tasks']}`, left-only `{row['left_correct_right_wrong']}`, "
                f"right-only `{row['right_correct_left_wrong']}`, both-correct `{row['both_correct']}`, "
                f"both-wrong `{row['both_wrong']}`"
            )
        lines.append("")
    if summary.get("message_audit"):
        lines.extend(
            [
                "## Public Message Audit",
                "",
                "| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for condition, row in summary["message_audit"].items():
            overlap = row.get("avg_private_fact_token_overlap")
            lines.append(
                f"| {condition} | {row.get('messages', 0)} | {row.get('private_fact_exact_count', 0)} | "
                f"{row.get('recommendation_leakage_count', 0)} | {row.get('shared_fact_overtalk_count', 0)} | "
                f"{row.get('possible_answer_mention_count', 0)} | "
                f"{'n/a' if overlap is None else f'{overlap:.3f}'} |"
            )
        lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> Dict[str, Any]:
    tasks = selected_tasks(load_json(args.benchmark), args)
    if not tasks:
        raise SystemExit("No HiddenBench tasks selected.")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    records_path = args.out_dir / "records.jsonl"
    failures_path = args.out_dir / "failures.jsonl"
    records: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []

    def emit_record(record: Dict[str, Any]) -> None:
        records.append(record)
        append_jsonl(records_path, [record])

    def collect_agent_messages(task: Mapping[str, Any], prompt_builder: Any) -> List[Dict[str, Any]]:
        messages = []
        for agent_index, private_fact in enumerate(task["hidden_information"], start=1):
            prompt = prompt_builder(task, private_fact=private_fact, agent_index=agent_index)
            output, usage, latency = run_call(args=args, prompt=prompt)
            messages.append(
                {
                    "agent_index": agent_index,
                    "private_fact": private_fact,
                    "message": output.strip(),
                    "usage": dict(usage),
                    "latency_seconds": round(latency, 3),
                }
            )
        return messages

    for task_index, task in enumerate(tasks, start=1):
        try:
            if "shared_only" in args.conditions:
                prompt = answer_prompt(
                    task,
                    visible_facts=[],
                    condition_note="You only see shared information. If private facts are missing, still choose the best option from the visible evidence.",
                )
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="shared_only",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        include_prompt=args.include_prompts,
                    )
                )

            if "single_private_agent" in args.conditions:
                for agent_index, private_fact in enumerate(task["hidden_information"], start=1):
                    prompt = answer_prompt(
                        task,
                        visible_facts=[private_fact],
                        condition_note="You are one participant with exactly one private fact. Choose from your partial evidence.",
                    )
                    output, usage, latency = run_call(args=args, prompt=prompt)
                    emit_record(
                        score_record(
                            run_id=args.run_id,
                            model=args.model,
                            task=task,
                            condition="single_private_agent",
                            prompt=prompt,
                            output=output,
                            usage=usage,
                            latency_seconds=latency,
                            agent_index=agent_index,
                            include_prompt=args.include_prompts,
                        )
                    )

            if "oracle_public_facts" in args.conditions:
                prompt = oracle_public_facts_prompt(task)
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="oracle_public_facts",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        include_prompt=args.include_prompts,
                    )
                )

            if "full_info" in args.conditions:
                prompt = answer_prompt(
                    task,
                    visible_facts=task["hidden_information"],
                    condition_note="You see all shared and private facts. Choose the best supported option.",
                )
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="full_info",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        include_prompt=args.include_prompts,
                    )
                )

            if "exchange_then_decide" in args.conditions:
                messages = collect_agent_messages(task, agent_message_prompt)
                prompt = exchange_decide_prompt(task, messages=messages)
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="exchange_then_decide",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        exchange_messages=messages,
                        include_prompt=args.include_prompts,
                    )
                )

            if "no_recommendation_exchange" in args.conditions:
                messages = collect_agent_messages(task, no_recommendation_agent_message_prompt)
                prompt = exchange_decide_prompt(task, messages=messages)
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="no_recommendation_exchange",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        exchange_messages=messages,
                        include_prompt=args.include_prompts,
                    )
                )

            if "no_shared_repeat_exchange" in args.conditions:
                messages = collect_agent_messages(task, no_shared_repeat_agent_message_prompt)
                prompt = exchange_decide_prompt(task, messages=messages)
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="no_shared_repeat_exchange",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        exchange_messages=messages,
                        include_prompt=args.include_prompts,
                    )
                )

            if "fact_only_with_options_exchange" in args.conditions:
                messages = collect_agent_messages(task, fact_only_with_options_agent_message_prompt)
                prompt = exchange_decide_prompt(task, messages=messages)
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="fact_only_with_options_exchange",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        exchange_messages=messages,
                        include_prompt=args.include_prompts,
                    )
                )

            if "blind_exchange" in args.conditions:
                messages = collect_agent_messages(task, blind_agent_message_prompt)
                prompt = exchange_decide_prompt(task, messages=messages)
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="blind_exchange",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        exchange_messages=messages,
                        include_prompt=args.include_prompts,
                    )
                )

            if "blind_minimal_exchange" in args.conditions:
                messages = collect_agent_messages(task, blind_minimal_agent_message_prompt)
                prompt = exchange_decide_prompt(task, messages=messages)
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="blind_minimal_exchange",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        exchange_messages=messages,
                        include_prompt=args.include_prompts,
                    )
                )

            if "private_plus_task_minimal_exchange" in args.conditions:
                messages = collect_agent_messages(task, private_plus_task_minimal_agent_message_prompt)
                prompt = exchange_decide_prompt(task, messages=messages)
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="private_plus_task_minimal_exchange",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        exchange_messages=messages,
                        include_prompt=args.include_prompts,
                    )
                )

            if "private_plus_options_minimal_exchange" in args.conditions:
                messages = collect_agent_messages(task, private_plus_options_minimal_agent_message_prompt)
                prompt = exchange_decide_prompt(task, messages=messages)
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="private_plus_options_minimal_exchange",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        exchange_messages=messages,
                        include_prompt=args.include_prompts,
                    )
                )

            if "private_plus_shared_minimal_exchange" in args.conditions:
                messages = collect_agent_messages(task, private_plus_shared_minimal_agent_message_prompt)
                prompt = exchange_decide_prompt(task, messages=messages)
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="private_plus_shared_minimal_exchange",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        exchange_messages=messages,
                        include_prompt=args.include_prompts,
                    )
                )

            if "full_visibility_minimal_exchange" in args.conditions:
                messages = collect_agent_messages(task, full_visibility_minimal_agent_message_prompt)
                prompt = exchange_decide_prompt(task, messages=messages)
                output, usage, latency = run_call(args=args, prompt=prompt)
                emit_record(
                    score_record(
                        run_id=args.run_id,
                        model=args.model,
                        task=task,
                        condition="full_visibility_minimal_exchange",
                        prompt=prompt,
                        output=output,
                        usage=usage,
                        latency_seconds=latency,
                        exchange_messages=messages,
                        include_prompt=args.include_prompts,
                    )
                )

            if "fact_only_exchange" in args.conditions or "fact_only_constraint_decide" in args.conditions:
                fact_only_messages = collect_agent_messages(task, fact_only_agent_message_prompt)

                if "fact_only_exchange" in args.conditions:
                    prompt = exchange_decide_prompt(task, messages=fact_only_messages)
                    output, usage, latency = run_call(args=args, prompt=prompt)
                    emit_record(
                        score_record(
                            run_id=args.run_id,
                            model=args.model,
                            task=task,
                            condition="fact_only_exchange",
                            prompt=prompt,
                            output=output,
                            usage=usage,
                            latency_seconds=latency,
                            exchange_messages=fact_only_messages,
                            include_prompt=args.include_prompts,
                        )
                    )

                if "fact_only_constraint_decide" in args.conditions:
                    prompt = constraint_decide_prompt(task, messages=fact_only_messages)
                    output, usage, latency = run_call(args=args, prompt=prompt)
                    emit_record(
                        score_record(
                            run_id=args.run_id,
                            model=args.model,
                            task=task,
                            condition="fact_only_constraint_decide",
                            prompt=prompt,
                            output=output,
                            usage=usage,
                            latency_seconds=latency,
                            exchange_messages=fact_only_messages,
                            include_prompt=args.include_prompts,
                        )
                    )

        except Exception as exc:  # noqa: BLE001 - preserve endpoint failure detail.
            failure = {
                "run_id": args.run_id,
                "task_id": task.get("id"),
                "task_name": task.get("name"),
                "task_index": task_index,
                "error": str(exc),
            }
            failures.append(failure)
            append_jsonl(failures_path, [failure])
            if not args.keep_going:
                break

        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)
        if args.progress_every and task_index % args.progress_every == 0:
            print(json.dumps({"seen_tasks": task_index, "records": len(records), "failures": len(failures)}))

    write_jsonl(records_path, records)
    if failures:
        write_jsonl(failures_path, failures)
    summary = summarize(records, tasks)
    summary.update(
        {
            "run_id": args.run_id,
            "model": args.model,
            "benchmark_path": str(args.benchmark),
            "conditions_requested": args.conditions,
            "failures": len(failures),
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
    )
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "summary.md", render_markdown(summary))
    manifest = {
        "run_id": args.run_id,
        "status": "completed" if not failures else "completed_with_failures",
        "benchmark": "HiddenBench",
        "benchmark_path": str(args.benchmark),
        "model": args.model,
        "base_url": args.base_url,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "request_timeout": args.request_timeout,
        "num_tasks": len(tasks),
        "conditions": args.conditions,
        "outputs": str(records_path),
        "summary": str(args.out_dir / "summary.json"),
        "failures": str(failures_path) if failures else None,
        "claim_status": "preflight" if args.limit and args.limit < 65 else "benchmark_probe",
        "caveats": [
            "This runner uses HiddenBench tasks but implements a local protocol rather than the official group-interaction harness.",
            "single_private_agent rows are partial-information probes, not independent human-like participants.",
            "exchange_then_decide can fail either because agents omit private facts or because the final decider misintegrates public messages.",
            "fact_only_constraint_decide reuses fact_only_exchange messages, so the paired contrast isolates final integration prompt effects.",
            "Stage 2 sender-ablation conditions isolate recommendation leakage, shared-fact repetition, and answer-option visibility in sender prompts.",
            "Stage 3 blind-sender conditions remove task description, shared facts, and answer options from sender prompts to test whether reduced sender task visibility improves public messages.",
            "Stage 4 sender-visibility-matrix conditions keep a minimal observation-note output format while varying task, shared-fact, answer-option, and full sender visibility.",
            "Public-message audit fields are automatic proxies; invented facts still require manual case inspection before becoming claims.",
        ],
    }
    write_json(args.out_dir / "manifest.json", manifest)
    write_text(args.out_dir / "README.md", render_run_readme(summary, manifest))
    return summary


def render_run_readme(summary: Mapping[str, Any], manifest: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# HiddenBench Communication Necessity Probe",
            "",
            "## Purpose",
            "",
            "This run tests whether the benchmark supplies external pressure for genuine communication necessity: individual agents see only partial private information, while public-fact and full-information conditions expose the information needed for the correct decision.",
            "",
            "## Status",
            "",
            f"- Run id: `{manifest['run_id']}`",
            f"- Status: `{manifest['status']}`",
            f"- Claim status: `{manifest['claim_status']}`",
            f"- Tasks: `{summary['num_tasks']}`",
            f"- Records: `{summary['num_records']}`",
            "",
            "## Primary Contrast",
            "",
            "`shared_only` and `single_private_agent` are the partial-information floor. `oracle_public_facts` and `full_info` test whether the task is solvable when private facts are surfaced. Exchange variants separate recommendation leakage, shared-fact repetition, private-fact reporting, answer-option visibility, and final integration.",
            "",
            "## Summary",
            "",
            render_markdown(summary),
            "",
            "## Caveats",
            "",
            *[f"- {caveat}" for caveat in manifest["caveats"]],
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", "EMPTY"))
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=220)
    parser.add_argument("--request-timeout", type=int, default=180)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--task-ids", nargs="*")
    parser.add_argument(
        "--conditions",
        nargs="+",
        default=[
            "shared_only",
            "single_private_agent",
            "oracle_public_facts",
            "full_info",
            "exchange_then_decide",
        ],
        choices=[
            "shared_only",
            "single_private_agent",
            "oracle_public_facts",
            "full_info",
            "exchange_then_decide",
            "no_recommendation_exchange",
            "no_shared_repeat_exchange",
            "fact_only_with_options_exchange",
            "blind_exchange",
            "blind_minimal_exchange",
            "private_plus_task_minimal_exchange",
            "private_plus_options_minimal_exchange",
            "private_plus_shared_minimal_exchange",
            "full_visibility_minimal_exchange",
            "fact_only_exchange",
            "fact_only_constraint_decide",
        ],
    )
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument("--include-prompts", action="store_true")
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--progress-every", type=int, default=5)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.run_id is None:
        safe_model = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in args.model)
        args.run_id = datetime.now().strftime(f"%Y%m%d-%H%M-a8002-hiddenbench-{safe_model}")
    if args.out_dir is None:
        args.out_dir = DEFAULT_OUT_ROOT / args.run_id
    summary = run(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
