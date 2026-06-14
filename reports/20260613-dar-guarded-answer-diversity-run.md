# DAR Guarded Answer-Diversity Run

## What We Tried

Ran a real DAR GSM8K100 follow-up after the offline guarded-retention simulation.

The variant keeps DAR `filter_critical`, then applies an answer-diversity guard over retained IDs and passes retained peer context as parsed answers only.

## What Happened

| Method | Round 0 Acc. | Round 1 Acc. | Right-to-Wrong | Total Tokens |
| --- | ---: | ---: | ---: | ---: |
| original DAR `filter_critical` | 0.95 | 0.93 | 3 | 542,498 |
| guarded answer-only | 0.95 | 0.95 | 1 | 418,427 |

Source run:

- `experiments/20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100/`

The guard changed 17 retained sets and recovered at least one correct retained first-round message in 13 cases. It did not drop any previously retained correct first-round message.

## Things Noticed

The online run partly confirms the offline audit but with a twist.

- DAR `22` behaves as expected: replacing an unparseable retained message with a parseable correct answer prevents the right-to-wrong transition.
- DAR `20` remains wrong even after the correct answer bucket is added, so answer diversity alone is not a guarantee.
- DAR `5` improves even though guard did not change the retained IDs. The likely intervention there is the answer-only message surface, which avoids the earlier full-reasoning continuation or parser failure.

This suggests two separate handles:

- selection guard: avoid retaining only wrong or unparseable answers when parseable alternatives exist;
- message surface guard: do not necessarily pass full previous reasoning forward.

## Caveats

- One seed/model/slice only.
- Two interventions were combined in this run: answer-diversity guard and answer-only retained messages.
- The result should be treated as a useful contact point, not a claim that this rule generalizes.

## Loose Threads

- Split the intervention: answer-only without guard, and guard with full retained messages.
- Inspect sample `20` as the remaining right-to-wrong case.
- If the split is still promising, try a harder benchmark slice rather than expanding GSM8K immediately.
