---
name: reproduction-first-research
description: Project-level research workflow for turning papers and open-source baselines into reliable ideas through code reproduction, implementation inspection, controlled ablations, and evidence-backed explanation. Use when this project evaluates a multi-agent communication paper, chooses a baseline to reproduce, asks an LLM for research help, or turns an observed implementation detail into a candidate idea.
---

# Reproduction-First Research

## Core Rule

Do not start by asking an LLM to invent ideas from paper summaries.

Start from runnable code, reproduced behavior, hidden implementation details, and controlled variants. Use the LLM as a code-reading, debugging, explanation, and ablation-design assistant.

## Why This Skill Exists

Modern code often contains more research signal than the paper text:

- prompt templates;
- data preprocessing;
- stopping conditions;
- message filtering;
- judge behavior;
- fallback paths;
- undocumented hyperparameters;
- evaluation scripts;
- failure handling.

Many non-obvious ideas come from seeing how the baseline actually works, where it is brittle, and which implementation choice unexpectedly controls performance.

## Workflow

### 1. Select A Reproducible Target

Prefer a paper with:

- public code;
- small runnable examples;
- clear tasks and metrics;
- controllable communication variables;
- no mandatory large training job.

For this project, prioritize methods related to:

- memory masking;
- context construction;
- communication topology;
- message compression;
- judge / verifier behavior;
- multi-agent disagreement and consensus.

### 2. Establish The Baseline

Before changing anything, record:

- paper title and link;
- code repo and commit;
- license if visible;
- environment;
- model;
- dataset/task;
- exact command;
- output path;
- whether the run passed.

If the baseline cannot run, the first result is a reproduction note, not a research claim.

### 3. Read The Code With The LLM

Use the LLM to answer concrete code questions:

- Where is inter-agent communication represented?
- What exactly is stored as memory/context?
- Which messages are visible to which agent?
- How is the final answer selected?
- Where does the judge/majority vote enter?
- What gets counted as token cost?
- Which defaults are hidden outside the paper?
- Which code path differs from the method description?

Avoid vague prompts such as:

```text
Summarize this paper and give me ideas.
```

Prefer:

```text
Trace how one problem instance flows through this baseline. Identify every place where an agent message is created, filtered, reused, or hidden from another agent.
```

### 4. Extract Candidate Control Points

Convert code observations into control points:

| Observation | Control Point |
| --- | --- |
| Agents see full prior reasoning | message visibility |
| Wrong prior answer changes later agents | memory noise |
| Judge follows majority | judge mode |
| Long messages are copied verbatim | compression |
| Agents share identical prompts | agent diversity |
| Early wrong consensus persists | stopping condition |

Each control point must be connected to a line of code, config field, prompt template, or logged behavior.

### 5. Run Small Variants

Start with one-axis variants:

- communication: `none`, `full`, `masked`, `compressed`;
- rounds: `1`, `2`, `3`;
- agents: `1`, `2`, `3`;
- message type: `answer_only`, `evidence`, `full_reasoning`;
- judge: `none`, `majority`, `verifier`;
- memory noise: `clean`, `wrong_memory_injected`.

Keep the first dataset small. The goal is to expose behavior, not to claim a benchmark win.

### 6. Ask Why It Works After It Works

Only after a variant changes behavior, use the LLM to help explain:

- Which intermediate messages changed?
- Did the final answer change because of communication or because of more samples?
- Did masking remove wrong evidence or useful evidence?
- Did compression improve focus or delete necessary context?
- Did the judge follow evidence, confidence, or majority?
- Did the effect persist across seeds/tasks?

The LLM's explanation is a hypothesis. Logs decide whether it survives.

### 7. Promote Only Evidence-Backed Ideas

A candidate idea can be promoted when it has:

- a baseline comparison;
- a minimal variant;
- logs showing changed intermediate behavior;
- at least one repeated run or neighboring task;
- a plausible mechanism tied to code or traces;
- a clear caveat.

Do not promote:

- summary-only ideas;
- ideas based on closed-source papers with no reproducible handle;
- effects explained only by extra token budget;
- single lucky examples;
- improvements without failure analysis.

## Output Artifacts

For each target paper or baseline, produce:

```text
papers/cards/<paper-id>.md
baselines/<method>/reproduction.md
experiments/<run-id>/README.md
reports/<date>-<method>-observations.md
```

## Report Template

```markdown
# <Method> Reproduction-First Analysis

## Short Answer

## Baseline Reproduction

## Code-Level Control Points

## Variants Tested

## What Changed In The Logs

## Plausible Mechanism

## Caveats

## Next Experiment
```

## Failure Modes

If a run fails, preserve the failure:

- command;
- traceback;
- suspected cause;
- fix attempt;
- whether the fix changes method behavior.

Reproduction failures are useful because they reveal missing assumptions in the paper or repo.

## Skill Boundary

This skill is for research workflow decisions. It does not replace:

- machine rules in `docs/machine_handbook.md`;
- experiment logging rules in `docs/experiment_protocol.md`;
- paper queue management in `papers/reading_queue.md`.

