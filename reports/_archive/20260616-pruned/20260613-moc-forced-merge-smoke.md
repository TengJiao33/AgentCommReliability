# MOC Forced Structural-Merge Smoke

## Short Answer

MOC's core structural merge branch now runs on A800_2 with local Qwen2.5-7B-Instruct through `VLLMChat`. A 5-question GSM8K diagnostic smoke with `neighbor_hops=2`, 5-chain agents, and forced merge completed `5/5`; the useful signal is not accuracy, but that the multi-hop neighbor summary and compression path produced nonzero compressed-token accounting.

## Setup

- Run record: `experiments/_archive/20260616-pruned/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke/`
- Patch: `baselines/MOC/patches/a8002-vllm-structural-merge.patch`
- Model: Qwen2.5-7B-Instruct via vLLM `qwen2.5-7b`
- Topology: `Chain`, 5 agents
- Hop depth: `neighbor_hops=2`
- Merge forcing: `ism_r=0`, `ism_kppa=45`

## Result

| Run | Accuracy | Total tokens | Compressed tokens | Runtime |
| --- | ---: | ---: | ---: | ---: |
| n=1 preflight | 1/1 | 5,894 | 13,846 | 54.319s |
| n=5 forced merge | 5/5 | 22,718 | 50,906 | 191.101s |

The n=5 log recorded 15 merged pairs and 75 summary-strategy calls.

## Trace Schema

`scripts/extract_comm_trace_schema.py` now emits a common JSONL schema for:

- MOC forced-merge smoke: 5 rows
- MAD-MM short subset: 400 rows
- DAR filter-critical history: 10 rows, limited by saved histories

Current normalized trace paths:

- `/data/xuhaoming/yfy/research_workspace/experiments/_archive/20260616-pruned/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke/comm_trace_moc.jsonl`
- `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-14b-gsm8k-short-subset.comm_trace.jsonl`
- `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-qwen25-7b-gsm8k-filtercritical-short.comm_trace.jsonl`

Observed transition counts from the normalized traces:

| Method family | Rows | Transition signal |
| --- | ---: | --- |
| MOC | 5 | final-only for now; merge counts are run-level |
| MAD-MM | 400 | vs COT: `wrong_to_right=6`, `right_to_wrong=1` |
| DAR | 10 | round0 to round1: `right_to_wrong=1`, `stable_right=9` |

## Caveats

- The MOC run is forced-merge smoke, not a paper-default setting.
- MOC detail JSON does not preserve per-agent round outputs or per-sample merge source IDs, so the unified trace uses run-level merge counts parsed from logs.
- DAR history only includes the first 10 samples for this run.
- The next useful patch is per-sample MOC merge instrumentation: source IDs, merged IDs, retained direct IDs, dropped IDs, and compressed-token deltas per merge event. `baselines/MOC/patches/a8002-comm-trace-events.patch` is prepared for that, but it has not yet produced a remote run.
