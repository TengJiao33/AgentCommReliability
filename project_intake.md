# Project Intake

## One-Line Positioning

This project keeps an open-ended reproduction notebook around **multi-agent communication reliability**: reproduce runnable systems, stay with their code and failures, and let questions or ideas appear without forcing them early.

## Background

Wu Xiaobao suggested starting from the multi-agent communication direction and reading several papers:

- Multi-Agent Debate with Memory Masking
- Context Learning for Multi-Agent Discussion
- Benefits and Limitations of Communication in Multi-Agent Reasoning

This felt worth entering because:

- The direction is close to LLM agents and reliability, not only traditional sentiment analysis.
- It is analysis-friendly and has many small runnable surfaces.
- It can often be touched with relatively modest compute.
- It can reuse the existing arXiv radar project instead of starting paper discovery from zero.
- It fits the desire to reproduce code first and let the work remain unsettled for a while.

## Top-Level Orientation

The project does not need to begin with a precise research question, a planned contribution, or a narrowed experimental loop.

The preferred state is:

- reproduce before summarizing too much;
- keep logs, failures, patches, and odd cases close;
- avoid turning every observation into a claim;
- allow confusion and idle curiosity to remain part of the work;
- make practical choices locally without converting them into a project ideology.

## Top-Level Skills

Use these as the project's top-level skills:

- `skills/reproduction-first-research/SKILL.md`
- `skills/research-story-synthesis/SKILL.md`
- `skills/repro-friction-memory/SKILL.md`

This means:

- paper reading should stay connected to runnable code when possible;
- LLM help should focus on code tracing, debugging, implementation explanation, and careful note keeping;
- candidate ideas may come from observed behavior, but do not need to be produced on schedule;
- if an idea is eventually given sharper form, it should remember the logs, code paths, or variants that gave rise to it.
- research stories and mentor updates should be synthesized late from reports, evidence rows, and run artifacts, then judged by whether they are solid root-cause stories, genuinely novel angles, or only known limitations;
- a paper story should tightly connect motivation, method, ablations, qualitative evidence, quantitative gains, and diagnostics of the diagnosed failure cause;
- recurring operational blockers should be captured as reusable friction-memory rules instead of rediscovered.

## Seed Questions, Not Commitments

1. When does communication between LLM agents actually improve final accuracy or consistency?
2. When does communication propagate wrong memories, majority pressure, or irrelevant context?
3. Which communication controls are most robust under small compute?
4. Is the benefit from "debate" itself, or from ensembling, self-consistency, extra tokens, or stronger judge prompts?
5. Can a lightweight harness expose failure modes that are invisible in paper-level summaries?

These questions are starting points. They are allowed to become less important after contact with code.

## Things We May Notice

| Mechanism | Question |
| --- | --- |
| Memory masking | Can removing suspicious previous messages prevent wrong-memory contamination? |
| Context learning | Can dynamic context construction improve discussion state across rounds? |
| Sparse topology | Can fewer communication links preserve performance while reducing token cost? |
| Message compression | What information should agents pass forward: full CoT, answer only, evidence, confidence, or action-state record? |
| Heterogeneous models | Does diversity matter more than the number of agents? |
| Verifier / judge | Does a judge improve truth-seeking or merely amplify majority pressure? |

## Initial Practical Shape

Useful early artifacts:

- This project folder.
- Machine handbook.
- Seed reading queue.
- Experiment protocol.
- Mentor/senior update drafts.

Useful early motions:

- pick one code-available baseline and make contact with it locally or on `A800_2`;
- record exact commands, failures, output paths, and fixes;
- read the implementation around message passing, memory, judging, or evaluation;
- try small variants only when they help us see the system better;
- write short notes when an encounter leaves something worth remembering.

Early candidates:

- MAD-M2 / memory masking, because it directly matches Wu Xiaobao's seed paper.
- MOC, PACT, or another communication-control method if code is cleaner and smaller.

## Guardrails

- No broad "multi-agent survey" as a substitute for reproduction.
- No large training or RL policy optimization while the project is still mostly contact and reading.
- No uncontrolled use of shared GPUs.
- No modification to RA EasyEdit source trees for this project unless explicitly coordinated.
- No private credentials, SSH keys, tokens, or proxy configuration details in this repository.
