# PACT Typed Boundary Split Evaluation

- Prediction source: `gold`
- Records: `440`
- Exact match: `1.000`
- Avg F1: `1.000`

## By Variant

| Slice | Records | EM | Avg F1 | Cand match | Visible copy | Hidden match | Corrections |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| forged_final_commitment | 40 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 40 |
| original_untyped_public | 40 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |
| typed_candidate_hidden | 40 | 1.000 | 1.000 | 0.000 | n/a | 0.000 | 40 |
| typed_candidate_visible | 40 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 40 |
| typed_candidate_visible_extract_first | 40 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 40 |
| typed_no_candidate | 40 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |
| typed_wrong_contract_candidate_hidden | 40 | 1.000 | 1.000 | 0.000 | n/a | 0.000 | 40 |
| typed_wrong_contract_candidate_visible | 40 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 40 |
| typed_wrong_contract_candidate_visible_extract_first | 40 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 40 |
| typed_wrong_contract_no_candidate | 40 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |
| wrong_contract_public_task | 40 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |

## By Source Type And Variant

| Slice | Records | EM | Avg F1 | Cand match | Visible copy | Hidden match | Corrections |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| negative_control | forged_final_commitment | 8 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 8 |
| negative_control | original_untyped_public | 8 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |
| negative_control | typed_candidate_hidden | 8 | 1.000 | 1.000 | 0.000 | n/a | 0.000 | 8 |
| negative_control | typed_candidate_visible | 8 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 8 |
| negative_control | typed_candidate_visible_extract_first | 8 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 8 |
| negative_control | typed_no_candidate | 8 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |
| negative_control | typed_wrong_contract_candidate_hidden | 8 | 1.000 | 1.000 | 0.000 | n/a | 0.000 | 8 |
| negative_control | typed_wrong_contract_candidate_visible | 8 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 8 |
| negative_control | typed_wrong_contract_candidate_visible_extract_first | 8 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 8 |
| negative_control | typed_wrong_contract_no_candidate | 8 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |
| negative_control | wrong_contract_public_task | 8 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |
| positive_target_focus | forged_final_commitment | 32 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 32 |
| positive_target_focus | original_untyped_public | 32 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |
| positive_target_focus | typed_candidate_hidden | 32 | 1.000 | 1.000 | 0.000 | n/a | 0.000 | 32 |
| positive_target_focus | typed_candidate_visible | 32 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 32 |
| positive_target_focus | typed_candidate_visible_extract_first | 32 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 32 |
| positive_target_focus | typed_no_candidate | 32 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |
| positive_target_focus | typed_wrong_contract_candidate_hidden | 32 | 1.000 | 1.000 | 0.000 | n/a | 0.000 | 32 |
| positive_target_focus | typed_wrong_contract_candidate_visible | 32 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 32 |
| positive_target_focus | typed_wrong_contract_candidate_visible_extract_first | 32 | 1.000 | 1.000 | 0.000 | 0.000 | n/a | 32 |
| positive_target_focus | typed_wrong_contract_no_candidate | 32 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |
| positive_target_focus | wrong_contract_public_task | 32 | 1.000 | 1.000 | n/a | n/a | n/a | 0 |

## Paired Deltas From Original Untyped Public

| Slice | Records | Base-correct | Outcomes | Avg F1 delta | AVR |
| --- | ---: | ---: | --- | ---: | ---: |
| negative_control | forged_final_commitment | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 |
| negative_control | typed_candidate_hidden | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 |
| negative_control | typed_candidate_visible | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 |
| negative_control | typed_candidate_visible_extract_first | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 |
| negative_control | typed_no_candidate | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 |
| negative_control | typed_wrong_contract_candidate_hidden | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 |
| negative_control | typed_wrong_contract_candidate_visible | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 |
| negative_control | typed_wrong_contract_candidate_visible_extract_first | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 |
| negative_control | typed_wrong_contract_no_candidate | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 |
| negative_control | wrong_contract_public_task | 8 | 8 | `{'stable_right': 8}` | 0.000 | 0.000 |
| positive_target_focus | forged_final_commitment | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 |
| positive_target_focus | typed_candidate_hidden | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 |
| positive_target_focus | typed_candidate_visible | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 |
| positive_target_focus | typed_candidate_visible_extract_first | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 |
| positive_target_focus | typed_no_candidate | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 |
| positive_target_focus | typed_wrong_contract_candidate_hidden | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 |
| positive_target_focus | typed_wrong_contract_candidate_visible | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 |
| positive_target_focus | typed_wrong_contract_candidate_visible_extract_first | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 |
| positive_target_focus | typed_wrong_contract_no_candidate | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 |
| positive_target_focus | wrong_contract_public_task | 32 | 32 | `{'stable_right': 32}` | 0.000 | 0.000 |

## Rescue Retention By Anchor And Typed Variant

| Slice | Records | Anchor failures | Rescue | New typed AVR | Cand match | Visible copy | Hidden match |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| forged_final_commitment | typed_candidate_hidden | 40 | 0 | n/a | 0.000 | 0.000 | n/a | 0.000 |
| forged_final_commitment | typed_candidate_visible | 40 | 0 | n/a | 0.000 | 0.000 | 0.000 | n/a |
| forged_final_commitment | typed_candidate_visible_extract_first | 40 | 0 | n/a | 0.000 | 0.000 | 0.000 | n/a |
| forged_final_commitment | typed_no_candidate | 40 | 0 | n/a | 0.000 | n/a | n/a | n/a |
| forged_final_commitment | typed_wrong_contract_candidate_hidden | 40 | 0 | n/a | 0.000 | 0.000 | n/a | 0.000 |
| forged_final_commitment | typed_wrong_contract_candidate_visible | 40 | 0 | n/a | 0.000 | 0.000 | 0.000 | n/a |
| forged_final_commitment | typed_wrong_contract_candidate_visible_extract_first | 40 | 0 | n/a | 0.000 | 0.000 | 0.000 | n/a |
| forged_final_commitment | typed_wrong_contract_no_candidate | 40 | 0 | n/a | 0.000 | n/a | n/a | n/a |
| wrong_contract_public_task | typed_candidate_hidden | 40 | 0 | n/a | 0.000 | 0.000 | n/a | 0.000 |
| wrong_contract_public_task | typed_candidate_visible | 40 | 0 | n/a | 0.000 | 0.000 | 0.000 | n/a |
| wrong_contract_public_task | typed_candidate_visible_extract_first | 40 | 0 | n/a | 0.000 | 0.000 | 0.000 | n/a |
| wrong_contract_public_task | typed_no_candidate | 40 | 0 | n/a | 0.000 | n/a | n/a | n/a |
| wrong_contract_public_task | typed_wrong_contract_candidate_hidden | 40 | 0 | n/a | 0.000 | 0.000 | n/a | 0.000 |
| wrong_contract_public_task | typed_wrong_contract_candidate_visible | 40 | 0 | n/a | 0.000 | 0.000 | 0.000 | n/a |
| wrong_contract_public_task | typed_wrong_contract_candidate_visible_extract_first | 40 | 0 | n/a | 0.000 | 0.000 | 0.000 | n/a |
| wrong_contract_public_task | typed_wrong_contract_no_candidate | 40 | 0 | n/a | 0.000 | n/a | n/a | n/a |

## Authority Violation By Semantic Family And Variant

| Slice | Records | Base-correct | Violations | AVR |
| --- | ---: | ---: | ---: | ---: |
| answer_type_projection | forged_final_commitment | 12 | 12 | 0 | 0.000 |
| answer_type_projection | typed_candidate_hidden | 12 | 12 | 0 | 0.000 |
| answer_type_projection | typed_candidate_visible | 12 | 12 | 0 | 0.000 |
| answer_type_projection | typed_candidate_visible_extract_first | 12 | 12 | 0 | 0.000 |
| answer_type_projection | typed_no_candidate | 12 | 12 | 0 | 0.000 |
| answer_type_projection | typed_wrong_contract_candidate_hidden | 12 | 12 | 0 | 0.000 |
| answer_type_projection | typed_wrong_contract_candidate_visible | 12 | 12 | 0 | 0.000 |
| answer_type_projection | typed_wrong_contract_candidate_visible_extract_first | 12 | 12 | 0 | 0.000 |
| answer_type_projection | typed_wrong_contract_no_candidate | 12 | 12 | 0 | 0.000 |
| answer_type_projection | wrong_contract_public_task | 12 | 12 | 0 | 0.000 |
| evidence_or_content_failure | forged_final_commitment | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | typed_candidate_hidden | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | typed_candidate_visible | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | typed_candidate_visible_extract_first | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | typed_no_candidate | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | typed_wrong_contract_candidate_hidden | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | typed_wrong_contract_candidate_visible | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | typed_wrong_contract_candidate_visible_extract_first | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | typed_wrong_contract_no_candidate | 3 | 3 | 0 | 0.000 |
| evidence_or_content_failure | wrong_contract_public_task | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | forged_final_commitment | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_candidate_hidden | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_candidate_visible | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_candidate_visible_extract_first | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_no_candidate | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_wrong_contract_candidate_hidden | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_wrong_contract_candidate_visible | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_wrong_contract_candidate_visible_extract_first | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | typed_wrong_contract_no_candidate | 3 | 3 | 0 | 0.000 |
| evidence_sentence_or_distractor | wrong_contract_public_task | 3 | 3 | 0 | 0.000 |
| final_candidate_attractor | forged_final_commitment | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | typed_candidate_hidden | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | typed_candidate_visible | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | typed_candidate_visible_extract_first | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | typed_no_candidate | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | typed_wrong_contract_candidate_hidden | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | typed_wrong_contract_candidate_visible | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | typed_wrong_contract_candidate_visible_extract_first | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | typed_wrong_contract_no_candidate | 2 | 2 | 0 | 0.000 |
| final_candidate_attractor | wrong_contract_public_task | 2 | 2 | 0 | 0.000 |
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
| public_target_misdirection | forged_final_commitment | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | typed_candidate_hidden | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | typed_candidate_visible | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | typed_candidate_visible_extract_first | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | typed_no_candidate | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | typed_wrong_contract_candidate_hidden | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | typed_wrong_contract_candidate_visible | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | typed_wrong_contract_candidate_visible_extract_first | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | typed_wrong_contract_no_candidate | 3 | 3 | 0 | 0.000 |
| public_target_misdirection | wrong_contract_public_task | 3 | 3 | 0 | 0.000 |
| question_root_boundary_regression | forged_final_commitment | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | typed_candidate_hidden | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | typed_candidate_visible | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | typed_candidate_visible_extract_first | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | typed_no_candidate | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | typed_wrong_contract_candidate_hidden | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | typed_wrong_contract_candidate_visible | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | typed_wrong_contract_candidate_visible_extract_first | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | typed_wrong_contract_no_candidate | 2 | 2 | 0 | 0.000 |
| question_root_boundary_regression | wrong_contract_public_task | 2 | 2 | 0 | 0.000 |
| short_span_or_granularity | forged_final_commitment | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | typed_candidate_hidden | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | typed_candidate_visible | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | typed_candidate_visible_extract_first | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | typed_no_candidate | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | typed_wrong_contract_candidate_hidden | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | typed_wrong_contract_candidate_visible | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | typed_wrong_contract_candidate_visible_extract_first | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | typed_wrong_contract_no_candidate | 12 | 12 | 0 | 0.000 |
| short_span_or_granularity | wrong_contract_public_task | 12 | 12 | 0 | 0.000 |
| strict_span_or_granularity_surface | forged_final_commitment | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | typed_candidate_hidden | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | typed_candidate_visible | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | typed_candidate_visible_extract_first | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | typed_no_candidate | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | typed_wrong_contract_candidate_hidden | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | typed_wrong_contract_candidate_visible | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | typed_wrong_contract_candidate_visible_extract_first | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | typed_wrong_contract_no_candidate | 1 | 1 | 0 | 0.000 |
| strict_span_or_granularity_surface | wrong_contract_public_task | 1 | 1 | 0 | 0.000 |
