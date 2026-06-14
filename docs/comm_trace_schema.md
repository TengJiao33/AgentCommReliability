# Communication Trace Schema

`scripts/extract_comm_trace_schema.py` normalizes DAR, MAD-MM, and MOC outputs into JSONL using schema version `acr.comm_trace.v1`.

Each line is one problem instance for one method/run.

## Core Fields

- `run_id`, `method_family`, `method`
- `instance_id`, `sample_index`, `question`, `gold_answer`
- `final`: final answer and correctness
- `transition`: `right_to_wrong`, `wrong_to_right`, `stable_right`, `stable_wrong`, or `unknown`
- `rounds`: per-round agent answers, correctness, confidence when available, and token stats when available
- `retention_events`: retained/dropped/merged agent IDs when the source exposes them
- `communication_events`: structural merge or other communication events
- `token_cost`: input/output/total tokens plus compressed-token counters when available
- `method_comparison`: optional baseline comparison, currently used by MAD-MM against COT
- `source`: raw file paths used to build the record

Missing source data is represented as `null`, not omitted.

## Commands

MAD-MM:

```bash
python scripts/extract_comm_trace_schema.py madmm \
  --run-id 20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset \
  --results-dir /data/xuhaoming/yfy/research_workspace/results/mad-mm-short-subset/main/qwen2.5-14b/gsm8k \
  --out /data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-14b-gsm8k-short-subset.comm_trace.jsonl
```

Verified MAD-MM MATH50 probe:

```bash
python scripts/extract_comm_trace_schema.py madmm \
  --run-id 20260613-1855-a8002-madmm-qwen25-7b-math50-probe \
  --results-dir /data/xuhaoming/yfy/research_workspace/results/mad-mm-benchmark-probe/math_probe50/qwen2.5-7b/math \
  --methods cot mad_naive mad_objective mad_subjective \
  --out /data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-7b-math50-probe.comm_trace.jsonl
```

DAR:

```bash
python scripts/extract_comm_trace_schema.py dar \
  --run-id 20260612-a8002-dar-qwen25-7b-gsm8k-filtercritical-short \
  --method filter_critical \
  --history-jsonl /data/xuhaoming/yfy/research_workspace/results/dar-short-filtercritical-qwen25-7b-gsm8k100-20260612_193240/out/history/gsm8k_100__qwen2.5-7b_N=3_R=1_P=True_V=True_K=None_M=filter_critical_S=42.jsonl \
  --out /data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-qwen25-7b-gsm8k-filtercritical-short.comm_trace.jsonl
```

Future DAR runs with `baselines/DAR/patches/a8002-filter-retention-history.patch` should include `retention_events` in each filtered round. The extractor reads those events when present; older histories leave retention fields empty.

If `baselines/DAR/patches/a8002-guarded-answer-diversity.patch` is also applied, DAR `retention_events` can additionally include `original_retained_agent_ids`, `guard_mode`, `guard_added_agent_ids`, `guard_removed_agent_ids`, `guard_notes`, `guard_parseable_buckets`, `guard_missing_parseable_buckets`, and `retention_message_mode`.

Verified instrumented DAR check:

```bash
python scripts/extract_comm_trace_schema.py dar \
  --run-id 20260613-1721-a8002-dar-trace-filtercritical-gsm8k5 \
  --method filter_critical \
  --history-jsonl /data/xuhaoming/yfy/research_workspace/results/dar-trace-check-filtercritical-gsm8k5-20260613_1721/out/history/gsm8k_5__qwen2.5-7b_N=3_R=1_P=True_V=True_K=None_M=filter_critical_S=42.jsonl \
  --out /data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-trace-filtercritical-gsm8k5.comm_trace.jsonl
```

MOC:

```bash
python scripts/extract_comm_trace_schema.py moc \
  --run-id 20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke \
  --detail-json /data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b_2026-06-13-14-21-39_detail.json \
  --summary-json /data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b_Chain_2026-06-13-14-21-39.json \
  --log-path /data/xuhaoming/yfy/research_workspace/logs/moc-forcedmerge-chain5-hop2-n5-20260613_1425_forcedmerge8192.log \
  --out /data/xuhaoming/yfy/research_workspace/experiments/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke/comm_trace_moc.jsonl
```

Future MOC runs with `baselines/MOC/patches/a8002-comm-trace-events.patch` should set `MOC_COMM_TRACE_JSONL` during the run and pass it back into extraction:

```bash
python scripts/extract_comm_trace_schema.py moc \
  --run-id <run-id> \
  --detail-json <detail.json> \
  --summary-json <summary.json> \
  --comm-events-jsonl <moc_comm_events.jsonl> \
  --out <comm_trace.jsonl>
```

Verified instrumented MOC check:

```bash
python scripts/extract_comm_trace_schema.py moc \
  --run-id 20260613-1718-a8002-moc-trace-instrumentation-n1 \
  --detail-json /data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b-trace_2026-06-13-17-19-41_detail.json \
  --summary-json /data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b-trace_Chain_2026-06-13-17-19-41.json \
  --comm-events-jsonl /data/xuhaoming/yfy/research_workspace/results/moc-trace-check-20260613_1718/moc_comm_events.jsonl \
  --out /data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-trace-instrumentation-n1.comm_trace.jsonl
```

## Current Verified Outputs

| Method family | Rows | Output |
| --- | ---: | --- |
| MOC | 5 | `/data/xuhaoming/yfy/research_workspace/experiments/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke/comm_trace_moc.jsonl` |
| MOC instrumented | 1 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-trace-instrumentation-n1.comm_trace.jsonl` |
| MOC hop1 instrumented | 5 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-hopcheck-hop1-n5.comm_trace.jsonl` |
| MOC hop2 instrumented | 5 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-hopcheck-hop2-n5.comm_trace.jsonl` |
| MAD-MM | 400 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-14b-gsm8k-short-subset.comm_trace.jsonl` |
| MAD-MM MATH probe | 200 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-7b-math50-probe.comm_trace.jsonl` |
| MAD-MM benchmark sweep MATH50 | 150 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-math-50.comm_trace.jsonl` |
| MAD-MM benchmark sweep MMLU-Pro50 | 150 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-mmlu_pro-50.comm_trace.jsonl` |
| MAD-MM benchmark sweep AIME24 | 90 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-aime24-all.comm_trace.jsonl` |
| MAD-MM benchmark sweep AIME25 | 90 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-aime25-all.comm_trace.jsonl` |
| DAR | 10 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-qwen25-7b-gsm8k-filtercritical-short.comm_trace.jsonl` |
| DAR instrumented | 5 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-trace-filtercritical-gsm8k5.comm_trace.jsonl` |
| DAR full-history instrumented | 100 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-trace-filtercritical-gsm8k100-fullhistory.comm_trace.jsonl` |
| DAR guarded answer-only | 100 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-guarded-answer-diversity-gsm8k100-20260613_2038.comm_trace.jsonl` |
| DAR answer-only no guard | 100 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-answer-only-noguard-gsm8k100-20260613_2143.comm_trace.jsonl` |
| DAR guard full | 100 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-guard-full-gsm8k100-20260613_2143.comm_trace.jsonl` |

The older DAR trace has only 10 rows because that run saved only the first 10 histories. The instrumented DAR check confirms full-history saving and per-round retention events.

## Current Limits

- Older MOC detail JSON lacks per-agent round traces and per-sample merge source IDs, so pre-instrumentation MOC records include run-level merge counts parsed from logs. Instrumented MOC runs should pass `--comm-events-jsonl`.
- Older DAR history lacks retained/dropped IDs for `filter_critical`, so pre-instrumentation DAR retention fields are `null`. Instrumented DAR runs should use `--save_full_history`.
- MAD-MM exposes masks directly, so retained/dropped IDs and right/wrong retention counts are available.
- MAD-MM aggregate accuracy should still be read from the upstream result JSONs. The unified trace normalizer now compares textual labels case-insensitively, which is required for MMLU-Pro lower-case predictions against upper-case gold labels.
