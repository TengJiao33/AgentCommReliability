# Reports

Use this folder for human-readable research notes and mentor-facing summaries.

Reports can interpret evidence, but they should not force significance onto a run. They do not replace paper cards, run records, raw logs, or the evidence register.

When writing or revising a substantial report, follow `skills/research-report-writing/SKILL.md`: state the judgment first, keep each paragraph to one message, map major claims to evidence, and keep caveats close to the claim.

## Current Surface

As of `2026-06-18`, the top-level folder is deliberately kept small. It should show only the reports that still help steer the benchmark-first live story:

- benchmark-first reset and the retirement boundary for the old MATH / TypeCast main story;
- HiddenBench communication-necessity evidence and protocol pressure;
- PerspectiveGap role-specific routing and source/scope pressure;
- State Admission / role-scoped evidence admission pressure, including local baselines, executor results, external collision audits, and V2 preflight;
- PACT-style split-evidence notes, using HotpotQA / 2Wiki style settings as benchmark pressure;
- TeamBench / Docker feasibility and other external benchmark constraints;
- MATH / TypeCast mechanism microscopes only when they explain an externally motivated failure;
- model-family and setting-gap notes that keep Qwen2.5-14B diagnostic results in bounds.

Older reproduction contact, superseded setup notes, weak probes, and failed intermediate branches are archived under:

```text
reports/_archive/20260616-pruned/
```

Archived reports remain citable evidence. They are not part of the active reading surface.

## Active Reports

- `20260618-skill-guided-state-admission-v2-preflight.md`
- `20260618-state-admission-v2-visible-facts-ablation.md`
- `20260618-state-admission-v2-abstention-gate-ablation.md`
- `20260618-state-admission-v2-option-state-and-direct-controls.md`
- `20260618-state-admission-v2-smoke-gpu.md`
- `20260618-reviewer-verdict-state-admission-series.md`
- `20260618-state-admission-v1-ledger-hidden-unit-pressure.md`
- `20260618-state-admission-v1-priority-7b-replication.md`
- `20260618-state-admission-v1-priority-executor-pressure.md`
- `20260618-state-admission-v1-qwen25-14b-pressure.md`
- `20260618-state-admission-v1-local-baselines.md`
- `20260618-state-admission-external-pressure-wave2.md`
- `20260618-state-admission-fullpaper-collision-audit.md`
- `20260618-perspectivegap-model-smoke-and-paper-story.md`
- `20260618-perspectivegap-benchmark-contact.md`
- `20260617-benchmark-first-reckoning.md`
- `20260617-hiddenbench-v2-design-audit.md`
- `20260617-hiddenbench-v2-stage1-smoke12-qwen25-14b.md`
- `20260617-hiddenbench-v2-stage1-full65-qwen25-14b.md`
- `20260617-hiddenbench-v2-stage2-sender-ablation-preflight.md`
- `20260617-hiddenbench-v2-stage2-sender-ablation-smoke12-qwen25-14b.md`
- `20260617-hiddenbench-v2-stage2-sender-ablation-full65-qwen25-14b.md`
- `20260617-hiddenbench-v2-stage3-blind-sender-preflight.md`
- `20260617-hiddenbench-v2-stage3-blind-sender-full65-qwen25-14b.md`
- `20260617-hiddenbench-stage2-external-pressure.md`
- `20260617-hiddenbench-communication-necessity-qwen25-14b.md`
- `20260617-communication-necessity-benchmark-landscape.md`
- `20260617-model-family-and-experiment-setting-gap.md`
- `20260617-a8002-docker-feasibility.md`
- `20260617-math-operator-lifecycle-v1-packet.md`
- `20260617-math-operator-lifecycle-v1-qwen25-14b.md`
- `20260617-next-typecast-experiment-preflight.md`
- `20260617-typecast-boundary-obedience-preflight.md`
- `20260617-typecast-math200-inert-receiver315-qwen25-14b.md`
- `20260617-typecast-repaired-controlstable-packet.md`
- `20260617-typecast-repaired-controlstable117-qwen25-14b.md`
- `20260615-authority-genesis-idea.md`
- `20260615-math200-peer-claim-hygiene.md`
- `20260615-pact-authority-evidence-case-audit.md`
- `20260615-pact-authority-evidence-stress-qwen25-14b.md`
- `20260615-pact-field-contract-quarantine.md`
- `20260615-pact-public-state-field-bridge.md`
- `20260615-pact-public-state-field-qwen25-14b-pressure.md`
- `20260615-pact-typed-boundary-split-qwen25-14b.md`
- `20260615-slot-level-peer-influence-protocol.md`
- `20260615-typed-public-state-math200-statistical-pressure.md`
- `20260616-a-conference-story-synthesis-epistemic-type-erasure.md`
- `20260616-external-novelty-pressure-epistemic-type-erasure.md`
- `20260616-math-authority-genesis-ladder-qwen25-14b.md`
- `20260616-math-authority-genesis-mechanism-audit.md`
- `20260616-math-epistemic-type-erasure-v2-qwen25-14b.md`
- `20260616-math-sender-receiver-micro-protocol-qwen25-14b.md`
- `20260616-multiagent-specificity-external-pdf-pressure.md`
- `20260616-research-progress-synthesis.md`
- `20260616-typecast-math200-clean-rawgold-diagnosis.md`

## Report Types

| Type | Use When | Template |
| --- | --- | --- |
| first insight report | a bounded run leaves something worth saying | `reports/_templates/short_report.md` |
| objective research report | multiple sources or runs make a bounded claim worth preserving | `reports/_templates/objective_research_report.md` |
| frontier scan | arXiv radar or reading queue needs triage | no fixed template yet |
| mentor note | preparing discussion questions and options | derive from objective report |

## Required Discipline

When making claims, keep them tied to:

- run IDs;
- log paths;
- result JSON files;
- code commits;
- paper links;
- evidence-register claim IDs.

A common sequence:

```text
What We Tried -> What Happened -> Things Noticed -> Failures / Friction -> Loose Threads -> Caveats
```

Do not keep a report at top level because it once mattered. Keep it at top level only if it still guides the current research decision.
