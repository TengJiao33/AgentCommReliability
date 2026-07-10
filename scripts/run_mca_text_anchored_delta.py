#!/usr/bin/env python3
"""Run text-anchored hidden-delta communication diagnostics.

Protocol sketch:

* sender agents generate structured units with a short text anchor and hidden
  work text;
* receivers can see only the anchors;
* hidden deltas captured from each sender work span are injected at the matching
  anchor positions during receiver prompt prefill.

This is intentionally close to ``run_mca_natural_search_delta.py`` so the same
hard controls are available: random same-norm payloads, other-question payloads,
BaW/BaC transitions, and answer-change rates.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mca_hidden_channel_runner import _model_layers, _progress, _sample_next_token
from run_basic_mad import is_correct, load_rows, majority_vote, normalize_numeric, resolve_inside
from run_mad_mm import cot_prompt, extract_xml_answer, prepare_question
from run_mca_natural_search_delta import (
    _clip_vector,
    _condition_counts_update,
    _condition_metrics,
    _mean_vectors,
    _other_row_index,
    _parse_int_csv,
    _parse_str_csv,
    _random_like_same_norm,
    _set_generation_seed,
    _stable_seed,
    _transition,
    _vector_norm,
)
from run_mca_soft_prefix import _render_prompt, _torch_dtype


DEFAULT_CONDITIONS = (
    "anchor_only",
    "raw_delta",
    "anchor_delta",
    "anchor_random_same_norm",
    "anchor_other_question_delta",
)

UNIT_RE = re.compile(
    r"<unit>\s*<anchor>(?P<anchor>.*?)</anchor>\s*<work>(?P<work>.*?)</work>\s*</unit>",
    flags=re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class AnchorUnit:
    unit_index: int
    anchor: str
    work: str
    work_start: int
    work_end: int


@dataclass
class AnchorPayload:
    anchor: str
    vector_by_layer: dict[int, Any]
    source_row: int
    source_agent: int
    source_unit: int
    token_indices: list[int]


@dataclass
class SenderTrace:
    agent_index: int
    seed: int
    output: dict[str, Any]
    units: list[AnchorUnit]
    payloads: list[AnchorPayload]
    generated_token_ids: list[int]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class PromptInjection:
    layer: int
    token_position: int
    vector: Any
    label: str


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
    parser.add_argument("--conditions", default=",".join(DEFAULT_CONDITIONS))
    parser.add_argument("--max-anchors", type=int, default=4)
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


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_anchor_units(text: str) -> list[AnchorUnit]:
    units: list[AnchorUnit] = []
    for idx, match in enumerate(UNIT_RE.finditer(text)):
        anchor = _normalize_space(match.group("anchor"))
        work = match.group("work").strip()
        if not anchor or not work:
            continue
        units.append(
            AnchorUnit(
                unit_index=idx,
                anchor=anchor,
                work=work,
                work_start=match.start("work"),
                work_end=match.end("work"),
            )
        )
    return units


def _parse_output(text: str) -> dict[str, Any]:
    parsed = extract_xml_answer(text)
    return {
        "output": text,
        "parsed_answer": parsed,
        "normalized_answer": normalize_numeric(parsed),
        "mean_selected_logprob": None,
        "sequence_score": None,
    }


def _token_char_spans(tokenizer: Any, token_ids: list[int]) -> tuple[list[tuple[int, int]], str]:
    spans: list[tuple[int, int]] = []
    decoded = ""
    for idx in range(len(token_ids)):
        previous_len = len(decoded)
        decoded = tokenizer.decode(token_ids[: idx + 1], skip_special_tokens=True)
        spans.append((previous_len, len(decoded)))
    return spans, decoded


def _overlapping_token_indices(
    token_spans: list[tuple[int, int]],
    start: int,
    end: int,
) -> list[int]:
    return [
        idx
        for idx, (token_start, token_end) in enumerate(token_spans)
        if token_end > start and token_start < end
    ]


def _last_token_for_substring(tokenizer: Any, prompt_text: str, needle: str) -> int | None:
    offset = prompt_text.find(needle)
    if offset < 0:
        return None
    encoded = tokenizer(prompt_text, add_special_tokens=False).input_ids
    spans, _ = _token_char_spans(tokenizer, list(encoded))
    needle_end = offset + len(needle)
    candidates = [
        idx
        for idx, (token_start, token_end) in enumerate(spans)
        if token_end > offset and token_start < needle_end
    ]
    return candidates[-1] if candidates else None


def _sender_prompt(question: str, benchmark: str) -> str:
    prepared = prepare_question(question, benchmark)
    content = (
        f"Problem:\n{prepared}\n\n"
        "Solve the problem, but organize your private reasoning into 2 to 4 units. "
        "Each unit must use exactly this XML shape:\n"
        "<unit><anchor>short action label, 3 to 8 words</anchor><work>private local reasoning</work></unit>\n\n"
        "Keep anchors short. Put all detailed reasoning inside <work>. "
        "End with <answer>final answer only</answer>."
    )
    return content


def _receiver_prompt(question: str, benchmark: str, anchors: list[str]) -> str:
    prepared = prepare_question(question, benchmark)
    if not anchors:
        return cot_prompt(prepared)
    anchor_lines = "\n".join(f"[A{idx + 1}] {anchor}" for idx, anchor in enumerate(anchors))
    return (
        f"Problem:\n{prepared}\n\n"
        "A peer solver provided only these short reasoning anchors. "
        "The system may attach an invisible local latent payload to each anchor. "
        "Treat anchors as weak local hints and solve independently.\n\n"
        f"{anchor_lines}\n\n"
        "Now solve the problem. Do not mention hidden states, payloads, or anchors in the final answer. "
        "End with <answer>final answer only</answer>."
    )


def _generate_plain_output(
    *,
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    max_model_len: int,
) -> dict[str, Any]:
    text, _ = _generate_with_prompt_injections(
        model=model,
        tokenizer=tokenizer,
        prompt_text=prompt_text,
        injections=[],
        steering_scale=0.0,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        max_model_len=max_model_len,
    )
    output = _parse_output(text)
    return output


def _generate_sender_trace(
    *,
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    row_idx: int,
    agent_index: int,
    seed: int,
    layers: list[int],
    message_max_norm: float,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    max_model_len: int,
) -> SenderTrace:
    import torch

    device = next(model.parameters()).device
    max_prompt_tokens = max(1, max_model_len - max_new_tokens - 8)
    encoded = tokenizer(
        prompt_text,
        return_tensors="pt",
        truncation=True,
        max_length=max_prompt_tokens,
        add_special_tokens=False,
    )
    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded["attention_mask"].to(device)
    model_layers = _model_layers(model)
    if max(layers) >= len(model_layers):
        raise SystemExit(f"requested layer {max(layers)} but model only has {len(model_layers)} layers")

    current_step = 0
    generated_token_ids: list[int] = []
    hidden_by_layer: dict[int, list[Any]] = {layer: [] for layer in layers}
    handles = []

    def make_hook(layer_id: int):
        def hook(_module: Any, args: tuple[Any, ...]) -> None:
            if current_step <= 0:
                return None
            hidden_by_layer[layer_id].append(args[0].detach()[0, -1, :].float().cpu())
            return None

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
    units = parse_anchor_units(text)
    token_spans, _ = _token_char_spans(tokenizer, generated_token_ids)
    payloads: list[AnchorPayload] = []
    for unit in units:
        token_indices = _overlapping_token_indices(token_spans, unit.work_start, unit.work_end)
        vector_by_layer: dict[int, Any] = {}
        for layer in layers:
            deltas = []
            layer_hidden = hidden_by_layer[layer]
            for token_idx in token_indices:
                if token_idx <= 0 or token_idx >= len(layer_hidden):
                    continue
                deltas.append(layer_hidden[token_idx] - layer_hidden[token_idx - 1])
            vector = _mean_vectors(deltas)
            if vector is None:
                continue
            vector, _ = _clip_vector(vector, message_max_norm)
            vector_by_layer[layer] = vector.detach().cpu()
        if vector_by_layer:
            payloads.append(
                AnchorPayload(
                    anchor=unit.anchor,
                    vector_by_layer=vector_by_layer,
                    source_row=row_idx,
                    source_agent=agent_index,
                    source_unit=unit.unit_index,
                    token_indices=token_indices,
                )
            )

    output["agent_index"] = agent_index
    output["output_tokens"] = len(generated_token_ids)
    output["prompt_tokens"] = int(input_ids.shape[1])
    return SenderTrace(
        agent_index=agent_index,
        seed=seed,
        output=output,
        units=units,
        payloads=payloads,
        generated_token_ids=generated_token_ids,
        metadata={
            "unit_count": len(units),
            "payload_count": len(payloads),
            "generated_tokens": len(generated_token_ids),
            "prompt_tokens": int(input_ids.shape[1]),
        },
    )


def _collect_peer_payloads(
    *,
    traces_by_row: list[list[SenderTrace]],
    row_idx: int,
    agent_idx: int,
    max_anchors: int,
) -> list[AnchorPayload]:
    payloads: list[AnchorPayload] = []
    peer_payloads = [
        trace.payloads
        for peer_idx, trace in enumerate(traces_by_row[row_idx])
        if peer_idx != agent_idx and trace.payloads
    ]
    max_units = max((len(items) for items in peer_payloads), default=0)
    for unit_idx in range(max_units):
        for items in peer_payloads:
            if unit_idx >= len(items):
                continue
            payloads.append(items[unit_idx])
            if len(payloads) >= max_anchors:
                return payloads
    return payloads


def _payload_metadata(payloads: list[AnchorPayload], *, active: bool) -> dict[str, Any]:
    return {
        "active": active,
        "payload_count": len(payloads),
        "payloads": [
            {
                "anchor": payload.anchor,
                "source_row": payload.source_row,
                "source_agent": payload.source_agent,
                "source_unit": payload.source_unit,
                "token_indices": payload.token_indices,
                "layers": {
                    str(layer): {"norm": _vector_norm(vector)}
                    for layer, vector in payload.vector_by_layer.items()
                },
            }
            for payload in payloads
        ],
    }


def _other_payload_vectors(
    *,
    traces_by_row: list[list[SenderTrace]],
    row_idx: int,
    agent_idx: int,
    max_anchors: int,
) -> list[AnchorPayload]:
    other_idx = _other_row_index(row_idx, len(traces_by_row))
    if other_idx is None:
        return []
    return _collect_peer_payloads(
        traces_by_row=traces_by_row,
        row_idx=other_idx,
        agent_idx=min(agent_idx, len(traces_by_row[other_idx]) - 1),
        max_anchors=max_anchors,
    )


def _build_prompt_and_injections(
    *,
    tokenizer: Any,
    question: str,
    benchmark: str,
    condition: str,
    payloads: list[AnchorPayload],
    replacement_payloads: list[AnchorPayload],
    layers: list[int],
    seed: int,
) -> tuple[str, list[PromptInjection], dict[str, Any]]:
    import torch

    if condition == "raw_delta":
        prompt = _render_prompt(tokenizer, [{"role": "user", "content": cot_prompt(prepare_question(question, benchmark))}])
        encoded = tokenizer(prompt, add_special_tokens=False).input_ids
        final_position = max(0, len(encoded) - 1)
        injections: list[PromptInjection] = []
        for layer in layers:
            vectors = [payload.vector_by_layer[layer] for payload in payloads if layer in payload.vector_by_layer]
            vector = _mean_vectors(vectors)
            if vector is None:
                continue
            injections.append(PromptInjection(layer=layer, token_position=final_position, vector=vector, label="raw_delta"))
        return prompt, injections, _payload_metadata(payloads, active=bool(injections))

    anchors = [payload.anchor for payload in payloads]
    user_prompt = _receiver_prompt(question, benchmark, anchors)
    prompt = _render_prompt(tokenizer, [{"role": "user", "content": user_prompt}])
    if condition == "anchor_only":
        return prompt, [], _payload_metadata(payloads, active=False)

    injections = []
    active_payloads = payloads
    if condition == "anchor_other_question_delta":
        active_payloads = replacement_payloads[: len(payloads)]
    for idx, payload in enumerate(payloads):
        position = _last_token_for_substring(tokenizer, prompt, f"[A{idx + 1}] {payload.anchor}")
        if position is None:
            continue
        for layer in layers:
            vector = None
            if condition == "anchor_delta":
                vector = payload.vector_by_layer.get(layer)
            elif condition == "anchor_random_same_norm":
                reference = payload.vector_by_layer.get(layer)
                if reference is not None:
                    vector = _random_like_same_norm(reference, seed=_stable_seed(seed, idx, layer, "anchor_random"))
            elif condition == "anchor_other_question_delta" and idx < len(active_payloads):
                vector = active_payloads[idx].vector_by_layer.get(layer)
            if vector is None:
                continue
            if not isinstance(vector, torch.Tensor):
                continue
            injections.append(
                PromptInjection(layer=layer, token_position=position, vector=vector, label=f"A{idx + 1}:{condition}")
            )
    return prompt, injections, _payload_metadata(active_payloads, active=bool(injections))


def _generate_with_prompt_injections(
    *,
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    injections: list[PromptInjection],
    steering_scale: float,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    max_model_len: int,
) -> tuple[str, dict[str, Any]]:
    import torch

    device = next(model.parameters()).device
    max_prompt_tokens = max(1, max_model_len - max_new_tokens - 8)
    encoded = tokenizer(
        prompt_text,
        return_tensors="pt",
        truncation=True,
        max_length=max_prompt_tokens,
        add_special_tokens=False,
    )
    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded["attention_mask"].to(device)
    model_layers = _model_layers(model)
    by_layer: dict[int, list[PromptInjection]] = {}
    for injection in injections:
        if injection.layer >= len(model_layers):
            raise SystemExit(f"requested layer {injection.layer} but model only has {len(model_layers)} layers")
        if 0 <= injection.token_position < int(input_ids.shape[1]):
            by_layer.setdefault(injection.layer, []).append(injection)

    prefill_active = True
    handles = []

    def make_hook(layer_id: int):
        def hook(_module: Any, args: tuple[Any, ...]) -> tuple[Any, ...] | None:
            if not prefill_active:
                return None
            layer_injections = by_layer.get(layer_id, [])
            if not layer_injections:
                return None
            hidden = args[0]
            steered = hidden.clone()
            for injection in layer_injections:
                vector = injection.vector.to(device=device, dtype=hidden.dtype)
                steered[:, injection.token_position, :] = (
                    steered[:, injection.token_position, :] + vector * steering_scale
                )
            return (steered,) + args[1:]

        return hook

    for layer_id in by_layer:
        handles.append(model_layers[layer_id].register_forward_pre_hook(make_hook(layer_id)))

    generated_ids = []
    try:
        with torch.inference_mode():
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, use_cache=True)
            prefill_active = False
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

    text = ""
    if generated_ids:
        tokens = torch.cat(generated_ids, dim=1)[0]
        text = tokenizer.decode(tokens, skip_special_tokens=True)
    return text, {
        "active_injections": sum(len(items) for items in by_layer.values()),
        "injections": [
            {
                "layer": injection.layer,
                "token_position": injection.token_position,
                "label": injection.label,
                "norm": _vector_norm(injection.vector),
            }
            for items in by_layer.values()
            for injection in items
        ],
        "prompt_tokens": int(input_ids.shape[1]),
    }


def _sender_trace_metadata(trace: SenderTrace) -> dict[str, Any]:
    return {
        "agent_index": trace.agent_index,
        "seed": trace.seed,
        **trace.metadata,
        "anchors": [unit.anchor for unit in trace.units],
        "parsed_answer": trace.output.get("parsed_answer"),
        "normalized_answer": trace.output.get("normalized_answer"),
    }


def main() -> int:
    args = parse_args()
    if args.agents < 2:
        raise SystemExit("--agents must be >= 2")
    if args.max_anchors < 1:
        raise SystemExit("--max-anchors must be >= 1")
    layers = _parse_int_csv(args.layers, name="layers")
    conditions = _parse_str_csv(args.conditions, name="conditions")
    unknown = sorted(set(conditions) - set(DEFAULT_CONDITIONS))
    if unknown:
        raise SystemExit(f"unknown conditions: {', '.join(unknown)}")

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_id)
    work_dir = Path(args.work_dir).expanduser().resolve()
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-mca-text-anchored-delta",
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
        f"text-anchored-delta start run_id={args.run_id} rows={len(rows)} "
        f"layers={layers} conditions={conditions} max_anchors={args.max_anchors}"
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

    row_seed_keys = [row.get("id") or row.get("index", idx) for idx, row in enumerate(rows)]
    baseline_outputs_by_row: list[list[dict[str, Any]]] = []
    baseline_majorities: list[str | None] = []
    baseline_ties: list[bool] = []
    baseline_correct: list[bool] = []
    sender_traces_by_row: list[list[SenderTrace]] = []
    counts: Counter[str] = Counter()

    for row_idx, row in enumerate(rows):
        question = str(row.get("question") or "")
        gold = row.get("answer")
        baseline_outputs = []
        sender_traces = []
        for agent_idx in range(args.agents):
            seed = _stable_seed(args.seed, args.benchmark, args.split, row_seed_keys[row_idx], "agent", agent_idx)
            _set_generation_seed(torch, seed)
            baseline_prompt = _render_prompt(
                tokenizer,
                [{"role": "user", "content": cot_prompt(prepare_question(question, args.benchmark))}],
            )
            baseline_outputs.append(
                _generate_plain_output(
                    model=model,
                    tokenizer=tokenizer,
                    prompt_text=baseline_prompt,
                    max_new_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    max_model_len=args.max_model_len,
                )
            )
            _set_generation_seed(torch, seed)
            sender_prompt = _render_prompt(
                tokenizer,
                [{"role": "user", "content": _sender_prompt(question, args.benchmark)}],
            )
            sender_traces.append(
                _generate_sender_trace(
                    model=model,
                    tokenizer=tokenizer,
                    prompt_text=sender_prompt,
                    row_idx=row_idx,
                    agent_index=agent_idx,
                    seed=seed,
                    layers=layers,
                    message_max_norm=args.message_max_norm,
                    max_new_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    max_model_len=args.max_model_len,
                )
            )
            _progress(f"row {row_idx + 1}/{len(rows)} baseline+sender agent {agent_idx + 1}/{args.agents} done")
        answer, tie = majority_vote([item.get("parsed_answer") for item in baseline_outputs])
        ok = is_correct(answer, gold)
        baseline_outputs_by_row.append(baseline_outputs)
        sender_traces_by_row.append(sender_traces)
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
            question = str(row.get("question") or "")
            gold = row.get("answer")
            baseline_answer = baseline_majorities[row_idx]
            baseline_ok = baseline_correct[row_idx]
            record_conditions: dict[str, Any] = {}
            for condition in conditions:
                condition_outputs = []
                condition_metadata = []
                for agent_idx in range(args.agents):
                    seed = _stable_seed(args.seed, args.benchmark, args.split, row_seed_keys[row_idx], "agent", agent_idx)
                    payloads = _collect_peer_payloads(
                        traces_by_row=sender_traces_by_row,
                        row_idx=row_idx,
                        agent_idx=agent_idx,
                        max_anchors=args.max_anchors,
                    )
                    other_payloads = _other_payload_vectors(
                        traces_by_row=sender_traces_by_row,
                        row_idx=row_idx,
                        agent_idx=agent_idx,
                        max_anchors=args.max_anchors,
                    )
                    prompt, injections, payload_meta = _build_prompt_and_injections(
                        tokenizer=tokenizer,
                        question=question,
                        benchmark=args.benchmark,
                        condition=condition,
                        payloads=payloads,
                        replacement_payloads=other_payloads,
                        layers=layers,
                        seed=_stable_seed(args.seed, row_idx, agent_idx, condition),
                    )
                    _set_generation_seed(torch, seed)
                    text, injection_meta = _generate_with_prompt_injections(
                        model=model,
                        tokenizer=tokenizer,
                        prompt_text=prompt,
                        injections=injections,
                        steering_scale=args.steering_scale,
                        max_new_tokens=args.max_new_tokens,
                        temperature=args.temperature,
                        top_p=args.top_p,
                        max_model_len=args.max_model_len,
                    )
                    output = _parse_output(text)
                    output["agent_index"] = agent_idx
                    condition_outputs.append(output)
                    condition_metadata.append(
                        {
                            "agent_index": agent_idx,
                            "seed": seed,
                            "payload_metadata": payload_meta,
                            "injection_metadata": injection_meta,
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
                "mca_text_anchored_delta": {
                    "protocol": "mca-text-anchored-delta-v0",
                    "agents": args.agents,
                    "layers": layers,
                    "conditions": conditions,
                    "max_anchors": args.max_anchors,
                    "steering_scale": args.steering_scale,
                    "message_max_norm": args.message_max_norm,
                    "temperature": args.temperature,
                    "top_p": args.top_p,
                    "max_new_tokens": args.max_new_tokens,
                    "state_source": "sender_structured_work_span_delta",
                    "uses_peer_past_key_values": False,
                    "baseline_outputs": baseline_outputs_by_row[row_idx],
                    "baseline_majority_answer": baseline_answer,
                    "baseline_majority_tie": baseline_ties[row_idx],
                    "baseline_correct": baseline_ok,
                    "sender_trace_metadata": [_sender_trace_metadata(trace) for trace in sender_traces_by_row[row_idx]],
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
        "conditions": conditions,
        "max_anchors": args.max_anchors,
        "steering_scale": args.steering_scale,
        "message_max_norm": args.message_max_norm,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_new_tokens": args.max_new_tokens,
        "max_model_len": args.max_model_len,
        "state_source": "sender_structured_work_span_delta",
        "uses_peer_past_key_values": False,
        "counts": dict(counts),
        "metrics": metrics,
        "elapsed_seconds": elapsed,
        "records_path": str(records_path),
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as summary_file:
        json.dump(summary, summary_file, ensure_ascii=False, indent=2, sort_keys=True)
        summary_file.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as summary_file:
        summary_file.write(f"# {output_dir.name}\n\n")
        summary_file.write(f"- Rows: {counts['total']}\n")
        summary_file.write("- Protocol: mca-text-anchored-delta-v0\n")
        summary_file.write("- State source: sender structured work span delta\n")
        summary_file.write("- Uses peer past_key_values: false\n")
        summary_file.write(f"- Layers: {layers}\n")
        summary_file.write(f"- Conditions: {conditions}\n")
        summary_file.write(f"- Max anchors: {args.max_anchors}\n")
        summary_file.write(f"- Steering scale: {args.steering_scale}\n")
        summary_file.write(f"- Message max norm: {args.message_max_norm}\n")
        summary_file.write(f"- Baseline accuracy: {metrics['baseline_accuracy']:.4f}\n")
        for condition in conditions:
            item = metrics["conditions"][condition]
            summary_file.write(
                f"- {condition}: accuracy={item['accuracy']:.4f}, "
                f"delta={item['delta_vs_baseline']:+d}, "
                f"recovery={item['recovery_rate']:.4f}, harm={item['harm_rate']:.4f}, "
                f"change={item['answer_change_rate']:.4f}\n"
            )
        summary_file.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    _progress(f"text-anchored-delta complete elapsed_seconds={elapsed:.1f}")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
