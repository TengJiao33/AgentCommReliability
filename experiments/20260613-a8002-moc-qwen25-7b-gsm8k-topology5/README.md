# 20260613-a8002-moc-qwen25-7b-gsm8k-topology5

## Short Answer

MOC ran end to end on A800_2 with local Qwen2.5-7B-Instruct through vLLM. A 5-sample GSM8K topology smoke completed for `Chain`, `FullConnected`, and `Random`; each scored `5/5`.

## Scope

- Method: MOC
- Model: Qwen2.5-7B-Instruct, served as `qwen2.5-7b`
- Dataset: MOC upstream `datasets/test/gsm8k_test_n300.csv`, first 5 rows copied to `gsm8k_test_n5.csv`
- Seed: `42`
- Samples: `5`
- Comparison target: topology modes only (`Chain`, `FullConnected`, `Random`)

## Resource Budget

- Machine: A800_2
- GPU IDs: server on GPU `1`
- Timeout: `30m` per mode
- Started by: Codex

## Code

- Upstream repo: https://github.com/yao-guan/MOC
- Commit: `9c67c92507570704a7df73e452552a3f49e83897`
- Remote path: `/data/xuhaoming/yfy/research_workspace/baselines/MOC`
- Local changes:
  - `baselines/MOC/patches/a8002-smoke-embedding-fallback.patch`
  - `baselines/MOC/patches/a8002-vllm-openai-adapter.patch`

## Environment

- Env path: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- vLLM server log: `/data/xuhaoming/yfy/research_workspace/logs/moc-vllm-qwen25-7b-20260613_133817.log`
- vLLM status: stopped after run

## Data

- Data path: `/data/xuhaoming/yfy/research_workspace/baselines/MOC/datasets/test/gsm8k_test_n5.csv`
- Split: test
- Sampling: first 5 rows from upstream preprocessed `gsm8k_test_n300.csv`

## Command

```bash
for MODE in Chain FullConnected Random; do
  MOC_USE_HASH_EMBEDDING=1 \
  OPENAI_BASE_URL=http://127.0.0.1:8021/v1 \
  OPENAI_API_KEY=EMPTY \
  timeout 30m python experiments/run_experiment.py \
    --domain gsm8k \
    --n_size 5 \
    --llm_name vllm:qwen2.5-7b \
    --agent_nums 3 \
    --mode "$MODE" \
    --edge_density 0.7 \
    --random_dag_seed 42 \
    --batch_size 1 \
    --num_rounds 1 \
    --use_cot
done
```

## Remote Artifacts

- Main logs:
  - `/data/xuhaoming/yfy/research_workspace/experiments/20260613-a8002-moc-qwen25-7b-gsm8k-topology5/Chain.log`
  - `/data/xuhaoming/yfy/research_workspace/experiments/20260613-a8002-moc-qwen25-7b-gsm8k-topology5/FullConnected.log`
  - `/data/xuhaoming/yfy/research_workspace/experiments/20260613-a8002-moc-qwen25-7b-gsm8k-topology5/Random.log`
- Result JSON:
  - `/data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b_Chain_2026-06-13-13-43-32.json`
  - `/data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b_FullConnected_2026-06-13-13-44-10.json`
  - `/data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b_Random_2026-06-13-13-44-41.json`

## Result

| Mode | Status | Accuracy | Total tokens | Evaluation time |
| --- | --- | ---: | ---: | ---: |
| Chain | complete | 1.0 | 14,529 | 34.474s |
| FullConnected | complete | 1.0 | 14,042 | 26.863s |
| Random | complete | 1.0 | 13,967 | 26.208s |

## Status Timeline

- `2026-06-13 13:18`: source archive expanded on A800_2
- `2026-06-13 13:38`: vLLM launched on GPU 1
- `2026-06-13 13:42`: 1-sample smoke completed
- `2026-06-13 13:43`: 5-sample Chain launched
- `2026-06-13 13:44`: FullConnected and Random completed
- `2026-06-13 13:45`: vLLM stopped and GPU 1 released

## Caveats

- Smoke-level evidence only.
- `neighbor_hops=1`, so this does not test the paper's multi-order hop setting.
- Structural message consolidation did not trigger; compressed-token counters are `0`.
- Hash embeddings replaced the unavailable sentence-transformer model.

## Next Step

Run a forced-merge smoke after adapting `merge_multiple_messages` away from hard-coded Ollama.

