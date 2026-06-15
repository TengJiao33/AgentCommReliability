# PACT Authority/Evidence Stress Evaluation

- Prediction source: `outputs`
- Records: `200`
- Exact match: `0.570`
- Avg F1: `0.679`

## By Variant

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| delegated_action_required_authority | 40 | 0.375 | 0.541 | n/a | 0 | 0 |
| final_candidate_lure | 40 | 0.425 | 0.577 | 0.417 | 13 | 0 |
| frozen_question_target | 40 | 0.725 | 0.798 | n/a | 0 | 0 |
| trusted_root_injected_action_required | 40 | 0.575 | 0.677 | n/a | 0 | 0 |
| trusted_root_original_public | 40 | 0.750 | 0.803 | n/a | 0 | 0 |

## By Source Type And Variant

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| negative_control | delegated_action_required_authority | 8 | 0.500 | 0.604 | n/a | 0 | 0 |
| negative_control | final_candidate_lure | 8 | 0.250 | 0.354 | 0.500 | 0 | 0 |
| negative_control | frozen_question_target | 8 | 0.250 | 0.346 | n/a | 0 | 0 |
| negative_control | trusted_root_injected_action_required | 8 | 0.500 | 0.604 | n/a | 0 | 0 |
| negative_control | trusted_root_original_public | 8 | 0.500 | 0.557 | n/a | 0 | 0 |
| positive_target_focus | delegated_action_required_authority | 32 | 0.344 | 0.525 | n/a | 0 | 0 |
| positive_target_focus | final_candidate_lure | 32 | 0.469 | 0.633 | 0.400 | 13 | 0 |
| positive_target_focus | frozen_question_target | 32 | 0.844 | 0.911 | n/a | 0 | 0 |
| positive_target_focus | trusted_root_injected_action_required | 32 | 0.594 | 0.695 | n/a | 0 | 0 |
| positive_target_focus | trusted_root_original_public | 32 | 0.812 | 0.865 | n/a | 0 | 0 |

## By Semantic Family And Variant

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| answer_type_projection | delegated_action_required_authority | 12 | 0.500 | 0.589 | n/a | 0 | 0 |
| answer_type_projection | final_candidate_lure | 12 | 0.417 | 0.512 | 0.333 | 5 | 0 |
| answer_type_projection | frozen_question_target | 12 | 1.000 | 1.000 | n/a | 0 | 0 |
| answer_type_projection | trusted_root_injected_action_required | 12 | 0.833 | 0.833 | n/a | 0 | 0 |
| answer_type_projection | trusted_root_original_public | 12 | 0.917 | 0.917 | n/a | 0 | 0 |
| evidence_or_content_failure | delegated_action_required_authority | 3 | 0.000 | 0.000 | n/a | 0 | 0 |
| evidence_or_content_failure | final_candidate_lure | 3 | 0.000 | 0.000 | 1.000 | 0 | 0 |
| evidence_or_content_failure | frozen_question_target | 3 | 0.000 | 0.000 | n/a | 0 | 0 |
| evidence_or_content_failure | trusted_root_injected_action_required | 3 | 0.000 | 0.000 | n/a | 0 | 0 |
| evidence_or_content_failure | trusted_root_original_public | 3 | 0.000 | 0.000 | n/a | 0 | 0 |
| evidence_sentence_or_distractor | delegated_action_required_authority | 3 | 0.667 | 0.769 | n/a | 0 | 0 |
| evidence_sentence_or_distractor | final_candidate_lure | 3 | 0.667 | 0.800 | 0.333 | 2 | 0 |
| evidence_sentence_or_distractor | frozen_question_target | 3 | 1.000 | 1.000 | n/a | 0 | 0 |
| evidence_sentence_or_distractor | trusted_root_injected_action_required | 3 | 0.667 | 0.769 | n/a | 0 | 0 |
| evidence_sentence_or_distractor | trusted_root_original_public | 3 | 0.667 | 0.833 | n/a | 0 | 0 |
| final_candidate_attractor | delegated_action_required_authority | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| final_candidate_attractor | final_candidate_lure | 2 | 0.000 | 0.000 | 0.000 | 0 | 0 |
| final_candidate_attractor | frozen_question_target | 2 | 0.000 | 0.000 | n/a | 0 | 0 |
| final_candidate_attractor | trusted_root_injected_action_required | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| final_candidate_attractor | trusted_root_original_public | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| no_answer_contract_failure | delegated_action_required_authority | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| no_answer_contract_failure | final_candidate_lure | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| no_answer_contract_failure | frozen_question_target | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| no_answer_contract_failure | trusted_root_injected_action_required | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| no_answer_contract_failure | trusted_root_original_public | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| public_target_misdirection | delegated_action_required_authority | 3 | 0.333 | 0.333 | n/a | 0 | 0 |
| public_target_misdirection | final_candidate_lure | 3 | 0.333 | 0.333 | 0.667 | 1 | 0 |
| public_target_misdirection | frozen_question_target | 3 | 1.000 | 1.000 | n/a | 0 | 0 |
| public_target_misdirection | trusted_root_injected_action_required | 3 | 0.333 | 0.333 | n/a | 0 | 0 |
| public_target_misdirection | trusted_root_original_public | 3 | 0.333 | 0.333 | n/a | 0 | 0 |
| question_root_boundary_regression | delegated_action_required_authority | 2 | 0.500 | 0.722 | n/a | 0 | 0 |
| question_root_boundary_regression | final_candidate_lure | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| question_root_boundary_regression | frozen_question_target | 2 | 0.000 | 0.286 | n/a | 0 | 0 |
| question_root_boundary_regression | trusted_root_injected_action_required | 2 | 0.500 | 0.667 | n/a | 0 | 0 |
| question_root_boundary_regression | trusted_root_original_public | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| short_span_or_granularity | delegated_action_required_authority | 12 | 0.083 | 0.416 | n/a | 0 | 0 |
| short_span_or_granularity | final_candidate_lure | 12 | 0.417 | 0.727 | 0.417 | 5 | 0 |
| short_span_or_granularity | frozen_question_target | 12 | 0.750 | 0.881 | n/a | 0 | 0 |
| short_span_or_granularity | trusted_root_injected_action_required | 12 | 0.417 | 0.634 | n/a | 0 | 0 |
| short_span_or_granularity | trusted_root_original_public | 12 | 0.833 | 0.931 | n/a | 0 | 0 |
| strict_span_or_granularity_surface | delegated_action_required_authority | 1 | 0.000 | 0.833 | n/a | 0 | 0 |
| strict_span_or_granularity_surface | final_candidate_lure | 1 | 0.000 | 0.833 | 0.000 | 0 | 0 |
| strict_span_or_granularity_surface | frozen_question_target | 1 | 0.000 | 0.769 | n/a | 0 | 0 |
| strict_span_or_granularity_surface | trusted_root_injected_action_required | 1 | 0.000 | 0.833 | n/a | 0 | 0 |
| strict_span_or_granularity_surface | trusted_root_original_public | 1 | 0.000 | 0.455 | n/a | 0 | 0 |

## By Bridge Layer And Variant

| Slice | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| evidence_or_content | delegated_action_required_authority | 3 | 0.000 | 0.000 | n/a | 0 | 0 |
| evidence_or_content | final_candidate_lure | 3 | 0.000 | 0.000 | 1.000 | 0 | 0 |
| evidence_or_content | frozen_question_target | 3 | 0.000 | 0.000 | n/a | 0 | 0 |
| evidence_or_content | trusted_root_injected_action_required | 3 | 0.000 | 0.000 | n/a | 0 | 0 |
| evidence_or_content | trusted_root_original_public | 3 | 0.000 | 0.000 | n/a | 0 | 0 |
| final_answer_commitment | delegated_action_required_authority | 3 | 0.667 | 0.944 | n/a | 0 | 0 |
| final_answer_commitment | final_candidate_lure | 3 | 0.000 | 0.278 | 0.000 | 0 | 0 |
| final_answer_commitment | frozen_question_target | 3 | 0.000 | 0.256 | n/a | 0 | 0 |
| final_answer_commitment | trusted_root_injected_action_required | 3 | 0.667 | 0.944 | n/a | 0 | 0 |
| final_answer_commitment | trusted_root_original_public | 3 | 0.667 | 0.818 | n/a | 0 | 0 |
| stable_answer | delegated_action_required_authority | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| stable_answer | final_candidate_lure | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| stable_answer | frozen_question_target | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| stable_answer | trusted_root_injected_action_required | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| stable_answer | trusted_root_original_public | 2 | 1.000 | 1.000 | n/a | 0 | 0 |
| target_authority | delegated_action_required_authority | 22 | 0.364 | 0.571 | n/a | 0 | 0 |
| target_authority | final_candidate_lure | 22 | 0.545 | 0.708 | 0.273 | 12 | 0 |
| target_authority | frozen_question_target | 22 | 0.909 | 0.958 | n/a | 0 | 0 |
| target_authority | trusted_root_injected_action_required | 22 | 0.727 | 0.823 | n/a | 0 | 0 |
| target_authority | trusted_root_original_public | 22 | 1.000 | 1.000 | n/a | 0 | 0 |
| target_contract | delegated_action_required_authority | 10 | 0.300 | 0.425 | n/a | 0 | 0 |
| target_contract | final_candidate_lure | 10 | 0.300 | 0.470 | 0.750 | 1 | 0 |
| target_contract | frozen_question_target | 10 | 0.700 | 0.807 | n/a | 0 | 0 |
| target_contract | trusted_root_injected_action_required | 10 | 0.300 | 0.414 | n/a | 0 | 0 |
| target_contract | trusted_root_original_public | 10 | 0.400 | 0.567 | n/a | 0 | 0 |

## Paired Deltas From Trusted Root Original Public

| Slice | Records | Outcomes | Avg F1 delta |
| --- | ---: | --- | ---: |
| negative_control | delegated_action_required_authority | 8 | `{'stable_right': 4, 'stable_wrong': 4}` | 0.047 |
| negative_control | final_candidate_lure | 8 | `{'regression': 2, 'stable_right': 2, 'stable_wrong': 4}` | -0.203 |
| negative_control | frozen_question_target | 8 | `{'regression': 2, 'stable_right': 2, 'stable_wrong': 4}` | -0.211 |
| negative_control | trusted_root_injected_action_required | 8 | `{'stable_right': 4, 'stable_wrong': 4}` | 0.047 |
| positive_target_focus | delegated_action_required_authority | 32 | `{'regression': 15, 'stable_right': 11, 'stable_wrong': 6}` | -0.339 |
| positive_target_focus | final_candidate_lure | 32 | `{'regression': 11, 'stable_right': 15, 'stable_wrong': 6}` | -0.231 |
| positive_target_focus | frozen_question_target | 32 | `{'regression': 4, 'rescue': 5, 'stable_right': 22, 'stable_wrong': 1}` | 0.046 |
| positive_target_focus | trusted_root_injected_action_required | 32 | `{'regression': 7, 'stable_right': 19, 'stable_wrong': 6}` | -0.169 |
