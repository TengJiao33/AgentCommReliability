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

DAR:

```bash
python scripts/extract_comm_trace_schema.py dar \
  --run-id 20260612-a8002-dar-qwen25-7b-gsm8k-filtercritical-short \
  --method filter_critical \
  --history-jsonl /data/xuhaoming/yfy/research_workspace/results/dar-short-filtercritical-qwen25-7b-gsm8k100-20260612_193240/out/history/gsm8k_100__qwen2.5-7b_N=3_R=1_P=True_V=True_K=None_M=filter_critical_S=42.jsonl \
  --out /data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-qwen25-7b-gsm8k-filtercritical-short.comm_trace.jsonl
```

Future DAR runs with `baselines/DAR/patches/a8002-filter-retention-history.patch` should include `retention_events` in each filtered round. The extractor reads those events when present; older histories leave retention fields empty.

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

## Current Verified Outputs

| Method family | Rows | Output |
| --- | ---: | --- |
| MOC | 5 | `/data/xuhaoming/yfy/research_workspace/experiments/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke/comm_trace_moc.jsonl` |
| MAD-MM | 400 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-14b-gsm8k-short-subset.comm_trace.jsonl` |
| DAR | 10 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-qwen25-7b-gsm8k-filtercritical-short.comm_trace.jsonl` |

DAR currently has only 10 rows because that run saved only the first 10 histories.

## Current Limits

- Existing MOC detail JSON lacks per-agent round traces and per-sample merge source IDs, so current MOC records include run-level merge counts parsed from logs. `a8002-comm-trace-events.patch` is prepared to write per-sample sidecar events for future runs.
- Existing DAR history lacks retained/dropped IDs for `filter_critical`, so current DAR retention fields are `null`. `a8002-filter-retention-history.patch` is prepared to write retained/dropped IDs and support full-history saving for future runs.
- MAD-MM exposes masks directly, so retained/dropped IDs and right/wrong retention counts are available.
