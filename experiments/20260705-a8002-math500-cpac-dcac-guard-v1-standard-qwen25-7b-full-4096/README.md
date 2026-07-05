# CPAC-DCAC guard-v1 standard MATH500 full, 4096 output

## Purpose

Run the guarded CPAC+DCAC mechanism under the current standard MATH-500 comparison口径.

The main contrast is same-run initial majority versus guarded CPAC+DCAC final output. This run is intended to make the old guard-v1 diagnostic comparable with the current standard MAD 4096 / 24064 setting.

## Design

- Task: `math500/test`, full 500 rows.
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`.
- Method: `scripts/run_cpac_dcac.py`.
- Protocol: Candidate-Pool Adaptive Consensus with guarded DCAC for the minority-bearing branch.
- Agents: 3 independent initial solvers.
- Reviewers: 3 certificate/listwise reviewers.
- No-majority action: `listwise`.
- DCAC flip rule: require 2 guarded admissible flip certificates.
- Temperature/top-p: all generation temperatures `1.0`, top-p `1.0`.
- Output budget: initial, claim, certificate, and listwise max tokens all `4096`.
- Context budget: `max_model_len=24064`.

## Machine

- Host: `A800_2`.
- Remote work dir: `/data/xuhaoming/yfy/research_workspace`.
- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`.
- Planned GPU: `5`.

## Launch

See `run_remote.sh`.

## Status

`RUNNING_GPU5`.

Launched on 2026-07-05 23:07 CST.

- First attempt on GPU `6` reached model load but failed during vLLM KV-cache allocation with CUDA OOM at `gpu_memory_utilization=0.85`; no records or summary were produced.
- Relaunch uses GPU `5` with `gpu_memory_utilization=0.55` while keeping model, prompts, temperatures, token budgets, and `max_model_len=24064` unchanged.
- Launcher PID: `3832761`.
- Timeout PID: `3832798`.
- Python PID: `3832799`.
- GPU: `5`.
- Log: `/data/xuhaoming/yfy/research_workspace/experiments/20260705-a8002-math500-cpac-dcac-guard-v1-standard-qwen25-7b-full-4096/run_remote.nohup.log`.
- Startup check: evaluator smoke and guard smoke passed; Qwen2.5-7B loaded with `max_seq_len=24064`; KV cache initialized with 30177 GPU blocks; CUDA graph capture completed.
- First failed log archived as `run_remote.oom-gpu6-2307.log`.

## Expected Outputs

- `math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.json`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.md`
- `run_remote.nohup.log`
- `launcher.pid`
