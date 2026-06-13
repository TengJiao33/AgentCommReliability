# Research Map

This map captures the current shape of the project. It should evolve as evidence changes.

## Central Object

The project studies the reliability of communication events in LLM-based multi-agent systems.

A communication event is any moment when one agent's intermediate state becomes visible to another component:

- peer answer;
- peer reasoning;
- memory item;
- evidence citation;
- confidence score;
- tool result;
- judge or verifier feedback;
- compressed state record.

The core question is not "do more agents help?" The core question is:

> Which information should cross agent boundaries, under what conditions, and with what safeguards?

## Current Problem Axes

| Axis | Question | Observable Signals |
| --- | --- | --- |
| Helpfulness | Does communication correct an otherwise wrong answer? | final answer flips from wrong to correct; peer evidence appears before correction. |
| Contamination | Does wrong peer memory make later agents worse? | correct single-agent answer becomes wrong after message exposure. |
| Conformity | Do agents collapse to majority or authority without evidence? | repeated phrasing, confidence drop, unexplained answer copying. |
| Token efficiency | Does the gain justify extra context and calls? | tokens per extra correct answer, wall time, call count. |
| Evidence fidelity | Is the final answer supported by preserved evidence? | final answer references accurate evidence, not only peer agreement. |
| Routing | Should every instance use debate? | uncertain/conflict cases benefit more than easy cases. |
| Judge reliability | Does the aggregator follow evidence, confidence, or majority? | judge trace contradicts evidence or always follows majority. |
| Stability | Does the result survive seeds, tasks, or model changes? | cross-run variance, disagreement rate, unstable winners. |

## Mechanism Families

| Family | Representative Ideas | Potential Value | Main Risk |
| --- | --- | --- | --- |
| Memory masking | MAD-MM objective/subjective masking | remove harmful prior messages | crude pruning or costly no-op filtering |
| Multi-order communication | MOC | preserve multi-hop evidence under token constraints | added complexity without clear gains |
| Sparse or conditional debate | SMADE-IE, dynamic coordination selection | debate only where conflict exists | routing errors may skip useful discussion |
| Confidence-aware updates | DebUnc, confidence/diversity debate | reduce overconfident wrong influence | confidence calibration may be unreliable |
| Evidence-aligned consensus | EAGLE, evidence-driven debate | require agreement on support, not only answer | harder to generalize beyond evidence-rich tasks |
| Resource-rational communication | auction or bandwidth methods | treat communication as scarce | optimization signal may reward short but incomplete messages |
| Monitoring and harness design | monitoring before reliability, system scaling | detect structural failures early | monitor signals can become proxy metrics |
| Skill and memory drift audit | behavioral trajectories, SkillHarm | track persistent agent changes | may become security-specific rather than communication-specific |

## Current Evidence Snapshot

| Evidence | Source | Status | What It Supports | Caveat |
| --- | --- | --- | --- | --- |
| MAD-MM short subset on Qwen2.5-14B/GSM8K, 100 samples | `experiments/20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset/` | complete | communication rescued 2 CoT failures, but token cost was high. | short-subset evidence only. |
| Objective masking kept 100/300 memories and regressed one case | same run | complete | aggressive filtering can reduce cost but remove useful context. | only one observed regression. |
| Subjective masking kept 296/300 memories with 106 calls | same run | complete | LLM-based memory judging may be too permissive and costly in this setup. | may differ on harder tasks. |
| ArXiv digest scan identified MOC, SMADE-IE, dynamic coordination, monitoring papers | `reports/20260612-multi-agent-frontier-scan.md` | source-only | the frontier is shifting toward conditional, evidence-aware, and resource-aware communication. | digest-level scan, not paper-card evidence yet. |
| DAR short matrices on Qwen2.5-7B-Instruct | `experiments/20260612-a8002-dar-qwen25-7b-arithmetics-short-matrix/`; `experiments/20260612-a8002-dar-qwen25-7b-gsm8k-short-matrix/` | complete | DAR `filter_critical` improved/held on generated arithmetic but underperformed Basic MAD on GSM8K. | one seed/model; token accounting and trace-level flip analysis still incomplete. |

## Working Hypotheses

These are not conclusions. They are prompts for the next experiments.

| Hypothesis | Why It Is Plausible | Next Check |
| --- | --- | --- |
| Communication is most useful on uncertain or conflict-heavy instances. | MAD-MM short run showed small accuracy gain at high token cost. | compare easy vs uncertain subsets using confidence or disagreement routing. |
| Full reasoning exchange is often wasteful. | MAD naive used 441,846 tokens for 100 GSM8K examples. | test answer-only, evidence-only, and compressed state messages. |
| Masking needs a risk-aware fallback. | objective masking saved tokens but introduced a regression. | inspect case `id=214` and design fallback when pruning confidence is low. |
| Debate gains may be explained by extra samples or judge behavior, not communication itself. | common concern in MAD literature and our current run lacks self-consistency controls. | add self-consistency and majority-only baselines. |
| A useful project contribution may be a harness, not a new debate prompt. | current papers increasingly focus on routing, monitoring, and system-level control. | formalize logging schema and compare multiple communication modes. |

## Near-Term Reading Priorities

1. MOC: inspect multi-order evidence construction and merging.
2. SMADE-IE: inspect adaptive routing and evidence-driven debate.
3. Dynamic Coordination Strategy Selection: extract task taxonomy and routing criteria.
4. Monitoring Agentic Systems Before They're Reliable: adapt the monitoring matrix into our experiment templates.

## Deprioritized For Now

| Direction | Reason |
| --- | --- |
| Full MAD-MM standard matrix | Too expensive relative to current insight gain. Keep short-subset baseline. |
| Training-heavy policy optimization | Useful later, but not first-stage compute friendly. |
| Domain-heavy MARL or robotics consensus | Conceptually relevant, but less direct for LLM communication reliability. |
| Broad survey writing | Premature until more paper cards and code inspections exist. |
