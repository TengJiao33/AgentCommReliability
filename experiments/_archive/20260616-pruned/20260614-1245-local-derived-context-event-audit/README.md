# 20260614-1245-local-derived-context-event-audit

## What We Tried

Summarized derived `context_events` from existing schema v1.1 real baseline traces.

No model was launched. No GPU or remote machine was used.

## Scope

- Method: context-event audit over existing communication traces
- Model: none
- Dataset: existing MAD-MM MATH50, DAR GSM8K100, and MOC GSM8K5 trace artifacts
- Samples: 610 trace records across 7 trace files
- Comparison target: recipient-context structure, not accuracy benchmarking

## Resource Notes

- Machine: local Windows workspace
- GPU IDs: none
- Timeout: none
- Started by: Codex

## Code

- Script: `scripts/summarize_context_events.py`
- Inputs: local `*_v11.jsonl` trace files

## Command

```bash
python scripts/summarize_context_events.py \
  experiments/_archive/20260616-pruned/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/comm_trace_madmm_math50_v11.jsonl \
  experiments/_archive/20260616-pruned/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/comm_trace_dar_v11.jsonl \
  experiments/_archive/20260616-pruned/20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100/comm_trace_dar_guarded_v11.jsonl \
  experiments/_archive/20260616-pruned/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_answer_only_noguard_v11.jsonl \
  experiments/_archive/20260616-pruned/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_guard_full_v11.jsonl \
  experiments/_archive/20260616-pruned/20260613-1740-a8002-moc-hopcheck-n5/comm_trace_hop1_v11.jsonl \
  experiments/_archive/20260616-pruned/20260613-1740-a8002-moc-hopcheck-n5/comm_trace_hop2_v11.jsonl \
  --out experiments/_archive/20260616-pruned/20260614-1245-local-derived-context-event-audit/summary.json
```

## Outputs

- `summary.json`

## What Happened

| Metric | Value |
| --- | ---: |
| Trace files | 7 |
| Records | 610 |
| Rows with context events | 560 |
| Context events | 590 |
| From MAD-MM `mask_history` | 150 |
| From DAR `retention_events` | 400 |
| From MOC `ism_result` | 40 |

## Things Noticed

- MAD-MM MATH50 CoT has no context events; MAD-MM debate methods have one derived context event per row.
- DAR original `filter_critical` retains one visible peer in 64/100 rows, two in 27/100, and all three in 9/100.
- DAR guard variants shift visible context larger: 53 rows with one peer, 35 with two, and 12 with three.
- MOC hop1 has 20 target contexts with one visible represented source each.
- MOC hop2 has 5 target contexts with one visible source and 15 target contexts where a merge represents two source agents.

## Caveats

- These context events are derived, not raw prompt logs.
- Visible/suppressed counts are source-agent counts, not semantic evidence quality.
- MOC transitions remain `unknown` because this extractor lacks an independent before-stage baseline for MOC detail files.

## Loose Threads

- Inspect whether DAR right-to-wrong cases correlate more with visible count, message surface, or downstream continuation.
- Add prompt-level recipient-context logging in one small real run if the next GPU use is justified.
