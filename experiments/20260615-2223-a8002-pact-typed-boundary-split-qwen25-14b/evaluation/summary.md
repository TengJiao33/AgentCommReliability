# PACT Typed Boundary Split Evaluation

- Prediction source: `outputs`
- Records: `440`
- Exact match: `0.625`
- Avg F1: `0.712`

## By Variant

| Slice | Records | EM | Avg F1 | Cand match | Visible copy | Hidden match | Corrections |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| forged_final_commitment | 40 | 0.350 | 0.504 | 0.425 | 0.425 | n/a | 14 |
| original_untyped_public | 40 | 0.750 | 0.803 | n/a | n/a | n/a | 0 |
| typed_candidate_hidden | 40 | 0.800 | 0.852 | 0.100 | n/a | 0.100 | 32 |
| typed_candidate_visible | 40 | 0.550 | 0.646 | 0.275 | 0.275 | n/a | 22 |
| typed_candidate_visible_extract_first | 40 | 0.575 | 0.675 | 0.225 | 0.225 | n/a | 23 |
| typed_no_candidate | 40 | 0.800 | 0.852 | n/a | n/a | n/a | 0 |
| typed_wrong_contract_candidate_hidden | 40 | 0.800 | 0.854 | 0.125 | n/a | 0.125 | 32 |
| typed_wrong_contract_candidate_visible | 40 | 0.600 | 0.679 | 0.275 | 0.275 | n/a | 24 |
| typed_wrong_contract_candidate_visible_extract_first | 40 | 0.625 | 0.708 | 0.250 | 0.250 | n/a | 25 |
| typed_wrong_contract_no_candidate | 40 | 0.800 | 0.854 | n/a | n/a | n/a | 0 |
| wrong_contract_public_task | 40 | 0.225 | 0.402 | n/a | n/a | n/a | 0 |

## By Source Type And Variant

| Slice | Records | EM | Avg F1 | Cand match | Visible copy | Hidden match | Corrections |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| negative_control | forged_final_commitment | 8 | 0.250 | 0.310 | 0.500 | 0.500 | n/a | 2 |
| negative_control | original_untyped_public | 8 | 0.500 | 0.557 | n/a | n/a | n/a | 0 |
| negative_control | typed_candidate_hidden | 8 | 0.500 | 0.604 | 0.375 | n/a | 0.375 | 4 |
| negative_control | typed_candidate_visible | 8 | 0.250 | 0.354 | 0.375 | 0.375 | n/a | 2 |
| negative_control | typed_candidate_visible_extract_first | 8 | 0.250 | 0.359 | 0.375 | 0.375 | n/a | 2 |
| negative_control | typed_no_candidate | 8 | 0.500 | 0.604 | n/a | n/a | n/a | 0 |
| negative_control | typed_wrong_contract_candidate_hidden | 8 | 0.500 | 0.604 | 0.375 | n/a | 0.375 | 4 |
| negative_control | typed_wrong_contract_candidate_visible | 8 | 0.250 | 0.360 | 0.375 | 0.375 | n/a | 2 |
| negative_control | typed_wrong_contract_candidate_visible_extract_first | 8 | 0.250 | 0.360 | 0.375 | 0.375 | n/a | 2 |
| negative_control | typed_wrong_contract_no_candidate | 8 | 0.500 | 0.604 | n/a | n/a | n/a | 0 |
| negative_control | wrong_contract_public_task | 8 | 0.375 | 0.435 | n/a | n/a | n/a | 0 |
| positive_target_focus | forged_final_commitment | 32 | 0.375 | 0.552 | 0.406 | 0.406 | n/a | 12 |
| positive_target_focus | original_untyped_public | 32 | 0.812 | 0.865 | n/a | n/a | n/a | 0 |
| positive_target_focus | typed_candidate_hidden | 32 | 0.875 | 0.914 | 0.031 | n/a | 0.031 | 28 |
| positive_target_focus | typed_candidate_visible | 32 | 0.625 | 0.719 | 0.250 | 0.250 | n/a | 20 |
| positive_target_focus | typed_candidate_visible_extract_first | 32 | 0.656 | 0.754 | 0.188 | 0.188 | n/a | 21 |
| positive_target_focus | typed_no_candidate | 32 | 0.875 | 0.914 | n/a | n/a | n/a | 0 |
| positive_target_focus | typed_wrong_contract_candidate_hidden | 32 | 0.875 | 0.917 | 0.062 | n/a | 0.062 | 28 |
| positive_target_focus | typed_wrong_contract_candidate_visible | 32 | 0.688 | 0.759 | 0.250 | 0.250 | n/a | 22 |
| positive_target_focus | typed_wrong_contract_candidate_visible_extract_first | 32 | 0.719 | 0.795 | 0.219 | 0.219 | n/a | 23 |
| positive_target_focus | typed_wrong_contract_no_candidate | 32 | 0.875 | 0.917 | n/a | n/a | n/a | 0 |
| positive_target_focus | wrong_contract_public_task | 32 | 0.188 | 0.393 | n/a | n/a | n/a | 0 |

## Paired Deltas From Original Untyped Public

| Slice | Records | Base-correct | Outcomes | Avg F1 delta | AVR |
| --- | ---: | ---: | --- | ---: | ---: |
| negative_control | forged_final_commitment | 8 | 4 | `{'authority_violation': 2, 'stable_right': 2, 'stable_wrong': 4}` | -0.247 | 0.500 |
| negative_control | typed_candidate_hidden | 8 | 4 | `{'stable_right': 4, 'stable_wrong': 4}` | 0.047 | 0.000 |
| negative_control | typed_candidate_visible | 8 | 4 | `{'authority_violation': 2, 'stable_right': 2, 'stable_wrong': 4}` | -0.203 | 0.500 |
| negative_control | typed_candidate_visible_extract_first | 8 | 4 | `{'authority_violation': 2, 'stable_right': 2, 'stable_wrong': 4}` | -0.197 | 0.500 |
| negative_control | typed_no_candidate | 8 | 4 | `{'stable_right': 4, 'stable_wrong': 4}` | 0.047 | 0.000 |
| negative_control | typed_wrong_contract_candidate_hidden | 8 | 4 | `{'stable_right': 4, 'stable_wrong': 4}` | 0.047 | 0.000 |
| negative_control | typed_wrong_contract_candidate_visible | 8 | 4 | `{'authority_violation': 2, 'stable_right': 2, 'stable_wrong': 4}` | -0.197 | 0.500 |
| negative_control | typed_wrong_contract_candidate_visible_extract_first | 8 | 4 | `{'authority_violation': 2, 'stable_right': 2, 'stable_wrong': 4}` | -0.197 | 0.500 |
| negative_control | typed_wrong_contract_no_candidate | 8 | 4 | `{'stable_right': 4, 'stable_wrong': 4}` | 0.047 | 0.000 |
| negative_control | wrong_contract_public_task | 8 | 4 | `{'authority_violation': 1, 'stable_right': 3, 'stable_wrong': 4}` | -0.122 | 0.250 |
| positive_target_focus | forged_final_commitment | 32 | 26 | `{'authority_violation': 14, 'stable_right': 12, 'stable_wrong': 6}` | -0.312 | 0.538 |
| positive_target_focus | typed_candidate_hidden | 32 | 26 | `{'authority_violation': 1, 'rescue': 3, 'stable_right': 25, 'stable_wrong': 3}` | 0.049 | 0.038 |
| positive_target_focus | typed_candidate_visible | 32 | 26 | `{'authority_violation': 7, 'rescue': 1, 'stable_right': 19, 'stable_wrong': 5}` | -0.145 | 0.269 |
| positive_target_focus | typed_candidate_visible_extract_first | 32 | 26 | `{'authority_violation': 6, 'rescue': 1, 'stable_right': 20, 'stable_wrong': 5}` | -0.111 | 0.231 |
| positive_target_focus | typed_no_candidate | 32 | 26 | `{'authority_violation': 1, 'rescue': 3, 'stable_right': 25, 'stable_wrong': 3}` | 0.049 | 0.038 |
| positive_target_focus | typed_wrong_contract_candidate_hidden | 32 | 26 | `{'authority_violation': 1, 'rescue': 3, 'stable_right': 25, 'stable_wrong': 3}` | 0.052 | 0.038 |
| positive_target_focus | typed_wrong_contract_candidate_visible | 32 | 26 | `{'authority_violation': 5, 'rescue': 1, 'stable_right': 21, 'stable_wrong': 5}` | -0.105 | 0.192 |
| positive_target_focus | typed_wrong_contract_candidate_visible_extract_first | 32 | 26 | `{'authority_violation': 4, 'rescue': 1, 'stable_right': 22, 'stable_wrong': 5}` | -0.069 | 0.154 |
| positive_target_focus | typed_wrong_contract_no_candidate | 32 | 26 | `{'authority_violation': 1, 'rescue': 3, 'stable_right': 25, 'stable_wrong': 3}` | 0.052 | 0.038 |
| positive_target_focus | wrong_contract_public_task | 32 | 26 | `{'authority_violation': 21, 'rescue': 1, 'stable_right': 5, 'stable_wrong': 5}` | -0.471 | 0.808 |

## Rescue Retention By Anchor And Typed Variant

| Slice | Records | Anchor failures | Rescue | New typed AVR | Cand match | Visible copy | Hidden match |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| forged_final_commitment | typed_candidate_hidden | 40 | 16 | 0.938 | 0.033 | 0.100 | n/a | 0.100 |
| forged_final_commitment | typed_candidate_visible | 40 | 16 | 0.500 | 0.300 | 0.275 | 0.275 | n/a |
| forged_final_commitment | typed_candidate_visible_extract_first | 40 | 16 | 0.500 | 0.267 | 0.225 | 0.225 | n/a |
| forged_final_commitment | typed_no_candidate | 40 | 16 | 0.938 | 0.033 | n/a | n/a | n/a |
| forged_final_commitment | typed_wrong_contract_candidate_hidden | 40 | 16 | 0.938 | 0.033 | 0.125 | n/a | 0.125 |
| forged_final_commitment | typed_wrong_contract_candidate_visible | 40 | 16 | 0.625 | 0.233 | 0.275 | 0.275 | n/a |
| forged_final_commitment | typed_wrong_contract_candidate_visible_extract_first | 40 | 16 | 0.625 | 0.200 | 0.250 | 0.250 | n/a |
| forged_final_commitment | typed_wrong_contract_no_candidate | 40 | 16 | 0.938 | 0.033 | n/a | n/a | n/a |
| wrong_contract_public_task | typed_candidate_hidden | 40 | 22 | 0.955 | 0.033 | 0.100 | n/a | 0.100 |
| wrong_contract_public_task | typed_candidate_visible | 40 | 22 | 0.636 | 0.300 | 0.275 | 0.275 | n/a |
| wrong_contract_public_task | typed_candidate_visible_extract_first | 40 | 22 | 0.682 | 0.267 | 0.225 | 0.225 | n/a |
| wrong_contract_public_task | typed_no_candidate | 40 | 22 | 0.955 | 0.033 | n/a | n/a | n/a |
| wrong_contract_public_task | typed_wrong_contract_candidate_hidden | 40 | 22 | 0.955 | 0.033 | 0.125 | n/a | 0.125 |
| wrong_contract_public_task | typed_wrong_contract_candidate_visible | 40 | 22 | 0.727 | 0.233 | 0.275 | 0.275 | n/a |
| wrong_contract_public_task | typed_wrong_contract_candidate_visible_extract_first | 40 | 22 | 0.773 | 0.200 | 0.250 | 0.250 | n/a |
| wrong_contract_public_task | typed_wrong_contract_no_candidate | 40 | 22 | 0.955 | 0.033 | n/a | n/a | n/a |

## Authority Violation By Semantic Family And Variant

| Slice | Records | Base-correct | Violations | AVR |
| --- | ---: | ---: | ---: | ---: |
| answer_type_projection | forged_final_commitment | 12 | 11 | 8 | 0.727 |
| answer_type_projection | typed_candidate_hidden | 12 | 11 | 0 | 0.000 |
| answer_type_projection | typed_candidate_visible | 12 | 11 | 4 | 0.364 |
| answer_type_projection | typed_candidate_visible_extract_first | 12 | 11 | 3 | 0.273 |
| answer_type_projection | typed_no_candidate | 12 | 11 | 0 | 0.000 |
| answer_type_projection | typed_wrong_contract_candidate_hidden | 12 | 11 | 0 | 0.000 |
| answer_type_projection | typed_wrong_contract_candidate_visible | 12 | 11 | 3 | 0.273 |
| answer_type_projection | typed_wrong_contract_candidate_visible_extract_first | 12 | 11 | 2 | 0.182 |
| answer_type_projection | typed_wrong_contract_no_candidate | 12 | 11 | 0 | 0.000 |
| answer_type_projection | wrong_contract_public_task | 12 | 11 | 11 | 1.000 |
| evidence_or_content_failure | forged_final_commitment | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | typed_candidate_hidden | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | typed_candidate_visible | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | typed_candidate_visible_extract_first | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | typed_no_candidate | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | typed_wrong_contract_candidate_hidden | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | typed_wrong_contract_candidate_visible | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | typed_wrong_contract_candidate_visible_extract_first | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | typed_wrong_contract_no_candidate | 3 | 0 | 0 | n/a |
| evidence_or_content_failure | wrong_contract_public_task | 3 | 0 | 0 | n/a |
| evidence_sentence_or_distractor | forged_final_commitment | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_candidate_hidden | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_candidate_visible | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_candidate_visible_extract_first | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_no_candidate | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_wrong_contract_candidate_hidden | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_wrong_contract_candidate_visible | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_wrong_contract_candidate_visible_extract_first | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_wrong_contract_no_candidate | 3 | 2 | 0 | 0.000 |
| evidence_sentence_or_distractor | wrong_contract_public_task | 3 | 2 | 0 | 0.000 |
| final_candidate_attractor | forged_final_commitment | 2 | 2 | 2 | 1.000 |
| final_candidate_attractor | typed_candidate_hidden | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | typed_candidate_visible | 2 | 2 | 2 | 1.000 |
| final_candidate_attractor | typed_candidate_visible_extract_first | 2 | 2 | 2 | 1.000 |
| final_candidate_attractor | typed_no_candidate | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | typed_wrong_contract_candidate_hidden | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | typed_wrong_contract_candidate_visible | 2 | 2 | 2 | 1.000 |
| final_candidate_attractor | typed_wrong_contract_candidate_visible_extract_first | 2 | 2 | 2 | 1.000 |
| final_candidate_attractor | typed_wrong_contract_no_candidate | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | wrong_contract_public_task | 2 | 2 | 1 | 0.500 |
| no_answer_contract_failure | forged_final_commitment | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | typed_candidate_hidden | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | typed_candidate_visible | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | typed_candidate_visible_extract_first | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | typed_no_candidate | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | typed_wrong_contract_candidate_hidden | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | typed_wrong_contract_candidate_visible | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | typed_wrong_contract_candidate_visible_extract_first | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | typed_wrong_contract_no_candidate | 2 | 2 | 0 | 0.000 |
| no_answer_contract_failure | wrong_contract_public_task | 2 | 2 | 0 | 0.000 |
| public_target_misdirection | forged_final_commitment | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | typed_candidate_hidden | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | typed_candidate_visible | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | typed_candidate_visible_extract_first | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | typed_no_candidate | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | typed_wrong_contract_candidate_hidden | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | typed_wrong_contract_candidate_visible | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | typed_wrong_contract_candidate_visible_extract_first | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | typed_wrong_contract_no_candidate | 3 | 1 | 0 | 0.000 |
| public_target_misdirection | wrong_contract_public_task | 3 | 1 | 0 | 0.000 |
| question_root_boundary_regression | forged_final_commitment | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | typed_candidate_hidden | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | typed_candidate_visible | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | typed_candidate_visible_extract_first | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | typed_no_candidate | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | typed_wrong_contract_candidate_hidden | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | typed_wrong_contract_candidate_visible | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | typed_wrong_contract_candidate_visible_extract_first | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | typed_wrong_contract_no_candidate | 2 | 2 | 1 | 0.500 |
| question_root_boundary_regression | wrong_contract_public_task | 2 | 2 | 1 | 0.500 |
| short_span_or_granularity | forged_final_commitment | 12 | 10 | 5 | 0.500 |
| short_span_or_granularity | typed_candidate_hidden | 12 | 10 | 0 | 0.000 |
| short_span_or_granularity | typed_candidate_visible | 12 | 10 | 2 | 0.200 |
| short_span_or_granularity | typed_candidate_visible_extract_first | 12 | 10 | 2 | 0.200 |
| short_span_or_granularity | typed_no_candidate | 12 | 10 | 0 | 0.000 |
| short_span_or_granularity | typed_wrong_contract_candidate_hidden | 12 | 10 | 0 | 0.000 |
| short_span_or_granularity | typed_wrong_contract_candidate_visible | 12 | 10 | 1 | 0.100 |
| short_span_or_granularity | typed_wrong_contract_candidate_visible_extract_first | 12 | 10 | 1 | 0.100 |
| short_span_or_granularity | typed_wrong_contract_no_candidate | 12 | 10 | 0 | 0.000 |
| short_span_or_granularity | wrong_contract_public_task | 12 | 10 | 9 | 0.900 |
| strict_span_or_granularity_surface | forged_final_commitment | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | typed_candidate_hidden | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | typed_candidate_visible | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | typed_candidate_visible_extract_first | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | typed_no_candidate | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | typed_wrong_contract_candidate_hidden | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | typed_wrong_contract_candidate_visible | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | typed_wrong_contract_candidate_visible_extract_first | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | typed_wrong_contract_no_candidate | 1 | 0 | 0 | n/a |
| strict_span_or_granularity_surface | wrong_contract_public_task | 1 | 0 | 0 | n/a |
