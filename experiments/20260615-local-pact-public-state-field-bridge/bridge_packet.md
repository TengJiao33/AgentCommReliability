# PACT Public-State Field Bridge

## Reading

This is an offline bridge audit over the PACT HotpotQA offset50 focus cases.
It reframes older PACT findings in the same field/slot language used by the peer-message work.

Main read: the object is not typed public state itself. The object is field-level public-state reliability: preserve the target contract, carry evidence without distractor migration, and commit the final answer to the requested slot and granularity.

## Sources

- `experiments\20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired\case_atlas_focus_cases.jsonl`
- `experiments\20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired\public_state_gold_manual_labels.jsonl`
- `experiments\20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired\target_slot_drift_cases.jsonl`

## Counts

- Focus cases: `28`
- Manual public-state-gold labels merged: `10`
- Target-slot drift candidates merged: `8`

| Bridge layer | Count | Samples |
| --- | --- | --- |
| diagnostic_noise | 1 | 59 |
| evidence_carriage | 5 | 68, 71, 77, 88, 94 |
| final_answer_commitment | 12 | 50, 54, 55, 62, 64, 66, 74, 83, 87, 89, 92, 97 |
| positive_contract_rescue | 6 | 57, 61, 78, 85, 93, 99 |
| target_contract | 2 | 58, 82 |
| target_final_alignment | 2 | 60, 67 |

| Bridge family | Count | Samples |
| --- | --- | --- |
| alias_or_name_granularity | 1 | 74 |
| contract_rescued_content_or_field | 1 | 61 |
| contract_rescued_verbose_surface | 5 | 57, 78, 85, 93, 99 |
| false_positive_string_signal | 1 | 59 |
| likely_evidence_or_reasoning_failure | 5 | 68, 71, 77, 88, 94 |
| missing_required_token_or_qualifier | 3 | 50, 55, 83 |
| near_miss_surface_or_span | 1 | 97 |
| over_specific_answer | 3 | 87, 89, 92 |
| recoverable_from_public_state_policy | 1 | 62 |
| strict_span_regression | 2 | 64, 66 |
| strict_span_regression_with_soft_target_shift | 1 | 54 |
| target_migration_regression | 1 | 58 |
| target_under_specification_or_anchor_loss | 1 | 82 |
| wrong_answer_type_or_slot | 2 | 60, 67 |

## Target Candidates

| Sample | Transition | Bridge family | Reasons |
| --- | --- | --- | --- |
| 54 | right_to_wrong | strict_span_regression_with_soft_target_shift | new_anchor_loss, large_overlap_drop, low_variant_overlap, slot_term_replacement |
| 55 | stable_wrong | missing_required_token_or_qualifier | new_anchor_loss |
| 58 | right_to_wrong | target_migration_regression | new_anchor_loss, large_overlap_drop, slot_term_replacement |
| 60 | stable_wrong | wrong_answer_type_or_slot | new_anchor_loss, large_overlap_drop, low_variant_overlap |
| 82 | stable_wrong | target_under_specification_or_anchor_loss | new_anchor_loss, large_overlap_drop |
| 83 | stable_wrong | missing_required_token_or_qualifier | new_anchor_loss |
| 87 | stable_wrong | over_specific_answer | new_anchor_loss, large_overlap_drop, low_variant_overlap |
| 89 | stable_wrong | over_specific_answer | new_anchor_loss, large_overlap_drop, low_variant_overlap |

## Manual Public-State-Gold Cases

| Sample | Manual family | Bridge layer | Bridge family |
| --- | --- | --- | --- |
| 50 | missing_required_token_or_qualifier | final_answer_commitment | missing_required_token_or_qualifier |
| 55 | missing_required_token_or_qualifier | final_answer_commitment | missing_required_token_or_qualifier |
| 59 | false_positive_string_signal | diagnostic_noise | false_positive_string_signal |
| 60 | wrong_answer_type_or_slot | target_final_alignment | wrong_answer_type_or_slot |
| 67 | wrong_answer_type_or_slot | target_final_alignment | wrong_answer_type_or_slot |
| 74 | alias_or_name_granularity | final_answer_commitment | alias_or_name_granularity |
| 83 | missing_required_token_or_qualifier | final_answer_commitment | missing_required_token_or_qualifier |
| 87 | over_specific_answer | final_answer_commitment | over_specific_answer |
| 89 | over_specific_answer | final_answer_commitment | over_specific_answer |
| 92 | over_specific_answer | final_answer_commitment | over_specific_answer |

## Implication

The useful next move is a communication-necessity benchmark or intervention around field preservation, not another small typed/MATH variant. PACT already gives the larger surface: information is split, public fields are passed across agents, and failures happen at target, evidence, and final-commitment layers.

## Caveats

- This is a re-read of one saved 50-sample PACT slice, not a new model result.
- Bridge labels combine mechanical atlas labels, a ten-case manual audit, and a lexical target-slot diagnostic.
- Target-slot candidates remain heuristic; sample-level labels are inspection handles, not final taxonomy.
