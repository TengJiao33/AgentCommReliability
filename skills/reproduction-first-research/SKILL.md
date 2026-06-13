---
name: reproduction-first-research
description: Project-level posture for open-ended reproduction of papers and open-source baselines without forcing premature research questions, usefulness claims, or idea funnels. Use when this project reads, runs, records, repairs, or reflects on a multi-agent communication baseline.
---

# Reproduction-First Research

## Core Rule

Do not require a narrowed research question, proposed idea, or expected payoff before reproducing.

Start from contact with runnable code, reproduced behavior, errors, logs, implementation details, and the felt confusion of the work. Use the LLM as a companion for reading code, debugging, preserving context, and noticing details, not as a machine for converting every observation into a thesis.

## Why This Skill Exists

Modern code contains a different kind of contact than the paper text:

- prompt templates;
- data preprocessing;
- stopping conditions;
- message filtering;
- judge behavior;
- fallback paths;
- undocumented hyperparameters;
- evaluation scripts;
- failure handling.

The point is not to mine these details for immediate novelty. The point is to stay close enough to the system that questions, irritations, failures, and possible ideas can emerge without being forced.

## Practice

### 1. Pick Up A Reproducible Object

Prefer objects that can be touched:

- public code;
- small runnable examples;
- clear tasks and metrics;
- visible communication variables;
- no mandatory large training job.

The following themes are current attractors, not obligations:

- memory masking;
- context construction;
- communication topology;
- message compression;
- judge / verifier behavior;
- multi-agent disagreement and consensus.

### 2. Establish Contact

Before changing behavior, record enough to return later:

- paper title and link;
- code repo and commit;
- license if visible;
- environment;
- model;
- dataset/task;
- exact command;
- output path;
- whether the run passed.

If the baseline cannot run, the failed reproduction is still part of the project. It does not need to become a claim.

### 3. Read The Code With The LLM

Use the LLM to answer concrete code questions and to keep the reading process from becoming shapeless:

- Where is inter-agent communication represented?
- What exactly is stored as memory/context?
- Which messages are visible to which agent?
- How is the final answer selected?
- Where does the judge/majority vote enter?
- What gets counted as token cost?
- Which defaults are hidden outside the paper?
- Which code path differs from the method description?

Avoid prompts that skip contact:

```text
Summarize this paper and give me ideas.
```

Prefer:

```text
Trace how one problem instance flows through this baseline. Identify every place where an agent message is created, filtered, reused, or hidden from another agent.
```

### 4. Stay With What Appears

Some observations may later become control points. They do not need to become control points immediately.

Record things like:

| What appeared | Possible later handle |
| --- | --- |
| Agents see full prior reasoning | message visibility |
| Wrong prior answer changes later agents | memory noise |
| Judge follows majority | judge mode |
| Long messages are copied verbatim | compression |
| Agents share identical prompts | agent diversity |
| Early wrong consensus persists | stopping condition |

When something feels important, attach it to a line of code, config field, prompt template, output, or log. When it does not yet feel important, it is still acceptable to leave it as a note.

### 5. Try Small Variations When Curiosity Points There

Small variants are allowed when they help touch the system more clearly:

- communication: `none`, `full`, `masked`, `compressed`;
- rounds: `1`, `2`, `3`;
- agents: `1`, `2`, `3`;
- message type: `answer_only`, `evidence`, `full_reasoning`;
- judge: `none`, `majority`, `verifier`;
- memory noise: `clean`, `wrong_memory_injected`.

Keep early runs small because small runs are easier to understand and easier to abandon. They are not required to justify themselves as pilots for a larger matrix.

### 6. Interpret Late And Lightly

After behavior is visible, the LLM can help ask:

- Which intermediate messages changed?
- Did the final answer change because of communication or because of more samples?
- Did masking remove wrong evidence or useful evidence?
- Did compression improve focus or delete necessary context?
- Did the judge follow evidence, confidence, or majority?
- Did the effect persist across seeds/tasks?

Treat explanations as provisional language around an encounter, not as something the project must defend.

### 7. Let Ideas Emerge Without A Schedule

An idea may eventually deserve a sharper form when it has:

- a baseline comparison;
- a minimal variant;
- logs showing changed intermediate behavior;
- at least one repeated run or neighboring task;
- a plausible mechanism tied to code or traces;
- a clear caveat.

But do not force that sharpening. The following are especially worth resisting:

- summary-only ideas;
- ideas based on closed-source papers with no reproducible handle;
- effects explained only by extra token budget;
- single lucky examples;
- improvements without failure analysis.
- the feeling that every run must lead to a named contribution.

## Project Operating Rules

### Open-Ended Reproduction

The project is allowed to be exploratory, confused, and non-instrumental.

Do not turn a temporary plan into the identity of the project unless the user explicitly asks for that frame. Temporary choices are local conveniences.

### Original Runs As Contact

Original paper benchmarks are useful because they put us in contact with the authors' code path and assumptions. They are not a loyalty test and they do not have to become anchors for every later action.

### Traces Are Notes, Not Gates

Traces, logs, token counts, and case records are ways of remembering what happened. They should reduce self-deception, but they should not become a gate that forbids wandering.

Useful things to preserve when available:

- `wrong_to_right`;
- `right_to_wrong`;
- correct evidence dropped;
- wrong evidence retained;
- compressed summary lost a required condition;
- judge followed majority instead of evidence;
- communication changed only token cost.

It is still acceptable for a run to produce only aggregate accuracy, a setup failure, or a feeling that the object is not interesting right now.

### Benchmarks Are Objects, Not Funnels

A benchmark can be tried because it is nearby, runnable, weird, suggested by someone, or simply alive in the current workspace. It does not need to be justified as a test of an already named mechanism.

Benchmarks that make us notice the following may become interesting:

- disagreement;
- long or distributed evidence;
- rule selection;
- verifier behavior;
- memory/context compression;
- tool or state recovery.

If a benchmark feels dead, saturated, noisy, or too expensive, leave it. That is a local practical choice, not a research verdict.

### Documentation Minimalism

This skill is the posture authority. Do not create new planning documents when an experiment note, project log entry, or evidence-register row is enough.

Use:

```text
facts -> experiment README or project_log
durable observations or claims -> evidence_register
commands and run metadata -> experiment README
project posture -> this skill
machine/resource facts -> machine/resource docs
```

Avoid documents that only restate plans, duplicate templates, create parallel research maps, or make the project sound more settled than it is.

### Remote-Reproducible Setup

Local machines are transient. Source, patches, scripts, submodules, and notes must live in the project repository.

Large runs and raw outputs live on the fixed remote workspace and are referenced from run notes:

```text
A800_2:/data/xuhaoming/yfy/research_workspace
```

Never rely on a machine-local clone outside the project as the only copy of a benchmark or baseline setup.

## Output Artifacts

When an object becomes worth preserving, prefer these artifacts:

```text
papers/cards/<paper-id>.md
baselines/<method>/reproduction.md
experiments/<run-id>/README.md
reports/<date>-<method>-observations.md
```

Not every passing curiosity needs all of them.

## Report Template

```markdown
# <Method> Reproduction Notes

## What We Tried

## What Happened

## Things Noticed

## Failures / Friction

## Loose Threads

## Caveats
```

## Failure Modes

If a run fails, preserve the failure:

- command;
- traceback;
- suspected cause;
- fix attempt;
- whether the fix changes method behavior.

Reproduction failures are worth preserving because they reveal missing assumptions in the paper, repo, machine, or our own reading.

For recurring operational friction such as shell quoting, remote cache misses, parser quirks, output-path surprises, or debug logging gaps, also update `skills/repro-friction-memory/SKILL.md` with the reusable prevention rule.

## Skill Boundary

This skill is the top-level project posture. It does not replace:

- machine checklist in `docs/machine_quickstart.md`;
- experiment logging details in `docs/experiment_protocol.md`;
- paper queue management in `papers/reading_queue.md`.
