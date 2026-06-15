# PACT Typed Boundary Split Audit

- Records: `240`

## By Comparison

| Comparison | Records | Outcomes | Avg F1 delta | Regression | Repair | Copy |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| no_candidate_vs_hidden | 40 | `{'both_right': 32, 'both_wrong': 8}` | 0.000 | 0.000 | 0.000 | 0.000 |
| no_candidate_vs_visible | 40 | `{'both_right': 22, 'both_wrong': 8, 'right_regression': 10}` | -0.206 | 0.312 | 0.000 | 0.275 |
| visible_vs_extract_first | 40 | `{'both_right': 22, 'both_wrong': 17, 'right_repair': 1}` | 0.029 | 0.000 | 0.056 | 0.225 |
| wrong_contract_no_candidate_vs_hidden | 40 | `{'both_right': 32, 'both_wrong': 8}` | 0.000 | 0.000 | 0.000 | 0.000 |
| wrong_contract_no_candidate_vs_visible | 40 | `{'both_right': 24, 'both_wrong': 8, 'right_regression': 8}` | -0.175 | 0.250 | 0.000 | 0.275 |
| wrong_contract_visible_vs_extract_first | 40 | `{'both_right': 24, 'both_wrong': 15, 'right_repair': 1}` | 0.029 | 0.000 | 0.062 | 0.250 |

## Positive Target-Focus Comparisons

| Comparison | Records | Outcomes | Avg F1 delta | Regression | Repair | Copy |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| no_candidate_vs_hidden | 32 | `{'both_right': 28, 'both_wrong': 4}` | 0.000 | 0.000 | 0.000 | 0.000 |
| no_candidate_vs_visible | 32 | `{'both_right': 20, 'both_wrong': 4, 'right_regression': 8}` | -0.195 | 0.286 | 0.000 | 0.250 |
| visible_vs_extract_first | 32 | `{'both_right': 20, 'both_wrong': 11, 'right_repair': 1}` | 0.034 | 0.000 | 0.083 | 0.188 |
| wrong_contract_no_candidate_vs_hidden | 32 | `{'both_right': 28, 'both_wrong': 4}` | 0.000 | 0.000 | 0.000 | 0.000 |
| wrong_contract_no_candidate_vs_visible | 32 | `{'both_right': 22, 'both_wrong': 4, 'right_regression': 6}` | -0.158 | 0.214 | 0.000 | 0.250 |
| wrong_contract_visible_vs_extract_first | 32 | `{'both_right': 22, 'both_wrong': 9, 'right_repair': 1}` | 0.036 | 0.000 | 0.100 | 0.219 |
