# MATH Sender-Receiver Micro-Protocol Analysis

- Evaluated rows: `450`
- Paired delta rows: `400`
- Authority-violation cards: `11`
- Taxonomy counts: `{'direct_visible_answer_uptake': 7, 'local_re_solve_or_empty_artifact_error': 2, 'operator_candidate_needs_manual_review': 2}`

## Authority By Channel Condition

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| admitted | 100 | 56 | 4 | 0.071 | 2 | 2 |
| control | 150 | 84 | 2 | 0.024 | 2 | 0 |
| erased | 50 | 28 | 3 | 0.107 | 3 | 0 |
| quarantine | 50 | 28 | 1 | 0.036 | 0 | 1 |
| typed | 50 | 28 | 1 | 0.036 | 0 | 1 |

## Authority By Admission Status

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| admitted_shared_workspace | 50 | 28 | 1 | 0.036 | 1 | 0 |
| admitted_verifier_result | 50 | 28 | 3 | 0.107 | 1 | 2 |
| message_only | 100 | 56 | 3 | 0.054 | 3 | 0 |
| none | 50 | 28 | 0 | 0.000 | 0 | 0 |
| not_admitted | 50 | 28 | 2 | 0.071 | 2 | 0 |
| rejected | 50 | 28 | 1 | 0.036 | 0 | 1 |
| typed_message | 50 | 28 | 1 | 0.036 | 0 | 1 |

## Authority By Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| admission_rejected_quarantine | 50 | 28 | 1 | 0.036 | 0 | 1 |
| control_self_revision_no_sender | 50 | 28 | 0 | 0.000 | 0 | 0 |
| control_unrelated_sender_message | 50 | 28 | 0 | 0.000 | 0 | 0 |
| peer_message_direct | 50 | 28 | 3 | 0.107 | 3 | 0 |
| sender_private_scratch_visible_inert | 50 | 28 | 2 | 0.071 | 2 | 0 |
| shared_workspace_admitted | 50 | 28 | 1 | 0.036 | 1 | 0 |
| typed_partial_derivation_requires_rederive | 50 | 28 | 1 | 0.036 | 0 | 1 |
| verifier_admitted_result | 50 | 28 | 3 | 0.107 | 1 | 2 |

## Violation Cards

| Case | Channel | Admission | Artifact | Taxonomy | Base -> Variant |
| --- | --- | --- | --- | --- | --- |
| math200_case010 | peer_message_direct | message_only | live_sender_artifact | direct_visible_answer_uptake | 2 -> -1 |
| math200_case010 | sender_private_scratch_visible_inert | not_admitted | live_sender_artifact | direct_visible_answer_uptake | 2 -> -1 |
| math200_case020 | peer_message_direct | message_only | live_sender_artifact | direct_visible_answer_uptake | 110 -> 11 |
| math200_case022 | admission_rejected_quarantine | rejected | live_sender_artifact | local_re_solve_or_empty_artifact_error | 44% -> 43.99% |
| math200_case022 | verifier_admitted_result | admitted_verifier_result | live_sender_artifact | operator_candidate_needs_manual_review | 44% -> 44.05% |
| math200_case029 | typed_partial_derivation_requires_rederive | typed_message | live_sender_artifact | local_re_solve_or_empty_artifact_error | 3 -> 2 |
| math200_case029 | verifier_admitted_result | admitted_verifier_result | live_sender_artifact | operator_candidate_needs_manual_review | 3 -> 2 |
| math200_case038 | peer_message_direct | message_only | live_sender_artifact | direct_visible_answer_uptake | 1152 -> 1152 cups of flour |
| math200_case038 | sender_private_scratch_visible_inert | not_admitted | live_sender_artifact | direct_visible_answer_uptake | 1152 -> 1152 cups of flour |
| math200_case038 | shared_workspace_admitted | admitted_shared_workspace | live_sender_artifact | direct_visible_answer_uptake | 1152 -> 1152 cups of flour |
| math200_case038 | verifier_admitted_result | admitted_verifier_result | live_sender_artifact | direct_visible_answer_uptake | 1152 -> 1152 cups of flour |

## Caveat

Taxonomy labels are deterministic seed labels for triage. Manual inspection is still required before turning counts into claims.
