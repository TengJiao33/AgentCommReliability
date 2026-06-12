# Documentation System

This project should read like a research record, not a chat transcript. The goal is to preserve what was done, what was observed, what is only hypothesized, and what should be checked next.

## Document Layers

| Layer | Location | Purpose | What Belongs Here | What Does Not Belong Here |
| --- | --- | --- | --- | --- |
| Project orientation | `README.md`, `project_intake.md` | Explain why the project exists and how to enter it. | Scope, research questions, first milestone, important constraints. | Detailed experiment interpretation. |
| Operating rules | `docs/` | Define repeatable practice. | machine rules, experiment protocol, recording standard, documentation rules. | Raw results or paper summaries. |
| Research map | `docs/research_map.md` | Keep the current conceptual structure visible. | problem axes, mechanism families, known failure modes, open hypotheses. | New claims without evidence. |
| Evidence register | `docs/evidence_register.md` | Track claims and their support level. | claim, source, evidence type, status, caveat, next check. | Long narrative analysis. |
| Paper queue | `papers/reading_queue.md` | Decide what to read or reproduce next. | priority, paper, why it matters, first action. | Full paper notes. |
| Paper cards | `papers/cards/` | Capture one paper in comparable structure. | method, setup, baselines, communication variables, caveats. | Unchecked hype or broad survey prose. |
| Baseline notes | `baselines/<method>/` | Record upstream code and reproduction path. | repo, commit, install notes, smallest runnable command, patches. | General paper discussion. |
| Run records | `experiments/<run-id>/` | Preserve exact run facts. | command, model, data, env, outputs, metric snapshot, caveats. | Post-hoc interpretation beyond labeled notes. |
| Reports | `reports/` | Interpret multiple facts into a readable argument. | short answer, setup, compared runs, observations, caveats, next experiment. | Untraceable claims. |
| Project log | `docs/project_log.md` | Chronological audit trail. | important actions, completed artifacts, major decisions. | Detailed run tables already stored elsewhere. |

## Artifact Lifecycle

```text
arXiv radar or mentor seed
  -> reading queue
  -> paper card
  -> baseline note
  -> short run record
  -> evidence register entry
  -> objective report
  -> next experiment or deprioritize
```

Promotion rule: a paper should not become an experiment only because its abstract sounds relevant. It should expose a controllable variable, have runnable code or a clear small reimplementation path, and connect to a project question.

## Evidence Levels

| Level | Label | Meaning | Allowed Claim |
| --- | --- | --- | --- |
| 0 | source-only | Paper, digest, or abstract inspected. | "The paper claims..." |
| 1 | code-inspected | Repo, prompt, or evaluation path inspected. | "The implementation appears to..." |
| 2 | setup evidence | Environment and code path prepared. | "The baseline can be launched under..." |
| 3 | short-subset evidence | Bounded run completed on a small subset. | "On this model/task/subset..." |
| 4 | repeated-subset evidence | Same comparison repeated across seed, task, or model. | "The trend appears stable across..." |
| 5 | standard-subset evidence | Author settings reproduced on a reduced matrix. | "A reduced author-style reproduction shows..." |
| 6 | full reproduction evidence | Full target matrix completed and compared. | "This reproduces the reported setting..." |

Default wording should name the level. Avoid turning Level 3 evidence into a general method claim.

## Writing Rules

Use objective presentation first:

- Separate `Observation`, `Interpretation`, and `Caveat`.
- Tie each result to a run ID, source file, paper link, or commit.
- Record negative and stopped runs, especially when they reveal resource cost.
- Prefer tables for comparisons and prose for interpretation.
- Keep hypotheses as hypotheses until another run, code path, or paper supports them.

Avoid:

- "This proves..."
- "The paper is wrong..."
- "The method is SOTA..."
- "Agents understand..."
- "We reproduced the paper..." unless the full matrix is actually reproduced.

## Standard Sections

Paper cards should answer:

- What is the one-sentence claim?
- What problem does the method isolate?
- What communication variables are controlled?
- What baselines and datasets are used?
- What code path needs inspection?
- What would make the claim fail?

Run notes should answer:

- What exact command ran?
- On which machine and model?
- How much resource was budgeted?
- What artifacts were produced?
- What is the evidence level?
- What caveat limits the result?

Reports should answer:

- What was compared?
- What changed in metrics?
- What changed in traces?
- Which explanation is plausible?
- Which explanation remains untested?
- What is the next smallest useful check?
