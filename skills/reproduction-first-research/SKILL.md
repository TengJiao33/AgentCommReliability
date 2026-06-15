---
name: reproduction-first-research
description: Project-level posture for open-ended reproduction of papers and open-source baselines without forcing premature research questions, usefulness claims, or idea funnels. Use when this project reads, runs, records, repairs, publicly searches, incubates live research handles, coordinates with the ArXiv_Daily_Digest radar, or reflects on a multi-agent communication baseline.
---

# Reproduction-First Research

## Core Rule

Do not require a narrowed research question, proposed idea, or expected payoff before reproducing.

Start from contact with runnable code, reproduced behavior, errors, logs, implementation details, and the felt confusion of the work. Use the LLM as a companion for reading code, debugging, preserving context, and noticing details, not as a machine for converting every observation into a thesis.

This skill is a posture, not a checklist. Do not run every section on every turn. Choose the mode that matches the project state:

- contact mode: when a system has not yet been run or understood;
- outside-check mode: when a local observation, suspected mechanism, or new paper candidate may already have public names, code, benchmarks, or nearby work;
- pressure mode: when external papers can challenge or reorganize what the reproduction has shown;
- incubation mode: when repeated observations point to a live handle that is not yet a paper story;
- synthesis mode: when several reproduced systems expose a common tension worth naming.

The skill should prevent premature ideas, not prevent ideas altogether.

## Why This Skill Exists

Modern code exposes contact that papers often hide: prompt templates, data
preprocessing, stopping conditions, message filters, judge behavior, fallback
paths, hidden defaults, and evaluation scripts. Stay close enough that
questions, irritations, failures, and possible ideas can emerge without being
forced.

External literature is part of this contact when it puts pressure on reproduced behavior. Use papers to ask whether our traces are missing a more fundamental variable, not as a substitute for running code.

Do not build in isolation. When a local trace starts to look like a mechanism, first ask what the public record already calls it, what code or benchmark already exists, and whether the nearby arXiv radar has already seen a related paper.

## Practice

### 0. Check Outside Before Naming

Use public search as an anti-isolation step, not as a broad survey detour.

When a candidate paper, mechanism, benchmark, or failure pattern starts to matter:

- search public sources for exact paper titles, method names, benchmark names, arXiv IDs, repo names, and mechanism phrases;
- look for code, issues, reproduction notes, follow-up papers, benchmark variants, negative results, and known limitations;
- prefer source material that can change the next contact point: paper, code repo, benchmark, issue, artifact, or author page;
- record only the useful hits in `papers/reading_queue.md`, a paper card, or the current experiment/report note;
- do not write a survey document just because search found many papers.

Use the sibling `ArXiv_Daily_Digest` project as the standing radar when it is available:

```text
D:\develop\ArXiv_Daily_Digest
../ArXiv_Daily_Digest
```

Useful surfaces: `config/directions.yaml`,
`data/<direction>/<ISO-week>/papers.jsonl`,
`data/<direction>/<ISO-week>/weekly_digest.md`, and
`data/<direction>/<ISO-week>/landscape.md`.

If a paper belongs in the radar but is not being captured, add it to the digest project's `config/manual_papers.yaml` or propose a small query/seed update there. Do not run the digest pipeline casually; `python main.py` may call arXiv, Semantic Scholar, GitHub, Hugging Face, venue endpoints, and Doubao/Ark, and may consume quota.

Pull promising radar hits back into this project through `papers/reading_queue.md`, `papers/cards/<paper-id>.md`, or a bounded report. Keep the handoff concrete: title, link, source direction/week, why it pressures current traces, and whether code is available.

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

Keep the first contact runs small because small runs are easier to understand and easier to abandon. Do not let that become the project's resting state.

Once the command path, parser, and metric are working, actively ask whether a larger or more heterogeneous benchmark would reveal the behavior more clearly than another local variant. For ranking methods, judging robustness, estimating variance, or making any method-level claim, prefer scaling the benchmark pressure before adding another tiny ablation.

Do not hide behind minimal versions. When several small probes point at the same tension, move decisively: run the larger slice, change the task family, add heterogeneity, or build the broader bridge that would actually test the idea. Minimal probes are for contact and debugging; they are not a virtue once they become a way to avoid the harder pressure.

Small variants are probes, not automatically ideas. If a variant only changes a prompt surface, retained field, threshold, or message format, treat it as diagnostic unless it reveals a mechanism that connects to a broader literature question.

### 6. Incubate Live Handles

When several reports keep saying `diagnostic, not method claim`, do not merely
run another small variant or send the idea back to generic contact mode.

Create a compact live handle:

- phenomenon: what keeps appearing;
- mechanism candidate: why it may happen;
- artifacts: the exact reports, traces, labels, or code paths;
- boundary: what already weakens it;
- outside pressure: what public work already explains or names;
- next escalation: retire, scale, bridge to another task, prototype a protocol,
  or hand off to story synthesis.

If the same handle appears in three separate reports, choose one escalation.
Do not let `diagnostic` become a permanent waiting room.

### 7. Use Literature As Pressure

After several runnable systems have been touched, deliberately step out of pure reproduction mode.

Use external papers to pressure-test our observations:

- What task regimes do they distinguish that our benchmarks collapse?
- What variables do they treat as fundamental that our traces do not record?
- Which mechanisms do they claim are necessary, such as diversity, calibrated confidence, context alignment, routing, scarcity, or public state updates?
- Which of our observations become trivial under their framing?
- Which of our observations expose a gap in their framing?

This is not a broad survey license. Prefer papers that can reorganize an existing reproduction, explain a failure mode, or suggest a sharper next contact point.

When doing this pressure pass, include both fresh public search and the `ArXiv_Daily_Digest` radar before concluding that a tension is new, unnamed, or underserved.

### 8. Interpret Late And Lightly

After behavior is visible, the LLM can help ask:

- Which intermediate messages changed?
- Did the final answer change because of communication or because of more samples?
- Did masking remove wrong evidence or useful evidence?
- Did compression improve focus or delete necessary context?
- Did the judge follow evidence, confidence, or majority?
- Did the effect persist across seeds/tasks?

Treat explanations as provisional language around an encounter, not as something the project must defend.

### 9. Let Ideas Emerge Without A Schedule

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

Also resist the opposite failure mode: staying forever at patchable ablations.
When a handle keeps returning, make it inspectable as a protocol, benchmark
packet, field taxonomy, or falsifiable pressure test.

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

Small benchmarks are contact and debugging objects. Larger benchmarks are not bureaucracy; they are often the clearest way to see whether an effect survives heterogeneity, rare cases, and run variance.

Do not treat tiny saturated benchmarks as evidence for method claims, and do not keep returning to them once a larger runnable alternative exists. When a small run looks promising, flat, or confusing, the default next pressure should be a larger sample, another task family, a fuller benchmark slice, or repeated seeds unless cost or logistics make that unreasonable.

Benchmarks that make us notice the following may become interesting:

- disagreement;
- long or distributed evidence;
- rule selection;
- verifier behavior;
- memory/context compression;
- tool or state recovery;
- method ranking changes under scale, seed, or task heterogeneity.

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

## Report Shape

For short notes, prefer: what we tried, what happened, things noticed,
failures/friction, loose threads, and caveats.

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

This skill is the top-level contact and reproduction posture. It does not replace:

- machine checklist in `docs/machine_quickstart.md`;
- experiment logging details in `docs/experiment_protocol.md`;
- paper queue management in `papers/reading_queue.md`;
- late bounded synthesis in `skills/research-story-synthesis/SKILL.md`;
- recurring operational friction memory in `skills/repro-friction-memory/SKILL.md`.
