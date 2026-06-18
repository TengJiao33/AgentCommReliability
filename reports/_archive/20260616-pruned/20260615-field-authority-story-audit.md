# Field-Authority Story Audit

Date: 2026-06-15

## Verdict

**Classification: live diagnostic / bounded protocol candidate.**

This is not yet a solid paper story and not a novelty story.

It is live because the same mechanism now appears in:

- offset50 public-state field pressure;
- offset50 quarantine intervention;
- external collision pressure;
- offset100 neighboring-slice pressure;
- offset100 bridge labels.

But it is not solid yet because the current evidence is still a saved-field
re-answering stress test, not a full multi-agent rerun or cross-task protocol.
It also has strong prompt wording and strict-span confounds.

## Evidence Map

| Artifact | What It Directly Shows | Caveat |
| --- | --- | --- |
| `reports/20260615-pact-public-state-field-qwen25-14b-pressure.md` | On offset50, public target without the original question collapses, while hiding or freezing target helps over original public state. | One saved-field slice, not full PACT rerun. |
| `reports/20260615-pact-field-contract-quarantine.md` | First intervention-shaped quarantine beats fixed controls on offset50 (`0.610` EM). | Uses paired target-slot diagnostic and exact-match span noise remains. |
| `reports/_archive/20260616-pruned/20260615-field-contract-quarantine-external-pressure.md` | Broad novelty claims collide with PACT, DeLM, memory-card, and security/trust-boundary work. | Literature pressure only. |
| `reports/_archive/20260616-pruned/20260615-field-authority-offset100-pressure.md` | On offset100, frozen question target is best (`0.560` EM); standalone detector underperforms (`0.440`); public target without question collapses (`0.300`). | Prompt wording differs between security projection and frozen control. |
| `reports/_archive/20260616-pruned/20260615-field-authority-offset100-bridge-audit.md` | Offset100 failures are inspectable: `20` target-authority units, `10` target-contract units, `18` final-answer/span units, `25` evidence/content units. | Evaluation-side labels use gold correctness and span audits. |

## A / B / C / M / D

**A: Prior surface.** PACT-style action-state public communication exposes
structured fields such as `Action Required`, `Environment State`,
`Action Result`, and final answer candidates to downstream generation.

**B: Diagnosed cause candidate.** Some public fields carry authority, not just
information. In particular, an upstream `Action Required` can become a lossy or
over-authoritative substitute for the original question. Final-answer
candidates can also become attractors.

**C: Current contribution shape.** Not a detector yet. The current C-shape is a
diagnostic/protocol surface:

- trusted root: original question;
- allowed observations: evidence/result fields;
- projected authority: question-derived target only;
- blocked authority: upstream public target and final-answer candidate unless a
  stronger verifier exists.

**M: Metric.** HotpotQA EM/F1 on saved-field re-answering packets, sliced by
field visibility and source run.

**D: Diagnostic.** Field bridge labels and paired deltas:

- target-authority collapse when original question is hidden;
- frozen question-target rescues/regressions;
- final-answer candidate regressions;
- strict-span/granularity failures;
- evidence/content failures that the authority story does not explain.

## What Survives

The durable claim is narrow:

**Public `Action Required` is not a reliable standalone task contract. A
downstream answerer needs the trusted question root, or a projection of public
target authority back to that root.**

This is supported by two neighboring slices:

- offset50: public target without question underperforms and target quarantine
  helps;
- offset100: public target without question collapses to `0.300` EM, while
  frozen question target reaches `0.560` EM.

The field bridge audit also shows that this is not just an aggregate score
quirk: `20/100` offset100 units are directly target-authority failures and
`10/100` are target-contract units.

## What Dies

These should not be carried forward as live claims:

- standalone lexical authority detector as a method component;
- broad novelty around structured public state;
- broad novelty around shared verified context;
- final-answer candidate licensing as a near-term route;
- aggregate EM improvement as sufficient proof of the mechanism.

The detector is especially important to retire for now. On offset100,
standalone quarantine has EM `0.440`, below public-state/no-final (`0.500`),
security projection (`0.510`), and frozen target (`0.560`).

## What This Cannot Prove

The current evidence cannot prove that field-authority projection is a general
multi-agent method. It cannot yet show:

- survival under a full PACT rerun rather than saved-field re-answering;
- survival on 2WikiMultiHopQA, MuSiQue, or another distributed-information task;
- a standalone runtime verifier that detects unsafe target authority;
- a clean separation from prompt wording effects;
- a large enough gain after removing strict-span and granularity artifacts.

## Retirement Conditions

Retire or demote this handle if:

- a cleaner projection/frozen-target packet does not move target-authority or
  target-contract bridge units on another slice;
- gains are mostly strict-span formatting rather than field-authority movement;
- another task family shows no target-authority collapse when the original
  question is hidden;
- a full PACT rerun shows the saved-field stress test was an artifact of
  re-answering.

## Next Pressure

Do not build another detector yet.

The next useful object is:

1. Build a cleaner projection-only packet whose prompt wording matches the
   stronger frozen-target control.
2. Run or reuse it on a fresh neighboring slice, not the same offset100 packet
   only.
3. Score movement by bridge layer, especially `target_authority` and
   `target_contract`, not just aggregate EM.
4. If that survives, move to a task where public state is necessary rather than
   merely available.

Current story status:

**live, bounded, falsifiable; not solid yet; not novel as broad public state.**
