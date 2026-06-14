# Peer Auto-Evidence Contact Notes

## What We Tried

We extended `scripts/run_peer_exposure_probe.py` to schema
`acr.peer_exposure.v0.3` with:

- `correct_auto_evidence`
- `wrong_auto_evidence`
- `--selection-mode random`
- `--sample-seed`
- `auto_evidence_extractions.jsonl`

The auto-evidence surface uses the same served model to compress a peer rationale
into one short evidence or relation note before the target model revises its own
answer. The prompt asks the extractor not to state the final answer. This is a
contact probe, not a clean method.

Formal runs:

- `experiments/20260614-2205-a8002-peer-auto-evidence-dar-random14/`
  - DAR GSM8K mixed-correctness cases selected with random seed `61421`
  - `14` cases, `98` answer records, `28` auto-evidence extraction records
- `experiments/20260614-2206-a8002-peer-auto-evidence-math-random8/`
  - MAD-MM MATH mixed-correctness cases selected with random seed `61421`
  - `8` cases, `56` answer records, `16` auto-evidence extraction records

Both runs used Qwen2.5-7B-Instruct through a temporary A800_2 vLLM service on GPU
`1`, port `8024`. The service was stopped after the runs and GPU `1` returned to
idle.

## What Happened

On DAR random14:

| Condition | Correct | Accuracy | Main transition |
| --- | ---: | ---: | --- |
| `no_peer` | 11/14 | 0.786 | baseline |
| `correct_answer_only` | 11/14 | 0.786 | no rescues |
| `correct_auto_evidence` | 12/14 | 0.857 | one rescue |
| `correct_rationale` | 13/14 | 0.929 | two rescues |
| `wrong_answer_only` | 11/14 | 0.786 | no regressions |
| `wrong_auto_evidence` | 9/14 | 0.643 | two regressions |
| `wrong_rationale` | 9/14 | 0.643 | two regressions |

The clean positive auto-evidence case was still DAR case `8`: no-peer answered
`14`, while correct auto-evidence rescued it to `24`. The evidence note did not
include the source final answer:

```text
John's current age (28) minus 20 years equals Jim's age when Digimon came out,
then add 20 years to find Jim's current age.
```

Wrong auto-evidence created right-to-wrong regressions on cases `97` and `4`.
Case `4` is especially clean: the wrong note changed the melting rate relation
to a net gain of `16` snowballs/hour, and the target moved from `5` to `3.75`.

On MATH random8:

| Condition | Correct | Accuracy | Main transition |
| --- | ---: | ---: | --- |
| `no_peer` | 4/8 | 0.500 | two no-peer outputs unparseable |
| `correct_answer_only` | 6/8 | 0.750 | one wrong-to-right plus parse/format help |
| `correct_auto_evidence` | 5/8 | 0.625 | one wrong-to-right |
| `correct_rationale` | 7/8 | 0.875 | strongest condition |
| `wrong_answer_only` | 5/8 | 0.625 | mixed parse/format effects |
| `wrong_auto_evidence` | 5/8 | 0.625 | one surprising rescue |
| `wrong_rationale` | 4/8 | 0.500 | no net gain over no-peer |

The surprising MATH case was `47` (`28800`, circular seating by party blocks).
Both correct auto-evidence and wrong auto-evidence rescued the no-peer answer
`14400` to `28800`. The wrong peer's compressed evidence preserved the useful
block structure while retaining the wrong internal count:

```text
Arrange 3 groups in a circle (2 ways), then arrange 5 Democrats and 5
Republicans within their groups (24 ways each).
```

The target model noticed the structure and repaired the internal count to
`5! = 120`, producing `28800`.

## Things Noticed

The automatic short-evidence surface partially reproduces the hand-written
relation-only signal on DAR, but it is noisier than full rationale and not clean
enough to call a method.

The relation/mechanism handle still looks more alive than answer-only exposure:
on DAR, correct auto-evidence rescued one case without answer adoption, while
wrong auto-evidence caused two regressions despite `peer_answer_adoption_rate =
0.0`.

MATH complicates the story. Correct auto-evidence underperformed correct
answer-only and full rationale. Some MATH problems seem to need more than a
single compressed relation; the full rationale preserves derivation details that
the short surface drops.

Wrong evidence is not uniformly poison. It can contain a recoverable task
skeleton even when its arithmetic or final answer is wrong. MATH case `47` is
the clearest contact point for this: wrong compressed evidence helped because it
preserved the right decomposition.

The old binary label "correct peer" vs "wrong peer" is too crude. More useful
labels may be:

- target predicate preserved or drifted;
- relation skeleton correct or wrong;
- numerical slot correct or wrong;
- final answer exposed or hidden;
- derivation long enough to repair local arithmetic.

## Failures / Friction

The extractor often violated the "do not state the final answer" instruction.
Naive source-answer containment found:

- DAR: `9/28` auto-evidence notes contained the source answer;
- MATH: `7/16` auto-evidence notes contained the source answer.

Some of these are legitimate intermediate equations, but several are clear final
answer leaks. This means the current auto-evidence surface is not a clean
relation-only surface.

The extraction model and target model are the same served Qwen2.5-7B model. That
is fine for contact, but it is not an independent compressor.

The DAR random16 request selected only `14` cases because the saved GSM8K100
trace had only `14` mixed-correctness cases under the current selector.

## Loose Threads

The next pressure should probably be a stricter surface, not a broader method:

- a relation-skeleton extractor that redacts the source final answer before
  extraction;
- a quantity-table surface with a blank final slot;
- an extractor audit that labels target predicate, relation skeleton, numeric
  slots, and answer leakage;
- a paired run comparing `auto_evidence`, `answer_redacted_full_rationale`, and
  `full_rationale` on the same cases.

## Caveats

These are selected disagreement cases with regenerated no-peer baselines. The
auto-evidence condition adds extra model calls and possible compression errors.
The run is useful because it makes the surface itself inspectable; it is not a
claim that automatic evidence compression improves multi-agent communication.
