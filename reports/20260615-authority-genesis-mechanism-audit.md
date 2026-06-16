# Authority Genesis Mechanism Audit

Date: 2026-06-15

Status: further exploration / seed-label audit, not a final taxonomy.

## What We Tried

Built a mechanism-audit surface for the first Authority Genesis Ladder run.
This is not a new model run. It joins the existing ladder packet, evaluated
rows, and paired deltas, then extracts:

- base-correct `wrong_lure` rows that become wrong under a future signal;
- base-wrong `correct_gold` rows rescued by a future signal;
- deterministic seed labels for copy kind and likely mechanism family.

Artifacts:

- script: `scripts/build_authority_genesis_mechanism_audit.py`
- audit directory:
  `experiments/20260615-local-authority-genesis-ladder-mechanism-audit/`
- source run:
  `experiments/20260615-2318-a8002-authority-genesis-ladder-qwen25-14b/`

The audit is deliberately modest. The seed labels are for inspection, not
population-level manual labels.

## Why This Pressure

The previous ladder showed that hidden metadata was harmless while visible
future signals could change answers. But that result can still be explained too
thinly:

```text
Maybe the model simply copies a visible candidate.
```

The stronger Authority Genesis idea needs a harder read:

```text
Does the model only adopt content, or does it adopt the injected text's right
to change the task, answer contract, relation role, answerability status, or
commitment state?
```

This audit asks whether the failure surface contains only answer copying, or
whether future signals also induce state-transition behavior.

## What Happened

The audit extracted `46` wrong-lure authority-violation cards and `20`
correct-gold utility cards.

Wrong-lure violation copy kinds:

| Copy kind | Count |
| --- | ---: |
| exact injected copy | 17 |
| partial or surface overlap | 13 |
| no direct copy | 16 |

Wrong-lure primary mechanism seed labels:

| Primary seed | Count |
| --- | ---: |
| relation or entity-role uptake | 19 |
| answer-contract surface uptake | 11 |
| refusal / insufficient-evidence drift | 10 |
| short-span / granularity uptake | 6 |

Correct-gold utility is much thinner: all `20/20` utility cards are exact
injected-content copies. That means authority can help by making the right
short answer salient, but the harmful side is not reducible to exact copying.

## Things Noticed

The important split is now:

```text
referential uptake versus jurisdictional uptake
```

Referential uptake means the model adopts the injected content as a string or
surface. Jurisdictional uptake means the model adopts the injected artifact's
right to decide what kind of answer is allowed, which entity/relation is in
scope, or whether the question is answerable.

The ladder has both. Exact copying accounts for `17/46` violations, but
`16/46` have no direct copy and `13/46` only partially overlap the injected
content. That is the current strongest reason not to collapse Authority Genesis
into ordinary candidate-copying.

The largest seed family is relation/entity-role uptake (`19/46`). Examples
include cases where the answer flips toward the wrong role or entity rather
than simply copying the candidate string. This is the PACT-side version of the
MATH suspicion: a future-looking artifact can donate a relation skeleton, not
just a final answer.

The Boss Bailey control is the sharpest non-copy warning. The baseline gives
`2003`, but several future signals move the model into an
insufficient-evidence/refusal explanation. The injected artifact is not merely
copied; it changes the local answerability protocol. This is exactly the kind
of behavior the container-only framing misses.

`active_task_required` remains the strongest signal, but more importantly it
is broad: it touches answer-contract surface uptake, refusal drift,
relation/entity-role uptake, and span/granularity uptake. That suggests task
authority is not one mechanism. It is a high-level license under which several
state transitions become available.

Correct-gold mirrors should be interpreted carefully. They rescue by exact
copying, mostly in answer-contract and short-span cases. This is useful as an
oracle control, but it does not show a deployable protocol and it does not
explain the richer wrong-lure failure surface.

## Interpretation

This pushes the idea one level deeper.

The previous sentence was:

```text
Authority is not a property of a message. Authority is an inferred future of a
message.
```

The new candidate sentence is:

```text
The inferred future of a message selects a state-transition operator over the
message.
```

That operator may be:

| Operator | What the model behaves as if the text can do |
| --- | --- |
| assert | provide evidence or a candidate content string |
| bind | attach an entity, number, or role to the task |
| rewrite | change the task or answer contract |
| declare | decide answerability or insufficiency |
| commit | become final answer, memory, verifier result, or shared state |

This is a better answer to the earlier question, "where does the container
itself come from?"

Containers may be the visible residue of these inferred state-transition
operators. A field like `Memory`, `Verifier Result`, `Peer Claim`, or `Action
Required` matters because it tells the model not only what the text says, but
what the text is licensed to do next.

This framing is more radical than the container ladder and more falsifiable
than the metaphor. If it is right, future experiments should distinguish
content adoption from operator adoption.

## Current Story Status

Still not a solid paper story.

But the handle is more alive than before. The evidence now supports a sharper
diagnostic shape:

```text
Authority Genesis is not only candidate attraction. It is state-transition
confusion in model-visible public text.
```

The current C-shape is no longer only a ladder. It may become a protocol or
benchmark that tests whether agent communication separates:

- content that may be read;
- roles that may be bound;
- contracts that may be rewritten;
- commitments that may be persisted;
- procedural outputs that may be trusted.

## Caveats

- Seed labels are deterministic audit labels, not final manual labels.
- The packet is small and selected: `24` PACT source cases.
- The wrong-lure rows come from prior observed outputs, so they mix semantic
  errors, span/granularity errors, answer-contract surfaces, and refusal
  surfaces.
- Exact-match scoring can mark verbose but semantically recoverable outputs as
  failures.
- Qwen2.5-14B only.
- This is still saved-field re-answering, not a full PACT rerun.
- The MATH relation/numeric-role bridge has not yet been run under this exact
  state-transition framing.

## Next Pressure

The next step should be larger and stranger than another PACT wording tweak:

```text
Build a state-transition ladder for MATH peer influence.
```

It should hold the problem fixed and inject the same wrong artifact under
different inferred futures, but the artifact should not be only a final answer.
It should include:

- wrong relation skeleton;
- wrong numeric or role binding;
- wrong equation surface;
- wrong final answer.

The scoring should separate:

- exact answer copy;
- relation-skeleton uptake;
- numeric-role uptake;
- answerability or refusal drift;
- final-answer commitment.

If MATH shows only exact answer copy, Authority Genesis should shrink back
toward PACT public-state/candidate attraction. If MATH shows role or relation
operator uptake without final-answer copying, the idea becomes a genuinely
cross-task story candidate.
