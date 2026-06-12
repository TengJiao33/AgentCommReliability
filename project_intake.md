# Project Intake

## One-Line Positioning

This project studies **multi-agent communication reliability** through reproduction-driven analysis: reproduce small baselines, expose hidden implementation assumptions, and run controlled ablations to understand when communication improves or damages LLM-agent reasoning.

## Background

Wu Xiaobao suggested starting from the multi-agent communication direction and reading several papers:

- Multi-Agent Debate with Memory Masking
- Context Learning for Multi-Agent Discussion
- Benefits and Limitations of Communication in Multi-Agent Reasoning

This aligns with the current personal strategy:

- The direction is close to LLM agents and reliability, not only traditional sentiment analysis.
- It is analysis-friendly and can produce meaningful small experiments.
- It can be run with relatively modest compute if the harness is controlled.
- It can reuse the existing arXiv radar project instead of starting paper discovery from zero.
- It fits the "reproduce code first, then find non-obvious ablation points" methodology.

## Top-Level Skill

Use `skills/reproduction-first-research/SKILL.md` as the default project workflow.

This means:

- paper reading should lead to a reproducible target;
- LLM help should focus on code tracing, debugging, implementation explanation, and ablation design;
- candidate ideas should come from observed behavior, not summary-only novelty claims;
- every promoted idea should be tied to logs, code paths, or controlled variants.

## Core Research Questions

1. When does communication between LLM agents actually improve final accuracy or consistency?
2. When does communication propagate wrong memories, majority pressure, or irrelevant context?
3. Which communication controls are most robust under small compute?
4. Is the benefit from "debate" itself, or from ensembling, self-consistency, extra tokens, or stronger judge prompts?
5. Can a lightweight harness expose failure modes that are invisible in paper-level summaries?

## Candidate Mechanisms

| Mechanism | Question |
| --- | --- |
| Memory masking | Can removing suspicious previous messages prevent wrong-memory contamination? |
| Context learning | Can dynamic context construction improve discussion state across rounds? |
| Sparse topology | Can fewer communication links preserve performance while reducing token cost? |
| Message compression | What information should agents pass forward: full CoT, answer only, evidence, confidence, or action-state record? |
| Heterogeneous models | Does diversity matter more than the number of agents? |
| Verifier / judge | Does a judge improve truth-seeking or merely amplify majority pressure? |

## Phase Plan

### Phase 0: Documentation And Setup

Deliverables:

- This project folder.
- Machine handbook.
- Seed reading queue.
- Experiment protocol.
- Mentor/senior update drafts.

### Phase 1: Baseline Reproduction

Goal:

- Pick one code-available baseline and make it run locally or on `A800_2`.

Preferred first candidates:

- MAD-M2 / memory masking, because it directly matches Wu Xiaobao's seed paper.
- MOC, PACT, or another communication-control method if code is cleaner and smaller.

Evidence:

- exact commit;
- environment;
- command;
- task/dataset;
- model;
- output path;
- pass/fail;
- first failure and fix notes.

### Phase 2: Unified Harness

Goal:

- Wrap baseline runs into one logging format.

Minimum fields:

- run id;
- paper/method;
- model;
- dataset/task;
- agent count;
- communication topology;
- rounds;
- message type;
- token budget;
- final answer;
- correctness;
- per-round messages;
- detected conflicts;
- judge decision if any.

### Phase 3: Controlled Ablations

Small first ablations:

- `communication = none/full/masked/compressed`;
- `agents = 1/2/3/5`;
- `rounds = 1/2/3`;
- `message = answer_only/evidence/confidence/full_reasoning`;
- `memory_noise = clean/injected_wrong`;
- `judge = none/majority/verifier`.

### Phase 4: Short Report

Target report:

- 4-6 pages or a compact Markdown report.
- Clearly separate reproduction evidence from new observations.
- Include "surprising findings" only if backed by logs.
- End with concrete open questions and next experiment choices.

## Non-Goals

- No broad "multi-agent survey" as the first output.
- No large training or RL policy optimization in the first phase.
- No uncontrolled use of shared GPUs.
- No modification to RA EasyEdit source trees for this project unless explicitly coordinated.
- No private credentials, SSH keys, tokens, or proxy configuration details in this repository.
