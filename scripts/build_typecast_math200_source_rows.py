#!/usr/bin/env python3
"""Build a 200-case MATH source and sender-stage packet for TypeCastArena.

This is a local setup script only. It reads the existing MATH200 unified trace,
keeps every case, and prepares Stage 1 prompts where Agent A independently
emits a structured sender artifact. Stage 2 should later materialize receiver
prompts from the actual sender outputs, holding artifact content constant while
varying only the communication-boundary cast.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.typecast_arena import FAMILY, render_math_sender_prompt, sha1_text


DEFAULT_TRACE = Path(
    "experiments/20260615-1151-a8002-typed-public-state-math200-anon/"
    "madmm-qwen25-7b-math200-naive-20260615_1142.comm_trace.jsonl"
)
DEFAULT_OUT_DIR = Path("experiments/20260616-local-typecast-arena-math200-decisive-source")
SENDER_PACKET_NAME = "typecast_math200_sender_stage_packet.jsonl"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def round0_agents(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    for round_data in record.get("rounds") or []:
        if round_data.get("round_index") == 0:
            return [dict(agent) for agent in round_data.get("agents") or []]
    return []


def first_answer(agents: list[Mapping[str, Any]], *, correct: bool) -> Any:
    for agent in agents:
        if agent.get("correct") is correct:
            return agent.get("answer")
    return None


def trace_to_source_row(record: Mapping[str, Any]) -> dict[str, Any]:
    sample_index = int(record.get("sample_index") or 0)
    agents = round0_agents(record)
    correct_count = sum(1 for agent in agents if agent.get("correct") is True)
    wrong_count = sum(1 for agent in agents if agent.get("correct") is False)
    case_id = f"math200_case{sample_index:03d}"
    final = record.get("final") or {}
    transition = record.get("transition") or {}
    return {
        "case_id": case_id,
        "math_case_id": str(sample_index),
        "condition": "math200_live_sender_source",
        "mode": "live_sender_200case",
        "instance_id": str(record.get("instance_id") or sample_index),
        "question": record.get("question"),
        "gold_answer": record.get("gold_answer"),
        "baseline_answer": final.get("answer"),
        "baseline_output": (
            "No prior independent Agent B solution is supplied for this decisive "
            "cast test. Solve from the original problem; any later Agent A object "
            "must be independently checked against the task root."
        ),
        "wrong_peer_answer": first_answer(agents, correct=False),
        "correct_peer_answer": first_answer(agents, correct=True),
        "source_surface": "math200_live_sender_artifact",
        "manual_seed_label": {},
        "source_record": {
            "run_id": record.get("run_id"),
            "sample_index": sample_index,
            "instance_id": record.get("instance_id"),
            "method_family": record.get("method_family"),
            "method": record.get("method"),
            "task_regime": record.get("task_regime"),
            "round0_correct_count": correct_count,
            "round0_wrong_count": wrong_count,
            "round0_answers": [
                {
                    "agent_id": agent.get("agent_id"),
                    "answer": agent.get("answer"),
                    "correct": agent.get("correct"),
                    "confidence": agent.get("confidence"),
                }
                for agent in agents
            ],
            "final_answer": final.get("answer"),
            "final_correct": final.get("correct"),
            "transition_type": transition.get("type"),
            "transition_before_correct": transition.get("before_correct"),
            "transition_after_correct": transition.get("after_correct"),
        },
        "typecast_source_meta": {
            "source_pool": "madmm_math200_comm_trace",
            "round0_correct_count": correct_count,
            "round0_wrong_count": wrong_count,
            "has_correct_peer": correct_count > 0,
            "has_wrong_peer": wrong_count > 0,
            "peer_mix": f"{correct_count}correct_{wrong_count}wrong",
            "existing_trace_transition": transition.get("type"),
        },
    }


def sender_packet_row(source_row: Mapping[str, Any]) -> dict[str, Any]:
    prompt = render_math_sender_prompt(source_row)
    packet_id = f"{source_row['case_id']}::{FAMILY}::live_sender_stage"
    return {
        "packet_id": packet_id,
        "case_id": source_row["case_id"],
        "math_case_id": source_row.get("math_case_id"),
        "condition": source_row.get("condition"),
        "variant": "live_sender_stage",
        "typecast_arena_family": FAMILY,
        "stage": "sender",
        "sender_id": "Agent A",
        "receiver_id": "Agent B",
        "question": source_row.get("question"),
        "gold_answer": source_row.get("gold_answer"),
        "baseline_answer": source_row.get("baseline_answer"),
        "source_surface": source_row.get("source_surface"),
        "source_case_id": source_row.get("case_id"),
        "prompt": prompt,
        "prompt_sha1": sha1_text(prompt),
        "evaluation": {
            "gold_answer": source_row.get("gold_answer"),
            "primary_metric": "math_semantic_equivalence",
            "gold_is_metadata_not_prompt_input": True,
            "stage": "sender_artifact_generation",
        },
        "typecast_source_meta": source_row.get("typecast_source_meta"),
    }


def summarize(source_rows: list[Mapping[str, Any]], sender_packet: list[Mapping[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    metas = [row.get("typecast_source_meta") or {} for row in source_rows]
    return {
        "source_trace": str(args.trace),
        "source_rows": len(source_rows),
        "sender_packet_rows": len(sender_packet),
        "peer_mix_counts": dict(sorted(Counter(str(meta.get("peer_mix")) for meta in metas).items())),
        "has_correct_peer": sum(1 for meta in metas if meta.get("has_correct_peer")),
        "has_wrong_peer": sum(1 for meta in metas if meta.get("has_wrong_peer")),
        "existing_trace_transition_counts": dict(
            sorted(Counter(str(meta.get("existing_trace_transition")) for meta in metas).items())
        ),
        "outputs": {
            "source_rows": str(args.out_dir / "source_rows.jsonl"),
            "sender_packet": str(args.out_dir / SENDER_PACKET_NAME),
            "summary": str(args.out_dir / "summary.json"),
            "README": str(args.out_dir / "README.md"),
        },
        "run_later": {
            "stage1_packet": str(args.out_dir / SENDER_PACKET_NAME),
            "stage2_materializer": "scripts/materialize_typecast_math_live_receiver_packet.py",
            "decisive_channels": [
                "sender_private_scratch_visible_inert",
                "peer_message_direct",
                "shared_workspace_admitted",
                "verifier_admitted_result",
                "admission_rejected_quarantine",
                "typed_partial_derivation_requires_rederive",
            ],
        },
    }


def render_readme(summary: Mapping[str, Any]) -> str:
    lines = [
        "# TypeCastArena MATH200 Decisive Source",
        "",
        "This local setup prepares a 200-case live-sender TypeCastArena stage from the saved MATH200 MAD-MM trace.",
        "It does not run a model. The point is to create a large but sharp content-held-constant cast test.",
        "",
        "## Shape",
        "",
        f"- Source rows: `{summary['source_rows']}`",
        f"- Sender-stage prompt rows: `{summary['sender_packet_rows']}`",
        f"- Cases with at least one correct round-0 peer: `{summary['has_correct_peer']}`",
        f"- Cases with at least one wrong round-0 peer: `{summary['has_wrong_peer']}`",
        f"- Peer-mix counts: `{summary['peer_mix_counts']}`",
        f"- Existing trace transitions: `{summary['existing_trace_transition_counts']}`",
        "",
        "## Decisive Question",
        "",
        "For the same live Agent A artifact, does Agent B behave differently when the communication boundary casts it as inert scratch, a direct peer message, admitted shared state, verifier-admitted state, quarantine, or typed partial derivation requiring re-derivation?",
        "",
        "## Later GPU Stages",
        "",
        "Stage 1, sender artifact generation:",
        "",
        "```bash",
        "PACKET=<this-dir>/typecast_math200_sender_stage_packet.jsonl \\",
        "RUN_ID=<stamp>-a8002-typecast-math200-sender200-qwen25-7b \\",
        "MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct \\",
        "SERVED_MODEL=qwen2.5-7b-typecast-sender200 \\",
        "GPU_ID=<free-gpu> PORT=<free-port> LIMIT= scripts/run_typecast_arena_packet_a8002.sh",
        "```",
        "",
        "Stage 2, materialize the receiver packet from sender outputs:",
        "",
        "```bash",
        "python scripts/materialize_typecast_math_live_receiver_packet.py \\",
        "  --source-rows <this-dir>/source_rows.jsonl \\",
        "  --sender-packet <this-dir>/typecast_math200_sender_stage_packet.jsonl \\",
        "  --sender-outputs <sender-run>/outputs.jsonl \\",
        "  --channels sender_private_scratch_visible_inert peer_message_direct shared_workspace_admitted verifier_admitted_result admission_rejected_quarantine typed_partial_derivation_requires_rederive \\",
        "  --out-dir experiments/<local-receiver-packet-dir>",
        "```",
        "",
        "Stage 3, receiver run can be sharded by `LIMIT` or by pre-splitting the packet. Use one GPU only and no long overnight run.",
        "",
        "## Primary Contrasts",
        "",
        "- `shared_workspace_admitted` versus `sender_private_scratch_visible_inert`: cast effect with content visible in both.",
        "- `verifier_admitted_result` versus `peer_message_direct`: procedural-approval cast effect.",
        "- `typed_partial_derivation_requires_rederive` versus `shared_workspace_admitted`: mitigation without deleting the artifact.",
        "- `admission_rejected_quarantine`: negative control for withheld content.",
        "",
        "## Readout",
        "",
        "- Wrong sender artifacts: harmful cast rate, wrong-answer uptake, non-copy operator uptake.",
        "- Correct sender artifacts: useful evidence retention and rescue rate.",
        "- All sender artifacts: boundary obedience, especially unauthorized use under inert/quarantine/typed-rederive channels.",
        "",
    ]
    return "\n".join(lines)


def build(args: argparse.Namespace) -> dict[str, Any]:
    trace_rows = load_jsonl(args.trace)
    source_rows = [trace_to_source_row(row) for row in trace_rows]
    if args.max_cases:
        source_rows = source_rows[: args.max_cases]
    sender_packet = [sender_packet_row(row) for row in source_rows]
    summary = summarize(source_rows, sender_packet, args)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out_dir / "source_rows.jsonl", source_rows)
    write_jsonl(args.out_dir / SENDER_PACKET_NAME, sender_packet)
    write_json(args.out_dir / "summary.json", summary)
    write_text(args.out_dir / "README.md", render_readme(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--max-cases", type=int, default=0, help="0 means all cases")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
