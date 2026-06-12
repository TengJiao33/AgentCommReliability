# Reports

Use this folder for human-readable research notes and mentor-facing summaries.

Reports interpret evidence. They should not replace paper cards, run records, or raw logs.

## Report Types

| Type | Use When | Template |
| --- | --- | --- |
| first insight report | a bounded run has produced a small but useful signal | `reports/_templates/short_report.md` |
| objective research report | multiple sources or runs support a bounded claim | `reports/_templates/objective_research_report.md` |
| frontier scan | arXiv radar or reading queue needs triage | no fixed template yet |
| mentor note | preparing discussion questions and options | derive from objective report |

## Required Discipline

Keep claims tied to:

- run IDs;
- log paths;
- result JSON files;
- code commits;
- paper links;
- evidence-register claim IDs.

Prefer the sequence:

```text
Short Answer -> Scope -> Sources -> Results -> Observations -> Interpretation -> Caveats -> Next Small Check
```

## Existing Reports

- `20260612-madmm-short-subset-first-insights.md`
- `20260612-madmm-trace-message-retention.md`
- `20260612-dar-arithmetics-short-matrix.md`
- `20260612-multi-agent-frontier-scan.md`
