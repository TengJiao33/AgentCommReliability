# PACT Evidence Field Audit

## What We Tried

Using the PACT HotpotQA50 schema v1.1 trace, I audited where gold-answer
signals appear in PACT's public action-state fields. This is a follow-up to the
final-answer surface audit: instead of asking only whether strict EM failed, it
asks whether the saved public state already contains the answer signal.

No model call or GPU run was launched.

## What Happened

Official EM remains `17/50`. Among 33 official wrong-EM cases:

| Field-level category | Count |
| --- | ---: |
| output field already has gold/polarity signal | 23 |
| environment-only strict gold signal | 8 |
| yes/no final polarity mismatch or unclear | 1 |
| no strict gold field signal | 1 |

For the 25 wrong non-yes/no cases:

| Strict field signal | Count |
| --- | ---: |
| final answer contains normalized gold | 15 |
| action result contains normalized gold | 15 |
| final environment state contains normalized gold | 19 |
| any environment state contains normalized gold | 23 |

The important split is that many wrong cases are not clean evidence-transfer
failures. They look like:

- verbose final answers that include the gold span but fail strict EM;
- action results that contain the answer while final answer format is too broad;
- environment states that contain the answer while action result/final answer
  selects a competing entity or underspecified span.

## Things Noticed

The `Environment State` field is not just decorative in this run. In `23/25`
wrong non-yes/no cases, some environment state contains the normalized gold
span; in `19/25`, even the final environment state contains it.

That makes PACT a useful pressure object for the project's public-state axis:
the field structure is compliant, but the agent may still fail to transform
available public state into an evaluation-compatible final answer.

The lone `no strict gold field signal` case is sample `40`, where the saved
fields say "The Scotch Collie's ancestors..." and the gold answer is `Scotch
Collie`. The relaxed possessive/plural diagnostic catches this, but it should
remain a diagnostic rather than a scoring rule.

## Loose Threads

- See `reports/20260614-pact-extraction-only-audit.md` for the completed
  extraction-only follow-up.
- If a tiny rerun becomes justified, change only the final-answer instruction
  or parser contract, not the whole communication method.
- Keep separating public-state evidence quality from final answer formatting.

## Caveats

- Field signals are not alternate official scores.
- Gold containment can over-credit cases where the surrounding evidence is
  misleading.
- Yes/no cases are audited by final-answer first-token polarity, not by literal
  `yes`/`no` containment in evidence fields.
