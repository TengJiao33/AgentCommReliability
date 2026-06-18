# PerspectiveGap Tight-Budget Source-Ledger Smoke, Qwen2.5-14B

## Purpose

Test whether a utility-aware source-ledger prompt helps Qwen2.5-14B choose high-utility source subsets under scarce role budgets, and whether the budget compiler can turn the model's source order into a feasible routing plan.

## Launch

- Host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- GPU: `7`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-perspectivegap-tight-budget-source-ledger`
- Port: `8069`
- Packet: `experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl`
- Rows: `40`
- Script: `scripts/run_perspectivegap_tight_budget_source_ledger_a8002.sh`
- Cleanup: script trap terminated vLLM; post-run GPU check showed GPU 7 back to `4 MiB`.

## Results

| Condition | Strict | Coverage | Precision | Budget pass | Overrun | Utility ratio | Raw utility ratio | Exact role target |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| raw source-ledger 14B | 0/40 | 0.778 | 0.531 | 0.025 | 23.000 | 0.147 | 1.205 | 0.157 |
| budget-compiled source-ledger 14B | 10/40 | 0.704 | 0.919 | 1.000 | 0.000 | 0.846 | 0.846 | 0.608 |

The raw model usually lists too many eligible sources. It achieves `1.205` raw utility ratio, but almost all of that disappears under feasibility because it violates role budgets. The compiler restores budget feasibility and high precision, but the resulting utility ratio is below the offline full-prompt 14B recompile (`0.871`) and well below the local utility-density greedy baseline (`0.982`).

## Artifacts

- `predictions.jsonl`: raw source-ledger model outputs compiled into hard cards without budget filtering.
- `scores_raw.jsonl`, `summary_raw.md`, `summary_raw.json`: tight-budget scoring for raw model cards.
- `predictions_budget_compiled.jsonl`: deterministic recipient and budget compilation over the model's source order.
- `scores_budget_compiled.jsonl`, `summary_budget_compiled.md`, `summary_budget_compiled.json`: tight-budget scoring for compiled cards.
- `run.log`, `runner.stdout.log`, `vllm.log`: launch and execution logs.

## Interpretation

This is a benchmark-shape diagnostic. The run supports the budget compiler as a boundary executor, but it does not support the current `rank_scope` utility packet as a strong benchmark: a simple utility-density greedy baseline is already near oracle.
