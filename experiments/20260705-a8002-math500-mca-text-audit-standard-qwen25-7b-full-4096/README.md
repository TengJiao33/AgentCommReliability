# MCA-T audit standard MATH500 full, 4096 output

## Purpose

Run conservative text-based MCA audit under the current standard MATH-500 comparison口径.

This run samples fresh initial answers with the Standard MAD prompt family, then extracts answer-free cues and allows answer changes only through cue-derived audit certificates.

## Design

- Task: `math500/test`, full 500 rows.
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`.
- Method: `scripts/run_mca_text_audit.py`.
- Protocol: `mca-text-audit`.
- Initial prompt style: `standard-mad`.
- Agents: 3 independent initial solvers.
- Reviewers: 3 audit reviewers.
- Cue count: 2 per source trace.
- Change rule: require 2 admissible change certificates.
- Pool-state scope: `all`.
- Temperature/top-p: all generation temperatures `1.0`, top-p `1.0`.
- Output budget: initial, cue, and audit max tokens all `4096`.
- Context budget: `max_model_len=24064`.

## Machine

- Host: `A800_2`.
- Remote work dir: `/data/xuhaoming/yfy/research_workspace`.
- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`.
- Planned GPU: `7`.

## Launch

See `run_remote.sh`.

## Status

`RUNNING_GPU7`.

First attempt on GPU `0` was stopped manually because GPU 0 already had other users' resident processes. No valid summary was produced; the partial log is archived as `run_remote.stopped-gpu0-2322.log`.

Relaunch uses GPU `7`, which was empty at launch check.

- Launcher PID: `3867571`.
- Timeout PID: `3867606`.
- Python PID: `3867607`.
- Startup check: evaluator smoke and audit aggregation smoke passed; Qwen2.5-7B loaded with `max_seq_len=24064`; KV cache initialized with 58001 GPU blocks; CUDA graph capture completed.

## Expected Outputs

- `math500-qwen25-7b-instruct-mca-text-audit-all/records.jsonl`
- `math500-qwen25-7b-instruct-mca-text-audit-all/summary.json`
- `math500-qwen25-7b-instruct-mca-text-audit-all/summary.md`
- `run_remote.nohup.log`
- `launcher.pid`
