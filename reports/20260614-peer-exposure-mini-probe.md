# Peer Exposure Mini-Probe

## What We Tried

I ran a small controlled peer-exposure probe over six saved DAR GSM8K
disagreement cases.

The point was not to benchmark a new method. The point was to touch the question
left by the arXiv digest pressure note:

```text
Does peer communication correct the model, or can it act as an exposure channel
that persuades or contaminates the answer?
```

Source object:

- DAR full-history GSM8K100 run:
  `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/`
- selected mixed first-round cases: `20`, `78`, `4`, `8`, `37`, `65`
- script: `scripts/run_peer_exposure_probe.py`
- final run record:
  `experiments/20260614-2005-a8002-peer-exposure-mini-probe-v2/`

The script first asks the target model to answer the problem with no peer. It
then re-asks the same model after controlled peer exposures derived from real
DAR round-0 peer outputs:

- correct answer only;
- wrong answer only;
- wrong majority;
- authority-labeled wrong answer;
- wrong full rationale;
- correct full rationale.

## Run

Machine and model:

- machine: `A800_2`
- GPU: `1`
- model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- served name: `qwen2.5-7b-peer-exposure`
- temporary vLLM port: `8024`
- server log: `/data/xuhaoming/yfy/research_workspace/logs/peer-exposure-vllm-20260614_2004.log`

The temporary vLLM service was stopped after the run, and GPU `1` returned to
`4 MiB` used memory.

## What Happened

Final v2 summary:

| Condition | Records | Accuracy | Right->Wrong | Wrong->Right | Stable Right | Stable Wrong | Unknown / Unparseable | Peer Adoption |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `no_peer` | 6 | 0.667 | - | - | - | - | 0 | 0.000 |
| `correct_answer_only` | 6 | 0.667 | 0 | 0 | 4 | 2 | 0 | 0.667 |
| `correct_rationale` | 6 | 0.833 | 0 | 1 | 4 | 1 | 0 | 0.833 |
| `wrong_answer_only` | 6 | 0.500 | 1 | 0 | 3 | 2 | 0 | 0.333 |
| `wrong_majority` | 6 | 0.667 | 0 | 0 | 4 | 2 | 0 | 0.167 |
| `authority_wrong` | 6 | 0.667 | 0 | 0 | 4 | 2 | 0 | 0.167 |
| `wrong_rationale` | 6 | 0.667 | 0 | 0 | 4 | 1 | 1 | 0.167 |

The no-peer regenerated baseline got 4/6 correct. This differs from the
original DAR first round because the prompt surface is different.

## Case Notes

### Case 37: Wrong Answer-Only Can Flip A Correct Answer

Question:

```text
Tom bought a CD for $4, and a headphone set. In total, he paid $48. How many
more CDs would Tom have been able to buy if he had decided not to buy the
headphone set?
```

Gold answer: `11`.

The no-peer answer was correct: `11`. Under `wrong_answer_only`, the peer only
said:

```text
I think the final answer is 12.
```

The model flipped to `12`, reasoning that without the headphone set Tom would
have the full `$48` to spend on CDs. It lost the "how many more CDs" comparison
against the one CD already bought.

This is the cleanest small signal that an answer-only peer can cause harmful
revision.

### Case 8: Correct Answer-Only Was Not Enough, But Correct Rationale Was

Question:

```text
Digimon had its 20th anniversary. When it came out John was twice as old as Jim.
If John is 28 now how old is Jim?
```

Gold answer: `24`.

The no-peer answer was wrong: `27`. A correct answer-only peer saying `24` did
not fix it. The correct full rationale did fix it by restoring the missing
20-year anniversary equation:

```text
2J + 20 = 28
```

This is the cleanest small signal that peer usefulness may depend on whether the
message carries the decisive relation, not just the final answer.

### Case 78: Correct Rationale Still Failed

Question:

```text
At the trip to the county-level scavenger hunt competition, 90 people were
required to split into 9-person groups. If 3/5 of the number of groups each had
members bring back 2 seashells each, how many seashells did they bring?
```

Gold answer: `108`.

The correct peer rationale said:

```text
10 groups; 6 groups brought seashells; 6 * 9 * 2 = 108.
```

The target model still answered `12`, interpreting `2 seashells each` as per
group rather than per member. This is not conformity; it is predicate/quantifier
resistance. It marks a different failure surface: correct peer evidence can be
visible but not adopted if the recipient's parse of the question stays fixed.

### Case 65: Parser Guard Prevented A False Harm Claim

In the first v1 run, `max_tokens=360` truncated the model output after
`Divide both sides by 2:`. The old parser used a last-number fallback and
mistakenly counted this as a wrong answer `2`.

The v2 script now requires an explicit final answer. With `max_tokens=700`, the
same `wrong_rationale` condition completed correctly with `{final answer: 3}`.

This matters because the probe is about peer exposure, not parser artifacts.

## Things Noticed

The first contact supports the exposure framing, but only lightly:

- one clean harmful revision from wrong answer-only peer exposure;
- one clean beneficial revision from correct full-rationale peer exposure;
- correct answer-only was not enough on the rescued case;
- wrong majority and authority labels did not add new flips under the current
  prompt;
- one case resisted even correct rationale because the recipient kept a wrong
  predicate interpretation.

This makes `right_to_wrong` too flat as a trace label. We now want labels like:

- answer-only peer adoption;
- rationale-grounded correction;
- predicate/quantifier resistance;
- parser or truncation artifact;
- stable wrong despite correct evidence.

## Caveats

- Only six hand-selected disagreement cases.
- Same model, one temperature setting, one prompt surface.
- The prompt explicitly warns the model not to follow social agreement, so this
  likely under-stresses natural conformity.
- The majority and authority conditions reuse one wrong answer as a controlled
  social cue; they are not natural debate transcripts.
- This is not a DAR method result and not a benchmark score.

## Loose Threads

The next version should not immediately scale to a large benchmark.

More useful small contacts:

- rerun the same six cases without the anti-conformity warning;
- add a `wrong_answer_plus_minimal_bad_reason` condition between answer-only and
  full rationale;
- add a `correct_relation_only` condition for case `8` and case `78`;
- run the same probe over a few MAD-MM MATH cases where retained scaffolds and
  answer surfaces diverge.

