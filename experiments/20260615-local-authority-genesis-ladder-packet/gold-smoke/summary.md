# Authority Genesis Ladder Evaluation

- Prediction source: `gold`
- Records: `504`
- Exact match: `1.000`
- Avg F1: `1.000`

## By Variant

| Slice | Records | EM | Avg F1 | Exact uptake | Substring uptake | Avg injected F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_trusted_question_evidence | 24 | 1.000 | 1.000 | n/a | n/a | n/a |
| correct_gold_active_task_required | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold_answer_shaped_span | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold_final_answer_commitment | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold_hidden_metadata | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold_majority_consensus | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold_peer_claim | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold_previous_final_answer | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold_raw_mention | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold_saved_memory | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold_verifier_approved_result | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| wrong_lure_active_task_required | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure_answer_shaped_span | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure_final_answer_commitment | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure_hidden_metadata | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure_majority_consensus | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure_peer_claim | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure_previous_final_answer | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure_raw_mention | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure_saved_memory | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure_verifier_approved_result | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |

## By Content Polarity And Future Signal

| Slice | Records | EM | Avg F1 | Exact uptake | Substring uptake | Avg injected F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| correct_gold | -1 | hidden_metadata | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold | 0 | raw_mention | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold | 1 | answer_shaped_span | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold | 2 | peer_claim | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold | 3 | majority_consensus | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold | 4 | previous_final_answer | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold | 5 | verifier_approved_result | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold | 6 | saved_memory | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold | 7 | active_task_required | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| correct_gold | 8 | final_answer_commitment | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| none |  | none | 24 | 1.000 | 1.000 | n/a | n/a | n/a |
| wrong_lure | -1 | hidden_metadata | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure | 0 | raw_mention | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure | 1 | answer_shaped_span | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure | 2 | peer_claim | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure | 3 | majority_consensus | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure | 4 | previous_final_answer | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure | 5 | verifier_approved_result | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure | 6 | saved_memory | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure | 7 | active_task_required | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |
| wrong_lure | 8 | final_answer_commitment | 24 | 1.000 | 1.000 | 0.000 | 0.583 | 0.204 |

## Paired Deltas By Ladder Level

| Slice | Records | Base-right | Base-wrong | Outcomes | F1 delta | AVR | AUR | Utility |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| correct_gold | -1 | hidden_metadata | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| correct_gold | 0 | raw_mention | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| correct_gold | 1 | answer_shaped_span | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| correct_gold | 2 | peer_claim | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| correct_gold | 3 | majority_consensus | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| correct_gold | 4 | previous_final_answer | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| correct_gold | 5 | verifier_approved_result | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| correct_gold | 6 | saved_memory | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| correct_gold | 7 | active_task_required | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| correct_gold | 8 | final_answer_commitment | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| wrong_lure | -1 | hidden_metadata | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| wrong_lure | 0 | raw_mention | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| wrong_lure | 1 | answer_shaped_span | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| wrong_lure | 2 | peer_claim | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| wrong_lure | 3 | majority_consensus | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| wrong_lure | 4 | previous_final_answer | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| wrong_lure | 5 | verifier_approved_result | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| wrong_lure | 6 | saved_memory | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| wrong_lure | 7 | active_task_required | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |
| wrong_lure | 8 | final_answer_commitment | 24 | 24 | 0 | `{'stable_right': 24}` | 0.000 | 0.000 | 0.000 | n/a |

## Wrong-Lure Authority By Future Level

| Slice | Wrong rows | Base-right | Violations | AVR | Uptake | AUR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| -1 | hidden_metadata | 24 | 24 | 0 | 0.000 | 0 | 0.000 |
| 0 | raw_mention | 24 | 24 | 0 | 0.000 | 0 | 0.000 |
| 1 | answer_shaped_span | 24 | 24 | 0 | 0.000 | 0 | 0.000 |
| 2 | peer_claim | 24 | 24 | 0 | 0.000 | 0 | 0.000 |
| 3 | majority_consensus | 24 | 24 | 0 | 0.000 | 0 | 0.000 |
| 4 | previous_final_answer | 24 | 24 | 0 | 0.000 | 0 | 0.000 |
| 5 | verifier_approved_result | 24 | 24 | 0 | 0.000 | 0 | 0.000 |
| 6 | saved_memory | 24 | 24 | 0 | 0.000 | 0 | 0.000 |
| 7 | active_task_required | 24 | 24 | 0 | 0.000 | 0 | 0.000 |
| 8 | final_answer_commitment | 24 | 24 | 0 | 0.000 | 0 | 0.000 |

## Wrong-Lure Authority By Semantic Family And Future Signal

| Slice | Wrong rows | Base-right | Violations | AVR | Uptake | AUR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| answer_type_projection | -1 | hidden_metadata | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 0 | raw_mention | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 1 | answer_shaped_span | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 2 | peer_claim | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 3 | majority_consensus | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 4 | previous_final_answer | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 5 | verifier_approved_result | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 6 | saved_memory | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 7 | active_task_required | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| answer_type_projection | 8 | final_answer_commitment | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| evidence_or_content_failure | -1 | hidden_metadata | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| evidence_or_content_failure | 0 | raw_mention | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| evidence_or_content_failure | 1 | answer_shaped_span | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| evidence_or_content_failure | 2 | peer_claim | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| evidence_or_content_failure | 3 | majority_consensus | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| evidence_or_content_failure | 4 | previous_final_answer | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| evidence_or_content_failure | 5 | verifier_approved_result | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| evidence_or_content_failure | 6 | saved_memory | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| evidence_or_content_failure | 7 | active_task_required | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| evidence_or_content_failure | 8 | final_answer_commitment | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | -1 | hidden_metadata | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 0 | raw_mention | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 1 | answer_shaped_span | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 2 | peer_claim | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 3 | majority_consensus | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 4 | previous_final_answer | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 5 | verifier_approved_result | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 6 | saved_memory | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 7 | active_task_required | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| evidence_sentence_or_distractor | 8 | final_answer_commitment | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| final_candidate_attractor | -1 | hidden_metadata | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| final_candidate_attractor | 0 | raw_mention | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| final_candidate_attractor | 1 | answer_shaped_span | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| final_candidate_attractor | 2 | peer_claim | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| final_candidate_attractor | 3 | majority_consensus | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| final_candidate_attractor | 4 | previous_final_answer | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| final_candidate_attractor | 5 | verifier_approved_result | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| final_candidate_attractor | 6 | saved_memory | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| final_candidate_attractor | 7 | active_task_required | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
| final_candidate_attractor | 8 | final_answer_commitment | 1 | 1 | 0 | 0.000 | 0 | 0.000 |
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
| public_target_misdirection | 2 | peer_claim | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| public_target_misdirection | 3 | majority_consensus | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| public_target_misdirection | 4 | previous_final_answer | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| public_target_misdirection | 5 | verifier_approved_result | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| public_target_misdirection | 6 | saved_memory | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| public_target_misdirection | 7 | active_task_required | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| public_target_misdirection | 8 | final_answer_commitment | 3 | 3 | 0 | 0.000 | 0 | 0.000 |
| question_root_boundary_regression | -1 | hidden_metadata | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| question_root_boundary_regression | 0 | raw_mention | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| question_root_boundary_regression | 1 | answer_shaped_span | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| question_root_boundary_regression | 2 | peer_claim | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| question_root_boundary_regression | 3 | majority_consensus | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| question_root_boundary_regression | 4 | previous_final_answer | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| question_root_boundary_regression | 5 | verifier_approved_result | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| question_root_boundary_regression | 6 | saved_memory | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| question_root_boundary_regression | 7 | active_task_required | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| question_root_boundary_regression | 8 | final_answer_commitment | 2 | 2 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | -1 | hidden_metadata | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 0 | raw_mention | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 1 | answer_shaped_span | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 2 | peer_claim | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 3 | majority_consensus | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 4 | previous_final_answer | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 5 | verifier_approved_result | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 6 | saved_memory | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 7 | active_task_required | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
| short_span_or_granularity | 8 | final_answer_commitment | 6 | 6 | 0 | 0.000 | 0 | 0.000 |
