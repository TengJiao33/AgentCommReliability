#!/usr/bin/env python3
"""Re-score HiddenBench probe records and compute paired contrasts."""

from __future__ import annotations

import argparse
import json
import re
import string
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as f:
        return [json.loads(line) for line in f if line.strip()]


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


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize_answer(value: Optional[str]) -> str:
    if value is None:
        return ""
    text = str(value).lower()
    text = "".join(ch for ch in text if ch not in set(string.punctuation))
    return " ".join(text.split())


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


def parse_choice(output: str, choices: Sequence[str]) -> Tuple[Optional[str], str]:
    answer_match = re.search(r"(?im)^\s*answer\s*:\s*(.+?)\s*$", output)
    candidates = [answer_match.group(1).strip()] if answer_match else []
    if output.strip():
        candidates.append(output.strip().splitlines()[-1].strip())

    exact = {normalize_answer(choice): choice for choice in choices}
    prefixes: Dict[str, List[str]] = defaultdict(list)
    for choice in choices:
        if ":" in choice:
            prefixes[normalize_answer(choice.split(":", 1)[0].strip())].append(choice)

    for candidate in candidates:
        candidate_norm = normalize_answer(candidate)
        if candidate_norm in exact:
            return exact[candidate_norm], "answer_line_exact"
        if len(prefixes.get(candidate_norm, [])) == 1:
            return prefixes[candidate_norm][0], "answer_line_unique_prefix"

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


def summarize_condition(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    correct = sum(1 for row in rows if row.get("rescored_correct"))
    unparsed = sum(1 for row in rows if row.get("rescored_parse_source") == "unparsed")
    return {
        "records": total,
        "correct": correct,
        "accuracy": correct / total if total else None,
        "unparsed": unparsed,
    }


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


def paired_contrasts(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    by_task: Dict[int, Dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in rows:
        condition = str(row.get("condition"))
        if condition != "single_private_agent":
            by_task[int(row["task_id"])][condition] = row

    out = {}
    for left, right in PAIRED_CONDITION_PAIRS:
        paired = [task_rows for task_rows in by_task.values() if left in task_rows and right in task_rows]
        if not paired:
            continue
        left_correct_right_wrong = sum(
            1
            for task_rows in paired
            if task_rows[left].get("rescored_correct") and not task_rows[right].get("rescored_correct")
        )
        right_correct_left_wrong = sum(
            1
            for task_rows in paired
            if task_rows[right].get("rescored_correct") and not task_rows[left].get("rescored_correct")
        )
        both_correct = sum(
            1
            for task_rows in paired
            if task_rows[left].get("rescored_correct") and task_rows[right].get("rescored_correct")
        )
        out[f"{left}_vs_{right}"] = {
            "paired_tasks": len(paired),
            "left_correct_right_wrong": left_correct_right_wrong,
            "right_correct_left_wrong": right_correct_left_wrong,
            "both_correct": both_correct,
            "both_wrong": len(paired) - left_correct_right_wrong - right_correct_left_wrong - both_correct,
        }
    return out


def fallback_message_audit(row: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    messages = row.get("exchange_messages") or []
    if not messages:
        return None
    per_message = []
    choices = row.get("possible_answers") or []
    for message in messages:
        text = str(message.get("message") or "")
        private_fact = str(message.get("private_fact") or "")
        private_fact_norm = normalize_answer(private_fact)
        message_norm = normalize_answer(text)
        private_exact = bool(private_fact_norm and private_fact_norm in message_norm)
        answer_mentions = mentioned_choices(text, choices)
        private_overlap = token_overlap_ratio(private_fact, text)
        per_message.append(
            {
                "agent_index": message.get("agent_index"),
                "message_chars": len(text),
                "private_fact_exact": private_exact,
                "private_fact_token_overlap": round(private_overlap, 3),
                "recommendation_leakage": bool(RECOMMENDATION_RE.search(text)),
                "shared_fact_overtalk": None,
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
            "private_fact_exact_count": sum(1 for item in per_message if item["private_fact_exact"]),
            "recommendation_leakage_count": sum(1 for item in per_message if item["recommendation_leakage"]),
            "shared_fact_overtalk_count": None,
            "possible_answer_mention_count": sum(1 for item in per_message if item["possible_answer_mention_count"]),
            "low_private_overlap_proxy_count": sum(1 for item in per_message if item["low_private_overlap_proxy"]),
            "avg_private_fact_token_overlap": round(
                sum(item["private_fact_token_overlap"] for item in per_message) / total_messages,
                3,
            )
            if total_messages
            else None,
        },
    }


def message_audit_summary(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    totals: Dict[str, Counter] = defaultdict(Counter)
    overlap_sums: Dict[str, float] = defaultdict(float)
    has_shared_overtalk: Dict[str, bool] = defaultdict(bool)
    for row in rows:
        audit = row.get("message_audit") or fallback_message_audit(row) or {}
        aggregate = audit.get("aggregate") or {}
        if not aggregate:
            continue
        condition = str(row.get("condition"))
        message_count = int(aggregate.get("messages") or 0)
        totals[condition]["records"] += 1
        totals[condition]["messages"] += message_count
        totals[condition]["private_fact_exact_count"] += int(aggregate.get("private_fact_exact_count") or 0)
        totals[condition]["recommendation_leakage_count"] += int(aggregate.get("recommendation_leakage_count") or 0)
        if aggregate.get("shared_fact_overtalk_count") is not None:
            has_shared_overtalk[condition] = True
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
        shared_count = counter["shared_fact_overtalk_count"] if has_shared_overtalk[condition] else None
        out[condition] = {
            **dict(counter),
            "shared_fact_overtalk_count": shared_count,
            "private_fact_exact_rate": counter["private_fact_exact_count"] / messages if messages else None,
            "recommendation_leakage_rate": counter["recommendation_leakage_count"] / messages if messages else None,
            "shared_fact_overtalk_rate": shared_count / messages if messages and shared_count is not None else None,
            "possible_answer_mention_rate": counter["possible_answer_mention_count"] / messages if messages else None,
            "low_private_overlap_proxy_rate": counter["low_private_overlap_proxy_count"] / messages if messages else None,
            "avg_private_fact_token_overlap": round(overlap_sums[condition] / messages, 3) if messages else None,
        }
    return out


def build(args: argparse.Namespace) -> Dict[str, Any]:
    rows = load_jsonl(args.records)
    rescored = []
    changes = []
    for row in rows:
        parsed, parse_source = parse_choice(str(row.get("output") or ""), row.get("possible_answers") or [])
        correct = normalize_answer(parsed) == normalize_answer(row.get("gold_answer")) if parsed is not None else False
        updated = dict(row)
        updated["rescored_answer"] = parsed
        updated["rescored_correct"] = correct
        updated["rescored_parse_source"] = parse_source
        if updated.get("message_audit") is None:
            updated["message_audit"] = fallback_message_audit(updated)
        if parsed != row.get("parsed_answer") or correct != row.get("correct"):
            changes.append({
                "task_id": row.get("task_id"),
                "task_name": row.get("task_name"),
                "condition": row.get("condition"),
                "old_answer": row.get("parsed_answer"),
                "new_answer": parsed,
                "old_correct": row.get("correct"),
                "new_correct": correct,
                "parse_source": parse_source,
            })
        rescored.append(updated)

    by_condition: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for row in rescored:
        by_condition[str(row["condition"])].append(row)
    summary = {
        "records": str(args.records),
        "num_records": len(rescored),
        "conditions": {
            condition: summarize_condition(condition_rows)
            for condition, condition_rows in sorted(by_condition.items())
        },
        "paired_contrasts": paired_contrasts(rescored),
        "message_audit": message_audit_summary(rescored),
        "rescoring_changes": changes,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "corrected_summary.json", summary)
    write_jsonl(args.out_dir / "corrected_records.jsonl", rescored)
    write_text(args.out_dir / "corrected_summary.md", render_markdown(summary))
    return summary


def render_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# HiddenBench Corrected Summary",
        "",
        f"- Records: `{summary['num_records']}`",
        f"- Rescoring changes: `{len(summary['rescoring_changes'])}`",
        "",
        "| Condition | Records | Correct | Accuracy | Unparsed |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for condition, row in summary["conditions"].items():
        accuracy = row["accuracy"]
        lines.append(
            f"| {condition} | {row['records']} | {row['correct']} | "
            f"{accuracy:.3f} | {row['unparsed']} |"
        )
    lines.extend(["", "## Paired Contrasts", ""])
    for key, row in summary["paired_contrasts"].items():
        lines.append(
            f"- `{key}`: paired `{row['paired_tasks']}`, left-only `{row['left_correct_right_wrong']}`, "
            f"right-only `{row['right_correct_left_wrong']}`, both-correct `{row['both_correct']}`, "
            f"both-wrong `{row['both_wrong']}`"
        )
    if summary.get("message_audit"):
        lines.extend(
            [
                "",
                "## Public Message Audit",
                "",
                "| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for condition, row in summary["message_audit"].items():
            overlap = row.get("avg_private_fact_token_overlap")
            shared_overtalk = row.get("shared_fact_overtalk_count")
            lines.append(
                f"| {condition} | {row.get('messages', 0)} | {row.get('private_fact_exact_count', 0)} | "
                f"{row.get('recommendation_leakage_count', 0)} | "
                f"{'n/a' if shared_overtalk is None else shared_overtalk} | "
                f"{row.get('possible_answer_mention_count', 0)} | "
                f"{'n/a' if overlap is None else f'{overlap:.3f}'} |"
            )
    if summary["rescoring_changes"]:
        lines.extend(["", "## Rescoring Changes", ""])
        for row in summary["rescoring_changes"]:
            lines.append(
                f"- task `{row['task_id']}` `{row['condition']}`: "
                f"`{row['old_answer']}` -> `{row['new_answer']}`, correct `{row['old_correct']}` -> `{row['new_correct']}`"
            )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
