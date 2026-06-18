# PACT Public-State Field Packet Evaluation

- Prediction source: `official_final_answer`
- Records: `500`
- Exact match: `0.470`
- Avg F1: `0.641`

## By Source Run

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| compact_final_contract | 250 | 0.440 | 0.604 | 0.940 | 0 | 0 |
| final_contract | 250 | 0.500 | 0.678 | 1.000 | 0 | 0 |

## By Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| frozen_target_plus_evidence_no_final | 100 | 0.470 | 0.641 | n/a | 0 | 0 |
| public_target_plus_evidence_no_question_no_final | 100 | 0.470 | 0.641 | n/a | 0 | 0 |
| question_plus_evidence_no_target_no_final | 100 | 0.470 | 0.641 | n/a | 0 | 0 |
| question_plus_public_state_no_final | 100 | 0.470 | 0.641 | n/a | 0 | 0 |
| question_plus_public_state_with_final | 100 | 0.470 | 0.641 | 0.970 | 0 | 0 |

## By Source Run And Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| compact_final_contract | frozen_target_plus_evidence_no_final | 50 | 0.440 | 0.604 | n/a | 0 | 0 |
| compact_final_contract | public_target_plus_evidence_no_question_no_final | 50 | 0.440 | 0.604 | n/a | 0 | 0 |
| compact_final_contract | question_plus_evidence_no_target_no_final | 50 | 0.440 | 0.604 | n/a | 0 | 0 |
| compact_final_contract | question_plus_public_state_no_final | 50 | 0.440 | 0.604 | n/a | 0 | 0 |
| compact_final_contract | question_plus_public_state_with_final | 50 | 0.440 | 0.604 | 0.940 | 0 | 0 |
| final_contract | frozen_target_plus_evidence_no_final | 50 | 0.500 | 0.678 | n/a | 0 | 0 |
| final_contract | public_target_plus_evidence_no_question_no_final | 50 | 0.500 | 0.678 | n/a | 0 | 0 |
| final_contract | question_plus_evidence_no_target_no_final | 50 | 0.500 | 0.678 | n/a | 0 | 0 |
| final_contract | question_plus_public_state_no_final | 50 | 0.500 | 0.678 | n/a | 0 | 0 |
| final_contract | question_plus_public_state_with_final | 50 | 0.500 | 0.678 | 1.000 | 0 | 0 |

## By Bridge Layer

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stable_right_or_not_focus | 500 | 0.470 | 0.641 | 0.970 | 0 | 0 |

## By Target Drift Candidate

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| False | 410 | 0.573 | 0.679 | 0.963 | 0 | 0 |
| True | 90 | 0.000 | 0.467 | 1.000 | 0 | 0 |
