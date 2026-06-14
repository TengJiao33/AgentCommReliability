# Reports

Use this folder for human-readable research notes and mentor-facing summaries.

Reports can interpret evidence, but they should not force significance onto a run. They do not replace paper cards, run records, or raw logs.

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

## Existing Reports

- `20260612-madmm-short-subset-first-insights.md`
- `20260612-madmm-trace-message-retention.md`
- `20260612-dar-arithmetics-short-matrix.md`
- `20260612-dar-gsm8k-short-matrix.md`
- `20260612-multi-agent-frontier-scan.md`
- `20260613-moc-gsm8k-topology-smoke.md`
- `20260613-moc-forced-merge-smoke.md`
- `20260613-madmm-dar-trace-case-followup.md`
- `20260613-retained-message-role-audit.md`
- `20260613-guarded-retention-offline-simulation.md`
- `20260613-dar-guarded-answer-diversity-run.md`
- `20260613-madmm-benchmark-atlas.md`
- `20260613-dar-retention-split-ablation.md`
- `20260614-dar-sample20-retained-surface-note.md`
