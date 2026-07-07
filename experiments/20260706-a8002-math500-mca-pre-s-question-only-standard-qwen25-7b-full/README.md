# 20260706-a8002-math500-mca-pre-s-question-only-standard-qwen25-7b-full

## Purpose

Full diagnostic run for MCA-Pre-S with question-only pre-answer state.

## Status

Launched on A800_2 GPU 3, which was fully empty by `nvidia-smi pmon` at preflight.

- Launcher PID: `2388112`
- Worker PID: `2388139`
- Started: `2026-07-06T13:44:31+08:00`
- Status check at `2026-07-06T13:48:37+08:00`: row-level progress active; `records.jsonl` had 1 row.

## Configuration

- Remote root: `/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Benchmark: `math500/test/canonical.jsonl`
- Rows: 500
- Protocol: `mca-pre-activation-steering`
- Pre-state stage: `question_only`
- State source: `pre_answer_sender_pass`
- Agents/reviewers: `3/3`
- GPU: `3`
- Steering: layer `16`, scale `1.0`
- Max tokens: baseline sender `4096`, receiver `1536`, max model len `8192`
- Temperatures: baseline `1.0`, receiver `0.2`, top-p `1.0`

## Artifacts

- `run_remote.sh`
- `run_remote.nohup.log`
- `launcher.pid`
- `math500-qwen25-7b-instruct-mca-pre-activation-steering-question_only-state/records.jsonl`
- `math500-qwen25-7b-instruct-mca-pre-activation-steering-question_only-state/summary.json`
- `math500-qwen25-7b-instruct-mca-pre-activation-steering-question_only-state/summary.md`
