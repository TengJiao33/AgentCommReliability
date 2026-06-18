# State Admission V1.1 Full40 Qwen2.5-7B Priority Executor

## Purpose

This run tests whether the State Admission V1.1 priority-executor decomposition survives a smaller model.

The model outputs ranked admission units, and the deterministic executor uses `pair_group_primary` to enforce source assignment, role closure, per-role budgets, global budget, rejection of unselected sources, and visibility labels.

## Launch

- Remote: `A800_2:/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Served model: `qwen2.5-7b-state-admission-v1-priority`
- GPU: `7`
- Port: `8071`
- Packet: `experiments/20260618-local-state-admission-v1/state_admission_v1_rotated20.jsonl`
- Rows: `40`
- Router mode: `priority`
- Prompt style: `default`
- Executor policy during GPU run: `pair_group_primary`
- Temperature: `0`
- Max tokens: `1024`
- Max model len: `16384`
- Timeout: `7200`
- Cleanup: launch script `trap` cleaned up vLLM; post-run check reported no launcher process, no port `8071` listener, and GPU 7 back at `4 MB`.

```bash
GPU_ID=7 \
PORT=8071 \
RUN_ID=20260618-a8002-state-admission-v1-priority-full40-qwen25-7b \
RUN_TIMEOUT=7200 \
HARD_IDS_MODE=all \
ROUTER_MODE=priority \
PROMPT_STYLE=default \
EXECUTOR_POLICY=pair_group_primary \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct \
SERVED_MODEL=qwen2.5-7b-state-admission-v1-priority \
MAX_TOKENS=1024 \
MAX_MODEL_LEN=16384 \
nohup bash scripts/run_state_admission_v1_a8002.sh > experiments/$RUN_ID/ssh_launch.log 2>&1 &
```

## Outputs

- `predictions.jsonl`
- `scores.jsonl`
- `summary.json`
- `summary.md`
- `predictions_normalized_recompiled.jsonl`
- `scores_normalized_recompiled.jsonl`
- `summary_normalized_recompiled.md`
- `run.log`
- `runner.stdout.log`
- `vllm.log`
- `ssh_launch.log`

## GPU Run Summary

```text
evaluations: 40
strict_pass: 0.6250 (25/40)
required_coverage: 0.7546
boundary_precision: 0.9044
distractor_leakage: 0.0000
budget_pass: 1.0000
budget_overrun: 0.0000
source_accuracy_on_tp: 1.0000
visibility_accuracy_on_tp: 0.9675
reject_recall: 1.0000
needed_rejected: 0.7000
utility_ratio: 0.8530
raw_utility_ratio: 0.8530
completed_role_rate: 0.3800
exact_oracle_role_rate: 0.8150
per_role_budget_pass_rate: 1.0000
global_budget_pass: 1.0000
global_budget_overrun: 0.0000
closure_violations: 0.0000
oracle_utility: 33561
feasible_completed_utility: 28629
raw_completed_utility: 28629
```

## Normalized Offline Recompile

The same `priority_response` rows were recompiled after conservative unit-id normalization in `run_state_admission_v1_priority_openai_compatible.py`.

Normalization strips prefixes such as `bundle_id=` and resolves unique aliases where the model replaced spaces with underscores. It does not add missing units or change the executor objective.

```powershell
python scripts\run_state_admission_v1_priority_openai_compatible.py `
  --packet experiments\20260618-local-state-admission-v1\state_admission_v1_rotated20.jsonl `
  --recompile-predictions experiments\20260618-a8002-state-admission-v1-priority-full40-qwen25-7b\predictions.jsonl `
  --executor-policy pair_group_primary `
  --out experiments\20260618-a8002-state-admission-v1-priority-full40-qwen25-7b\predictions_normalized_recompiled.jsonl

python scripts\score_state_admission_v1.py `
  --packet experiments\20260618-local-state-admission-v1\state_admission_v1_rotated20.jsonl `
  --predictions experiments\20260618-a8002-state-admission-v1-priority-full40-qwen25-7b\predictions_normalized_recompiled.jsonl `
  --out experiments\20260618-a8002-state-admission-v1-priority-full40-qwen25-7b\scores_normalized_recompiled.jsonl `
  --summary-out experiments\20260618-a8002-state-admission-v1-priority-full40-qwen25-7b\summary_normalized_recompiled.md
```

```text
evaluations: 40
strict_pass: 0.6500 (26/40)
required_coverage: 0.7853
boundary_precision: 0.9078
distractor_leakage: 0.0000
budget_pass: 1.0000
budget_overrun: 0.0000
source_accuracy_on_tp: 1.0000
visibility_accuracy_on_tp: 0.9688
reject_recall: 1.0000
needed_rejected: 0.6000
utility_ratio: 0.8828
raw_utility_ratio: 0.8828
completed_role_rate: 0.3967
exact_oracle_role_rate: 0.8317
per_role_budget_pass_rate: 1.0000
global_budget_pass: 1.0000
global_budget_overrun: 0.0000
closure_violations: 0.0000
oracle_utility: 33561
feasible_completed_utility: 29629
raw_completed_utility: 29629
```

## Comparison

| Condition | Strict | Coverage | Precision | Global budget pass | Utility ratio | Closure violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-7B priority + pair-group-primary | 25/40 | 0.7546 | 0.9044 | 1.0000 | 0.8530 | 0.0000 |
| Qwen2.5-7B normalized recompile | 26/40 | 0.7853 | 0.9078 | 1.0000 | 0.8828 | 0.0000 |
| Qwen2.5-14B priority + pair-group-primary | 33/40 | 0.8712 | 0.9103 | 1.0000 | 0.9014 | 0.0000 |
| symbolic group-density baseline | 32/40 | 0.9018 | 1.0000 | 1.0000 | 0.9666 | 0.0000 |
| oracle priority executor | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

## Triage

- The GPU run completed `40/40` rows with parseable outputs.
- Legal admission stayed clean: global budget pass `1.0000`, per-role budget pass `1.0000`, closure violations `0.0000`, distractor leakage `0.0000`.
- Conservative normalization reduced `unknown_unit` skips from `37` to `3`, but strict improved only from `25/40` to `26/40`.
- The single newly passing row was `pg_109__seed_42`.
- After normalized recompile, 7B failed `14` rows and 14B failed `7` rows under the same packet and executor; their failure overlap was `4` rows.
- A common 7B failure pattern is explanation-text reasoning about a feasible fallback bundle while the JSON priority keeps only an infeasible pair group. The executor can only compile the JSON priority, so those rows remain empty or under-covered.

## Status

Diagnostic cross-model replication. It supports the priority-executor decomposition because a smaller model still reaches legal admission with useful utility, but it also shows that priority quality and machine-executable fallback listing are now first-class bottlenecks.

The result is stronger as a protocol-shape signal than as a hard benchmark win. The symbolic group-density baseline remains strong, and the prompt still exposes admission units directly.
