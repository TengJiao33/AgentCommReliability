# Peer Relation-Slot Focus Cards

## What We Tried

I turned the redacted-evidence postcards into a small semantic audit instead of
launching another model run.

Artifacts:

- `experiments/_archive/20260616-pruned/20260614-2345-local-peer-relation-slot-cards/focus_cards.jsonl`
- `experiments/_archive/20260616-pruned/20260614-2345-local-peer-relation-slot-cards/manual_labels.jsonl`

The cards are the 10 focus cases selected from the redacted-evidence audit:

- `3` correct-evidence rescues;
- `5` wrong-evidence harmful-relation cases;
- `2` wrong-evidence recoverable-skeleton cases.

## What Happened

Manual label counts:

| Field | Counts |
| --- | --- |
| `relation_skeleton` | `correct: 3`, `wrong: 4`, `mixed: 1`, `recoverable_wrong: 2` |
| `numeric_slots` | `correct: 2`, `wrong: 3`, `mixed: 4`, `abstract: 1` |
| `final_slot` | `derivable: 5`, `absent: 4`, `blank: 1` |
| `answer_copy` | `relation_derived: 3`, `relation_derived_not_source_copy: 3`, `source_answer_copied_or_derived: 2`, `repaired: 2` |
| `target_predicate_preserved` | `true: 10` |

## Things Noticed

The most useful split is no longer answer visibility. It is whether the peer
surface carries a correct, wrong, mixed, or recoverable relation skeleton.

Correct relation-only surfaces rescued three cases without visible final-answer
copying:

- DAR `8`: age-anniversary relation preserved enough structure to derive `24`.
- MATH `9`: AM-GM plus the right transformed expression selected the solution
  route.
- DAR `78`: a blank-final group/member/quantity surface preserved all slots for
  `6 * 9 * 2`.

Wrong surfaces harmed through wrong slots rather than only wrong final answers:

- DAR `4`: wrong rate slot, `4/hour` melted instead of `8/hour`, moved
  `5 -> 3.75`.
- DAR `97`: wrong duration slot, `10` bonus months instead of `12`, moved
  `31800 -> 31500` under both auto and redacted evidence.
- DAR `65`: wrong average-scope equation, `(20-H)/4`, moved
  `3 -> 19/3`; the mechanical leakage flag is a false positive because `2`
  appears as a coefficient, not as the source final answer.
- MATH `47`: mixed circular-block skeleton. The target partly repaired the
  peer's `4!` internal count to `5!`, but changed another factor and ended at
  `14400` instead of copying the peer source answer `1152`.

The recoverable wrong surfaces are the counterweight:

- DAR `8` wrong auto and wrong redacted evidence both preserved the age anchor
  and target predicate, even though the equation was flawed. The target rejected
  the bad equation and rebuilt the correct solution.

## Caveats

These are selected focus cards, not a rate estimate. The labels are manual and
case-local. They should be used as schema pressure for the next audit, not as a
claim that these proportions will hold under a larger sample.

The same model produced the peer evidence and the target revision. This audit
only says what surfaces were available in the saved traces and how the target
responded in these runs.

## Loose Threads

The next pressure should be a slightly broader relation-slot audit over all
redacted evidence records, using the manual labels here as the seed taxonomy.
The useful fields are:

- relation skeleton: `correct`, `wrong`, `mixed`, `recoverable_wrong`;
- numeric slots: `correct`, `wrong`, `mixed`, `abstract`;
- final slot: `absent`, `blank`, `derivable`, `leaked`;
- target response: copied/derived source answer, derived a different wrong
  answer, repaired, or ignored.
