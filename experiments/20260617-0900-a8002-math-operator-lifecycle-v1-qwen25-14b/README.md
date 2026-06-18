# MATH Operator Lifecycle V1 Qwen2.5-14B Run

## Status

Completed on A800_2. The temporary vLLM process exited through the runner cleanup path, and GPU 7 returned to idle memory.

## Purpose

This run tests whether the same wrong sender artifact becomes more harmful when a communication layer changes its lifecycle status: direct peer message, admitted shared workspace, verifier-admitted result, quarantine, typed metadata, or typed partial derivation.

The unit is sender artifact x lifecycle channel, paired against a real prior Agent B solution.

## Launch

- Run id: `20260617-0900-a8002-math-operator-lifecycle-v1-qwen25-14b`
- Host: `A800_2`
- Remote output: `/data/xuhaoming/yfy/research_workspace/experiments/20260617-0900-a8002-math-operator-lifecycle-v1-qwen25-14b/`
- Local mirror: `experiments/20260617-0900-a8002-math-operator-lifecycle-v1-qwen25-14b/`
- Packet: `/data/xuhaoming/yfy/research_workspace/experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl`
- Packet rows: `166`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-math-operator-lifecycle-v1`
- GPU: `7`
- Port: `8047`
- Max tokens: `768`
- Temperature: `0`
- Request timeout: `420`
- Run timeout: `21600`

Launch command:

```bash
cd /data/xuhaoming/yfy/research_workspace
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl \
RUN_STAMP=20260617-0900 \
RUN_ID=20260617-0900-a8002-math-operator-lifecycle-v1-qwen25-14b \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
SERVED_MODEL=qwen2.5-14b-math-operator-lifecycle-v1 \
GPU_ID=7 \
PORT=8047 \
MAX_TOKENS=768 \
REQUEST_TIMEOUT=420 \
RUN_TIMEOUT=21600 \
EVALUATE=1 \
BOUNDARY_ANALYZE=1 \
bash scripts/run_typecast_arena_packet_a8002.sh
```

## Completion

- Completed rows: `166`
- Failed rows: `0`
- Outputs: `outputs.jsonl`
- Evaluation: `evaluation/summary.json`, `evaluation/evaluated_rows.jsonl`, `evaluation/paired_deltas.jsonl`
- Boundary audit: `boundary_obedience/summary.json`, `boundary_obedience/boundary_records.jsonl`, `boundary_obedience/boundary_concern_cards.jsonl`
- Remote cleanup: GPU 7 returned to `4 MiB` used after runner exit.

## Result Summary

Overall evaluation:

- Records: `166`
- Semantic correct: `161`
- Semantic wrong: `5`
- Semantic unknown: `0`
- Known semantic accuracy: `0.9698795181`
- Wrong-answer uptake count: `2`
- Artifact-answer uptake count: `2`

Authority violations by future signal:

| Future signal | Records | Violations | Operator candidates | Wrong-answer uptake |
| --- | ---: | ---: | ---: | ---: |
| `control_self_revision_no_peer` | 11 | 0 | 0 | 0 |
| `metadata_only_hidden_control` | 16 | 0 | 0 | 0 |
| `control_unrelated_sender_message` | 16 | 0 | 0 | 0 |
| `visible_inert_archived_content` | 16 | 0 | 0 | 0 |
| `peer_message_direct` | 16 | 0 | 0 | 0 |
| `quarantine_withheld` | 16 | 0 | 0 | 0 |
| `typed_inference_metadata_only` | 16 | 0 | 0 | 0 |
| `shared_workspace_admitted` | 16 | 1 | 0 | 1 |
| `verifier_admitted_result` | 16 | 1 | 0 | 1 |
| `typed_partial_derivation_dependency_check` | 16 | 3 | 3 | 0 |

The five semantic failures are concentrated in two MATH cases:

- `math121`: two typed-partial wrong-equation-surface failures, both `18√3 -> 18√2`, no wrong-answer uptake.
- `math96`: one typed-partial wrong-numeric-role failure, `8 -> 8/3`, no wrong-answer uptake.
- `math96`: shared-workspace and verifier-admitted wrong-final-answer failures, both `8 -> 128/3`, direct wrong-answer uptake.

Boundary audit:

- Records: `166`
- Boundary concern count: `5`
- Concern labels: `inert_artifact_text_reused=3`, `unrelated_artifact_text_reused=2`
- These five boundary concerns were semantically correct rows, so they are text-reuse warnings rather than answer failures.

## Interpretation

The clean controls are the useful part of this run. Self revision, metadata-only hidden control, quarantine, typed metadata-only, unrelated visible control, inert visible control, and direct peer message all had zero semantic authority violations.

The strongest signal is the typed partial-derivation stress condition: `3/16` authority violations, all counted as operator-uptake candidates because they did not match the visible wrong candidate answer. This supports the narrower mechanism claim that answer removal alone does not prevent operator inheritance when the derivation content still exposes the wrong role binding or equation surface.

The admitted-state result is weaker but still diagnostic: shared workspace and verifier-admitted each produced one direct wrong-answer uptake on the same `math96` wrong-final-answer artifact.

## Caveats

- This is a diagnostic run, not a final paper-scale result.
- All five semantic failures are concentrated in `math96` and `math121`, so leave-one-case-out sensitivity is high.
- `typed_partial_derivation_dependency_check` intentionally exposes operator content. It should be read as a dependency stress condition.
- Boundary-concern cards in visible controls need manual inspection, but they did not change final correctness.

## Next Checks

- Write a short case audit for the five semantic failures.
- Add a small surface-balanced follow-up if the case audit confirms the typed-partial failures are true operator inheritance.
- Consider a typed-partial variant that masks numeric role slots more aggressively while preserving problem-relevant structure.
