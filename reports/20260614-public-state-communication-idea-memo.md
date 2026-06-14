# Public-State Communication Reliability Idea Memo

## Core Idea

Multi-agent communication reliability should be evaluated at the public-state
interface, not only at final accuracy.

For current LLM agent systems, a useful decomposition is:

```text
task regime -> public state surface -> target preservation -> final commitment
```

The failure question is not only whether agents reason correctly. It is whether
the shared public state carries the right target, evidence, action result, and
answer contract forward without letting private reasoning noise, distractors,
or overly generic requests distort the final answer.

## Why This Is Alive

Local reproductions now support the decomposition:

- MAD-MM shows that communication-method ranking changes by benchmark, so task
  regime matters.
- DAR shows that selection, message surface, and continuation failures are
  separable.
- PACT shows that public action-state fields can contain useful answer signals
  while final EM remains poor because final commitment or target granularity
  fails.
- The PACT final-answer contract improves EM on multiple slices, which makes
  final commitment a real model-behavior confound.
- The offset50 and offset100 target diagnostics show that `Action Required`
  can drift, underspecify the target, or mismatch the final answer.

## Current Hypothesis

A compact target-state field may preserve the useful part of target-slot control
without the large token cost of a verbose target-preservation prompt.

Candidate public message:

```text
Target Slot: [answer type; anchor entity or entities; required qualifier]
Action Required: ...
Environment State: ...
Action Result: ...
Final Answer: ...
```

The test is not whether this single field immediately wins EM. The test is
whether it moves target preservation independently while keeping cost near the
final-answer-contract baseline.

## Next GPU Check

Fresh HotpotQA slice, Qwen2.5-14B, paired arms:

| Arm | Purpose |
| --- | --- |
| final-answer contract | current strongest surface baseline |
| compact target-state + final-answer contract | test compact target preservation on top of final commitment |
| compact target-state only | isolate target-state behavior without final-answer contract |

Primary metrics:

- EM and F1;
- right-to-wrong / wrong-to-right transitions;
- average communication and total tokens;
- target-slot drift candidates;
- `Target Slot` field compliance and stability.

## What Would Count As Progress

The compact target-state arm is promising if it:

- reduces target-slot candidates versus final-only;
- avoids the large token increase seen in the verbose target contract;
- does not increase right-to-wrong cases substantially;
- preserves or improves F1 even if EM is flat.

It is not promising if it becomes another long prompt surface, frequently emits
generic target slots, or causes downstream agents to overcommit to an early
misread target.
