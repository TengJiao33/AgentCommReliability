#!/usr/bin/env python3
"""Run live MCA-Pre-KV first round followed by one Standard MAD text round.

This is a bridge diagnostic:

* Round 0 communication is live question-only KV, generated in this process.
* Round 1 is ordinary Standard MAD text debate over the Pre-KV receiver outputs.

It intentionally does not read prior MCA records as inputs and should not be
interpreted as pure latent multi-round debate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any

from mca_hidden_channel_runner import _manual_generate_sender_state, _progress
from mca_pre_answer_runner import _generate_receiver_from_state, pre_state_prompt
from run_basic_mad import is_correct, load_rows, majority_vote, normalize_numeric, resolve_inside
from run_mad_mm import answer_list, cot_prompt, debate_prompt, prepare_question
from run_mca_soft_prefix import _render_prompt, _torch_dtype


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
    parser.add_argument("--pre-state-temperature", type=float, default=0.7)
    parser.add_argument("--first-round-temperature", type=float, default=0.2)
    parser.add_argument("--debate-temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--first-round-max-tokens", type=int, default=1536)
    parser.add_argument("--debate-max-tokens", type=int, default=4096)
    parser.add_argument("--batch-size", type=int, default=3)
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def _record_key(row: dict[str, Any], row_idx: int) -> Any:
    return row.get("index", row_idx)


def _load_existing(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _transition(prefix: str, before_ok: bool, after_ok: bool) -> str:
    if before_ok and after_ok:
        return f"{prefix}C_to_C"
    if before_ok and not after_ok:
        return f"{prefix}C_to_W"
    if not before_ok and after_ok:
        return f"{prefix}W_to_C"
    return f"{prefix}W_to_W"


def _stable_seed(base_seed: int, *parts: Any) -> int:
    payload = "\x1f".join([str(base_seed), *(str(part) for part in parts)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % (2**31)


def _set_generation_seed(torch_module: Any, seed: int) -> None:
    torch_module.manual_seed(seed)
    if torch_module.cuda.is_available():
        torch_module.cuda.manual_seed_all(seed)


def _accumulate(records: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        payload = record.get("mca_pre_kv_then_mad", {})
        first_transition = payload.get("first_round_transition")
        no_channel_debate_transition = payload.get("no_channel_debate_transition_from_first_round")
        pre_kv_debate_transition = (
            payload.get("pre_kv_debate_transition_from_first_round")
            or payload.get("debate_transition_from_first_round")
        )
        counts["total"] += 1
        if first_transition:
            counts[first_transition] += 1
            if first_transition in {"BaC_to_C", "BaC_to_W"}:
                counts["no_channel_correct"] += 1
            if first_transition in {"BaC_to_C", "BaW_to_C"}:
                counts["pre_kv_first_correct"] += 1
        if no_channel_debate_transition:
            counts[no_channel_debate_transition] += 1
            if no_channel_debate_transition in {"NCC_to_C", "NCW_to_C"}:
                counts["no_channel_debate_correct"] += 1
        if pre_kv_debate_transition:
            counts[pre_kv_debate_transition] += 1
            if pre_kv_debate_transition in {"PKC_to_C", "PKW_to_C"}:
                counts["pre_kv_debate_correct"] += 1
        if payload.get("pre_kv_first_majority_tie"):
            counts["pre_kv_first_ties"] += 1
        if payload.get("no_channel_debate_majority_tie"):
            counts["no_channel_debate_ties"] += 1
        if payload.get("pre_kv_debate_majority_tie") or payload.get("debate_majority_tie"):
            counts["pre_kv_debate_ties"] += 1
        no_channel_debate_answer = payload.get("no_channel_debate_majority_answer")
        if no_channel_debate_transition and normalize_numeric(no_channel_debate_answer) is None:
            counts["no_channel_debate_parse_fail"] += 1
        pre_kv_debate_answer = payload.get("pre_kv_debate_majority_answer", payload.get("debate_majority_answer"))
        if pre_kv_debate_transition and normalize_numeric(pre_kv_debate_answer) is None:
            counts["pre_kv_debate_parse_fail"] += 1
    return counts


def _metrics(counts: Counter[str], total: int) -> dict[str, float]:
    no_channel_wrong = max(1, counts["BaW_to_C"] + counts["BaW_to_W"])
    no_channel_correct = max(1, counts["BaC_to_C"] + counts["BaC_to_W"])
    pre_kv_wrong = max(1, counts["PKW_to_C"] + counts["PKW_to_W"])
    pre_kv_correct = max(1, counts["PKC_to_C"] + counts["PKC_to_W"])
    no_channel_debate_wrong = max(1, counts["NCW_to_C"] + counts["NCW_to_W"])
    no_channel_debate_correct = max(1, counts["NCC_to_C"] + counts["NCC_to_W"])
    return {
        "no_channel_accuracy": counts["no_channel_correct"] / max(1, total),
        "pre_kv_first_accuracy": counts["pre_kv_first_correct"] / max(1, total),
        "no_channel_debate_accuracy": counts["no_channel_debate_correct"] / max(1, total),
        "pre_kv_debate_accuracy": counts["pre_kv_debate_correct"] / max(1, total),
        "debate_accuracy": counts["pre_kv_debate_correct"] / max(1, total),
        "pre_kv_delta_vs_no_channel": counts["pre_kv_first_correct"] - counts["no_channel_correct"],
        "no_channel_debate_delta_vs_no_channel": counts["no_channel_debate_correct"] - counts["no_channel_correct"],
        "pre_kv_debate_delta_vs_no_channel": counts["pre_kv_debate_correct"] - counts["no_channel_correct"],
        "pre_kv_debate_delta_vs_pre_kv_first": counts["pre_kv_debate_correct"] - counts["pre_kv_first_correct"],
        "pre_kv_debate_delta_vs_no_channel_debate": (
            counts["pre_kv_debate_correct"] - counts["no_channel_debate_correct"]
        ),
        "debate_delta_vs_no_channel": counts["pre_kv_debate_correct"] - counts["no_channel_correct"],
        "debate_delta_vs_pre_kv_first": counts["pre_kv_debate_correct"] - counts["pre_kv_first_correct"],
        "pre_kv_recovery_rate": counts["BaW_to_C"] / no_channel_wrong,
        "pre_kv_harm_rate": counts["BaC_to_W"] / no_channel_correct,
        "no_channel_debate_recovery_rate": counts["NCW_to_C"] / no_channel_debate_wrong,
        "no_channel_debate_harm_rate": counts["NCC_to_W"] / no_channel_debate_correct,
        "debate_recovery_from_pre_kv_rate": counts["PKW_to_C"] / pre_kv_wrong,
        "debate_harm_from_pre_kv_rate": counts["PKC_to_W"] / pre_kv_correct,
        "pre_kv_first_tie_rate": counts["pre_kv_first_ties"] / max(1, total),
        "no_channel_debate_tie_rate": counts["no_channel_debate_ties"] / max(1, total),
        "pre_kv_debate_tie_rate": counts["pre_kv_debate_ties"] / max(1, total),
        "debate_tie_rate": counts["pre_kv_debate_ties"] / max(1, total),
        "no_channel_debate_parse_fail_rate": counts["no_channel_debate_parse_fail"] / max(1, total),
        "pre_kv_debate_parse_fail_rate": counts["pre_kv_debate_parse_fail"] / max(1, total),
        "debate_parse_fail_rate": counts["pre_kv_debate_parse_fail"] / max(1, total),
    }


def main() -> int:
    args = parse_args()
    if args.agents < 1:
        raise SystemExit("--agents must be >= 1")

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_id)
    work_dir = Path(args.work_dir).expanduser().resolve()
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-mca-pre-kv-then-mad",
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
    records_path = output_dir / "records.jsonl"
    existing = _load_existing(records_path) if args.resume else []
    completed = {record.get("index") for record in existing}
    counts = _accumulate(existing) if args.resume else Counter()

    _progress(
        f"pre-kv-then-mad start run_id={args.run_id} rows={len(rows)} "
        f"existing={len(existing)} max_model_len={args.max_model_len}"
    )

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    started_at = time.time()
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    model_path = Path(args.model_path).expanduser().resolve()
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

    open_mode = "a" if args.resume else "w"
    with records_path.open(open_mode, encoding="utf-8", newline="\n") as handle:
        for row_idx, row in enumerate(rows):
            row_key = _record_key(row, row_idx)
            if args.resume and row_key in completed:
                continue
            question = prepare_question(str(row.get("question") or ""), args.benchmark)
            gold = row.get("answer")
            row_seed_key = row.get("id") or row_key
            generation_seeds: dict[str, Any] = {
                "base_seed": args.seed,
                "seed_key": row_seed_key,
                "sender_pre_state": [],
                "first_round_agents": [],
                "debate_agents": [],
            }
            _progress(f"row {row_idx + 1}/{len(rows)} live pre-kv start")

            sender_states = []
            for agent_idx in range(args.agents):
                seed = _stable_seed(args.seed, args.benchmark, args.split, row_seed_key, "sender_pre_state", agent_idx)
                _set_generation_seed(torch, seed)
                generation_seeds["sender_pre_state"].append(seed)
                state_prompt = _render_prompt(tokenizer, pre_state_prompt(question, agent_idx, "question_only"))
                state = _manual_generate_sender_state(
                    model,
                    tokenizer,
                    state_prompt,
                    max_new_tokens=0,
                    temperature=args.pre_state_temperature,
                    top_p=args.top_p,
                    max_model_len=args.max_model_len,
                    steering_layer=16,
                    keep_past_key_values=True,
                )
                sender_states.append(state)
                _progress(
                    f"row {row_idx + 1}/{len(rows)} pre-state sender {agent_idx + 1}/{args.agents} "
                    f"tokens={state.metadata['generated_tokens']}"
                )

            receiver_prompt_text = _render_prompt(tokenizer, [{"role": "user", "content": cot_prompt(question)}])
            no_channel_outputs = []
            no_channel_metadata = []
            for agent_idx in range(args.agents):
                seed = _stable_seed(args.seed, args.benchmark, args.split, row_seed_key, "first_round", agent_idx)
                generation_seeds["first_round_agents"].append(
                    {"agent_index": agent_idx, "no_channel": seed, "pre_kv": seed}
                )
                _set_generation_seed(torch, seed)
                output, metadata = _generate_receiver_from_state(
                    "kv",
                    model,
                    tokenizer,
                    receiver_prompt_text,
                    None,
                    channel_mode="none",
                    max_new_tokens=args.first_round_max_tokens,
                    temperature=args.first_round_temperature,
                    top_p=args.top_p,
                    max_model_len=args.max_model_len,
                    steering_layer=16,
                    steering_scale=1.0,
                )
                output["source_agent_index"] = agent_idx
                no_channel_outputs.append(output)
                no_channel_metadata.append({**metadata, "source_agent_index": agent_idx})
                _progress(f"row {row_idx + 1}/{len(rows)} no-channel first {agent_idx + 1}/{args.agents} done")
            no_channel_answer, no_channel_tie = majority_vote([item.get("parsed_answer") for item in no_channel_outputs])

            pre_kv_outputs = []
            pre_kv_metadata = []
            for agent_idx in range(args.agents):
                seed = generation_seeds["first_round_agents"][agent_idx]["pre_kv"]
                _set_generation_seed(torch, seed)
                output, metadata = _generate_receiver_from_state(
                    "kv",
                    model,
                    tokenizer,
                    receiver_prompt_text,
                    sender_states[agent_idx],
                    channel_mode="state",
                    max_new_tokens=args.first_round_max_tokens,
                    temperature=args.first_round_temperature,
                    top_p=args.top_p,
                    max_model_len=args.max_model_len,
                    steering_layer=16,
                    steering_scale=1.0,
                )
                output["source_agent_index"] = agent_idx
                pre_kv_outputs.append(output)
                pre_kv_metadata.append({**metadata, "source_agent_index": agent_idx})
                _progress(f"row {row_idx + 1}/{len(rows)} pre-kv receiver {agent_idx + 1}/{args.agents} done")
            pre_kv_answer, pre_kv_tie = majority_vote([item.get("parsed_answer") for item in pre_kv_outputs])

            no_channel_debate_prompt_text = _render_prompt(
                tokenizer,
                [{"role": "user", "content": debate_prompt(question, no_channel_outputs)}],
            )
            no_channel_debate_outputs = []
            no_channel_debate_metadata = []
            for agent_idx in range(args.agents):
                seed = _stable_seed(args.seed, args.benchmark, args.split, row_seed_key, "debate", agent_idx)
                generation_seeds["debate_agents"].append(
                    {"agent_index": agent_idx, "no_channel_debate": seed, "pre_kv_debate": seed}
                )
                _set_generation_seed(torch, seed)
                output, metadata = _generate_receiver_from_state(
                    "kv",
                    model,
                    tokenizer,
                    no_channel_debate_prompt_text,
                    None,
                    channel_mode="none",
                    max_new_tokens=args.debate_max_tokens,
                    temperature=args.debate_temperature,
                    top_p=args.top_p,
                    max_model_len=args.max_model_len,
                    steering_layer=16,
                    steering_scale=1.0,
                )
                output["source_agent_index"] = agent_idx
                no_channel_debate_outputs.append(output)
                no_channel_debate_metadata.append({**metadata, "source_agent_index": agent_idx})
                _progress(f"row {row_idx + 1}/{len(rows)} no-channel debate {agent_idx + 1}/{args.agents} done")
            no_channel_debate_answer, no_channel_debate_tie = majority_vote(answer_list(no_channel_debate_outputs))

            pre_kv_debate_prompt_text = _render_prompt(
                tokenizer,
                [{"role": "user", "content": debate_prompt(question, pre_kv_outputs)}],
            )
            pre_kv_debate_outputs = []
            pre_kv_debate_metadata = []
            for agent_idx in range(args.agents):
                seed = generation_seeds["debate_agents"][agent_idx]["pre_kv_debate"]
                _set_generation_seed(torch, seed)
                output, metadata = _generate_receiver_from_state(
                    "kv",
                    model,
                    tokenizer,
                    pre_kv_debate_prompt_text,
                    None,
                    channel_mode="none",
                    max_new_tokens=args.debate_max_tokens,
                    temperature=args.debate_temperature,
                    top_p=args.top_p,
                    max_model_len=args.max_model_len,
                    steering_layer=16,
                    steering_scale=1.0,
                )
                output["source_agent_index"] = agent_idx
                pre_kv_debate_outputs.append(output)
                pre_kv_debate_metadata.append({**metadata, "source_agent_index": agent_idx})
                _progress(f"row {row_idx + 1}/{len(rows)} pre-kv debate {agent_idx + 1}/{args.agents} done")
            pre_kv_debate_answer, pre_kv_debate_tie = majority_vote(answer_list(pre_kv_debate_outputs))

            no_channel_ok = is_correct(no_channel_answer, gold)
            pre_kv_ok = is_correct(pre_kv_answer, gold)
            no_channel_debate_ok = is_correct(no_channel_debate_answer, gold)
            pre_kv_debate_ok = is_correct(pre_kv_debate_answer, gold)
            first_transition = _transition("Ba", no_channel_ok, pre_kv_ok)
            no_channel_debate_transition = _transition("NC", no_channel_ok, no_channel_debate_ok)
            pre_kv_debate_transition = _transition("PK", pre_kv_ok, pre_kv_debate_ok)

            counts["total"] += 1
            if no_channel_ok:
                counts["no_channel_correct"] += 1
            if pre_kv_ok:
                counts["pre_kv_first_correct"] += 1
            if no_channel_debate_ok:
                counts["no_channel_debate_correct"] += 1
            if pre_kv_debate_ok:
                counts["pre_kv_debate_correct"] += 1
            counts[first_transition] += 1
            counts[no_channel_debate_transition] += 1
            counts[pre_kv_debate_transition] += 1
            if pre_kv_tie:
                counts["pre_kv_first_ties"] += 1
            if no_channel_debate_tie:
                counts["no_channel_debate_ties"] += 1
            if pre_kv_debate_tie:
                counts["pre_kv_debate_ties"] += 1
            if normalize_numeric(no_channel_debate_answer) is None:
                counts["no_channel_debate_parse_fail"] += 1
            if normalize_numeric(pre_kv_debate_answer) is None:
                counts["pre_kv_debate_parse_fail"] += 1

            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row_key,
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "mca_pre_kv_then_mad": {
                    "stage": "live_question_only_kv_then_standard_mad_text_round",
                    "agents": args.agents,
                    "state_source": "live_pre_answer_sender_pass",
                    "generation_seeds": generation_seeds,
                    "sender_state_metadata": [state.metadata for state in sender_states],
                    "no_channel_first_outputs": no_channel_outputs,
                    "no_channel_first_metadata": no_channel_metadata,
                    "no_channel_first_majority_answer": no_channel_answer,
                    "no_channel_first_majority_tie": no_channel_tie,
                    "pre_kv_first_outputs": pre_kv_outputs,
                    "pre_kv_receiver_metadata": pre_kv_metadata,
                    "pre_kv_first_majority_answer": pre_kv_answer,
                    "pre_kv_first_majority_tie": pre_kv_tie,
                    "no_channel_debate_inputs_source": "no_channel_first_outputs_text",
                    "no_channel_debate_outputs": no_channel_debate_outputs,
                    "no_channel_debate_metadata": no_channel_debate_metadata,
                    "no_channel_debate_majority_answer": no_channel_debate_answer,
                    "no_channel_debate_majority_tie": no_channel_debate_tie,
                    "pre_kv_debate_inputs_source": "pre_kv_first_outputs_text",
                    "pre_kv_debate_outputs": pre_kv_debate_outputs,
                    "pre_kv_debate_metadata": pre_kv_debate_metadata,
                    "pre_kv_debate_majority_answer": pre_kv_debate_answer,
                    "pre_kv_debate_majority_tie": pre_kv_debate_tie,
                    "debate_inputs_source": "pre_kv_first_outputs_text",
                    "debate_outputs": pre_kv_debate_outputs,
                    "debate_majority_answer": pre_kv_debate_answer,
                    "debate_majority_tie": pre_kv_debate_tie,
                    "first_round_transition": first_transition,
                    "no_channel_debate_transition_from_first_round": no_channel_debate_transition,
                    "pre_kv_debate_transition_from_first_round": pre_kv_debate_transition,
                    "debate_transition_from_first_round": pre_kv_debate_transition,
                    "no_channel_debate_correct": no_channel_debate_ok,
                    "pre_kv_debate_correct": pre_kv_debate_ok,
                    "debate_correct": pre_kv_debate_ok,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            handle.flush()
            _progress(
                f"row {row_idx + 1}/{len(rows)} written first={first_transition} "
                f"nc_debate={no_channel_debate_transition} pk_debate={pre_kv_debate_transition} "
                f"no_channel={no_channel_answer} pre_kv={pre_kv_answer} "
                f"nc_debate_answer={no_channel_debate_answer} pk_debate_answer={pre_kv_debate_answer}"
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
        "rows": counts["total"],
        "agents": args.agents,
        "pre_state_stage": "question_only",
        "first_round_temperature": args.first_round_temperature,
        "debate_temperature": args.debate_temperature,
        "top_p": args.top_p,
        "first_round_max_tokens": args.first_round_max_tokens,
        "debate_max_tokens": args.debate_max_tokens,
        "max_model_len": args.max_model_len,
        "counts": dict(counts),
        "metrics": _metrics(counts, total),
        "elapsed_seconds": elapsed,
        "records_path": str(records_path),
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {output_dir.name}\n\n")
        handle.write(f"- Rows: {counts['total']}\n")
        handle.write("- Stage: A/B first round, then C/D Standard MAD text debate\n")
        handle.write(f"- No-channel first accuracy: {summary['metrics']['no_channel_accuracy']:.4f}\n")
        handle.write(f"- Pre-KV first accuracy: {summary['metrics']['pre_kv_first_accuracy']:.4f}\n")
        handle.write(f"- No-channel + MAD accuracy: {summary['metrics']['no_channel_debate_accuracy']:.4f}\n")
        handle.write(f"- Pre-KV + MAD accuracy: {summary['metrics']['pre_kv_debate_accuracy']:.4f}\n")
        handle.write(f"- Pre-KV delta vs no-channel: {summary['metrics']['pre_kv_delta_vs_no_channel']:+d}\n")
        handle.write(
            f"- No-channel + MAD delta vs no-channel first: "
            f"{summary['metrics']['no_channel_debate_delta_vs_no_channel']:+d}\n"
        )
        handle.write(
            f"- Pre-KV + MAD delta vs no-channel first: "
            f"{summary['metrics']['pre_kv_debate_delta_vs_no_channel']:+d}\n"
        )
        handle.write(
            f"- Pre-KV + MAD delta vs Pre-KV first: "
            f"{summary['metrics']['pre_kv_debate_delta_vs_pre_kv_first']:+d}\n"
        )
        handle.write(
            f"- Pre-KV + MAD delta vs no-channel + MAD: "
            f"{summary['metrics']['pre_kv_debate_delta_vs_no_channel_debate']:+d}\n"
        )
        handle.write(f"- Pre-KV recovery rate: {summary['metrics']['pre_kv_recovery_rate']:.4f}\n")
        handle.write(f"- Pre-KV harm rate: {summary['metrics']['pre_kv_harm_rate']:.4f}\n")
        handle.write(
            f"- No-channel + MAD recovery rate: "
            f"{summary['metrics']['no_channel_debate_recovery_rate']:.4f}\n"
        )
        handle.write(
            f"- No-channel + MAD harm rate: "
            f"{summary['metrics']['no_channel_debate_harm_rate']:.4f}\n"
        )
        handle.write(
            f"- Pre-KV + MAD recovery from Pre-KV wrong rate: "
            f"{summary['metrics']['debate_recovery_from_pre_kv_rate']:.4f}\n"
        )
        handle.write(
            f"- Pre-KV + MAD harm from Pre-KV correct rate: "
            f"{summary['metrics']['debate_harm_from_pre_kv_rate']:.4f}\n"
        )
        handle.write(f"- No-channel + MAD tie rate: {summary['metrics']['no_channel_debate_tie_rate']:.4f}\n")
        handle.write(f"- Pre-KV + MAD tie rate: {summary['metrics']['pre_kv_debate_tie_rate']:.4f}\n")
        handle.write(
            f"- No-channel + MAD parse fail rate: "
            f"{summary['metrics']['no_channel_debate_parse_fail_rate']:.4f}\n"
        )
        handle.write(
            f"- Pre-KV + MAD parse fail rate: "
            f"{summary['metrics']['pre_kv_debate_parse_fail_rate']:.4f}\n"
        )
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
