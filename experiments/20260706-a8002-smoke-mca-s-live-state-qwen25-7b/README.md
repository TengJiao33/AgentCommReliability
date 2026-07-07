# 20260706-a8002-smoke-mca-s-live-state-qwen25-7b

## Purpose

Diagnostic smoke for MCA-S after changing the implementation to steer the receiver from a vector captured during live sender generation.

## Status

Failed on A800_2 GPU 6. This is not claim-bearing; it is a plumbing and progress-visibility check.

## Configuration

- Remote root: `/data/xuhaoming/yfy/research_workspace`
- Remote run dir: `/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-smoke-mca-s-live-state-qwen25-7b`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Benchmark: `math500/test/canonical.jsonl`
- Unit: benchmark row
- Rows: `--limit 2`
- Protocol: `mca-activation-steering`
- State source: live sender generation
- GPU: `CUDA_VISIBLE_DEVICES=6`
- Agents/reviewers: `3/3`
- Prompt family: `standard-mad`
- Steering: layer `16`, scale `1.0`
- Max tokens: sender `512`, receiver `512`, max model len `4096`
- Temperatures: sender `1.0`, receiver `0.2`, top-p `1.0`

## Readout

- Success signal: records are written row by row; sender activation metadata and receiver steering metadata appear in records; a summary is produced.
- Failure signal: hook/layer mismatch, tensor device mismatch, no row-level progress, hidden outputs empty for in-scope rows, or records cannot be parsed.
- Invalidation conditions: this smoke is too small for behavioral interpretation; any accuracy/recovery/harm number is diagnostic only.

## Expected Artifacts

- `run_remote.sh`
- `run_remote.nohup.log`
- `launcher.pid`
- `math500-qwen25-7b-instruct-mca-activation-steering-state-all/records.jsonl`
- `math500-qwen25-7b-instruct-mca-activation-steering-state-all/summary.json`
- `math500-qwen25-7b-instruct-mca-activation-steering-state-all/summary.md`

## Result

- Started: `2026-07-06T12:40:32+08:00`
- Failed during row 2 receiver generation.
- Failure: CUDA OOM after row 1 completed and row 2 selected three receiver sources.
- Partial caveat: row 1 parsed the literal prompt text `final answer only` as an answer, indicating the layer/scale/prompt contract is behaviorally unstable.

Fix applied afterward:

- receiver manual generation now runs under `torch.inference_mode()`;
- MCA-S sender state no longer retains unused sender KV caches.

See rerun: `experiments/20260706-a8002-smoke-mca-s-live-state-qwen25-7b-rerun1`.
