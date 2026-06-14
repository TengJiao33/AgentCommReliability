---
name: research-story-synthesis
description: Project-level skill for judging and shaping research-paper stories from reproduced evidence. Use when Codex needs to decide whether observations support a solid root-cause story, a genuinely novel angle, or only a known limitation; to align motivation, method modules, ablations, qualitative cases, quantitative results, and caveats into a paper or mentor narrative without inventing claims.
---

# Research Story Synthesis

## Core Rule

Do story taste before story polish.

A research story must earn at least one of these reader reactions:

- Solid: "That is why the previous approach failed." The motivation is
  grounded in theory, repeated experimental observation, or both; it exposes a
  root cause or deep tension; the proposed method is designed against that
  cause; experiments show both task improvement and reduction of the diagnosed
  failure mode.
- Novel: "I did not realize one could do it that way." The contribution changes
  the framing, object, intervention, or evaluation lens enough to feel
  surprising. This is harder than a solid story and needs stronger evidence
  against obvious "just another variant" explanations.

If the work earns neither reaction yet, say so. Return to reproduction-first
contact instead of turning a known limitation into a paper claim.

Start from artifacts already in the repository: `docs/evidence_register.md`,
`docs/project_log.md`, reports, experiment summaries, trace records, manual
labels, and paper cards. Build the story from those objects, not from what the
project "seems to be about."

This skill is for making a research story visible after enough contact exists.
It is not a license to skip reproduction, inflate a local observation into a
claim, or turn every run into a contribution.

## Relation To Other Top-Level Skills

Use `skills/reproduction-first-research/SKILL.md` when the project is making
contact with code, baselines, logs, traces, or small variations.

Use `skills/repro-friction-memory/SKILL.md` when the project hits recurring
operational blockers such as shell quoting, parser bugs, remote workflow
friction, cache issues, or logging surprises.

Use this skill when there is enough reproduced material to ask:

- Is this merely a known limitation, or a deeper tension/root cause?
- Is the story solid, novel, or not ready?
- What are A, B, and C: previous approach, diagnosed cause, proposed fix?
- Do the method and experiments tightly follow from the motivation?

## The Paper Spine

Prefer an A/B/C story spine:

- Prior work or the current baseline uses A, but A does not work under problem
  or condition P.
- Theory, traces, ablations, or repeated observations suggest the reason is B.
- The project proposes C because C attacks B directly.
- With C, metric M improves; more importantly, diagnostic D shows that B is
  reduced, removed, or controlled.
- Without C, or with C removed, A's original failure mode returns or remains.

Do not accept a story if it only says:

- A is weak, so add C, without a precise B.
- C improves M, but there is no evidence that C affects B.
- B exists, but the method does not actually target B.
- Qualitative cases look nice, but they are not tied to quantitative or
  diagnostic evidence.

## Solid Versus Novel

Use the solid route when the project can make a well-based root-cause argument:

- motivation comes from theory, repeated experimental observation, or both;
- the insight helps readers understand why earlier methods did not work;
- the method is a response to that cause, not a module shopping list;
- ablations compare with and without the B-targeting component;
- diagnostics show the old failure mode is weaker after adding C;
- qualitative cases make the mechanism legible, not just impressive.

Use the novel route only when the project changes what seems possible or natural:

- a surprising formulation, intervention point, supervision signal, evaluation
  lens, or system decomposition;
- a contribution that does not collapse into "a standard module in a new place";
- clear evidence that the surprising move works for reasons the reader can
  inspect;
- careful comparisons against the most boring alternative explanations.

Novel is higher-risk and higher-threshold than solid. If the novelty is thin,
prefer a strong solid story over a weak novelty claim.

## Known Limitation Or Deep Tension

Before claiming a story, classify the observation.

Known limitation signs:

- the observation says only that a model, parser, communication channel, or
  baseline sometimes fails;
- the failure is expected from existing literature or common sense;
- the result does not explain why a class of methods fails;
- the proposed fix is generic and would fit many unrelated failures.

Deep tension signs:

- the observation explains why a plausible prior approach should fail or plateau;
- it reveals a mismatch between the assumed mechanism and the observed
  mechanism;
- controlling the suspected cause changes behavior in the predicted direction;
- the tension creates a concrete design target for C;
- the same mechanism appears in aggregate results and inspectable cases.

For this project, ask whether the evidence exposes a mechanism such as:

- public answer surface versus private reasoning or context construction;
- final-answer slot versus relation skeleton;
- numeric, role-slot, or target-predicate preservation under redaction;
- recipient visibility and communication cost versus evidential value;
- parser, prompt-surface, or answer-contract confounds that could fake a story.

These are diagnostic handles, not automatic contributions. Use them only when
local artifacts support them.

## Evidence First

Before writing a story, build a compact evidence map:

- artifact paths;
- exact run IDs or report names;
- what each artifact directly shows;
- caveats and parser/evaluation quirks;
- whether evidence is aggregate, case-level, manual-label, or literature
  pressure;
- which observations contradict or bound earlier claims.

If an observation cannot be tied to a file, command output, trace, report,
manual label, paper card, or evidence-register row, treat it as a hypothesis,
not a claim.

## Motivation Quality

A good motivation is independent of "we want a higher score." It should:

- give the reader a useful explanation;
- make the old method's failure feel less mysterious;
- predict what the new method should change;
- identify what evidence would falsify the story.

A weak motivation:

- starts from benchmark underperformance only;
- says "existing methods ignore X" without showing why X is the root cause;
- uses one selected example as the whole motivation;
- adds modules before naming the failure mechanism.

## Method Coupling

For every proposed module, design choice, or analysis handle, answer:

- Which B does it address?
- Why should it affect B?
- What ablation removes it?
- What diagnostic should change if it works?
- What qualitative trace or case would make the mechanism visible?

If these questions cannot be answered, mark the component as an engineering
add-on rather than a story-bearing contribution.

## Experiment Coupling

The experiment section should close the story loop:

- main quantitative result: C versus A or strong baselines;
- ablation: C with the B-targeting part removed;
- diagnostic: direct evidence that B is reduced, controlled, or no longer
  causes the old failure;
- qualitative cases: before/after examples showing the mechanism, not just
  cherry-picked wins;
- boundary cases: where C fails or the story becomes ambiguous;
- confound audit: parser, prompt, data selection, evaluation contract, and run
  variance issues near the claim.

If the experiments only show that C is better but do not show why, the story is
performance-first, not insight-first.

## Story Shape

Prefer a story that preserves tension over one that sounds complete.

Useful story units:

- phenomenon: what keeps appearing across traces or runs;
- mechanism candidate: how the saved artifacts suggest it happens;
- boundary: where the phenomenon fails, reverses, or becomes ambiguous;
- diagnostic handle: what field, surface, prompt, slot, or trace event made it
  inspectable;
- next pressure: the smallest check that would make the story more honest.

For this project, recurring story handles may include:

- public surface versus private reasoning;
- final-answer slot versus relation skeleton;
- numeric or role-slot preservation;
- target-predicate drift or preservation;
- context construction and recipient visibility;
- communication cost versus evidential value;
- parser or answer-contract confounds.

Do not use these handles as a fixed agenda. They are vocabulary for already
observed contact, not a checklist every run must satisfy.

## Synthesis Workflow

1. Re-read the relevant top-level evidence rows and recent reports.
2. Separate facts, active interpretations, hypotheses, and caveats.
3. Classify the candidate as solid, novel, known limitation, or not ready.
4. Name A, B, C, M, and D: baseline, diagnosed cause, proposed fix, metric, and
   diagnostic.
5. Check that each method component targets B.
6. Check that each experiment tests either performance, B-reduction, or a
   confound.
7. Add at least one boundary case or counterexample.
8. State what the current evidence cannot prove.
9. Choose the next pressure point only after the story is bounded.

When the story is not ready, say so and return to contact mode.

## Output Artifacts

Use existing project surfaces:

- `reports/<date>-<topic>.md` for a bounded synthesis memo;
- `docs/project_log.md` for facts about what was synthesized;
- `docs/evidence_register.md` only for durable claims or explicit boundaries;
- `papers/cards/<paper-id>.md` only when literature is part of the pressure.

Do not create parallel roadmaps, research-manifesto documents, or duplicate
planning files when a short report and an evidence-register row are enough.

## Quality Bar

A good synthesis in this project:

- cites local artifacts by path;
- distinguishes run results from interpretation;
- makes the solid/novel/not-ready classification explicit;
- identifies A, B, C, M, and D when proposing a paper story;
- checks whether the observation is a known limitation or a deep tension;
- includes caveats near the claim, not buried at the end;
- preserves failed or contradictory evidence;
- avoids novelty language unless the evidence earns the harder threshold;
- gives the user a clearer next contact point.

A weak synthesis:

- summarizes papers without runnable contact;
- cherry-picks the nicest run;
- mistakes a known limitation for a root-cause insight;
- proposes a module that is not tightly coupled to the motivation;
- reports a score gain without diagnosing whether the original B improved;
- turns a selected-case manual label into a population claim;
- ignores parser, prompt-surface, or answer-contract confounds;
- ends with a generic "do more experiments" instead of a concrete pressure.

## Useful Prompts

```text
Given these reports and evidence rows, decide whether the candidate story is
solid, novel, a known limitation, or not ready. Identify A, B, C, M, D, the
strongest caveat, and the next pressure point.
```

```text
Turn this cluster of runs into a mentor update. Separate facts, interpretation,
caveats, the root-cause hypothesis, method implications, and what we should
check next.
```

```text
Audit whether this proposed claim is supported by the current evidence register
and reports. List the exact artifacts that support, bound, or contradict it.
```

```text
For this proposed module, explain which diagnosed failure cause it targets, what
ablation removes it, and what diagnostic should improve if the story is true.
```
