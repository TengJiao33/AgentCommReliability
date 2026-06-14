# MAD-MM 1237 Raw Role Card

## What This Is

This is a raw-log follow-up to the cross-system role cards.

No model calls. No new script. The point was to touch the original MAD-MM debate
log for case `1237` before letting the "wrong-looking scaffold" phrase become
too smooth.

Source files:

- `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/mad_objective_3agents_2rounds_seed41_debate_log.json`
- `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/mad_3agents_2rounds_seed41_debate_log.json`
- `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/mad_subjective_3agents_2rounds_seed41_debate_log.json`
- `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/comm_trace_madmm_math50_v11.jsonl`

## Case

Question:

```text
Simplify the following expression: $\sqrt{28 + \sqrt{1296}}$
```

Gold answer:

```text
8
```

## Round 1

All debate variants share the same first round.

| Agent | Parsed answer | Role visible in raw response |
| --- | --- | --- |
| Agent1 | `\(\sqrt{34}\)` | says to simplify inner root, add to 28, then take outer root, but never performs `sqrt(1296)=36`. |
| Agent2 | `5` | same high-level operation plan, wrong answer. |
| Agent3 | `\(\sqrt{34}\)` | same high-level operation plan, explicitly notes `1296` is a perfect square, but still stops at wrong final answer. |

The objective mask keeps only Agent3.

That means the retained message is not a correct answer. Its possible role is:

```text
operation scaffold:
  first simplify sqrt(1296);
  then add to 28;
  then take the outer square root.
```

## Objective Round 2

Objective round 2 shows the cleanest scaffold story.

The visible solution in every round-2 prompt is Agent3's first-round message:

```text
Since 1296 is a perfect square, we can find its square root directly.
Then we will add the result to 28 and take the square root of the entire expression.
```

All three round-2 agents then complete the missing arithmetic:

```text
sqrt(1296) = 36
sqrt(28 + 36) = sqrt(64) = 8
```

Final objective answer:

```text
8
```

## Naive Round 2

Naive keeps all three first-round messages.

This creates a stranger surface. Agent3 solves correctly in round 2, but
Agent1 and Agent2 compute the right path in their thinking and still output
`\(\sqrt{34}\)`.

So the naive failure is not simply "no one saw the scaffold." They saw too much
or saw conflicting answer anchors:

```text
\(\sqrt{34}\)
5
\(\sqrt{34}\)
```

Two agents appear pulled back toward the wrong retained answer surface even
after deriving `sqrt(64)=8` in the reasoning text.

Final naive majority:

```text
\(\sqrt{34}\)
```

## Subjective Round 2

Subjective is the important caveat.

For this case, subjective masking retains no first-round messages. Its round-2
prompt is just the original question again.

Even with no visible retained scaffold:

- Agent2 answers `8`;
- Agent3 answers `8`;
- Agent1 produces a malformed answer-like string from its reasoning.

Final subjective majority:

```text
8
```

This means the objective scaffold story is plausible but not sufficient as a
causal explanation. A fresh second pass can also solve this item.

## Role Card

message:

```text
Agent3 round-1 response says to simplify sqrt(1296), add to 28, then take the
outer square root, but answers sqrt(34).
```

parsed answer:

```text
\(\sqrt{34}\)
```

role it played:

```text
operation scaffold, not answer anchor
```

role it lost:

```text
none under objective masking; under answer-only retention it would collapse to
only the wrong parsed answer.
```

downstream effect:

```text
objective: all agents complete the arithmetic and answer 8;
naive: two agents compute 8 in reasoning but still answer sqrt(34);
subjective: no retained scaffold, but a fresh second pass still gets majority 8.
```

what this system makes visible:

```text
MAD-MM messages can carry separable roles:
parsed answer, operation scaffold, and answer-surface anchor.
```

## Things Noticed

This case is less clean than the earlier summary.

The objective retained message has a useful scaffold role, but the subjective
zero-retention run shows that the scaffold was not necessary for the item to be
solved on a second pass. The more interesting contrast may be objective versus
naive: sparse retention removed the wrong answer-surface majority, while full
retention let `sqrt(34)` remain as an answer anchor.

So the role vocabulary should include both:

```text
operation scaffold retained
```

and:

```text
wrong answer-surface anchor suppressed
```

## Caveats

- One case.
- The subjective result is a different generated trajectory, not a controlled
  ablation of the objective prompt.
- The raw logs do not prove why an agent chose its final answer after computing
  the correct intermediate value.
- This should refine the card vocabulary, not become a claim.
