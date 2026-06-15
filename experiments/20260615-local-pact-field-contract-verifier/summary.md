# PACT Field-Contract Verifier Audit

- Source units: `100`
- Generated packet rows: `400`
- Target actions: `{'freeze': 33, 'keep': 67}`
- Candidate actions: `{'hide': 9, 'show': 91}`

## Offline Routing Scores

| Slice | Records | EM | Avg F1 | Chosen conditions |
| --- | ---: | ---: | ---: | --- |
| always_base_public_state | 100 | 0.520 | 0.688 | `question_plus_public_state_no_final`=100 |
| always_hide_public_target | 100 | 0.590 | 0.725 | `question_plus_evidence_no_target_no_final`=100 |
| always_freeze_question_target | 100 | 0.580 | 0.734 | `frozen_target_plus_evidence_no_final`=100 |
| always_show_final_candidate | 100 | 0.550 | 0.710 | `question_plus_public_state_with_final`=100 |
| verifier_freeze_risky_else_base | 100 | 0.540 | 0.685 | `frozen_target_plus_evidence_no_final`=33, `question_plus_public_state_no_final`=67 |
| verifier_hide_risky_else_base | 100 | 0.570 | 0.710 | `question_plus_evidence_no_target_no_final`=33, `question_plus_public_state_no_final`=67 |
| verifier_hide_risky_else_freeze | 100 | 0.610 | 0.759 | `frozen_target_plus_evidence_no_final`=67, `question_plus_evidence_no_target_no_final`=33 |
| verifier_licensed_final_else_freeze | 100 | 0.540 | 0.683 | `frozen_target_plus_evidence_no_final`=5, `question_plus_public_state_no_final`=4, `question_plus_public_state_with_final`=91 |
| verifier_licensed_final_else_hide | 100 | 0.550 | 0.689 | `question_plus_evidence_no_target_no_final`=5, `question_plus_public_state_no_final`=4, `question_plus_public_state_with_final`=91 |

## Condition Counts

| Condition | Rows |
| --- | ---: |
| `verified_freeze_on_risk_no_final` | 100 |
| `verified_freeze_with_licensed_final` | 100 |
| `verified_hide_risky_target_no_final` | 100 |
| `verified_quarantine_risky_else_frozen_no_final` | 100 |

## Target Reasons

| Reason | Count |
| --- | ---: |
| `generic_low_overlap_target` | 14 |
| `kept` | 67 |
| `target_slot_drift_candidate` | 16 |
| `under_specified_target` | 18 |

## Candidate Reasons

| Reason | Count |
| --- | ---: |
| `candidate_not_concise` | 7 |
| `candidate_restates_question` | 5 |
| `low_evidence_support` | 8 |
| `shown` | 88 |
