# PACT Public-State Field Packet Evaluation

- Prediction source: `outputs`
- Records: `500`
- Exact match: `0.452`
- Avg F1: `0.602`

## By Source Run

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 250 | 0.444 | 0.609 | 0.560 | 8 | 3 |
| final_contract | 250 | 0.460 | 0.596 | 0.840 | 0 | 4 |

## By Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| frozen_target_plus_evidence_no_final | 100 | 0.560 | 0.698 | n/a | 0 | 0 |
| public_target_plus_evidence_no_question_no_final | 100 | 0.300 | 0.481 | n/a | 0 | 0 |
| question_plus_evidence_no_target_no_final | 100 | 0.470 | 0.610 | n/a | 0 | 0 |
| question_plus_public_state_no_final | 100 | 0.500 | 0.648 | n/a | 0 | 0 |
| question_plus_public_state_with_final | 100 | 0.430 | 0.575 | 0.700 | 8 | 7 |

## By Source Run And Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | frozen_target_plus_evidence_no_final | 50 | 0.560 | 0.708 | n/a | 0 | 0 |
| baseline | public_target_plus_evidence_no_question_no_final | 50 | 0.280 | 0.474 | n/a | 0 | 0 |
| baseline | question_plus_evidence_no_target_no_final | 50 | 0.460 | 0.624 | n/a | 0 | 0 |
| baseline | question_plus_public_state_no_final | 50 | 0.500 | 0.658 | n/a | 0 | 0 |
| baseline | question_plus_public_state_with_final | 50 | 0.420 | 0.580 | 0.560 | 8 | 3 |
| final_contract | frozen_target_plus_evidence_no_final | 50 | 0.560 | 0.689 | n/a | 0 | 0 |
| final_contract | public_target_plus_evidence_no_question_no_final | 50 | 0.320 | 0.488 | n/a | 0 | 0 |
| final_contract | question_plus_evidence_no_target_no_final | 50 | 0.480 | 0.596 | n/a | 0 | 0 |
| final_contract | question_plus_public_state_no_final | 50 | 0.500 | 0.637 | n/a | 0 | 0 |
| final_contract | question_plus_public_state_with_final | 50 | 0.440 | 0.571 | 0.840 | 0 | 4 |

## By Bridge Layer

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stable_right_or_not_focus | 500 | 0.452 | 0.602 | 0.700 | 8 | 7 |

## By Target Drift Candidate

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| False | 440 | 0.505 | 0.621 | 0.705 | 7 | 7 |
| True | 60 | 0.067 | 0.465 | 0.667 | 1 | 0 |
