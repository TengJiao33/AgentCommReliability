# PACT Public-State Field Packet Evaluation

- Prediction source: `outputs`
- Records: `500`
- Exact match: `0.536`
- Avg F1: `0.689`

## By Source Run

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 250 | 0.560 | 0.701 | 0.680 | 5 | 1 |
| final_contract | 250 | 0.512 | 0.677 | 0.800 | 1 | 4 |

## By Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| frozen_target_plus_evidence_no_final | 100 | 0.580 | 0.734 | n/a | 0 | 0 |
| public_target_plus_evidence_no_question_no_final | 100 | 0.440 | 0.591 | n/a | 0 | 0 |
| question_plus_evidence_no_target_no_final | 100 | 0.590 | 0.725 | n/a | 0 | 0 |
| question_plus_public_state_no_final | 100 | 0.520 | 0.688 | n/a | 0 | 0 |
| question_plus_public_state_with_final | 100 | 0.550 | 0.710 | 0.740 | 6 | 5 |

## By Source Run And Condition

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | frozen_target_plus_evidence_no_final | 50 | 0.600 | 0.738 | n/a | 0 | 0 |
| baseline | public_target_plus_evidence_no_question_no_final | 50 | 0.460 | 0.601 | n/a | 0 | 0 |
| baseline | question_plus_evidence_no_target_no_final | 50 | 0.580 | 0.717 | n/a | 0 | 0 |
| baseline | question_plus_public_state_no_final | 50 | 0.560 | 0.701 | n/a | 0 | 0 |
| baseline | question_plus_public_state_with_final | 50 | 0.600 | 0.750 | 0.680 | 5 | 1 |
| final_contract | frozen_target_plus_evidence_no_final | 50 | 0.560 | 0.730 | n/a | 0 | 0 |
| final_contract | public_target_plus_evidence_no_question_no_final | 50 | 0.420 | 0.580 | n/a | 0 | 0 |
| final_contract | question_plus_evidence_no_target_no_final | 50 | 0.600 | 0.733 | n/a | 0 | 0 |
| final_contract | question_plus_public_state_no_final | 50 | 0.480 | 0.674 | n/a | 0 | 0 |
| final_contract | question_plus_public_state_with_final | 50 | 0.500 | 0.671 | 0.800 | 1 | 4 |

## By Bridge Layer

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| diagnostic_noise | 10 | 0.100 | 0.110 | 0.000 | 0 | 0 |
| evidence_carriage | 50 | 0.040 | 0.132 | 0.800 | 0 | 0 |
| final_answer_commitment | 120 | 0.192 | 0.647 | 0.625 | 0 | 0 |
| positive_contract_rescue | 60 | 0.467 | 0.538 | 0.500 | 4 | 2 |
| stable_right_or_not_focus | 220 | 0.905 | 0.958 | 0.932 | 0 | 3 |
| target_contract | 20 | 0.250 | 0.250 | 0.750 | 0 | 0 |
| target_final_alignment | 20 | 0.500 | 0.560 | 0.250 | 2 | 0 |

## By Target Drift Candidate

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| False | 420 | 0.588 | 0.720 | 0.774 | 5 | 5 |
| True | 80 | 0.263 | 0.530 | 0.562 | 1 | 0 |
