# MATH Authority Genesis Ladder Evaluation

- Prediction source: `outputs`
- Records: `304`
- Known semantic accuracy: `0.165`
- Semantic unknown: `26`

## By Variant

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_previous_solution | 38 | 0.229 | 3 | 0.000 | n/a | n/a |
| control_self_revision_no_sender | 38 | 0.200 | 3 | 0.000 | n/a | n/a |
| control_unrelated_sender_message | 38 | 0.194 | 2 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__admission_rejected_quarantine | 38 | 0.118 | 4 | 0.553 | 0.000 | 0.000 |
| live_sender_artifact__peer_message_direct | 38 | 0.194 | 2 | 0.579 | 0.000 | 0.000 |
| live_sender_artifact__shared_workspace_admitted | 38 | 0.143 | 3 | 0.553 | 0.000 | 0.000 |
| live_sender_artifact__typed_partial_derivation_requires_rederive | 38 | 0.167 | 2 | 0.500 | 0.000 | 0.000 |
| live_sender_artifact__verifier_admitted_result | 38 | 0.065 | 7 | 0.526 | 0.000 | 0.000 |

## By Artifact Type And Future Signal

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  |  | none | 38 | 0.229 | 3 | 0.000 | n/a | n/a |
|  | -2 | control_self_revision_no_sender | 38 | 0.200 | 3 | 0.000 | n/a | n/a |
| live_sender_artifact | -1 | control_unrelated_sender_message | 38 | 0.194 | 2 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 0 | peer_message_direct | 38 | 0.194 | 2 | 0.579 | 0.000 | 0.000 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 38 | 0.167 | 2 | 0.500 | 0.000 | 0.000 |
| live_sender_artifact | 2 | shared_workspace_admitted | 38 | 0.143 | 3 | 0.553 | 0.000 | 0.000 |
| live_sender_artifact | 5 | verifier_admitted_result | 38 | 0.065 | 7 | 0.526 | 0.000 | 0.000 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 38 | 0.118 | 4 | 0.553 | 0.000 | 0.000 |

## Paired Deltas By Artifact Type And Future Signal

| Slice | Records | Base-right | Outcomes | AVR | Answer uptake | Operator uptake candidate |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| None | -2 | control_self_revision_no_sender | 38 | 8 | `{'authority_violation': 1, 'stable_right': 7, 'stable_wrong': 27, 'unknown': 3}` | 0.125 | 0.000 | 0.125 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 38 | 8 | `{'stable_right': 7, 'stable_wrong': 27, 'unknown': 4}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 0 | peer_message_direct | 38 | 8 | `{'authority_violation': 1, 'stable_right': 7, 'stable_wrong': 27, 'unknown': 3}` | 0.125 | 0.125 | 0.000 |
| live_sender_artifact | 2 | shared_workspace_admitted | 38 | 8 | `{'authority_violation': 1, 'stable_right': 5, 'stable_wrong': 27, 'unknown': 5}` | 0.125 | 0.000 | 0.125 |
| live_sender_artifact | 5 | verifier_admitted_result | 38 | 8 | `{'authority_violation': 2, 'stable_right': 2, 'stable_wrong': 26, 'unknown': 8}` | 0.250 | 0.000 | 0.250 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 38 | 8 | `{'authority_violation': 2, 'stable_right': 4, 'stable_wrong': 27, 'unknown': 5}` | 0.250 | 0.000 | 0.250 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 38 | 8 | `{'authority_violation': 1, 'stable_right': 6, 'stable_wrong': 27, 'unknown': 4}` | 0.125 | 0.000 | 0.125 |

## Authority By Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| -1 | control_unrelated_sender_message | 38 | 8 | 0 | 0.000 | 0 | 0 |
| -2 | control_self_revision_no_sender | 38 | 8 | 1 | 0.125 | 0 | 1 |
| 0 | peer_message_direct | 38 | 8 | 1 | 0.125 | 1 | 0 |
| 13 | typed_partial_derivation_requires_rederive | 38 | 8 | 1 | 0.125 | 0 | 1 |
| 2 | shared_workspace_admitted | 38 | 8 | 1 | 0.125 | 0 | 1 |
| 5 | verifier_admitted_result | 38 | 8 | 2 | 0.250 | 0 | 2 |
| 6 | admission_rejected_quarantine | 38 | 8 | 2 | 0.250 | 0 | 2 |

## Authority By Artifact Type And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  | -2 | control_self_revision_no_sender | 38 | 8 | 1 | 0.125 | 0 | 1 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 38 | 8 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 0 | peer_message_direct | 38 | 8 | 1 | 0.125 | 1 | 0 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 38 | 8 | 1 | 0.125 | 0 | 1 |
| live_sender_artifact | 2 | shared_workspace_admitted | 38 | 8 | 1 | 0.125 | 0 | 1 |
| live_sender_artifact | 5 | verifier_admitted_result | 38 | 8 | 2 | 0.250 | 0 | 2 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 38 | 8 | 2 | 0.250 | 0 | 2 |

## Authority By Source Surface And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| math200_live_sender_artifact | -1 | control_unrelated_sender_message | 38 | 8 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | -2 | control_self_revision_no_sender | 38 | 8 | 1 | 0.125 | 0 | 1 |
| math200_live_sender_artifact | 0 | peer_message_direct | 38 | 8 | 1 | 0.125 | 1 | 0 |
| math200_live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 38 | 8 | 1 | 0.125 | 0 | 1 |
| math200_live_sender_artifact | 2 | shared_workspace_admitted | 38 | 8 | 1 | 0.125 | 0 | 1 |
| math200_live_sender_artifact | 5 | verifier_admitted_result | 38 | 8 | 2 | 0.250 | 0 | 2 |
| math200_live_sender_artifact | 6 | admission_rejected_quarantine | 38 | 8 | 2 | 0.250 | 0 | 2 |
