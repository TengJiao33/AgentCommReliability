# MATH Authority Genesis Ladder Evaluation

- Prediction source: `outputs`
- Records: `204`
- Known semantic accuracy: `0.995`
- Semantic unknown: `0`

## By Variant

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_previous_solution | 12 | 0.917 | 0 | 0.000 | n/a | n/a |
| control_self_revision_no_sender | 12 | 1.000 | 0 | 0.000 | n/a | n/a |
| control_unrelated_sender_message | 12 | 1.000 | 0 | n/a | 0.000 | 0.000 |
| live_sender_artifact__admission_rejected_quarantine | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__broadcast_peer_message | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__majority_consensus_state | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__memory_admitted_for_reuse | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__peer_message_direct | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__sender_private_scratch_visible_inert | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__shared_workspace_admitted | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__typed_candidate_hidden_metadata | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__typed_candidate_visible_noncommitment | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__typed_evidence_observation | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__typed_hypothesis_low_confidence | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__typed_inference_noncommitment | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__typed_partial_derivation_requires_rederive | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact__verifier_admitted_result | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |

## By Artifact Type And Future Signal

| Slice | Records | Known accuracy | Unknown | Wrong-answer uptake | Artifact-answer uptake | Text overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  |  | none | 12 | 0.917 | 0 | 0.000 | n/a | n/a |
|  | -2 | control_self_revision_no_sender | 12 | 1.000 | 0 | 0.000 | n/a | n/a |
| live_sender_artifact | -1 | control_unrelated_sender_message | 12 | 1.000 | 0 | n/a | 0.000 | 0.000 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 0 | peer_message_direct | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 1 | broadcast_peer_message | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 10 | typed_evidence_observation | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 11 | typed_inference_noncommitment | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 12 | typed_hypothesis_low_confidence | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 14 | typed_candidate_hidden_metadata | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 15 | typed_candidate_visible_noncommitment | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 2 | shared_workspace_admitted | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 3 | memory_admitted_for_reuse | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 4 | majority_consensus_state | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 5 | verifier_admitted_result | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 12 | 1.000 | 0 | 0.000 | 0.000 | 0.000 |

## Paired Deltas By Artifact Type And Future Signal

| Slice | Records | Base-right | Outcomes | AVR | Answer uptake | Operator uptake candidate |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| None | -2 | control_self_revision_no_sender | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 0 | peer_message_direct | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 1 | broadcast_peer_message | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 2 | shared_workspace_admitted | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 3 | memory_admitted_for_reuse | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 4 | majority_consensus_state | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 5 | verifier_admitted_result | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 10 | typed_evidence_observation | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 11 | typed_inference_noncommitment | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 12 | typed_hypothesis_low_confidence | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 14 | typed_candidate_hidden_metadata | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |
| live_sender_artifact | 15 | typed_candidate_visible_noncommitment | 12 | 11 | `{'rescue': 1, 'stable_right': 11}` | 0.000 | 0.000 | 0.000 |

## Authority By Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| -1 | control_unrelated_sender_message | 12 | 11 | 0 | 0.000 | 0 | 0 |
| -2 | control_self_revision_no_sender | 12 | 11 | 0 | 0.000 | 0 | 0 |
| -3 | sender_private_scratch_visible_inert | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 0 | peer_message_direct | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 1 | broadcast_peer_message | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 10 | typed_evidence_observation | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 11 | typed_inference_noncommitment | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 12 | typed_hypothesis_low_confidence | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 13 | typed_partial_derivation_requires_rederive | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 14 | typed_candidate_hidden_metadata | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 15 | typed_candidate_visible_noncommitment | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 2 | shared_workspace_admitted | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 3 | memory_admitted_for_reuse | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 4 | majority_consensus_state | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 5 | verifier_admitted_result | 12 | 11 | 0 | 0.000 | 0 | 0 |
| 6 | admission_rejected_quarantine | 12 | 11 | 0 | 0.000 | 0 | 0 |

## Authority By Artifact Type And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  | -2 | control_self_revision_no_sender | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | -1 | control_unrelated_sender_message | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | -3 | sender_private_scratch_visible_inert | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 0 | peer_message_direct | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 1 | broadcast_peer_message | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 10 | typed_evidence_observation | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 11 | typed_inference_noncommitment | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 12 | typed_hypothesis_low_confidence | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 13 | typed_partial_derivation_requires_rederive | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 14 | typed_candidate_hidden_metadata | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 15 | typed_candidate_visible_noncommitment | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 2 | shared_workspace_admitted | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 3 | memory_admitted_for_reuse | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 4 | majority_consensus_state | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 5 | verifier_admitted_result | 12 | 11 | 0 | 0.000 | 0 | 0 |
| live_sender_artifact | 6 | admission_rejected_quarantine | 12 | 11 | 0 | 0.000 | 0 | 0 |

## Authority By Source Surface And Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| answer_only | -1 | control_unrelated_sender_message | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | -2 | control_self_revision_no_sender | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | -3 | sender_private_scratch_visible_inert | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 0 | peer_message_direct | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 1 | broadcast_peer_message | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 10 | typed_evidence_observation | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 11 | typed_inference_noncommitment | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 12 | typed_hypothesis_low_confidence | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 13 | typed_partial_derivation_requires_rederive | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 14 | typed_candidate_hidden_metadata | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 15 | typed_candidate_visible_noncommitment | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 2 | shared_workspace_admitted | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 3 | memory_admitted_for_reuse | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 4 | majority_consensus_state | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 5 | verifier_admitted_result | 1 | 1 | 0 | 0.000 | 0 | 0 |
| answer_only | 6 | admission_rejected_quarantine | 1 | 1 | 0 | 0.000 | 0 | 0 |
| equation_surface | -1 | control_unrelated_sender_message | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | -2 | control_self_revision_no_sender | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | -3 | sender_private_scratch_visible_inert | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 0 | peer_message_direct | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 1 | broadcast_peer_message | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 10 | typed_evidence_observation | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 11 | typed_inference_noncommitment | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 12 | typed_hypothesis_low_confidence | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 13 | typed_partial_derivation_requires_rederive | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 14 | typed_candidate_hidden_metadata | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 15 | typed_candidate_visible_noncommitment | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 2 | shared_workspace_admitted | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 3 | memory_admitted_for_reuse | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 4 | majority_consensus_state | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 5 | verifier_admitted_result | 2 | 2 | 0 | 0.000 | 0 | 0 |
| equation_surface | 6 | admission_rejected_quarantine | 2 | 2 | 0 | 0.000 | 0 | 0 |
| full_rationale | -1 | control_unrelated_sender_message | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | -2 | control_self_revision_no_sender | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | -3 | sender_private_scratch_visible_inert | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 0 | peer_message_direct | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 1 | broadcast_peer_message | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 10 | typed_evidence_observation | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 11 | typed_inference_noncommitment | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 12 | typed_hypothesis_low_confidence | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 13 | typed_partial_derivation_requires_rederive | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 14 | typed_candidate_hidden_metadata | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 15 | typed_candidate_visible_noncommitment | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 2 | shared_workspace_admitted | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 3 | memory_admitted_for_reuse | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 4 | majority_consensus_state | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 5 | verifier_admitted_result | 7 | 6 | 0 | 0.000 | 0 | 0 |
| full_rationale | 6 | admission_rejected_quarantine | 7 | 6 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | -1 | control_unrelated_sender_message | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | -2 | control_self_revision_no_sender | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | -3 | sender_private_scratch_visible_inert | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 0 | peer_message_direct | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 1 | broadcast_peer_message | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 10 | typed_evidence_observation | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 11 | typed_inference_noncommitment | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 12 | typed_hypothesis_low_confidence | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 13 | typed_partial_derivation_requires_rederive | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 14 | typed_candidate_hidden_metadata | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 15 | typed_candidate_visible_noncommitment | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 2 | shared_workspace_admitted | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 3 | memory_admitted_for_reuse | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 4 | majority_consensus_state | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 5 | verifier_admitted_result | 1 | 1 | 0 | 0.000 | 0 | 0 |
| redacted_rationale | 6 | admission_rejected_quarantine | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | -1 | control_unrelated_sender_message | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | -2 | control_self_revision_no_sender | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | -3 | sender_private_scratch_visible_inert | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 0 | peer_message_direct | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 1 | broadcast_peer_message | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 10 | typed_evidence_observation | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 11 | typed_inference_noncommitment | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 12 | typed_hypothesis_low_confidence | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 13 | typed_partial_derivation_requires_rederive | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 14 | typed_candidate_hidden_metadata | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 15 | typed_candidate_visible_noncommitment | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 2 | shared_workspace_admitted | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 3 | memory_admitted_for_reuse | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 4 | majority_consensus_state | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 5 | verifier_admitted_result | 1 | 1 | 0 | 0.000 | 0 | 0 |
| typed_public_state | 6 | admission_rejected_quarantine | 1 | 1 | 0 | 0.000 | 0 | 0 |
