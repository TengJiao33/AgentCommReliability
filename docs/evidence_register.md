# Evidence Register

This file is a parking place for observations or claims that seem worth carrying forward.

It is not a scoreboard and not a demand that every run produce a claim. Most notes should stay in run records, reports, or the project log. Add something here only when it feels likely to matter again.

Contact shorthand:

| Level | Meaning |
| ---: | --- |
| 1 | source-only or paper/digest signal |
| 2 | setup, import, loader, or smoke evidence |
| 3 | short-subset run with concrete metrics or traces |
| 4 | controlled variant with repeated or neighboring checks |
| 5 | reduced author-style reproduction |
| 6 | full target matrix compared against the paper |

## Carried Observations And Claims

| ID | Claim | Evidence Level | Source | Status | Caveat | Next Check |
| --- | --- | ---: | --- | --- | --- | --- |
| E-001 | MAD-MM provides a runnable baseline and trace logs for studying wrong-memory contamination in multi-agent debate. | 3 | `papers/cards/mad-mm.md`; `reports/20260612-madmm-short-subset-first-insights.md`; `reports/20260612-madmm-trace-message-retention.md` | active | based on one short GSM8K subset plus paper reading. | compare with another message-retention method under a bounded setting. |
| E-002 | On the 100-sample Qwen2.5-14B/GSM8K subset, naive MAD improved accuracy from 0.94 to 0.96 over CoT while using much more tokens. | 3 | `experiments/20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset/analysis_short_subset_summary.json` | factual | not a benchmark-scale result. | repeat on another seed or task if the cost is justified. |
| E-003 | Objective masking reduced token use relative to naive MAD but introduced at least one observed regression. | 3 | same as E-002; case `id=214`; `reports/20260612-madmm-trace-message-retention.md` | factual | still one short subset; trace inspection now explains the regression mechanism. | test a disagreement-aware retention method such as DAR. |
| E-004 | Subjective masking behaved almost like a costly no-op on the short subset, keeping 296 of 300 memories. | 3 | same as E-002 | factual | may be task-specific or prompt-specific. | inspect subjective judge prompts and kept/dropped examples. |
| E-005 | The local arXiv scan contains several candidate follow-ups focused on conditional, sparse, evidence-aware, or structured communication. | 1 | `reports/20260612-multi-agent-frontier-scan.md` | hypothesis | source-only scan; no code inspection yet. | create paper cards before promoting any candidate to experiment. |
| E-006 | Documentation should separate raw run records from interpretation. | 2 | current repo structure and recording standards | accepted process rule | process claim, not empirical claim. | enforce through templates and project log. |
| E-007 | On the MAD-MM short subset, objective masking selected only wrong memory despite correct memories being available in cases `214` and `1227`. | 3 | `experiments/20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset/trace_cases_summary.json`; `reports/20260612-madmm-trace-message-retention.md` | factual | case-level evidence only; not a rate estimate for all tasks. | compare retained-message traces against an explicit disagreement-aware retention rule. |
| E-008 | Subjective masking kept 296/300 memories overall but dropped the only correct first-round memory in case `1227`. | 3 | same as E-007 | factual | single case for the dropped-correct-minority behavior; subjective judge output text was not yet separately audited. | inspect subjective judge prompts or compare with explicit disagreement-preserving filters. |
| E-009 | DAR can be launched on A800_2 with local Qwen2.5-7B-Instruct after local model-path, parser, and output-path patches. | 2 | `experiments/20260612-a8002-dar-qwen25-7b-arithmetics-smoke/`; `baselines/DAR/reproduction.md` | factual | smoke only; no 100-sample performance result. | run bounded 100-sample arithmetics short matrix. |
| E-010 | On the 100-sample Qwen2.5-7B-Instruct arithmetics short matrix, Basic MAD ended at 0.98, Top-K uncertainty 0.5 ended at 0.94, and DAR `filter_critical` ended at 0.99. | 3 | `experiments/20260612-a8002-dar-qwen25-7b-arithmetics-short-matrix/summary.json`; `reports/20260612-dar-arithmetics-short-matrix.md` | factual | generated arithmetic only; one seed/model; token accounting not normalized across methods. | inspect per-sample histories and consider a GSM8K short matrix. |
| E-011 | On the 100-sample Qwen2.5-7B-Instruct GSM8K short matrix, Basic MAD ended at 0.95, Top-K uncertainty 0.5 ended at 0.94, and DAR `filter_critical` ended at 0.93. | 3 | `experiments/20260612-a8002-dar-qwen25-7b-gsm8k-short-matrix/summary.json`; `reports/20260612-dar-gsm8k-short-matrix.md` | factual | one seed/model; GSM8K loaded through project-local MAD-MM JSONL fallback; non-debug histories include only first 10 samples. | analyze flips and retained IDs before drawing a mechanism claim. |
| E-012 | MOC can run end to end on A800_2 with local Qwen2.5-7B-Instruct via a vLLM adapter for tiny GSM8K topology and forced structural-merge smoke tests. | 2 | `experiments/20260613-a8002-moc-qwen25-7b-gsm8k-topology5/`; `experiments/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke/`; `reports/20260613-moc-gsm8k-topology-smoke.md`; `reports/20260613-moc-forced-merge-smoke.md`; `baselines/MOC/reproduction.md` | factual | smoke only; forced merge uses `ism_r=0`; hash embeddings used; MOC raw detail lacks per-sample merge source IDs. | add per-sample merge instrumentation before scaling hop-depth comparisons. |
| E-013 | A first unified communication trace schema can extract comparable final correctness, right/wrong transitions, retention or merge events, and token cost from current MAD-MM, DAR, and MOC artifacts. | 2 | `scripts/extract_comm_trace_schema.py`; `docs/comm_trace_schema.md`; remote unified traces under `/data/xuhaoming/yfy/research_workspace/results/unified-traces/` | factual | method-specific raw logs expose different detail levels; current completed DAR history has only 10 saved rows; current completed MOC merge events are run-level from logs. Trace instrumentation patches are prepared but not yet represented in a remote run. | apply MOC/DAR instrumentation patches and rerun tiny checks before scaling comparisons. |

## Status Labels

| Status | Meaning |
| --- | --- |
| factual | Directly recorded from a run, source, or file. |
| active | Current working interpretation with bounded support. |
| hypothesis | Plausible but not yet checked enough. |
| challenged | Conflicting evidence exists. |
| retired | No longer useful or unsupported after checks. |

## Update Rule

When a report leaves behind a durable observation or claim, add or update a row. If the report is just a local encounter, it does not need to modify this file.

When a run contradicts a claim, keep the old claim and mark it `challenged` instead of silently deleting it.
