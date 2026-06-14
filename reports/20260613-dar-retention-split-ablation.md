# DAR Retention Split Ablation

## What We Tried

Split the previous DAR guarded answer-only variant into two GSM8K100 ablations:

- `answer_only_no_guard`: keep original `filter_critical` selection, pass retained peers as parsed answers only.
- `guard_full`: apply the answer-diversity guard, pass full retained peer messages.

Run record: `experiments/20260613-2143-a8002-dar-retention-split-gsm8k100/`.

## What Happened

| Method | Round 1 Acc. | Right-to-Wrong | Total Tokens |
| --- | ---: | ---: | ---: |
| original DAR `filter_critical` | 0.93 | 3 | 542,498 |
| `answer_only_no_guard` | 0.95 | 1 | 419,180 |
| guarded answer-only | 0.95 | 1 | 418,427 |
| `guard_full` | 0.96 | 0 | 545,520 |

## Things Noticed

The previous guarded answer-only gain was not one thing.

The answer-only message surface accounts for the token drop and fixes two original right-to-wrong cases, samples `5` and `22`, even without changing retained IDs.

The answer-diversity guard matters for sample `20`: `guard_full` adds the originally dropped correct `Agent1` and turns the case from wrong to right. The same added answer bucket under answer-only still ends wrong, so sample `20` likely needs more than the parsed answer surface.

This leaves a real tradeoff:

- answer-only is cheaper and removes some parser/continuation failures;
- guarded full retention is more accurate on this slice, but gives back the token savings.

## Caveats

- One seed/model/GSM8K100 slice only.
- `guard_full` is a useful diagnostic, not a cheap method.
- GSM8K is already fairly saturated here; a harder slice is a better next empirical test.

## Loose Threads

- Inspect sample `20` before designing another variant.
- Consider an intermediate retained surface, such as answer plus short evidence, instead of only `answer_only` or full reasoning.
