#!/usr/bin/env python3
"""Run question-token-anchored hidden-delta communication diagnostics.

Protocol sketch:

* sender agents solve with the ordinary CoT prompt;
* no sender is asked to emit XML, short anchors, plans, or structured messages;
* sender decode traces are split into local spans;
* each span is routed to tokens in the original question by runtime attribution;
* receivers see the same ordinary prompt, with hidden deltas injected at the
  corresponding question-token positions during prompt prefill.

The core contrast with SDE-style token-wise delta communication is that SDE
anchors deltas to sender message tokens, while this runner anchors deltas to
the task text shared by sender and receiver.
"""

from __future__ import annotations

import argparse
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
from run_mca_natural_search_delta import (
    _clip_vector,
    _condition_counts_update,
    _condition_metrics,
    _mean_vectors,
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
    "raw_delta",
    "question_token_delta",
    "question_token_random_same_norm",
)


@dataclass(frozen=True)
class QuestionTokenAnchor:
    token_position: int
    token_text: str
    score: float
    weight: float


@dataclass
class SegmentPayload:
    vector_by_layer: dict[int, Any]
    source_row: int
    source_agent: int
    source_segment: int
    generated_token_range: tuple[int, int]
    anchors: list[QuestionTokenAnchor]


@dataclass
class SenderTrace:
    agent_index: int
    seed: int
    output: dict[str, Any]
    payloads: list[SegmentPayload]
    generated_token_ids: list[int]
    question_token_positions: list[int]
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
    parser.add_argument("--span-tokens", type=int, default=16)
    parser.add_argument("--max-payloads", type=int, default=8)
    parser.add_argument("--max-question-anchors", type=int, default=3)
    parser.add_argument("--attribution-method", choices=("attention", "hidden_similarity"), default="attention")
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


def _question_token_positions(
    tokenizer: Any,
    prompt_text: str,
    question_text: str,
    prepared_question: str,
) -> list[int]:
    """Return prompt token positions overlapping the original question text.

    The original question is preferred over the prepared prompt so the answer
    formatting instruction does not become an anchor surface. If the exact raw
    question cannot be found, fall back to the prepared question.
    """

    offset = prompt_text.find(question_text)
    needle = question_text
    if offset < 0:
        offset = prompt_text.find(prepared_question)
        needle = prepared_question
    if offset < 0:
        return []

    encoded = tokenizer(prompt_text, add_special_tokens=False).input_ids
    spans, _ = _token_char_spans(tokenizer, list(encoded))
    end = offset + len(needle)
    positions = []
    for idx, (token_start, token_end) in enumerate(spans):
        if token_end <= offset or token_start >= end:
            continue
        token_text = tokenizer.decode([encoded[idx]], skip_special_tokens=True)
        if not token_text or token_text.isspace():
            continue
        positions.append(idx)
    return positions


def _segment_ranges(token_count: int, span_tokens: int) -> list[tuple[int, int]]:
    if span_tokens <= 0:
        raise ValueError("span_tokens must be positive")
    return [(start, min(token_count, start + span_tokens)) for start in range(0, token_count, span_tokens)]


def _decode_token_text(tokenizer: Any, prompt_token_ids: list[int], token_position: int) -> str:
    if token_position < 0 or token_position >= len(prompt_token_ids):
        return ""
    return tokenizer.decode([prompt_token_ids[token_position]], skip_special_tokens=True)


def _softmax_weights(values: list[float]) -> list[float]:
    import math

    if not values:
        return []
    maximum = max(values)
    exps = [math.exp(value - maximum) for value in values]
    total = sum(exps) or 1.0
    return [value / total for value in exps]


def _top_anchors(
    *,
    tokenizer: Any,
    prompt_token_ids: list[int],
    question_positions: list[int],
    scores: Any,
    max_question_anchors: int,
) -> list[QuestionTokenAnchor]:
    import torch

    if max_question_anchors <= 0 or not question_positions:
        return []
    score_tensor = scores.detach().float().cpu()
    if int(score_tensor.numel()) != len(question_positions):
        return []
    k = min(max_question_anchors, len(question_positions))
    top_values, top_indices = torch.topk(score_tensor, k=k)
    raw_scores = [float(value.item()) for value in top_values]
    weights = _softmax_weights(raw_scores)
    anchors: list[QuestionTokenAnchor] = []
    for value, local_idx, weight in zip(raw_scores, top_indices.tolist(), weights):
        token_position = question_positions[local_idx]
        anchors.append(
            QuestionTokenAnchor(
                token_position=token_position,
                token_text=_decode_token_text(tokenizer, prompt_token_ids, token_position),
                score=value,
                weight=weight,
            )
        )
    return anchors


def _hidden_similarity_scores(
    *,
    vector_by_layer: dict[int, Any],
    prompt_hidden_by_layer: dict[int, Any],
    question_positions: list[int],
) -> Any | None:
    import torch
    import torch.nn.functional as F

    for layer, vector in vector_by_layer.items():
        prompt_hidden = prompt_hidden_by_layer.get(layer)
        if prompt_hidden is None or not question_positions:
            continue
        valid_positions = [pos for pos in question_positions if 0 <= pos < int(prompt_hidden.shape[0])]
        if not valid_positions:
            continue
        matrix = prompt_hidden[valid_positions].float()
        repeated = vector.float().view(1, -1).expand_as(matrix)
        return F.cosine_similarity(repeated, matrix, dim=-1).cpu()
    return None


def _attention_scores(
    *,
    attention_by_step: list[Any | None],
    start: int,
    end: int,
) -> Any | None:
    vectors = [item for item in attention_by_step[start:end] if item is not None]
    return _mean_vectors(vectors)


def _attributed_anchors(
    *,
    tokenizer: Any,
    prompt_token_ids: list[int],
    question_positions: list[int],
    attribution_method: str,
    attention_by_step: list[Any | None],
    start: int,
    end: int,
    vector_by_layer: dict[int, Any],
    prompt_hidden_by_layer: dict[int, Any],
    max_question_anchors: int,
) -> tuple[list[QuestionTokenAnchor], str]:
    scores = None
    used_method = attribution_method
    if attribution_method == "attention":
        scores = _attention_scores(attention_by_step=attention_by_step, start=start, end=end)
        if scores is None:
            used_method = "hidden_similarity_fallback"
            scores = _hidden_similarity_scores(
                vector_by_layer=vector_by_layer,
                prompt_hidden_by_layer=prompt_hidden_by_layer,
                question_positions=question_positions,
            )
    else:
        scores = _hidden_similarity_scores(
            vector_by_layer=vector_by_layer,
            prompt_hidden_by_layer=prompt_hidden_by_layer,
            question_positions=question_positions,
        )
    if scores is None:
        return [], used_method
    return (
        _top_anchors(
            tokenizer=tokenizer,
            prompt_token_ids=prompt_token_ids,
            question_positions=question_positions,
            scores=scores,
            max_question_anchors=max_question_anchors,
        ),
        used_method,
    )


def _generate_sender_trace(
    *,
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    question_text: str,
    prepared_question: str,
    row_idx: int,
    agent_index: int,
    seed: int,
    layers: list[int],
    span_tokens: int,
    max_question_anchors: int,
    attribution_method: str,
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
    prompt_token_ids = list(encoded["input_ids"][0].detach().cpu().tolist())
    question_positions = _question_token_positions(tokenizer, prompt_text, question_text, prepared_question)
    question_positions = [pos for pos in question_positions if pos < int(input_ids.shape[1])]

    model_layers = _model_layers(model)
    if max(layers) >= len(model_layers):
        raise SystemExit(f"requested layer {max(layers)} but model only has {len(model_layers)} layers")

    current_step = 0
    generated_token_ids: list[int] = []
    hidden_by_layer: dict[int, list[Any]] = {layer: [] for layer in layers}
    prompt_hidden_by_layer: dict[int, Any] = {}
    attention_by_step: list[Any | None] = []
    handles = []

    def make_hook(layer_id: int):
        def hook(_module: Any, args: tuple[Any, ...]) -> None:
            hidden = args[0].detach()[0].float().cpu()
            if current_step <= 0:
                if layer_id not in prompt_hidden_by_layer:
                    prompt_hidden_by_layer[layer_id] = hidden
                return None
            hidden_by_layer[layer_id].append(hidden[-1, :])
            return None

        return hook

    for layer_id in layers:
        handles.append(model_layers[layer_id].register_forward_pre_hook(make_hook(layer_id)))

    generated_ids = []
    use_attention = attribution_method == "attention" and bool(question_positions)
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
                    output_attentions=use_attention,
                )
                if use_attention:
                    attention_by_step.append(
                        _step_question_attention(outputs.attentions, layers=layers, question_positions=question_positions)
                    )
                else:
                    attention_by_step.append(None)
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
    payloads: list[SegmentPayload] = []
    attribution_counts: Counter[str] = Counter()
    for segment_idx, (start, end) in enumerate(_segment_ranges(len(generated_token_ids), span_tokens)):
        vector_by_layer: dict[int, Any] = {}
        for layer in layers:
            deltas = []
            layer_hidden = hidden_by_layer[layer]
            for token_idx in range(start, end):
                if token_idx <= 0 or token_idx >= len(layer_hidden):
                    continue
                deltas.append(layer_hidden[token_idx] - layer_hidden[token_idx - 1])
            vector = _mean_vectors(deltas)
            if vector is None:
                continue
            vector, _ = _clip_vector(vector, message_max_norm)
            vector_by_layer[layer] = vector.detach().cpu()
        if not vector_by_layer:
            continue
        anchors, used_method = _attributed_anchors(
            tokenizer=tokenizer,
            prompt_token_ids=prompt_token_ids,
            question_positions=question_positions,
            attribution_method=attribution_method,
            attention_by_step=attention_by_step,
            start=start,
            end=end,
            vector_by_layer=vector_by_layer,
            prompt_hidden_by_layer=prompt_hidden_by_layer,
            max_question_anchors=max_question_anchors,
        )
        attribution_counts[used_method] += 1
        if not anchors:
            continue
        payloads.append(
            SegmentPayload(
                vector_by_layer=vector_by_layer,
                source_row=row_idx,
                source_agent=agent_index,
                source_segment=segment_idx,
                generated_token_range=(start, end),
                anchors=anchors,
            )
        )

    output["agent_index"] = agent_index
    output["output_tokens"] = len(generated_token_ids)
    output["prompt_tokens"] = int(input_ids.shape[1])
    return SenderTrace(
        agent_index=agent_index,
        seed=seed,
        output=output,
        payloads=payloads,
        generated_token_ids=generated_token_ids,
        question_token_positions=question_positions,
        metadata={
            "payload_count": len(payloads),
            "generated_tokens": len(generated_token_ids),
            "prompt_tokens": int(input_ids.shape[1]),
            "question_token_count": len(question_positions),
            "span_tokens": span_tokens,
            "attribution_counts": dict(attribution_counts),
        },
    )


def _step_question_attention(attentions: Any, *, layers: list[int], question_positions: list[int]) -> Any | None:
    if not attentions or not question_positions:
        return None
    vectors = []
    for layer in layers:
        if layer >= len(attentions):
            continue
        attention = attentions[layer]
        if attention is None:
            continue
        key_len = int(attention.shape[-1])
        valid_positions = [pos for pos in question_positions if pos < key_len]
        if not valid_positions:
            continue
        vectors.append(attention[0, :, -1, valid_positions].detach().float().mean(dim=0).cpu())
    return _mean_vectors(vectors)


def _collect_peer_payloads(
    *,
    traces_by_row: list[list[SenderTrace]],
    row_idx: int,
    agent_idx: int,
    max_payloads: int,
) -> list[SegmentPayload]:
    payloads: list[SegmentPayload] = []
    peer_payloads = [
        trace.payloads
        for peer_idx, trace in enumerate(traces_by_row[row_idx])
        if peer_idx != agent_idx and trace.payloads
    ]
    max_segments = max((len(items) for items in peer_payloads), default=0)
    for segment_idx in range(max_segments):
        for items in peer_payloads:
            if segment_idx >= len(items):
                continue
            payloads.append(items[segment_idx])
            if len(payloads) >= max_payloads:
                return payloads
    return payloads


def _payload_metadata(payloads: list[SegmentPayload], *, active: bool) -> dict[str, Any]:
    return {
        "active": active,
        "payload_count": len(payloads),
        "payloads": [
            {
                "source_row": payload.source_row,
                "source_agent": payload.source_agent,
                "source_segment": payload.source_segment,
                "generated_token_range": list(payload.generated_token_range),
                "anchors": [
                    {
                        "token_position": anchor.token_position,
                        "token_text": anchor.token_text,
                        "score": anchor.score,
                        "weight": anchor.weight,
                    }
                    for anchor in payload.anchors
                ],
                "layers": {
                    str(layer): {"norm": _vector_norm(vector)}
                    for layer, vector in payload.vector_by_layer.items()
                },
            }
            for payload in payloads
        ],
    }


def _plain_prompt(tokenizer: Any, question: str, benchmark: str) -> str:
    return _render_prompt(
        tokenizer,
        [{"role": "user", "content": cot_prompt(prepare_question(question, benchmark))}],
    )


def _build_prompt_and_injections(
    *,
    tokenizer: Any,
    question: str,
    benchmark: str,
    condition: str,
    payloads: list[SegmentPayload],
    layers: list[int],
    seed: int,
) -> tuple[str, list[PromptInjection], dict[str, Any]]:
    import torch

    prompt = _plain_prompt(tokenizer, question, benchmark)
    encoded = tokenizer(prompt, add_special_tokens=False).input_ids
    final_position = max(0, len(encoded) - 1)

    if condition == "raw_delta":
        injections: list[PromptInjection] = []
        for layer in layers:
            vectors = [payload.vector_by_layer[layer] for payload in payloads if layer in payload.vector_by_layer]
            vector = _mean_vectors(vectors)
            if vector is None:
                continue
            injections.append(PromptInjection(layer=layer, token_position=final_position, vector=vector, label="raw_delta"))
        return prompt, injections, _payload_metadata(payloads, active=bool(injections))

    grouped: dict[tuple[int, int], list[Any]] = {}
    for payload_idx, payload in enumerate(payloads):
        for layer in layers:
            reference = payload.vector_by_layer.get(layer)
            if reference is None or not isinstance(reference, torch.Tensor):
                continue
            for anchor_idx, anchor in enumerate(payload.anchors):
                if condition == "question_token_delta":
                    vector = reference.float() * float(anchor.weight)
                elif condition == "question_token_random_same_norm":
                    vector = _random_like_same_norm(
                        reference,
                        seed=_stable_seed(seed, payload_idx, anchor_idx, layer, "question_token_random"),
                    ) * float(anchor.weight)
                else:
                    vector = None
                if vector is None:
                    continue
                grouped.setdefault((layer, anchor.token_position), []).append(vector)

    injections = []
    for (layer, token_position), vectors in sorted(grouped.items()):
        vector = _mean_vectors(vectors)
        if vector is None:
            continue
        injections.append(
            PromptInjection(
                layer=layer,
                token_position=token_position,
                vector=vector,
                label=f"qtoken:{condition}",
            )
        )
    return prompt, injections, _payload_metadata(payloads, active=bool(injections))


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
        "parsed_answer": trace.output.get("parsed_answer"),
        "normalized_answer": trace.output.get("normalized_answer"),
    }


def _load_model(model_path: Path, args: argparse.Namespace, torch_module: Any) -> Any:
    from transformers import AutoModelForCausalLM

    kwargs = {
        "trust_remote_code": True,
        "torch_dtype": _torch_dtype(args.dtype, torch_module),
    }
    if args.attribution_method == "attention":
        kwargs["attn_implementation"] = "eager"
    try:
        return AutoModelForCausalLM.from_pretrained(str(model_path), **kwargs)
    except TypeError:
        kwargs.pop("attn_implementation", None)
        return AutoModelForCausalLM.from_pretrained(str(model_path), **kwargs)


def main() -> int:
    args = parse_args()
    if args.agents < 2:
        raise SystemExit("--agents must be >= 2")
    if args.span_tokens < 2:
        raise SystemExit("--span-tokens must be >= 2")
    if args.max_payloads < 1:
        raise SystemExit("--max-payloads must be >= 1")
    if args.max_question_anchors < 1:
        raise SystemExit("--max-question-anchors must be >= 1")
    layers = _parse_int_csv(args.layers, name="layers")
    conditions = _parse_str_csv(args.conditions, name="conditions")
    unknown = sorted(set(conditions) - set(DEFAULT_CONDITIONS))
    if unknown:
        raise SystemExit(f"unknown conditions: {', '.join(unknown)}")

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_id)
    work_dir = Path(args.work_dir).expanduser().resolve()
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-mca-question-token-anchored-delta",
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
        f"question-token-anchored-delta start run_id={args.run_id} rows={len(rows)} "
        f"layers={layers} conditions={conditions} span_tokens={args.span_tokens}"
    )

    import torch
    from transformers import AutoTokenizer

    started_at = time.time()
    model_path = Path(args.model_path).expanduser().resolve()
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = _load_model(model_path, args, torch)
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
        prepared = prepare_question(question, args.benchmark)
        gold = row.get("answer")
        sender_traces = []
        for agent_idx in range(args.agents):
            seed = _stable_seed(args.seed, args.benchmark, args.split, row_seed_keys[row_idx], "agent", agent_idx)
            _set_generation_seed(torch, seed)
            prompt = _plain_prompt(tokenizer, question, args.benchmark)
            sender_traces.append(
                _generate_sender_trace(
                    model=model,
                    tokenizer=tokenizer,
                    prompt_text=prompt,
                    question_text=question,
                    prepared_question=prepared,
                    row_idx=row_idx,
                    agent_index=agent_idx,
                    seed=seed,
                    layers=layers,
                    span_tokens=args.span_tokens,
                    max_question_anchors=args.max_question_anchors,
                    attribution_method=args.attribution_method,
                    message_max_norm=args.message_max_norm,
                    max_new_tokens=args.max_new_tokens,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    max_model_len=args.max_model_len,
                )
            )
            _progress(f"row {row_idx + 1}/{len(rows)} baseline+trace agent {agent_idx + 1}/{args.agents} done")
        baseline_outputs = [trace.output for trace in sender_traces]
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
                        max_payloads=args.max_payloads,
                    )
                    prompt, injections, payload_meta = _build_prompt_and_injections(
                        tokenizer=tokenizer,
                        question=question,
                        benchmark=args.benchmark,
                        condition=condition,
                        payloads=payloads,
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
                "mca_question_token_anchored_delta": {
                    "protocol": "mca-question-token-anchored-delta-v0",
                    "agents": args.agents,
                    "layers": layers,
                    "conditions": conditions,
                    "span_tokens": args.span_tokens,
                    "max_payloads": args.max_payloads,
                    "max_question_anchors": args.max_question_anchors,
                    "attribution_method": args.attribution_method,
                    "steering_scale": args.steering_scale,
                    "message_max_norm": args.message_max_norm,
                    "temperature": args.temperature,
                    "top_p": args.top_p,
                    "max_new_tokens": args.max_new_tokens,
                    "state_source": "ordinary_cot_decode_span_delta",
                    "anchor_source": "original_question_tokens",
                    "sender_prompt_intervention": False,
                    "receiver_prompt_intervention": False,
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
        "span_tokens": args.span_tokens,
        "max_payloads": args.max_payloads,
        "max_question_anchors": args.max_question_anchors,
        "attribution_method": args.attribution_method,
        "steering_scale": args.steering_scale,
        "message_max_norm": args.message_max_norm,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_new_tokens": args.max_new_tokens,
        "max_model_len": args.max_model_len,
        "state_source": "ordinary_cot_decode_span_delta",
        "anchor_source": "original_question_tokens",
        "sender_prompt_intervention": False,
        "receiver_prompt_intervention": False,
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
        summary_file.write("- Protocol: mca-question-token-anchored-delta-v0\n")
        summary_file.write("- State source: ordinary CoT decode span delta\n")
        summary_file.write("- Anchor source: original question tokens\n")
        summary_file.write("- Sender prompt intervention: false\n")
        summary_file.write("- Receiver prompt intervention: false\n")
        summary_file.write("- Uses peer past_key_values: false\n")
        summary_file.write(f"- Layers: {layers}\n")
        summary_file.write(f"- Conditions: {conditions}\n")
        summary_file.write(f"- Span tokens: {args.span_tokens}\n")
        summary_file.write(f"- Max payloads: {args.max_payloads}\n")
        summary_file.write(f"- Max question anchors: {args.max_question_anchors}\n")
        summary_file.write(f"- Attribution method: {args.attribution_method}\n")
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
    _progress(f"question-token-anchored-delta complete elapsed_seconds={elapsed:.1f}")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
