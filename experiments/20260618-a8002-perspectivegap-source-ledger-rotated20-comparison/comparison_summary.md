# PerspectiveGap Source Ledger Rotated20 Comparison

| Condition | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Visibility acc | Reject recall | Needed rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| oracle | 40/40 | 1.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 1.000 | 0.000 |
| legacy_7b_on_rotated | 0/40 | 0.076 | 0.135 | 0.050 | 0.300 | 2.950 | 1.000 | 0.000 | 0.000 |
| source_ledger_7b | 0/40 | 0.574 | 0.745 | 0.300 | 0.350 | 4.650 | 0.700 | 1.000 | 0.025 |
| legacy_14b_on_rotated | 0/40 | 0.150 | 0.197 | 0.450 | 0.075 | 8.250 | 1.000 | 0.000 | 0.000 |
| source_ledger_14b | 3/40 | 0.854 | 0.779 | 0.075 | 0.225 | 13.150 | 0.761 | 1.000 | 0.000 |

## Source Ledger Diagnostics

- `source_ledger_7b`: statuses={'ok': 40}, parse_error_rows=0, strict_rows=0, needed_reject_rows=1, over_budget_rows=26, distractor_leak_rows=10.
- `source_ledger_14b`: statuses={'ok': 40}, parse_error_rows=0, strict_rows=3, needed_reject_rows=0, over_budget_rows=31, distractor_leak_rows=1.

## By Role Count

### source_ledger_7b
| Roles | n | Coverage | Precision | Leak/eval | Budget pass | Overrun | Visibility acc | Needed rejected |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 8 | 0.804 | 0.957 | 0.000 | 0.875 | 0.250 | 0.822 | 0.000 |
| 3 | 8 | 0.684 | 0.825 | 0.125 | 0.500 | 2.625 | 0.692 | 0.000 |
| 4 | 8 | 0.670 | 0.824 | 0.000 | 0.000 | 5.875 | 0.760 | 0.000 |
| 5 | 8 | 0.388 | 0.557 | 1.000 | 0.125 | 10.375 | 0.508 | 0.125 |
| 6 | 8 | 0.549 | 0.725 | 0.375 | 0.250 | 4.125 | 0.722 | 0.000 |

### source_ledger_14b
| Roles | n | Coverage | Precision | Leak/eval | Budget pass | Overrun | Visibility acc | Needed rejected |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 8 | 0.982 | 0.932 | 0.000 | 0.500 | 2.625 | 0.909 | 0.000 |
| 3 | 8 | 0.921 | 0.864 | 0.000 | 0.250 | 9.125 | 0.786 | 0.000 |
| 4 | 8 | 0.821 | 0.730 | 0.000 | 0.000 | 15.500 | 0.674 | 0.000 |
| 5 | 8 | 0.776 | 0.648 | 0.375 | 0.125 | 31.375 | 0.636 | 0.000 |
| 6 | 8 | 0.875 | 0.875 | 0.000 | 0.250 | 7.125 | 0.865 | 0.000 |

