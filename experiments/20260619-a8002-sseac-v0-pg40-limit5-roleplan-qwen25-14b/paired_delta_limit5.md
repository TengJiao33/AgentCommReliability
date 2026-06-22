# SSEAC Paired Delta Summary

- benchmark: `pg40`
- paired_rows: `5`
- structured_no_compiler_rows: `5`
- compiled_rows: `5`

| metric | structured_no_compiler | compiled | delta | improved | worsened | tied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| strict_pass | 0.0000 | 0.2000 | 0.2000 | 1 | 0 | 4 |
| required_coverage | 0.7714 | 0.6381 | -0.1333 | 0 | 3 | 2 |
| boundary_precision | 0.6533 | 0.7833 | 0.1300 | 4 | 0 | 1 |
| distractor_leakage | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 5 |
| budget_pass | 0.0000 | 1.0000 | 1.0000 | 5 | 0 | 0 |
| budget_overrun | 7.2000 | 0.0000 | -7.2000 | 0 | 5 | 0 |
| utility_ratio | 0.2745 | 0.7761 | 0.5017 | 5 | 0 | 0 |
| exact_target_role_rate | 0.3000 | 0.5000 | 0.2000 | 2 | 0 | 3 |
