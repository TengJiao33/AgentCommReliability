# PACT Public-State Field Packet Evaluation

- Prediction source: `outputs`
- Records: `200`
- Exact match: `0.475`
- Avg F1: `0.633`

## By Source Run

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 100 | 0.480 | 0.644 | n/a | 0 | 0 |
| final_contract | 100 | 0.470 | 0.621 | n/a | 0 | 0 |

## By Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| security_projection_question_root_no_final | 100 | 0.510 | 0.661 | n/a | 0 | 0 |
| standalone_authority_quarantine_no_final | 100 | 0.440 | 0.604 | n/a | 0 | 0 |

## By Source Run And Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | security_projection_question_root_no_final | 50 | 0.520 | 0.678 | n/a | 0 | 0 |
| baseline | standalone_authority_quarantine_no_final | 50 | 0.440 | 0.610 | n/a | 0 | 0 |
| final_contract | security_projection_question_root_no_final | 50 | 0.500 | 0.644 | n/a | 0 | 0 |
| final_contract | standalone_authority_quarantine_no_final | 50 | 0.440 | 0.598 | n/a | 0 | 0 |

## By Bridge Layer

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stable_right_or_not_focus | 200 | 0.475 | 0.633 | n/a | 0 | 0 |

## By Target Drift Candidate

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| False | 176 | 0.517 | 0.649 | n/a | 0 | 0 |
| True | 24 | 0.167 | 0.511 | n/a | 0 | 0 |
