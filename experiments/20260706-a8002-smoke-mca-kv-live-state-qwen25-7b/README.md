# 20260706-a8002-smoke-mca-kv-live-state-qwen25-7b

## Purpose

Diagnostic smoke for MCA-KV after changing the implementation to transfer live sender-generation KV cache instead of deriving hidden artifacts from text records.

## Status

Completed on A800_2 GPU 6. This is not claim-bearing; it is a plumbing and progress-visibility check.

## Configuration

- Remote root: `/data/xuhaoming/yfy/research_workspace`
- Remote run dir: `/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-smoke-mca-kv-live-state-qwen25-7b`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Benchmark: `math500/test/canonical.jsonl`
- Unit: benchmark row
- Rows: `--limit 2`
- Protocol: `mca-kv-cache`
- State source: live sender generation
- GPU: `CUDA_VISIBLE_DEVICES=6`
- Agents/reviewers: `3/3`
- Prompt family: `standard-mad`
- Max tokens: sender `512`, receiver `512`, max model len `4096`
- Temperatures: sender `1.0`, receiver `0.2`, top-p `1.0`

## Readout

- Success signal: records are written row by row; each row reports sender state metadata, selected source indices, KV continuation metadata, and a summary is produced.
- Failure signal: model crashes, cache shape mismatch, no row-level progress, hidden outputs empty for in-scope rows, or records cannot be parsed.
- Invalidation conditions: this smoke is too small for behavioral interpretation; any accuracy/recovery/harm number is diagnostic only.

## Expected Artifacts

- `run_remote.sh`
- `run_remote.nohup.log`
- `launcher.pid`
- `math500-qwen25-7b-instruct-mca-kv-cache-state-all/records.jsonl`
- `math500-qwen25-7b-instruct-mca-kv-cache-state-all/summary.json`
- `math500-qwen25-7b-instruct-mca-kv-cache-state-all/summary.md`

## Result

- Started: `2026-07-06T12:38:05+08:00`
- Finished: `2026-07-06T12:39:40+08:00`
- Rows: 2
- Elapsed seconds: 93.0
- Initial majority accuracy: 0.5000
- Final accuracy: 0.5000
- Hidden channel rate: 1.0000
- Wrong-majority recovery rate: 0.0000
- Correct-majority harm rate: 0.0000

Interpretation: live KV-cache transfer is runnable and writes visible row-level progress plus complete records. This smoke is too small for behavioral claims.
