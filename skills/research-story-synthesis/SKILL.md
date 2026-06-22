---
name: research-story-synthesis
description: Project-level skill for judging and shaping research-paper stories from reproduced evidence. Use when Codex needs to decide whether observations support a solid root-cause story, a genuinely novel angle, an A-conference mechanism-improvement route, a benchmark/evaluation route, a live diagnostic handle, or only a known limitation; to perform external-pressure or literature-collision audits from full-paper evidence; to align motivation, contribution shape, ablations, qualitative cases, quantitative results, and caveats into a paper or mentor narrative without inventing claims.
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

If the work earns neither reaction yet, say so. If a live handle is emerging,
name the next pressure object; otherwise return to reproduction-first contact.

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

Use `skills/research-report-writing/SKILL.md` after the story judgment is made,
when the task is to explain the state to the user, a mentor, or a paper-facing
report in clear Chinese with claim-evidence discipline.

Use this skill when there is enough reproduced material to ask:

- Is this merely a known limitation, or a deeper tension/root cause?
- Is the story solid, novel, or not ready?
- What are A, B, and C: previous approach, diagnosed cause, contribution shape?
- Do the contribution and experiments tightly follow from the motivation?

## The Paper Spine

Prefer an A/B/C story spine:

- Prior work or the current baseline uses A, but A does not work under problem
  or condition P.
- Theory, traces, ablations, or repeated observations suggest the reason is B.
- The project proposes C because C attacks, exposes, or measures B directly.
- With C, metric M improves; more importantly, diagnostic D shows that B is
  reduced, removed, or controlled.
- Without C, or with C removed, A's original failure mode returns or remains.

C may be a method, diagnostic protocol, benchmark packet, evaluation lens,
field taxonomy, or intervention surface. If it is not a method, judge whether
it makes B inspectable and sets up a decisive pressure test.

Do not accept a story if it only says:

- A is weak, so add C, without a precise B.
- C improves M, but there is no evidence that C affects B.
- B exists, but C does not actually target, expose, or measure B.
- Qualitative cases look nice, but they are not tied to quantitative or
  diagnostic evidence.

## A-Conference Mechanism Calibration

When judging an A-conference route, do not reduce the question to "does it beat
SOTA." First ask what kind of paper the evidence has earned:

- a method-improvement paper, if C improves the task and reduces the diagnosed
  failure;
- a diagnostic / compiler paper, if C mainly makes the failure executable,
  inspectable, and controllable;
- a benchmark / stress-test paper, if the main contribution is the measurable
  failure object and evaluator;
- a mechanism microscope, if the evidence explains failures but cannot carry
  the main claim.

Use templates as taste, not as checklists. PAL says to separate model proposal
from reliable execution; ReAct says to make trajectories inspectable;
Decomposed Prompting says named interfaces matter; Sparse communication says
quality and cost should be read together; benchmark papers say a failure object
can be a contribution when the evaluator and baselines are clean.

Strong baselines should narrow the claim, not automatically kill it. Losing to
a transparent baseline may still leave a diagnostic or benchmark contribution.
Beating only weak prompt baselines is not enough for a method claim.

For this project, favor tables that reveal the contrast between free-form or
direct behavior, structured/model-only behavior, executor-assisted behavior,
transparent heuristics, and oracle controls. Include mechanism metrics, not
only final task success.

## Solid Versus Novel

Use the solid route when the project can explain why earlier methods fail and
show that C reduces that failure. Use the novel route only when the framing,
object, intervention point, evaluation lens, or decomposition feels genuinely
surprising and survives boring alternative explanations.

Novel is higher-threshold than solid. Prefer a strong root-cause story over a
thin novelty claim.

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

## Live Handles

Not-ready stories split into two kinds:

- stale: a known limitation, local quirk, parser issue, or unsupported hunch;
- live: a repeated diagnostic handle with artifacts, boundaries, and a concrete
  next pressure object.

For a live handle, preserve:

- the short name;
- the strongest artifact and strongest caveat;
- the current C-shape: method, protocol, benchmark, lens, taxonomy, or surface;
- the next pressure test;
- the retirement condition.

If a handle has appeared across three reports, do not end with only `not ready`.
Choose: retire it, scale it, bridge it to a better task, prototype the protocol,
or promote it to a bounded story candidate.

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

## External Pressure And Collision Audit

Treat external pressure as a claim-overlap audit, not a keyword alarm.

Do not judge a paper as serious pressure from the abstract alone. Abstracts,
titles, and search snippets may only create a reading queue or a weak
``possible neighbor'' note. A collision judgment requires reading enough of the
full paper to identify its actual object, mechanism, experiments, and final
claim.

Before saying a prior paper "already does this", inspect at least:

- introduction: the problem and motivation the paper claims;
- related work or positioning: what gap the authors say they fill;
- method: the mechanism, interface, algorithm, or protocol;
- experiments: the benchmark object, controls, metrics, and ablations;
- conclusion or limitations: the final contribution claim and boundaries.

Classify external work by overlap level:

- background neighbor: shares domain words or motivation, but uses a different
  object, mechanism, experiment, or claim;
- useful prior: attacks a nearby problem and can support framing, baselines, or
  evaluation, but does not occupy the project claim;
- partial overlap: shares one or two of object, mechanism, experiment, or
  claim; requires careful positioning and a differentiating experiment;
- direct collision: substantially shares the research object, mechanism,
  experimental test, and contribution claim; the project must pivot, narrow, or
  explicitly outperform it.

Use this overlap checklist before down-ranking a story:

- Object: what exact phenomenon or system component is studied?
- Concept: what named concept or decomposition carries the paper?
- Mechanism: what intervention, algorithm, protocol, or causal explanation is
  proposed?
- Experiment: what perturbation, benchmark, control, and metric make the claim
  visible?
- Claim sentence: what would the authors put in the abstract or introduction as
  their contribution?

Only direct collision should strongly pressure novelty. Neighboring work is
often helpful because it proves the area matters, supplies baselines, and gives
language for reviewers. If overlap is uncertain, write "needs full-paper
collision audit" rather than treating the paper as a threat.

For this project, do not mark DALA, PerspectiveGap, WhoFlips, Trust, MINT,
ProvenanceGuard, or related multi-agent communication papers as direct pressure
unless the audit shows they also study the same state-admission object, the
same source/scope/budget/verification mechanism, the same perturbation shape,
and the same contribution claim.

A good external-pressure note should output a compact table:

```text
Paper | Object | Mechanism | Experiments | Claim | Overlap level | What it pressures | How we differ
```

End the note with one of three actions: use as background, add as baseline, or
pivot/narrow the project claim. Do not end with vague anxiety.

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

## Contribution Coupling

For every proposed module, protocol, benchmark, lens, or analysis handle, answer:

- Which B does it address?
- Why should it affect B?
- What ablation, perturbation, or control removes it?
- What diagnostic should change if it works?
- What qualitative trace or case would make the mechanism visible?

If these questions cannot be answered, mark the component as an engineering
add-on rather than a story-bearing contribution.

## Experiment Coupling

The experiment section should close the story loop:

- main quantitative result: C versus A or strong baselines;
- ablation/control: C with the B-targeting part removed or perturbed;
- diagnostic: direct evidence that B is reduced, controlled, or no longer
  causes the old failure;
- qualitative cases: before/after examples showing the mechanism, not just
  cherry-picked wins;
- boundary cases: where C fails or the story becomes ambiguous;
- confound audit: parser, prompt, data selection, evaluation contract, and run
  variance issues near the claim.

If the experiments only show that C is better but do not show why, the story is
performance-first, not insight-first.

For compiler, executor, or admission stories, prefer paired evidence: the same
model proposal with and without hard execution, a transparent baseline or clear
reason it is absent, and diagnostics showing which failure was prevented. Task
success alone is too thin.

## Story Shape

Prefer a story that preserves tension over one that sounds complete.

Useful story units:

- phenomenon: what keeps appearing across traces or runs;
- mechanism candidate: how the saved artifacts suggest it happens;
- boundary: where the phenomenon fails, reverses, or becomes ambiguous;
- diagnostic handle: what field, surface, prompt, slot, or trace event made it
  inspectable;
- next pressure: the smallest check that would make the story more honest.

Recurring handles include public surface versus private reasoning,
final-answer slot versus relation skeleton, numeric/role slots,
target-predicate drift, recipient visibility, communication cost, and
parser/answer-contract confounds. Treat them as vocabulary, not a checklist.

## Synthesis Workflow

1. Re-read the relevant top-level evidence rows and recent reports.
2. Separate facts, active interpretations, hypotheses, and caveats.
3. Classify the candidate as solid method route, diagnostic/compiler route,
   benchmark/stress-test route, mechanism microscope, known limitation, live
   diagnostic, or stale/not ready.
4. If literature pressure is involved, perform the full-paper collision audit
   before judging novelty or declaring a neighboring paper threatening.
5. Name A, B, C, M, and D: baseline, diagnosed cause, contribution shape,
   metric, and diagnostic.
6. Check that each contribution component targets, exposes, or measures B.
7. Check that each experiment tests either performance, B-reduction, or a
   confound.
8. Add at least one boundary case or counterexample.
9. State what the current evidence cannot prove.
10. Choose the next pressure point only after the story is bounded.

When the story is not ready, say so. If it is live, preserve the handle and
next escalation. If it is stale, return to contact mode.

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
- makes the solid/novel/live/stale classification explicit;
- identifies A, B, C, M, and D when proposing a paper story;
- checks whether the observation is a known limitation or a deep tension;
- includes caveats near the claim, not buried at the end;
- preserves failed or contradictory evidence;
- avoids novelty language unless the evidence earns the harder threshold;
- treats external pressure as full-paper claim overlap, not abstract-level
  keyword similarity;
- gives the user a clearer next contact point.

A weak synthesis:

- summarizes papers without runnable contact;
- declares a literature collision after reading only abstracts, titles, or
  search snippets;
- cherry-picks the nicest run;
- mistakes a known limitation for a root-cause insight;
- proposes a module that is not tightly coupled to the motivation;
- reports a score gain without diagnosing whether the original B improved;
- says `not ready` without naming the live handle or retirement condition;
- turns a selected-case manual label into a population claim;
- ignores parser, prompt-surface, or answer-contract confounds;
- ends with a generic "do more experiments" instead of a concrete pressure.

## Useful Prompts

```text
Given these reports and evidence rows, decide whether the candidate story is
solid, novel, live diagnostic, known limitation, or stale. Identify A, B, C, M,
D, the strongest caveat, and the next pressure point.
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
For this proposed contribution shape, explain which diagnosed failure cause it
targets or exposes, what control removes it, and what diagnostic should improve
if the story is true.
```
