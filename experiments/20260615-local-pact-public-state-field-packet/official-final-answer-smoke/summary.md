# PACT Public-State Field Packet Evaluation

- Prediction source: `official_final_answer`
- Records: `500`
- Exact match: `0.540`
- Avg F1: `0.695`

## By Source Run

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 250 | 0.520 | 0.647 | 1.000 | 0 | 0 |
| final_contract | 250 | 0.560 | 0.743 | 1.000 | 0 | 0 |

## By Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| frozen_target_plus_evidence_no_final | 100 | 0.540 | 0.695 | n/a | 0 | 0 |
| public_target_plus_evidence_no_question_no_final | 100 | 0.540 | 0.695 | n/a | 0 | 0 |
| question_plus_evidence_no_target_no_final | 100 | 0.540 | 0.695 | n/a | 0 | 0 |
| question_plus_public_state_no_final | 100 | 0.540 | 0.695 | n/a | 0 | 0 |
| question_plus_public_state_with_final | 100 | 0.540 | 0.695 | 1.000 | 0 | 0 |

## By Source Run And Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | frozen_target_plus_evidence_no_final | 50 | 0.520 | 0.647 | n/a | 0 | 0 |
| baseline | public_target_plus_evidence_no_question_no_final | 50 | 0.520 | 0.647 | n/a | 0 | 0 |
| baseline | question_plus_evidence_no_target_no_final | 50 | 0.520 | 0.647 | n/a | 0 | 0 |
| baseline | question_plus_public_state_no_final | 50 | 0.520 | 0.647 | n/a | 0 | 0 |
| baseline | question_plus_public_state_with_final | 50 | 0.520 | 0.647 | 1.000 | 0 | 0 |
| final_contract | frozen_target_plus_evidence_no_final | 50 | 0.560 | 0.743 | n/a | 0 | 0 |
| final_contract | public_target_plus_evidence_no_question_no_final | 50 | 0.560 | 0.743 | n/a | 0 | 0 |
| final_contract | question_plus_evidence_no_target_no_final | 50 | 0.560 | 0.743 | n/a | 0 | 0 |
| final_contract | question_plus_public_state_no_final | 50 | 0.560 | 0.743 | n/a | 0 | 0 |
| final_contract | question_plus_public_state_with_final | 50 | 0.560 | 0.743 | 1.000 | 0 | 0 |

## By Bridge Layer

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| diagnostic_noise | 10 | 0.000 | 0.000 | 1.000 | 0 | 0 |
| evidence_carriage | 50 | 0.000 | 0.133 | 1.000 | 0 | 0 |
| final_answer_commitment | 120 | 0.125 | 0.642 | 1.000 | 0 | 0 |
| positive_contract_rescue | 60 | 0.500 | 0.604 | 1.000 | 0 | 0 |
| stable_right_or_not_focus | 220 | 1.000 | 1.000 | 1.000 | 0 | 0 |
| target_contract | 20 | 0.250 | 0.250 | 1.000 | 0 | 0 |
| target_final_alignment | 20 | 0.000 | 0.119 | 1.000 | 0 | 0 |

## By Target Drift Candidate

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| False | 420 | 0.619 | 0.733 | 1.000 | 0 | 0 |
| True | 80 | 0.125 | 0.492 | 1.000 | 0 | 0 |
