---
name: research-experiment-gate
description: Project-level gate for designing, launching, evaluating, and recording research experiments, especially LLM/GPU benchmark runs, sender-receiver packets, multi-agent communication studies, parser-sensitive datasets such as MATH, and any result that may become a paper claim. Use before starting a run, when preparing packets, when results look strange, when comparing against earlier benchmark results, when writing run records, or when deciding whether a failed experiment is evidence or plumbing.
---

# Research Experiment Gate

## Core Rule

Make the experiment earn the GPU run before launching it.

Do not treat a larger run as progress unless the packet, gold labels, parser,
controls, and intended readout are already clear enough that a surprising
result can be diagnosed. This skill is a gate, not a brake: it should prevent
sloppy runs while still allowing large, decisive experiments once the setup is
sharp.

## Use Pattern

Choose the smallest mode that fits the turn:

- preflight mode: before building a packet or launching GPU;
- packet-audit mode: after materializing prompts but before running;
- launch mode: immediately before remote/GPU execution;
- result-triage mode: after a run, especially if the result looks strange;
- record mode: before ending a run-bearing turn;
- postmortem mode: when an experiment failed to answer its intended question.

If the user explicitly says to run now, still run the minimum preflight that
can catch fatal issues. If a fatal issue appears, stop and explain it before
using GPU.

## Preflight Contract

Before any claim-bearing experiment, write down these items in the chat, a run
note, or a packet README:

- purpose: the exact hypothesis or diagnostic question;
- unit: case, row, packet, sender artifact, agent turn, or task instance;
- primary contrast: the one comparison that would answer the question;
- secondary contrasts: controls and robustness checks;
- success signal: what result would promote the idea;
- failure signal: what result would retire, weaken, or redirect it;
- invalidation conditions: parser failure, label leakage, wrong gold, baseline
  instability, unbalanced packet, sample contamination, or control noise;
- expected artifact paths: packet, outputs, evaluation, analysis, report.

If these cannot be stated, do not call the run decisive.

## Paper-Facing Mechanism Gate

For A-conference mechanism-improvement runs, record the table role before
launch. The run should know whether it is a direct baseline, structured/model
only baseline, executor-assisted method row, transparent heuristic, oracle, or
ablation.

Record the fairness contract: same backbone or explicit cross-model reference,
same packet rows and evaluator, compatible budget/cost accounting, and no
prediction-time leakage of evaluator-only fields.

For compiler, executor, or admission claims, prefer paired artifacts: model-only
outputs, executed/compiled outputs over the same proposals, and a paired delta.
If a strong transparent baseline or oracle smoke is absent, say why.

Do not treat final task success as sufficient. Predeclare the diagnostic
metrics that would show the mechanism changed the right failure surface, such
as coverage, precision, leakage, budget pass, rejection, forced commitment,
cost, or slot completeness.

Benchmark construction is allowed when existing benchmarks cannot measure the
target failure. In that case, the run must include executable scorer paths,
direct controls, oracle controls, and a failure taxonomy plan; otherwise treat
the artifact as a diagnostic packet rather than a benchmark claim.

## Gold And Parser Gate

For parser-sensitive tasks, audit gold before trusting any metric.

For MATH and symbolic answer tasks:

- use original boxed/reference answers as primary gold;
- preserve trace-extracted numeric answers only as diagnostic metadata;
- compare at least several concrete rows by hand: question, gold, model answer,
  parse result, semantic status;
- run a gold-smoke when possible, scoring `{final answer: <gold>}` through the
  same evaluator;
- verify fractions, roots, pi, percentages, variables, units, sets, matrices,
  and mixed numbers;
- reject any packet where source filtering depends on lossy numeric gold unless
  that exact label source has already been audited.

Do not compare two runs on the same benchmark unless they use compatible gold
and evaluator semantics.

## Packet Gate

Before GPU launch, inspect the materialized packet rather than trusting the
builder summary.

Check:

- row counts by condition, variant, source case, and artifact type;
- one-to-one or many-to-one grouping expected by the design;
- baseline rows exist for every case that needs paired deltas;
- candidate visibility matches the channel contract;
- hidden/quarantine/typed-redacted prompts do not leak the candidate answer;
- unrelated controls are actually unrelated;
- sender-candidate correctness is computed against the same gold used for final
  evaluation;
- baseline-correct filters use audited semantic labels, not stale trace labels;
- content-held-constant contrasts really hold content constant except for the
  intended cast or lifecycle state;
- prompt text states the task without over-warning the model into eliminating
  the effect being tested.

For a large packet, sample concrete rows from every condition, not just the
first and last row.

## Control Gate

Every claim-bearing communication experiment needs controls that can separate
the target effect from background instability.

Prefer these controls when relevant:

- no sender / self revision;
- unrelated sender message;
- visible inert scratch;
- direct peer message;
- admitted shared state;
- verifier/admission frame;
- quarantine or rejected metadata-only state;
- typed noncommitment or rederive-required state.

If controls show comparable failure rates to target channels, treat the run as
background instability until concrete case inspection says otherwise.

## Launch Gate

Immediately before GPU or remote execution, record:

- remote host and path;
- model path and served model name;
- GPU id, port, max tokens, temperature, timeout;
- packet path and expected row count;
- output directory and whether it already exists;
- storage and GPU occupancy if relevant;
- exact launch command;
- planned stop condition and cleanup command.

Use one GPU unless the user explicitly authorizes more. Do not leave a required
server, runner, or helper process running at turn end.

## Result Triage

When a result looks strange, inspect concrete answers before interpreting
tables.

Minimum triage:

- compare baseline answer, gold, prediction, and parser output for several
  true positives and false positives;
- check whether the surprising delta survives raw-gold or semantic relabeling;
- check whether sender labels and wrong-answer uptake were computed from the
  correct gold;
- inspect violation cards by case, not just aggregate rates;
- separate direct answer copying, operator/relation inheritance, local re-solve
  noise, parser unknowns, and missing final-answer formatting;
- compare with earlier benchmark results only after confirming the same gold,
  evaluator, prompt contract, and source pool assumptions.

If the issue is plumbing, say so plainly. Do not turn it into a behavioral
claim.

## Record Gate

Before ending a turn that launched, evaluated, or materially diagnosed an
experiment, create or update:

- `experiments/<run-id>/README.md` for exact run record;
- `reports/<date>-<short-topic>.md` for interpretation, if the run changes the
  research state;
- packet README or summary when a new reusable packet is created.

The run record must include:

- purpose and status;
- remote/local paths;
- model, GPU, packet, command, and row counts;
- output files;
- evaluation command and summary;
- concrete caveats;
- whether the result is claim-bearing, diagnostic, failed, or retired;
- next usable artifact, if any.

Do not rely on chat history as the only record.

## Postmortem Gate

If an experiment fails to answer its purpose, write the failure in the record.

Classify the failure:

- design failure: wrong contrast, weak stimulus, bad controls;
- data failure: wrong gold, contaminated sample, label leakage;
- evaluator failure: parser, metric, missing output, incompatible comparison;
- execution failure: GPU, timeout, crash, partial output;
- true negative: setup was clean and the intended effect did not appear.

Only true negatives should pressure the research idea directly. The other
failure types pressure the experimental workflow.

When a failure exposes a reusable prevention rule, update this skill or
`skills/repro-friction-memory/SKILL.md` before continuing.
