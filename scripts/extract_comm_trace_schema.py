#!/usr/bin/env python3
"""Normalize communication traces from MAD-MM, DAR, and MOC into JSONL."""

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


SCHEMA_VERSION = "acr.comm_trace.v1"

MADMM_METHOD_FILES = {
    "cot": "cot_seed41.json",
    "mad_naive": "mad_3agents_2rounds_seed41.json",
    "mad_objective": "mad_objective_3agents_2rounds_seed41.json",
    "mad_subjective": "mad_subjective_3agents_2rounds_seed41.json",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(records: Iterable[Dict[str, Any]], out_path: Optional[Path]) -> None:
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_file = out_path.open("w", encoding="utf-8")
    else:
        out_file = sys.stdout
    try:
        for record in records:
            out_file.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    finally:
        if out_path:
            out_file.close()


def normalize_number(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return int(value) if float(value).is_integer() else float(value)

    text = str(value).replace(",", "")
    matches = re.findall(r"-?\d+(?:\.\d+)?", text)
    if not matches:
        return text.strip()
    number = float(matches[-1])
    return int(number) if number.is_integer() else number


def normalize_gold(value: Any) -> Any:
    text = str(value)
    if "####" in text:
        text = text.split("####")[-1]
    return normalize_number(text)


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


def sum_token_stats(stats: Any) -> Dict[str, Optional[int]]:
    if not isinstance(stats, list):
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    seen = False
    for row in stats:
        if not isinstance(row, dict):
            continue
        seen = True
        input_tokens += int(row.get("input_tokens") or 0)
        output_tokens += int(row.get("output_tokens") or 0)
        total_tokens += int(row.get("total_tokens") or 0)
    if not seen:
        return {"input_tokens": None, "output_tokens": None, "total_tokens": None}
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def majority_answer(answers: List[Any]) -> Any:
    normalized = [normalize_number(answer) for answer in answers]
    counts = Counter(normalized)
    if not counts:
        return None
    return counts.most_common(1)[0][0]


def base_record(
    *,
    run_id: str,
    method_family: str,
    method: str,
    instance_id: Any,
    sample_index: int,
    question: Optional[str],
    gold_answer: Any,
    source: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "method_family": method_family,
        "method": method,
        "instance_id": str(instance_id) if instance_id is not None else str(sample_index),
        "sample_index": sample_index,
        "question": question,
        "gold_answer": normalize_gold(gold_answer),
        "final": {"answer": None, "correct": None},
        "transition": {
            "from_stage": None,
            "to_stage": "final",
            "type": "unknown",
            "before_answer": None,
            "before_correct": None,
            "after_answer": None,
            "after_correct": None,
        },
        "rounds": [],
        "retention_events": [],
        "communication_events": [],
        "token_cost": {
            "scope": None,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "compressed_prompt_tokens": None,
            "compressed_completion_tokens": None,
            "compressed_total_tokens": None,
        },
        "method_comparison": None,
        "source": source,
    }


def madmm_rounds(item: Dict[str, Any], gold: Any, mask: Optional[List[bool]]) -> List[Dict[str, Any]]:
    rounds = []
    debate_history = item.get("debate_history") or []
    perplexity_history = item.get("perplexity_history") or []
    for round_index, agents in enumerate(debate_history):
        agent_rows = []
        if not isinstance(agents, list):
            continue
        confidences = perplexity_history[round_index] if round_index < len(perplexity_history) else []
        for agent_index, agent in enumerate(agents):
            answer = agent.get("answer") if isinstance(agent, dict) else None
            retained = None
            if round_index == 0 and mask and agent_index < len(mask):
                retained = bool(mask[agent_index])
            agent_rows.append(
                {
                    "agent_id": f"Agent{agent_index + 1}",
                    "answer": normalize_number(answer),
                    "correct": is_correct(answer, gold),
                    "confidence": confidences[agent_index] if agent_index < len(confidences) else None,
                    "retained": retained,
                    "tokens": None,
                }
            )
        answers = [agent.get("answer") for agent in agents if isinstance(agent, dict)]
        maj = majority_answer(answers)
        rounds.append(
            {
                "round_index": round_index,
                "agents": agent_rows,
                "debate_answer": maj,
                "debate_correct": is_correct(maj, gold),
            }
        )
    return rounds


def madmm_retention_event(item: Dict[str, Any], gold: Any, method: str) -> Optional[Dict[str, Any]]:
    mask_history = item.get("mask_history") or []
    if len(mask_history) < 2 or not isinstance(mask_history[1], list):
        return None
    mask = [bool(value) for value in mask_history[1]]
    round_0 = item.get("debate_history", [[]])[0]
    kept = []
    dropped = []
    kept_correct = 0
    dropped_correct = 0
    for index, keep in enumerate(mask):
        agent_id = f"Agent{index + 1}"
        answer = round_0[index].get("answer") if index < len(round_0) else None
        correct = bool(is_correct(answer, gold))
        if keep:
            kept.append(agent_id)
            kept_correct += int(correct)
        else:
            dropped.append(agent_id)
            dropped_correct += int(correct)
    return {
        "stage": "mask_history[1]",
        "mechanism": "memory_mask" if method != "mad_naive" else "full_retention",
        "retained_agent_ids": kept,
        "dropped_agent_ids": dropped,
        "merged_agent_ids": None,
        "retained_correct_count": kept_correct,
        "dropped_correct_count": dropped_correct,
        "token_cost": None,
    }


def extract_madmm(args: argparse.Namespace) -> List[Dict[str, Any]]:
    base = Path(args.results_dir)
    method_files = {k: v for k, v in MADMM_METHOD_FILES.items() if (base / v).exists()}
    if args.methods:
        method_files = {k: method_files[k] for k in args.methods}

    loaded = {method: load_json(base / filename) for method, filename in method_files.items()}
    by_method = {
        method: {str(item.get("id")): item for item in data.get("results", [])}
        for method, data in loaded.items()
    }
    baseline = args.baseline_method if args.baseline_method in by_method else None
    baseline_correct = {}
    if baseline:
        baseline_correct = {
            qid: is_correct(item.get("pred"), item.get("ground_truth"))
            for qid, item in by_method[baseline].items()
        }

    records = []
    for method, data in loaded.items():
        usage = data.get("token_usage_summary") or {}
        for sample_index, item in enumerate(data.get("results", [])):
            gold = item.get("ground_truth")
            final_answer = normalize_number(item.get("pred"))
            final_correct = is_correct(final_answer, gold)
            mask = None
            if len(item.get("mask_history") or []) > 1:
                mask = item["mask_history"][1]
            record = base_record(
                run_id=args.run_id,
                method_family="MAD-MM",
                method=method,
                instance_id=item.get("id"),
                sample_index=sample_index,
                question=item.get("question"),
                gold_answer=gold,
                source={"result_file": str(base / method_files[method])},
            )
            record["final"] = {"answer": final_answer, "correct": final_correct}
            record["rounds"] = madmm_rounds(item, gold, mask)
            before_answer = None
            before_correct = None
            if record["rounds"]:
                before_answer = record["rounds"][0]["debate_answer"]
                before_correct = record["rounds"][0]["debate_correct"]
            record["transition"] = {
                "from_stage": "round_0_majority",
                "to_stage": "final",
                "type": transition_type(before_correct, final_correct),
                "before_answer": before_answer,
                "before_correct": before_correct,
                "after_answer": final_answer,
                "after_correct": final_correct,
            }
            event = madmm_retention_event(item, gold, method)
            if event:
                record["retention_events"].append(event)
            record["token_cost"] = {
                "scope": "run_method",
                "input_tokens": usage.get("input_tokens", usage.get("total_input_tokens")),
                "output_tokens": usage.get("output_tokens", usage.get("total_output_tokens")),
                "total_tokens": usage.get("total_tokens"),
                "compressed_prompt_tokens": None,
                "compressed_completion_tokens": None,
                "compressed_total_tokens": None,
            }
            if baseline and method != baseline:
                qid = str(item.get("id"))
                base_item = by_method[baseline].get(qid)
                base_final = None
                if base_item:
                    base_final = {
                        "method": baseline,
                        "answer": normalize_number(base_item.get("pred")),
                        "correct": baseline_correct.get(qid),
                    }
                record["method_comparison"] = {
                    "baseline": base_final,
                    "transition_vs_baseline": transition_type(
                        baseline_correct.get(qid), final_correct
                    ),
                }
            records.append(record)
    return records


def extract_dar(args: argparse.Namespace) -> List[Dict[str, Any]]:
    records = []
    history_path = Path(args.history_jsonl)
    with history_path.open("r", encoding="utf-8-sig") as f:
        for sample_index, line in enumerate(f):
            if not line.strip():
                continue
            item = json.loads(line)
            round_keys = sorted(item.keys(), key=lambda x: int(x) if str(x).isdigit() else str(x))
            first_round = item.get(round_keys[0], {}) if round_keys else {}
            last_round = item.get(round_keys[-1], {}) if round_keys else {}
            gold = last_round.get("answer", first_round.get("answer"))
            record = base_record(
                run_id=args.run_id,
                method_family="DAR",
                method=args.method,
                instance_id=sample_index,
                sample_index=sample_index,
                question=None,
                gold_answer=gold,
                source={"history_jsonl": str(history_path)},
            )
            before_answer = first_round.get("debate_answer")
            before_correct = first_round.get("debate_answer_iscorr")
            final_answer = last_round.get("debate_answer")
            final_correct = last_round.get("debate_answer_iscorr")
            record["final"] = {"answer": normalize_number(final_answer), "correct": final_correct}
            record["transition"] = {
                "from_stage": f"round_{round_keys[0]}_debate" if round_keys else None,
                "to_stage": f"round_{round_keys[-1]}_debate" if round_keys else "final",
                "type": transition_type(before_correct, final_correct),
                "before_answer": normalize_number(before_answer),
                "before_correct": before_correct,
                "after_answer": normalize_number(final_answer),
                "after_correct": final_correct,
            }

            total_tokens = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
            for round_key in round_keys:
                round_data = item[round_key]
                response_ids = list((round_data.get("responses") or {}).keys())
                answers = round_data.get("final_answers") or []
                correctness = round_data.get("final_answer_iscorr") or []
                token_stats = round_data.get("token_stats") or []
                agents = []
                for agent_index, agent_id in enumerate(response_ids):
                    tokens = token_stats[agent_index] if agent_index < len(token_stats) else None
                    if isinstance(tokens, dict):
                        total_tokens["input_tokens"] += int(tokens.get("input_tokens") or 0)
                        total_tokens["output_tokens"] += int(tokens.get("output_tokens") or 0)
                        total_tokens["total_tokens"] += int(tokens.get("total_tokens") or 0)
                    agents.append(
                        {
                            "agent_id": agent_id,
                            "answer": normalize_number(answers[agent_index]) if agent_index < len(answers) else None,
                            "correct": correctness[agent_index] if agent_index < len(correctness) else None,
                            "confidence": None,
                            "retained": None,
                            "tokens": tokens,
                        }
                    )
                record["rounds"].append(
                    {
                        "round_index": int(round_key) if str(round_key).isdigit() else round_key,
                        "agents": agents,
                        "debate_answer": normalize_number(round_data.get("debate_answer")),
                        "debate_correct": round_data.get("debate_answer_iscorr"),
                    }
                )
                retention_events = round_data.get("retention_events") or []
                if isinstance(retention_events, dict):
                    retention_events = [retention_events]
                for event in retention_events:
                    if not isinstance(event, dict):
                        continue
                    record["retention_events"].append(
                        {
                            "stage": event.get("stage", f"round_{round_key}_filter"),
                            "mechanism": event.get("mechanism", args.method),
                            "retained_agent_ids": event.get("retained_agent_ids"),
                            "dropped_agent_ids": event.get("dropped_agent_ids"),
                            "merged_agent_ids": None,
                            "retained_correct_count": None,
                            "dropped_correct_count": None,
                            "token_cost": event.get("filter_tokens"),
                            "candidate_agent_ids": event.get("candidate_agent_ids"),
                            "original_retained_agent_ids": event.get("original_retained_agent_ids"),
                            "guard_mode": event.get("guard_mode"),
                            "guard_added_agent_ids": event.get("guard_added_agent_ids"),
                            "guard_removed_agent_ids": event.get("guard_removed_agent_ids"),
                            "guard_notes": event.get("guard_notes"),
                            "guard_parseable_buckets": event.get("guard_parseable_buckets"),
                            "guard_missing_parseable_buckets": event.get("guard_missing_parseable_buckets"),
                            "retention_message_mode": event.get("retention_message_mode"),
                            "raw_filter_response": event.get("raw_filter_response"),
                        }
                    )
            record["token_cost"] = {
                "scope": "sample",
                **total_tokens,
                "compressed_prompt_tokens": None,
                "compressed_completion_tokens": None,
                "compressed_total_tokens": None,
            }
            records.append(record)
    return records


def moc_log_summary(log_path: Optional[str]) -> Dict[str, Any]:
    if not log_path:
        return {}
    path = Path(log_path)
    if not path.exists():
        return {"log_path": str(path), "available": False}
    text = path.read_text(encoding="utf-8", errors="replace")
    prompt_tokens = [int(x) for x in re.findall(r"conpressed_prompt_tokens:(\d+)", text)]
    completion_tokens = [int(x) for x in re.findall(r"conpressed_completion_tokens:(\d+)", text)]
    return {
        "log_path": str(path),
        "available": True,
        "merged_pair_count": len(re.findall(r"\[ISM Phase 2\] Merged pair", text)),
        "summary_strategy_calls": len(re.findall(r"\[Summary\] Trying strategy", text)),
        "logged_compressed_prompt_tokens": sum(prompt_tokens),
        "logged_compressed_completion_tokens": sum(completion_tokens),
        "logged_compressed_total_tokens": sum(prompt_tokens) + sum(completion_tokens),
    }


def load_moc_comm_events(comm_events_jsonl: Optional[str]) -> Dict[str, List[Dict[str, Any]]]:
    if not comm_events_jsonl:
        return {}
    path = Path(comm_events_jsonl)
    if not path.exists():
        return {}

    events_by_sample: Dict[str, List[Dict[str, Any]]] = {}
    for event in load_jsonl(path):
        sample_index = event.get("sample_index")
        key = str(sample_index) if sample_index is not None else "unknown"
        events_by_sample.setdefault(key, []).append(event)
    return events_by_sample


def extract_moc(args: argparse.Namespace) -> List[Dict[str, Any]]:
    detail_path = Path(args.detail_json)
    summary_path = Path(args.summary_json)
    details = load_json(detail_path)
    summary = load_json(summary_path)
    log_summary = moc_log_summary(args.log_path)
    comm_events_by_sample = load_moc_comm_events(args.comm_events_jsonl)
    records = []
    for sample_index, item in enumerate(details):
        trace_sample_index = item.get("Trace Sample Index", sample_index)
        final_answer = normalize_number(item.get("Predicted"))
        final_correct = item.get("Correct")
        record = base_record(
            run_id=args.run_id,
            method_family="MOC",
            method=summary.get("mode", args.method),
            instance_id=trace_sample_index,
            sample_index=sample_index,
            question=item.get("Question"),
            gold_answer=item.get("True Answer"),
            source={
                "detail_json": str(detail_path),
                "summary_json": str(summary_path),
                "log_path": args.log_path,
                "comm_events_jsonl": args.comm_events_jsonl,
            },
        )
        record["final"] = {"answer": final_answer, "correct": final_correct}
        record["transition"] = {
            "from_stage": None,
            "to_stage": "final",
            "type": "unknown",
            "before_answer": None,
            "before_correct": None,
                "after_answer": final_answer,
                "after_correct": final_correct,
            }
        sample_events = comm_events_by_sample.get(str(trace_sample_index), [])
        if not sample_events:
            sample_events = comm_events_by_sample.get(str(sample_index), [])
        if sample_events:
            record["communication_events"].extend(sample_events)
        else:
            record["communication_events"].append(
                {
                    "stage": "neighbor_summary_ism",
                    "mechanism": "structural_merge",
                    "scope": "run",
                    "neighbor_hops": summary.get("neighbor_hops"),
                    "ism_r": summary.get("ism_r"),
                    "ism_kppa": summary.get("ism_kppa"),
                    **log_summary,
                }
            )
        record["token_cost"] = {
            "scope": "run_method",
            "input_tokens": summary.get("prompt_tokens"),
            "output_tokens": summary.get("completion_tokens"),
            "total_tokens": summary.get("total_tokens"),
            "compressed_prompt_tokens": summary.get("conpressed_prompt_tokens"),
            "compressed_completion_tokens": summary.get("conpressed_completion_tokens"),
            "compressed_total_tokens": summary.get("conpressed_total_tokens"),
        }
        records.append(record)
    return records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    madmm = subparsers.add_parser("madmm", help="Extract MAD-MM result JSON traces")
    madmm.add_argument("--results-dir", required=True)
    madmm.add_argument("--run-id", required=True)
    madmm.add_argument("--methods", nargs="+", choices=sorted(MADMM_METHOD_FILES), default=None)
    madmm.add_argument("--baseline-method", default="cot")
    madmm.add_argument("--out", type=Path, default=None)

    dar = subparsers.add_parser("dar", help="Extract DAR history JSONL traces")
    dar.add_argument("--history-jsonl", required=True)
    dar.add_argument("--run-id", required=True)
    dar.add_argument("--method", default="filter_critical")
    dar.add_argument("--out", type=Path, default=None)

    moc = subparsers.add_parser("moc", help="Extract MOC detail/summary traces")
    moc.add_argument("--detail-json", required=True)
    moc.add_argument("--summary-json", required=True)
    moc.add_argument("--log-path", default=None)
    moc.add_argument("--comm-events-jsonl", default=None)
    moc.add_argument("--run-id", required=True)
    moc.add_argument("--method", default="Chain")
    moc.add_argument("--out", type=Path, default=None)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "madmm":
        records = extract_madmm(args)
    elif args.command == "dar":
        records = extract_dar(args)
    elif args.command == "moc":
        records = extract_moc(args)
    else:
        raise SystemExit(f"Unknown command: {args.command}")
    write_jsonl(records, args.out)


if __name__ == "__main__":
    main()
