# Communication Regimes Synthesis

## What This Note Is

This is a pressure/synthesis note, not a new experiment report.

The immediate reason for writing it is that our recent DAR variants started to feel too local. They helped diagnose message-surface effects, but they did not answer a deeper question:

```text
When is inter-agent communication structurally needed, and what kind of public state should it carry?
```

The goal here is to place our existing reproductions under external literature pressure and decide what should happen before another GPU run.

## External Pressure Axes

| Axis | Paper | What It Pressures In Our Work |
| --- | --- | --- |
| Task regime and communication necessity | [Benefits and Limitations of Communication in Multi-Agent Reasoning](https://arxiv.org/abs/2510.13903) | We should stop treating GSM8K, MATH, MMLU-Pro, HotpotQA, and AIME as interchangeable "reasoning" tasks. Communication may be useful, useless, or intrinsically costly depending on whether the task resembles recall, state tracking, k-hop reasoning, or conflict resolution. |
| Context alignment | [Context Learning for Multi-Agent Discussion](https://openreview.net/forum?id=EUu8TILWpR); [arXiv](https://arxiv.org/abs/2602.02350) | Our retention traces record which messages are visible, but not whether each agent has a coherent discussion context. M2CL frames failures as context misalignment and premature convergence on majority noise, which is deeper than message filtering. |
| Debate dynamics | [Demystifying Multi-Agent Debate: The Role of Confidence and Diversity](https://arxiv.org/abs/2601.19921) | Our homogeneous MAD/DAR-style runs mostly manipulate what messages are retained. They do not yet test whether debate starts with enough hypothesis diversity or whether confidence is calibrated and used in updates. |
| Public state surface | [What Should Agents Say? Action-state Communication for Efficient Multi-Agent Systems](https://arxiv.org/abs/2606.05304) | PACT reframes communication as a public state update, not a shortened private reasoning trace. This pressures our `answer_only` / `full` contrast, which is too coarse. |
| Multi-hop evidence receptive field | [MOC: Multi-Order Communication in LLM-based Multi-Agent Systems](https://arxiv.org/abs/2606.02359) | MOC says first-order neighbor concatenation can hide multi-hop evidence and dilute source information. This pressures our trace schema to record evidence path and compression loss, not only final answer flips. |
| Conditional debate and structured evidence | [SMADE-IE](https://arxiv.org/abs/2606.04691) | Debate may be something to trigger only for conflict cases, with structured claims, grounds, warrants, and evidence scores. This is stronger than always running the same MAD loop. |
| Scarce communication budget | [Cost-Effective Communication / DALA](https://arxiv.org/abs/2511.13193); [AAAI page](https://ojs.aaai.org/index.php/AAAI/article/view/40182) | Communication should not be assumed free. "Strategic silence" is a mechanism-level alternative to message filtering after everyone has already spoken. |

## Where Our Reproductions Sit

| Local Object | What We Actually Touched | Current Limit |
| --- | --- | --- |
| MAD-MM | Wrong-memory contamination, subjective/objective masking, benchmark sweep over MATH/MMLU-Pro/AIME | Still mostly a memory-quality framing. It does not decide when communication is needed in the first place. |
| DAR | Disagreement-aware retention, full-history traces, answer-only/full/guard split | Strong local diagnostics, but still inside a message-retention frame. Recent variants risk becoming prompt-surface engineering. |
| MOC | Topology smoke, forced structural merge, preliminary unified trace | Useful as contact with multi-hop evidence and compression, but current runs are too small and GSM8K-saturated. |
| PACT | HotpotQA split-evidence smoke with clean action-state fields | Good contact with public-state communication, but strict EM is confounded by final-answer surface. |
| Unified trace schema | Comparable transitions, retention events, merge events, token cost | It records what was retained or merged, but not task regime, evidence locality, confidence calibration, or communication necessity. |

## What Becomes Too Shallow

The recent DAR message-mode variants are useful probes, but they should not be treated as the idea.

`answer_only`, `full`, `guard_full`, and a possible `answer_plus_evidence` variant can show that message surface matters. They cannot by themselves answer:

- whether the task requires communication;
- whether the agents began with enough diverse hypotheses;
- whether confidence should modulate updates;
- whether the recipient context is aligned;
- whether evidence should be routed, summarized, or left silent;
- whether the same protocol should apply to easy, conflict, recall, state-tracking, and multi-hop cases.

So the right interpretation is:

```text
DAR variants diagnosed a local failure surface.
They did not define a research direction.
```

## What Still Survives

Several local observations remain useful under the literature pressure.

First, benchmark choice already changed method ranking. MAD-MM objective was best on MATH50, naive MAD was slightly best on MMLU-Pro50, and AIME showed no reliable multi-agent gain while consuming far more tokens. This supports a task-regime framing more than a universal method-ranking framing.

Second, DAR sample `20` is still informative, but not because it suggests one more retained surface. It shows that answer correctness, parseability, and useful reasoning evidence can diverge. That is evidence for typed public state, not just answer-bucket diversity.

Third, PACT's 50-sample HotpotQA run gave clean public action-state fields but weak strict EM due to answer verbosity. This suggests that communication evaluation must separate evidence transfer, final-answer extraction, and reasoning failure.

Fourth, MOC's forced merge smoke made the compression path visible, but saturated GSM8K accuracy hid whether multi-hop evidence helped. This argues for tasks where evidence locality and hop structure are explicit.

## Working Reframe

The project should not currently be framed as:

```text
Find a better message-retention rule for multi-agent debate.
```

A better working frame is:

```text
Build evidence for when LLM agents should communicate, what public state should be transmitted, and when communication should be suppressed.
```

That frame connects our local evidence to the literature axes:

- task regime: recall, state tracking, k-hop, conflict evidence, saturated arithmetic;
- communication decision: speak, stay silent, route, merge, broadcast;
- public state surface: answer, evidence, action-state, confidence, full reasoning;
- debate dynamics: initial diversity, calibrated confidence, majority pressure;
- evaluation: accuracy, right/wrong transitions, evidence transfer, extraction failure, token budget.

## Candidate Next Contacts

### 1. Paper/Card Sprint Before GPU

Create focused paper cards for:

- `Benefits and Limitations of Communication in Multi-Agent Reasoning`;
- `Context Learning for Multi-Agent Discussion`;
- `Demystifying Multi-Agent Debate`.

The purpose is not a survey. The purpose is to extract variables our current traces do not record.

### 2. Communication-Regime Harness Sketch

Design a small harness before implementing it. It should sort tasks by communication structure:

| Regime | Example Task Shape | What To Test |
| --- | --- | --- |
| Recall | one shard contains the answer | whether communication can be minimal and targeted |
| State tracking | distributed sequence/state updates | whether parallel agents reduce depth only with enough communication |
| K-hop reasoning | answer depends on facts across shards | whether multi-hop evidence paths matter |
| Conflict evidence | multiple plausible labels/answers with evidence | whether debate should be triggered conditionally |
| Saturated arithmetic | easy GSM8K-like cases | whether communication only adds cost or conformity |

Candidate protocols:

- single agent;
- independent samples / self-consistency;
- full MAD;
- memory masking / retention;
- action-state public records;
- routed or silent communication;
- confidence/evidence-aware arbitration.

### 3. M2CL Code Contact

M2CL is a useful next object because it is about context generation rather than message retention. The first contact should be code reading, not training:

- where context generators are represented;
- what they emit per round;
- how context coherence and discrepancy are measured;
- whether any inference-only reproduction is possible without full checkpoint/training cost.

## Not Recommended Next

Do not immediately run another DAR surface variant. It is too likely to produce another local case improvement without changing the research frame.

Do not scale GSM8K. It is already saturated enough to hide communication effects.

Do not treat PACT EM as reasoning evidence until answer extraction and evidence-transfer failure are separated.

Do not expand MOC hop-depth runs until the task exposes actual multi-hop evidence needs and per-sample merge loss can be inspected.

## Short Conclusion

The next real move is not another patch.

The next move is to convert the existing reproduction notebook into a task-regime and public-state communication lens. After that, a small harness or a focused M2CL contact can be justified without pretending that a prompt-surface ablation is already an idea.

