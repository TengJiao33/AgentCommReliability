#!/usr/bin/env python3
"""Run MCA-P: continuous-prefix metacognitive communication.

MCA-P keeps the answer-free cue extraction path from MCA-T, but the receiver
does not see cue text. Kept cue text is converted into a fixed-length
continuous prefix in the model embedding space and prepended to the receiver
prompt through ``inputs_embeds``.
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
from typing import Any

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


PREFIX_RESOLVE_FORMAT = (
    "\n\nEnd with exactly these XML tags:\n"
    "<prefix_effect>helpful|ignored|unclear</prefix_effect>\n"
    "<new_realization>one sentence or NONE</new_realization>\n"
    "<answer>final answer only</answer>"
)


@dataclass(frozen=True)
class ParsedSoftPrefixResolve:
    output: str
    parsed_answer: str | None
    normalized_answer: str | None
    prefix_effect: str
    new_realization: str


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
    parser.add_argument("--reviewers", type=int, default=3)
    parser.add_argument("--cue-k", type=int, default=2)
    parser.add_argument("--prefix-len", type=int, default=32)
    parser.add_argument(
        "--prefix-mode",
        choices=("cue", "zero", "random"),
        default="cue",
        help="cue uses cue-derived embeddings; zero/random are controls.",
    )
    parser.add_argument("--random-prefix-scale", type=float, default=0.02)
    parser.add_argument(
        "--prefix-fill",
        choices=("mean", "zero"),
        default="mean",
        help="How to fill unused prefix slots when there are fewer cue tokens than prefix slots.",
    )
    parser.add_argument(
        "--pool-state-scope",
        choices=("all", "collapse", "minority_bearing", "no_majority_conflict", "plurality_conflict"),
        default="all",
        help="Only run soft-prefix review for this CPAC pool state; others keep initial majority.",
    )
    parser.add_argument("--input-records", default="", help="Optional existing records.jsonl to reuse initial outputs.")
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
    parser.add_argument("--prefix-batch-size", type=int, default=4)
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=0, help="0 means full split.")
    parser.add_argument("--disable-tqdm", action="store_true")
    return parser.parse_args()


def _extract_tag(text: str, tag: str) -> str:
    match = re.search(fr"<{tag}>(.*?)</{tag}>", text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_prefix_effect(text: str) -> str:
    compact = re.sub(r"[^a-z]+", "", text.lower())
    if compact.startswith("help"):
        return "helpful"
    if compact.startswith("ignore"):
        return "ignored"
    return "unclear"


def parse_soft_prefix_resolve_output(text: str) -> ParsedSoftPrefixResolve:
    parsed_answer = extract_xml_answer(text)
    return ParsedSoftPrefixResolve(
        output=text,
        parsed_answer=parsed_answer,
        normalized_answer=normalize_numeric(parsed_answer),
        prefix_effect=_normalize_prefix_effect(_extract_tag(text, "prefix_effect")),
        new_realization=_normalize_space(_extract_tag(text, "new_realization")),
    )


def soft_prefix_payload(item: ParsedSoftPrefixResolve) -> dict[str, Any]:
    return {
        "output": item.output,
        "parsed_answer": item.parsed_answer,
        "normalized_answer": item.normalized_answer,
        "prefix_effect": item.prefix_effect,
        "new_realization": item.new_realization,
    }


def kept_cue_items(filtered: list[FilteredCue]) -> list[FilteredCue]:
    return [item for item in filtered if item.keep]


def soft_prefix_source_text(kept: list[FilteredCue]) -> str:
    lines = []
    for item in kept:
        cue = item.cue
        lines.append(f"{cue.cue_id} [{cue.cue_type}]: {cue.cue_text}")
    return "\n".join(lines)


def balanced_pool_spans(token_count: int, prefix_len: int) -> list[tuple[int, int]]:
    if token_count < 1 or prefix_len < 1:
        return []
    if token_count <= prefix_len:
        return [(idx, idx + 1) for idx in range(token_count)]
    spans = []
    for prefix_idx in range(prefix_len):
        start = (prefix_idx * token_count) // prefix_len
        end = ((prefix_idx + 1) * token_count) // prefix_len
        if end <= start:
            end = start + 1
        spans.append((start, min(end, token_count)))
    return spans


def soft_prefix_review_prompt(question: str, reviewer_index: int) -> list[dict[str, str]]:
    role = ROLE_NAMES[reviewer_index % len(ROLE_NAMES)]
    return [
        {
            "role": "system",
            "content": (
                f"You are MCA-P reviewer {reviewer_index + 1}, a {role}. "
                "The system may prepend an invisible continuous vector prefix derived from "
                "answer-free metacognitive cues. You cannot read the original cues. "
                "Treat any influence as a weak internal hint and solve independently."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                "Solve the problem independently. Do not mention hidden vectors or cues in the final answer. "
                "End with the required XML tags."
                f"{PREFIX_RESOLVE_FORMAT}"
            ),
        },
    ]


def _torch_dtype(dtype_name: str, torch_mod: Any) -> Any:
    value = dtype_name.lower()
    if value in {"auto", "bfloat16", "bf16"}:
        return torch_mod.bfloat16
    if value in {"float16", "fp16", "half"}:
        return torch_mod.float16
    if value in {"float32", "fp32"}:
        return torch_mod.float32
    raise SystemExit(f"unsupported dtype for HF backend: {dtype_name}")


def _sampling_kwargs(temperature: float, top_p: float) -> dict[str, Any]:
    if temperature and temperature > 0:
        return {"do_sample": True, "temperature": temperature, "top_p": top_p}
    return {"do_sample": False}


def _render_prompt(tokenizer: Any, messages: list[dict[str, str]]) -> str:
    return prompt_from_messages(tokenizer, messages)


def generate_hf_texts(
    model: Any,
    tokenizer: Any,
    prompts: list[str],
    *,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    batch_size: int,
    max_model_len: int,
) -> list[str]:
    import torch

    outputs: list[str] = []
    device = next(model.parameters()).device
    max_input_tokens = max(1, max_model_len - max_new_tokens - 8)
    pad_token_id = tokenizer.pad_token_id
    eos_token_id = tokenizer.eos_token_id
    with torch.inference_mode():
        for start in range(0, len(prompts), batch_size):
            batch = prompts[start : start + batch_size]
            encoded = tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_input_tokens,
            )
            input_ids = encoded["input_ids"].to(device)
            attention_mask = encoded["attention_mask"].to(device)
            generated = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=max_new_tokens,
                pad_token_id=pad_token_id,
                eos_token_id=eos_token_id,
                use_cache=True,
                **_sampling_kwargs(temperature, top_p),
            )
            prompt_width = int(input_ids.shape[1])
            for sequence in generated:
                completion_ids = sequence[prompt_width:]
                outputs.append(tokenizer.decode(completion_ids, skip_special_tokens=True))
    return outputs


def generate_hf_outputs(
    model: Any,
    tokenizer: Any,
    prompts: list[str],
    *,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    batch_size: int,
    max_model_len: int,
) -> list[dict[str, Any]]:
    texts = generate_hf_texts(
        model,
        tokenizer,
        prompts,
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


def make_soft_prefix_embeddings(
    model: Any,
    tokenizer: Any,
    prefix_text: str,
    *,
    prefix_len: int,
    prefix_mode: str,
    prefix_fill: str,
    random_prefix_scale: float,
    rng: random.Random,
) -> tuple[Any, dict[str, Any]]:
    import torch

    device = next(model.parameters()).device
    embedding = model.get_input_embeddings()
    hidden_size = int(embedding.embedding_dim)
    metadata: dict[str, Any] = {
        "prefix_mode": prefix_mode,
        "prefix_len": prefix_len,
        "prefix_fill": prefix_fill,
        "source_token_count": 0,
        "active_prefix_slots": prefix_len,
    }
    if prefix_mode == "zero":
        return torch.zeros((prefix_len, hidden_size), device=device, dtype=embedding.weight.dtype), metadata
    if prefix_mode == "random":
        seed = rng.randint(0, 2**31 - 1)
        generator = torch.Generator(device=device)
        generator.manual_seed(seed)
        metadata["random_seed"] = seed
        return (
            torch.randn(
                (prefix_len, hidden_size),
                device=device,
                dtype=embedding.weight.dtype,
                generator=generator,
            )
            * random_prefix_scale,
            metadata,
        )

    token_ids = tokenizer(prefix_text, add_special_tokens=False, return_tensors="pt").input_ids.to(device)
    if token_ids.numel() == 0:
        return torch.zeros((prefix_len, hidden_size), device=device, dtype=embedding.weight.dtype), metadata
    token_embeds = embedding(token_ids)[0]
    metadata["source_token_count"] = int(token_embeds.shape[0])
    spans = balanced_pool_spans(int(token_embeds.shape[0]), prefix_len)
    pooled = [token_embeds[start:end].mean(dim=0) for start, end in spans[:prefix_len]]
    if not pooled:
        prefix = torch.zeros((prefix_len, hidden_size), device=device, dtype=embedding.weight.dtype)
    else:
        if len(pooled) < prefix_len:
            if prefix_fill == "mean":
                filler = torch.stack(pooled, dim=0).mean(dim=0)
            else:
                filler = torch.zeros((hidden_size,), device=device, dtype=embedding.weight.dtype)
            pooled.extend(filler.clone() for _ in range(prefix_len - len(pooled)))
        prefix = torch.stack(pooled[:prefix_len], dim=0)
    return prefix.to(dtype=embedding.weight.dtype), metadata


def generate_with_soft_prefixes(
    model: Any,
    tokenizer: Any,
    prompt_texts: list[str],
    prefix_texts: list[str],
    *,
    prefix_len: int,
    prefix_mode: str,
    prefix_fill: str,
    random_prefix_scale: float,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    batch_size: int,
    max_model_len: int,
    seed: int,
) -> tuple[list[str], list[dict[str, Any]]]:
    import torch

    if len(prompt_texts) != len(prefix_texts):
        raise ValueError("prompt_texts and prefix_texts must have the same length")
    outputs: list[str] = []
    metadata: list[dict[str, Any]] = []
    device = next(model.parameters()).device
    embedding = model.get_input_embeddings()
    max_prompt_tokens = max(1, max_model_len - max_new_tokens - prefix_len - 8)
    rng = random.Random(seed)
    pad_token_id = tokenizer.pad_token_id
    eos_token_id = tokenizer.eos_token_id

    with torch.inference_mode():
        for start in range(0, len(prompt_texts), batch_size):
            batch_prompts = prompt_texts[start : start + batch_size]
            batch_prefix_texts = prefix_texts[start : start + batch_size]
            sequence_embeds = []
            sequence_masks = []
            batch_metadata = []
            for row_idx, prompt in enumerate(batch_prompts):
                encoded = tokenizer(
                    prompt,
                    return_tensors="pt",
                    padding=False,
                    truncation=True,
                    max_length=max_prompt_tokens,
                )
                input_ids = encoded["input_ids"][0].to(device)
                prompt_embeds = embedding(input_ids)
                prefix_embeds, prefix_meta = make_soft_prefix_embeddings(
                    model,
                    tokenizer,
                    batch_prefix_texts[row_idx],
                    prefix_len=prefix_len,
                    prefix_mode=prefix_mode,
                    prefix_fill=prefix_fill,
                    random_prefix_scale=random_prefix_scale,
                    rng=rng,
                )
                combined = torch.cat([prefix_embeds, prompt_embeds], dim=0)
                sequence_embeds.append(combined)
                sequence_masks.append(torch.ones((combined.shape[0],), device=device, dtype=torch.long))
                prefix_meta["prompt_token_count"] = int(input_ids.shape[0])
                batch_metadata.append(prefix_meta)

            max_len = max(int(item.shape[0]) for item in sequence_embeds)
            hidden_size = int(sequence_embeds[0].shape[-1])
            padded_embeds = torch.zeros(
                (len(sequence_embeds), max_len, hidden_size),
                device=device,
                dtype=embedding.weight.dtype,
            )
            attention_mask = torch.zeros((len(sequence_embeds), max_len), device=device, dtype=torch.long)
            for row_idx, embeds in enumerate(sequence_embeds):
                offset = max_len - int(embeds.shape[0])
                padded_embeds[row_idx, offset:] = embeds
                attention_mask[row_idx, offset:] = sequence_masks[row_idx]

            generated = model.generate(
                inputs_embeds=padded_embeds,
                attention_mask=attention_mask,
                max_new_tokens=max_new_tokens,
                pad_token_id=pad_token_id,
                eos_token_id=eos_token_id,
                use_cache=True,
                **_sampling_kwargs(temperature, top_p),
            )
            for row_idx, sequence in enumerate(generated):
                outputs.append(tokenizer.decode(sequence, skip_special_tokens=True))
                metadata.append(batch_metadata[row_idx])
    return outputs, metadata


def build_summary_metrics(summary_counts: Counter[str], filter_reason_counts: Counter[str], total: int) -> dict[str, float]:
    scoped_total = max(1, summary_counts["scoped_cases"])
    cue_atoms_total = max(1, summary_counts["cue_atoms"])
    prefix_outputs_total = max(1, summary_counts["soft_prefix_outputs"])
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
        "prefix_helpful_self_report_rate": summary_counts["prefix_helpful_reports"] / prefix_outputs_total,
        "answer_change_rate": summary_counts["answer_changed"] / max(1, total),
        "wrong_majority_recovery_rate": summary_counts["MaW_to_C"] / initial_wrong,
        "correct_majority_harm_rate": summary_counts["MaC_to_W"] / initial_correct,
        "final_parse_fail_rate": summary_counts["final_parse_fail"] / max(1, total),
        "final_majority_tie_rate": summary_counts["final_majority_ties"] / max(1, total),
    }


def main() -> int:
    args = parse_args()
    if args.agents < 2:
        raise SystemExit("--agents must be >= 2")
    if args.reviewers < 1:
        raise SystemExit("--reviewers must be >= 1")
    if args.cue_k < 1:
        raise SystemExit("--cue-k must be >= 1")
    if args.prefix_len < 1:
        raise SystemExit("--prefix-len must be >= 1")

    work_dir = Path(args.work_dir).expanduser().resolve()
    method_key = f"mca-soft-prefix-{args.prefix_mode}-{args.pool_state_scope}"
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-{method_key}",
        work_dir,
        "output dir",
    )
    output_dir.mkdir(parents=True, exist_ok=True)

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

    questions = [prepare_question(str(row.get("question") or ""), args.benchmark) for row in rows]
    if not initial_by_row:
        initial_prompts: list[str] = []
        for question in questions:
            for agent_idx in range(args.agents):
                if args.initial_prompt_style == "standard-mad":
                    initial_prompts.append(_render_prompt(tokenizer, [{"role": "user", "content": cot_prompt(question)}]))
                else:
                    initial_prompts.append(_render_prompt(tokenizer, independent_prompt(question, agent_idx)))
        initial_flat = generate_hf_outputs(
            model,
            tokenizer,
            initial_prompts,
            max_new_tokens=args.max_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            batch_size=args.batch_size,
            max_model_len=args.max_model_len,
        )
        initial_by_row = reshape(initial_flat, len(rows), args.agents)

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

    cue_texts = (
        generate_hf_texts(
            model,
            tokenizer,
            cue_prompts,
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

    prefix_prompt_texts: list[str] = []
    prefix_source_texts: list[str] = []
    prefix_owners: list[int] = []
    prefix_source_ids: list[list[str]] = []
    for row_idx, (question, decision, filtered) in enumerate(zip(questions, decisions, filtered_by_row)):
        if not row_in_scope(decision.pool_state, args.pool_state_scope):
            continue
        kept = kept_cue_items(filtered)
        if not kept:
            continue
        source_text = soft_prefix_source_text(kept)
        source_ids = [item.cue.cue_id for item in kept]
        for reviewer_idx in range(args.reviewers):
            prefix_prompt_texts.append(_render_prompt(tokenizer, soft_prefix_review_prompt(question, reviewer_idx)))
            prefix_source_texts.append(source_text)
            prefix_source_ids.append(source_ids)
            prefix_owners.append(row_idx)

    prefix_outputs, prefix_metadata = (
        generate_with_soft_prefixes(
            model,
            tokenizer,
            prefix_prompt_texts,
            prefix_source_texts,
            prefix_len=args.prefix_len,
            prefix_mode=args.prefix_mode,
            prefix_fill=args.prefix_fill,
            random_prefix_scale=args.random_prefix_scale,
            max_new_tokens=args.resolve_max_tokens,
            temperature=args.resolve_temperature,
            top_p=args.top_p,
            batch_size=args.prefix_batch_size,
            max_model_len=args.max_model_len,
            seed=args.seed + 1009,
        )
        if prefix_prompt_texts
        else ([], [])
    )
    resolves_by_row: list[list[ParsedSoftPrefixResolve]] = [[] for _ in rows]
    prefix_metadata_by_row: list[list[dict[str, Any]]] = [[] for _ in rows]
    for owner, output, metadata_item, source_ids in zip(prefix_owners, prefix_outputs, prefix_metadata, prefix_source_ids):
        resolves_by_row[owner].append(parse_soft_prefix_resolve_output(output))
        prefix_metadata_by_row[owner].append({**metadata_item, "source_cue_ids": source_ids})

    records_path = output_dir / "records.jsonl"
    summary_counts: Counter[str] = Counter()
    pool_state_counts: Counter[str] = Counter()
    filter_reason_counts: Counter[str] = Counter()
    pool_state_metrics: dict[str, Counter[str]] = {}

    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
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

            kept = kept_cue_items(filtered_by_row[idx])
            summary_counts["cue_atoms"] += len(cue_atoms_by_row[idx])
            summary_counts["kept_cues"] += len(kept)
            if kept:
                summary_counts["cue_coverage_cases"] += 1
                pool_metrics["cue_coverage_cases"] += 1
            for item in filtered_by_row[idx]:
                if not item.keep:
                    for reason in item.reasons:
                        filter_reason_counts[reason] += 1

            if resolves_by_row[idx]:
                review_answers = [resolve.parsed_answer for resolve in resolves_by_row[idx]]
                final_answer, final_tie = majority_vote(review_answers)
                summary_counts["soft_prefix_cases"] += 1
                summary_counts["soft_prefix_outputs"] += len(resolves_by_row[idx])
                pool_metrics["soft_prefix_cases"] += 1
            else:
                final_answer, final_tie = initial_majorities[idx], initial_ties[idx]
            summary_counts["prefix_helpful_reports"] += sum(
                1 for resolve in resolves_by_row[idx] if resolve.prefix_effect == "helpful"
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
                    "variant": "soft_prefix",
                    "prefix_mode": args.prefix_mode,
                    "prefix_len": args.prefix_len,
        "prefix_fill": args.prefix_fill,
        "pool_state_scope": args.pool_state_scope,
        "initial_prompt_style": args.initial_prompt_style,
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
                    "soft_prefix_metadata": prefix_metadata_by_row[idx],
                    "soft_prefix_outputs": [soft_prefix_payload(item) for item in resolves_by_row[idx]],
                    "final_majority_answer": final_answer,
                    "final_normalized_answer": normalize_numeric(final_answer),
                    "final_majority_tie": final_tie,
                    "correct": final_ok,
                    "transition": transition,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

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
                "soft_prefix_rate": counts["soft_prefix_cases"] / state_total,
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
        "protocol": "mca-soft-prefix",
        "prefix_mode": args.prefix_mode,
        "prefix_len": args.prefix_len,
        "prefix_fill": args.prefix_fill,
        "agents": args.agents,
        "reviewers": args.reviewers,
        "cue_k": args.cue_k,
        "pool_state_scope": args.pool_state_scope,
        "input_records": args.input_records or None,
        "temperature": args.temperature,
        "cue_temperature": args.cue_temperature,
        "resolve_temperature": args.resolve_temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
        "max_model_len": args.max_model_len,
        "gpu_id": args.gpu_id,
        "records_path": str(records_path),
        "elapsed_seconds": elapsed,
        "counts": {
            **dict(summary_counts),
            "cue_prompt_count": len(cue_prompts),
            "soft_prefix_prompt_count": len(prefix_prompt_texts),
            "pool_states": dict(sorted(pool_state_counts.items())),
            "filter_reasons": dict(sorted(filter_reason_counts.items())),
        },
        "metrics": build_summary_metrics(summary_counts, filter_reason_counts, total),
        "pool_state_metrics": pool_metrics_payload,
    }
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    with (output_dir / "summary.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {args.benchmark}-{args.model_key}-mca-soft-prefix\n\n")
        handle.write(f"- Rows: {len(rows)}\n")
        handle.write(f"- Prefix mode: {args.prefix_mode}\n")
        handle.write(f"- Prefix length: {args.prefix_len}\n")
        handle.write(f"- Pool-state scope: {args.pool_state_scope}\n")
        handle.write(f"- Initial majority accuracy: {summary['metrics']['initial_majority_accuracy']:.4f}\n")
        handle.write(f"- Final accuracy: {summary['metrics']['final_accuracy']:.4f}\n")
        handle.write(f"- Cue coverage rate: {summary['metrics']['cue_coverage_rate']:.4f}\n")
        handle.write(f"- Prefix helpful self-report rate: {summary['metrics']['prefix_helpful_self_report_rate']:.4f}\n")
        handle.write(f"- Wrong-majority recovery rate: {summary['metrics']['wrong_majority_recovery_rate']:.4f}\n")
        handle.write(f"- Correct-majority harm rate: {summary['metrics']['correct_majority_harm_rate']:.4f}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
