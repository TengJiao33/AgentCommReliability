# State Admission V1.1 Full40 Qwen2.5-14B Priority Executor

## Purpose

This run tests whether the State Admission V1.1 failure comes mainly from direct source-card emission or from higher-level admission preference.

The model outputs only a ranked list of admission units:

- pair group ids;
- role bundle ids.

A deterministic executor then enforces source assignment, role closure, per-role budgets, global budget, rejection of unselected sources, and visibility labels before scoring with `score_state_admission_v1.py`.

## Launch

- Remote: `A800_2:/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-state-admission-v1`
- GPU: `7`
- Port: `8071`
- Packet: `experiments/20260618-local-state-admission-v1/state_admission_v1_rotated20.jsonl`
- Rows: `40`
- Router mode: `priority`
- Prompt style: `default`
- Executor policy during GPU run: `greedy`
- Temperature: `0`
- Max tokens: `1024`
- Max model len: `16384`
- Timeout: `7200`
- Cleanup: launch script `trap` killed vLLM after scoring; post-run GPU 7 returned to `4 MB`, port `8071` had no listener.

```bash
GPU_ID=7 \
PORT=8071 \
RUN_ID=20260618-a8002-state-admission-v1-priority-full40-qwen25-14b \
RUN_TIMEOUT=7200 \
HARD_IDS_MODE=all \
ROUTER_MODE=priority \
PROMPT_STYLE=default \
MAX_TOKENS=1024 \
MAX_MODEL_LEN=16384 \
nohup bash scripts/run_state_admission_v1_a8002.sh
```

## Outputs

- `predictions.jsonl`
- `scores.jsonl`
- `summary.json`
- `summary.md`
- `predictions_pair_group_primary_recompiled.jsonl`
- `scores_pair_group_primary_recompiled.jsonl`
- `summary_pair_group_primary_recompiled.md`
- `run.log`
- `runner.stdout.log`
- `vllm.log`

## GPU Run Summary

This is the original GPU run with the `greedy` executor policy.

```text
evaluations: 40
strict_pass: 0.7000 (28/40)
required_coverage: 0.8957
boundary_precision: 0.8202
distractor_leakage: 0.0000
budget_pass: 1.0000
budget_overrun: 0.0000
source_accuracy_on_tp: 1.0000
visibility_accuracy_on_tp: 0.9452
reject_recall: 1.0000
needed_rejected: 0.2500
utility_ratio: 0.9067
raw_utility_ratio: 0.9067
completed_role_rate: 0.5433
exact_oracle_role_rate: 0.8900
per_role_budget_pass_rate: 1.0000
global_budget_pass: 1.0000
global_budget_overrun: 0.0000
closure_violations: 0.0000
oracle_utility: 33561
feasible_completed_utility: 30430
raw_completed_utility: 30430
```

## Offline Recompile

The same `priority_response` rows were recompiled with `executor_policy=pair_group_primary`.

```powershell
python scripts\run_state_admission_v1_priority_openai_compatible.py `
  --packet experiments\20260618-local-state-admission-v1\state_admission_v1_rotated20.jsonl `
  --recompile-predictions experiments\20260618-a8002-state-admission-v1-priority-full40-qwen25-14b\predictions.jsonl `
  --executor-policy pair_group_primary `
  --out experiments\20260618-a8002-state-admission-v1-priority-full40-qwen25-14b\predictions_pair_group_primary_recompiled.jsonl

python scripts\score_state_admission_v1.py `
  --packet experiments\20260618-local-state-admission-v1\state_admission_v1_rotated20.jsonl `
  --predictions experiments\20260618-a8002-state-admission-v1-priority-full40-qwen25-14b\predictions_pair_group_primary_recompiled.jsonl `
  --out experiments\20260618-a8002-state-admission-v1-priority-full40-qwen25-14b\scores_pair_group_primary_recompiled.jsonl `
  --summary-out experiments\20260618-a8002-state-admission-v1-priority-full40-qwen25-14b\summary_pair_group_primary_recompiled.md
```

```text
evaluations: 40
strict_pass: 0.8250 (33/40)
required_coverage: 0.8712
boundary_precision: 0.9103
distractor_leakage: 0.0000
budget_pass: 1.0000
budget_overrun: 0.0000
source_accuracy_on_tp: 1.0000
visibility_accuracy_on_tp: 0.9648
reject_recall: 1.0000
needed_rejected: 0.3000
utility_ratio: 0.9014
raw_utility_ratio: 0.9014
completed_role_rate: 0.4883
exact_oracle_role_rate: 0.9283
per_role_budget_pass_rate: 1.0000
global_budget_pass: 1.0000
global_budget_overrun: 0.0000
closure_violations: 0.0000
oracle_utility: 33561
feasible_completed_utility: 30251
raw_completed_utility: 30251
```

## Comparison

| Condition | Strict | Coverage | Precision | Global budget pass | Utility ratio | Closure violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| direct default Qwen2.5-14B | 0/40 | 1.0000 | 0.4025 | 0.0000 | 0.0000 | 0.0250 |
| direct budget-first Qwen2.5-14B | 0/40 | 0.7914 | 0.4464 | 0.1000 | 0.0203 | 0.1500 |
| priority + greedy executor | 28/40 | 0.8957 | 0.8202 | 1.0000 | 0.9067 | 0.0000 |
| priority + pair-group-primary recompile | 33/40 | 0.8712 | 0.9103 | 1.0000 | 0.9014 | 0.0000 |
| symbolic group-density baseline | 32/40 | 0.9018 | 1.0000 | 1.0000 | 0.9666 | 0.0000 |
| oracle priority executor | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

## Triage

- The priority run completed `40/40` rows with `40` parseable outputs.
- The deterministic executor removed all global-budget and closure failures.
- The greedy executor recovered high utility but sometimes admitted extra single-role bundles after already completing the best pair group.
- The `pair_group_primary` offline recompile cleaned up many of those extras, improving strict from `28/40` to `33/40`.
- The remaining failures are mostly high-level priority mistakes: the model ranks a plausible but lower-value pair group before the oracle pair group, and the executor faithfully commits to it.

## Status

Diagnostic method-shape result. It supports a live intervention surface: model proposes admission priorities; a deterministic rule layer enforces legal state admission.

The strongest caveat is that the prompt exposes bundle and pair-group tables directly. This run does not yet prove that the model can infer admission units from raw task traces, nor that the protocol improves downstream multi-agent task success.
