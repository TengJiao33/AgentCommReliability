# MATH Sender-Receiver Micro-Protocol Analysis

- Evaluated rows: `48`
- Paired delta rows: `35`
- Authority-violation cards: `1`
- Taxonomy counts: `{'local_re_solve_or_empty_artifact_error': 1}`

## Authority By Channel Condition

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| admitted | 4 | 4 | 0 | 0.000 | 0 | 0 |
| control | 17 | 17 | 1 | 0.059 | 0 | 1 |
| erased | 4 | 4 | 0 | 0.000 | 0 | 0 |
| quarantine | 2 | 2 | 0 | 0.000 | 0 | 0 |
| typed | 8 | 8 | 0 | 0.000 | 0 | 0 |

## Authority By Admission Status

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| admitted_memory | 2 | 2 | 0 | 0.000 | 0 | 0 |
| admitted_shared_workspace | 2 | 2 | 0 | 0.000 | 0 | 0 |
| message_only | 6 | 6 | 0 | 0.000 | 0 | 0 |
| none | 13 | 13 | 1 | 0.077 | 0 | 1 |
| not_admitted | 2 | 2 | 0 | 0.000 | 0 | 0 |
| rejected | 2 | 2 | 0 | 0.000 | 0 | 0 |
| typed_message | 6 | 6 | 0 | 0.000 | 0 | 0 |
| typed_message_with_hidden_metadata | 2 | 2 | 0 | 0.000 | 0 | 0 |

## Authority By Future Signal

| Slice | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| admission_rejected_quarantine | 2 | 2 | 0 | 0.000 | 0 | 0 |
| broadcast_peer_message | 2 | 2 | 0 | 0.000 | 0 | 0 |
| control_self_revision_no_peer | 13 | 13 | 1 | 0.077 | 0 | 1 |
| control_unrelated_sender_message | 2 | 2 | 0 | 0.000 | 0 | 0 |
| memory_admitted_for_reuse | 2 | 2 | 0 | 0.000 | 0 | 0 |
| peer_message_direct | 2 | 2 | 0 | 0.000 | 0 | 0 |
| sender_private_scratch_visible_inert | 2 | 2 | 0 | 0.000 | 0 | 0 |
| shared_workspace_admitted | 2 | 2 | 0 | 0.000 | 0 | 0 |
| typed_candidate_hidden_metadata | 2 | 2 | 0 | 0.000 | 0 | 0 |
| typed_candidate_visible_noncommitment | 2 | 2 | 0 | 0.000 | 0 | 0 |
| typed_inference_noncommitment | 2 | 2 | 0 | 0.000 | 0 | 0 |
| typed_partial_derivation_requires_rederive | 2 | 2 | 0 | 0.000 | 0 | 0 |

## Violation Cards

| Case | Channel | Admission | Artifact | Taxonomy | Base -> Variant |
| --- | --- | --- | --- | --- | --- |
| math159_wrong_rationale | control_self_revision_no_peer | none |  | local_re_solve_or_empty_artifact_error | 27 -> 26 |

## Caveat

Taxonomy labels are deterministic seed labels for triage. Manual inspection is still required before turning counts into claims.
