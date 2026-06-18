# State Admission V1.1 Full40 Qwen2.5-7B Fallback-Required Priority

## Purpose

This run tests whether the main Qwen2.5-7B priority-executor gap is partly caused by non-executable priority JSON.

The previous 7B run often explained that an infeasible pair group should fall back to an individual role bundle, while the JSON `priority` list kept only the infeasible pair group. The `fallback_required` prompt style explicitly tells the model that the deterministic executor reads only JSON priority and requires fallback bundles after pair groups that may exceed the global budget.

## Launch

- Remote: `A800_2:/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Served model: `qwen2.5-7b-state-admission-v1-priority-fallback`
- GPU: `7`
- Port: `8071`
- Packet: `experiments/20260618-local-state-admission-v1/state_admission_v1_rotated20.jsonl`
- Rows: `40`
- Router mode: `priority`
- Prompt style: `fallback_required`
- Executor policy: `pair_group_primary`
- Temperature: `0`
- Max tokens: `1024`
- Max model len: `16384`
- Timeout: `7200`
- Cleanup: launch script `trap` cleaned up vLLM; post-run GPU 7 returned to `4 MB`, and port `8071` had no listener.

```bash
GPU_ID=7 \
PORT=8071 \
RUN_ID=20260618-a8002-state-admission-v1-priority-fallback-full40-qwen25-7b \
RUN_TIMEOUT=7200 \
HARD_IDS_MODE=all \
ROUTER_MODE=priority \
PROMPT_STYLE=fallback_required \
EXECUTOR_POLICY=pair_group_primary \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct \
SERVED_MODEL=qwen2.5-7b-state-admission-v1-priority-fallback \
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

## Summary

```text
evaluations: 40
strict_pass: 0.7750 (31/40)
required_coverage: 0.8344
boundary_precision: 0.8718
distractor_leakage: 0.0000
budget_pass: 1.0000
budget_overrun: 0.0000
source_accuracy_on_tp: 1.0000
visibility_accuracy_on_tp: 0.9338
reject_recall: 1.0000
needed_rejected: 0.3250
utility_ratio: 0.8431
raw_utility_ratio: 0.8431
completed_role_rate: 0.4883
exact_oracle_role_rate: 0.8817
per_role_budget_pass_rate: 1.0000
global_budget_pass: 1.0000
global_budget_overrun: 0.0000
closure_violations: 0.0000
oracle_utility: 33561
feasible_completed_utility: 28296
raw_completed_utility: 28296
```

## Comparison

| Condition | Strict | Coverage | Precision | Global budget pass | Utility ratio | Closure violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-7B default priority | 25/40 | 0.7546 | 0.9044 | 1.0000 | 0.8530 | 0.0000 |
| Qwen2.5-7B normalized recompile | 26/40 | 0.7853 | 0.9078 | 1.0000 | 0.8828 | 0.0000 |
| Qwen2.5-7B fallback-required priority | 31/40 | 0.8344 | 0.8718 | 1.0000 | 0.8431 | 0.0000 |
| Qwen2.5-14B priority + pair-group-primary | 33/40 | 0.8712 | 0.9103 | 1.0000 | 0.9014 | 0.0000 |
| symbolic group-density baseline | 32/40 | 0.9018 | 1.0000 | 1.0000 | 0.9666 | 0.0000 |

## Triage

- The run completed `40/40` rows with `40` `status=ok` predictions.
- Compared with normalized 7B recompile, fallback-required gained `8` strict rows and regressed `3`, for a net improvement from `26/40` to `31/40`.
- Newly strict-passing rows over normalized 7B: `pg_000` seeds `1` and `42`; `pg_015` seeds `1` and `42`; `pg_022` seeds `1` and `42`; `pg_029` seeds `1` and `42`.
- Regressed rows from normalized 7B: `pg_002` seeds `1` and `42`; `pg_066` seed `42`.
- Skip reasons changed from default `{global_budget: 37, pair_group_primary_mode: 100, unknown_unit: 37, role_already_closed: 62}` to fallback `{global_budget: 57, pair_group_primary_mode: 143, role_already_closed: 80}`. The `unknown_unit` failure disappeared.
- Fallback-required still failed `9` rows; `4` of those overlap with 14B pair-group-primary failures.

## Status

Diagnostic schema-pressure result. It shows that executable-priority prompting matters: a schema that forces fallback bundles into JSON substantially improves 7B strict score while preserving legal budgets and closure.

The tradeoff is utility and precision. The model lists more candidate units, and the executor rejects more infeasible units. This makes strict higher but utility lower than normalized 7B and 14B pair-group-primary. The next pressure should combine fallback-required JSON with hidden or weakened admission-unit tables.
