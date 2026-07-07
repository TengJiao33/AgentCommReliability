# 20260706-a8002-math500-mca-pre-kv-early-plan-standard-qwen25-7b-full

## Purpose

Full diagnostic run for MCA-Pre-KV with short early-plan pre-answer state.

## Status

Launched on A800_2 GPU 4, which was fully empty by `nvidia-smi pmon` at preflight.

- Launcher PID: `2388100`
- Worker PID: `2388135`
- Started: `2026-07-06T13:44:31+08:00`
- Status check at `2026-07-06T13:48:37+08:00`: row-level progress active; `records.jsonl` had 4 rows.

## Configuration

- Remote root: `/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Benchmark: `math500/test/canonical.jsonl`
- Rows: 500
- Protocol: `mca-pre-kv-cache`
- Pre-state stage: `early_plan`
- Pre-state tokens: `64`
- State source: `pre_answer_sender_pass`
- Agents/reviewers: `3/3`
- GPU: `4`
- Max tokens: baseline sender `4096`, receiver `1536`, max model len `8192`
- Temperatures: pre-state `0.7`, baseline `1.0`, receiver `0.2`, top-p `1.0`

## Artifacts

- `run_remote.sh`
- `run_remote.nohup.log`
- `launcher.pid`
- `math500-qwen25-7b-instruct-mca-pre-kv-cache-early_plan-state/records.jsonl`
- `math500-qwen25-7b-instruct-mca-pre-kv-cache-early_plan-state/summary.json`
- `math500-qwen25-7b-instruct-mca-pre-kv-cache-early_plan-state/summary.md`
