# Target Role Lens Across Baselines

## What This Is

This is a sideways note.

PACT made `target role` visible because its public action-state messages contain
fields like `Action Required`, `Environment State`, `Action Result`, and the
later compact `Target Slot`. The question here is whether the same lens has a
shadow in DAR, MAD-MM, and MOC, or whether it is only a PACT artifact.

No new model run was launched. No new script was added.

Sources:

- `reports/_archive/20260616-pruned/20260614-pact-question-target-postcards.md`
- `reports/_archive/20260616-pruned/20260613-madmm-dar-trace-case-followup.md`
- `reports/_archive/20260616-pruned/20260614-dar-sample20-retained-surface-note.md`
- `reports/_archive/20260616-pruned/20260614-dar-context-failure-audit.md`
- `reports/_archive/20260616-pruned/20260612-madmm-trace-message-retention.md`
- `reports/_archive/20260616-pruned/20260613-moc-forced-merge-smoke.md`
- `experiments/_archive/20260616-pruned/20260613-1740-a8002-moc-hopcheck-n5/README.md`
- `reports/_archive/20260616-pruned/20260614-real-trace-v11-regime-labels.md`
- `reports/_archive/20260616-pruned/20260614-derived-context-event-audit.md`

## The Lens From PACT

The postcard vocabulary was:

```text
answer_type
clue_object
bridge_entity
requested_relation
required_qualifier
forbidden_replacement
surface_failure
```

PACT exposes these because agents write public state. Failures can be seen as
target role movement:

- clue object becomes answer object;
- bridge entity replaces final entity;
- requested predicate changes;
- answer granularity changes;
- final answer surface fails even when target state is stable.

The important caveat from the postcards is that target movement is sometimes
the task. HotpotQA needs motion through bridge entities; it only becomes a
failure when the role changes in the wrong way.

## DAR: Role Hidden Inside Retained Message Surface

DAR does not expose a public target field. It exposes retained peer messages.
So the lens changes shape:

```text
target role -> role of retained evidence inside the next prompt
```

Case `20` is the useful pressure point.

Round 0 had:

- Agent1: parsed answer `7`, correct reasoning;
- Agent2: parsed answer `120`, genuinely wrong path;
- Agent3: parsed answer `700`, but reasoning contains the useful calculation
  `$7.00`.

Answer-only retained context collapses Agent3 to:

```text
Previous parsed final answer: 700.0
```

That destroys the role distinction between:

```text
wrong final marker
```

and:

```text
useful calculation scaffold with malformed final answer
```

In PACT language, this is not anchor drift. It is surface flattening. The
message loses the evidence role that would let another agent reinterpret the
answer.

DAR case `5` adds a second warning. Correct context was visible, but the next
round still lost the answer. So even if target/evidence role is preserved in
context, continuation and final-answer formatting can still fail.

Small note to carry:

```text
DAR target role is not a field. It is whether retained text preserves enough
evidence role to let the recipient repair or reuse it.
```

## MAD-MM: Role As Memory Anchor

MAD-MM also does not expose a public target field. It exposes full prior
reasoning, masked or unmasked.

Here the target-role lens becomes:

```text
target role -> what the retained memory anchors the next round to do
```

The GSM8K short-subset cases `214` and `1227` show the blunt version:

- `214`: objective masking kept the wrong `24` memory while correct `8`
  memories existed; round 2 converged to `24`.
- `1227`: the correct minority `66` was not preserved; several debate variants
  collapsed to wrong majority memory.

The MATH50 cases make it less simple:

- `494`: retained memory works as a correct-answer anchor.
- `1237`: retained memory has a wrong-looking answer but useful reasoning
  scaffold.
- `2965`: objective masking drops two correct agents yet retains enough partial
  setup for the next round to solve.

This is close to DAR sample `20`: answer correctness is too thin a label for a
message's role.

PACT taught us to separate `answer object`, `bridge entity`, and `requested
relation`. MAD-MM asks for another separation:

```text
parsed answer
reasoning scaffold
operation target
next-round anchor
```

Small note to carry:

```text
MAD-MM target role may live in the operation or scaffold a memory induces, not
in its parsed final answer.
```

## MOC: Role May Be Lost In Compression, But We Barely See It Yet

MOC is the least touched by this lens so far.

The hop-depth checks show the structural path:

- hop1: neighbor context, no merge;
- hop2 forced merge: compressed summaries, merge source IDs and represented
  sources recorded in sidecar events;
- current task slice: GSM8K, saturated at 5/5.

The PACT target-role question would become:

```text
when multiple source messages are merged, does the summary preserve which
source carried the clue, which carried the bridge, and which carried the answer
slot?
```

But current MOC evidence is mostly trace coverage and token cost. The GSM8K
smoke does not pressure clue-object versus answer-object or predicate survival.
It tells us that compressed public state exists, not whether it preserves target
roles.

So the honest note is negative:

```text
MOC is a plausible place for target-role loss through summarization, but the
current run does not expose it.
```

The next MOC contact, if we ever go there, should not be more saturated
arithmetic. It should be a tiny k-hop or split-evidence task where a merge can
actually blur clue, bridge, and answer roles.

## PACT Compared To The Others

| Baseline | Where Target Role Is Visible | What Can Go Wrong | Current Limitation |
| --- | --- | --- | --- |
| PACT | explicit public action-state fields | public target drifts, bridge becomes answer, predicate/granularity shifts, final commitment fails | easy to over-focus on prompt fields |
| DAR | retained peer message surface | answer-only removes useful evidence role; correct context can still fail after update | no raw recipient prompt; arithmetic is saturated |
| MAD-MM | retained or broadcast reasoning memory | wrong memory anchors next round; useful scaffold may have wrong parsed answer | role labels are manual; no explicit target field |
| MOC | compressed neighbor summary / represented sources | possible summary loss of clue/bridge/answer roles | current trace does not pressure the question |

## What Seems Shared

The shared thing is not a `Target Slot` field.

The shared thing is more like:

```text
messages have roles relative to the question,
and communication can preserve, erase, flatten, or replace those roles.
```

PACT makes the role textual and inspectable.

DAR shows role flattening: answer-only can erase the difference between wrong
final marker and useful calculation evidence.

MAD-MM shows role anchoring: retained reasoning can pull the next round toward a
wrong answer, or help despite a wrong parsed answer.

MOC suggests role compression: a summary may preserve the answer but lose which
piece was clue, bridge, or requested relation. We have not really tested that
yet.

## A Maybe-Useful Negative Boundary

Do not turn the PACT target-state idea into:

```text
add target slot fields everywhere
```

That would miss what the other systems are showing.

In DAR and MAD-MM, the issue is not that a target field is absent. The issue is
that the communicated message surface can fail to preserve the role of evidence
or reasoning relative to the question.

In MOC, the issue may be whether compression preserves role structure, not
whether it names a target.

## Loose Next Drift

If we keep touching this, the gentlest next move is a tiny role-card file across
systems, with one or two cases per baseline:

```text
message:
parsed answer:
role it played:
role it lost:
downstream effect:
```

That would be more faithful than writing a checker right now.

Possible cards:

- PACT `199`: distractor anchor replaces answer entity.
- PACT `176`: useful bridge refinement.
- DAR `20`: parsed-wrong message carries useful calculation evidence.
- DAR `5`: correct context visible but lost after continuation.
- MAD-MM `1237`: wrong-looking retained answer carries useful operation scaffold.
- MAD-MM `214`: wrong retained answer anchors final wrong answer.
- MOC hop2: compressed merge exists, but role loss cannot yet be judged.

## Caveats

- This is interpretive alignment across existing notes, not new evidence.
- The baselines are on different tasks and trace surfaces.
- PACT's explicit fields make it easier to see target movement than the other
  systems; that visibility difference should not be mistaken for a behavioral
  difference.
- MOC is mostly a placeholder in this lens until a less saturated task or more
  role-sensitive trace is available.
