# MATH Authority Genesis Ladder Evaluation

- Prediction source: `gold`
- Records: `117`
- Known semantic accuracy: `1.000`
- Semantic unknown: `0`

## By Variant

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_previous_solution | 13 | 1.000 | 0 | 0.000 | n/a | n/a |
| control_self_revision_no_sender | 13 | 1.000 | 0 | 0.000 | n/a | n/a |
| control_unrelated_sender_message | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__admission_rejected_quarantine | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__peer_message_direct | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__sender_private_scratch_visible_inert | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__shared_workspace_admitted | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__typed_partial_derivation_requires_rederive | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__verifier_admitted_result | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |

## By Artifact Type And Future Signal

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  |  | none | 13 | 1.000 | 0 | 0.000 | n/a | n/a |
|  | -2 | control_self_revision_no_sender | 13 | 1.000 | 0 | 0.000 | n/a | n/a |
| live_sender_artifact | -1 | control_unrelated_sender_message | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 0 | peer_message_direct | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 2 | shared_workspace_admitted | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 5 | verifier_admitted_result | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 13 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |

## Paired Deltas By Artifact Type And Future Signal

| Slice | Records | Base-right | Outcomes | AVR | Answer uptake | Operator uptake candidate |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| None | -2 | control_self_revision_no_sender | 13 | 13 | `{'stable_right': 13}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 13 | 13 | `{'stable_right': 13}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 13 | 13 | `{'stable_right': 13}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 0 | peer_message_direct | 13 | 13 | `{'stable_right': 13}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 2 | shared_workspace_admitted | 13 | 13 | `{'stable_right': 13}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 5 | verifier_admitted_result | 13 | 13 | `{'stable_right': 13}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 13 | 13 | `{'stable_right': 13}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 13 | 13 | `{'stable_right': 13}` | 0.000 | 0.000 | 0.000 |

## Authority By Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| -1 | control_unrelated_sender_message | 13 | 13 | 0 | 0.000 | 0 | 0 |
| -2 | control_self_revision_no_sender | 13 | 13 | 0 | 0.000 | 0 | 0 |
| -3 | sender_private_scratch_visible_inert | 13 | 13 | 0 | 0.000 | 0 | 0 |
| 0 | peer_message_direct | 13 | 13 | 0 | 0.000 | 0 | 0 |
| 13 | typed_partial_derivation_requires_rederive | 13 | 13 | 0 | 0.000 | 0 | 0 |
| 2 | shared_workspace_admitted | 13 | 13 | 0 | 0.000 | 0 | 0 |
| 5 | verifier_admitted_result | 13 | 13 | 0 | 0.000 | 0 | 0 |
| 6 | admission_rejected_quarantine | 13 | 13 | 0 | 0.000 | 0 | 0 |

## Authority By Artifact Type And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  | -2 | control_self_revision_no_sender | 13 | 13 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 13 | 13 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 13 | 13 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 0 | peer_message_direct | 13 | 13 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 13 | 13 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 2 | shared_workspace_admitted | 13 | 13 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 5 | verifier_admitted_result | 13 | 13 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 13 | 13 | 0 | 0.000 | 0 | 0 |

## Authority By Source Surface And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| math200_live_sender_artifact | -1 | control_unrelated_sender_message | 13 | 13 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | -2 | control_self_revision_no_sender | 13 | 13 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | -3 | sender_private_scratch_visible_inert | 13 | 13 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | 0 | peer_message_direct | 13 | 13 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 13 | 13 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | 2 | shared_workspace_admitted | 13 | 13 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | 5 | verifier_admitted_result | 13 | 13 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | 6 | admission_rejected_quarantine | 13 | 13 | 0 | 0.000 | 0 | 0 |
