# State Admission V1.1 Full40 Qwen2.5-7B Ledger-First Router

## Purpose

This run tests the first hidden-unit pressure point for State Admission V1.1.

The model does not see role-bundle or pair-group tables. It sees only:

- roles and per-role budgets;
- global budget;
- source access ledger with eligible recipients, cost, utility, and standalone hint fields;
- payload previews.

The model outputs role-to-source priority lists. A deterministic compiler then enforces ledger scope, per-role budgets, global budget, rejection of unselected sources, and visibility labels before scoring with `score_state_admission_v1.py`.

## Launch

- Remote: `A800_2:/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Served model: `qwen2.5-7b-state-admission-v1-ledger`
- GPU: `7`
- Port: `8071`
- Packet: `experiments/20260618-local-state-admission-v1/state_admission_v1_rotated20.jsonl`
- Rows: `40`
- Router mode: `ledger`
- Prompt style: `utility_payload`
- Temperature: `0`
- Max tokens: `1024`
- Max model len: `16384`
- Timeout: `7200`
- Cleanup: launch script `trap` cleaned up vLLM; post-run GPU 7 returned to `4 MB`, and port `8071` had no listener.

```bash
GPU_ID=7 \
PORT=8071 \
RUN_ID=20260618-a8002-state-admission-v1-ledger-full40-qwen25-7b \
RUN_TIMEOUT=7200 \
HARD_IDS_MODE=all \
ROUTER_MODE=ledger \
PROMPT_STYLE=utility_payload \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct \
SERVED_MODEL=qwen2.5-7b-state-admission-v1-ledger \
MAX_TOKENS=1024 \
MAX_MODEL_LEN=16384 \
nohup bash scripts/run_state_admission_v1_a8002.sh > experiments/$RUN_ID/ssh_launch.log 2>&1 &
```

## Outputs

- `predictions.jsonl`
- `scores.jsonl`
- `summary.json`
- `summary.md`
- `run.log`
- `runner.stdout.log`
- `vllm.log`
- `ssh_launch.log`

## Local Controls

Before the GPU run, local compiler smokes were run through the same scorer:

| Local condition | Strict | Coverage | Precision | Global budget pass | Utility ratio | Closure violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ledger oracle | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| ledger utility-density | 4/40 | 0.7362 | 0.5106 | 1.0000 | 0.4931 | 1.0500 |
| ledger hint-density | 4/40 | 0.7055 | 0.4772 | 1.0000 | 0.4024 | 1.1000 |

This validates the compiler upper bound and shows that source-level density heuristics do not recover bundle closure.

## GPU Summary

```text
evaluations: 40
strict_pass: 0.0250 (1/40)
required_coverage: 0.4417
boundary_precision: 0.4645
distractor_leakage: 0.0000
budget_pass: 1.0000
budget_overrun: 0.0000
source_accuracy_on_tp: 1.0000
visibility_accuracy_on_tp: 0.8611
reject_recall: 1.0000
needed_rejected: 1.2500
utility_ratio: 0.0409
raw_utility_ratio: 0.0409
completed_role_rate: 0.0975
exact_oracle_role_rate: 0.3038
per_role_budget_pass_rate: 1.0000
global_budget_pass: 1.0000
global_budget_overrun: 0.0000
closure_violations: 1.6750
oracle_utility: 33561
feasible_completed_utility: 1371
raw_completed_utility: 1371
```

## Comparison

| Condition | Strict | Coverage | Precision | Global budget pass | Utility ratio | Closure violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-7B ledger-first | 1/40 | 0.4417 | 0.4645 | 1.0000 | 0.0409 | 1.6750 |
| ledger utility-density local | 4/40 | 0.7362 | 0.5106 | 1.0000 | 0.4931 | 1.0500 |
| Qwen2.5-7B fallback-required priority | 31/40 | 0.8344 | 0.8718 | 1.0000 | 0.8431 | 0.0000 |
| Qwen2.5-14B priority + pair-group-primary | 33/40 | 0.8712 | 0.9103 | 1.0000 | 0.9014 | 0.0000 |
| symbolic group-density baseline | 32/40 | 0.9018 | 1.0000 | 1.0000 | 0.9666 | 0.0000 |

## Triage

- The run completed `40/40` rows with `40` `status=ok` predictions.
- The only strict pass was `pg_000__seed_1`.
- The compiler kept legality clean: per-role budget pass `1.0000`, global budget pass `1.0000`, reject recall `1.0000`, distractor leakage `0.0000`.
- Compiler skip counts across all rows: invalid `9`, duplicate `1`, wrong recipient `70`, role budget `54`, global budget `43`.
- The average selected source-role assignments after compilation was `3.875` per row.
- The dominant failure is incomplete bundle construction: closure violations average `1.6750`, and utility ratio collapses to `0.0409`.

## Status

Diagnostic hidden-unit failure. The result says the exposed bundle/group table in priority runs is doing real work.

The ledger-first run should not be read as a model capability ceiling, because V1.1's pair-group utilities are synthetic and hidden from the model. It is useful as a pressure test: if we want a paper story, we need an explicit admission-unit construction stage or a V2 packet where units can be inferred from real downstream task structure.
