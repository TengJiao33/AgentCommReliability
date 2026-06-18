# PerspectiveGap Budget-Compiled Source Ledger Rotated20

| Condition | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Visibility acc | Reject recall | Needed rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy_7b_on_rotated | 0/40 | 0.076 | 0.135 | 0.050 | 0.300 | 2.950 | 1.000 | 0.000 | 0.000 |
| source_ledger_7b_raw | 0/40 | 0.574 | 0.745 | 0.300 | 0.350 | 4.650 | 0.700 | 1.000 | 0.025 |
| source_ledger_7b_budget_compiled | 0/40 | 0.574 | 1.000 | 0.000 | 1.000 | 0.000 | 0.819 | 1.000 | 0.000 |
| legacy_14b_on_rotated | 0/40 | 0.150 | 0.197 | 0.450 | 0.075 | 8.250 | 1.000 | 0.000 | 0.000 |
| source_ledger_14b_raw | 3/40 | 0.854 | 0.779 | 0.075 | 0.225 | 13.150 | 0.761 | 1.000 | 0.000 |
| source_ledger_14b_budget_compiled | 12/40 | 0.854 | 1.000 | 0.000 | 1.000 | 0.000 | 0.952 | 1.000 | 0.000 |

## Budget Compiler Diagnostics

- `source_ledger_7b_budget_compiled`: statuses={'ok': 40}, strict_rows=0, parse_error_rows=0, skipped={'wrong_recipient': 106, 'over_budget': 0, 'invalid': 0, 'duplicate': 13}.
- `source_ledger_14b_budget_compiled`: statuses={'ok': 40}, strict_rows=12, parse_error_rows=0, skipped={'wrong_recipient': 131, 'over_budget': 0, 'invalid': 0, 'duplicate': 1}.

## By Role Count

### source_ledger_7b_budget_compiled
| Roles | n | Strict | Coverage | Precision | Budget pass | Visibility acc |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 8 | 0 | 0.804 | 1.000 | 1.000 | 0.844 |
| 3 | 8 | 0 | 0.684 | 1.000 | 1.000 | 0.750 |
| 4 | 8 | 0 | 0.670 | 1.000 | 1.000 | 0.880 |
| 5 | 8 | 0 | 0.388 | 1.000 | 1.000 | 0.695 |
| 6 | 8 | 0 | 0.549 | 1.000 | 1.000 | 0.886 |

### source_ledger_14b_budget_compiled
| Roles | n | Strict | Coverage | Precision | Budget pass | Visibility acc |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 8 | 7 | 0.982 | 1.000 | 1.000 | 0.982 |
| 3 | 8 | 3 | 0.921 | 1.000 | 1.000 | 0.929 |
| 4 | 8 | 0 | 0.821 | 1.000 | 1.000 | 0.967 |
| 5 | 8 | 1 | 0.776 | 1.000 | 1.000 | 0.924 |
| 6 | 8 | 1 | 0.875 | 1.000 | 1.000 | 0.968 |

