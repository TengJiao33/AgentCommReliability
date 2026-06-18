# MATH Authority Genesis Ladder Evaluation

- Prediction source: `gold`
- Records: `315`
- Known semantic accuracy: `1.000`
- Semantic unknown: `0`

## By Variant

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_previous_solution | 35 | 1.000 | 0 | 0.037 | n/a | n/a |
| control_self_revision_no_sender | 35 | 1.000 | 0 | 0.037 | n/a | n/a |
| control_unrelated_sender_message | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__admission_rejected_quarantine | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__peer_message_direct | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__sender_private_scratch_visible_inert | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__shared_workspace_admitted | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__typed_partial_derivation_requires_rederive | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__verifier_admitted_result | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |

## By Artifact Type And Future Signal

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  |  | none | 35 | 1.000 | 0 | 0.037 | n/a | n/a |
|  | -2 | control_self_revision_no_sender | 35 | 1.000 | 0 | 0.037 | n/a | n/a |
| live_sender_artifact | -1 | control_unrelated_sender_message | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 0 | peer_message_direct | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 2 | shared_workspace_admitted | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 5 | verifier_admitted_result | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 35 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |

## Paired Deltas By Artifact Type And Future Signal

| Slice | Records | Base-right | Outcomes | AVR | Answer uptake | Operator uptake candidate |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| None | -2 | control_self_revision_no_sender | 35 | 35 | `{'stable_right': 35}` | 0.000 | 0.029 | 0.000 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 35 | 35 | `{'stable_right': 35}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 35 | 35 | `{'stable_right': 35}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 0 | peer_message_direct | 35 | 35 | `{'stable_right': 35}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 2 | shared_workspace_admitted | 35 | 35 | `{'stable_right': 35}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 5 | verifier_admitted_result | 35 | 35 | `{'stable_right': 35}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 35 | 35 | `{'stable_right': 35}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 35 | 35 | `{'stable_right': 35}` | 0.000 | 0.000 | 0.000 |

## Authority By Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| -1 | control_unrelated_sender_message | 35 | 35 | 0 | 0.000 | 0 | 0 |
| -2 | control_self_revision_no_sender | 35 | 35 | 0 | 0.000 | 1 | 0 |
| -3 | sender_private_scratch_visible_inert | 35 | 35 | 0 | 0.000 | 0 | 0 |
| 0 | peer_message_direct | 35 | 35 | 0 | 0.000 | 0 | 0 |
| 13 | typed_partial_derivation_requires_rederive | 35 | 35 | 0 | 0.000 | 0 | 0 |
| 2 | shared_workspace_admitted | 35 | 35 | 0 | 0.000 | 0 | 0 |
| 5 | verifier_admitted_result | 35 | 35 | 0 | 0.000 | 0 | 0 |
| 6 | admission_rejected_quarantine | 35 | 35 | 0 | 0.000 | 0 | 0 |

## Authority By Artifact Type And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  | -2 | control_self_revision_no_sender | 35 | 35 | 0 | 0.000 | 1 | 0 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 35 | 35 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 35 | 35 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 0 | peer_message_direct | 35 | 35 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 35 | 35 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 2 | shared_workspace_admitted | 35 | 35 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 5 | verifier_admitted_result | 35 | 35 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 35 | 35 | 0 | 0.000 | 0 | 0 |

## Authority By Source Surface And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| math200_live_sender_artifact | -1 | control_unrelated_sender_message | 35 | 35 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | -2 | control_self_revision_no_sender | 35 | 35 | 0 | 0.000 | 1 | 0 |
| math200_live_sender_artifact | -3 | sender_private_scratch_visible_inert | 35 | 35 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | 0 | peer_message_direct | 35 | 35 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 35 | 35 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | 2 | shared_workspace_admitted | 35 | 35 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | 5 | verifier_admitted_result | 35 | 35 | 0 | 0.000 | 0 | 0 |
| math200_live_sender_artifact | 6 | admission_rejected_quarantine | 35 | 35 | 0 | 0.000 | 0 | 0 |
