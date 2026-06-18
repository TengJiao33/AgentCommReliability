# Authority Genesis Ladder Evaluation

- Prediction source: `outputs`
- Records: `504`
- Exact match: `0.687`
- Avg F1: `0.747`

## By Variant

| Slice | Records | EM | Avg F1 | Exact uptake | Substring uptake | Avg injected F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_trusted_question_evidence | 24 | 0.750 | 0.799 | n/a | n/a | n/a |
| correct_gold_active_task_required | 24 | 0.833 | 0.837 | 0.833 | 0.875 | 0.837 |
| correct_gold_answer_shaped_span | 24 | 0.833 | 0.854 | 0.833 | 0.875 | 0.854 |
| correct_gold_final_answer_commitment | 24 | 0.750 | 0.800 | 0.750 | 0.875 | 0.800 |
| correct_gold_hidden_metadata | 24 | 0.750 | 0.799 | 0.750 | 0.875 | 0.799 |
| correct_gold_majority_consensus | 24 | 0.792 | 0.817 | 0.792 | 0.875 | 0.817 |
| correct_gold_peer_claim | 24 | 0.792 | 0.818 | 0.792 | 0.875 | 0.818 |
| correct_gold_previous_final_answer | 24 | 0.750 | 0.800 | 0.750 | 0.875 | 0.800 |
| correct_gold_raw_mention | 24 | 0.833 | 0.854 | 0.833 | 0.875 | 0.854 |
| correct_gold_saved_memory | 24 | 0.875 | 0.875 | 0.875 | 0.875 | 0.875 |
| correct_gold_verifier_approved_result | 24 | 0.875 | 0.906 | 0.875 | 0.958 | 0.906 |
| wrong_lure_active_task_required | 24 | 0.292 | 0.474 | 0.583 | 0.750 | 0.694 |
| wrong_lure_answer_shaped_span | 24 | 0.625 | 0.679 | 0.250 | 0.667 | 0.426 |
| wrong_lure_final_answer_commitment | 24 | 0.458 | 0.575 | 0.333 | 0.667 | 0.499 |
| wrong_lure_hidden_metadata | 24 | 0.750 | 0.799 | 0.125 | 0.667 | 0.367 |
| wrong_lure_majority_consensus | 24 | 0.583 | 0.668 | 0.292 | 0.708 | 0.448 |
| wrong_lure_peer_claim | 24 | 0.500 | 0.617 | 0.375 | 0.667 | 0.507 |
| wrong_lure_previous_final_answer | 24 | 0.667 | 0.721 | 0.250 | 0.667 | 0.413 |
| wrong_lure_raw_mention | 24 | 0.667 | 0.721 | 0.208 | 0.667 | 0.388 |
| wrong_lure_saved_memory | 24 | 0.542 | 0.667 | 0.292 | 0.667 | 0.449 |
| wrong_lure_verifier_approved_result | 24 | 0.500 | 0.617 | 0.333 | 0.667 | 0.487 |

## By Content Polarity And Future Signal

| Slice | Records | EM | Avg F1 | Exact uptake | Substring uptake | Avg injected F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| correct_gold | -1 | hidden_metadata | 24 | 0.750 | 0.799 | 0.750 | 0.875 | 0.799 |
| correct_gold | 0 | raw_mention | 24 | 0.833 | 0.854 | 0.833 | 0.875 | 0.854 |
| correct_gold | 1 | answer_shaped_span | 24 | 0.833 | 0.854 | 0.833 | 0.875 | 0.854 |
| correct_gold | 2 | peer_claim | 24 | 0.792 | 0.818 | 0.792 | 0.875 | 0.818 |
| correct_gold | 3 | majority_consensus | 24 | 0.792 | 0.817 | 0.792 | 0.875 | 0.817 |
| correct_gold | 4 | previous_final_answer | 24 | 0.750 | 0.800 | 0.750 | 0.875 | 0.800 |
| correct_gold | 5 | verifier_approved_result | 24 | 0.875 | 0.906 | 0.875 | 0.958 | 0.906 |
| correct_gold | 6 | saved_memory | 24 | 0.875 | 0.875 | 0.875 | 0.875 | 0.875 |
| correct_gold | 7 | active_task_required | 24 | 0.833 | 0.837 | 0.833 | 0.875 | 0.837 |
| correct_gold | 8 | final_answer_commitment | 24 | 0.750 | 0.800 | 0.750 | 0.875 | 0.800 |
| none |  | none | 24 | 0.750 | 0.799 | n/a | n/a | n/a |
| wrong_lure | -1 | hidden_metadata | 24 | 0.750 | 0.799 | 0.125 | 0.667 | 0.367 |
| wrong_lure | 0 | raw_mention | 24 | 0.667 | 0.721 | 0.208 | 0.667 | 0.388 |
| wrong_lure | 1 | answer_shaped_span | 24 | 0.625 | 0.679 | 0.250 | 0.667 | 0.426 |
| wrong_lure | 2 | peer_claim | 24 | 0.500 | 0.617 | 0.375 | 0.667 | 0.507 |
| wrong_lure | 3 | majority_consensus | 24 | 0.583 | 0.668 | 0.292 | 0.708 | 0.448 |
| wrong_lure | 4 | previous_final_answer | 24 | 0.667 | 0.721 | 0.250 | 0.667 | 0.413 |
| wrong_lure | 5 | verifier_approved_result | 24 | 0.500 | 0.617 | 0.333 | 0.667 | 0.487 |
| wrong_lure | 6 | saved_memory | 24 | 0.542 | 0.667 | 0.292 | 0.667 | 0.449 |
| wrong_lure | 7 | active_task_required | 24 | 0.292 | 0.474 | 0.583 | 0.750 | 0.694 |
| wrong_lure | 8 | final_answer_commitment | 24 | 0.458 | 0.575 | 0.333 | 0.667 | 0.499 |

## Paired Deltas By Ladder Level

| Slice | Records | Base-right | Base-wrong | Outcomes | F1 delta | AVR | AUR | Utility |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| correct_gold | -1 | hidden_metadata | 24 | 18 | 6 | `{'stable_right': 18, 'stable_wrong': 6}` | 0.000 | 0.000 | 0.000 | 0.000 |
| correct_gold | 0 | raw_mention | 24 | 18 | 6 | `{'rescue': 2, 'stable_right': 18, 'stable_wrong': 4}` | 0.056 | 0.000 | 0.000 | 0.333 |
| correct_gold | 1 | answer_shaped_span | 24 | 18 | 6 | `{'rescue': 2, 'stable_right': 18, 'stable_wrong': 4}` | 0.056 | 0.000 | 0.000 | 0.333 |
| correct_gold | 2 | peer_claim | 24 | 18 | 6 | `{'authority_violation': 1, 'rescue': 2, 'stable_right': 17, 'stable_wrong': 4}` | 0.020 | 0.056 | 0.000 | 0.333 |
| correct_gold | 3 | majority_consensus | 24 | 18 | 6 | `{'authority_violation': 1, 'rescue': 2, 'stable_right': 17, 'stable_wrong': 4}` | 0.018 | 0.056 | 0.000 | 0.333 |
| correct_gold | 4 | previous_final_answer | 24 | 18 | 6 | `{'authority_violation': 1, 'rescue': 1, 'stable_right': 17, 'stable_wrong': 5}` | 0.002 | 0.056 | 0.000 | 0.167 |
| correct_gold | 5 | verifier_approved_result | 24 | 18 | 6 | `{'authority_violation': 1, 'rescue': 4, 'stable_right': 17, 'stable_wrong': 2}` | 0.108 | 0.056 | 0.000 | 0.667 |
| correct_gold | 6 | saved_memory | 24 | 18 | 6 | `{'rescue': 3, 'stable_right': 18, 'stable_wrong': 3}` | 0.076 | 0.000 | 0.000 | 0.500 |
| correct_gold | 7 | active_task_required | 24 | 18 | 6 | `{'authority_violation': 1, 'rescue': 3, 'stable_right': 17, 'stable_wrong': 3}` | 0.038 | 0.056 | 0.000 | 0.500 |
| correct_gold | 8 | final_answer_commitment | 24 | 18 | 6 | `{'authority_violation': 1, 'rescue': 1, 'stable_right': 17, 'stable_wrong': 5}` | 0.002 | 0.056 | 0.000 | 0.167 |
| wrong_lure | -1 | hidden_metadata | 24 | 18 | 6 | `{'stable_right': 18, 'stable_wrong': 6}` | 0.000 | 0.000 | 0.000 | 0.000 |
| wrong_lure | 0 | raw_mention | 24 | 18 | 6 | `{'authority_violation': 2, 'stable_right': 16, 'stable_wrong': 6}` | -0.078 | 0.111 | 0.000 | 0.000 |
| wrong_lure | 1 | answer_shaped_span | 24 | 18 | 6 | `{'authority_violation': 3, 'stable_right': 15, 'stable_wrong': 6}` | -0.119 | 0.167 | 0.000 | 0.000 |
| wrong_lure | 2 | peer_claim | 24 | 18 | 6 | `{'authority_violation': 6, 'stable_right': 12, 'stable_wrong': 6}` | -0.182 | 0.333 | 0.167 | 0.000 |
| wrong_lure | 3 | majority_consensus | 24 | 18 | 6 | `{'authority_violation': 4, 'stable_right': 14, 'stable_wrong': 6}` | -0.131 | 0.222 | 0.056 | 0.000 |
| wrong_lure | 4 | previous_final_answer | 24 | 18 | 6 | `{'authority_violation': 2, 'stable_right': 16, 'stable_wrong': 6}` | -0.078 | 0.111 | 0.000 | 0.000 |
| wrong_lure | 5 | verifier_approved_result | 24 | 18 | 6 | `{'authority_violation': 6, 'stable_right': 12, 'stable_wrong': 6}` | -0.182 | 0.333 | 0.111 | 0.000 |
| wrong_lure | 6 | saved_memory | 24 | 18 | 6 | `{'authority_violation': 5, 'stable_right': 13, 'stable_wrong': 6}` | -0.131 | 0.278 | 0.056 | 0.000 |
| wrong_lure | 7 | active_task_required | 24 | 18 | 6 | `{'authority_violation': 11, 'stable_right': 7, 'stable_wrong': 6}` | -0.325 | 0.611 | 0.444 | 0.000 |
| wrong_lure | 8 | final_answer_commitment | 24 | 18 | 6 | `{'authority_violation': 7, 'stable_right': 11, 'stable_wrong': 6}` | -0.224 | 0.389 | 0.111 | 0.000 |

## Wrong-Lure Authority By Future Level

| Slice | Wrong rows | Base-right | Violations | AVR | Uptake | AUR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| -1 | hidden_metadata | 24 | 18 | 0 | 0.000 | 0 | 0.000 |
| 0 | raw_mention | 24 | 18 | 2 | 0.111 | 0 | 0.000 |
| 1 | answer_shaped_span | 24 | 18 | 3 | 0.167 | 0 | 0.000 |
| 2 | peer_claim | 24 | 18 | 6 | 0.333 | 3 | 0.167 |
| 3 | majority_consensus | 24 | 18 | 4 | 0.222 | 1 | 0.056 |
| 4 | previous_final_answer | 24 | 18 | 2 | 0.111 | 0 | 0.000 |
| 5 | verifier_approved_result | 24 | 18 | 6 | 0.333 | 2 | 0.111 |
| 6 | saved_memory | 24 | 18 | 5 | 0.278 | 1 | 0.056 |
| 7 | active_task_required | 24 | 18 | 11 | 0.611 | 8 | 0.444 |
| 8 | final_answer_commitment | 24 | 18 | 7 | 0.389 | 2 | 0.111 |

## Wrong-Lure Authority By Semantic Family And Future Signal

| Slice | Wrong rows | Base-right | Violations | AVR | Uptake | AUR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| answer_type_projection | -1 | hidden_metadata | 6 | 5 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 0 | raw_mention | 6 | 5 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 1 | answer_shaped_span | 6 | 5 | 1 | 0.200 | 0 | 0.000 |
| answer_type_projection | 2 | peer_claim | 6 | 5 | 3 | 0.600 | 3 | 0.600 |
| answer_type_projection | 3 | majority_consensus | 6 | 5 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 4 | previous_final_answer | 6 | 5 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 5 | verifier_approved_result | 6 | 5 | 1 | 0.200 | 1 | 0.200 |
| answer_type_projection | 6 | saved_memory | 6 | 5 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 7 | active_task_required | 6 | 5 | 4 | 0.800 | 4 | 0.800 |
| answer_type_projection | 8 | final_answer_commitment | 6 | 5 | 2 | 0.400 | 1 | 0.200 |
| evidence_or_content_failure | -1 | hidden_metadata | 2 | 0 | 0 | n/a | 0 | n/a |
| evidence_or_content_failure | 0 | raw_mention | 2 | 0 | 0 | n/a | 0 | n/a |
| evidence_or_content_failure | 1 | answer_shaped_span | 2 | 0 | 0 | n/a | 0 | n/a |
| evidence_or_content_failure | 2 | peer_claim | 2 | 0 | 0 | n/a | 0 | n/a |
| evidence_or_content_failure | 3 | majority_consensus | 2 | 0 | 0 | n/a | 0 | n/a |
| evidence_or_content_failure | 4 | previous_final_answer | 2 | 0 | 0 | n/a | 0 | n/a |
| evidence_or_content_failure | 5 | verifier_approved_result | 2 | 0 | 0 | n/a | 0 | n/a |
| evidence_or_content_failure | 6 | saved_memory | 2 | 0 | 0 | n/a | 0 | n/a |
| evidence_or_content_failure | 7 | active_task_required | 2 | 0 | 0 | n/a | 0 | n/a |
| evidence_or_content_failure | 8 | final_answer_commitment | 2 | 0 | 0 | n/a | 0 | n/a |
| evidence_sentence_or_distractor | -1 | hidden_metadata | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 0 | raw_mention | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 1 | answer_shaped_span | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 2 | peer_claim | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 3 | majority_consensus | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 4 | previous_final_answer | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 5 | verifier_approved_result | 3 | 3 | 1 | 0.333 | 0 | 0.000 |
| evidence_sentence_or_distractor | 6 | saved_memory | 3 | 3 | 1 | 0.333 | 0 | 0.000 |
| evidence_sentence_or_distractor | 7 | active_task_required | 3 | 3 | 1 | 0.333 | 1 | 0.333 |
| evidence_sentence_or_distractor | 8 | final_answer_commitment | 3 | 3 | 1 | 0.333 | 0 | 0.000 |
| final_candidate_attractor | -1 | hidden_metadata | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| final_candidate_attractor | 0 | raw_mention | 1 | 1 | 1 | 1.000 | 0 | 0.000 |
| final_candidate_attractor | 1 | answer_shaped_span | 1 | 1 | 1 | 1.000 | 0 | 0.000 |
| final_candidate_attractor | 2 | peer_claim | 1 | 1 | 1 | 1.000 | 0 | 0.000 |
| final_candidate_attractor | 3 | majority_consensus | 1 | 1 | 1 | 1.000 | 0 | 0.000 |
| final_candidate_attractor | 4 | previous_final_answer | 1 | 1 | 1 | 1.000 | 0 | 0.000 |
| final_candidate_attractor | 5 | verifier_approved_result | 1 | 1 | 1 | 1.000 | 0 | 0.000 |
| final_candidate_attractor | 6 | saved_memory | 1 | 1 | 1 | 1.000 | 0 | 0.000 |
| final_candidate_attractor | 7 | active_task_required | 1 | 1 | 1 | 1.000 | 0 | 0.000 |
| final_candidate_attractor | 8 | final_answer_commitment | 1 | 1 | 1 | 1.000 | 0 | 0.000 |
| no_answer_contract_failure | -1 | hidden_metadata | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| no_answer_contract_failure | 0 | raw_mention | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| no_answer_contract_failure | 1 | answer_shaped_span | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| no_answer_contract_failure | 2 | peer_claim | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| no_answer_contract_failure | 3 | majority_consensus | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| no_answer_contract_failure | 4 | previous_final_answer | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| no_answer_contract_failure | 5 | verifier_approved_result | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| no_answer_contract_failure | 6 | saved_memory | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| no_answer_contract_failure | 7 | active_task_required | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| no_answer_contract_failure | 8 | final_answer_commitment | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| public_target_misdirection | -1 | hidden_metadata | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| public_target_misdirection | 0 | raw_mention | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| public_target_misdirection | 1 | answer_shaped_span | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| public_target_misdirection | 2 | peer_claim | 3 | 3 | 1 | 0.333 | 0 | 0.000 |
| public_target_misdirection | 3 | majority_consensus | 3 | 3 | 1 | 0.333 | 0 | 0.000 |
| public_target_misdirection | 4 | previous_final_answer | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| public_target_misdirection | 5 | verifier_approved_result | 3 | 3 | 1 | 0.333 | 0 | 0.000 |
| public_target_misdirection | 6 | saved_memory | 3 | 3 | 1 | 0.333 | 0 | 0.000 |
| public_target_misdirection | 7 | active_task_required | 3 | 3 | 2 | 0.667 | 1 | 0.333 |
| public_target_misdirection | 8 | final_answer_commitment | 3 | 3 | 1 | 0.333 | 0 | 0.000 |
| question_root_boundary_regression | -1 | hidden_metadata | 2 | 1 | 0 | 0.000 | 0 | 0.000 |
| question_root_boundary_regression | 0 | raw_mention | 2 | 1 | 1 | 1.000 | 0 | 0.000 |
| question_root_boundary_regression | 1 | answer_shaped_span | 2 | 1 | 1 | 1.000 | 0 | 0.000 |
| question_root_boundary_regression | 2 | peer_claim | 2 | 1 | 1 | 1.000 | 0 | 0.000 |
| question_root_boundary_regression | 3 | majority_consensus | 2 | 1 | 1 | 1.000 | 0 | 0.000 |
| question_root_boundary_regression | 4 | previous_final_answer | 2 | 1 | 1 | 1.000 | 0 | 0.000 |
| question_root_boundary_regression | 5 | verifier_approved_result | 2 | 1 | 1 | 1.000 | 0 | 0.000 |
| question_root_boundary_regression | 6 | saved_memory | 2 | 1 | 1 | 1.000 | 0 | 0.000 |
| question_root_boundary_regression | 7 | active_task_required | 2 | 1 | 1 | 1.000 | 0 | 0.000 |
| question_root_boundary_regression | 8 | final_answer_commitment | 2 | 1 | 1 | 1.000 | 0 | 0.000 |
| short_span_or_granularity | -1 | hidden_metadata | 6 | 4 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 0 | raw_mention | 6 | 4 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 1 | answer_shaped_span | 6 | 4 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 2 | peer_claim | 6 | 4 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 3 | majority_consensus | 6 | 4 | 1 | 0.250 | 1 | 0.250 |
| short_span_or_granularity | 4 | previous_final_answer | 6 | 4 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 5 | verifier_approved_result | 6 | 4 | 1 | 0.250 | 1 | 0.250 |
| short_span_or_granularity | 6 | saved_memory | 6 | 4 | 1 | 0.250 | 1 | 0.250 |
| short_span_or_granularity | 7 | active_task_required | 6 | 4 | 2 | 0.500 | 2 | 0.500 |
| short_span_or_granularity | 8 | final_answer_commitment | 6 | 4 | 1 | 0.250 | 1 | 0.250 |
