#!/usr/bin/env python3
"""Shared runner for pre-answer latent MCA variants.

The communication event happens before any final sender answer exists:

* MCA-Pre-KV: the receiver continues after a sender's pre-answer KV prefix.
* MCA-Pre-S: the receiver is steered by activations captured during a
  sender's pre-answer pass.

This runner intentionally does not use textual cue extraction, certificates,
or post-answer revision prompts.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any, Literal

from run_basic_mad import is_correct, load_rows, majority_vote, normalize_numeric, resolve_inside
from run_consensus_quarantine import transition_label
from run_mad_mm import cot_prompt, extract_xml_answer, prepare_question
from mca_hidden_channel_runner import (
    SenderState,
    _generate_with_steering,
    _manual_generate_sender_state,
    _manual_generate_with_optional_past,
    _progress,
)
from mca_hidden_channel_runner import generate_hf_outputs_with_progress
from run_mca_soft_prefix import _render_prompt, _torch_dtype


Channel = Literal["kv", "steer"]
PreStateStage = Literal["question_only", "early_plan"]


GENERIC_SOLVER_NAMES = (
    "independent solver A",
    "independent solver B",
    "independent solver C",
    "independent solver D",
    "independent solver E",
)


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--work-dir", default=os.environ.get("ACR_WORK_DIR", os.getcwd()))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--split", default="test")
    parser.add_argument("--model-key", required=True)
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--gpu-id", default=os.environ.get("CUDA_VISIBLE_DEVICES", "0"))
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--reviewers", type=int, default=3)
    parser.add_argument(
        "--pre-state-stage",
        choices=("question_only", "early_plan"),
        default="question_only",
        help="question_only captures only the read-question pass; early_plan also samples a short private plan.",
    )
    parser.add_argument("--pre-state-tokens", type=int, default=64)
    parser.add_argument("--pre-state-temperature", type=float, default=0.7)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--resolve-temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--resolve-max-tokens", type=int, default=1536)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    parser.add_argument("--resume", action="store_true", help="Append to an existing records.jsonl and skip completed rows.")
    parser.add_argument("--disable-tqdm", action="store_true")
    parser.add_argument(
        "--channel-mode",
        choices=("state", "none"),
        default="state",
        help="state applies pre-answer latent state; none is a no-channel control.",
    )
    parser.add_argument("--steering-layer", type=int, default=16)
    parser.add_argument("--steering-scale", type=float, default=1.0)
    return parser


def pre_state_prompt(question: str, agent_index: int, stage: PreStateStage) -> list[dict[str, str]]:
    """Return the sender prompt used before any final answer is requested."""

    solver_name = GENERIC_SOLVER_NAMES[agent_index % len(GENERIC_SOLVER_NAMES)]
    if stage == "question_only":
        user_text = (
            f"Problem:\n{question}\n\n"
            "Read the problem and form an internal representation for a later solver pass."
        )
    else:
        user_text = (
            f"Problem:\n{question}\n\n"
            "Privately sketch only the problem representation and first search direction. "
            "Stop before final computation."
        )
    return [
        {
            "role": "system",
            "content": f"You are {solver_name}. This is a pre-answer representation pass.",
        },
        {"role": "user", "content": user_text},
    ]


def receiver_prompt(question: str) -> list[dict[str, str]]:
    """Return the from-scratch receiver prompt; no channel text is shown."""

    return [{"role": "user", "content": cot_prompt(question)}]


def parse_answer_output(text: str) -> dict[str, Any]:
    parsed = extract_xml_answer(text)
    return {
        "output": text,
        "parsed_answer": parsed,
        "normalized_answer": normalize_numeric(parsed),
        "mean_selected_logprob": None,
        "sequence_score": None,
    }


def _pre_state_token_budget(stage: PreStateStage, requested_tokens: int) -> int:
    if stage == "question_only":
        return 0
    return max(1, requested_tokens)


def _source_indices(agents: int, reviewers: int) -> list[int]:
    if agents < 1:
        raise ValueError("agents must be >= 1")
    return [idx % agents for idx in range(max(1, reviewers))]


def _generate_receiver_from_state(
    channel: Channel,
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    sender_state: SenderState | None,
    *,
    channel_mode: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    max_model_len: int,
    steering_layer: int,
    steering_scale: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if channel_mode == "none" or sender_state is None:
        text = _manual_generate_with_optional_past(
            model,
            tokenizer,
            prompt_text,
            past_key_values=None,
            past_token_count=0,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            max_prompt_tokens=max(1, max_model_len - max_new_tokens - 8),
        )
        return parse_answer_output(text), {"channel_mode": "none", "active": False}

    if channel == "kv":
        text = _manual_generate_with_optional_past(
            model,
            tokenizer,
            prompt_text,
            past_key_values=sender_state.past_key_values,
            past_token_count=sender_state.past_token_count,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            max_prompt_tokens=max(1, max_model_len - max_new_tokens - sender_state.past_token_count - 8),
        )
        return parse_answer_output(text), {
            "channel": "pre_kv",
            "channel_mode": "state",
            "active": True,
            "source_past_token_count": sender_state.past_token_count,
        }

    text = _generate_with_steering(
        model,
        tokenizer,
        prompt_text,
        steering_vector=sender_state.steering_vector,
        layer_index=steering_layer,
        steering_scale=steering_scale,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        max_prompt_tokens=max(1, max_model_len - max_new_tokens - 8),
    )
    return parse_answer_output(text), {
        "channel": "pre_steer",
        "channel_mode": "state",
        "active": sender_state.steering_vector is not None,
        "source_activation_capture_count": sender_state.metadata.get("activation_capture_count", 0),
        "source_steering_vector_norm": sender_state.metadata.get("steering_vector_norm", 0.0),
        "steering_layer": steering_layer,
        "steering_scale": steering_scale,
    }


def _metrics(counts: Counter[str], total: int) -> dict[str, float]:
    baseline_wrong = max(1, counts["BaW_to_C"] + counts["BaW_to_W"])
    baseline_correct = max(1, counts["BaC_to_C"] + counts["BaC_to_W"])
    return {
        "baseline_majority_accuracy": counts["baseline_majority_correct"] / max(1, total),
        "final_accuracy": counts["final_correct"] / max(1, total),
        "pre_state_case_rate": counts["pre_state_cases"] / max(1, total),
        "answer_change_rate": counts["answer_changed"] / max(1, total),
        "baseline_wrong_recovery_rate": counts["BaW_to_C"] / baseline_wrong,
        "baseline_correct_harm_rate": counts["BaC_to_W"] / baseline_correct,
        "final_parse_fail_rate": counts["final_parse_fail"] / max(1, total),
        "final_majority_tie_rate": counts["final_majority_ties"] / max(1, total),
    }


def _transition_label(baseline_ok: bool, final_ok: bool) -> str:
    label = transition_label(baseline_ok, final_ok)
    return label.replace("Ma", "Ba", 1)


def _record_row_key(row: dict[str, Any], row_idx: int) -> Any:
    return row.get("index", row_idx)


def _record_key_from_output(record: dict[str, Any]) -> Any:
    return record.get("index")


def _load_existing_records(records_path: Path) -> list[dict[str, Any]]:
    if not records_path.exists():
        return []
    records: list[dict[str, Any]] = []
    with records_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _accumulate_existing_pre_counts(records: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        mca_pre = record.get("mca_pre", {})
        transition = mca_pre.get("transition")
        counts["total"] += 1
        if mca_pre.get("channel_mode") == "state":
            counts["pre_state_cases"] += 1
        if transition:
            counts[transition] += 1
            if transition in {"BaC_to_C", "BaC_to_W"}:
                counts["baseline_majority_correct"] += 1
            if transition in {"BaC_to_C", "BaW_to_C"}:
                counts["final_correct"] += 1
        baseline_answer = mca_pre.get("baseline_majority_answer")
        final_answer = mca_pre.get("final_majority_answer")
        if normalize_numeric(baseline_answer) != normalize_numeric(final_answer):
            counts["answer_changed"] += 1
        if normalize_numeric(final_answer) is None:
            counts["final_parse_fail"] += 1
        if mca_pre.get("final_majority_tie"):
            counts["final_majority_ties"] += 1
    return counts


def run_main(channel: Channel, args: argparse.Namespace) -> int:
    if args.agents < 1:
        raise SystemExit("--agents must be >= 1")
    if args.reviewers < 1:
        raise SystemExit("--reviewers must be >= 1")
    if args.steering_layer < 0:
        raise SystemExit("--steering-layer must be >= 0")

    work_dir = Path(args.work_dir).expanduser().resolve()
    protocol = "mca-pre-kv-cache" if channel == "kv" else "mca-pre-activation-steering"
    method_key = f"{protocol}-{args.pre_state_stage}-{args.channel_mode}"
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-{method_key}",
        work_dir,
        "output dir",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    data_path = resolve_inside(
        work_dir / "data" / "benchmarks" / args.benchmark / args.split / "canonical.jsonl",
        work_dir,
        "benchmark path",
    )
    rows = load_rows(data_path, args.limit)
    pre_tokens = _pre_state_token_budget(args.pre_state_stage, args.pre_state_tokens)
    _progress(
        f"pre-answer run start protocol={protocol} run_id={args.run_id} rows={len(rows)} "
        f"stage={args.pre_state_stage} channel_mode={args.channel_mode}"
    )

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    started_at = time.time()
    model_path = Path(args.model_path).expanduser().resolve()
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        trust_remote_code=True,
        torch_dtype=_torch_dtype(args.dtype, torch),
    )
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    _progress(f"model loaded device={device} dtype={args.dtype} model_path={model_path}")

    records_path = output_dir / "records.jsonl"
    existing_records = _load_existing_records(records_path) if args.resume else []
    completed_keys = {_record_key_from_output(record) for record in existing_records}
    counts: Counter[str] = _accumulate_existing_pre_counts(existing_records) if args.resume else Counter()
    if args.resume:
        _progress(
            f"resume enabled existing_records={len(existing_records)} "
            f"completed_rows={len(completed_keys)} records_path={records_path}"
        )
    source_indices = _source_indices(args.agents, args.reviewers)

    open_mode = "a" if args.resume else "w"
    with records_path.open(open_mode, encoding="utf-8", newline="\n") as handle:
        for row_idx, row in enumerate(rows):
            row_key = _record_row_key(row, row_idx)
            if args.resume and row_key in completed_keys:
                continue
            question = prepare_question(str(row.get("question") or ""), args.benchmark)
            sender_states: list[SenderState] = []
            if args.channel_mode == "state":
                _progress(f"row {row_idx + 1}/{len(rows)} pre-state generation start")
                for agent_idx in range(args.agents):
                    prompt = _render_prompt(tokenizer, pre_state_prompt(question, agent_idx, args.pre_state_stage))
                    state = _manual_generate_sender_state(
                        model,
                        tokenizer,
                        prompt,
                        max_new_tokens=pre_tokens,
                        temperature=args.pre_state_temperature,
                        top_p=args.top_p,
                        max_model_len=args.max_model_len,
                        steering_layer=args.steering_layer,
                        keep_past_key_values=(channel == "kv"),
                    )
                    sender_states.append(state)
                    _progress(
                        f"row {row_idx + 1}/{len(rows)} pre-state sender {agent_idx + 1}/{args.agents} "
                        f"tokens={state.metadata['generated_tokens']}"
                    )
            else:
                _progress(f"row {row_idx + 1}/{len(rows)} pre-state generation skipped channel_mode=none")

            receiver_messages = receiver_prompt(question)
            receiver_prompt_text = _render_prompt(tokenizer, receiver_messages)
            baseline_prompts = [receiver_prompt_text for _ in range(args.agents)]
            baseline_outputs = generate_hf_outputs_with_progress(
                model,
                tokenizer,
                baseline_prompts,
                label=f"row {row_idx + 1}/{len(rows)} baseline",
                max_new_tokens=args.max_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                batch_size=args.batch_size,
                max_model_len=args.max_model_len,
            )
            baseline_answer, baseline_tie = majority_vote([item.get("parsed_answer") for item in baseline_outputs])

            receiver_outputs: list[dict[str, Any]] = []
            receiver_metadata: list[dict[str, Any]] = []
            for reviewer_idx, source_idx in enumerate(source_indices):
                output, metadata = _generate_receiver_from_state(
                    channel,
                    model,
                    tokenizer,
                    receiver_prompt_text,
                    sender_states[source_idx] if sender_states else None,
                    channel_mode=args.channel_mode,
                    max_new_tokens=args.resolve_max_tokens,
                    temperature=args.resolve_temperature,
                    top_p=args.top_p,
                    max_model_len=args.max_model_len,
                    steering_layer=args.steering_layer,
                    steering_scale=args.steering_scale,
                )
                output["source_agent_index"] = source_idx
                receiver_outputs.append(output)
                receiver_metadata.append({**metadata, "source_agent_index": source_idx})
                _progress(f"row {row_idx + 1}/{len(rows)} receiver {reviewer_idx + 1}/{len(source_indices)} done")

            final_answer, final_tie = majority_vote([item.get("parsed_answer") for item in receiver_outputs])
            gold = row.get("answer")
            baseline_ok = is_correct(baseline_answer, gold)
            final_ok = is_correct(final_answer, gold)
            transition = _transition_label(baseline_ok, final_ok)
            counts["total"] += 1
            counts["pre_state_cases"] += 1 if args.channel_mode == "state" else 0
            if baseline_ok:
                counts["baseline_majority_correct"] += 1
            if final_ok:
                counts["final_correct"] += 1
            if normalize_numeric(baseline_answer) != normalize_numeric(final_answer):
                counts["answer_changed"] += 1
            if normalize_numeric(final_answer) is None:
                counts["final_parse_fail"] += 1
            if final_tie:
                counts["final_majority_ties"] += 1
            counts[transition] += 1

            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row.get("index", row_idx),
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "mca_pre": {
                    "variant": "pre_kv_cache" if channel == "kv" else "pre_activation_steering",
                    "protocol": protocol,
                    "pre_state_stage": args.pre_state_stage,
                    "pre_state_tokens": pre_tokens,
                    "state_source": "pre_answer_sender_pass",
                    "channel_mode": args.channel_mode,
                    "agents": args.agents,
                    "reviewers": args.reviewers,
                    "source_indices": source_indices,
                    "sender_state_metadata": [state.metadata for state in sender_states],
                    "baseline_outputs": baseline_outputs,
                    "baseline_majority_answer": baseline_answer,
                    "baseline_majority_tie": baseline_tie,
                    "receiver_outputs": receiver_outputs,
                    "receiver_state_metadata": receiver_metadata,
                    "final_majority_answer": final_answer,
                    "final_normalized_answer": normalize_numeric(final_answer),
                    "final_majority_tie": final_tie,
                    "correct": final_ok,
                    "transition": transition,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            handle.flush()
            _progress(
                f"row {row_idx + 1}/{len(rows)} written transition={transition} "
                f"baseline={baseline_answer} final={final_answer}"
            )
            del sender_states
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    elapsed = time.time() - started_at
    total = max(1, counts["total"])
    summary = {
        "run_id": args.run_id,
        "model_key": args.model_key,
        "model_path": str(model_path),
        "benchmark": args.benchmark,
        "split": args.split,
        "rows": len(rows),
        "protocol": protocol,
        "pre_state_stage": args.pre_state_stage,
        "pre_state_tokens": pre_tokens,
        "state_source": "pre_answer_sender_pass",
        "channel_mode": args.channel_mode,
        "agents": args.agents,
        "reviewers": args.reviewers,
        "temperature": args.temperature,
        "resolve_temperature": args.resolve_temperature,
        "pre_state_temperature": args.pre_state_temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "resolve_max_tokens": args.resolve_max_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": dict(counts),
        "metrics": _metrics(counts, total),
    }
    if channel == "steer":
        summary["steering"] = {"layer": args.steering_layer, "scale": args.steering_scale}
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {args.benchmark}-{args.model_key}-{protocol}\n\n")
        handle.write(f"- Rows: {len(rows)}\n")
        handle.write("- State source: pre-answer sender pass\n")
        handle.write(f"- Pre-state stage: {args.pre_state_stage}\n")
        handle.write(f"- Channel mode: {args.channel_mode}\n")
        handle.write(f"- Baseline majority accuracy: {summary['metrics']['baseline_majority_accuracy']:.4f}\n")
        handle.write(f"- Final accuracy: {summary['metrics']['final_accuracy']:.4f}\n")
        handle.write(f"- Pre-state case rate: {summary['metrics']['pre_state_case_rate']:.4f}\n")
        handle.write(f"- Baseline-wrong recovery rate: {summary['metrics']['baseline_wrong_recovery_rate']:.4f}\n")
        handle.write(f"- Baseline-correct harm rate: {summary['metrics']['baseline_correct_harm_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    _progress(f"pre-answer run complete protocol={protocol} elapsed_seconds={elapsed:.1f}")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0
