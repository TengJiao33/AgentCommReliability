# MATH Authority Genesis Ladder Evaluation

- Prediction source: `outputs`
- Records: `450`
- Known semantic accuracy: `0.709`
- Semantic unknown: `103`

## By Variant

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_previous_solution | 50 | 0.757 | 13 | 0.107 | n/a | n/a |
| control_self_revision_no_sender | 50 | 0.763 | 12 | 0.071 | n/a | n/a |
| control_unrelated_sender_message | 50 | 0.718 | 11 | n/a | 0.000 | 0.000 |
| live_sender_artifact__admission_rejected_quarantine | 50 | 0.675 | 10 | 0.333 | 0.000 | 0.000 |
| live_sender_artifact__peer_message_direct | 50 | 0.675 | 10 | 0.476 | 0.000 | 0.000 |
| live_sender_artifact__sender_private_scratch_visible_inert | 50 | 0.730 | 13 | 0.429 | 0.000 | 0.000 |
| live_sender_artifact__shared_workspace_admitted | 50 | 0.675 | 10 | 0.381 | 0.000 | 0.000 |
| live_sender_artifact__typed_partial_derivation_requires_rederive | 50 | 0.718 | 11 | 0.286 | 0.000 | 0.000 |
| live_sender_artifact__verifier_admitted_result | 50 | 0.676 | 13 | 0.381 | 0.000 | 0.000 |

## By Artifact Type And Future Signal

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  |  | none | 50 | 0.757 | 13 | 0.107 | n/a | n/a |
|  | -2 | control_self_revision_no_sender | 50 | 0.763 | 12 | 0.071 | n/a | n/a |
| live_sender_artifact | -1 | control_unrelated_sender_message | 50 | 0.718 | 11 | n/a | 0.000 | 0.000 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 50 | 0.730 | 13 | 0.429 | 0.000 | 0.000 |
| live_sender_artifact | 0 | peer_message_direct | 50 | 0.675 | 10 | 0.476 | 0.000 | 0.000 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 50 | 0.718 | 11 | 0.286 | 0.000 | 0.000 |
| live_sender_artifact | 2 | shared_workspace_admitted | 50 | 0.675 | 10 | 0.381 | 0.000 | 0.000 |
| live_sender_artifact | 5 | verifier_admitted_result | 50 | 0.676 | 13 | 0.381 | 0.000 | 0.000 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 50 | 0.675 | 10 | 0.333 | 0.000 | 0.000 |

## Paired Deltas By Artifact Type And Future Signal

| Slice | Records | Base-right | Outcomes | AVR | Answer uptake | Operator uptake candidate |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| None | -2 | control_self_revision_no_sender | 50 | 28 | `{'rescue': 1, 'stable_right': 28, 'stable_wrong': 8, 'unknown': 13}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 50 | 28 | `{'authority_violation': 1, 'stable_right': 27, 'stable_wrong': 7, 'unknown': 15}` | 0.036 | 0.071 | 0.000 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 50 | 28 | `{'stable_right': 28, 'stable_wrong': 7, 'unknown': 15}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 0 | peer_message_direct | 50 | 28 | `{'authority_violation': 2, 'stable_right': 26, 'stable_wrong': 8, 'unknown': 14}` | 0.071 | 0.107 | 0.000 |
| live_sender_artifact | 2 | shared_workspace_admitted | 50 | 28 | `{'stable_right': 27, 'stable_wrong': 8, 'unknown': 15}` | 0.000 | 0.036 | 0.000 |
| live_sender_artifact | 5 | verifier_admitted_result | 50 | 28 | `{'authority_violation': 2, 'stable_right': 25, 'stable_wrong': 8, 'unknown': 15}` | 0.071 | 0.036 | 0.071 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 50 | 28 | `{'authority_violation': 1, 'stable_right': 27, 'stable_wrong': 9, 'unknown': 13}` | 0.036 | 0.036 | 0.036 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 50 | 28 | `{'authority_violation': 1, 'stable_right': 27, 'stable_wrong': 9, 'unknown': 13}` | 0.036 | 0.036 | 0.036 |

## Authority By Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| -1 | control_unrelated_sender_message | 50 | 28 | 0 | 0.000 | 0 | 0 |
| -2 | control_self_revision_no_sender | 50 | 28 | 0 | 0.000 | 0 | 0 |
| -3 | sender_private_scratch_visible_inert | 50 | 28 | 1 | 0.036 | 2 | 0 |
| 0 | peer_message_direct | 50 | 28 | 2 | 0.071 | 3 | 0 |
| 13 | typed_partial_derivation_requires_rederive | 50 | 28 | 1 | 0.036 | 1 | 1 |
| 2 | shared_workspace_admitted | 50 | 28 | 0 | 0.000 | 1 | 0 |
| 5 | verifier_admitted_result | 50 | 28 | 2 | 0.071 | 1 | 2 |
| 6 | admission_rejected_quarantine | 50 | 28 | 1 | 0.036 | 1 | 1 |

## Authority By Artifact Type And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  | -2 | control_self_revision_no_sender | 50 | 28 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 50 | 28 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 50 | 28 | 1 | 0.036 | 2 | 0 |
| live_sender_artifact | 0 | peer_message_direct | 50 | 28 | 2 | 0.071 | 3 | 0 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 50 | 28 | 1 | 0.036 | 1 | 1 |
| live_sender_artifact | 2 | shared_workspace_admitted | 50 | 28 | 0 | 0.000 | 1 | 0 |
| live_sender_artifact | 5 | verifier_admitted_result | 50 | 28 | 2 | 0.071 | 1 | 2 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 50 | 28 | 1 | 0.036 | 1 | 1 |

## Authority By Source Surface And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| math200_live_sender_artifact | -1 | control_unrelated_sender_message | 50 | 28 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | -2 | control_self_revision_no_sender | 50 | 28 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | -3 | sender_private_scratch_visible_inert | 50 | 28 | 1 | 0.036 | 2 | 0 |
| math200_live_sender_artifact | 0 | peer_message_direct | 50 | 28 | 2 | 0.071 | 3 | 0 |
| math200_live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 50 | 28 | 1 | 0.036 | 1 | 1 |
| math200_live_sender_artifact | 2 | shared_workspace_admitted | 50 | 28 | 0 | 0.000 | 1 | 0 |
| math200_live_sender_artifact | 5 | verifier_admitted_result | 50 | 28 | 2 | 0.071 | 1 | 2 |
| math200_live_sender_artifact | 6 | admission_rejected_quarantine | 50 | 28 | 1 | 0.036 | 1 | 1 |
