# MOC Hop-2 Forced-Merge Smoke

## Short Answer

MOC's structural merge branch now runs through the local vLLM-backed `VLLMChat` adapter. A 5-question GSM8K smoke with `neighbor_hops=2`, `Chain`, 5 agents, and `ism_r=0` completed at `5/5` accuracy and recorded `50,906` compressed tokens.

This is diagnostic smoke evidence, not benchmark evidence.

## Scope

- Method: MOC, Multi-Order Communication
- Model: Qwen2.5-7B-Instruct served as `qwen2.5-7b`
- Dataset: MOC upstream GSM8K preprocessed CSV, first 1 and first 5 rows
- Topology: `Chain`
- Agents: 5 `MathSolver` agents
- Rounds: 1
- Neighbor hops: 2
- Merge forcing: `ism_r=0`, `ism_kppa=45`

## Resource Budget

- Host: A800_2
- GPU: 1
- vLLM port: `8021`
- vLLM max context: `8192`
- Timeout: 75 minutes for preflight, 90 minutes for 5-question run
- GPU 1 was released after the run.

## Code

- Upstream: https://github.com/yao-guan/MOC
- Upstream commit: `9c67c92507570704a7df73e452552a3f49e83897`
- Remote source: `/data/xuhaoming/yfy/research_workspace/baselines/MOC`
- New patch: `baselines/MOC/patches/a8002-vllm-structural-merge.patch`

Existing required patches:

- `baselines/MOC/patches/a8002-vllm-openai-adapter.patch`
- `baselines/MOC/patches/a8002-smoke-embedding-fallback.patch`

## Environment

- Python env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- vLLM log: `/data/xuhaoming/yfy/research_workspace/logs/moc-vllm-qwen25-7b-20260613_1425_forcedmerge8192.log`
- `PYTHONPATH` was pinned to the MOC repo so `datasets.data_process` resolves to the local MOC package.

## Command

```bash
cd /data/xuhaoming/yfy/research_workspace/baselines/MOC
export PYTHONPATH=/data/xuhaoming/yfy/research_workspace/baselines/MOC:$PYTHONPATH
export MOC_USE_HASH_EMBEDDING=1
export OPENAI_BASE_URL=http://127.0.0.1:8021/v1
export OPENAI_API_KEY=EMPTY
export MOC_MERGE_LLM_NAME=vllm:qwen2.5-7b

timeout 90m /data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python experiments/run_experiment.py \
  --domain gsm8k \
  --n_size 5 \
  --llm_name vllm:qwen2.5-7b \
  --agent_nums 5 \
  --mode Chain \
  --batch_size 1 \
  --num_rounds 1 \
  --use_cot \
  --neighbor_hops 2 \
  --ism_r 0 \
  --ism_epsilon 0.01 \
  --ism_kppa 45
```

## Remote Artifacts

| Artifact | Path |
| --- | --- |
| n=1 log | `/data/xuhaoming/yfy/research_workspace/logs/moc-forcedmerge-chain5-hop2-n1-20260613_1425_forcedmerge8192.log` |
| n=5 log | `/data/xuhaoming/yfy/research_workspace/logs/moc-forcedmerge-chain5-hop2-n5-20260613_1425_forcedmerge8192.log` |
| n=1 summary | `/data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b_Chain_2026-06-13-14-20-24.json` |
| n=5 summary | `/data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b_Chain_2026-06-13-14-21-39.json` |
| n=5 detail | `/data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b_2026-06-13-14-21-39_detail.json` |
| unified trace | `/data/xuhaoming/yfy/research_workspace/experiments/_archive/20260616-pruned/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke/comm_trace_moc.jsonl` |

Small local copies:

- `summary.json`
- `detail.json`
- `comm_trace_moc.jsonl`
- `summary_n1.json`
- `detail_n1.json`

## Result

| Run | Accuracy | Total tokens | Compressed tokens | Runtime |
| --- | ---: | ---: | ---: | ---: |
| n=1 preflight | 1/1 | 5,894 | 13,846 | 54.319s |
| n=5 forced merge | 5/5 | 22,718 | 50,906 | 191.101s |

The n=5 log shows:

- merged pairs: `15`
- summary strategy calls: `75`
- compressed prompt tokens: `39,810`
- compressed completion tokens: `11,096`

## Status Timeline

- Initial run reached `[ISM Phase 2] Merged pair`, proving the branch was hit, but failed at final decision with a 4096-context vLLM limit.
- vLLM was restarted with `--max-model-len 8192`.
- The 1-question preflight completed.
- The 5-question forced-merge smoke completed.
- Unified MOC trace was extracted with `scripts/extract_comm_trace_schema.py`.

## Caveats

- `ism_r=0` is a forced-merge diagnostic setting.
- Hash embeddings are deterministic but not equivalent to the upstream sentence-transformer path.
- MOC result detail JSON does not store per-agent round traces or per-sample merge events; the unified trace records run-level merge counts from the log.
- Accuracy is not meaningful at 5 samples; the useful evidence is that multi-hop neighbor collection and structural compression now execute end to end.

## Next Step

Use the unified trace schema to collect comparable right-to-wrong and wrong-to-right cases across larger MOC/DAR/MAD-MM runs, with per-sample retention or merge instrumentation where the upstream code exposes it.
