#!/usr/bin/env python3
"""Shared runner for hidden-channel MCA variants.

This module implements two real sender-state communication channels:

* MCA-KV: a sender solves the problem, and the receiver continues from that
  sender generation's actual KV cache. The sender text is not rendered into the
  receiver prompt, but the hidden cache may contain answer information.
* MCA-S: a sender solves the problem, and the receiver is steered by an
  activation vector captured during that sender generation.

These variants intentionally do not accept text-only records as a true
hidden-state source. JSONL records can align visible initial answers, but they
do not contain the live KV cache or residual activations.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from run_basic_mad import (
    ROLE_NAMES,
    is_correct,
    load_rows,
    majority_vote,
    normalize_numeric,
    prompt_from_messages,
    resolve_inside,
)
from run_consensus_quarantine import build_candidate_cards, independent_prompt, reshape, transition_label
from run_cpac_dcac import analyze_candidate_pool, decision_payload
from run_mad_mm import cot_prompt, extract_xml_answer, prepare_question
from run_mca_soft_prefix import _render_prompt, _sampling_kwargs, _torch_dtype, generate_hf_outputs, generate_hf_texts
from run_mca_text import (
    CueAtom,
    FilteredCue,
    cue_extraction_prompt,
    cue_payload,
    filter_cues,
    filtered_cue_payload,
    load_input_record_rows,
    parse_cue_atoms,
    row_in_scope,
)


Channel = Literal["kv", "steer"]

CHANNEL_RESOLVE_FORMAT = (
    "\n\nEnd with exactly these XML tags:\n"
    "<channel_effect>helpful|ignored|unclear</channel_effect>\n"
    "<new_realization>one sentence or NONE</new_realization>\n"
    "<answer>final answer only</answer>"
)


def _progress(message: str) -> None:
    print(f"[mca-hidden] {time.strftime('%Y-%m-%dT%H:%M:%S')} {message}", flush=True)


@dataclass(frozen=True)
class ParsedHiddenResolve:
    output: str
    parsed_answer: str | None
    normalized_answer: str | None
    channel_effect: str
    new_realization: str


@dataclass
class SenderState:
    output: dict[str, Any]
    past_key_values: Any | None
    past_token_count: int
    steering_vector: Any | None
    metadata: dict[str, Any]


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
    parser.add_argument("--cue-k", type=int, default=2)
    parser.add_argument(
        "--pool-state-scope",
        choices=("all", "collapse", "minority_bearing", "no_majority_conflict", "plurality_conflict"),
        default="all",
    )
    parser.add_argument(
        "--input-records",
        default="",
        help="Only valid with --channel-mode none; text records do not contain live hidden state.",
    )
    parser.add_argument(
        "--initial-prompt-style",
        choices=("mca", "standard-mad"),
        default="mca",
        help="Prompt family for newly sampled initial answers when --input-records is not used.",
    )
    parser.add_argument("--overlap-threshold", type=float, default=0.72)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--cue-temperature", type=float, default=0.2)
    parser.add_argument("--resolve-temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--cue-max-tokens", type=int, default=512)
    parser.add_argument("--resolve-max-tokens", type=int, default=1536)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--hidden-batch-size", type=int, default=1)
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--max-source-tokens", type=int, default=512)
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    parser.add_argument("--disable-tqdm", action="store_true")
    parser.add_argument(
        "--channel-mode",
        choices=("state", "none"),
        default="state",
        help="state applies live sender hidden state; none is a no-channel control.",
    )
    parser.add_argument("--steering-layer", type=int, default=16)
    parser.add_argument("--steering-scale", type=float, default=1.0)
    parser.add_argument("--steering-normalize", action="store_true")
    return parser


def _extract_tag(text: str, tag: str) -> str:
    match = re.search(fr"<{tag}>(.*?)</{tag}>", text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_channel_effect(text: str) -> str:
    compact = re.sub(r"[^a-z]+", "", text.lower())
    if compact.startswith("help"):
        return "helpful"
    if compact.startswith("ignore"):
        return "ignored"
    return "unclear"


def parse_hidden_resolve_output(text: str) -> ParsedHiddenResolve:
    parsed_answer = extract_xml_answer(text)
    return ParsedHiddenResolve(
        output=text,
        parsed_answer=parsed_answer,
        normalized_answer=normalize_numeric(parsed_answer),
        channel_effect=_normalize_channel_effect(_extract_tag(text, "channel_effect")),
        new_realization=_normalize_space(_extract_tag(text, "new_realization")),
    )


def hidden_resolve_payload(item: ParsedHiddenResolve) -> dict[str, Any]:
    return {
        "output": item.output,
        "parsed_answer": item.parsed_answer,
        "normalized_answer": item.normalized_answer,
        "channel_effect": item.channel_effect,
        "new_realization": item.new_realization,
    }


def kept_cue_items(filtered: list[FilteredCue]) -> list[FilteredCue]:
    return [item for item in filtered if item.keep]


def hidden_source_text(kept: list[FilteredCue]) -> str:
    lines = []
    for item in kept:
        cue = item.cue
        lines.append(f"{cue.cue_id} [{cue.cue_type}]: {cue.cue_text}")
    return "\n".join(lines)


def hidden_review_prompt(question: str, reviewer_index: int, channel: Channel) -> list[dict[str, str]]:
    role = ROLE_NAMES[reviewer_index % len(ROLE_NAMES)]
    channel_label = "KV-cache state" if channel == "kv" else "activation steering vector"
    return [
        {
            "role": "system",
            "content": (
                f"You are MCA-{channel.upper()} reviewer {reviewer_index + 1}, a {role}. "
                f"The system may provide an invisible {channel_label} captured from another solver's real reasoning pass. "
                "You cannot read the original cues. Treat any influence as a weak internal hint and solve independently."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                "Solve the problem independently. Do not mention hidden state, vectors, cache, or cues in the final answer. "
                "End with the required XML tags."
                f"{CHANNEL_RESOLVE_FORMAT}"
            ),
        },
    ]


def generate_hf_texts_with_progress(
    model: Any,
    tokenizer: Any,
    prompts: list[str],
    *,
    label: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    batch_size: int,
    max_model_len: int,
) -> list[str]:
    outputs: list[str] = []
    total = len(prompts)
    if not prompts:
        _progress(f"{label}: skipped, 0 prompts")
        return outputs
    _progress(f"{label}: start, prompts={total}, batch_size={batch_size}, max_new_tokens={max_new_tokens}")
    for start in range(0, total, batch_size):
        batch = prompts[start : start + batch_size]
        batch_outputs = generate_hf_texts(
            model,
            tokenizer,
            batch,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            batch_size=len(batch),
            max_model_len=max_model_len,
        )
        outputs.extend(batch_outputs)
        _progress(f"{label}: completed {len(outputs)}/{total}")
    return outputs


def generate_hf_outputs_with_progress(
    model: Any,
    tokenizer: Any,
    prompts: list[str],
    *,
    label: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    batch_size: int,
    max_model_len: int,
) -> list[dict[str, Any]]:
    texts = generate_hf_texts_with_progress(
        model,
        tokenizer,
        prompts,
        label=label,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        batch_size=batch_size,
        max_model_len=max_model_len,
    )
    return [
        {
            "output": text,
            "parsed_answer": extract_xml_answer(text),
            "normalized_answer": normalize_numeric(extract_xml_answer(text)),
            "mean_selected_logprob": None,
            "sequence_score": None,
            "output_tokens": None,
            "prompt_tokens": None,
        }
        for text in texts
    ]


def _sample_next_token(logits: Any, *, temperature: float, top_p: float) -> Any:
    import torch

    if not temperature or temperature <= 0:
        return torch.argmax(logits, dim=-1, keepdim=True)
    scaled = logits / temperature
    probs = torch.softmax(scaled, dim=-1)
    if top_p < 1.0:
        sorted_probs, sorted_indices = torch.sort(probs, descending=True)
        cumulative = torch.cumsum(sorted_probs, dim=-1)
        remove = cumulative > top_p
        remove[..., 1:] = remove[..., :-1].clone()
        remove[..., 0] = False
        sorted_probs = sorted_probs.masked_fill(remove, 0.0)
        sorted_probs = sorted_probs / sorted_probs.sum(dim=-1, keepdim=True).clamp_min(1e-12)
        sampled = torch.multinomial(sorted_probs, num_samples=1)
        return sorted_indices.gather(-1, sampled)
    return torch.multinomial(probs, num_samples=1)


def _manual_generate_with_optional_past(
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    *,
    past_key_values: Any | None,
    past_token_count: int,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    max_prompt_tokens: int,
) -> str:
    import torch

    device = next(model.parameters()).device
    encoded = tokenizer(
        prompt_text,
        return_tensors="pt",
        truncation=True,
        max_length=max_prompt_tokens,
    )
    input_ids = encoded["input_ids"].to(device)
    generated_ids: list[Any] = []
    total_len = past_token_count + int(input_ids.shape[1])
    attention_mask = torch.ones((1, total_len), device=device, dtype=torch.long)
    position_ids = torch.arange(past_token_count, total_len, device=device, dtype=torch.long).unsqueeze(0)
    with torch.inference_mode():
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            use_cache=True,
        )
        past = outputs.past_key_values
        next_logits = outputs.logits[:, -1, :]
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

    if not generated_ids:
        return ""
    tokens = torch.cat(generated_ids, dim=1)[0]
    return tokenizer.decode(tokens, skip_special_tokens=True)


def _manual_generate_sender_state(
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    *,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    max_model_len: int,
    steering_layer: int,
    keep_past_key_values: bool,
) -> SenderState:
    import torch

    device = next(model.parameters()).device
    max_input_tokens = max(1, max_model_len - max_new_tokens - 8)
    encoded = tokenizer(
        prompt_text,
        return_tensors="pt",
        truncation=True,
        max_length=max_input_tokens,
    )
    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded["attention_mask"].to(device)
    captures: list[Any] = []
    layers = _model_layers(model)
    if steering_layer >= len(layers):
        raise SystemExit(f"--steering-layer {steering_layer} out of range for {len(layers)} layers")

    def capture_hook(_module: Any, args: tuple[Any, ...]) -> None:
        captures.append(args[0].detach()[0, -1, :].float().cpu())

    handle = layers[steering_layer].register_forward_pre_hook(capture_hook)
    generated_ids: list[Any] = []
    past = None
    try:
        with torch.inference_mode():
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                use_cache=True,
            )
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
        handle.remove()

    if generated_ids:
        tokens = torch.cat(generated_ids, dim=1)[0]
        text = tokenizer.decode(tokens, skip_special_tokens=True)
    else:
        text = ""
    if captures:
        steering_vector = torch.stack(captures, dim=0).mean(dim=0)
        vector_norm = float(torch.linalg.vector_norm(steering_vector).item())
    else:
        steering_vector = None
        vector_norm = 0.0
    parsed_answer = extract_xml_answer(text)
    retained_past = past if keep_past_key_values else None
    if not keep_past_key_values:
        del past
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return SenderState(
        output={
            "output": text,
            "parsed_answer": parsed_answer,
            "normalized_answer": normalize_numeric(parsed_answer),
            "mean_selected_logprob": None,
            "sequence_score": None,
            "output_tokens": len(generated_ids),
            "prompt_tokens": int(input_ids.shape[1]),
        },
        past_key_values=retained_past,
        past_token_count=int(input_ids.shape[1]) + len(generated_ids),
        steering_vector=steering_vector,
        metadata={
            "prompt_tokens": int(input_ids.shape[1]),
            "generated_tokens": len(generated_ids),
            "past_token_count": int(input_ids.shape[1]) + len(generated_ids),
            "steering_layer": steering_layer,
            "activation_capture_count": len(captures),
            "steering_vector_norm": vector_norm,
        },
    )


def select_sender_state_indices(cards: list[Any], reviewers: int) -> list[int]:
    indices: list[int] = []
    for card in cards:
        for source_idx in card.source_indices:
            if source_idx not in indices:
                indices.append(source_idx)
                break
        if len(indices) >= reviewers:
            break
    return indices[:reviewers]


def _generate_from_sender_state(
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    *,
    channel: Channel,
    channel_mode: str,
    sender_state: SenderState,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    max_model_len: int,
    steering_layer: int,
    steering_scale: float,
) -> tuple[str, dict[str, Any]]:
    if channel_mode == "none":
        text = _manual_generate_with_optional_past(
            model,
            tokenizer,
            prompt_text,
            past_key_values=None,
            past_token_count=0,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            max_prompt_tokens=max_model_len - max_new_tokens - 8,
        )
        return text, {"channel_mode": "none", "active": False}
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
            max_prompt_tokens=max_model_len - max_new_tokens - sender_state.past_token_count - 8,
        )
        return text, {
            "channel": "kv",
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
        max_prompt_tokens=max_model_len - max_new_tokens - 8,
    )
    return text, {
        "channel": "steer",
        "channel_mode": "state",
        "active": sender_state.steering_vector is not None,
        "source_activation_capture_count": sender_state.metadata.get("activation_capture_count", 0),
        "source_steering_vector_norm": sender_state.metadata.get("steering_vector_norm", 0.0),
        "steering_layer": steering_layer,
        "steering_scale": steering_scale,
    }


def _make_kv_cache(
    model: Any,
    tokenizer: Any,
    source_text: str,
    *,
    max_source_tokens: int,
    channel_mode: str,
) -> tuple[Any | None, int, dict[str, Any]]:
    import torch

    metadata: dict[str, Any] = {
        "channel": "kv",
        "channel_mode": channel_mode,
        "source_token_count": 0,
        "active": False,
    }
    if channel_mode == "none" or not source_text.strip():
        return None, 0, metadata
    device = next(model.parameters()).device
    encoded = tokenizer(
        source_text,
        return_tensors="pt",
        truncation=True,
        max_length=max_source_tokens,
        add_special_tokens=False,
    )
    source_ids = encoded["input_ids"].to(device)
    if source_ids.numel() == 0:
        return None, 0, metadata
    attention_mask = torch.ones_like(source_ids, device=device)
    outputs = model(input_ids=source_ids, attention_mask=attention_mask, use_cache=True)
    metadata["source_token_count"] = int(source_ids.shape[1])
    metadata["active"] = True
    return outputs.past_key_values, int(source_ids.shape[1]), metadata


def _model_layers(model: Any) -> Any:
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    if hasattr(model, "transformer") and hasattr(model.transformer, "h"):
        return model.transformer.h
    raise ValueError("unsupported model architecture: cannot locate transformer layers")


def _capture_layer_last_hidden(model: Any, input_ids: Any, layer_index: int) -> Any:
    captures: list[Any] = []
    layers = _model_layers(model)
    layer = layers[layer_index]

    def hook(_module: Any, args: tuple[Any, ...]) -> None:
        captures.append(args[0].detach())

    handle = layer.register_forward_pre_hook(hook)
    try:
        model(input_ids=input_ids, use_cache=False)
    finally:
        handle.remove()
    if not captures:
        raise RuntimeError("failed to capture layer activations")
    return captures[0][0, -1, :]


def _make_steering_vector(
    model: Any,
    tokenizer: Any,
    source_text: str,
    *,
    neutral_text: str,
    layer_index: int,
    max_source_tokens: int,
    channel_mode: str,
    normalize: bool,
) -> tuple[Any | None, dict[str, Any]]:
    import torch

    metadata: dict[str, Any] = {
        "channel": "steer",
        "channel_mode": channel_mode,
        "source_token_count": 0,
        "neutral_token_count": 0,
        "steering_layer": layer_index,
        "active": False,
    }
    if channel_mode == "none" or not source_text.strip():
        return None, metadata
    device = next(model.parameters()).device
    source_ids = tokenizer(
        source_text,
        return_tensors="pt",
        truncation=True,
        max_length=max_source_tokens,
        add_special_tokens=False,
    ).input_ids.to(device)
    neutral_ids = tokenizer(
        neutral_text,
        return_tensors="pt",
        truncation=True,
        max_length=max_source_tokens,
        add_special_tokens=False,
    ).input_ids.to(device)
    if source_ids.numel() == 0 or neutral_ids.numel() == 0:
        return None, metadata
    source_vec = _capture_layer_last_hidden(model, source_ids, layer_index)
    neutral_vec = _capture_layer_last_hidden(model, neutral_ids, layer_index)
    vector = source_vec - neutral_vec
    norm = torch.linalg.vector_norm(vector.float()).clamp_min(1e-12)
    if normalize:
        vector = vector / norm.to(dtype=vector.dtype)
    metadata.update(
        {
            "source_token_count": int(source_ids.shape[1]),
            "neutral_token_count": int(neutral_ids.shape[1]),
            "vector_norm": float(norm.item()),
            "normalized": normalize,
            "active": True,
        }
    )
    return vector.detach(), metadata


def _generate_with_steering(
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    *,
    steering_vector: Any | None,
    layer_index: int,
    steering_scale: float,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    max_prompt_tokens: int,
) -> str:
    import torch

    handle = None
    if steering_vector is not None:
        layers = _model_layers(model)
        vector = steering_vector.to(next(model.parameters()).device)

        def steer_hook(_module: Any, args: tuple[Any, ...]) -> tuple[Any, ...]:
            hidden = args[0]
            steered = hidden.clone()
            steered[:, -1, :] = steered[:, -1, :] + vector.to(dtype=hidden.dtype) * steering_scale
            return (steered,) + args[1:]

        handle = layers[layer_index].register_forward_pre_hook(steer_hook)
    try:
        return _manual_generate_with_optional_past(
            model,
            tokenizer,
            prompt_text,
            past_key_values=None,
            past_token_count=0,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            max_prompt_tokens=max_prompt_tokens,
        )
    finally:
        if handle is not None:
            handle.remove()


def generate_with_hidden_channel(
    model: Any,
    tokenizer: Any,
    prompt_texts: list[str],
    source_texts: list[str],
    *,
    channel: Channel,
    channel_mode: str,
    max_source_tokens: int,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    batch_size: int,
    max_model_len: int,
    steering_layer: int,
    steering_scale: float,
    steering_normalize: bool,
) -> tuple[list[str], list[dict[str, Any]]]:
    if len(prompt_texts) != len(source_texts):
        raise ValueError("prompt_texts and source_texts must have the same length")
    outputs: list[str] = []
    metadata: list[dict[str, Any]] = []
    max_prompt_tokens = max(1, max_model_len - max_new_tokens - max_source_tokens - 8)
    neutral_text = "No answer-free metacognitive cue is available."

    with __import__("torch").inference_mode():
        total = len(prompt_texts)
        completed = 0
        _progress(
            f"{channel} hidden generation: start, prompts={total}, batch_size={batch_size}, "
            f"max_new_tokens={max_new_tokens}, channel_mode={channel_mode}"
        )
        for start in range(0, len(prompt_texts), batch_size):
            batch_prompts = prompt_texts[start : start + batch_size]
            batch_sources = source_texts[start : start + batch_size]
            for prompt_text, source_text in zip(batch_prompts, batch_sources):
                if channel == "kv":
                    past, past_count, item_meta = _make_kv_cache(
                        model,
                        tokenizer,
                        source_text,
                        max_source_tokens=max_source_tokens,
                        channel_mode=channel_mode,
                    )
                    text = _manual_generate_with_optional_past(
                        model,
                        tokenizer,
                        prompt_text,
                        past_key_values=past,
                        past_token_count=past_count,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        max_prompt_tokens=max_prompt_tokens,
                    )
                else:
                    vector, item_meta = _make_steering_vector(
                        model,
                        tokenizer,
                        source_text,
                        neutral_text=neutral_text,
                        layer_index=steering_layer,
                        max_source_tokens=max_source_tokens,
                        channel_mode=channel_mode,
                        normalize=steering_normalize,
                    )
                    item_meta["steering_scale"] = steering_scale
                    text = _generate_with_steering(
                        model,
                        tokenizer,
                        prompt_text,
                        steering_vector=vector,
                        layer_index=steering_layer,
                        steering_scale=steering_scale,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        max_prompt_tokens=max_prompt_tokens,
                    )
                outputs.append(text)
                metadata.append(item_meta)
                completed += 1
                _progress(f"{channel} hidden generation: completed {completed}/{total}")
    return outputs, metadata


def build_summary_metrics(summary_counts: Counter[str], filter_reason_counts: Counter[str], total: int) -> dict[str, float]:
    scoped_total = max(1, summary_counts["scoped_cases"])
    cue_atoms_total = max(1, summary_counts["cue_atoms"])
    hidden_outputs_total = max(1, summary_counts["hidden_outputs"])
    initial_wrong = max(1, summary_counts["MaW_to_C"] + summary_counts["MaW_to_W"])
    initial_correct = max(1, summary_counts["MaC_to_C"] + summary_counts["MaC_to_W"])
    return {
        "initial_majority_accuracy": summary_counts["initial_majority_correct"] / max(1, total),
        "final_accuracy": summary_counts["final_correct"] / max(1, total),
        "scoped_case_rate": summary_counts["scoped_cases"] / max(1, total),
        "cue_coverage_rate": summary_counts["cue_coverage_cases"] / scoped_total,
        "kept_cues_per_scoped_case": summary_counts["kept_cues"] / scoped_total,
        "answer_leak_rejection_rate": (
            filter_reason_counts["candidate_answer_leak"] + filter_reason_counts["self_reported_answer_leak"]
        )
        / cue_atoms_total,
        "generic_cue_rejection_rate": filter_reason_counts["generic"] / cue_atoms_total,
        "channel_helpful_self_report_rate": summary_counts["channel_helpful_reports"] / hidden_outputs_total,
        "answer_change_rate": summary_counts["answer_changed"] / max(1, total),
        "wrong_majority_recovery_rate": summary_counts["MaW_to_C"] / initial_wrong,
        "correct_majority_harm_rate": summary_counts["MaC_to_W"] / initial_correct,
        "final_parse_fail_rate": summary_counts["final_parse_fail"] / max(1, total),
        "final_majority_tie_rate": summary_counts["final_majority_ties"] / max(1, total),
    }


def build_state_summary_metrics(summary_counts: Counter[str], total: int) -> dict[str, float]:
    initial_wrong = max(1, summary_counts["MaW_to_C"] + summary_counts["MaW_to_W"])
    initial_correct = max(1, summary_counts["MaC_to_C"] + summary_counts["MaC_to_W"])
    hidden_outputs_total = max(1, summary_counts["hidden_outputs"])
    return {
        "initial_majority_accuracy": summary_counts["initial_majority_correct"] / max(1, total),
        "final_accuracy": summary_counts["final_correct"] / max(1, total),
        "hidden_channel_rate": summary_counts["hidden_cases"] / max(1, total),
        "channel_helpful_self_report_rate": summary_counts["channel_helpful_reports"] / hidden_outputs_total,
        "answer_change_rate": summary_counts["answer_changed"] / max(1, total),
        "wrong_majority_recovery_rate": summary_counts["MaW_to_C"] / initial_wrong,
        "correct_majority_harm_rate": summary_counts["MaC_to_W"] / initial_correct,
        "final_parse_fail_rate": summary_counts["final_parse_fail"] / max(1, total),
        "final_majority_tie_rate": summary_counts["final_majority_ties"] / max(1, total),
    }


def run_live_state_main(channel: Channel, args: argparse.Namespace) -> int:
    if args.input_records and args.channel_mode == "state":
        raise SystemExit("live MCA-KV/S requires live sender generation; text records do not contain hidden states")

    work_dir = Path(args.work_dir).expanduser().resolve()
    protocol = "mca-kv-cache" if channel == "kv" else "mca-activation-steering"
    method_key = f"{protocol}-{args.channel_mode}-{args.pool_state_scope}"
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
    _progress(
        f"live-state run start protocol={protocol} run_id={args.run_id} rows={len(rows)} "
        f"channel_mode={args.channel_mode}"
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
    summary_counts: Counter[str] = Counter()
    pool_state_counts: Counter[str] = Counter()
    pool_state_metrics: dict[str, Counter[str]] = {}

    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for idx, row in enumerate(rows):
            question = prepare_question(str(row.get("question") or ""), args.benchmark)
            _progress(f"row {idx + 1}/{len(rows)} sender generation start")
            sender_states: list[SenderState] = []
            initial_by_row: list[dict[str, Any]] = []
            for agent_idx in range(args.agents):
                if args.initial_prompt_style == "standard-mad":
                    prompt = _render_prompt(tokenizer, [{"role": "user", "content": cot_prompt(question)}])
                else:
                    prompt = _render_prompt(tokenizer, independent_prompt(question, agent_idx))
                state = _manual_generate_sender_state(
                    model,
                    tokenizer,
                    prompt,
                    max_new_tokens=args.max_tokens,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    max_model_len=args.max_model_len,
                    steering_layer=args.steering_layer,
                    keep_past_key_values=(channel == "kv"),
                )
                sender_states.append(state)
                initial_by_row.append(state.output)
                _progress(
                    f"row {idx + 1}/{len(rows)} sender {agent_idx + 1}/{args.agents} "
                    f"tokens={state.metadata['generated_tokens']}"
                )

            cards = build_candidate_cards(initial_by_row)
            decision = analyze_candidate_pool(
                initial_by_row,
                cards,
                no_majority_action="listwise",
                overlap_threshold=args.overlap_threshold,
            )
            initial_majority, initial_tie = majority_vote([output.get("parsed_answer") for output in initial_by_row])
            scoped = row_in_scope(decision.pool_state, args.pool_state_scope)
            selected_sources = select_sender_state_indices(cards, args.reviewers) if scoped else []
            _progress(
                f"row {idx + 1}/{len(rows)} pool_state={decision.pool_state} "
                f"selected_sources={selected_sources}"
            )

            resolves: list[ParsedHiddenResolve] = []
            hidden_metadata: list[dict[str, Any]] = []
            for reviewer_idx, source_idx in enumerate(selected_sources):
                prompt = _render_prompt(tokenizer, hidden_review_prompt(question, reviewer_idx, channel))
                text, metadata_item = _generate_from_sender_state(
                    model,
                    tokenizer,
                    prompt,
                    channel=channel,
                    channel_mode=args.channel_mode,
                    sender_state=sender_states[source_idx],
                    max_new_tokens=args.resolve_max_tokens,
                    temperature=args.resolve_temperature,
                    top_p=args.top_p,
                    max_model_len=args.max_model_len,
                    steering_layer=args.steering_layer,
                    steering_scale=args.steering_scale,
                )
                resolves.append(parse_hidden_resolve_output(text))
                hidden_metadata.append(
                    {
                        **metadata_item,
                        "source_agent_index": source_idx,
                        "source_answer": initial_by_row[source_idx].get("parsed_answer"),
                    }
                )
                _progress(f"row {idx + 1}/{len(rows)} receiver {reviewer_idx + 1}/{len(selected_sources)} done")

            if resolves:
                final_answer, final_tie = majority_vote([resolve.parsed_answer for resolve in resolves])
                summary_counts["hidden_cases"] += 1
            else:
                final_answer, final_tie = initial_majority, initial_tie
            summary_counts["hidden_outputs"] += len(resolves)
            summary_counts["channel_helpful_reports"] += sum(1 for resolve in resolves if resolve.channel_effect == "helpful")

            gold = row.get("answer")
            initial_ok = is_correct(initial_majority, gold)
            final_ok = is_correct(final_answer, gold)
            transition = transition_label(initial_ok, final_ok)
            pool_state_counts[decision.pool_state] += 1
            pool_metrics = pool_state_metrics.setdefault(decision.pool_state, Counter())
            pool_metrics["total"] += 1
            summary_counts["total"] += 1
            if initial_ok:
                summary_counts["initial_majority_correct"] += 1
                pool_metrics["initial_majority_correct"] += 1
            if final_ok:
                summary_counts["final_correct"] += 1
                pool_metrics["final_correct"] += 1
            if normalize_numeric(final_answer) is None:
                summary_counts["final_parse_fail"] += 1
            if final_tie:
                summary_counts["final_majority_ties"] += 1
            if normalize_numeric(initial_majority) != normalize_numeric(final_answer):
                summary_counts["answer_changed"] += 1
            summary_counts[transition] += 1
            pool_metrics[transition] += 1

            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row.get("index", idx),
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "mca": {
                    "variant": "kv_cache_live_state" if channel == "kv" else "activation_steering_live_state",
                    "channel_mode": args.channel_mode,
                    "state_source": "live_sender_generation",
                    "pool_state_scope": args.pool_state_scope,
                    "agents": args.agents,
                    "reviewers": args.reviewers,
                    "initial_outputs": initial_by_row,
                    "sender_state_metadata": [state.metadata for state in sender_states],
                    "initial_majority_answer": initial_majority,
                    "initial_majority_tie": initial_tie,
                    "candidate_cards": [
                        {
                            "card_id": card.card_id,
                            "parsed_answer": card.parsed_answer,
                            "normalized_answer": card.normalized_answer,
                            "supporter_count_hidden_from_prompt": card.supporter_count,
                            "source_indices": list(card.source_indices),
                            "representative_output": card.representative_output,
                        }
                        for card in cards
                    ],
                    "candidate_pool_decision": decision_payload(decision),
                    "in_scope": scoped,
                    "hidden_channel_metadata": hidden_metadata,
                    "hidden_channel_outputs": [hidden_resolve_payload(item) for item in resolves],
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
                f"row {idx + 1}/{len(rows)} written transition={transition} "
                f"initial={initial_majority} final={final_answer}"
            )
            del sender_states
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    elapsed = time.time() - started_at
    total = max(1, summary_counts["total"])
    pool_metrics_payload = {}
    for state, counts in sorted(pool_state_metrics.items()):
        state_total = max(1, counts["total"])
        state_initial_wrong = max(1, counts["MaW_to_C"] + counts["MaW_to_W"])
        state_initial_correct = max(1, counts["MaC_to_C"] + counts["MaC_to_W"])
        pool_metrics_payload[state] = {
            "counts": dict(sorted(counts.items())),
            "metrics": {
                "initial_majority_accuracy": counts["initial_majority_correct"] / state_total,
                "final_accuracy": counts["final_correct"] / state_total,
                "wrong_majority_recovery_rate": counts["MaW_to_C"] / state_initial_wrong,
                "correct_majority_harm_rate": counts["MaC_to_W"] / state_initial_correct,
            },
        }

    summary = {
        "run_id": args.run_id,
        "model_key": args.model_key,
        "model_path": str(model_path),
        "benchmark": args.benchmark,
        "split": args.split,
        "rows": len(rows),
        "protocol": protocol,
        "state_source": "live_sender_generation",
        "channel_mode": args.channel_mode,
        "agents": args.agents,
        "reviewers": args.reviewers,
        "pool_state_scope": args.pool_state_scope,
        "initial_prompt_style": args.initial_prompt_style,
        "temperature": args.temperature,
        "resolve_temperature": args.resolve_temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "resolve_max_tokens": args.resolve_max_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": {
            **dict(summary_counts),
            "pool_states": dict(sorted(pool_state_counts.items())),
        },
        "metrics": build_state_summary_metrics(summary_counts, total),
        "pool_state_metrics": pool_metrics_payload,
    }
    if channel == "steer":
        summary["steering"] = {
            "layer": args.steering_layer,
            "scale": args.steering_scale,
            "normalize": args.steering_normalize,
        }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {args.benchmark}-{args.model_key}-{protocol}\n\n")
        handle.write(f"- Rows: {len(rows)}\n")
        handle.write("- State source: live sender generation\n")
        handle.write(f"- Channel mode: {args.channel_mode}\n")
        handle.write(f"- Pool-state scope: {args.pool_state_scope}\n")
        handle.write(f"- Initial majority accuracy: {summary['metrics']['initial_majority_accuracy']:.4f}\n")
        handle.write(f"- Final accuracy: {summary['metrics']['final_accuracy']:.4f}\n")
        handle.write(f"- Hidden channel rate: {summary['metrics']['hidden_channel_rate']:.4f}\n")
        handle.write(f"- Channel helpful self-report rate: {summary['metrics']['channel_helpful_self_report_rate']:.4f}\n")
        handle.write(f"- Wrong-majority recovery rate: {summary['metrics']['wrong_majority_recovery_rate']:.4f}\n")
        handle.write(f"- Correct-majority harm rate: {summary['metrics']['correct_majority_harm_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    _progress(f"live-state run complete protocol={protocol} elapsed_seconds={elapsed:.1f}")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def run_main(channel: Channel, args: argparse.Namespace) -> int:
    if args.agents < 2:
        raise SystemExit("--agents must be >= 2")
    if args.reviewers < 1:
        raise SystemExit("--reviewers must be >= 1")
    if args.cue_k < 1:
        raise SystemExit("--cue-k must be >= 1")
    if args.max_source_tokens < 1:
        raise SystemExit("--max-source-tokens must be >= 1")
    if channel == "steer" and args.steering_layer < 0:
        raise SystemExit("--steering-layer must be >= 0")
    if not args.input_records:
        return run_live_state_main(channel, args)
    if args.channel_mode == "state":
        raise SystemExit("live MCA-KV/S requires live sender generation; text records do not contain hidden states")

    work_dir = Path(args.work_dir).expanduser().resolve()
    protocol = "mca-kv-cache" if channel == "kv" else "mca-activation-steering"
    method_key = f"{protocol}-{args.channel_mode}-{args.pool_state_scope}"
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-{method_key}",
        work_dir,
        "output dir",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _progress(
        f"run start protocol={protocol} run_id={args.run_id} benchmark={args.benchmark}/{args.split} "
        f"channel_mode={args.channel_mode} limit={args.limit}"
    )

    if args.input_records:
        rows, initial_by_row = load_input_record_rows(resolve_inside(Path(args.input_records), work_dir, "input records"), args.limit)
    else:
        data_path = resolve_inside(
            work_dir / "data" / "benchmarks" / args.benchmark / args.split / "canonical.jsonl",
            work_dir,
            "benchmark path",
        )
        rows = load_rows(data_path, args.limit)
        initial_by_row = []
    _progress(f"loaded rows={len(rows)} input_records={'yes' if args.input_records else 'no'}")

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

    questions = [prepare_question(str(row.get("question") or ""), args.benchmark) for row in rows]
    if not initial_by_row:
        initial_prompts: list[str] = []
        for question in questions:
            for agent_idx in range(args.agents):
                if args.initial_prompt_style == "standard-mad":
                    initial_prompts.append(_render_prompt(tokenizer, [{"role": "user", "content": cot_prompt(question)}]))
                else:
                    initial_prompts.append(_render_prompt(tokenizer, independent_prompt(question, agent_idx)))
        initial_flat = generate_hf_outputs_with_progress(
            model,
            tokenizer,
            initial_prompts,
            label="initial answers",
            max_new_tokens=args.max_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            batch_size=args.batch_size,
            max_model_len=args.max_model_len,
        )
        initial_by_row = reshape(initial_flat, len(rows), args.agents)
    else:
        _progress(f"initial answers: reused {sum(len(item) for item in initial_by_row)} outputs")

    cards_by_row = [build_candidate_cards(outputs) for outputs in initial_by_row]
    decisions = [
        analyze_candidate_pool(
            outputs,
            cards,
            no_majority_action="listwise",
            overlap_threshold=args.overlap_threshold,
        )
        for outputs, cards in zip(initial_by_row, cards_by_row)
    ]

    cue_prompts: list[str] = []
    cue_owners: list[tuple[int, int]] = []
    for row_idx, (question, outputs, decision) in enumerate(zip(questions, initial_by_row, decisions)):
        if not row_in_scope(decision.pool_state, args.pool_state_scope):
            continue
        for agent_idx, output in enumerate(outputs):
            cue_prompts.append(_render_prompt(tokenizer, cue_extraction_prompt(question, output, cue_k=args.cue_k)))
            cue_owners.append((row_idx, agent_idx))
    _progress(f"cue extraction prompts={len(cue_prompts)}")

    cue_texts = (
        generate_hf_texts_with_progress(
            model,
            tokenizer,
            cue_prompts,
            label="cue extraction",
            max_new_tokens=args.cue_max_tokens,
            temperature=args.cue_temperature,
            top_p=args.top_p,
            batch_size=args.batch_size,
            max_model_len=args.max_model_len,
        )
        if cue_prompts
        else []
    )
    cue_atoms_by_row: list[list[CueAtom]] = [[] for _ in rows]
    cue_raw_outputs_by_row: list[list[dict[str, Any]]] = [[] for _ in rows]
    for (row_idx, agent_idx), cue_output in zip(cue_owners, cue_texts):
        cue_atoms = parse_cue_atoms(
            cue_output,
            source_agent_index=agent_idx,
            source_answer=initial_by_row[row_idx][agent_idx].get("parsed_answer"),
            max_cues=args.cue_k,
        )
        cue_atoms_by_row[row_idx].extend(cue_atoms)
        cue_raw_outputs_by_row[row_idx].append(
            {
                "source_agent_index": agent_idx,
                "cue_output": cue_output,
                "parsed_cue_ids": [cue.cue_id for cue in cue_atoms],
            }
        )

    filtered_by_row = [
        filter_cues(cues, cards) if row_in_scope(decision.pool_state, args.pool_state_scope) else []
        for cues, cards, decision in zip(cue_atoms_by_row, cards_by_row, decisions)
    ]

    initial_majorities: list[str | None] = []
    initial_ties: list[bool] = []
    for outputs in initial_by_row:
        majority_answer, initial_tie = majority_vote([output.get("parsed_answer") for output in outputs])
        initial_majorities.append(majority_answer)
        initial_ties.append(initial_tie)

    hidden_prompt_texts: list[str] = []
    hidden_source_texts: list[str] = []
    hidden_owners: list[int] = []
    hidden_source_ids: list[list[str]] = []
    for row_idx, (question, decision, filtered) in enumerate(zip(questions, decisions, filtered_by_row)):
        if not row_in_scope(decision.pool_state, args.pool_state_scope):
            continue
        kept = kept_cue_items(filtered)
        if not kept:
            continue
        source_text = hidden_source_text(kept)
        source_ids = [item.cue.cue_id for item in kept]
        for reviewer_idx in range(args.reviewers):
            hidden_prompt_texts.append(_render_prompt(tokenizer, hidden_review_prompt(question, reviewer_idx, channel)))
            hidden_source_texts.append(source_text)
            hidden_source_ids.append(source_ids)
            hidden_owners.append(row_idx)
    _progress(f"hidden channel prompts={len(hidden_prompt_texts)}")

    hidden_outputs, hidden_metadata = (
        generate_with_hidden_channel(
            model,
            tokenizer,
            hidden_prompt_texts,
            hidden_source_texts,
            channel=channel,
            channel_mode=args.channel_mode,
            max_source_tokens=args.max_source_tokens,
            max_new_tokens=args.resolve_max_tokens,
            temperature=args.resolve_temperature,
            top_p=args.top_p,
            batch_size=args.hidden_batch_size,
            max_model_len=args.max_model_len,
            steering_layer=args.steering_layer,
            steering_scale=args.steering_scale,
            steering_normalize=args.steering_normalize,
        )
        if hidden_prompt_texts
        else ([], [])
    )
    resolves_by_row: list[list[ParsedHiddenResolve]] = [[] for _ in rows]
    hidden_metadata_by_row: list[list[dict[str, Any]]] = [[] for _ in rows]
    for owner, output, metadata_item, source_ids in zip(hidden_owners, hidden_outputs, hidden_metadata, hidden_source_ids):
        resolves_by_row[owner].append(parse_hidden_resolve_output(output))
        hidden_metadata_by_row[owner].append({**metadata_item, "source_cue_ids": source_ids})

    records_path = output_dir / "records.jsonl"
    summary_counts: Counter[str] = Counter()
    pool_state_counts: Counter[str] = Counter()
    filter_reason_counts: Counter[str] = Counter()
    pool_state_metrics: dict[str, Counter[str]] = {}

    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        _progress(f"writing records to {records_path}")
        for idx, row in enumerate(rows):
            gold = row.get("answer")
            decision = decisions[idx]
            scoped = row_in_scope(decision.pool_state, args.pool_state_scope)
            pool_state_counts[decision.pool_state] += 1
            pool_metrics = pool_state_metrics.setdefault(decision.pool_state, Counter())
            pool_metrics["total"] += 1
            summary_counts["total"] += 1
            if scoped:
                summary_counts["scoped_cases"] += 1

            filtered = filtered_by_row[idx]
            kept_cues = kept_cue_items(filtered)
            summary_counts["cue_atoms"] += len(cue_atoms_by_row[idx])
            summary_counts["kept_cues"] += len(kept_cues)
            if kept_cues:
                summary_counts["cue_coverage_cases"] += 1
                pool_metrics["cue_coverage_cases"] += 1
            for item in filtered:
                if not item.keep:
                    for reason in item.reasons:
                        filter_reason_counts[reason] += 1

            if resolves_by_row[idx]:
                review_answers = [resolve.parsed_answer for resolve in resolves_by_row[idx]]
                final_answer, final_tie = majority_vote(review_answers)
                summary_counts["hidden_cases"] += 1
                pool_metrics["hidden_cases"] += 1
            else:
                final_answer, final_tie = initial_majorities[idx], initial_ties[idx]

            summary_counts["hidden_outputs"] += len(resolves_by_row[idx])
            summary_counts["channel_helpful_reports"] += sum(
                1 for resolve in resolves_by_row[idx] if resolve.channel_effect == "helpful"
            )

            initial_ok = is_correct(initial_majorities[idx], gold)
            final_ok = is_correct(final_answer, gold)
            transition = transition_label(initial_ok, final_ok)
            if initial_ok:
                summary_counts["initial_majority_correct"] += 1
                pool_metrics["initial_majority_correct"] += 1
            if final_ok:
                summary_counts["final_correct"] += 1
                pool_metrics["final_correct"] += 1
            if normalize_numeric(final_answer) is None:
                summary_counts["final_parse_fail"] += 1
            if final_tie:
                summary_counts["final_majority_ties"] += 1
            if normalize_numeric(initial_majorities[idx]) != normalize_numeric(final_answer):
                summary_counts["answer_changed"] += 1
            summary_counts[transition] += 1
            pool_metrics[transition] += 1

            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row.get("index", idx),
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "mca": {
                    "variant": "kv_cache" if channel == "kv" else "activation_steering",
                    "channel_mode": args.channel_mode,
                    "pool_state_scope": args.pool_state_scope,
                    "agents": args.agents,
                    "reviewers": args.reviewers,
                    "cue_k": args.cue_k,
                    "initial_outputs": initial_by_row[idx],
                    "initial_majority_answer": initial_majorities[idx],
                    "initial_majority_tie": initial_ties[idx],
                    "candidate_cards": [
                        {
                            "card_id": card.card_id,
                            "parsed_answer": card.parsed_answer,
                            "normalized_answer": card.normalized_answer,
                            "supporter_count_hidden_from_prompt": card.supporter_count,
                            "source_indices": list(card.source_indices),
                            "representative_output": card.representative_output,
                        }
                        for card in cards_by_row[idx]
                    ],
                    "candidate_pool_decision": decision_payload(decision),
                    "in_scope": scoped,
                    "cue_raw_outputs": cue_raw_outputs_by_row[idx],
                    "cue_atoms": [cue_payload(cue) for cue in cue_atoms_by_row[idx]],
                    "filtered_cues": [filtered_cue_payload(item) for item in filtered_by_row[idx]],
                    "hidden_channel_metadata": hidden_metadata_by_row[idx],
                    "hidden_channel_outputs": [hidden_resolve_payload(item) for item in resolves_by_row[idx]],
                    "final_majority_answer": final_answer,
                    "final_normalized_answer": normalize_numeric(final_answer),
                    "final_majority_tie": final_tie,
                    "correct": final_ok,
                    "transition": transition,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            if (idx + 1) % 25 == 0 or idx + 1 == len(rows):
                _progress(f"records written {idx + 1}/{len(rows)}")

    elapsed = time.time() - started_at
    total = max(1, summary_counts["total"])
    pool_metrics_payload = {}
    for state, counts in sorted(pool_state_metrics.items()):
        state_total = max(1, counts["total"])
        state_initial_wrong = max(1, counts["MaW_to_C"] + counts["MaW_to_W"])
        state_initial_correct = max(1, counts["MaC_to_C"] + counts["MaC_to_W"])
        pool_metrics_payload[state] = {
            "counts": dict(sorted(counts.items())),
            "metrics": {
                "initial_majority_accuracy": counts["initial_majority_correct"] / state_total,
                "final_accuracy": counts["final_correct"] / state_total,
                "cue_coverage_rate": counts["cue_coverage_cases"] / state_total,
                "hidden_channel_rate": counts["hidden_cases"] / state_total,
                "wrong_majority_recovery_rate": counts["MaW_to_C"] / state_initial_wrong,
                "correct_majority_harm_rate": counts["MaC_to_W"] / state_initial_correct,
            },
        }

    summary = {
        "run_id": args.run_id,
        "model_key": args.model_key,
        "model_path": str(model_path),
        "benchmark": args.benchmark,
        "split": args.split,
        "rows": len(rows),
        "protocol": protocol,
        "channel_mode": args.channel_mode,
        "agents": args.agents,
        "reviewers": args.reviewers,
        "cue_k": args.cue_k,
        "pool_state_scope": args.pool_state_scope,
        "input_records": args.input_records or None,
        "initial_prompt_style": args.initial_prompt_style,
        "temperature": args.temperature,
        "cue_temperature": args.cue_temperature,
        "resolve_temperature": args.resolve_temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "cue_max_tokens": args.cue_max_tokens,
        "resolve_max_tokens": args.resolve_max_tokens,
        "max_source_tokens": args.max_source_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": {
            **dict(summary_counts),
            "hidden_prompt_count": len(hidden_prompt_texts),
            "pool_states": dict(sorted(pool_state_counts.items())),
            "filter_reasons": dict(sorted(filter_reason_counts.items())),
        },
        "metrics": build_summary_metrics(summary_counts, filter_reason_counts, total),
        "pool_state_metrics": pool_metrics_payload,
    }
    if channel == "steer":
        summary["steering"] = {
            "layer": args.steering_layer,
            "scale": args.steering_scale,
            "normalize": args.steering_normalize,
        }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {args.benchmark}-{args.model_key}-{protocol}\n\n")
        handle.write(f"- Rows: {len(rows)}\n")
        handle.write(f"- Channel mode: {args.channel_mode}\n")
        handle.write(f"- Pool-state scope: {args.pool_state_scope}\n")
        handle.write(f"- Initial majority accuracy: {summary['metrics']['initial_majority_accuracy']:.4f}\n")
        handle.write(f"- Final accuracy: {summary['metrics']['final_accuracy']:.4f}\n")
        handle.write(f"- Cue coverage rate: {summary['metrics']['cue_coverage_rate']:.4f}\n")
        handle.write(f"- Channel helpful self-report rate: {summary['metrics']['channel_helpful_self_report_rate']:.4f}\n")
        handle.write(f"- Wrong-majority recovery rate: {summary['metrics']['wrong_majority_recovery_rate']:.4f}\n")
        handle.write(f"- Correct-majority harm rate: {summary['metrics']['correct_majority_harm_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    _progress(f"run complete protocol={protocol} elapsed_seconds={elapsed:.1f}")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0
