# PerspectiveGap Budget-Compiled Source Ledger Rotated20

## Status

Completed offline compiler gate. No new model calls were made; this reuses the Qwen2.5 7B/14B source-ledger outputs from `20260618-a8002-perspectivegap-source-ledger-rotated20-*`.

## Purpose

Test whether a deterministic communication-state compiler can keep the source-ledger signal while enforcing valid recipients, global rejection, and per-role budget.

The model output is treated as an ordered source priority list. The compiler:

- resolves source IDs against the authoritative ledger;
- skips duplicate, invalid, and wrong-recipient sources;
- keeps the model order for valid sources;
- skips sources that would exceed the role budget;
- fills `source_id` and `visibility` from the final selected recipient set;
- emits all ledger `REJECT` entries as global rejections.

## Main Result

| Condition | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Visibility acc | Reject recall | Needed rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy_7b_on_rotated | 0/40 | 0.076 | 0.135 | 0.050 | 0.300 | 2.950 | 1.000 | 0.000 | 0.000 |
| source_ledger_7b_raw | 0/40 | 0.574 | 0.745 | 0.300 | 0.350 | 4.650 | 0.700 | 1.000 | 0.025 |
| source_ledger_7b_budget_compiled | 0/40 | 0.574 | 1.000 | 0.000 | 1.000 | 0.000 | 0.819 | 1.000 | 0.000 |
| legacy_14b_on_rotated | 0/40 | 0.150 | 0.197 | 0.450 | 0.075 | 8.250 | 1.000 | 0.000 | 0.000 |
| source_ledger_14b_raw | 3/40 | 0.854 | 0.779 | 0.075 | 0.225 | 13.150 | 0.761 | 1.000 | 0.000 |
| source_ledger_14b_budget_compiled | 12/40 | 0.854 | 1.000 | 0.000 | 1.000 | 0.000 | 0.952 | 1.000 | 0.000 |

The 14B budget-compiled result is the strongest result in this line so far: strict pass rises from `3/40` to `12/40` without losing coverage.

## Diagnostics

- 7B compiler skipped `106` wrong-recipient entries and `13` duplicates.
- 14B compiler skipped `131` wrong-recipient entries and `1` duplicate.
- Neither compiler skipped over-budget valid sources because the current packet budget equals the cost of all gold needed sources per role.

This means the present gain mostly comes from deterministic recipient validation and boundary execution. A tighter-budget packet is still needed to test true priority under scarcity.

## Commands

```powershell
python scripts\compile_perspectivegap_source_ledger_budget.py `
  --packet experiments\20260618-local-perspectivegap-source-perturbation-v0\source_perturbation_rotated20.jsonl `
  --predictions experiments\20260618-a8002-perspectivegap-source-ledger-rotated20-qwen25-14b\predictions.jsonl `
  --out experiments\20260618-a8002-perspectivegap-source-ledger-budget-compiled-rotated20\predictions_budget_compiled_qwen25_14b.jsonl
```

```powershell
python scripts\score_perspectivegap_hard_routing.py `
  --packet experiments\20260618-local-perspectivegap-source-perturbation-v0\source_perturbation_rotated20.jsonl `
  --predictions experiments\20260618-a8002-perspectivegap-source-ledger-budget-compiled-rotated20\predictions_budget_compiled_qwen25_14b.jsonl `
  --out experiments\20260618-a8002-perspectivegap-source-ledger-budget-compiled-rotated20\scores_budget_compiled_qwen25_14b.jsonl `
  --summary-out experiments\20260618-a8002-perspectivegap-source-ledger-budget-compiled-rotated20\summary_budget_compiled_qwen25_14b.md
```

## Next

Build a tight-budget source-ledger packet where oracle must choose a subset by priority, then compare model-only routing with deterministic budget compilation under real scarcity.
