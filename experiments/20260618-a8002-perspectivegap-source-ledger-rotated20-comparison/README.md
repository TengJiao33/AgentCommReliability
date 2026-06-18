# PerspectiveGap Source Ledger Rotated20 Comparison

## Purpose

Test whether explicit source/scope state can overcome content-driven routing when the same fragment texts are assigned to rotated recipient scopes.

## Main Table

| Condition | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Visibility acc | Reject recall | Needed rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| oracle | 40/40 | 1.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 |
| legacy_7b_on_rotated | 0/40 | 0.076 | 0.135 | 0.050 | 0.300 | 2.950 | 1.000 | 0.000 | 0.000 |
| source_ledger_7b | 0/40 | 0.574 | 0.745 | 0.300 | 0.350 | 4.650 | 0.700 | 1.000 | 0.025 |
| legacy_14b_on_rotated | 0/40 | 0.150 | 0.197 | 0.450 | 0.075 | 8.250 | 1.000 | 0.000 | 0.000 |
| source_ledger_14b | 3/40 | 0.854 | 0.779 | 0.075 | 0.225 | 13.150 | 0.761 | 1.000 | 0.000 |

## Diagnosis

The rotated packet breaks the content-routing shortcut: legacy role-list predictions collapse to `0.076` coverage for 7B and `0.150` for 14B. Explicit source ledger routing recovers much of the signal, especially for 14B.

The live failure has moved: source/scope following is viable, but budgeted delivery is not solved. The 14B source-ledger run has high coverage and perfect reject recall, yet only `0.225` budget pass.

## Artifacts

- `comparison_summary.md`
- `comparison_summary.json`
- `../20260618-a8002-perspectivegap-source-ledger-rotated20-qwen25-7b/`
- `../20260618-a8002-perspectivegap-source-ledger-rotated20-qwen25-14b/`
