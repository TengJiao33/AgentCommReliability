# State Admission V1.1 Full40 Qwen2.5-14B Budget-First Prompt

## Purpose

This run is a prompt-control over the default Qwen2.5-14B State Admission V1.1 run. It adds an explicit budget-first decision procedure:

- choose the role bundles or pair group before assigning sources;
- allow some roles to receive an empty list;
- reject eligible but unselected sources;
- treat useful-looking extra roles as invalid when they break the global budget.

The diagnostic question is whether the default run failed because the prompt did not emphasize empty-role selection and global budget strongly enough.

## Launch

- Remote: `A800_2:/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-state-admission-v1`
- GPU: `7`
- Port: `8071`
- Packet: `experiments/20260618-local-state-admission-v1/state_admission_v1_rotated20.jsonl`
- Rows: `40`
- Prompt style: `budget_first`
- Temperature: `0`
- Max tokens: `1536`
- Max model len: `16384`
- Timeout: `7200`
- Cleanup: launch script `trap` killed vLLM after scoring; post-run GPU 7 returned to `4 MB`, port `8071` had no listener.

```bash
GPU_ID=7 \
PORT=8071 \
RUN_ID=20260618-a8002-state-admission-v1-budgetfirst-full40-qwen25-14b \
RUN_TIMEOUT=7200 \
HARD_IDS_MODE=all \
PROMPT_STYLE=budget_first \
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
required_coverage: 0.7914
boundary_precision: 0.4464
budget_pass: 0.8500
budget_overrun: 0.6750
source_accuracy_on_tp: 1.0000
visibility_accuracy_on_tp: 0.7132
reject_recall: 0.9250
needed_rejected: 0.2250
utility_ratio: 0.0203
raw_utility_ratio: 0.8114
completed_role_rate: 0.7746
exact_oracle_role_rate: 0.4700
per_role_budget_pass_rate: 0.8658
global_budget_pass: 0.1000
global_budget_overrun: 7.1500
closure_violations: 0.1500
oracle_utility: 33561
feasible_completed_utility: 681
raw_completed_utility: 27231
```

## Triage

- The run parsed and scored all `40/40` rows.
- Expected empty roles were filled in `68/82` cases, down from `82/82` in the default run.
- Per-role budget overruns dropped to `10/160`, down from `44/160`.
- Oracle-needed roles became less stable: `57/78` expected nonempty roles were exact, `3/78` were supersets, and `18/78` missed required content.
- Global budget passed on `4/40` rows, but strict remained `0/40` because those budget-valid rows lost required coverage or rejected needed sources.

## Status

Diagnostic prompt-control result. It shows that stronger budget wording reduces over-admission but does not solve the admission problem. The model moves along a bad tradeoff: fewer extra roles, lower required coverage, and still almost no feasible utility.
