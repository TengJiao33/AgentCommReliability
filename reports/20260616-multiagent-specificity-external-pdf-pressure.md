# Multi-Agent Specificity External PDF Pressure

Date: 2026-06-16

Status: outside-pressure synthesis from downloaded PDFs, not a new run.

## What Was Read

PDFs were downloaded under `papers/external-pressure-20260616/` and text was extracted for local reading.

| Paper | Local PDF | Source |
| --- | --- | --- |
| Benefits and Limitations of Communication in Multi-Agent Reasoning | `papers/external-pressure-20260616/benefits-limitations-communication-2510.13903.pdf` | https://arxiv.org/pdf/2510.13903 |
| Demystifying Multi-Agent Debate: The Role of Confidence and Diversity | `papers/external-pressure-20260616/demystifying-mad-2601.19921.pdf` | https://arxiv.org/pdf/2601.19921 |
| Talk Isn't Always Cheap: Understanding Failure Modes in Multi-Agent Debate | `papers/external-pressure-20260616/talk-isnt-always-cheap-2509.05396.pdf` | https://arxiv.org/pdf/2509.05396 |
| The Cost of Consensus | `papers/external-pressure-20260616/cost-of-consensus-2605.00914.pdf` | https://arxiv.org/pdf/2605.00914 |
| When Persuasion Overrides Truth in Multi-Agent LLM Debates | `papers/external-pressure-20260616/persuasion-overrides-truth-2504.00374.pdf` | https://arxiv.org/pdf/2504.00374 |
| MultiAgent Collaboration Attack | `papers/external-pressure-20260616/multiagent-collaboration-attack-2024.findings-emnlp.407.pdf` | https://aclanthology.org/2024.findings-emnlp.407.pdf |
| HIDDENBENCH | `papers/external-pressure-20260616/hiddenbench-2505.11556.pdf` | https://arxiv.org/pdf/2505.11556 |
| PACT Action-state Communication | `papers/external-pressure-20260616/pact-action-state-2606.05304.pdf` | https://arxiv.org/pdf/2606.05304 |
| DeLM Shared Context | `papers/external-pressure-20260616/delm-shared-context-2606.10662.pdf` | https://arxiv.org/pdf/2606.10662 |
| CaMeL Prompt Injection Defense | `papers/external-pressure-20260616/camel-prompt-injection-2503.18813.pdf` | https://arxiv.org/pdf/2503.18813 |

## Pressure On The Current Idea

The user's objection is right: the current Authority Genesis packet can still look too much like a generic LLM context-authority problem. The outside papers sharpen the distinction.

The multi-agent-specific object is not:

```text
LLMs are influenced by authoritative-looking text.
```

That is too broad and is already adjacent to prompt injection, data/control-flow security, persuasion, and context poisoning.

The multi-agent-specific object is closer to:

```text
Communication acts transform one agent's local text into public, reusable, socially weighted, or procedurally admitted state for other agents.
```

The question becomes not "does an LLM follow a label?" but:

```text
Which communication transition turns information into authority?
```

## What The PDFs Add

### 1. Multi-agent communication is a graph/process, not a static label

The Benefits and Limitations paper formalizes MAS as a communication graph with agent-time nodes, communication edges, depth, width, size, and communication budget. Its key pressure is that multi-agent reasoning earns its name through partitioning, handoff, communication cost, and depth/resource tradeoffs. Debate/voting over the same input is treated as a different family: stochastic ensembling, not expressivity-increasing communication.

Implication for us:

- A static prompt ladder is only a proxy.
- The next object needs actual communication transitions: private output, sent message, broadcast, aggregation, admission, memory, downstream handoff.
- We should score the marginal effect of each transition, not only the wording of a field.

### 2. Debate papers make peer influence measurable

Talk Isn't Always Cheap and Cost of Consensus both treat peer exchange as a source of harmful answer transitions. Cost of Consensus is especially useful because it separates:

- semantic peer debate;
- stochastic unrelated-context control;
- isolated self-correction;
- vulnerability rate;
- recovery rate;
- modal sycophancy;
- oracle accuracy and oracle gap;
- communication density K;
- prompt-routing token overhead.

Implication for us:

- Our current MATH ladder should borrow these controls.
- The right comparison is not only hidden versus visible artifact.
- It is peer content versus self-revision versus unrelated peer-like context, plus whether the correct answer was already present in the team pool but discarded by consensus.

### 3. HiddenBench says the strongest multi-agent regime is distributed information

HIDDENBENCH isolates multi-agent reasoning under distributed information. The failure is not that agents cannot reason over all facts; when all facts are revealed, performance nearly closes the gap. The failure is that agents do not surface unshared information and converge too early on shared evidence. The structured Exchange-then-Decide protocol helps by forcing agents to share decision-relevant facts and reasons the front-runner may be wrong.

Implication for us:

- Authority Genesis becomes more multi-agent-specific if wrong authority competes with missing or unshared evidence.
- A good packet should include "information surfacing" metrics, not only final answer flips.
- The dangerous transition may be: a visible public artifact suppresses exploration of other agents' private evidence.

### 4. PACT and DeLM make admission into shared state the real boundary

PACT treats inter-agent communication as public state update: raw output is projected into ACTION, STATE, RESULT before entering shared history. DeLM treats shared context as an admission-gated communication substrate: compact updates become visible to all only after verification.

Implication for us:

- Our handle is probably not "authority label" but "admission semantics."
- Once a message is admitted to shared history, memory, verified context, or final-candidate state, downstream agents treat it as reusable problem state.
- The next experiment should manipulate admission gates: raw peer message, projected state, verified/admitted state, rejected state, and memory/handoff state.

### 5. Security papers bound the generic explanation

CaMeL says the generic agent-security problem is trusted control flow versus untrusted data flow. This is useful as a negative boundary: if our phenomenon can be fully explained by untrusted text hijacking a single model's task contract, it is not a multi-agent contribution.

Implication for us:

- Do not make "context authority" the contribution.
- Use it as a confound/baseline.
- The contribution candidate must be about communication provenance, visibility, aggregation, admission, and reuse across agents.

## Updated Status Of The Idea

Authority Genesis is still alive, but the old static ladder is not enough.

Current status:

```text
live diagnostic handle, not yet a solid story
```

What survives:

- Hidden metadata versus visible communication artifacts matters.
- PACT and MATH both show future-like communication states can change behavior.
- MATH operator uptake suggests something richer than exact answer copying.

What is weakened:

- "Future-looking labels create authority" is too generic.
- "Verifier/memory/final answer labels" are not automatically multi-agent-specific unless they are tied to actual communication lifecycle events.
- Current MATH operator-core evidence is case-concentrated, especially `math159` and `math121`.

## Better C-shape

Old C-shape:

```text
Authority Genesis ladder: same artifact under different future-looking labels.
```

Better C-shape after PDF pressure:

```text
Communication Lifecycle Stress Test: same local artifact as it crosses multi-agent communication transitions.
```

Lifecycle states:

- private scratch, not communicated;
- peer message to one receiver;
- broadcast to all agents;
- majority/plurality state;
- confidence-ranked state;
- verifier/admission-gated state;
- shared memory;
- downstream handoff / active task.

Controls:

- isolated self-correction with same revision format;
- unrelated peer-like context / stochastic noise;
- same artifact as inert text;
- same artifact as admitted shared state;
- same artifact with evidence hidden versus evidence visible.

Measurements:

- right-to-wrong vulnerability;
- wrong-to-right recovery;
- modal adoption / sycophancy;
- oracle gap: correct answer present but discarded;
- adversary agreement / peer-agreement change;
- information surfacing rate: unique private facts mentioned;
- authority escalation delta: effect added by each communication transition;
- token cost / routing overhead.

## Next Pressure

The next skill-aligned move is not another static balanced MATH v2 packet by itself.

Build a small communication-lifecycle packet that uses the MATH Authority Genesis artifacts but runs them through real multi-agent roles:

1. agents first solve independently;
2. one agent holds or emits the wrong artifact;
3. other agents receive it under controlled communication transitions;
4. the system optionally writes it into public/shared/admitted state;
5. downstream agents revise;
6. final aggregation records whether correct candidates were present but suppressed.

This preserves the multi-agent research object while still using the Authority Genesis handle.

Retirement condition:

- if peer/public/admission/reuse transitions do not add explanatory power beyond self-correction and inert-context controls, demote Authority Genesis to a generic LLM context-authority confound.

Promotion condition:

- if lifecycle transitions predict vulnerability, oracle gap, or information-surfacing suppression beyond content alone, promote the handle to a bounded multi-agent communication story candidate.
