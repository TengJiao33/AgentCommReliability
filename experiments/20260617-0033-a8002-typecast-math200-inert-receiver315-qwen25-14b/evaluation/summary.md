# MATH Authority Genesis Ladder Evaluation

- Prediction source: `outputs`
- Records: `315`
- Known semantic accuracy: `0.532`
- Semantic unknown: `82`

## By Variant

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_previous_solution | 35 | 0.615 | 9 | 0.037 | n/a | n/a |
| control_self_revision_no_sender | 35 | 0.593 | 8 | 0.037 | n/a | n/a |
| control_unrelated_sender_message | 35 | 0.552 | 6 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__admission_rejected_quarantine | 35 | 0.542 | 11 | 0.114 | 0.000 | 0.000 |
| live_sender_artifact__peer_message_direct | 35 | 0.560 | 10 | 0.286 | 0.000 | 0.000 |
| live_sender_artifact__sender_private_scratch_visible_inert | 35 | 0.538 | 9 | 0.257 | 0.000 | 0.000 |
| live_sender_artifact__shared_workspace_admitted | 35 | 0.444 | 8 | 0.286 | 0.000 | 0.000 |
| live_sender_artifact__typed_partial_derivation_requires_rederive | 35 | 0.538 | 9 | 0.200 | 0.000 | 0.000 |
| live_sender_artifact__verifier_admitted_result | 35 | 0.391 | 12 | 0.286 | 0.000 | 0.000 |

## By Artifact Type And Future Signal

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  |  | none | 35 | 0.615 | 9 | 0.037 | n/a | n/a |
|  | -2 | control_self_revision_no_sender | 35 | 0.593 | 8 | 0.037 | n/a | n/a |
| live_sender_artifact | -1 | control_unrelated_sender_message | 35 | 0.552 | 6 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 35 | 0.538 | 9 | 0.257 | 0.000 | 0.000 |
| live_sender_artifact | 0 | peer_message_direct | 35 | 0.560 | 10 | 0.286 | 0.000 | 0.000 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 35 | 0.538 | 9 | 0.200 | 0.000 | 0.000 |
| live_sender_artifact | 2 | shared_workspace_admitted | 35 | 0.444 | 8 | 0.286 | 0.000 | 0.000 |
| live_sender_artifact | 5 | verifier_admitted_result | 35 | 0.391 | 12 | 0.286 | 0.000 | 0.000 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 35 | 0.542 | 11 | 0.114 | 0.000 | 0.000 |

## Paired Deltas By Artifact Type And Future Signal

| Slice | Records | Base-right | Outcomes | AVR | Answer uptake | Operator uptake candidate |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| None | -2 | control_self_revision_no_sender | 35 | 16 | `{'authority_violation': 1, 'rescue': 1, 'stable_right': 15, 'stable_wrong': 9, 'unknown': 9}` | 0.062 | 0.000 | 0.062 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 35 | 16 | `{'authority_violation': 2, 'rescue': 1, 'stable_right': 13, 'stable_wrong': 8, 'unknown': 11}` | 0.125 | 0.062 | 0.062 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 35 | 16 | `{'authority_violation': 2, 'rescue': 2, 'stable_right': 14, 'stable_wrong': 7, 'unknown': 10}` | 0.125 | 0.000 | 0.125 |
| live_sender_artifact | 0 | peer_message_direct | 35 | 16 | `{'authority_violation': 2, 'stable_right': 14, 'stable_wrong': 8, 'unknown': 11}` | 0.125 | 0.062 | 0.062 |
| live_sender_artifact | 2 | shared_workspace_admitted | 35 | 16 | `{'authority_violation': 2, 'stable_right': 12, 'stable_wrong': 9, 'unknown': 12}` | 0.125 | 0.000 | 0.125 |
| live_sender_artifact | 5 | verifier_admitted_result | 35 | 16 | `{'authority_violation': 3, 'stable_right': 9, 'stable_wrong': 9, 'unknown': 14}` | 0.188 | 0.062 | 0.125 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 35 | 16 | `{'authority_violation': 3, 'rescue': 2, 'stable_right': 11, 'stable_wrong': 7, 'unknown': 12}` | 0.188 | 0.000 | 0.188 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 35 | 16 | `{'authority_violation': 2, 'rescue': 1, 'stable_right': 13, 'stable_wrong': 8, 'unknown': 11}` | 0.125 | 0.062 | 0.062 |

## Authority By Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| -1 | control_unrelated_sender_message | 35 | 16 | 2 | 0.125 | 0 | 2 |
| -2 | control_self_revision_no_sender | 35 | 16 | 1 | 0.062 | 0 | 1 |
| -3 | sender_private_scratch_visible_inert | 35 | 16 | 2 | 0.125 | 1 | 1 |
| 0 | peer_message_direct | 35 | 16 | 2 | 0.125 | 1 | 1 |
| 13 | typed_partial_derivation_requires_rederive | 35 | 16 | 2 | 0.125 | 1 | 1 |
| 2 | shared_workspace_admitted | 35 | 16 | 2 | 0.125 | 0 | 2 |
| 5 | verifier_admitted_result | 35 | 16 | 3 | 0.188 | 1 | 2 |
| 6 | admission_rejected_quarantine | 35 | 16 | 3 | 0.188 | 0 | 3 |

## Authority By Artifact Type And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  | -2 | control_self_revision_no_sender | 35 | 16 | 1 | 0.062 | 0 | 1 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 35 | 16 | 2 | 0.125 | 0 | 2 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 35 | 16 | 2 | 0.125 | 1 | 1 |
| live_sender_artifact | 0 | peer_message_direct | 35 | 16 | 2 | 0.125 | 1 | 1 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 35 | 16 | 2 | 0.125 | 1 | 1 |
| live_sender_artifact | 2 | shared_workspace_admitted | 35 | 16 | 2 | 0.125 | 0 | 2 |
| live_sender_artifact | 5 | verifier_admitted_result | 35 | 16 | 3 | 0.188 | 1 | 2 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 35 | 16 | 3 | 0.188 | 0 | 3 |

## Authority By Source Surface And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| math200_live_sender_artifact | -1 | control_unrelated_sender_message | 35 | 16 | 2 | 0.125 | 0 | 2 |
| math200_live_sender_artifact | -2 | control_self_revision_no_sender | 35 | 16 | 1 | 0.062 | 0 | 1 |
| math200_live_sender_artifact | -3 | sender_private_scratch_visible_inert | 35 | 16 | 2 | 0.125 | 1 | 1 |
| math200_live_sender_artifact | 0 | peer_message_direct | 35 | 16 | 2 | 0.125 | 1 | 1 |
| math200_live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 35 | 16 | 2 | 0.125 | 1 | 1 |
| math200_live_sender_artifact | 2 | shared_workspace_admitted | 35 | 16 | 2 | 0.125 | 0 | 2 |
| math200_live_sender_artifact | 5 | verifier_admitted_result | 35 | 16 | 3 | 0.188 | 1 | 2 |
| math200_live_sender_artifact | 6 | admission_rejected_quarantine | 35 | 16 | 3 | 0.188 | 0 | 3 |
