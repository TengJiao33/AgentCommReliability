# State Admission V1.1 Full40 Qwen2.5-14B Default Prompt

## Purpose

This run tests whether Qwen2.5-14B can solve the State Admission V1.1 role-scoped source admission packet when the prompt exposes global budget, role budgets, role bundles, pair groups, source eligibility, standalone hints, and payload previews.

The diagnostic question is whether model-only admission can match the oracle or the strong symbolic `group_density_global` planner, or whether it collapses into over-admitting locally useful evidence.

## Launch

- Remote: `A800_2:/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-state-admission-v1`
- GPU: `7`
- Port: `8071`
- Packet: `experiments/20260618-local-state-admission-v1/state_admission_v1_rotated20.jsonl`
- Rows: `40`
- Prompt style: `default`
- Temperature: `0`
- Max tokens: `1536`
- Max model len: `16384`
- Timeout: `7200`
- Cleanup: launch script `trap` killed vLLM after scoring; post-run GPU 7 returned to `4 MB`, port `8071` had no listener.

```bash
GPU_ID=7 \
PORT=8071 \
RUN_ID=20260618-a8002-state-admission-v1-full40-qwen25-14b \
RUN_TIMEOUT=7200 \
HARD_IDS_MODE=all \
MAX_TOKENS=1536 \
MAX_MODEL_LEN=16384 \
nohup bash scripts/run_state_admission_v1_a8002.sh
```

## Outputs

- `predictions.jsonl`
- `scores.jsonl`
- `summary.json`
- `summary.md`
- `run.log`
- `runner.stdout.log`
- `vllm.log`

## Summary

```text
evaluations: 40
strict_pass: 0.0000 (0/40)
required_coverage: 1.0000
boundary_precision: 0.4025
budget_pass: 0.6250
budget_overrun: 6.7000
source_accuracy_on_tp: 1.0000
visibility_accuracy_on_tp: 0.7178
reject_recall: 1.0000
needed_rejected: 0.0000
utility_ratio: 0.0000
raw_utility_ratio: 1.0307
completed_role_rate: 0.7663
exact_oracle_role_rate: 0.4350
per_role_budget_pass_rate: 0.7867
global_budget_pass: 0.0000
global_budget_overrun: 15.3250
closure_violations: 0.0250
oracle_utility: 33561
feasible_completed_utility: 0
raw_completed_utility: 34591
```

## Triage

- The run parsed and scored all `40/40` rows.
- Oracle-needed roles were always covered: `63/78` expected nonempty roles were exact, and the remaining `15/78` were supersets.
- Expected empty roles were always filled: `82/82`.
- Per-role budget overruns occurred in `44/160` role outputs.
- Global budget failed on every row: `0/40`.
- The strongest mechanism signal is over-admission: the model recognizes useful sources, then admits extra locally plausible role bundles until the row-level budget collapses.

## Status

Diagnostic model result. It supports a model-facing admission-boundary pressure signal, but it does not support a method claim by itself.

The strongest caveat is that `group_density_global` already reaches `32/40` strict and `0.967` utility ratio on the same packet, so the current benchmark pressures LLM state admission more than it pressures symbolic planning.
