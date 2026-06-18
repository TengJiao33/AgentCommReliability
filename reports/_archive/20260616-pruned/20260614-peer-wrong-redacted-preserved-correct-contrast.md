# Wrong Redacted Evidence Preserved-Correct Contrast

## What We Tried

I built a local contrast packet for the cases where the target was already
correct and stayed correct after seeing `wrong_redacted_evidence`.

Command shape:

```text
python scripts/build_peer_relation_slot_cards.py --conditions wrong_redacted_evidence --target-behaviors preserved_correct_answer ...
```

Artifacts:

- `experiments/_archive/20260616-pruned/20260614-2355-local-peer-wrong-redacted-preserved-correct-cards/summary.json`
- `experiments/_archive/20260616-pruned/20260614-2355-local-peer-wrong-redacted-preserved-correct-cards/focus_cards.jsonl`
- `experiments/_archive/20260616-pruned/20260614-2355-local-peer-wrong-redacted-preserved-correct-cards/manual_contrast_labels.jsonl`

## What Happened

The packet contains `12` stable-right cards:

| Contact label | Count |
| --- | ---: |
| `plain_relation_surface` | `6` |
| `dense_formula_surface` | `3` |
| `answer_leak_audit` | `3` |

Manual contrast labels split them into three rough families:

| Family | Cases | Count |
| --- | --- | ---: |
| Wrong final removed, leaving correct or partial surface | `1`, `14`, `42`, `48`, `63`, `82` | `6` |
| Wrong numeric/role slot rejected or repaired | `20`, `22`, `38`, `76` | `4` |
| Target predicate or answer contract guarded the answer | `13`, `37` | `2` |

## Things Noticed

The stable-right contrast should not be read as a clean model robustness signal.
In half of these cases, the redacted evidence surface is no longer semantically
wrong in the way the source peer final answer was wrong.

Examples:

- MATH `42`: the peer was parsed as answer `0` because it ended with an
  equation set equal to zero, but the evidence surface is the correct
  denominator-zero setup.
- DAR `63`: the peer rationale computes the correct Becky/Kelly difference but
  ends with a nonsensical final answer; redaction removes the bad final slot.
- DAR `82`: the wrong peer final answer used multiplication by `1.04`, but the
  extracted evidence says to divide by `1 + percentage error`, which is the
  correct relation.

The cases that really look like resistance are the explicit wrong-slot repairs:

- DAR `76`: the target rejects `30` students and restores `40`.
- MATH `22`: the target rejects `24.8` as the 20 percent increase of `24` and
  restores `28.8`.
- MATH `38`: the target repairs a radius/diameter role error.
- DAR `20`: the target overrides the peer's candy-cost slot using the original
  question.

The answer-leak flags are also noisy on this contrast packet. MATH `42` counts
source answer `0`, but the `0` is the equation's right-hand side. MATH `38`
counts `288`, but the target uses it as converted diameter, not as a final
answer.

## Caveats

This is still a selected local packet. The manual contrast labels are not a
rate estimate. They mainly keep the project from over-reading stable-right
wrong-evidence cases as generic resistance to peer influence.

## Loose Threads

If this axis stays active, the next audit should separate:

- wrong source final answer with correct extracted evidence;
- wrong extracted relation or numeric slot that the target rejects;
- wrong extracted relation or numeric slot that the target adopts;
- target-predicate or answer-contract conflicts.
