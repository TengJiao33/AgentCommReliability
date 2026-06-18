# Peer Relation-Slot Labeling Rubric

Use this as a compact checklist for the next redacted peer-evidence slice.
Labels are semantic notes over saved traces, not model judgments.

## Relation-Slot Labels

| Field | Suggested values | Question |
| --- | --- | --- |
| `relation_skeleton` | `correct`, `wrong`, `mixed`, `recoverable_wrong` | Does the evidence preserve the right relation among quantities, roles, or theorem objects? |
| `numeric_slots` | `correct`, `wrong`, `mixed`, `abstract`, `missing_required_role` | Are the numbers and role bindings right, wrong, mixed, absent, or missing a needed multiplicative/additive role? |
| `final_slot` | `absent`, `blank`, `derivable`, `leaked` | Is the final answer absent, explicitly blanked, reconstructable from the surface, or directly present? |
| `answer_copy` | `relation_derived`, `relation_derived_not_source_copy`, `source_answer_copied_or_derived`, `repaired`, `none` | Did the target copy, derive, repair, or ignore the source answer? |

## Contrast / Non-Rescue Labels

| Field | Suggested values | Question |
| --- | --- | --- |
| `peer_surface_status` | `correct_partial_method`, `correct_method_wrong_final`, `correct_relation_wrong_final`, `wrong_numeric_slot`, `wrong_numeric_role`, `wrong_relation_surface`, `wrong_solution_slot`, `missing_multiplicative_role`, `underspecified_correct_relation`, `dense_correct_condition`, `abstract_correct_method` | What kind of surface did the extractor leave behind? |
| `target_response` | `adopted_correct_surface`, `completed_correct_method`, `rejected_wrong_slot`, `repaired_from_question`, `repaired_from_units`, `adopted_wrong_slot`, `adopted_wrong_relation`, `preserved_missing_role_solution`, `overrode_correct_slot_with_prior_error`, `preserved_flawed_pre_solution`, `post_unparseable_after_dense_surface` | How did the target respond to that surface? |

## Minimal Note

Each row should include one short `semantic_note` tying the label to a concrete slot in the evidence text and to the target's post-exposure output.
