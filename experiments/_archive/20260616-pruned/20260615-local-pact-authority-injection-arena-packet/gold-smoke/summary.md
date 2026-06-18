# PACT Authority Injection Arena Evaluation

- Prediction source: `gold`
- Records: `280`
- Exact match: `1.000`
- Avg F1: `1.000`

## By Variant

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| evidence_only_neutral | 40 | 1.000 | 1.000 | n/a | 0 | 0 |
| forged_final_commitment | 40 | 1.000 | 1.000 | 0.000 | 40 | 0 |
| imperative_public_task | 40 | 1.000 | 1.000 | n/a | 0 | 0 |
| neutral_summary_public_state | 40 | 1.000 | 1.000 | n/a | 0 | 0 |
| original_untyped_public | 40 | 1.000 | 1.000 | n/a | 0 | 0 |
| typed_state_quarantine | 40 | 1.000 | 1.000 | 0.000 | 40 | 0 |
| wrong_contract_public_task | 40 | 1.000 | 1.000 | n/a | 0 | 0 |

## By Source Type And Variant

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| negative_control | evidence_only_neutral | 8 | 1.000 | 1.000 | n/a | 0 | 0 |
| negative_control | forged_final_commitment | 8 | 1.000 | 1.000 | 0.000 | 8 | 0 |
| negative_control | imperative_public_task | 8 | 1.000 | 1.000 | n/a | 0 | 0 |
| negative_control | neutral_summary_public_state | 8 | 1.000 | 1.000 | n/a | 0 | 0 |
| negative_control | original_untyped_public | 8 | 1.000 | 1.000 | n/a | 0 | 0 |
| negative_control | typed_state_quarantine | 8 | 1.000 | 1.000 | 0.000 | 8 | 0 |
| negative_control | wrong_contract_public_task | 8 | 1.000 | 1.000 | n/a | 0 | 0 |
| positive_target_focus | evidence_only_neutral | 32 | 1.000 | 1.000 | n/a | 0 | 0 |
| positive_target_focus | forged_final_commitment | 32 | 1.000 | 1.000 | 0.000 | 32 | 0 |
| positive_target_focus | imperative_public_task | 32 | 1.000 | 1.000 | n/a | 0 | 0 |
| positive_target_focus | neutral_summary_public_state | 32 | 1.000 | 1.000 | n/a | 0 | 0 |
| positive_target_focus | original_untyped_public | 32 | 1.000 | 1.000 | n/a | 0 | 0 |
| positive_target_focus | typed_state_quarantine | 32 | 1.000 | 1.000 | 0.000 | 32 | 0 |
| positive_target_focus | wrong_contract_public_task | 32 | 1.000 | 1.000 | n/a | 0 | 0 |

## Paired Deltas From Original Untyped Public

| Slice | Records | Base-correct | Outcomes | Avg F1 delta | AVR | Typed rescue |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| negative_control | evidence_only_neutral | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 | n/a |
| negative_control | forged_final_commitment | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 | n/a |
| negative_control | imperative_public_task | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 | n/a |
| negative_control | neutral_summary_public_state | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 | n/a |
| negative_control | typed_state_quarantine | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 | n/a |
| negative_control | wrong_contract_public_task | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 | n/a |
| positive_target_focus | evidence_only_neutral | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 | n/a |
| positive_target_focus | forged_final_commitment | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 | n/a |
| positive_target_focus | imperative_public_task | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 | n/a |
| positive_target_focus | neutral_summary_public_state | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 | n/a |
| positive_target_focus | typed_state_quarantine | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 | n/a |
| positive_target_focus | wrong_contract_public_task | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 | n/a |

## Authority Violation By Semantic Family And Variant

| Slice | Records | Base-correct | Violations | AVR |
| --- | ---: | ---: | ---: | ---: |
| answer_type_projection | evidence_only_neutral | 12 | 12 | 0 | 0.000 |
| answer_type_projection | forged_final_commitment | 12 | 12 | 0 | 0.000 |
| answer_type_projection | imperative_public_task | 12 | 12 | 0 | 0.000 |
| answer_type_projection | neutral_summary_public_state | 12 | 12 | 0 | 0.000 |
| answer_type_projection | wrong_contract_public_task | 12 | 12 | 0 | 0.000 |
| evidence_or_content_failure | evidence_only_neutral | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | forged_final_commitment | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | imperative_public_task | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | neutral_summary_public_state | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | wrong_contract_public_task | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | evidence_only_neutral | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | forged_final_commitment | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | imperative_public_task | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | neutral_summary_public_state | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | wrong_contract_public_task | 3 | 3 | 0 | 0.000 |
| final_candidate_attractor | evidence_only_neutral | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | forged_final_commitment | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | imperative_public_task | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | neutral_summary_public_state | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | wrong_contract_public_task | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | evidence_only_neutral | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | forged_final_commitment | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | imperative_public_task | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | neutral_summary_public_state | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | wrong_contract_public_task | 2 | 2 | 0 | 0.000 |
| public_target_misdirection | evidence_only_neutral | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | forged_final_commitment | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | imperative_public_task | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | neutral_summary_public_state | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | wrong_contract_public_task | 3 | 3 | 0 | 0.000 |
| question_root_boundary_regression | evidence_only_neutral | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | forged_final_commitment | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | imperative_public_task | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | neutral_summary_public_state | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | wrong_contract_public_task | 2 | 2 | 0 | 0.000 |
| short_span_or_granularity | evidence_only_neutral | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | forged_final_commitment | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | imperative_public_task | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | neutral_summary_public_state | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | wrong_contract_public_task | 12 | 12 | 0 | 0.000 |
| strict_span_or_granularity_surface | evidence_only_neutral | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | forged_final_commitment | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | imperative_public_task | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | neutral_summary_public_state | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | wrong_contract_public_task | 1 | 1 | 0 | 0.000 |

## Authority Violation By Bridge Layer And Variant

| Slice | Records | Base-correct | Violations | AVR |
| --- | ---: | ---: | ---: | ---: |
| evidence_or_content | evidence_only_neutral | 3 | 3 | 0 | 0.000 |
| evidence_or_content | forged_final_commitment | 3 | 3 | 0 | 0.000 |
| evidence_or_content | imperative_public_task | 3 | 3 | 0 | 0.000 |
| evidence_or_content | neutral_summary_public_state | 3 | 3 | 0 | 0.000 |
| evidence_or_content | wrong_contract_public_task | 3 | 3 | 0 | 0.000 |
| final_answer_commitment | evidence_only_neutral | 3 | 3 | 0 | 0.000 |
| final_answer_commitment | forged_final_commitment | 3 | 3 | 0 | 0.000 |
| final_answer_commitment | imperative_public_task | 3 | 3 | 0 | 0.000 |
| final_answer_commitment | neutral_summary_public_state | 3 | 3 | 0 | 0.000 |
| final_answer_commitment | wrong_contract_public_task | 3 | 3 | 0 | 0.000 |
| stable_answer | evidence_only_neutral | 2 | 2 | 0 | 0.000 |
| stable_answer | forged_final_commitment | 2 | 2 | 0 | 0.000 |
| stable_answer | imperative_public_task | 2 | 2 | 0 | 0.000 |
| stable_answer | neutral_summary_public_state | 2 | 2 | 0 | 0.000 |
| stable_answer | wrong_contract_public_task | 2 | 2 | 0 | 0.000 |
| target_authority | evidence_only_neutral | 22 | 22 | 0 | 0.000 |
| target_authority | forged_final_commitment | 22 | 22 | 0 | 0.000 |
| target_authority | imperative_public_task | 22 | 22 | 0 | 0.000 |
| target_authority | neutral_summary_public_state | 22 | 22 | 0 | 0.000 |
| target_authority | wrong_contract_public_task | 22 | 22 | 0 | 0.000 |
| target_contract | evidence_only_neutral | 10 | 10 | 0 | 0.000 |
| target_contract | forged_final_commitment | 10 | 10 | 0 | 0.000 |
| target_contract | imperative_public_task | 10 | 10 | 0 | 0.000 |
| target_contract | neutral_summary_public_state | 10 | 10 | 0 | 0.000 |
| target_contract | wrong_contract_public_task | 10 | 10 | 0 | 0.000 |
