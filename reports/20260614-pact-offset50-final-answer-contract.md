# PACT Offset50 Final-Answer-Contract Check

## What We Tried

After the first-50 PACT final-answer-contract run doubled strict EM, I ran a
neighboring-slice paired check on HotpotQA samples `50-99`.

The goal was not to make a broad claim. It was to see whether the signal
survives outside the inspected first slice.

Run record:

- `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/`

## What Happened

| Metric | Offset50 baseline | Offset50 final-contract |
| --- | ---: | ---: |
| EM | `26/50` | `28/50` |
| Avg F1 | `0.6469` | `0.7427` |
| Avg final-answer words | `7.62` | `2.32` |
| Avg communication tokens | `327.3` | `324.0` |
| Avg total tokens | `4306.6` | `4410.2` |

Transitions:

| Transition | Count |
| --- | ---: |
| stable right | `22` |
| wrong to right | `6` |
| right to wrong | `4` |
| stable wrong | `18` |

Question-aware extraction reaches `29/50` on both baseline and contract traces.
For the contract trace, it adds only one rescue over official output. Guarded
final-event arbitration stays at `28/50`, with one rescue and one regression.

## Things Noticed

The first-50 result does not simply repeat. The contract effect on strict EM is
small here: `+2` exact matches, not `+17`.

The surface signal remains real. Average F1 rises by about `0.096`, and final
answers shrink from `7.62` to `2.32` words on average. The clearest rescues are
answer-surface cases:

- sample `57`: full sentence -> `Keith Bostic`;
- sample `78`: full sentence -> `British`;
- sample `93`: full sentence -> `No`;
- sample `99`: full sentence -> `No`.

The right-to-wrong cases are mixed:

- sample `54`: high-F1 strict surface regression, dropped the explicit `and`;
- sample `64`: high-F1 strict surface regression, dropped `countries`;
- sample `66`: high-F1 strict surface regression, added `(IBHOF)`;
- sample `58`: real content regression, `35,124` -> `273`.

This makes the current object sharper. Final-answer contract is a real
confound, but it is not a clean method. It changes model behavior, exact-match
span length, and sometimes content.

## Caveats

- One neighboring 50-sample slice.
- Same Qwen2.5-14B model, not Qwen3-14B.
- The paired runs were sequential, not same-process.
- Postprocessing diagnostics are not replacement scores.

## Loose Threads

- Inspect sample `58` as the content-regression sentinel.
- Inspect the `18` stable-wrong cases by public-state fields before another
  prompt control.
- Keep PACT alive, but do not promote final-answer contract into a method by
  itself.
