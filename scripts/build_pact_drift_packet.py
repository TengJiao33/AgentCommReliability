#!/usr/bin/env python3
"""Build a compact paired-run drift packet for one PACT sample."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


FIELD_KEYS = ("action_required", "environment_state", "action_result", "final_answer")
NUMBER_RE = re.compile(r"(?<![A-Za-z0-9])(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?![A-Za-z0-9])")
PARAGRAPH_RE = re.compile(r"(?ms)^\[([^\]]+)\]\r?\n(.*?)(?=^\[[^\]]+\]\r?\n|^## Conversation|\Z)")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def find_sample(rows: Iterable[Dict[str, Any]], sample_index: int) -> Optional[Dict[str, Any]]:
    for row in rows:
        if row.get("sample_index") == sample_index:
            return row
    return None


def normalize(text: Any) -> str:
    text = "" if text is None else str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def numeric_mentions(text: Any) -> List[str]:
    seen = set()
    out = []
    for match in NUMBER_RE.findall("" if text is None else str(text)):
        if match not in seen:
            out.append(match)
            seen.add(match)
    return out


def digits_only(text: Any) -> str:
    return re.sub(r"\D+", "", "" if text is None else str(text))


def term_variants(*values: Any) -> List[str]:
    terms = []
    seen = set()
    for value in values:
        if value is None:
            continue
        raw = str(value).strip()
        if not raw:
            continue
        candidates = [raw]
        digits = digits_only(raw)
        if digits:
            candidates.append(digits)
            if len(digits) > 3:
                candidates.append(f"{int(digits):,}")
        for candidate in candidates:
            key = candidate.lower()
            if key not in seen:
                terms.append(candidate)
                seen.add(key)
    return terms


def compact_event(event: Dict[str, Any]) -> Dict[str, Any]:
    compact = {
        "turn": event.get("turn"),
        "stage": event.get("stage"),
        "actor_agent_id": event.get("actor_agent_id"),
        "output_tokens": (event.get("token_cost") or {}).get("output_tokens"),
    }
    for key in FIELD_KEYS:
        compact[key] = event.get(key)
        compact[f"{key}_numbers"] = numeric_mentions(event.get(key))
    return compact


def pair_events(
    baseline_trace: Dict[str, Any],
    variant_trace: Dict[str, Any],
) -> List[Dict[str, Any]]:
    baseline_events = {event.get("turn"): compact_event(event) for event in baseline_trace.get("communication_events", [])}
    variant_events = {event.get("turn"): compact_event(event) for event in variant_trace.get("communication_events", [])}
    turns = sorted(set(baseline_events) | set(variant_events))
    paired = []
    for turn in turns:
        base = baseline_events.get(turn, {})
        var = variant_events.get(turn, {})
        changed_fields = [
            key for key in FIELD_KEYS
            if normalize(base.get(key)) != normalize(var.get(key))
        ]
        paired.append({
            "turn": turn,
            "actor_agent_id": base.get("actor_agent_id") or var.get("actor_agent_id"),
            "changed_fields": changed_fields,
            "baseline": base,
            "variant": var,
        })
    return paired


def first_divergence(paired_events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for row in paired_events:
        if row["changed_fields"]:
            return {
                "turn": row["turn"],
                "actor_agent_id": row["actor_agent_id"],
                "changed_fields": row["changed_fields"],
            }
    return None


def extract_relevant_paragraphs(raw_row: Optional[Dict[str, Any]], watch_terms: List[str]) -> List[Dict[str, str]]:
    if not raw_row:
        return []
    final_agents = [agent for agent in raw_row.get("agents", []) if agent.get("is_final")]
    if not final_agents:
        return []
    prompt = str(final_agents[-1].get("input") or "")
    prompt_norm_digits = digits_only(prompt)
    terms_norm = [normalize(term) for term in watch_terms if normalize(term)]
    terms_digits = [digits_only(term) for term in watch_terms if digits_only(term)]
    hits = []
    for match in PARAGRAPH_RE.finditer(prompt):
        title = match.group(1).strip()
        text = " ".join(match.group(2).split())
        hay_norm = normalize(f"{title} {text}")
        hay_digits = digits_only(f"{title} {text}")
        if any(term in hay_norm for term in terms_norm) or any(term in hay_digits for term in terms_digits):
            hits.append({
                "title": title,
                "text": text,
            })
    if not hits and prompt_norm_digits and any(term in prompt_norm_digits for term in terms_digits):
        hits.append({"title": "final_prompt", "text": "A watched numeric term appears in the final prompt."})
    return hits


def md_escape(text: Any) -> str:
    value = "" if text is None else str(text)
    return value.replace("|", "\\|").replace("\n", "<br>")


def write_markdown(path: Path, packet: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    case = packet["case"]
    divergence = packet["first_divergence"]
    if divergence:
        divergence_text = (
            f"turn {divergence['turn']} / {divergence['actor_agent_id']} / "
            f"{', '.join(divergence['changed_fields'])}"
        )
    else:
        divergence_text = "none"
    lines = [
        f"# PACT Drift Packet: Sample {case['sample_index']}",
        "",
        "## Case",
        "",
        f"- Question: {case['question']}",
        f"- Gold: `{case['gold_answer']}`",
        f"- Transition: `{case.get('transition')}`",
        f"- Baseline final: `{case['baseline_final_answer']}`",
        f"- Variant final: `{case['variant_final_answer']}`",
        f"- First differing turn: `{divergence_text}`",
        "",
        "## Turn Pairing",
        "",
        "| Turn | Actor | Changed fields | Baseline Action Required | Variant Action Required | Baseline Action Result | Variant Action Result |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in packet["paired_events"]:
        base = row["baseline"]
        var = row["variant"]
        lines.append(
            "| {turn} | {actor} | `{changed}` | {base_ar} | {var_ar} | {base_res} | {var_res} |".format(
                turn=row["turn"],
                actor=md_escape(row["actor_agent_id"]),
                changed=", ".join(row["changed_fields"]) or "none",
                base_ar=md_escape(base.get("action_required")),
                var_ar=md_escape(var.get("action_required")),
                base_res=md_escape(base.get("action_result")),
                var_res=md_escape(var.get("action_result")),
            )
        )

    lines.extend([
        "",
        "## Numeric Mentions",
        "",
        "| Turn | Actor | Baseline numbers | Variant numbers |",
        "| ---: | --- | --- | --- |",
    ])
    for row in packet["paired_events"]:
        base_nums = sorted({
            number
            for key in FIELD_KEYS
            for number in row["baseline"].get(f"{key}_numbers", [])
        })
        var_nums = sorted({
            number
            for key in FIELD_KEYS
            for number in row["variant"].get(f"{key}_numbers", [])
        })
        lines.append(
            f"| {row['turn']} | {md_escape(row['actor_agent_id'])} | `{', '.join(base_nums)}` | `{', '.join(var_nums)}` |"
        )

    lines.extend([
        "",
        "## Final-Prompt Evidence Hits",
        "",
        "| Run | Paragraph | Text |",
        "| --- | --- | --- |",
    ])
    for run_name in ("baseline", "variant"):
        for hit in packet["final_prompt_hits"].get(run_name, []):
            lines.append(f"| {run_name} | {md_escape(hit['title'])} | {md_escape(hit['text'])} |")

    lines.extend([
        "",
        "## Reading",
        "",
        "- Turn 0 is identical: Agent A locates Kirton End in the Boston district.",
        "- The contract run still sees `35,124` at turn 1, so the correct evidence is not absent.",
        "- The harmful retargeting appears after that: the variant action requirement moves from the city/town population to the civil parish of Kirton.",
        "- The final variant answer then selects `273` from the distractor paragraph `Kirton, Nottinghamshire`, while the baseline remains anchored to `Boston, Lincolnshire` and answers `35,124`.",
        "- This is a target-slot drift case, not an extraction-only surface failure.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def build(args: argparse.Namespace) -> Dict[str, Any]:
    baseline_trace = find_sample(load_jsonl(args.baseline_trace), args.sample_index)
    variant_trace = find_sample(load_jsonl(args.variant_trace), args.sample_index)
    if not baseline_trace or not variant_trace:
        raise SystemExit(f"sample_index={args.sample_index} missing from one trace")

    changed_case = find_sample(load_jsonl(args.changed_cases), args.sample_index) if args.changed_cases else None
    baseline_raw = find_sample(load_jsonl(args.baseline_raw), args.sample_index) if args.baseline_raw else None
    variant_raw = find_sample(load_jsonl(args.variant_raw), args.sample_index) if args.variant_raw else None

    paired = pair_events(baseline_trace, variant_trace)
    case = {
        "sample_index": args.sample_index,
        "instance_id": baseline_trace.get("instance_id"),
        "question": baseline_trace.get("question"),
        "gold_answer": baseline_trace.get("gold_answer"),
        "transition": (changed_case or {}).get("transition"),
        "baseline_final_answer": (baseline_trace.get("communication_events") or [{}])[-1].get("final_answer"),
        "variant_final_answer": (variant_trace.get("communication_events") or [{}])[-1].get("final_answer"),
        "baseline_correct": (baseline_trace.get("final") or {}).get("correct"),
        "variant_correct": (variant_trace.get("final") or {}).get("correct"),
        "baseline_f1": (changed_case or {}).get("baseline_f1"),
        "variant_f1": (changed_case or {}).get("variant_f1"),
    }
    watch_terms = term_variants(
        case["gold_answer"],
        case["baseline_final_answer"],
        case["variant_final_answer"],
        (changed_case or {}).get("baseline_prediction"),
        (changed_case or {}).get("variant_prediction"),
    )
    packet = {
        "case": case,
        "watch_terms": watch_terms,
        "first_divergence": first_divergence(paired),
        "paired_events": paired,
        "final_prompt_hits": {
            "baseline": extract_relevant_paragraphs(baseline_raw, watch_terms),
            "variant": extract_relevant_paragraphs(variant_raw, watch_terms),
        },
        "sources": {
            "baseline_trace": str(args.baseline_trace),
            "variant_trace": str(args.variant_trace),
            "changed_cases": str(args.changed_cases) if args.changed_cases else None,
            "baseline_raw": str(args.baseline_raw) if args.baseline_raw else None,
            "variant_raw": str(args.variant_raw) if args.variant_raw else None,
        },
    }
    write_json(args.output_json, packet)
    if args.output_md:
        write_markdown(args.output_md, packet)
    return packet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-index", type=int, required=True)
    parser.add_argument("--baseline-trace", type=Path, required=True)
    parser.add_argument("--variant-trace", type=Path, required=True)
    parser.add_argument("--changed-cases", type=Path)
    parser.add_argument("--baseline-raw", type=Path)
    parser.add_argument("--variant-raw", type=Path)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    packet = build(args)
    print(json.dumps({
        "sample_index": packet["case"]["sample_index"],
        "transition": packet["case"]["transition"],
        "first_divergence": packet["first_divergence"],
        "output_json": str(args.output_json),
        "output_md": str(args.output_md) if args.output_md else None,
    }, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
