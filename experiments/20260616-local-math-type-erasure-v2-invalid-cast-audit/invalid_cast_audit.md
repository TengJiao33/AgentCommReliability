# MATH Type-Erasure v2 Invalid-Cast Audit

This audit re-labels the v2 authority-violation rows with a narrower seed taxonomy.
The purpose is to separate communication-boundary invalid casts from local re-solve and final-line/evaluator collisions before building the sender-receiver protocol.

## Counts

- Violation cards: `5`
- Invalid-cast core cards: `2`
- Direct visible answer-copy cards: `0`
- Local re-solve error cards: `2`
- Final-answer contract / semantic-collision cards: `1`

## Primary Taxonomy

| Slice | Count |
| --- | ---: |
| inherited_operator_state | 2 |
| local_re_solve_error_after_empty_typed_artifact | 2 |
| final_answer_contract_glitch_or_hidden_collision | 1 |

## Future Signals

| Slice | Count |
| --- | ---: |
| type_erased_shared_workspace_entry | 2 |
| typed_no_candidate_evidence_inference | 2 |
| typed_hidden_candidate_metadata | 1 |

## Artifact Types

| Slice | Count |
| --- | ---: |
| wrong_equation_surface | 2 |
| wrong_final_answer | 2 |
| wrong_relation_skeleton | 1 |

## Candidate Visibility

| Slice | Count |
| --- | ---: |
| artifact_native | 2 |
| none | 2 |
| hidden_metadata | 1 |

## Cards

| Case | Channel | Artifact | Candidate visibility | Taxonomy | Base -> Variant | Wrong visible |
| --- | --- | --- | --- | --- | --- | --- |
| math121_wrong_equation_surface | type_erased_shared_workspace_entry | wrong_equation_surface | artifact_native | inherited_operator_state | 18√3 -> 18√2 | False |
| math121_wrong_rationale | type_erased_shared_workspace_entry | wrong_equation_surface | artifact_native | inherited_operator_state | 18√3 -> 18√2 | False |
| math21_wrong_rationale | typed_no_candidate_evidence_inference | wrong_relation_skeleton | none | final_answer_contract_glitch_or_hidden_collision | 900 -> 15 | False |
| math96_wrong_rationale | typed_hidden_candidate_metadata | wrong_final_answer | hidden_metadata | local_re_solve_error_after_empty_typed_artifact | 8 -> 8/3 | False |
| math96_wrong_rationale | typed_no_candidate_evidence_inference | wrong_final_answer | none | local_re_solve_error_after_empty_typed_artifact | 8 -> 24 | False |

## Read

Only the shared-workspace `math121` rows are clean invalid-cast-core candidates in this seed taxonomy.
The typed no-candidate/hidden-candidate failures are better treated as local validation or final-answer-contract ambiguity, not as visible candidate copying.

## Caveat

These are deterministic seed labels. They are appropriate for selecting the next packet and for manual review triage, not for a population claim.
