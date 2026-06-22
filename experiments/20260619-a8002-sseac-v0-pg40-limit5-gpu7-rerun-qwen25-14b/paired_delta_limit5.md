# SSEAC Paired Delta Summary

- benchmark: `pg40`
- paired_rows: `5`
- structured_no_compiler_rows: `5`
- compiled_rows: `5`

| metric | structured_no_compiler | compiled | delta | improved | worsened | tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| strict_pass | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 5 |
| required_coverage | 0.7881 | 0.4167 | -0.3714 | 0 | 3 | 2 |
| boundary_precision | 0.6533 | 0.6833 | 0.0300 | 3 | 1 | 1 |
| distractor_leakage | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 5 |
| budget_pass | 0.0000 | 1.0000 | 1.0000 | 5 | 0 | 0 |
| budget_overrun | 8.6000 | 0.0000 | -8.6000 | 0 | 5 | 0 |
| utility_ratio | 0.1932 | 0.5345 | 0.3412 | 3 | 0 | 2 |
| exact_target_role_rate | 0.2333 | 0.3333 | 0.1000 | 1 | 0 | 4 |
