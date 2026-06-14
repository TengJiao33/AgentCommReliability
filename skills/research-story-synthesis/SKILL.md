---
name: research-story-synthesis
description: Project-level skill for synthesizing bounded research stories, contribution shapes, mentor updates, paper-outline narratives, or idea memos from existing reproduced evidence. Use when the project already has reports, run artifacts, evidence-register rows, manual case labels, or literature pressure, and Codex needs to connect them into a careful story without inventing claims or forcing premature novelty.
---

# Research Story Synthesis

## Core Rule

Synthesize late and auditably.

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

- What is the actual story the evidence can support?
- Which observations belong together?
- Which claims are too strong for the current artifacts?
- What would a skeptical reader need to see next?

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
3. Name the smallest story that explains more than one artifact.
4. Add at least one boundary case or counterexample.
5. State what the current evidence cannot prove.
6. Choose the next pressure point only after the story is bounded.

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
- includes caveats near the claim, not buried at the end;
- preserves failed or contradictory evidence;
- avoids novelty language unless the evidence justifies it;
- gives the user a clearer next contact point.

A weak synthesis:

- summarizes papers without runnable contact;
- cherry-picks the nicest run;
- turns a selected-case manual label into a population claim;
- ignores parser, prompt-surface, or answer-contract confounds;
- ends with a generic "do more experiments" instead of a concrete pressure.

## Useful Prompts

```text
Given these reports and evidence rows, extract the smallest bounded research
story they support. Include one counterexample and one next pressure point.
```

```text
Turn this cluster of runs into a mentor update. Separate facts, interpretation,
caveats, and what we should check next.
```

```text
Audit whether this proposed claim is supported by the current evidence register
and reports. List the exact artifacts that support, bound, or contradict it.
```
