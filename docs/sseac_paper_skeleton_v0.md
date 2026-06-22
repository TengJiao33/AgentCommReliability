# SSEAC Paper Skeleton v0

Snapshot date: `2026-06-19`.

Working title:

```text
Source-Scoped Evidence Admission for Reliable Multi-Agent Communication
```

## Core Claim

Role-specific multi-agent communication fails when free-form messages mix evidence discovery, source authorization, budget control, rejection, and downstream commitment. SSEAC separates these responsibilities: an LLM proposes source-scoped evidence candidates and priorities, then a deterministic compiler enforces source, scope, verification, budget, and sufficiency constraints before any downstream answer.

Current status: this is a live method-paper claim under pressure, and the evidence hierarchy has been corrected. Public benchmark evidence must come first. HSA has a strong internal diagnostic signal, but it cannot carry the external method-validity claim. PG40 / PerspectiveGap public slices are now the primary route for the paper-facing main table.

## Template Being Imitated

The primary template is `PAL + Sparse MAD + Decomposed Prompting`.

| Template | Pattern to imitate | SSEAC mapping |
| --- | --- | --- |
| PAL | LLM generates an intermediate object; executor handles reliable execution. | LLM proposes candidate evidence units; compiler handles admission constraints. |
| Sparse MAD | Communication policy is the experimental variable; quality and cost are both reported. | Evidence visibility/admission policy is the variable; task, leakage, budget, and admitted-card cost are reported. |
| Decomposed Prompting | System is a set of replaceable handlers with clear interfaces. | Candidate generator, source/scope checker, priority estimator, compiler, and downstream answerer are separate components. |
| ReAct | A trajectory makes hidden failure surfaces inspectable. | Source cards, candidate units, rejected units, admitted state, and final decision form an inspectable admission trajectory. |

## Abstract Draft

Large language model agents increasingly coordinate by appending free-form messages to a shared context. This design gives agents flexibility, but it also leaves a critical question implicit: which source-specific pieces of evidence are allowed to become public state for each role? We study this admission problem in role-specific and partially observed communication settings, where failures include missing required evidence, admitting distractors, leaking out-of-scope facts, exceeding evidence budgets, and committing to answers under insufficient evidence.

We introduce Source-Scoped Evidence Admission Compiler (SSEAC), a test-time communication pipeline that separates semantic proposal from constraint execution. The model proposes candidate evidence units, target recipients, claimed slots, and priorities. A deterministic compiler then enforces recipient scope, verification state, duplicate removal, budget constraints, and sufficiency before downstream use. This design turns unreliable message exchange into an inspectable admitted-state trajectory.

We evaluate SSEAC first on public or public-derived benchmark slices such as PerspectiveGap / PG40. Hidden-State Admission v0 is used as a mechanism-analysis suite. We compare against direct prompting, free exchange, source-ledger prompting, model-only structured admission, transparent greedy baselines, and oracle controls under the same backbone and budget. We report task success together with evidence coverage, precision, leakage, budget pass, forced commitment, admitted-card cost, and compiler diagnostics.

## Introduction Spine

Paragraph 1: Multi-agent LLM systems often rely on natural-language messages as the communication substrate. This is convenient, but role-specific tasks require more than message sharing: they require deciding which evidence should become visible to which role.

Paragraph 2: Free-form communication hides several failures under one transcript. A receiver may miss necessary private evidence, accept distractors, use out-of-scope facts, exceed a context or evidence budget, or answer when admissible evidence is insufficient. These failures can produce the same final-answer error, so final accuracy alone gives weak diagnostic signal.

Paragraph 3: Existing multi-agent debate and routing work usually varies who talks to whom or how many turns are used. That leaves admission as an implicit model behavior. Our central object is source-scoped admitted state: a structured public state that records source identity, recipient scope, verification status, cost, rejection, and sufficiency.

Paragraph 4: SSEAC is a test-time system for this object. The model proposes candidate units and priorities; the compiler executes hard constraints and builds a final slot table. This mirrors the PAL pattern: use the model for semantic proposal and a deterministic executor for the part that must be reliable.

Paragraph 5: The experimental question is whether executable admission improves communication reliability under same-backbone comparisons. We therefore evaluate `structured_no_compiler` against `ours_sseac_v0`, transparent heuristics, source-ledger prompts, and oracle controls, reporting both task and evidence-discipline metrics.

## Method Section Skeleton

### Problem Setup

Each instance contains roles, candidate decisions, role budgets, source cards, and hidden evaluator slots. At prediction time the model sees source cards with allowed fields only: `card_id`, `source_role`, `recipient_scope`, `verification_state`, `evidence_type`, `cost`, and `content`. It does not see evaluator-required slots, gold assignments, or expected final decisions.

### SSEAC Pipeline

1. Normalize benchmark information into `SourceCard` and `TaskSpec`.
2. Prompt the LLM to propose candidate units:

```json
{
  "unit_id": "u1",
  "recipient": "role_name",
  "card_ids": ["c1"],
  "priority": 10.0,
  "claimed_slots": ["short label"],
  "claimed_effect": "why this card matters"
}
```

3. Compile candidate units into admitted/rejected units using deterministic constraints.
4. Build a slot table and final state.
5. Score task success and evidence-discipline metrics.

### Ablations

| Condition | Meaning |
| --- | --- |
| `direct` | Model answers without admitted-state structure. |
| `free_exchange` | Agents exchange or receive broad natural-language context. |
| `source_ledger` | Model receives explicit source/scope metadata but self-enforces constraints. |
| `structured_no_compiler` | Model emits SSEAC schema; admitted state follows the model output directly. |
| `ours_sseac_v0` | Model emits SSEAC schema; compiler enforces hard constraints and sufficiency. |
| `transparent_greedy` | Non-LLM heuristic baseline using visible metadata. |
| `oracle` | Upper bound with gold admissible units or assignments. |

## Experiment Tables To Build

### Table 1: PG40 / PerspectiveGap Public-Slice Main Table

Purpose: test role-specific evidence admission under budget pressure on a public benchmark slice.

Rows:

| Row | Current status |
| --- | --- |
| oracle utility | exists: `40/40`, utility `1.0000` |
| utility-density greedy | exists: `25/40`, utility `0.9825` |
| source-ledger 14B compiled | exists: `11/40`, utility `0.8707` |
| direct prompt | must be filled on same model and same public slice |
| structured_no_compiler | card-unit limit5 exists: `0/5`, budget pass `0.0000`, utility `0.1803`; needs public-slice completion |
| ours_sseac_v0 | card-unit limit5 exists: `1/5`, budget pass `1.0000`, utility `0.8155`, coverage `0.6667`; current result is not yet a method advantage |
| role-plan diagnostic | exists: `1/5`, budget pass `1.0000`, utility `0.7811`; retired |

Primary readout: strict pass, coverage, precision, distractor leakage, budget pass, utility, exact role, paired delta.

### Table 2: HSA-v0 Mechanism Analysis

Purpose: analyze whether admitted evidence supports final decisions while avoiding over-admission and forced commitment. This table explains mechanism behavior and should not be used as the external benchmark table.

Rows:

| Row | Current status |
| --- | --- |
| oracle admissible facts | exists: 36-row `36/36`, base `12/12`, perturb `24/24` |
| shared-only verified | exists: 36-row `24/36`, base strict `0/12`, extra final cards `129` |
| all-scoped verified | exists: 36-row `36/36`, extra final cards `195` |
| structured_no_compiler | 36-row constraint run exists: `16/36`, base `0.9167`, perturb `0.2083`, extra final cards `43` |
| ours_sseac_v0 | 36-row hard admission exists: `34/36`; blocker completion `35/36`; support completion `36/36`, base `1.0000`, perturb `1.0000`, extra final cards `42` |

Primary readout: strict, base strict, perturb strict, slot recall, extra final cards, forced commitment, paired delta.

### Table 3: State Admission V1.1 Mechanism Support

Purpose: show that priority + executor already has a method-shaped signal.

Rows:

| Row | Current status |
| --- | --- |
| oracle | exists: `40/40` |
| group-density global | exists: `32/40`, utility `0.9666` |
| direct 14B default | exists: `0/40` |
| priority 14B pair-group-primary | exists: `33/40`, utility `0.9014` |
| priority 7B fallback-required | exists: `31/40`, utility `0.8431` |

Primary readout: strict, utility, budget pass, closure violations, cross-model replication.

## Claims And Evidence Handles

| Claim | Current evidence | Status |
| --- | --- | --- |
| Free-form communication can fail through admission pollution. | HiddenBench old exchange `23/55` clean versus fact-only `55/55`; recommendation leakage and shared overtalk reduced by fact-state contract. | supported as background |
| Direct admitted-state generation is unreliable under constraints. | State Admission V1.1 direct 14B `0/40`; over-budget and empty roles filled. | supported on synthetic packet |
| LLM + executor is a viable method shape. | State Admission V1.1 priority + executor 14B `33/40`; 7B fallback `31/40`. | supported with caveats |
| Source/scope ledger helps proposal quality but does not solve budgeted routing. | PerspectiveGap source-ledger improves coverage; PG40 source-ledger 14B compiled `11/40` below greedy `25/40`. | supported as boundary |
| SSEAC improves over model-only structured admission. | HSA 36-row run improves `16/36 -> 34/36` under hard admission, then `36/36` with support completion and extra final cards `42`; old 33/15 replay is clean. PG40 card-unit limit5 improves strict `0/5 -> 1/5`, budget, utility, and exact role, while role-plan does not improve over card-unit. | internal and pilot evidence only; public benchmark proof still missing |

## Reviewer Risks

Contribution risk: the method may look like a prompt wrapper. Mitigation: show `structured_no_compiler` versus `ours_sseac_v0`, plus deterministic compiler diagnostics.

Baseline risk: transparent greedy baselines are strong on PG40. Mitigation: report them in the main table, and downgrade claim if SSEAC only beats weak text baselines.

Dataset risk: HSA-v0 is still small and partly constructed, even after the 36-row expansion. Mitigation: present the current result as a mechanism table and keep the paper-facing main claim tied to public benchmark or public-slice results.

Metric risk: final strict may reward all-scoped evidence. Mitigation: report extra final cards, leakage, budget pass, forced commitment, and admitted-card cost beside strict.

Leaderboard risk: closed-source frontier scores may distract from the method claim. Mitigation: keep them as reference ceiling only.

## Next Experimental Gate

Purpose: determine whether deterministic admission execution improves over model-only structured admission after fixing the current candidate construction bottlenecks.

Unit: PG40 / PerspectiveGap public slice first; HSA remains a mechanism table. PG40 should continue only with a new budget-aware ranking mechanism or paired sorter.

Primary contrast: `ours_sseac_v0` versus `structured_no_compiler`.

Secondary contrasts: source-ledger, transparent greedy/all-scoped, shared-only, oracle.

Success signal: on a public benchmark slice, compiled SSEAC beats direct, source-ledger, and structured no compiler under the same model and budget, while remaining interpretable against transparent greedy and oracle.

Failure signal: compiler path produces no meaningful paired delta, gains only come from rejecting many useful cards, or PG40 ranking variants stay below the card-unit contract.

Invalidation conditions: prompt leaks evaluator-only slots, rows are not paired, scorer cannot distinguish model-only from compiled, or endpoint output fails schema too often to interpret.

Immediate artifacts:

```text
reports/20260619-public-benchmark-report-reset.md
docs/pg40_tight_budget_numeric_main_table.md
docs/next_model_run_queue.md
```
