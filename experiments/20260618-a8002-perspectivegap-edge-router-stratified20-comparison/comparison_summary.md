# PerspectiveGap Edge Router Stratified20 Comparison

| Condition | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Visibility acc | Reject recall | Needed rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy_7b | 0/40 | 0.443 | 0.786 | 0.050 | 0.625 | 1.275 | 1.000 | 0.000 | 0.000 |
| edge_7b | 0/40 | 0.331 | 0.613 | 0.200 | 0.575 | 4.050 | 0.760 | 0.550 | 1.900 |
| legacy_14b | 0/40 | 0.615 | 0.808 | 0.450 | 0.400 | 4.725 | 1.000 | 0.000 | 0.000 |
| edge_14b | 0/40 | 0.513 | 0.669 | 0.600 | 0.100 | 7.650 | 0.751 | 0.525 | 1.350 |

## Edge Router Diagnostics

- `edge_7b`: statuses={'ok': 40}, parse_error_rows=0, needed_reject_rows=28, over_budget_rows=17, distractor_leak_rows=7.
- `edge_14b`: statuses={'ok': 40}, parse_error_rows=0, needed_reject_rows=31, over_budget_rows=36, distractor_leak_rows=22.

## By Role Count

### edge_7b
| Roles | n | Coverage | Precision | Leak/eval | Budget pass | Visibility acc | Needed rejected |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 8 | 0.500 | 0.757 | 0.125 | 0.625 | 0.893 | 1.750 |
| 3 | 8 | 0.329 | 0.500 | 0.250 | 0.375 | 0.680 | 1.625 |
| 4 | 8 | 0.348 | 0.639 | 0.000 | 0.625 | 0.897 | 1.000 |
| 5 | 8 | 0.296 | 0.616 | 0.375 | 0.625 | 0.689 | 1.875 |
| 6 | 8 | 0.292 | 0.592 | 0.250 | 0.625 | 0.667 | 3.250 |

### edge_14b
| Roles | n | Coverage | Precision | Leak/eval | Budget pass | Visibility acc | Needed rejected |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 8 | 0.768 | 0.768 | 0.750 | 0.125 | 0.767 | 1.000 |
| 3 | 8 | 0.539 | 0.519 | 0.750 | 0.000 | 0.683 | 0.625 |
| 4 | 8 | 0.464 | 0.703 | 0.000 | 0.125 | 0.885 | 1.625 |
| 5 | 8 | 0.507 | 0.713 | 0.750 | 0.125 | 0.675 | 1.875 |
| 6 | 8 | 0.444 | 0.660 | 0.750 | 0.125 | 0.766 | 1.625 |

