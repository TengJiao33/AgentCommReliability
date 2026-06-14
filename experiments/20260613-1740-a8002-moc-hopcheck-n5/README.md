# MOC Hop-Depth Trace Check

## What We Tried

Ran a tiny instrumented MOC comparison on the same first 5 GSM8K samples, using `Chain`, 5 agents, one round, and local Qwen2.5-7B-Instruct through vLLM. The comparison checks `neighbor_hops=1` against forced structural merge with `neighbor_hops=2` and `ism_r=0`.

## Scope

- Method: MOC
- Model: Qwen2.5-7B-Instruct served as `qwen2.5-7b-moc-hopcheck`
- Dataset: MOC upstream GSM8K preprocessed CSV
- Samples: 5
- Agents: 5
- Topology: `Chain`
- Rounds: 1
- Comparison target: trace shape and token cost, not benchmark accuracy

## Resource Notes

- Machine: A800_2
- GPU: 7
- vLLM port: `8028`
- vLLM was stopped after the runs and GPU 7 was released.

## Code

- Upstream repo: https://github.com/yao-guan/MOC
- Commit: `9c67c92507570704a7df73e452552a3f49e83897`
- Required local patches:
  - `baselines/MOC/patches/a8002-smoke-embedding-fallback.patch`
  - `baselines/MOC/patches/a8002-vllm-openai-adapter.patch`
  - `baselines/MOC/patches/a8002-vllm-structural-merge.patch`
  - `baselines/MOC/patches/a8002-comm-trace-events.patch`

## Command Shape

```bash
cd /data/xuhaoming/yfy/research_workspace/baselines/MOC
MOC_USE_HASH_EMBEDDING=1 \
OPENAI_BASE_URL=http://127.0.0.1:8028/v1 \
OPENAI_API_KEY=EMPTY \
MOC_MERGE_LLM_NAME=vllm:qwen2.5-7b-moc-hopcheck \
MOC_COMM_TRACE_JSONL=<hop-events-jsonl> \
PYTHONPATH=/data/xuhaoming/yfy/research_workspace/baselines/MOC:$PYTHONPATH \
timeout 30m /data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python experiments/run_experiment.py \
  --domain gsm8k \
  --n_size 5 \
  --llm_name vllm:qwen2.5-7b-moc-hopcheck \
  --agent_nums 5 \
  --mode Chain \
  --batch_size 1 \
  --num_rounds 1 \
  --use_cot \
  --neighbor_hops <1-or-2> \
  --ism_r 0 \
  --ism_epsilon 0.01 \
  --ism_kppa 45
```

## Remote Artifacts

| Artifact | Path |
| --- | --- |
| hop1 log | `/data/xuhaoming/yfy/research_workspace/logs/moc-hopcheck-hop1-n5-20260613_1740.log` |
| hop2 log | `/data/xuhaoming/yfy/research_workspace/logs/moc-hopcheck-hop2-n5-20260613_1740.log` |
| hop1 events | `/data/xuhaoming/yfy/research_workspace/results/moc-hopcheck-n5-20260613_1740/hop1_comm_events.jsonl` |
| hop2 events | `/data/xuhaoming/yfy/research_workspace/results/moc-hopcheck-n5-20260613_1740/hop2_comm_events.jsonl` |
| hop1 unified trace | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-hopcheck-hop1-n5.comm_trace.jsonl` |
| hop2 unified trace | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-hopcheck-hop2-n5.comm_trace.jsonl` |

Small local copies include summaries, details, logs, sidecar events, unified traces, schema v1.1 traces, and `analysis_summary.json`.

## Derived Schema v1.1 Traces

Created locally without rerunning the model:

```bash
python scripts/extract_comm_trace_schema.py moc \
  --detail-json experiments/20260613-1740-a8002-moc-hopcheck-n5/hop1_detail.json \
  --summary-json experiments/20260613-1740-a8002-moc-hopcheck-n5/hop1_summary.json \
  --comm-events-jsonl experiments/20260613-1740-a8002-moc-hopcheck-n5/hop1_comm_events.jsonl \
  --run-id 20260613-1740-a8002-moc-hop1-n5-v11 \
  --method Chain \
  --task-regime saturated_arithmetic \
  --public-state-surface neighbor_context \
  --communication-policy topology_hop1 \
  --out experiments/20260613-1740-a8002-moc-hopcheck-n5/comm_trace_hop1_v11.jsonl

python scripts/extract_comm_trace_schema.py moc \
  --detail-json experiments/20260613-1740-a8002-moc-hopcheck-n5/hop2_detail.json \
  --summary-json experiments/20260613-1740-a8002-moc-hopcheck-n5/hop2_summary.json \
  --comm-events-jsonl experiments/20260613-1740-a8002-moc-hopcheck-n5/hop2_comm_events.jsonl \
  --run-id 20260613-1740-a8002-moc-hop2-forcedmerge-n5-v11 \
  --method Chain \
  --task-regime saturated_arithmetic \
  --public-state-surface compressed_summary \
  --communication-policy topology_merge \
  --out experiments/20260613-1740-a8002-moc-hopcheck-n5/comm_trace_hop2_v11.jsonl
```

Validation: both traces have 5 rows, schema `acr.comm_trace.v1.1`, and four derived `context_events` entries per row from MOC `ism_result` sidecar events.

## What Happened

| Setting | Accuracy | Total Tokens | Compressed Tokens | Communication Events |
| --- | ---: | ---: | ---: | --- |
| hop1 | 5/5 | 20,977 | 0 | 20 `ism_result`, no merge |
| hop2 forced merge | 5/5 | 22,422 | 50,699 | 20 `ism_result`, 15 `ism_merge` |

All hop1 `ism_result` events have `merge_performed=false`. All hop2 `ism_result` events have `merge_performed=true`, and the sidecar captures merge source IDs, represented IDs, similarity, selected summary strategy, and compressed-token stats.

## Caveats

- The hop2 setting uses forced merge with `ism_r=0`.
- Hash embeddings are still used.
- Accuracy is saturated at 5 samples; useful signal here is trace coverage and token cost.

## Loose Threads

- If MOC remains interesting, scale this exact hop1/hop2 trace comparison to 20-50 shared samples and inspect any answer flips or summary information loss.
