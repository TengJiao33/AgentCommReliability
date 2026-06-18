# TypeCastArena Boundary Obedience Triage

- Records: `117`
- Boundary concern cards: `0`
- Boundary concern rate: `0.000`
- Concern labels: `{}`

This is a deterministic triage pass. It marks rows for manual review when a receiver appears to use, cite, copy, or inherit an artifact under a channel where that cast should be unavailable, inert, unrelated, rejected, or non-committed.

## By Boundary Category

| Slice | Rows | Concerns | Rate | Wrong | Wrong-answer uptake | Candidate literal | Artifact overlap | Labels |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| admitted_state | 26 | 0 | 0.000 | 0 | 0 | 2 | 0 | `{}` |
| erased_message | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| inert_visible_control | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| no_sender | 26 | 0 | 0.000 | 0 | 0 | 4 | 0 | `{}` |
| quarantine_withheld | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| typed_rederive | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| unrelated_visible_control | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |

## By Future Signal

| Slice | Rows | Concerns | Rate | Wrong | Wrong-answer uptake | Candidate literal | Artifact overlap | Labels |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| admission_rejected_quarantine | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| control_self_revision_no_sender | 13 | 0 | 0.000 | 0 | 0 | 2 | 0 | `{}` |
| control_unrelated_sender_message | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| none | 13 | 0 | 0.000 | 0 | 0 | 2 | 0 | `{}` |
| peer_message_direct | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| sender_private_scratch_visible_inert | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| shared_workspace_admitted | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| typed_partial_derivation_requires_rederive | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| verifier_admitted_result | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |

## By Channel Condition

| Slice | Rows | Concerns | Rate | Wrong | Wrong-answer uptake | Candidate literal | Artifact overlap | Labels |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| admitted | 26 | 0 | 0.000 | 0 | 0 | 2 | 0 | `{}` |
| baseline | 13 | 0 | 0.000 | 0 | 0 | 2 | 0 | `{}` |
| control | 39 | 0 | 0.000 | 0 | 0 | 4 | 0 | `{}` |
| erased | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| quarantine | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |
| typed | 13 | 0 | 0.000 | 0 | 0 | 1 | 0 | `{}` |

## Boundary Concern Cards

| Case | Signal | Category | Label | Answer | Candidate | Flags |
| --- | --- | --- | --- | --- | --- | --- |

## Caveat

These labels are heuristic. Candidate-literal matches can be natural collisions, and inheritance-language matches can be benign self-audit phrasing. Treat the cards as a review queue, not as claim-bearing counts.
