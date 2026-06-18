# Cross-System Role Cards

## Why This Exists

This is a small card file, not a framework.

After the PACT target-state postcards, the question became whether other
baselines have the same problem under different surfaces. These cards keep the
comparison concrete.

Template:

```text
message:
parsed answer:
role it played:
role it lost:
downstream effect:
what this system makes visible:
```

The first version had no model calls and no script. Later MOC follow-ups added
one CPU-only role probe and one merge-only LLM prompt audit.

## PACT Cards

### PACT 199: Distractor Anchor Replaces Answer Entity

message:
the public state alternates between `1999 Odisha cyclone` and `Cyclone Gonu`,
while the final answer becomes `Kathantara`.

parsed answer:
`Kathantara`, wrong for the gold `1999 Odisha cyclone`.

role it played:
the film paragraph should be evidence for the cyclone answer.

role it lost:
the answer role moved from cyclone to film/distractor context. The public target
stopped holding the difference between evidence object and answer object.

downstream effect:
the agent answers a film title instead of the cyclone.

what this system makes visible:
PACT exposes target-role drift directly in public fields.

### PACT 176: Useful Bridge Refinement

message:
the public state moves from Hanna Leena Kristiina Varis and her works to
Albertina and finally to `drawings`.

parsed answer:
`drawings`, correct.

role it played:
the early artist/museum target was a bridge, not the final answer slot.

role it lost:
none, or at least not harmfully. The target moved in the way the question
required.

downstream effect:
compact target movement rescues the answer surface.

what this system makes visible:
not all target motion is drift. Some target motion is the task.

## DAR Cards

### DAR 20: Parsed-Wrong Message Carries Useful Calculation Evidence

message:
Agent3 is parsed as final answer `700`, but its reasoning contains the useful
calculation `$7.00`.

parsed answer:
`700`, wrong by parser; semantically, the reasoning contains the correct amount.

role it played:
in full retained form, it can act as calculation evidence or a scaffold for
another agent.

role it lost:
in answer-only retained form, it becomes only:

```text
Previous parsed final answer: 700.0
```

That collapses useful evidence into a wrong answer token.

downstream effect:
guard-full fixes the case; answer-only variants do not.

what this system makes visible:
DAR exposes message-surface role loss. The problem is not target-slot drift, but
evidence role flattening.

### DAR 5: Correct Context Visible, Still Lost

message:
the original filter retains two correct first-round agents for a case whose gold
answer is `5`.

parsed answer:
round 0 has correct visible answers; round 1 produces empty or wrong final
answers.

role it played:
the retained messages should provide a correct answer anchor.

role it lost:
not obviously lost at the retention surface. The failure moves later, into
continuation or formatting.

downstream effect:
the case becomes right-to-wrong despite correct visible context.

what this system makes visible:
preserving the right role in context is not enough if the recipient update or
answer parser fails.

## MAD-MM Cards

### MAD-MM 214: Wrong Memory Anchors The Next Round

message:
round 1 debate has answers `[8, 8, 24]`, with `8` correct. Objective masking
keeps only the wrong `24` memory.

parsed answer:
retained parsed answer `24`, wrong.

role it played:
the retained memory becomes the only visible peer anchor for round 2.

role it lost:
the correct-answer minority role disappears from the recipient context.

downstream effect:
all three round-2 agents answer `24`.

what this system makes visible:
MAD-MM exposes role through memory selection. A wrong retained memory can
retarget the debate without any explicit target field.

### MAD-MM 1237: Wrong-Looking Scaffold Helps

message:
objective masking retains Agent3, whose parsed answer is wrong-looking, but its
reasoning starts with the useful operation needed to solve the problem.

parsed answer:
wrong or incomplete in round 1.

role it played:
operation scaffold. The retained message tells later agents what computation to
perform, even though the final answer is not yet right.

role it lost:
none in this case. The message's role is easy to mislabel if we only look at
parsed correctness.

downstream effect:
round 2 recomputes and reaches the correct answer.

what this system makes visible:
answer correctness is too thin. A message can be wrong as an answer and useful
as a reasoning target.

raw-log caveat:
`reports/_archive/20260616-pruned/20260614-madmm-1237-raw-role-card.md` shows this case is not a clean
causal story. Subjective masking retained no first-round messages and still got
a correct majority on a fresh second pass. The useful contrast may be both that
objective retained an operation scaffold and that it suppressed the wrong
answer-surface majority visible under naive full retention.

## MOC Cards

### MOC Hop2: Compressed Merge Exists, Role Loss Unknown

message:
hop2 forced merge produces compressed summaries representing multiple source
agents.

parsed answer:
all five GSM8K smoke samples are correct.

role it played:
compressed public context. The merge represents multiple neighboring messages
before the target agent continues.

role it lost:
unknown. Current GSM8K smoke does not reveal whether the summary preserved clue,
bridge, or answer roles.

downstream effect:
accuracy remains saturated; token cost and merge events become visible.

what this system makes visible:
MOC exposes the compression site where role loss could happen, but not yet a
case where it matters.

### MOC Empty Card: The Task Did Not Ask Enough

message:
GSM8K arithmetic items in the hop check do not clearly separate clue object,
bridge entity, requested relation, and final answer object.

parsed answer:
mostly correct.

role it played:
setup/contact role, not failure-analysis role.

role it lost:
none observed.

downstream effect:
the trace is useful for instrumentation, not for target-role behavior.

what this system makes visible:
a benchmark can be alive for one purpose and dead for another. This is worth
remembering before launching another MOC run.

### MOC Role Probe: Synthetic Split-Evidence Compression

message:
`reports/_archive/20260616-pruned/20260614-moc-role-sensitive-split-evidence-probe.md` adds six
hand-built split-evidence cases and compares one-hop context, hop2 unmerged
context, role-aware compression, flat entity compression, and answer-only
compression.

parsed answer:
hop2 unmerged and role-aware compressed surfaces preserve all six cases; flat
and answer-only compressed surfaces preserve only the useful bridge-refinement
case.

role it played:
this is a schema/contact probe for the compression site that the GSM8K MOC
smoke could not stress.

role it lost:
the flat and answer-only policies deliberately lose requested relation,
qualifier, source attribution, and sometimes answer type, clue, bridge, and
forbidden-replacement roles.

downstream effect:
five cases become right-to-wrong relative to hop2 unmerged context, while the
useful bridge case stays correct. That keeps the important caveat alive: target
motion is not automatically target drift.

what this system makes visible:
MOC's plausible role-loss site can now be inspected with `role_slots_preserved`
and `role_slots_lost` fields before touching a real MOC domain or GPU run.

### MOC Merge Prompt Audit: Role Labels Change The Summary

message:
`reports/_archive/20260616-pruned/20260614-moc-merge-prompt-role-audit.md` runs the inspected MOC merge
prompt families over the same six synthetic role cases with Qwen2.5-7B.

parsed answer:
there is no benchmark answer score; the audit checks whether each merged summary
preserves answer type, clue object, bridge entity, requested relation, required
qualifier, forbidden replacement, and gold answer.

role it played:
this is the first real LLM contact for the MOC role-loss object, but still only
at the merge-prompt layer.

role it lost:
natural evidence summaries often drop guardrail roles. Across 30 natural-surface
outputs, `forbidden_replacement` is lost 21 times, `required_qualifier` 13
times, `clue_object` 10 times, and `requested_relation` 8 times.

downstream effect:
the audit does not run downstream agents, but it shows that compression can lose
the role information a downstream agent would need.

what this system makes visible:
role-aware labels are not just decoration. Labeled messages preserve all required
slots in 19/30 outputs, while natural evidence messages preserve all slots in
4/30. The labeled `technical_precision` strategy preserves 6/6.

## Things The Cards Changed

The same words should not be forced across systems.

PACT says:

```text
target role can drift in explicit public state.
```

DAR says:

```text
evidence role can be flattened by the retained message surface.
```

MAD-MM says:

```text
memory role can anchor the next round, sometimes through answer, sometimes
through scaffold.
```

MOC says:

```text
compression is a plausible role-loss site; synthetic role probes and merge-only
LLM prompts can now ask the question, but full MOC traces still do not.
```

The shared object is not `Target Slot`.

The shared object might be:

```text
communicated state has a role relative to the question, and reliability depends
on preserving the useful role while allowing necessary transformation.
```

That still feels a little too smooth. Leave it rough.

## Loose Next Touch

If this line keeps feeling alive, the next small touch should probably be one
of these:

- add two or three role cards from PACT offset50 public-state failures;
- inspect one MAD-MM retained scaffold case directly from the raw debate log;
- inspect natural-surface MOC merge failures before touching a tiny real MOC
  split-evidence domain;
- do nothing for a bit and let this vocabulary sit next to the existing trace
  schema.

The last option is legitimate.
