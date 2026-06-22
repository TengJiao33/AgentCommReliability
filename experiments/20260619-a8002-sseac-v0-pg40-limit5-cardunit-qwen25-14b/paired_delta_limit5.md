# SSEAC Paired Delta Summary

- benchmark: `pg40`
- paired_rows: `5`
- structured_no_compiler_rows: `5`
- compiled_rows: `5`

| metric | structured_no_compiler | compiled | delta | improved | worsened | tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| strict_pass | 0.0000 | 0.2000 | 0.2000 | 1 | 0 | 4 |
| required_coverage | 0.8167 | 0.6500 | -0.1667 | 0 | 2 | 3 |
| boundary_precision | 0.6600 | 0.8167 | 0.1567 | 3 | 0 | 2 |
| distractor_leakage | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 5 |
| budget_pass | 0.0000 | 1.0000 | 1.0000 | 5 | 0 | 0 |
| budget_overrun | 8.8000 | 0.0000 | -8.8000 | 0 | 5 | 0 |
| utility_ratio | 0.1932 | 0.8051 | 0.6118 | 5 | 0 | 0 |
| exact_target_role_rate | 0.2333 | 0.6000 | 0.3667 | 3 | 0 | 2 |
