# PACT Final-Answer-Contract GPU Run

## What We Tried

I ran a real GPU PACT HotpotQA50 variant on A800_2 with Qwen2.5-14B. The only
method change was an env-gated final-turn instruction:

```text
PACT_FINAL_ANSWER_CONTRACT=1
```

The PACT action-state communication format stayed the same.

## What Happened

The run completed on GPU 7 with `RC=0`.

| Metric | Original PACT50 | Final-contract PACT50 |
| --- | ---: | ---: |
| EM | `17/50` | `34/50` |
| Avg F1 | `0.508` | `0.792` |
| Avg final-answer words | `9.92` | `2.08` |
| Avg communication tokens | `339.3` | `321.9` |

Case transitions against the original PACT50:

| Transition | Count |
| --- | ---: |
| stable right | `14` |
| wrong to right | `20` |
| right to wrong | `3` |
| stable wrong | `13` |

## Things Noticed

This is the first GPU-backed version of the earlier postprocessing signal.
Final answer contract is not just a parser artifact: changing the actual model
prompt doubles strict EM on this 50-sample PACT smoke.

It is also not a clean method result. Three cases regress: `4`, `35`, and `49`.
The contract changes generation behavior, not just output formatting.

The nine previously inspected field-selection focus cases split as:

- wrong to right: `4`;
- stable wrong: `5`.

So the GPU run confirms part of the diagnosis but also narrows it. Final answer
contract helps many verbose-surface and answer-type cases, while full-name
preservation, year/date granularity, location granularity, and earlier-state
overwrite remain live problems.

## Loose Threads

The next defensible battlefield check is a neighboring-slice run, not a broad
benchmark claim. A useful next run would keep the same prompt control and test
samples `50-99`, or run a paired original/contract comparison on a smaller
slice if stochasticity becomes a concern.

## Caveats

- This is a 50-sample smoke, not benchmark evidence.
- Qwen2.5-14B is not Qwen3-14B.
- The comparison uses the prior same-model, same-seed first-50 baseline rather
  than a same-process paired rerun.
- The result supports final-answer contract as a real confound; it does not by
  itself establish a new communication method.
