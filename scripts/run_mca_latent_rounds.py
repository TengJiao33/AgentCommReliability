#!/usr/bin/env python3
"""Run pre-answer latent-state message passing before final answers.

This runner is intentionally different from Standard MAD and from Pre-KV hints:

* agents produce private natural thoughts before any final answer;
* peers never see those thoughts as text;
* each round shares only a latent activation vector derived from private thoughts;
* final answers are decoded only after the latent rounds finish.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

from mca_hidden_channel_runner import _generate_with_steering, _make_steering_vector, _progress
from run_basic_mad import is_correct, load_rows, majority_vote, normalize_numeric, resolve_inside
from run_mad_mm import extract_xml_answer, prepare_question
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
    parser.add_argument("--latent-rounds", type=int, default=2)
    parser.add_argument("--thought-tokens-per-round", type=int, default=96)
    parser.add_argument(
        "--private-thought-style",
        choices=("natural", "deliberative"),
        default="natural",
        help="natural minimizes prompt intervention; deliberative asks for critique/refinement notes.",
    )
    parser.add_argument("--final-max-tokens", type=int, default=1536)
    parser.add_argument("--thought-temperature", type=float, default=0.7)
    parser.add_argument("--final-temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--steering-layer", type=int, default=16)
    parser.add_argument("--steering-scale", type=float, default=0.05)
    parser.add_argument(
        "--normalize-steering",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Normalize thought-state deltas before exchange. Default: true.",
    )
    parser.add_argument(
        "--peer-fusion",
        choices=("mean", "norm_weighted_mean"),
        default="mean",
        help="How to fuse peer latent messages before steering.",
    )
    parser.add_argument(
        "--peer-mode",
        choices=("mean", "residual", "per_peer_branch"),
        default="mean",
        help=(
            "Latent exchange mechanism. mean uses fused peer states; residual uses fused "
            "peer-minus-own disagreement vectors; per_peer_branch probes each peer separately "
            "then fuses the resulting branch states."
        ),
    )
    parser.add_argument(
        "--peer-message-max-norm",
        type=float,
        default=1.0,
        help="Clip fused peer message norm before residual injection. 0 disables clipping.",
    )
    parser.add_argument(
        "--same-seed-conditions",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use matched generation seeds across baseline and latent conditions. Default: true.",
    )
    parser.add_argument(
        "--apply-peer-on-final",
        action=argparse.BooleanOptionalAction,
        default=False,
        help=(
            "Apply the last peer latent message during final answer generation. "
            "Default: false; latent exchange normally affects final answers only through prior private rounds."
        ),
    )
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--max-source-tokens", type=int, default=1024)
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


def _stable_seed(base_seed: int, *parts: Any) -> int:
    payload = "\x1f".join([str(base_seed), *(str(part) for part in parts)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % (2**31)


def _set_generation_seed(torch_module: Any, seed: int) -> None:
    torch_module.manual_seed(seed)
    if torch_module.cuda.is_available():
        torch_module.cuda.manual_seed_all(seed)


def _transition(prefix: str, before_ok: bool, after_ok: bool) -> str:
    if before_ok and after_ok:
        return f"{prefix}C_to_C"
    if before_ok and not after_ok:
        return f"{prefix}C_to_W"
    if not before_ok and after_ok:
        return f"{prefix}W_to_C"
    return f"{prefix}W_to_W"


def _private_thought_messages(
    question: str,
    own_thoughts: list[str],
    round_idx: int,
    style: str = "natural",
) -> list[dict[str, str]]:
    prior = ""
    if own_thoughts:
        prior = "\n\nYour private previous thoughts:\n" + "\n".join(
            f"Round {idx}: {thought}" for idx, thought in enumerate(own_thoughts)
        )
    if style == "deliberative":
        system_text = (
            "You are solving privately before the final answer phase. "
            "Maintain a tentative candidate, critique it, and refine the plan, "
            "but do not state a final answer, do not use <answer>, and do not box any result yet."
        )
        user_tail = (
            f"Continue private deliberation for latent round {round_idx}. "
            "Write a compact internal note covering: current approach, one uncertainty or possible flaw, "
            "and the next check to perform. Stop before final answer convergence."
        )
    else:
        system_text = (
            "You are solving privately before the final answer phase. "
            "Think naturally, but do not state a final answer, do not use <answer>, "
            "and do not box any result yet."
        )
        user_tail = f"Continue private reasoning for latent round {round_idx}. Stop before final answer convergence."
    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": f"Problem:\n{question}{prior}\n\n{user_tail}"},
    ]


def _final_messages(question: str, own_thoughts: list[str]) -> list[dict[str, str]]:
    prior = "\n".join(f"Round {idx}: {thought}" for idx, thought in enumerate(own_thoughts))
    return [
        {
            "role": "user",
            "content": (
                f"Problem:\n{question}\n\n"
                f"Your private pre-answer reasoning:\n{prior}\n\n"
                "Now solve the problem carefully and put only the final answer inside <answer>...</answer>."
            ),
        }
    ]


def _parse_output(text: str) -> dict[str, Any]:
    parsed = extract_xml_answer(text)
    return {
        "output": text,
        "parsed_answer": parsed,
        "normalized_answer": normalize_numeric(parsed),
        "mean_selected_logprob": None,
        "sequence_score": None,
    }


_ANSWER_MARKER_RE = re.compile(r"(<\s*/?\s*answer\b|final\s+answer\s*:|####|\\boxed\s*\{)", re.IGNORECASE)


def _thought_audit(text: str, gold: Any) -> dict[str, Any]:
    parsed = extract_xml_answer(text)
    return {
        "has_answer_marker": bool(_ANSWER_MARKER_RE.search(text or "")),
        "parsed_answer": parsed,
        "normalized_answer": normalize_numeric(parsed),
        "matches_gold": bool(parsed is not None and is_correct(parsed, gold)),
    }


def _thought_vector(
    model: Any,
    tokenizer: Any,
    question: str,
    thought: str,
    *,
    layer_index: int,
    max_source_tokens: int,
    normalize: bool,
) -> tuple[Any | None, dict[str, Any]]:
    source = f"Problem:\n{question}\n\nPrivate thought:\n{thought}"
    neutral = f"Problem:\n{question}\n\nPrivate thought:\n"
    return _make_steering_vector(
        model,
        tokenizer,
        source,
        neutral_text=neutral,
        layer_index=layer_index,
        max_source_tokens=max_source_tokens,
        channel_mode="state",
        normalize=normalize,
    )


def _seed_parts(args: argparse.Namespace, row_seed_key: Any, condition: str, *parts: Any) -> tuple[Any, ...]:
    if args.same_seed_conditions:
        return (args.benchmark, args.split, row_seed_key, *parts)
    return (args.benchmark, args.split, row_seed_key, condition, *parts)


def _clip_vector_norm(vector: Any, max_norm: float) -> tuple[Any, dict[str, Any]]:
    import torch

    norm = torch.linalg.vector_norm(vector.float()).clamp_min(1e-12)
    clipped = False
    if max_norm > 0 and float(norm.item()) > max_norm:
        vector = vector * (max_norm / norm.to(dtype=vector.dtype))
        clipped = True
    effective_norm = torch.linalg.vector_norm(vector.float())
    return vector, {
        "raw_norm": float(norm.item()),
        "effective_norm": float(effective_norm.item()),
        "clipped": clipped,
        "max_norm": max_norm,
    }


def _fuse_peer_vector(
    vectors: list[Any | None],
    agent_idx: int,
    *,
    fusion: str,
    max_norm: float,
) -> tuple[Any | None, dict[str, Any]]:
    peers = [vector for idx, vector in enumerate(vectors) if idx != agent_idx and vector is not None]
    return _fuse_vector_candidates(peers, fusion=fusion, max_norm=max_norm)


def _fuse_vector_candidates(
    candidates: list[Any | None],
    *,
    fusion: str,
    max_norm: float,
) -> tuple[Any | None, dict[str, Any]]:
    import torch

    active = [vector for vector in candidates if vector is not None]
    if not active:
        return None, {
            "active": False,
            "fusion": fusion,
            "source_count": 0,
            "raw_norm": 0.0,
            "effective_norm": 0.0,
            "clipped": False,
            "max_norm": max_norm,
        }
    stacked = torch.stack([candidate.float() for candidate in active], dim=0)
    if fusion == "norm_weighted_mean":
        norms = torch.linalg.vector_norm(stacked, dim=1).clamp_min(1e-12)
        weights = 1.0 / norms
        weights = weights / weights.sum()
        fused = (stacked * weights[:, None]).sum(dim=0)
    else:
        fused = stacked.mean(dim=0)
    fused, clip_meta = _clip_vector_norm(fused, max_norm)
    return fused, {
        "active": True,
        "fusion": fusion,
        "source_count": len(active),
        **clip_meta,
    }


def _peer_message_vector(
    vectors: list[Any | None],
    agent_idx: int,
    *,
    mode: str,
    fusion: str,
    max_norm: float,
) -> tuple[Any | None, dict[str, Any]]:
    import torch

    own = vectors[agent_idx] if 0 <= agent_idx < len(vectors) else None
    if mode == "residual":
        residuals = []
        for idx, vector in enumerate(vectors):
            if idx == agent_idx or vector is None:
                continue
            if own is None:
                residuals.append(vector)
            else:
                residuals.append(vector.float() - own.float())
        fused, meta = _fuse_vector_candidates(residuals, fusion=fusion, max_norm=max_norm)
        meta["peer_mode"] = mode
        meta["own_state_available"] = own is not None
        return fused, meta
    fused, meta = _fuse_peer_vector(vectors, agent_idx, fusion=fusion, max_norm=max_norm)
    meta["peer_mode"] = mode
    meta["own_state_available"] = own is not None
    return fused, meta


def _empty_peer_message_meta(*, mode: str, fusion: str, max_norm: float) -> dict[str, Any]:
    _, meta = _fuse_vector_candidates([], fusion=fusion, max_norm=max_norm)
    meta["peer_mode"] = mode
    meta["own_state_available"] = False
    return meta


def _vector_norm(vector: Any | None) -> float:
    if vector is None:
        return 0.0
    import torch

    return float(torch.linalg.vector_norm(vector.float()).item())


def _state_fusion_name(peer_mode: str) -> str:
    if peer_mode == "residual":
        return "mean_peer_minus_own_activation"
    if peer_mode == "per_peer_branch":
        return "per_peer_branch_activation"
    return "mean_peer_activation"


def _run_condition(
    *,
    condition: str,
    model: Any,
    tokenizer: Any,
    torch_module: Any,
    question: str,
    gold: Any,
    row_seed_key: Any,
    args: argparse.Namespace,
) -> dict[str, Any]:
    thoughts: list[list[str]] = [[] for _ in range(args.agents)]
    round_vectors: list[Any | None] = [None for _ in range(args.agents)]
    round_records: list[dict[str, Any]] = []
    seed_records: list[dict[str, Any]] = []
    for round_idx in range(args.latent_rounds):
        new_vectors: list[Any | None] = []
        round_agent_records: list[dict[str, Any]] = []
        for agent_idx in range(args.agents):
            seed = _stable_seed(args.seed, *_seed_parts(args, row_seed_key, condition, "thought", round_idx, agent_idx))
            prompt = _render_prompt(
                tokenizer,
                _private_thought_messages(question, thoughts[agent_idx], round_idx, args.private_thought_style),
            )
            branch_records: list[dict[str, Any]] = []
            if condition == "latent" and round_idx > 0 and args.peer_mode == "per_peer_branch":
                branch_vectors: list[Any | None] = []
                for peer_idx, peer_state in enumerate(round_vectors):
                    if peer_idx == agent_idx or peer_state is None:
                        continue
                    branch_peer_vector, branch_peer_meta = _fuse_vector_candidates(
                        [peer_state],
                        fusion=args.peer_fusion,
                        max_norm=args.peer_message_max_norm,
                    )
                    branch_peer_meta["peer_mode"] = args.peer_mode
                    branch_peer_meta["peer_agent_index"] = peer_idx
                    branch_seed = _stable_seed(
                        args.seed,
                        *_seed_parts(args, row_seed_key, condition, "branch", round_idx, agent_idx, peer_idx),
                    )
                    _set_generation_seed(torch_module, branch_seed)
                    branch_text = _generate_with_steering(
                        model,
                        tokenizer,
                        prompt,
                        steering_vector=branch_peer_vector,
                        layer_index=args.steering_layer,
                        steering_scale=args.steering_scale,
                        max_new_tokens=args.thought_tokens_per_round,
                        temperature=args.thought_temperature,
                        top_p=args.top_p,
                        max_prompt_tokens=max(1, args.max_model_len - args.thought_tokens_per_round - 8),
                    )
                    branch_vector, branch_vector_meta = _thought_vector(
                        model,
                        tokenizer,
                        question,
                        "\n".join([*thoughts[agent_idx], branch_text]),
                        layer_index=args.steering_layer,
                        max_source_tokens=args.max_source_tokens,
                        normalize=args.normalize_steering,
                    )
                    branch_vector_meta["effective_vector_norm"] = _vector_norm(branch_vector)
                    branch_vectors.append(branch_vector)
                    branch_records.append(
                        {
                            "peer_agent_index": peer_idx,
                            "seed": branch_seed,
                            "peer_vector_active": branch_peer_meta["active"],
                            "peer_vector_norm": branch_peer_meta["effective_norm"],
                            "peer_message_metadata": branch_peer_meta,
                            "thought": branch_text,
                            "thought_tokens_budget": args.thought_tokens_per_round,
                            "audit": _thought_audit(branch_text, gold),
                            "state_vector_metadata": branch_vector_meta,
                        }
                    )
                    seed_records.append(
                        {"round": round_idx, "agent_index": agent_idx, "peer_agent_index": peer_idx, "branch": branch_seed}
                    )
                peer_vector, peer_meta = _fuse_vector_candidates(
                    branch_vectors,
                    fusion=args.peer_fusion,
                    max_norm=args.peer_message_max_norm,
                )
                peer_meta["peer_mode"] = args.peer_mode
                peer_meta["branch_count"] = len(branch_records)
                peer_meta["own_state_available"] = round_vectors[agent_idx] is not None
            elif condition == "latent" and round_idx > 0:
                peer_vector, peer_meta = _peer_message_vector(
                    round_vectors,
                    agent_idx,
                    mode=args.peer_mode,
                    fusion=args.peer_fusion,
                    max_norm=args.peer_message_max_norm,
                )
            else:
                peer_vector = None
                peer_meta = _empty_peer_message_meta(
                    mode=args.peer_mode,
                    fusion=args.peer_fusion,
                    max_norm=args.peer_message_max_norm,
                )
            _set_generation_seed(torch_module, seed)
            text = _generate_with_steering(
                model,
                tokenizer,
                prompt,
                steering_vector=peer_vector,
                layer_index=args.steering_layer,
                steering_scale=args.steering_scale,
                max_new_tokens=args.thought_tokens_per_round,
                temperature=args.thought_temperature,
                top_p=args.top_p,
                max_prompt_tokens=max(1, args.max_model_len - args.thought_tokens_per_round - 8),
            )
            thoughts[agent_idx].append(text)
            vector, vector_meta = _thought_vector(
                model,
                tokenizer,
                question,
                "\n".join(thoughts[agent_idx]),
                layer_index=args.steering_layer,
                max_source_tokens=args.max_source_tokens,
                normalize=args.normalize_steering,
            )
            vector_meta["effective_vector_norm"] = _vector_norm(vector)
            new_vectors.append(vector)
            round_agent_records.append(
                {
                    "agent_index": agent_idx,
                    "seed": seed,
                    "peer_vector_active": peer_meta["active"],
                    "peer_vector_norm": peer_meta["effective_norm"],
                    "peer_message_metadata": peer_meta,
                    "thought": text,
                    "thought_tokens_budget": args.thought_tokens_per_round,
                    "audit": _thought_audit(text, gold),
                    "state_vector_metadata": vector_meta,
                    "branch_records": branch_records,
                }
            )
            seed_records.append({"round": round_idx, "agent_index": agent_idx, "thought": seed})
        round_vectors = new_vectors
        round_records.append({"round": round_idx, "agents": round_agent_records})
        _progress(f"condition={condition} latent round {round_idx + 1}/{args.latent_rounds} done")
    final_outputs = []
    final_metadata = []
    for agent_idx in range(args.agents):
        seed = _stable_seed(args.seed, *_seed_parts(args, row_seed_key, condition, "final", agent_idx))
        _set_generation_seed(torch_module, seed)
        if condition == "latent" and args.apply_peer_on_final:
            peer_vector, peer_meta = _peer_message_vector(
                round_vectors,
                agent_idx,
                mode=args.peer_mode,
                fusion=args.peer_fusion,
                max_norm=args.peer_message_max_norm,
            )
        else:
            peer_vector = None
            peer_meta = _empty_peer_message_meta(
                mode=args.peer_mode,
                fusion=args.peer_fusion,
                max_norm=args.peer_message_max_norm,
            )
        prompt = _render_prompt(tokenizer, _final_messages(question, thoughts[agent_idx]))
        text = _generate_with_steering(
            model,
            tokenizer,
            prompt,
            steering_vector=peer_vector,
            layer_index=args.steering_layer,
            steering_scale=args.steering_scale,
            max_new_tokens=args.final_max_tokens,
            temperature=args.final_temperature,
            top_p=args.top_p,
            max_prompt_tokens=max(1, args.max_model_len - args.final_max_tokens - 8),
        )
        output = _parse_output(text)
        output["agent_index"] = agent_idx
        final_outputs.append(output)
        final_metadata.append(
            {
                "agent_index": agent_idx,
                "seed": seed,
                "peer_vector_active": peer_meta["active"],
                "peer_vector_norm": peer_meta["effective_norm"],
                "peer_message_metadata": peer_meta,
            }
        )
        seed_records.append({"agent_index": agent_idx, "final": seed})
    majority_answer, majority_tie = majority_vote([item.get("parsed_answer") for item in final_outputs])
    correct = is_correct(majority_answer, gold)
    thought_answer_markers = sum(
        1
        for round_record in round_records
        for agent in round_record["agents"]
        if agent["audit"]["has_answer_marker"]
    )
    thought_gold_suspects = sum(
        1
        for round_record in round_records
        for agent in round_record["agents"]
        if agent["audit"]["matches_gold"]
    )
    return {
        "condition": condition,
        "rounds": round_records,
        "final_outputs": final_outputs,
        "final_metadata": final_metadata,
        "majority_answer": majority_answer,
        "majority_tie": majority_tie,
        "correct": correct,
        "thought_answer_marker_count": thought_answer_markers,
        "thought_gold_suspect_count": thought_gold_suspects,
        "seeds": seed_records,
    }


def _accumulate(records: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        payload = record.get("mca_latent_rounds", {})
        baseline = payload.get("baseline", {})
        latent = payload.get("latent", {})
        transition = payload.get("transition")
        counts["total"] += 1
        if baseline.get("correct"):
            counts["baseline_correct"] += 1
        if latent.get("correct"):
            counts["latent_correct"] += 1
        if transition:
            counts[transition] += 1
        if baseline.get("majority_tie"):
            counts["baseline_ties"] += 1
        if latent.get("majority_tie"):
            counts["latent_ties"] += 1
        counts["baseline_thought_answer_marker_count"] += int(baseline.get("thought_answer_marker_count", 0) or 0)
        counts["latent_thought_answer_marker_count"] += int(latent.get("thought_answer_marker_count", 0) or 0)
        counts["baseline_thought_gold_suspect_count"] += int(baseline.get("thought_gold_suspect_count", 0) or 0)
        counts["latent_thought_gold_suspect_count"] += int(latent.get("thought_gold_suspect_count", 0) or 0)
    return counts


def _metrics(counts: Counter[str], total: int) -> dict[str, float | int]:
    return {
        "baseline_accuracy": counts["baseline_correct"] / max(1, total),
        "latent_accuracy": counts["latent_correct"] / max(1, total),
        "latent_delta_vs_baseline": counts["latent_correct"] - counts["baseline_correct"],
        "latent_recovery_rate": counts["BaW_to_C"] / max(1, counts["BaW_to_C"] + counts["BaW_to_W"]),
        "latent_harm_rate": counts["BaC_to_W"] / max(1, counts["BaC_to_C"] + counts["BaC_to_W"]),
        "baseline_tie_rate": counts["baseline_ties"] / max(1, total),
        "latent_tie_rate": counts["latent_ties"] / max(1, total),
    }


def main() -> int:
    args = parse_args()
    if args.agents < 2:
        raise SystemExit("--agents must be >= 2")
    if args.latent_rounds < 1:
        raise SystemExit("--latent-rounds must be >= 1")
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_id)
    work_dir = Path(args.work_dir).expanduser().resolve()
    output_dir = resolve_inside(
        work_dir / "experiments" / args.run_id / f"{args.benchmark}-{args.model_key}-mca-latent-rounds",
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
        f"latent-rounds start run_id={args.run_id} rows={len(rows)} existing={len(existing)} "
        f"rounds={args.latent_rounds} thought_tokens={args.thought_tokens_per_round}"
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
            _progress(f"row {row_idx + 1}/{len(rows)} latent-rounds start")
            baseline = _run_condition(
                condition="baseline",
                model=model,
                tokenizer=tokenizer,
                torch_module=torch,
                question=question,
                gold=gold,
                row_seed_key=row_seed_key,
                args=args,
            )
            latent = _run_condition(
                condition="latent",
                model=model,
                tokenizer=tokenizer,
                torch_module=torch,
                question=question,
                gold=gold,
                row_seed_key=row_seed_key,
                args=args,
            )
            transition = _transition("Ba", bool(baseline["correct"]), bool(latent["correct"]))
            counts["total"] += 1
            if baseline["correct"]:
                counts["baseline_correct"] += 1
            if latent["correct"]:
                counts["latent_correct"] += 1
            counts[transition] += 1
            if baseline["majority_tie"]:
                counts["baseline_ties"] += 1
            if latent["majority_tie"]:
                counts["latent_ties"] += 1
            counts["baseline_thought_answer_marker_count"] += baseline["thought_answer_marker_count"]
            counts["latent_thought_answer_marker_count"] += latent["thought_answer_marker_count"]
            counts["baseline_thought_gold_suspect_count"] += baseline["thought_gold_suspect_count"]
            counts["latent_thought_gold_suspect_count"] += latent["thought_gold_suspect_count"]
            record = {
                "run_id": args.run_id,
                "model_key": args.model_key,
                "benchmark": args.benchmark,
                "split": args.split,
                "index": row_key,
                "id": row.get("id"),
                "question": row.get("question"),
                "gold_answer": gold,
                "mca_latent_rounds": {
                    "protocol": "mca-latent-rounds-activation-steering",
                    "agents": args.agents,
                    "latent_rounds": args.latent_rounds,
                    "thought_tokens_per_round": args.thought_tokens_per_round,
                    "private_thought_style": args.private_thought_style,
                    "state_fusion": _state_fusion_name(args.peer_mode),
                    "peer_mode": args.peer_mode,
                    "peer_fusion": args.peer_fusion,
                    "visible_peer_text": False,
                    "steering_layer": args.steering_layer,
                    "steering_scale": args.steering_scale,
                    "normalize_steering": args.normalize_steering,
                    "peer_message_max_norm": args.peer_message_max_norm,
                    "same_seed_conditions": args.same_seed_conditions,
                    "apply_peer_on_final": args.apply_peer_on_final,
                    "baseline": baseline,
                    "latent": latent,
                    "transition": transition,
                },
            }
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            handle.flush()
            _progress(
                f"row {row_idx + 1}/{len(rows)} written transition={transition} "
                f"baseline={baseline['majority_answer']} latent={latent['majority_answer']}"
            )
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
        "latent_rounds": args.latent_rounds,
        "thought_tokens_per_round": args.thought_tokens_per_round,
        "private_thought_style": args.private_thought_style,
        "final_max_tokens": args.final_max_tokens,
        "state_fusion": _state_fusion_name(args.peer_mode),
        "peer_mode": args.peer_mode,
        "peer_fusion": args.peer_fusion,
        "visible_peer_text": False,
        "steering_layer": args.steering_layer,
        "steering_scale": args.steering_scale,
        "normalize_steering": args.normalize_steering,
        "peer_message_max_norm": args.peer_message_max_norm,
        "same_seed_conditions": args.same_seed_conditions,
        "apply_peer_on_final": args.apply_peer_on_final,
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
        handle.write(f"- Latent rounds: {args.latent_rounds}\n")
        handle.write(f"- Thought tokens per round: {args.thought_tokens_per_round}\n")
        handle.write(f"- Private thought style: {args.private_thought_style}\n")
        handle.write("- Peer text visible: false\n")
        handle.write(f"- Peer mode: {args.peer_mode}\n")
        handle.write(f"- State fusion: {_state_fusion_name(args.peer_mode)} via {args.peer_fusion}\n")
        handle.write(f"- Steering scale: {args.steering_scale}\n")
        handle.write(f"- Normalize steering: {args.normalize_steering}\n")
        handle.write(f"- Peer message max norm: {args.peer_message_max_norm}\n")
        handle.write(f"- Same-seed conditions: {args.same_seed_conditions}\n")
        handle.write(f"- Baseline accuracy: {summary['metrics']['baseline_accuracy']:.4f}\n")
        handle.write(f"- Latent accuracy: {summary['metrics']['latent_accuracy']:.4f}\n")
        handle.write(f"- Latent delta vs baseline: {summary['metrics']['latent_delta_vs_baseline']:+d}\n")
        handle.write(f"- Latent recovery rate: {summary['metrics']['latent_recovery_rate']:.4f}\n")
        handle.write(f"- Latent harm rate: {summary['metrics']['latent_harm_rate']:.4f}\n")
        handle.write(f"- Baseline thought answer-marker count: {counts['baseline_thought_answer_marker_count']}\n")
        handle.write(f"- Latent thought answer-marker count: {counts['latent_thought_answer_marker_count']}\n")
        handle.write(f"- Elapsed seconds: {elapsed:.1f}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
