# Peer Redacted Relation-Slot Audit

## What We Tried

I merged the full redacted-evidence audit with the manual relation-slot and
contrast labels.

Artifacts:

- `scripts/audit_peer_relation_slots.py`
- `experiments/_archive/20260616-pruned/20260615-0006-local-peer-redacted-relation-slot-audit/summary.json`
- `experiments/_archive/20260616-pruned/20260615-0006-local-peer-redacted-relation-slot-audit/redacted_relation_slot_records.jsonl`
- `experiments/_archive/20260616-pruned/20260615-0006-local-peer-redacted-relation-slot-audit/unlabeled_redacted_records.jsonl`
- `experiments/_archive/20260616-pruned/20260615-0006-local-peer-redacted-relation-slot-audit/labeling_rubric.md`
- `experiments/_archive/20260616-pruned/20260615-0012-local-peer-redacted-nonrescue-cards/manual_nonrescue_labels.jsonl`

The merged audit covers all `44` redacted-evidence rows from:

- `correct_redacted_evidence`: `22`
- `wrong_redacted_evidence`: `22`

## What Happened

Manual semantic coverage now reaches `28/44` rows:

| Condition | Relation-slot labels | Contrast labels | Unlabeled |
| --- | ---: | ---: | ---: |
| `correct_redacted_evidence` | `2` | `4` | `16` |
| `wrong_redacted_evidence` | `5` | `17` | `0` |

The important coverage boundary is that every answer-changing redacted case is
now manually labeled:

- `right_to_wrong`: `4/4` labeled;
- `wrong_to_right`: `3/3` labeled.

The remaining unlabeled rows are all stable-right `correct_redacted_evidence`
records where the target was correct before exposure and stayed correct after
exposure.

The `summary.json` now makes those boundaries directly checkable:

- `answer_changing_manual_coverage_complete: true`;
- `answer_changing_records: 7`;
- `answer_changing_unlabeled_records: 0`;
- `unlabeled_all_preserved_correct_stable_right: true`.

Semantic families over the labeled rows:

| Family | Count |
| --- | ---: |
| `contrast_wrong_final_removed_or_correct_surface` | `5` |
| `contrast_wrong_slot_rejected_or_repaired` | `4` |
| `contrast_wrong_surface_preserved_wrong_answer` | `4` |
| `contrast_dense_or_abstract_surface_parse_drift` | `3` |
| `manual_wrong_relation_surface` | `3` |
| `contrast_correct_surface_not_rescued` | `2` |
| `contrast_target_contract_or_predicate_guard` | `2` |
| `manual_correct_relation_surface` | `2` |
| `contrast_partial_relation_filled` | `1` |
| `manual_mixed_relation_surface` | `1` |
| `manual_recoverable_wrong_surface` | `1` |

## Things Noticed

The full audit sharpens the earlier postcard story.

Wrong redacted evidence is not a single failure mode:

- harmful adoption: wrong or mixed relation/numeric slots caused all four
  right-to-wrong transitions;
- recoverable skeleton: one wrong redacted surface preserved enough age/time
  structure for the target to repair it;
- apparent robustness: stable-right wrong-redacted cases often came from wrong
  final answers being removed into correct/partial evidence, wrong slots being
  rejected, or target-predicate/answer-contract guards;
- stable wrong: three wrong-redacted cases preserved already-wrong answers by
  keeping the harmful relation, additive slot, or missing multiplicative role.

Correct redacted evidence also has two surfaces:

- two relation-only rescues, where the surface carried enough usable structure
  to move wrong-to-right;
- two stable-wrong non-rescues, where the correct surface was too thin or was
  overwritten by the target's prior wrong slot.

The current evidence supports a more careful phrasing: answer redaction changes
the peer surface, not just the leakage rate. Sometimes it removes a harmful
final slot and leaves a useful method; sometimes it preserves the harmful slot
that actually controls the target.

## Caveats

The semantic labels are manual and local to this selected DAR/MATH disagreement
set. They are not a rate estimate for a broad benchmark.

The remaining unlabeled `16` rows are not ignored because they are unimportant;
they are just the least diagnostic group for this question: correct redacted
evidence preserving already-correct answers.

The same model produced evidence and revisions, so this audit is about saved
surface behavior, not a method claim.

## Loose Threads

The next useful pressure is a same-schema rerun on a neighboring random slice or
seed. The point would not be higher accuracy; it would be checking whether the
same relation-slot families appear when the cases are not the exact same
postcards.
