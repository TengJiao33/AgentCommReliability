# PACT Public-State Field Packet Evaluation

- Prediction source: `outputs`
- Records: `100`
- Exact match: `0.610`
- Avg F1: `0.753`

## By Source Run

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 50 | 0.600 | 0.728 | n/a | 0 | 0 |
| final_contract | 50 | 0.620 | 0.778 | n/a | 0 | 0 |

## By Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| verified_quarantine_risky_else_frozen_no_final | 100 | 0.610 | 0.753 | n/a | 0 | 0 |

## By Source Run And Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | verified_quarantine_risky_else_frozen_no_final | 50 | 0.600 | 0.728 | n/a | 0 | 0 |
| final_contract | verified_quarantine_risky_else_frozen_no_final | 50 | 0.620 | 0.778 | n/a | 0 | 0 |

## By Bridge Layer

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| diagnostic_noise | 2 | 0.000 | 0.000 | n/a | 0 | 0 |
| evidence_carriage | 10 | 0.200 | 0.200 | n/a | 0 | 0 |
| final_answer_commitment | 24 | 0.333 | 0.731 | n/a | 0 | 0 |
| positive_contract_rescue | 12 | 0.583 | 0.699 | n/a | 0 | 0 |
| stable_right_or_not_focus | 44 | 0.932 | 0.986 | n/a | 0 | 0 |
| target_contract | 4 | 0.250 | 0.250 | n/a | 0 | 0 |
| target_final_alignment | 4 | 0.500 | 0.744 | n/a | 0 | 0 |

## By Target Drift Candidate

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| False | 84 | 0.643 | 0.767 | n/a | 0 | 0 |
| True | 16 | 0.438 | 0.682 | n/a | 0 | 0 |
