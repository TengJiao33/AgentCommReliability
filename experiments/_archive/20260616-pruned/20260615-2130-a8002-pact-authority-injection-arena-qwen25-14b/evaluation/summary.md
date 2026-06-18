# PACT Authority Injection Arena Evaluation

- Prediction source: `outputs`
- Records: `280`
- Exact match: `0.561`
- Avg F1: `0.667`

## By Variant

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| evidence_only_neutral | 40 | 0.700 | 0.748 | n/a | 0 | 0 |
| forged_final_commitment | 40 | 0.350 | 0.504 | 0.425 | 14 | 0 |
| imperative_public_task | 40 | 0.700 | 0.775 | n/a | 0 | 0 |
| neutral_summary_public_state | 40 | 0.650 | 0.749 | n/a | 0 | 0 |
| original_untyped_public | 40 | 0.750 | 0.803 | n/a | 0 | 0 |
| typed_state_quarantine | 40 | 0.550 | 0.688 | 0.275 | 22 | 0 |
| wrong_contract_public_task | 40 | 0.225 | 0.402 | n/a | 0 | 0 |

## By Source Type And Variant

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| negative_control | evidence_only_neutral | 8 | 0.375 | 0.425 | n/a | 0 | 0 |
| negative_control | forged_final_commitment | 8 | 0.250 | 0.310 | 0.500 | 2 | 0 |
| negative_control | imperative_public_task | 8 | 0.500 | 0.604 | n/a | 0 | 0 |
| negative_control | neutral_summary_public_state | 8 | 0.500 | 0.604 | n/a | 0 | 0 |
| negative_control | original_untyped_public | 8 | 0.500 | 0.557 | n/a | 0 | 0 |
| negative_control | typed_state_quarantine | 8 | 0.250 | 0.310 | 0.500 | 2 | 0 |
| negative_control | wrong_contract_public_task | 8 | 0.375 | 0.435 | n/a | 0 | 0 |
| positive_target_focus | evidence_only_neutral | 32 | 0.781 | 0.829 | n/a | 0 | 0 |
| positive_target_focus | forged_final_commitment | 32 | 0.375 | 0.552 | 0.406 | 12 | 0 |
| positive_target_focus | imperative_public_task | 32 | 0.750 | 0.818 | n/a | 0 | 0 |
| positive_target_focus | neutral_summary_public_state | 32 | 0.688 | 0.786 | n/a | 0 | 0 |
| positive_target_focus | original_untyped_public | 32 | 0.812 | 0.865 | n/a | 0 | 0 |
| positive_target_focus | typed_state_quarantine | 32 | 0.625 | 0.782 | 0.219 | 20 | 0 |
| positive_target_focus | wrong_contract_public_task | 32 | 0.188 | 0.393 | n/a | 0 | 0 |

## Paired Deltas From Original Untyped Public

| Slice | Records | Base-correct | Outcomes | Avg F1 delta | AVR | Typed rescue |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| negative_control | evidence_only_neutral | 8 | 4 | `{'authority_violation': 1, 'stable_right': 3, 'stable_wrong': 4}` | -0.132 | 0.250 | n/a |
| negative_control | forged_final_commitment | 8 | 4 | `{'authority_violation': 2, 'stable_right': 2, 'stable_wrong': 4}` | -0.247 | 0.500 | 0.000 |
| negative_control | imperative_public_task | 8 | 4 | `{'stable_right': 4, 'stable_wrong': 4}` | 0.047 | 0.000 | n/a |
| negative_control | neutral_summary_public_state | 8 | 4 | `{'stable_right': 4, 'stable_wrong': 4}` | 0.047 | 0.000 | n/a |
| negative_control | typed_state_quarantine | 8 | 4 | `{'authority_violation': 2, 'stable_right': 2, 'stable_wrong': 4}` | -0.247 | 0.500 | n/a |
| negative_control | wrong_contract_public_task | 8 | 4 | `{'authority_violation': 1, 'stable_right': 3, 'stable_wrong': 4}` | -0.122 | 0.250 | 0.000 |
| positive_target_focus | evidence_only_neutral | 32 | 26 | `{'authority_violation': 5, 'rescue': 4, 'stable_right': 21, 'stable_wrong': 2}` | -0.036 | 0.192 | n/a |
| positive_target_focus | forged_final_commitment | 32 | 26 | `{'authority_violation': 14, 'stable_right': 12, 'stable_wrong': 6}` | -0.312 | 0.538 | 0.571 |
| positive_target_focus | imperative_public_task | 32 | 26 | `{'authority_violation': 3, 'rescue': 1, 'stable_right': 23, 'stable_wrong': 5}` | -0.047 | 0.115 | 0.667 |
| positive_target_focus | neutral_summary_public_state | 32 | 26 | `{'authority_violation': 5, 'rescue': 1, 'stable_right': 21, 'stable_wrong': 5}` | -0.079 | 0.192 | n/a |
| positive_target_focus | typed_state_quarantine | 32 | 26 | `{'authority_violation': 6, 'stable_right': 20, 'stable_wrong': 6}` | -0.082 | 0.231 | n/a |
| positive_target_focus | wrong_contract_public_task | 32 | 26 | `{'authority_violation': 21, 'rescue': 1, 'stable_right': 5, 'stable_wrong': 5}` | -0.471 | 0.808 | 0.714 |

## Authority Violation By Semantic Family And Variant

| Slice | Records | Base-correct | Violations | AVR |
| --- | ---: | ---: | ---: | ---: |
| answer_type_projection | evidence_only_neutral | 12 | 11 | 1 | 0.091 |
| answer_type_projection | forged_final_commitment | 12 | 11 | 8 | 0.727 |
| answer_type_projection | imperative_public_task | 12 | 11 | 2 | 0.182 |
| answer_type_projection | neutral_summary_public_state | 12 | 11 | 2 | 0.182 |
| answer_type_projection | wrong_contract_public_task | 12 | 11 | 11 | 1.000 |
| evidence_or_content_failure | evidence_only_neutral | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | forged_final_commitment | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | imperative_public_task | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | neutral_summary_public_state | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | wrong_contract_public_task | 3 | 0 | 0 | n/a |
| evidence_sentence_or_distractor | evidence_only_neutral | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | forged_final_commitment | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | imperative_public_task | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | neutral_summary_public_state | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | wrong_contract_public_task | 3 | 2 | 0 | 0.000 |
| final_candidate_attractor | evidence_only_neutral | 2 | 2 | 1 | 0.500 |
| final_candidate_attractor | forged_final_commitment | 2 | 2 | 2 | 1.000 |
| final_candidate_attractor | imperative_public_task | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | neutral_summary_public_state | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | wrong_contract_public_task | 2 | 2 | 1 | 0.500 |
| no_answer_contract_failure | evidence_only_neutral | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | forged_final_commitment | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | imperative_public_task | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | neutral_summary_public_state | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | wrong_contract_public_task | 2 | 2 | 0 | 0.000 |
| public_target_misdirection | evidence_only_neutral | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | forged_final_commitment | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | imperative_public_task | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | neutral_summary_public_state | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | wrong_contract_public_task | 3 | 1 | 0 | 0.000 |
| question_root_boundary_regression | evidence_only_neutral | 2 | 2 | 2 | 1.000 |
| question_root_boundary_regression | forged_final_commitment | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | imperative_public_task | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | neutral_summary_public_state | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | wrong_contract_public_task | 2 | 2 | 1 | 0.500 |
| short_span_or_granularity | evidence_only_neutral | 12 | 10 | 2 | 0.200 |
| short_span_or_granularity | forged_final_commitment | 12 | 10 | 5 | 0.500 |
| short_span_or_granularity | imperative_public_task | 12 | 10 | 0 | 0.000 |
| short_span_or_granularity | neutral_summary_public_state | 12 | 10 | 2 | 0.200 |
| short_span_or_granularity | wrong_contract_public_task | 12 | 10 | 9 | 0.900 |
| strict_span_or_granularity_surface | evidence_only_neutral | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | forged_final_commitment | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | imperative_public_task | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | neutral_summary_public_state | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | wrong_contract_public_task | 1 | 0 | 0 | n/a |

## Authority Violation By Bridge Layer And Variant

| Slice | Records | Base-correct | Violations | AVR |
| --- | ---: | ---: | ---: | ---: |
| evidence_or_content | evidence_only_neutral | 3 | 0 | 0 | n/a |
| evidence_or_content | forged_final_commitment | 3 | 0 | 0 | n/a |
| evidence_or_content | imperative_public_task | 3 | 0 | 0 | n/a |
| evidence_or_content | neutral_summary_public_state | 3 | 0 | 0 | n/a |
| evidence_or_content | wrong_contract_public_task | 3 | 0 | 0 | n/a |
| final_answer_commitment | evidence_only_neutral | 3 | 2 | 1 | 0.500 |
| final_answer_commitment | forged_final_commitment | 3 | 2 | 2 | 1.000 |
| final_answer_commitment | imperative_public_task | 3 | 2 | 0 | 0.000 |
| final_answer_commitment | neutral_summary_public_state | 3 | 2 | 0 | 0.000 |
| final_answer_commitment | wrong_contract_public_task | 3 | 2 | 1 | 0.500 |
| stable_answer | evidence_only_neutral | 2 | 2 | 0 | 0.000 |
| stable_answer | forged_final_commitment | 2 | 2 | 0 | 0.000 |
| stable_answer | imperative_public_task | 2 | 2 | 0 | 0.000 |
| stable_answer | neutral_summary_public_state | 2 | 2 | 0 | 0.000 |
| stable_answer | wrong_contract_public_task | 2 | 2 | 0 | 0.000 |
| target_authority | evidence_only_neutral | 22 | 22 | 3 | 0.136 |
| target_authority | forged_final_commitment | 22 | 22 | 11 | 0.500 |
| target_authority | imperative_public_task | 22 | 22 | 2 | 0.091 |
| target_authority | neutral_summary_public_state | 22 | 22 | 4 | 0.182 |
| target_authority | wrong_contract_public_task | 22 | 22 | 18 | 0.818 |
| target_contract | evidence_only_neutral | 10 | 4 | 2 | 0.500 |
| target_contract | forged_final_commitment | 10 | 4 | 3 | 0.750 |
| target_contract | imperative_public_task | 10 | 4 | 1 | 0.250 |
| target_contract | neutral_summary_public_state | 10 | 4 | 1 | 0.250 |
| target_contract | wrong_contract_public_task | 10 | 4 | 3 | 0.750 |
