# AgentCommReliability

> Multi-agent communication reliability / reproducibility-driven analysis project.
> Created: 2026-06-12

This project tracks a focused research line around **multi-agent communication in LLM systems**: when communication helps, when it contaminates context, when it only burns tokens, and how mechanisms such as memory masking, context learning, topology control, message compression, and verifier/judge modules can make communication more reliable.

The project is meant to be a real research notebook, not just a paper-reading folder. The first useful outcome should be a small reproducible harness plus a short analysis report that can be discussed with Wu Xiaobao and senior collaborators.

## Why This Exists

Current signals:

- Wu Xiaobao suggested looking at the **multi-agent communication** direction and starting from related papers' introductions and related work.
- The direction is explicitly analysis-friendly: communication is a variable that can be controlled, ablated, and logged.
- Existing RA resources provide two possible compute targets:
  - Falcon via `falcon-rev` / reverse tunnel.
  - `A800_2`, an alternate 8 x A800 host that has been used successfully for small controlled GPU runs.
- `D:\develop\ArXiv_Daily_Digest` already maintains directions such as `multi-agent-consistency`, `agent-skills-harness`, and `agent-policy-optimization`; this project should consume that radar instead of duplicating it.
- The working methodology is reproduction-first: read paper code, run the baseline, inspect implementation details, then design small ablations where surprising behavior can appear.

## Start Here

Read these in order:

1. `project_intake.md` - research framing, first milestone, non-goals.
2. `skills/reproduction-first-research/SKILL.md` - the top-level research workflow for this project.
3. `skills/repro-friction-memory/SKILL.md` - reusable fixes for small reproduction blockers and machine-workflow friction.
4. `docs/documentation_system.md` - where each kind of research artifact belongs.
5. `docs/research_map.md` - current conceptual map, mechanism families, hypotheses, and evidence snapshot.
6. `docs/evidence_register.md` - bounded claims and their support level.
7. `docs/machine_handbook.md` - machine access, file placement, GPU rules, safety boundaries.
8. `docs/machine_quickstart.md` - shortest command/path checklist before touching remote machines.
9. `papers/reading_queue.md` - seed papers and next reading targets.
10. `docs/experiment_protocol.md` - run naming, logging, evidence levels, ablation templates.
11. `docs/reproduction_recording_standard.md` - concrete run-note, manifest, and report recording standard.

## Directory Layout

```text
AgentCommReliability/
  README.md
  project_intake.md
  docs/
    README.md
    documentation_system.md
    research_map.md
    evidence_register.md
    machine_handbook.md
    machine_quickstart.md
    experiment_protocol.md
    reproduction_recording_standard.md
    project_log.md
  skills/
    reproduction-first-research/
      SKILL.md
    repro-friction-memory/
      SKILL.md
  papers/
    reading_queue.md
    cards/
      _template.md
  baselines/
    README.md
    _templates/
  harness/
    README.md
  experiments/
    README.md
  reports/
    README.md
    _templates/
      objective_research_report.md
  scripts/
  assets/
  logs/
```

## Documentation Spine

Use this path when moving from an idea to evidence:

```text
reading_queue -> paper card -> baseline note -> experiment run -> evidence register -> report -> next check
```

The repository should distinguish:

- factual records: commands, paths, commits, metrics, artifacts;
- observations: what is visible in logs, traces, code, or paper text;
- interpretations: plausible mechanisms and hypotheses;
- caveats: what the current evidence does not establish.

## First Milestone

Target window: after exams, around 2026-06-28.

Minimum useful deliverable:

- 1 reproduced baseline or runnable open-source method.
- 1 unified log format for multi-agent runs.
- 3-5 controlled ablations:
  - full communication vs no communication;
  - memory masking on/off;
  - communication rounds;
  - number of agents;
  - token budget or compressed message format.
- 1 short report answering: **when does communication help or hurt in this setup?**

## Top-Level Skill

The project's default research workflow is `reproduction-first-research`.

Use it whenever a paper, repo, baseline, or candidate idea is evaluated. The key rule is:

```text
paper summary -> not enough
code reproduction -> inspect implementation -> controlled ablation -> evidence-backed idea
```

## Current Non-Goals

- Do not start with training-heavy policy optimization.
- Do not download large models or datasets without checking machine rules and recording the reason.
- Do not treat a single successful run as a benchmark result.
- Do not spend the first phase building a polished frontend.
- Do not modify shared RA repositories or shared conda environments for this project.
