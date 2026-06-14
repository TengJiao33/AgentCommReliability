# PACT Offset50 Sample 58 Drift

## What We Tried

I inspected sample `58`, the only clear content-drift regression in the
PACT HotpotQA offset50 paired run.

Source artifacts:

- `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/pact_sample58_drift_packet.json`
- `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/pact_sample58_drift_packet.md`
- `scripts/build_pact_drift_packet.py`

Question:

> According to the 2001 census, what was the population of the city in which
> Kirton End is located?

Gold answer: `35124`.

## What Happened

The baseline run answers `35,124`. The final-answer-contract run answers
`273`.

Both final prompts contain both relevant-looking paragraphs:

| Paragraph | Number | Role |
| --- | ---: | --- |
| `Boston, Lincolnshire` | `35,124` | correct city/town population |
| `Kirton, Nottinghamshire` | `273` | distractor population |

The turn-level drift is clean:

| Turn | Baseline target | Variant target | Number carried |
| ---: | --- | --- | --- |
| `0` | locate Kirton End | locate Kirton End | none |
| `1` | city in which Kirton End is located | Boston district | both carry `35,124` |
| `2` | city/Boston population | civil parish of Kirton | variant drops `35,124` |
| `3` | city/Boston population | civil parish of Kirton | variant selects `273` |

The important detail: the first divergence is at turn `1`, before the final
turn where `PACT_FINAL_ANSWER_CONTRACT` changes the prompt text. So this case
should not be treated as proof that the final-answer contract directly caused
the wrong content. The paired run is stochastic, and the regression path begins
as a trajectory divergence under otherwise matching non-final prompts.

## Things Noticed

Sample `58` is not an extraction-only failure. The final answer `273` is
faithful to the variant's final public state, but the public state is anchored
to the wrong entity/slot.

The failure is also not simple evidence absence. The variant sees the correct
`35,124` evidence at turn `1`. The loss happens when Agent A retargets the
needed fact to "the population of the civil parish of Kirton", and Agent B then
finds a plausible `Kirton` distractor with a 2001 population.

This exposes a slightly different object from the previous public-state-gold
cases. Those cases often had the right evidence in the final public state but
failed to commit to the right answer span. Sample `58` shows a prior failure:
the shared action state itself drifts to the wrong target slot, then the final
answer commits cleanly to that wrong slot.

## Interpretation

This is a target-slot drift sentinel.

The useful question is not only "does the final public state contain the
answer?" It is also "does the public state's current target still match the
original question?"

PACT's action-state format makes this failure visible because `Action
Required` acts like a small moving contract between agents. In sample `58`,
that contract migrates from:

- population of the city in which Kirton End is located;

to:

- population of the civil parish of Kirton.

That migration is enough to route the final agent into a distractor paragraph.

## Caveats

- One case only.
- The two paired runs are stochastic; this is not a clean causal attribution
  to the final-answer-contract prompt.
- HotpotQA wording says "city" even though Boston is a town, which may make
  the target easier to destabilize.
- The final-answer contract remains a run-level condition, but this case's
  earliest observed divergence is pre-final.

## Loose Threads

- See `reports/20260614-pact-offset50-target-slot-drift.md` for the first
  rough target-slot preservation diagnostic.
- Run the drift packet over the other right-to-wrong cases to separate
  strict-span regressions from true target-slot migrations.
- Treat stochastic trajectory divergence as part of the measurement problem
  for prompt-control experiments.
