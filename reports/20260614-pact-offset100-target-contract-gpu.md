# PACT Offset100 Target-Contract GPU Run

## What We Tried

I ran a fresh paired PACT HotpotQA slice on A800_2:

- samples: zero-based `100-149`
- model: Qwen2.5-14B-Instruct
- arms: baseline, final-answer contract, target-slot + final-answer contract

The new prompt control was env-gated:

```text
PACT_TARGET_SLOT_CONTRACT=1
```

It asks the public `Action Required` field to preserve the original question's
target, requested answer type, qualifier, and anchor entities.

Run record:

- `experiments/20260614-1552-a8002-pact-qwen25-14b-hotpot50-offset100-target-contract/`

## What Happened

| Arm | EM | Avg F1 | Avg final-answer words | Avg comm tokens | Avg total tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | `16/50` | `0.5517` | `7.08` | `361.6` | `4477.0` |
| final contract | `26/50` | `0.6332` | `2.94` | `331.5` | `4526.8` |
| target + final contract | `26/50` | `0.6494` | `2.66` | `485.2` | `5266.0` |

Against baseline, final-answer contract again gives a real EM lift:

- `+10` correct;
- 12 wrong-to-right;
- 2 right-to-wrong.

Adding target-slot preservation on top of final-answer contract gives:

- `0` net EM change;
- `+0.0162` average F1;
- 3 wrong-to-right and 3 right-to-wrong;
- about `+153.7` communication tokens/sample and `+739.2` total tokens/sample.

## Target-Slot Diagnostic

The rough lexical target-slot diagnostic over non-stable-right cases found:

| Comparison | Focus cases | Target-slot candidates |
| --- | ---: | ---: |
| baseline -> final contract | `36` | `6` |
| baseline -> target + final | `38` | `2` |
| final contract -> target + final | `27` | `1` |

So the target contract appears to improve the visible target-preservation
surface, but it does not translate into a clean accuracy improvement.

## Things Noticed

Sample `101` is a clean rescue from target + final over final-only: final-only
answered `Yes`, while target + final answered `Larnelle Harris`.

Sample `115` is another useful rescue: final-only answered `more than 230`,
while target + final committed to `230`.

Sample `147` improves from the over-specific `Kingdom of Mann and the Isles`
to `Kingdom of the Isles`.

The regressions are equally important. Sample `130` flips from the correct film
title to `No`; sample `149` flips from `We'll Burn That Bridge` to
`Chattahoochee`. The latter is especially telling: the target contract keeps
the original target verbose, but the final answer commits to the intermediate
third single rather than the song behind it.

## Interpretation

This strengthens the larger idea, but not because the new prompt wins.

The better reading is:

```text
public-state target preservation is a separable control surface.
Naively enforcing it reduces visible target drift but increases cost and can
still fail at final commitment or evidence selection.
```

That fits the project's current framing better than a pure prompt-method claim.
PACT failures are not one thing: final answer surface, public target state,
evidence selection, and answer commitment can move separately.

## Caveats

- One 50-sample slice.
- Qwen2.5-14B, not Qwen3-14B.
- The target-slot diagnostic is lexical, not semantic.
- No target-only arm was run.
- The target prompt increases public message length, so token cost is a real
  failure mode of the naive intervention.

## Next Honest Check

If this stays central, the next GPU check should not simply make the target
contract louder. A better next arm is a shorter target-state projection:

```text
Target Slot: [answer type + anchor + required qualifier]
```

That would test whether target preservation can be made compact enough to keep
the diagnostic benefit without the large communication-token increase.
