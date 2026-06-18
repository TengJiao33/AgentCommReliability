# PerspectiveGap Tight-Budget V0

## Purpose

This packet turns the rotated source/scope gate into a scarce-bandwidth routing task. The full eligible source set is preserved in `candidate_need_sets`, while `reference_need_sets` becomes the oracle subset selected under a per-role budget by additive utility.

## Packet

- Source packet: `experiments/20260618-local-perspectivegap-source-perturbation-v0/source_perturbation_rotated20.jsonl`
- Output packet: `tight_budget_rotated20.jsonl`
- Rows: `40`
- Role rows: `160`
- Scarce role rows: `134/160`
- Mean budget ratio: `0.589`
- Mean candidate sources per role: `3.375`
- Mean oracle-selected sources per role: `2.1125`
- Budget fraction: `0.55`
- Utility rule: `rank_scope`

## Local Baselines

| Condition | Strict | Coverage | Precision | Budget pass | Overrun | Utility ratio | Raw utility ratio | Exact role target |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| oracle_utility | 40/40 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| eligible_all | 0/40 | 1.000 | 0.626 | 0.000 | 21.650 | 0.100 | 1.444 | 0.140 |
| eligible_cheapest | 14/40 | 0.864 | 0.844 | 1.000 | 0.000 | 0.893 | 0.893 | 0.724 |
| utility_density_greedy | 25/40 | 0.950 | 0.939 | 1.000 | 0.000 | 0.982 | 0.982 | 0.878 |

`eligible_all` is the budget-sanity control: it obtains high raw utility by sending all eligible sources, but its feasible utility collapses because it violates budget on almost every row.

## Offline Model-Priority Compiler

Existing full-budget source-ledger outputs were recompiled through this tight packet. These are diagnostic only because the original model prompts did not include the utility objective.

| Condition | Strict | Coverage | Precision | Budget pass | Utility ratio | Exact role target |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| source_ledger_7b_fullprompt_budget_compiled | 2/40 | 0.467 | 0.778 | 1.000 | 0.603 | 0.371 |
| source_ledger_14b_fullprompt_budget_compiled | 11/40 | 0.751 | 0.927 | 1.000 | 0.871 | 0.684 |

## Commands

```powershell
python scripts\build_perspectivegap_tight_budget_packet.py `
  --packet experiments\20260618-local-perspectivegap-source-perturbation-v0\source_perturbation_rotated20.jsonl `
  --out experiments\20260618-local-perspectivegap-tight-budget-v0\tight_budget_rotated20.jsonl `
  --budget-fraction 0.55
```

```powershell
python scripts\generate_perspectivegap_tight_budget_baselines.py `
  --packet experiments\20260618-local-perspectivegap-tight-budget-v0\tight_budget_rotated20.jsonl `
  --baseline utility_density_greedy `
  --out experiments\20260618-local-perspectivegap-tight-budget-v0\predictions_utility_density_greedy.jsonl
```

```powershell
python scripts\score_perspectivegap_tight_budget.py `
  --packet experiments\20260618-local-perspectivegap-tight-budget-v0\tight_budget_rotated20.jsonl `
  --predictions experiments\20260618-local-perspectivegap-tight-budget-v0\predictions_utility_density_greedy.jsonl `
  --out experiments\20260618-local-perspectivegap-tight-budget-v0\scores_utility_density_greedy.jsonl `
  --summary-out experiments\20260618-local-perspectivegap-tight-budget-v0\summary_utility_density_greedy.md
```

## Caveat

The first utility rule is too friendly to simple greedy selection. This packet is useful as a budget-scarcity smoke and scorer validation, but it should not be treated as a final benchmark design.

## Next

Build a harder scarce-bandwidth packet with non-greedy utility, dependency closure, or role-coupled constraints before spending a full model sweep.
