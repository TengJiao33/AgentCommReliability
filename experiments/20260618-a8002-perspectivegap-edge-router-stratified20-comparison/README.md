# PerspectiveGap Edge Router Stratified20 Comparison

## Purpose

Compare legacy role-list routing with the new edge-router plus symbolic scope compiler on the same `40` stratified20 hard-routing rows.

## Main Table

| Condition | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Visibility acc | Reject recall | Needed rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy_7b | 0/40 | 0.443 | 0.786 | 0.050 | 0.625 | 1.275 | 1.000 | 0.000 | 0.000 |
| edge_7b | 0/40 | 0.331 | 0.613 | 0.200 | 0.575 | 4.050 | 0.760 | 0.550 | 1.900 |
| legacy_14b | 0/40 | 0.615 | 0.808 | 0.450 | 0.400 | 4.725 | 1.000 | 0.000 | 0.000 |
| edge_14b | 0/40 | 0.513 | 0.669 | 0.600 | 0.100 | 7.650 | 0.751 | 0.525 | 1.350 |

`legacy_*` source and visibility fields are auto-filled upper-bound diagnostics from old role-list outputs. `edge_*` source and visibility fields are compiled from model-selected edges, so they test whether symbolic bookkeeping helps once the model chooses recipient sets.

## Diagnosis

The compiler removes the worst direct hard-card visibility-output problem, but the hard edge-router prompt damages edge selection. Both 7B and 14B edge-router runs have `0` parse errors, so the degradation is not a JSON plumbing artifact.

The 14B model is more aggressive: coverage rises over 7B, while budget pass and distractor leakage get worse. This keeps the coverage/boundary tradeoff alive as a phenomenon, but the current edge-router protocol is not a candidate method.

## Artifacts

- `comparison_summary.md`
- `comparison_summary.json`
- `../20260618-a8002-perspectivegap-edge-router-stratified20-qwen25-7b/`
- `../20260618-a8002-perspectivegap-edge-router-stratified20-qwen25-14b/`
