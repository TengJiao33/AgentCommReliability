#!/usr/bin/env python3
"""Run natural-search-state delta communication diagnostics.

This runner is deliberately stricter than the earlier Pre-KV variants:

* senders solve with the ordinary from-scratch CoT prompt;
* no sender is asked to write a plan, sketch, or micro commitment;
* peer state is captured from normal decode steps via hooks;
* receiver generations never continue from peer ``past_key_values``;
* controls compare same-question deltas against other-question and random
  same-norm vectors.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mca_hidden_channel_runner import _model_layers, _progress, _sample_next_token
from run_basic_mad import is_correct, load_rows, majority_vote, normalize_numeric, resolve_inside
from run_mad_mm import cot_prompt, extract_xml_answer, prepare_question
from run_mca_soft_prefix import _render_prompt, _torch_dtype


DEFAULT_CONDITIONS = (
    "same_question_peer_delta",
    "other_question_peer_delta",
    "random_gaussian_same_norm",
    "same_question_peer_absolute",
)


@dataclass
class StepState:
    absolute: Any
    delta: Any | None
    absolute_norm: float
    delta_norm: float
    token_id: int
    token_window: str


@dataclass
class AgentTrace:
    agent_index: int
    seed: int
    output: dict[str, Any]
    layer_steps: dict[int, dict[int, StepState]]
    generated_token_ids: list[int]


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
    parser.add_argument("--layers", default="22", help="Comma-separated transformer layer ids.")
    parser.add_argument("--checkpoints", default="16,32,64,96", help="Comma-separated decode-step ids.")
    parser.add_argument("--conditions", default=",".join(DEFAULT_CONDITIONS))
    parser.add_argument("--steering-scale", type=float, default=0.03)
    parser.add_argument("--message-max-norm", type=float, default=1.0)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-new-tokens", type=int, default=1536)
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    return parser.parse_args()


def _parse_int_csv(value: str, *, name: str) -> list[int]:
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        raise SystemExit(f"--{name} must not be empty")
    parsed = [int(item) for item in items]
    if any(item < 0 for item in parsed):
        raise SystemExit(f"--{name} must contain non-negative integers")
    return parsed


def _parse_str_csv(value: str, *, name: str) -> list[str]:
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        raise SystemExit(f"--{name} must not be empty")
    return items


def _stable_seed(base_seed: int, *parts: Any) -> int:
    payload = "\x1f".join([str(base_seed), *(str(part) for part in parts)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % (2**31)


def _set_generation_seed(torch_module: Any, seed: int) -> None:
    torch_module.manual_seed(seed)
    if torch_module.cuda.is_available():
        torch_module.cuda.manual_seed_all(seed)


def _parse_output(text: str) -> dict[str, Any]:
    parsed = extract_xml_answer(text)
    return {
        "output": text,
        "parsed_answer": parsed,
        "normalized_answer": normalize_numeric(parsed),
        "mean_selected_logprob": None,
        "sequence_score": None,
    }


def _transition(prefix: str, before_ok: bool, after_ok: bool) -> str:
    if before_ok and after_ok:
        return f"{prefix}C_to_C"
    if before_ok and not after_ok:
        return f"{prefix}C_to_W"
    if not before_ok and after_ok:
        return f"{prefix}W_to_C"
    return f"{prefix}W_to_W"


def _vector_norm(vector: Any | None) -> float:
    if vector is None:
        return 0.0
    import torch

    return float(torch.linalg.vector_norm(vector.float()).item())


def _clip_vector(vector: Any, max_norm: float) -> tuple[Any, dict[str, Any]]:
    import torch

    raw_norm = torch.linalg.vector_norm(vector.float()).clamp_min(1e-12)
    clipped = False
    if max_norm > 0 and float(raw_norm.item()) > max_norm:
        vector = vector * (max_norm / raw_norm.to(dtype=vector.dtype))
        clipped = True
    effective_norm = torch.linalg.vector_norm(vector.float())
    return vector, {
        "raw_norm": float(raw_norm.item()),
        "effective_norm": float(effective_norm.item()),
        "clipped": clipped,
        "max_norm": max_norm,
    }


def _mean_vectors(vectors: list[Any]) -> Any | None:
    if not vectors:
        return None
    import torch

    return torch.stack([vector.float() for vector in vectors], dim=0).mean(dim=0)


def _random_like_same_norm(reference: Any, *, seed: int) -> Any:
    import torch

    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    random_vec = torch.randn(reference.shape, generator=generator, dtype=torch.float32)
    random_norm = torch.linalg.vector_norm(random_vec).clamp_min(1e-12)
    target_norm = torch.linalg.vector_norm(reference.float())
    return random_vec * (target_norm / random_norm)


def _other_row_index(row_idx: int, total_rows: int) -> int | None:
    if total_rows <= 1:
        return None
    if row_idx > 0:
        return row_idx - 1
    return 1


def _decode_window(tokenizer: Any, generated_token_ids: list[int], step: int, window_tokens: int = 20) -> str:
    start = max(0, step - window_tokens)
    token_ids = generated_token_ids[start:step]
    if not token_ids:
        return ""
    return tokenizer.decode(token_ids, skip_special_tokens=True)


def _state_summary(state: StepState | None) -> dict[str, Any]:
    if state is None:
        return {"available": False}
    return {
        "available": True,
        "absolute_norm": state.absolute_norm,
        "delta_norm": state.delta_norm,
        "token_id": state.token_id,
        "token_window": state.token_window,
    }


def _trace_metadata(trace: AgentTrace, *, layers: list[int], checkpoints: list[int]) -> dict[str, Any]:
    return {
        "agent_index": trace.agent_index,
        "seed": trace.seed,
        "generated_tokens": len(trace.generated_token_ids),
        "parsed_answer": trace.output.get("parsed_answer"),
        "normalized_answer": trace.output.get("normalized_answer"),
        "checkpoints": {
            str(layer): {
                str(step): _state_summary(trace.layer_steps.get(layer, {}).get(step))
                for step in checkpoints
            }
            for layer in layers
        },
    }


def _build_schedule(
    *,
    condition: str,
    references_by_row: list[list[AgentTrace]],
    row_idx: int,
    agent_idx: int,
    layers: list[int],
    checkpoints: list[int],
    message_max_norm: float,
    seed: int,
) -> tuple[dict[int, dict[int, Any]], dict[str, Any]]:
    schedule: dict[int, dict[int, Any]] = {}
    message_meta: dict[str, Any] = {
        "condition": condition,
        "active_messages": 0,
        "messages": [],
    }
    total_rows = len(references_by_row)
    other_idx = _other_row_index(row_idx, total_rows)
    for step in checkpoints:
        for layer in layers:
            candidates = []
            source_rows: list[int] = []
            source_agents: list[int] = []
            if condition in {"same_question_peer_delta", "same_question_peer_absolute"}:
                for peer_idx, trace in enumerate(references_by_row[row_idx]):
                    if peer_idx == agent_idx:
                        continue
                    state = trace.layer_steps.get(layer, {}).get(step)
                    if state is None:
                        continue
                    vector = state.delta if condition.endswith("delta") else state.absolute
                    if vector is not None:
                        candidates.append(vector)
                        source_rows.append(row_idx)
                        source_agents.append(peer_idx)
            elif condition == "other_question_peer_delta" and other_idx is not None:
                for peer_idx, trace in enumerate(references_by_row[other_idx]):
                    state = trace.layer_steps.get(layer, {}).get(step)
                    if state is None or state.delta is None:
                        continue
                    candidates.append(state.delta)
                    source_rows.append(other_idx)
                    source_agents.append(peer_idx)
            elif condition == "self_previous_delta":
                previous_steps = [candidate for candidate in checkpoints if candidate < step]
                previous_step = previous_steps[-1] if previous_steps else None
                if previous_step is not None:
                    state = references_by_row[row_idx][agent_idx].layer_steps.get(layer, {}).get(previous_step)
                    if state is not None and state.delta is not None:
                        candidates.append(state.delta)
                        source_rows.append(row_idx)
                        source_agents.append(agent_idx)
            elif condition == "zero_delta":
                own_state = references_by_row[row_idx][agent_idx].layer_steps.get(layer, {}).get(step)
                if own_state is not None:
                    candidates.append(own_state.absolute.float() * 0.0)
                    source_rows.append(row_idx)
                    source_agents.append(agent_idx)

            vector = _mean_vectors(candidates)
            if condition == "random_gaussian_same_norm":
                peer_schedule, peer_meta = _build_schedule(
                    condition="same_question_peer_delta",
                    references_by_row=references_by_row,
                    row_idx=row_idx,
                    agent_idx=agent_idx,
                    layers=[layer],
                    checkpoints=[step],
                    message_max_norm=0.0,
                    seed=seed,
                )
                reference = peer_schedule.get(step, {}).get(layer)
                if reference is not None:
                    vector = _random_like_same_norm(
                        reference,
                        seed=_stable_seed(seed, row_idx, agent_idx, layer, step, "random_gaussian_same_norm"),
                    )
                    source_rows = [row_idx]
                    source_agents = [-1]
                message_meta.setdefault("reference_peer_meta", []).append(peer_meta)

            if vector is None:
                message_meta["messages"].append(
                    {
                        "step": step,
                        "layer": layer,
                        "active": False,
                        "source_rows": source_rows,
                        "source_agents": source_agents,
                    }
                )
                continue
            vector, clip_meta = _clip_vector(vector, message_max_norm)
            schedule.setdefault(step, {})[layer] = vector.detach().cpu()
            message_meta["active_messages"] += 1
            message_meta["messages"].append(
                {
                    "step": step,
                    "layer": layer,
                    "active": True,
                    "source_rows": source_rows,
                    "source_agents": source_agents,
                    **clip_meta,
                }
            )
    return schedule, message_meta


def _generate_trace(
    *,
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    agent_index: int,
    seed: int,
    layers: list[int],
    checkpoints: list[int],
    injection_schedule: dict[int, dict[int, Any]] | None,
    steering_scale: float,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    max_model_len: int,
) -> AgentTrace:
    import torch

    device = next(model.parameters()).device
    max_prompt_tokens = max(1, max_model_len - max_new_tokens - 8)
    encoded = tokenizer(
        prompt_text,
        return_tensors="pt",
        truncation=True,
        max_length=max_prompt_tokens,
    )
    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded["attention_mask"].to(device)
    model_layers = _model_layers(model)
    if max(layers) >= len(model_layers):
        raise SystemExit(f"requested layer {max(layers)} but model only has {len(model_layers)} layers")

    current_step = 0
    generated_token_ids: list[int] = []
    last_hidden_by_layer: dict[int, Any] = {}
    layer_steps: dict[int, dict[int, StepState]] = {layer: {} for layer in layers}
    checkpoint_set = set(checkpoints)
    schedule = injection_schedule or {}
    handles = []

    def make_hook(layer_id: int):
        def hook(_module: Any, args: tuple[Any, ...]) -> tuple[Any, ...] | None:
            hidden = args[0]
            if current_step <= 0:
                return None
            current_hidden = hidden.detach()[0, -1, :].float().cpu()
            previous = last_hidden_by_layer.get(layer_id)
            delta = current_hidden - previous if previous is not None else None
            last_hidden_by_layer[layer_id] = current_hidden
            if current_step in checkpoint_set:
                token_id = generated_token_ids[current_step - 1] if len(generated_token_ids) >= current_step else -1
                layer_steps[layer_id][current_step] = StepState(
                    absolute=current_hidden,
                    delta=delta,
                    absolute_norm=_vector_norm(current_hidden),
                    delta_norm=_vector_norm(delta),
                    token_id=token_id,
                    token_window=_decode_window(tokenizer, generated_token_ids, current_step),
                )
            injection = schedule.get(current_step, {}).get(layer_id)
            if injection is None:
                return None
            vector = injection.to(device=device, dtype=hidden.dtype)
            steered = hidden.clone()
            steered[:, -1, :] = steered[:, -1, :] + vector * steering_scale
            return (steered,) + args[1:]

        return hook

    for layer_id in layers:
        handles.append(model_layers[layer_id].register_forward_pre_hook(make_hook(layer_id)))

    generated_ids = []
    past = None
    try:
        with torch.inference_mode():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, use_cache=True)
            past = outputs.past_key_values
            next_logits = outputs.logits[:, -1, :]
            total_len = int(input_ids.shape[1])
            eos_token_id = tokenizer.eos_token_id
            for _ in range(max_new_tokens):
                next_token = _sample_next_token(next_logits, temperature=temperature, top_p=top_p)
                token_value = int(next_token.item())
                if eos_token_id is not None and token_value == int(eos_token_id):
                    break
                generated_ids.append(next_token.detach().cpu())
                generated_token_ids.append(token_value)
                current_step = len(generated_token_ids)
                total_len += 1
                attention_mask = torch.ones((1, total_len), device=device, dtype=torch.long)
                position_ids = torch.tensor([[total_len - 1]], device=device, dtype=torch.long)
                outputs = model(
                    input_ids=next_token,
                    attention_mask=attention_mask,
                    position_ids=position_ids,
                    past_key_values=past,
                    use_cache=True,
                )
                past = outputs.past_key_values
                next_logits = outputs.logits[:, -1, :]
    finally:
        for handle in handles:
            handle.remove()

    if generated_ids:
        tokens = torch.cat(generated_ids, dim=1)[0]
        text = tokenizer.decode(tokens, skip_special_tokens=True)
    else:
        text = ""
    output = _parse_output(text)
    output["agent_index"] = agent_index
    output["output_tokens"] = len(generated_token_ids)
    output["prompt_tokens"] = int(input_ids.shape[1])
    return AgentTrace(
        agent_index=agent_index,
        seed=seed,
        output=output,
        layer_steps=layer_steps,
        generated_token_ids=generated_token_ids,
    )


def _condition_counts_update(
    counts: Counter[str],
    *,
    condition: str,
    baseline_ok: bool,
    condition_ok: bool,
    answer_changed: bool,
    tie: bool,
) -> None:
    prefix = f"{condition}:"
    counts[f"{prefix}total"] += 1
    if condition_ok:
        counts[f"{prefix}correct"] += 1
    transition = _transition("Ba", baseline_ok, condition_ok)
    counts[f"{prefix}{transition}"] += 1
    if answer_changed:
        counts[f"{prefix}answer_changed"] += 1
    if tie:
        counts[f"{prefix}majority_tie"] += 1


def _condition_metrics(counts: Counter[str], condition: str) -> dict[str, float | int]:
    prefix = f"{condition}:"
    total = max(1, counts[f"{prefix}total"])
    wrong = max(1, counts[f"{prefix}BaW_to_C"] + counts[f"{prefix}BaW_to_W"])
    correct = max(1, counts[f"{prefix}BaC_to_C"] + counts[f"{prefix}BaC_to_W"])
    return {
        "rows": counts[f"{prefix}total"],
        "accuracy": counts[f"{prefix}correct"] / total,
        "delta_vs_baseline": counts[f"{prefix}correct"] - counts["baseline_correct"],
        "recovery_rate": counts[f"{prefix}BaW_to_C"] / wrong,
        "harm_rate": counts[f"{prefix}BaC_to_W"] / correct,
        "answer_change_rate": counts[f"{prefix}answer_changed"] / total,
        "majority_tie_rate": counts[f"{prefix}majority_tie"] / total,
    }


def main() -> int:
    args = parse_args()
    if args.agents < 2:
        raise SystemExit("--agents must be >= 2")
    layers = _parse_int_csv(args.layers, name="layers")
    checkpoints = _parse_int_csv(args.checkpoints, name="checkpoints")
    conditions = _parse_str_csv(args.conditions, name="conditions")
    allowed_conditions = set(DEFAULT_CONDITIONS) | {"zero_delta", "self_previous_delta"}
    unknown = sorted(set(conditions) - allowed_conditions)
    if unknown:
        raise SystemExit(f"unknown conditions: {', '.join(unknown)}")

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_id)
    work_dir = Path(args.work_dir).expanduser().resolve()
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-mca-natural-search-delta",
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
    _progress(
        f"natural-search-delta start run_id={args.run_id} rows={len(rows)} "
        f"layers={layers} checkpoints={checkpoints} conditions={conditions}"
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

    prompt_texts = [
        _render_prompt(tokenizer, [{"role": "user", "content": cot_prompt(prepare_question(str(row.get("question") or ""), args.benchmark))}])
        for row in rows
    ]
    row_seed_keys = [row.get("id") or row.get("index", idx) for idx, row in enumerate(rows)]

    references_by_row: list[list[AgentTrace]] = []
    baseline_majorities: list[str | None] = []
    baseline_ties: list[bool] = []
    baseline_correct: list[bool] = []
    counts: Counter[str] = Counter()

    for row_idx, row in enumerate(rows):
        gold = row.get("answer")
        row_traces = []
        for agent_idx in range(args.agents):
            seed = _stable_seed(args.seed, args.benchmark, args.split, row_seed_keys[row_idx], "agent", agent_idx)
            _set_generation_seed(torch, seed)
            trace = _generate_trace(
                model=model,
                tokenizer=tokenizer,
                prompt_text=prompt_texts[row_idx],
                agent_index=agent_idx,
                seed=seed,
                layers=layers,
                checkpoints=checkpoints,
                injection_schedule=None,
                steering_scale=args.steering_scale,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                max_model_len=args.max_model_len,
            )
            row_traces.append(trace)
            _progress(f"row {row_idx + 1}/{len(rows)} reference agent {agent_idx + 1}/{args.agents} done")
        answer, tie = majority_vote([trace.output.get("parsed_answer") for trace in row_traces])
        ok = is_correct(answer, gold)
        references_by_row.append(row_traces)
        baseline_majorities.append(answer)
        baseline_ties.append(tie)
        baseline_correct.append(ok)
        counts["total"] += 1
        if ok:
            counts["baseline_correct"] += 1
        if tie:
            counts["baseline_majority_tie"] += 1

    records_path = output_dir / "records.jsonl"
    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row_idx, row in enumerate(rows):
            gold = row.get("answer")
            record_conditions: dict[str, Any] = {}
            baseline_answer = baseline_majorities[row_idx]
            baseline_ok = baseline_correct[row_idx]
            for condition in conditions:
                condition_outputs = []
                condition_metadata = []
                for agent_idx in range(args.agents):
                    seed = _stable_seed(args.seed, args.benchmark, args.split, row_seed_keys[row_idx], "agent", agent_idx)
                    schedule, message_meta = _build_schedule(
                        condition=condition,
                        references_by_row=references_by_row,
                        row_idx=row_idx,
                        agent_idx=agent_idx,
                        layers=layers,
                        checkpoints=checkpoints,
                        message_max_norm=args.message_max_norm,
                        seed=args.seed,
                    )
                    _set_generation_seed(torch, seed)
                    trace = _generate_trace(
                        model=model,
                        tokenizer=tokenizer,
                        prompt_text=prompt_texts[row_idx],
                        agent_index=agent_idx,
                        seed=seed,
                        layers=layers,
                        checkpoints=checkpoints,
                        injection_schedule=schedule,
                        steering_scale=args.steering_scale,
                        max_new_tokens=args.max_new_tokens,
                        temperature=args.temperature,
                        top_p=args.top_p,
                        max_model_len=args.max_model_len,
                    )
                    condition_outputs.append(trace.output)
                    condition_metadata.append(
                        {
                            "agent_index": agent_idx,
                            "seed": seed,
                            "message_metadata": message_meta,
                            "trace_metadata": _trace_metadata(trace, layers=layers, checkpoints=checkpoints),
                        }
                    )
                    _progress(
                        f"row {row_idx + 1}/{len(rows)} condition={condition} "
                        f"agent {agent_idx + 1}/{args.agents} done"
                    )
                answer, tie = majority_vote([item.get("parsed_answer") for item in condition_outputs])
                ok = is_correct(answer, gold)
                answer_changed = normalize_numeric(answer) != normalize_numeric(baseline_answer)
                _condition_counts_update(
                    counts,
                    condition=condition,
                    baseline_ok=baseline_ok,
                    condition_ok=ok,
                    answer_changed=answer_changed,
                    tie=tie,
                )
                record_conditions[condition] = {
                    "outputs": condition_outputs,
                    "metadata": condition_metadata,
                    "majority_answer": answer,
                    "majority_tie": tie,
                    "correct": ok,
                    "transition": _transition("Ba", baseline_ok, ok),
                    "answer_changed_vs_baseline": answer_changed,
                }

            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row.get("index", row_idx),
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "mca_natural_search_delta": {
                    "protocol": "mca-natural-search-delta-v0",
                    "agents": args.agents,
                    "layers": layers,
                    "checkpoints": checkpoints,
                    "conditions": conditions,
                    "steering_scale": args.steering_scale,
                    "message_max_norm": args.message_max_norm,
                    "temperature": args.temperature,
                    "top_p": args.top_p,
                    "max_new_tokens": args.max_new_tokens,
                    "state_source": "ordinary_cot_decode_trace",
                    "uses_peer_past_key_values": False,
                    "sender_prompt_intervention": False,
                    "baseline_outputs": [trace.output for trace in references_by_row[row_idx]],
                    "baseline_trace_metadata": [
                        _trace_metadata(trace, layers=layers, checkpoints=checkpoints)
                        for trace in references_by_row[row_idx]
                    ],
                    "baseline_majority_answer": baseline_answer,
                    "baseline_majority_tie": baseline_ties[row_idx],
                    "baseline_correct": baseline_ok,
                    "condition_results": record_conditions,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            handle.flush()
            _progress(f"row {row_idx + 1}/{len(rows)} written baseline={baseline_answer}")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    elapsed = time.time() - started_at
    total = max(1, counts["total"])
    metrics = {
        "baseline_accuracy": counts["baseline_correct"] / total,
        "baseline_majority_tie_rate": counts["baseline_majority_tie"] / total,
        "conditions": {condition: _condition_metrics(counts, condition) for condition in conditions},
    }
    summary = {
        "run_id": args.run_id,
        "model_key": args.model_key,
        "model_path": str(model_path),
        "benchmark": args.benchmark,
        "split": args.split,
        "rows": counts["total"],
        "agents": args.agents,
        "layers": layers,
        "checkpoints": checkpoints,
        "conditions": conditions,
        "steering_scale": args.steering_scale,
        "message_max_norm": args.message_max_norm,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_new_tokens": args.max_new_tokens,
        "max_model_len": args.max_model_len,
        "state_source": "ordinary_cot_decode_trace",
        "uses_peer_past_key_values": False,
        "sender_prompt_intervention": False,
        "counts": dict(counts),
        "metrics": metrics,
        "elapsed_seconds": elapsed,
        "records_path": str(records_path),
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {output_dir.name}\n\n")
        handle.write(f"- Rows: {counts['total']}\n")
        handle.write("- Protocol: natural-search-delta-v0\n")
        handle.write("- State source: ordinary CoT decode trace\n")
        handle.write("- Sender prompt intervention: false\n")
        handle.write("- Uses peer past_key_values: false\n")
        handle.write(f"- Layers: {layers}\n")
        handle.write(f"- Checkpoints: {checkpoints}\n")
        handle.write(f"- Steering scale: {args.steering_scale}\n")
        handle.write(f"- Message max norm: {args.message_max_norm}\n")
        handle.write(f"- Baseline accuracy: {metrics['baseline_accuracy']:.4f}\n")
        for condition in conditions:
            item = metrics["conditions"][condition]
            handle.write(
                f"- {condition}: accuracy={item['accuracy']:.4f}, "
                f"delta={item['delta_vs_baseline']:+d}, "
                f"recovery={item['recovery_rate']:.4f}, harm={item['harm_rate']:.4f}, "
                f"change={item['answer_change_rate']:.4f}\n"
            )
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    _progress(f"natural-search-delta complete elapsed_seconds={elapsed:.1f}")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
