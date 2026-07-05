# CPAC-DCAC guard-v1 standard-fixed MATH500 full, 4096 output

## Purpose

Run the guarded CPAC+DCAC mechanism with the same chat-rendered Standard MAD initial prompt family as the standard MAD baseline.

The main contrast is same-run initial majority versus guarded CPAC+DCAC final output.

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
- Planned GPU: `2`.

## Launch

See `run_remote.sh`.

## Status

`PREPARED_GPU2`.

Prepared on 2026-07-06 CST for GPU `2`.

## Expected Outputs

- `math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.json`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.md`
- `run_remote.nohup.log`
- `launcher.pid`
