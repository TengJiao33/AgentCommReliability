# MATH Sender-Receiver Micro-Protocol Analysis

- Evaluated rows: `304`
- Paired delta rows: `266`
- Authority-violation cards: `12`
- Taxonomy counts: `{'direct_visible_answer_uptake': 1, 'local_re_solve_or_empty_artifact_error': 6, 'operator_candidate_needs_manual_review': 5}`

## Authority By Channel Condition

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| admitted | 76 | 68 | 3 | 0.044 | 0 | 3 |
| control | 76 | 68 | 3 | 0.044 | 0 | 3 |
| erased | 38 | 34 | 1 | 0.029 | 1 | 0 |
| quarantine | 38 | 34 | 2 | 0.059 | 0 | 2 |
| typed | 38 | 34 | 3 | 0.088 | 0 | 3 |

## Authority By Admission Status

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| admitted_shared_workspace | 38 | 34 | 1 | 0.029 | 0 | 1 |
| admitted_verifier_result | 38 | 34 | 2 | 0.059 | 0 | 2 |
| message_only | 76 | 68 | 3 | 0.044 | 1 | 2 |
| none | 38 | 34 | 1 | 0.029 | 0 | 1 |
| rejected | 38 | 34 | 2 | 0.059 | 0 | 2 |
| typed_message | 38 | 34 | 3 | 0.088 | 0 | 3 |

## Authority By Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| admission_rejected_quarantine | 38 | 34 | 2 | 0.059 | 0 | 2 |
| control_self_revision_no_sender | 38 | 34 | 1 | 0.029 | 0 | 1 |
| control_unrelated_sender_message | 38 | 34 | 2 | 0.059 | 0 | 2 |
| peer_message_direct | 38 | 34 | 1 | 0.029 | 1 | 0 |
| shared_workspace_admitted | 38 | 34 | 1 | 0.029 | 0 | 1 |
| typed_partial_derivation_requires_rederive | 38 | 34 | 3 | 0.088 | 0 | 3 |
| verifier_admitted_result | 38 | 34 | 2 | 0.059 | 0 | 2 |

## Violation Cards

| Case | Channel | Admission | Artifact | Taxonomy | Base -> Variant |
| --- | --- | --- | --- | --- | --- |
| math200_case010 | peer_message_direct | message_only | live_sender_artifact | direct_visible_answer_uptake | 2 -> -1 |
| math200_case022 | admission_rejected_quarantine | rejected | live_sender_artifact | local_re_solve_or_empty_artifact_error | 44% -> 43.99% |
| math200_case022 | verifier_admitted_result | admitted_verifier_result | live_sender_artifact | operator_candidate_needs_manual_review | 44% -> 44.05% |
| math200_case112 | control_self_revision_no_sender | none |  | local_re_solve_or_empty_artifact_error | 118 -> 105 |
| math200_case112 | admission_rejected_quarantine | rejected | live_sender_artifact | local_re_solve_or_empty_artifact_error | 118 -> 43 |
| math200_case112 | shared_workspace_admitted | admitted_shared_workspace | live_sender_artifact | operator_candidate_needs_manual_review | 118 -> 105 |
| math200_case112 | typed_partial_derivation_requires_rederive | typed_message | live_sender_artifact | local_re_solve_or_empty_artifact_error | 118 -> 103 |
| math200_case112 | verifier_admitted_result | admitted_verifier_result | live_sender_artifact | operator_candidate_needs_manual_review | 118 -> 105 |
| math200_case121 | control_unrelated_sender_message | message_only | live_sender_artifact | operator_candidate_needs_manual_review | $18\sqrt{3}$ -> $18\sqrt{2}$ |
| math200_case130 | typed_partial_derivation_requires_rederive | typed_message | live_sender_artifact | local_re_solve_or_empty_artifact_error | \(\frac{5}{6}\) -> $\frac{2}{3}$ |
| math200_case147 | control_unrelated_sender_message | message_only | live_sender_artifact | operator_candidate_needs_manual_review | 5/7 -> $\frac{3}{4}$ |
| math200_case147 | typed_partial_derivation_requires_rederive | typed_message | live_sender_artifact | local_re_solve_or_empty_artifact_error | 5/7 -> 3/4 |

## Caveat

Taxonomy labels are deterministic seed labels for triage. Manual inspection is still required before turning counts into claims.
