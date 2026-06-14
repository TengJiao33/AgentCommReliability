# AgentCommReliability

Multi-agent communication reliability, kept as an open-ended reproduction notebook.

## Authority

The project posture is defined by three top-level skills:

```text
skills/reproduction-first-research/SKILL.md
skills/research-story-synthesis/SKILL.md
skills/repro-friction-memory/SKILL.md
```

The short version:

```text
paper summary -> not enough contact
reproduce code -> sit with logs, failures, traces, and odd details
record before explaining
synthesize late, but judge story taste: solid root-cause insight or real novelty
remember solved reproduction friction
```

## Top-Level Attitude

This project does not need a narrowed research question before it can proceed.

We reproduce in a deliberately open state:

- no demand that every run justify itself as an idea;
- no forced funnel from paper to benchmark to claim;
- no premature declaration of the "real" problem;
- no need to make confusion productive too early.

The basic practice is to enter runnable systems, reproduce what we can, notice what feels strange, and leave enough trace that the encounter can be returned to later.

MAD-MM, DAR, MOC, RuleArena, and future baselines are objects on the table, not a fixed agenda. We can follow whichever one currently invites contact.

## Core Files

- `skills/reproduction-first-research/SKILL.md`: top-level posture and reproduction practice.
- `skills/research-story-synthesis/SKILL.md`: solid/novel story judgment, root-cause motivation, and motivation-method-experiment coupling after evidence exists.
- `skills/repro-friction-memory/SKILL.md`: reusable memory for solved operational reproduction blockers.
- `docs/project_log.md`: chronological facts.
- `docs/evidence_register.md`: durable observations and claims, only when something is worth carrying forward.
- `docs/experiment_protocol.md`: run-note metadata and logging shape.
- `docs/machine_quickstart.md`: remote machine and GPU checklist.
- `docs/comm_trace_schema.md`: unified trace fields for MAD-MM, DAR, and MOC.
- `papers/reading_queue.md`: paper radar.
- `baselines/<method>/`: source and reproduction notes.
- `experiments/<run-id>/README.md`: exact run records.
- `reports/`: interpreted but bounded reports.

## Remote Source Of Truth

Local machines change. Remote runtime should use:

```text
A800_2:/data/xuhaoming/yfy/research_workspace
```

Project source, patches, submodules, scripts, and notes stay in this repository.
Large outputs stay under remote `results/` and are referenced from run notes.

## Guardrails

- No broad survey writing as a substitute for contact with code and runs.
- No full benchmark matrix just to create a result table.
- No obligation to turn every observation into a mechanism or proposal.
- No large model or dataset download without a recorded reason.
- No shared-environment or shared-model-folder edits.
