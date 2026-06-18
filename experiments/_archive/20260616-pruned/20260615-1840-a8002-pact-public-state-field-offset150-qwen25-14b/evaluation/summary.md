# PACT Public-State Field Packet Evaluation

- Prediction source: `outputs`
- Records: `500`
- Exact match: `0.418`
- Avg F1: `0.593`

## By Source Run

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| compact_final_contract | 250 | 0.436 | 0.606 | 0.860 | 2 | 1 |
| final_contract | 250 | 0.400 | 0.580 | 0.740 | 1 | 6 |

## By Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| frozen_target_plus_evidence_no_final | 100 | 0.480 | 0.657 | n/a | 0 | 0 |
| public_target_plus_evidence_no_question_no_final | 100 | 0.310 | 0.495 | n/a | 0 | 0 |
| question_plus_evidence_no_target_no_final | 100 | 0.450 | 0.623 | n/a | 0 | 0 |
| question_plus_public_state_no_final | 100 | 0.420 | 0.593 | n/a | 0 | 0 |
| question_plus_public_state_with_final | 100 | 0.430 | 0.599 | 0.800 | 3 | 7 |

## By Source Run And Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| compact_final_contract | frozen_target_plus_evidence_no_final | 50 | 0.500 | 0.660 | n/a | 0 | 0 |
| compact_final_contract | public_target_plus_evidence_no_question_no_final | 50 | 0.340 | 0.518 | n/a | 0 | 0 |
| compact_final_contract | question_plus_evidence_no_target_no_final | 50 | 0.460 | 0.633 | n/a | 0 | 0 |
| compact_final_contract | question_plus_public_state_no_final | 50 | 0.420 | 0.603 | n/a | 0 | 0 |
| compact_final_contract | question_plus_public_state_with_final | 50 | 0.460 | 0.617 | 0.860 | 2 | 1 |
| final_contract | frozen_target_plus_evidence_no_final | 50 | 0.460 | 0.653 | n/a | 0 | 0 |
| final_contract | public_target_plus_evidence_no_question_no_final | 50 | 0.280 | 0.472 | n/a | 0 | 0 |
| final_contract | question_plus_evidence_no_target_no_final | 50 | 0.440 | 0.613 | n/a | 0 | 0 |
| final_contract | question_plus_public_state_no_final | 50 | 0.420 | 0.582 | n/a | 0 | 0 |
| final_contract | question_plus_public_state_with_final | 50 | 0.400 | 0.580 | 0.740 | 1 | 6 |

## By Bridge Layer

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stable_right_or_not_focus | 500 | 0.418 | 0.593 | 0.800 | 3 | 7 |

## By Target Drift Candidate

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| False | 410 | 0.500 | 0.626 | 0.768 | 3 | 7 |
| True | 90 | 0.044 | 0.444 | 0.944 | 0 | 0 |
