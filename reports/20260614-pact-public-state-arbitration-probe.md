# PACT Public-State Arbitration Probe

## What We Tried

I ran a CPU-only postprocessing probe over the saved PACT HotpotQA50 trace to
test whether public-state field arbitration is a useful next contact point.

No model call or GPU run was launched.

## What Happened

| Policy | Correct | Rescues vs question-aware | Regressions vs question-aware |
| --- | ---: | ---: | ---: |
| official PACT extraction | `17/50` | n/a | n/a |
| question-aware policy | `38/50` | n/a | n/a |
| naive final-event arbitration | `38/50` | `6` | `6` |
| guarded final-event arbitration | `44/50` | `6` | `0` |

Naive arbitration is a useful negative control. Public-state candidates are not
safe to trust by default: unrestricted arbitration saves six cases but breaks
six already-correct question-aware cases.

The guarded version is the sharper signal. It only allows arbitration when the
current question-aware answer visibly violates the question contract. Under that
diagnostic policy, it preserves the `38` question-aware correct cases and
recovers six more: `1`, `15`, `25`, `30`, `31`, and `40`.

## Things Noticed

On the nine manually inspected focus cases:

| Manual family | Count | Guarded final-event recovered |
| --- | ---: | ---: |
| final field or anchor selection conflict | `3` | `3` |
| answer contract or extractor priority | `4` | `3` |
| earlier state lost or overwritten | `2` | `0` |

This separates two problems that were previously tangled:

- final-turn public fields often contain a usable answer, but the final answer
  contract chooses the wrong surface;
- earlier useful state can still be overwritten or outvoted by later comparison
  state, and this probe does not fix that.

The emerging handle is therefore not "more extraction rules." It is a guarded
arbitration/check layer between public state and final answer.

## Loose Threads

The most resource-conscious next step is a tiny final-answer-contract control
run or an offline verifier-style check over final public fields. The earlier
state lost cases should remain sentinels; scaling HotpotQA would mostly scale
this confound.

## Caveats

- `44/50` is a diagnostic postprocessing number, not an official PACT score.
- The guard was designed after case inspection, so it needs a neighboring
  slice or task before it can support a broader claim.
- Gold labels are used only for evaluation.
