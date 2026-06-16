# Authority Genesis Idea

Date: 2026-06-15

Status: live idea handle / revised framing after external multi-agent pressure.

2026-06-16 revision:

```text
Authority Genesis is no longer the deepest mechanism. It is one visible symptom
of epistemic type erasure across multi-agent communication boundaries.
```

## Why This Exists

This note originally split out the larger idea that emerged after the PACT
authority-injection and typed-boundary runs:

```text
The core object may not be the container. The core object may be how text
acquires authority to update later system state.
```

That was useful, but it is still one step too shallow.

The previous framing said that multi-agent public state contains different
containers: evidence fields, task fields, candidate fields, memory fields,
verifier fields, and final-answer fields. The next framing said that text
acquires different authority depending on its inferred future. That also helped,
but it still risks sounding like a generic single-LLM context-authority problem.

The deeper question is:

```text
When one agent's local computational artifact crosses into another agent's
context, which epistemic type survives the boundary?
```

Agent output is not raw information. It may be evidence, inference, hypothesis,
confidence, task interpretation, partial derivation, action suggestion,
commitment, tool result, memory candidate, or final answer. When it is
serialized as natural language and appended to another agent's context, these
types can collapse into one generic object:

```text
text the next agent may continue from.
```

This document is an incubation memo. Its job is to keep the idea inspectable,
pressure it against existing evidence, and define what would make it real or
make it die.

## Core Guess

The current guess is:

```text
Multi-agent communication often erases the epistemic type of one agent's
intermediate state. Downstream agents then perform invalid casts: hypothesis to
fact, vote to proof, candidate to answer, memory to instruction, partial
derivation to inherited operator, or local conclusion to public progress.
```

Authority is still real, but it is not the primitive object. It is one downstream
force created when the receiver cannot tell what kind of thing the sender's text
was supposed to be.

The model does not only read what peer text says. It also guesses how that text
should be typed in the local communication institution:

- Is this observed evidence or a peer's inference from evidence?
- Is this a tentative hypothesis or a committed answer?
- Is this a confidence report or a social pressure cue?
- Is this a local subproblem result or a global task target?
- Is this a verifier/tool result or generated prose about a result?
- Is this reusable memory or a transient scratch state?
- Is this an action suggestion or an instruction the receiver must obey?

If the communication channel does not preserve that type, the receiver fills in
the type from wording, position, speaker, repetition, majority status, answer
shape, or prompt ritual. That is where wrong text can acquire downstream force.

Working sentence:

```text
Reliable multi-agent communication is not only about how much information is
sent. It is about preserving the epistemic type of the sender's computation
across the receiver boundary.
```

## From Authority Genesis To Type Erasure

The container and authority framings remain useful, but they are now downstream
surface language.

Old framing:

```text
Different containers carry different authority.
```

Intermediate framing:

```text
Containers are the visible residue of authority genesis.
```

Current framing:

```text
Authority genesis is one failure mode of epistemic type erasure.
```

A field such as `Final Answer`, `Action Required`, `Memory`, `Tool Result`, or
`Untrusted Candidate` matters because it tells the receiver how to cast the text.
The same string can be harmless, useful, or destructive depending on whether it
is cast as evidence, inference, hypothesis, task, commitment, social fact,
procedural result, or memory.

In other words:

```text
The same text is not the same communicative act once its epistemic type changes
or disappears.
```

## The Epistemic Types That Get Erased

The suspected root problem is that LLM agents flatten several different kinds of
communicative object into one token stream.

| Epistemic type | Meaning | Invalid cast when erased |
| --- | --- | --- |
| Evidence | I observed this from the task/source. | Peer inference becomes fact. |
| Inference | I derived this from evidence. | A derivation step becomes inherited evidence. |
| Hypothesis | This might explain the case. | Tentative guess becomes task state. |
| Confidence | I am more or less sure. | Confidence becomes correctness. |
| Task interpretation | I think the question asks for X. | Peer target becomes the receiver's answer contract. |
| Partial derivation | This local operator/role/equation seemed useful. | Local scaffold becomes inherited operator. |
| Candidate answer | This is one possible final. | Candidate becomes answer anchor. |
| Commitment | This is my final answer. | One agent's commitment becomes public commitment. |
| Social state | Others/most agents believe this. | Vote becomes proof. |
| Procedural result | A verifier/tool/system recorded this. | Generated prose becomes external validation. |
| Memory | This should persist for later. | Transient text becomes reusable state. |
| Action suggestion | A later agent could do this. | Suggestion becomes instruction. |

Traditional software systems usually separate these by data structures,
permissions, call paths, commit operations, or provenance tags. In many LLM-agent
prompts they are all nearby text. The receiver must infer type from wording,
position, speaker, labels, repetition, answer shape, and local prompt ritual.

That cross-boundary type inference is now the thing to study.

## Why This Remains Multi-Agent

The generic single-LLM problem is "context can influence a model." That is not
enough.

The multi-agent object is sharper:

```text
One independent reasoning process emits an intermediate computational artifact,
and another independent reasoning process must decide what kind of artifact it
is allowed to inherit.
```

The uniqueness is not that text appears in context. It is that the text carries
lost provenance:

- which agent produced it;
- what local evidence that agent saw;
- what was hidden from that agent;
- whether the sender meant evidence, inference, hypothesis, or commitment;
- whether the message was private, peer-to-peer, broadcast, aggregated, verified,
  admitted, or persisted;
- whether later agents are supposed to read it, challenge it, reuse it, or obey
  it.

If the communication interface preserves these distinctions, the receiver can
use peer information without inheriting the wrong type. If it erases them, the
receiver performs an implicit cast inside the LLM black box.

## Local Evidence That Points Here

### PACT Authority/Evidence Stress

`reports/20260615-pact-authority-evidence-stress-qwen25-14b.md` shows that
changing public-field authority can change answers while keeping much of the
task/evidence surface fixed.

On `32` positive target-focus rows:

- trusted-root original public state: EM `0.812`, F1 `0.865`;
- injected authoritative `Action Required`: EM `0.594`, F1 `0.695`;
- delegated public authority as active task: EM `0.344`, F1 `0.525`;
- frozen question-derived target: EM `0.844`, F1 `0.911`;
- final-answer candidate lure: EM `0.469`, F1 `0.633`.

This does not prove authority genesis, but it says public text can steer more
than evidence use. It can rewrite what the model behaves as if it is answering.

### PACT Authority Injection Arena

`reports/20260615-pact-authority-injection-arena-qwen25-14b.md` makes the
pressure stronger. Over `26` base-correct positive rows:

- `wrong_contract_public_task`: `21/26` authority violations, AVR `0.808`;
- `forged_final_commitment`: `14/26` authority violations, AVR `0.538`;
- plain `imperative_public_task`: only `3/26`, AVR `0.115`;
- typed quarantine rescued many pressure failures, but also created `6/26`
  violations when it included a visible candidate.

The important hint is not simply that wrong content hurts. Plain imperative
wording hurts much less than wrong answer-contract or forged commitment
wording. The stronger perturbations are the ones that make text look like it
has the future of a task contract or final answer.

### Typed Boundary Split

`reports/20260615-pact-typed-boundary-split-qwen25-14b.md` is the cleanest
current artifact.

On the same `26` base-correct positive rows:

- typed no-candidate and typed hidden-candidate arms each create only `1/26`
  new authority violations;
- they rescue `20/21` wrong-contract failures and `13/14` forged-final
  failures;
- making the candidate visible raises new violations to `7/26`, drops positive
  EM from `0.875` to `0.625`, and copies visible candidates in `8/32`
  positive rows;
- extract-first reduces the visible-candidate damage only slightly.

This says the field label is not enough. A visible candidate still has the
shape of something that may be committed. In the revised framing, the key
failure is an invalid cast: a `candidate` object is not preserved as candidate,
so the receiver treats it as a possible answer anchor. Hiding it removes that
cast opportunity from the model-visible channel.

### MATH Peer Influence

`reports/20260615-typed-public-state-math200-statistical-pressure.md` and
`reports/20260615-math200-peer-claim-hygiene.md` prevent the idea from becoming
too PACT-only or too answer-copy-only.

On a cleaned MATH peer-influence subset, wrong full rationale is the strongest
harm surface, while wrong typed public state and wrong equation surface are
lower-harm but not harmless. Manual seed labels show final-answer authority is
not the whole channel:

- among `21` labeled harms, `10` have visible final-answer authority;
- `11` occur with the final-answer slot hidden;
- `18` involve wrong relation skeletons;
- `14` involve wrong numeric/role slots.

That points to a broader type-erasure process. The harm is not only final-answer
authority. A wrong relation skeleton, role binding, or equation surface can be
inherited as an operator. This is exactly the kind of invalid cast the revised
idea should test.

## External Pressure

This idea is not born in isolation. It collides with nearby public work:

- Indirect prompt injection argues that LLM-integrated applications blur the
  line between data and instructions:
  https://arxiv.org/abs/2302.12173
- NCSC argues that current LLMs do not enforce a hard instruction/data boundary
  inside prompts and should be treated as inherently confusable:
  https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection
- The classic confused deputy problem says a system can fail when authority
  from different sources is not kept apart:
  https://css.csail.mit.edu/6.858/2015/readings/confused-deputy.html
- Secure information-flow work treats unauthorized flow as a system-level
  property, not merely a bad string:
  https://www.cs.nmt.edu/~doshin/t/s06/cs589/pub/7.Denning-LMIF.pdf
- Speech-act theory gives useful pressure from another direction: utterances
  are not only propositions; they can be requests, promises, warnings,
  declarations, and other acts:
  https://plato.stanford.edu/entries/speech-acts/
- A later PDF pressure pass downloaded and read multi-agent-specific work under
  `papers/external-pressure-20260616/`; see
  `reports/20260616-multiagent-specificity-external-pdf-pressure.md`.
  The most relevant pressure came from:
  - Benefits and Limitations of Communication in Multi-Agent Reasoning:
    communication graphs, communication budget, and depth/resource regimes;
  - Cost of Consensus and Talk Isn't Always Cheap: vulnerability, recovery,
    modal sycophancy, oracle gap, and peer-vs-self controls;
  - HIDDENBENCH: distributed information surfacing and premature convergence;
  - PACT and DeLM: public/shared-state admission as the communication boundary;
  - CaMeL: trusted control/data-flow separation as the generic negative
    boundary.

The project should not claim these areas as new. The possible gap is narrower:

```text
In multi-agent LLM communication, what happens when the epistemic type of a
sender's computational artifact is erased before the receiver inherits it?
```

## Candidate Name

Current working names:

- epistemic type erasure in multi-agent communication;
- information identity erasure;
- cross-agent type safety;
- authority genesis;
- textual authority formation;
- communicative authority transfer;
- institutional state induction;
- speech-act collapse in LLM public state.

Best current short name:

```text
Epistemic Type Erasure
```

`Authority Genesis` remains useful as the historical handle and as one symptom
family. It should not remain the deepest mechanism name unless the evidence
specifically concerns commitment, memory, task, or procedural authority.

## What Would Make This Idea Real

The idea becomes more real if we can show paired behavior differences between
type-erased and type-preserved communication:

```text
Same task, same sender artifact, same receiver model; the erased channel gives
flat peer text, while the preserved channel explicitly marks evidence,
inference, hypothesis, confidence, dependency, commitment status, and missing
source context. Downstream invalid casts decrease without destroying useful
evidence transfer.
```

The old authority ladder remains a useful sub-probe, but no longer carries the
whole idea.

Old ladder as sub-probe:

| Level | Added future signal | Hypothesis |
| --- | --- | --- |
| 0 | raw mention inside evidence | low authority unless semantically useful |
| 1 | answer-shaped span | more attraction |
| 2 | peer claim | social/evidential uptake |
| 3 | majority or consensus claim | stronger social authority |
| 4 | previous final answer | commitment authority |
| 5 | verifier/tool-approved result | procedural authority |
| 6 | saved memory / public state | persistence authority |
| 7 | active task / action-required field | task authority |
| 8 | final answer to submit | full commitment authority |

The revised decisive test is not whether all levels are harmful. The test is
whether failures can be explained as invalid casts, and whether preserving type
information changes those casts:

- hypothesis to fact;
- candidate to final answer;
- vote/majority to proof;
- memory entry to instruction;
- verifier prose to external validation;
- partial equation to inherited operator;
- local task interpretation to global answer contract.

## What Would Kill Or Demote It

Retire or demote the idea if:

- the effect only appears in PACT saved-field re-answering and disappears in
  MATH, rule-following, or another public-state task;
- behavior is explained mostly by answer copying, strict-span formatting, or
  parser artifacts;
- type-preserved channels do not reduce invalid casts relative to type-erased
  channels;
- peer/public/admission/reuse transitions add no explanatory power beyond
  isolated self-correction and inert-context controls;
- hiding candidates only helps because it removes distractor tokens, not
  because it preserves or removes a communicative type;
- full-loop agent runs do not reproduce the saved-field pressure effects;
- stronger models treat typed boundaries literally enough that the type-erasure
  curve collapses.

If any of these happen, the useful remnant may still be a PACT prompt-surface
diagnostic, but not the deeper idea.

## What This Is Not

This is not yet:

- a claim that typed public state is a method;
- a claim that answer-contract verification is novel;
- a claim that containers alone solve reliability;
- a claim that all communication failures are authority failures;
- a claim that prompt labels enforce boundaries;
- a claim that hidden metadata is always safe;
- a claim that every context-authority problem is a multi-agent problem;
- a population estimate.

The evidence/content failure layer remains large in PACT bridge audits.
MATH relation and numeric-role failures show that final-answer authority is only
one channel. Runtime verifier attempts have also failed badly enough that the
boundary mechanism should not be assumed to be another zero-shot judge. The new
claim should be about communication interfaces preserving or erasing epistemic
type, not about asking the same receiver model to obey a longer warning.

## Next Pressure Object

The next object should not be another local prompt tweak or a detached new
benchmark. It should extend the existing PACT/MATH Authority Genesis artifacts
into a type-erasure pressure object.

Design principle:

```text
Do not throw away the ladder. Reinterpret each harmful artifact as a sender
artifact with an erased or preserved epistemic type.
```

Minimal design:

- start from existing MATH Authority Genesis violation/source rows, especially
  relation skeleton, numeric-role binding, equation surface, and wrong-final
  artifacts;
- keep the trusted problem and the receiver's previous correct solution fixed;
- compare a type-erased channel against type-preserved channels:
  - erased peer message: natural-language peer artifact;
  - preserved evidence/inference split;
  - preserved hypothesis with low or unknown confidence;
  - preserved partial-derivation/operator warning;
  - preserved candidate answer marked non-commitment;
  - preserved provenance/missing-source context;
- keep the old future-signal variants only as a smaller side axis, not the
  whole experiment;
- include self-revision and unrelated peer-like context controls borrowed from
  Cost of Consensus;
- score only paired movement from base-correct cases.

Why MATH first:

- it already has wrong relation, numeric-role, equation, and final-answer
  artifacts;
- the latest mechanism audit already separates copy from operator uptake;
- the biggest caveat, case concentration around `math159` and `math121`, can be
  handled by per-case caps and deconcentrated source selection;
- it remains connected to prior work rather than starting a new line.

Primary measurements:

- Invalid Cast Rate: base-correct cases where receiver behavior indicates
  hypothesis-to-fact, candidate-to-answer, vote-to-proof, memory-to-instruction,
  or operator inheritance;
- Type Preservation Rescue Rate: erased-channel failures repaired by preserving
  epistemic type;
- Hidden/Visible Gap: behavior difference when the same candidate is evaluator
  metadata versus model-visible text;
- Operator-Uptake Rate: wrong relation/numeric/equation artifact changes the
  solution without exact wrong-answer copying;
- Useful Evidence Retention: correct peer evidence still helps when type is
  preserved;
- Oracle Gap / Team Pool Gap if moved into a real multi-agent loop later.

## Current Story Shape

If this survives, the paper spine might become:

```text
A: Multi-agent LLM systems represent communication, memory, verification, and
   decisions through model-visible natural-language handoffs.

B: These handoffs can erase the epistemic type of the sender's computational
   artifact. Evidence, inference, hypothesis, confidence, candidate answer,
   commitment, memory, tool result, and action suggestion collapse into flat
   peer text. The receiver then performs implicit invalid casts inside the LLM.

C: Type-erasure tests compare erased and type-preserved communication channels
   while holding semantic content fixed. Authority Genesis ladders become one
   sub-probe for commitment/task/procedural casts.

M: Downstream answer correctness, invalid-cast rate, operator uptake,
   type-preservation rescue, useful evidence retention, hidden/visible gaps,
   and eventually oracle gap in full multi-agent loops.

D: Paired ablations showing that preserving evidence/inference/hypothesis/
   candidate/commitment provenance reduces diagnosed failures without merely
   deleting useful peer information.
```

This is currently a live diagnostic handle, not a solid story. It becomes solid
only if type-preserved channels reduce invalid casts across deconcentrated cases
and if the mechanism explains behavior beyond ordinary distractor copying.

## Bottom Line

The most important sentence for now:

```text
The question is not only what information an agent receives. The question is
what epistemic type survives when another agent's intermediate state crosses
the communication boundary.
```

If that type is erased, the receiver may inherit the wrong thing: a hypothesis
as fact, a vote as proof, a candidate as answer, a memory note as instruction,
or a partial equation as an operator. Authority Genesis is the old name for the
cases where that invalid cast gives text downstream force.
