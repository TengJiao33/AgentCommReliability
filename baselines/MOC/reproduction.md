# MOC Reproduction Note

## Short Answer

MOC now has A800_2 smoke evidence with local Qwen2.5-7B-Instruct through a vLLM adapter. The completed 5-sample GSM8K topology matrix ran `Chain`, `FullConnected`, and `Random`; all three scored `5/5`, with token use around `14k` per mode.

The structural merge branch has also been exercised. A diagnostic `Chain`, 5-agent, `neighbor_hops=2`, `ism_r=0` GSM8K smoke completed `5/5` and recorded `50,906` compressed tokens from 15 merge-pair events.

This is Level 2 setup/smoke evidence, not a strict paper-scale reproduction.

## Scope

- method: MOC, Multi-Order Communication
- paper: https://arxiv.org/abs/2606.02359
- repo: https://github.com/yao-guan/MOC
- commit: `9c67c92507570704a7df73e452552a3f49e83897`
- machine: A800_2
- model: Qwen2.5-7B-Instruct served as `qwen2.5-7b`
- dataset: upstream preprocessed GSM8K CSV, first 1 and first 5 rows
- evidence level: Level 2 smoke/topology and forced structural-merge check

## Environment

- remote source: `/data/xuhaoming/yfy/research_workspace/baselines/MOC`
- env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- temporary vLLM server:
  - GPU: `1`
  - port: `8021`
  - log: `/data/xuhaoming/yfy/research_workspace/logs/moc-vllm-qwen25-7b-20260613_133817.log`
  - status: stopped after runs; GPU 1 released

## Commands

vLLM launch:

```bash
CUDA_VISIBLE_DEVICES=1 HF_HOME=/data/xuhaoming/yfy/research_workspace/hf_home \
nohup /data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python \
  -m vllm.entrypoints.openai.api_server \
  --model /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct \
  --served-model-name qwen2.5-7b \
  --host 127.0.0.1 \
  --port 8021 \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.80 \
  --max-model-len 4096 \
  --disable-log-requests
```

1-sample smoke:

```bash
MOC_USE_HASH_EMBEDDING=1 \
OPENAI_BASE_URL=http://127.0.0.1:8021/v1 \
OPENAI_API_KEY=EMPTY \
python experiments/run_experiment.py \
  --domain gsm8k \
  --n_size 1 \
  --llm_name vllm:qwen2.5-7b \
  --agent_nums 2 \
  --mode Chain \
  --batch_size 1 \
  --num_rounds 1 \
  --use_cot
```

5-sample topology matrix:

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

Forced structural-merge smoke:

```bash
MOC_USE_HASH_EMBEDDING=1 \
OPENAI_BASE_URL=http://127.0.0.1:8021/v1 \
OPENAI_API_KEY=EMPTY \
MOC_MERGE_LLM_NAME=vllm:qwen2.5-7b \
MOC_COMM_TRACE_JSONL=/data/xuhaoming/yfy/research_workspace/results/moc-forcedmerge-comm-events.jsonl \
PYTHONPATH=/data/xuhaoming/yfy/research_workspace/baselines/MOC:$PYTHONPATH \
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

## Outputs

- remote run note root: `/data/xuhaoming/yfy/research_workspace/experiments/20260613-a8002-moc-qwen25-7b-gsm8k-topology5`
- forced-merge run note root: `/data/xuhaoming/yfy/research_workspace/experiments/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke`
- remote MOC result dir: `/data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k`
- graph structures: `/data/xuhaoming/yfy/research_workspace/baselines/MOC/graph_structures/gsm8k`
- local run record: `experiments/20260613-a8002-moc-qwen25-7b-gsm8k-topology5/`
- local forced-merge record: `experiments/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke/`

## Result Snapshot

| Setting | Samples | Agents | Neighbor hops | Accuracy | Total tokens | Runtime |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Chain smoke | 1 | 2 | 1 | 1.0 | 2,991 | 9.187s |
| Chain | 5 | 3 | 1 | 1.0 | 14,529 | 34.474s |
| FullConnected | 5 | 3 | 1 | 1.0 | 14,042 | 26.863s |
| Random | 5 | 3 | 1 | 1.0 | 13,967 | 26.208s |
| Chain forced merge | 1 | 5 | 2 | 1.0 | 5,894 + 13,846 compressed | 54.319s |
| Chain forced merge | 5 | 5 | 2 | 1.0 | 22,718 + 50,906 compressed | 191.101s |

## Deviations From Upstream

- Added `VLLMChat` because upstream routes `qwen` model names to Ollama and its `GPTChat` expects a custom gateway, not OpenAI-compatible vLLM.
- Patched `Graph.merge_multiple_messages` to route structural merge calls through `LLMRegistry.get(self.llm_name)` / `VLLMChat` instead of hard-coded Ollama `gemma2:9b`.
- Prepared trace-only instrumentation patch `baselines/MOC/patches/a8002-comm-trace-events.patch` to write ISM merge/result sidecar events when `MOC_COMM_TRACE_JSONL` is set. This patch has not yet produced a remote run.
- Used deterministic hash embeddings because the expected local sentence-transformer model was absent.
- Created `gsm8k_test_n1.csv` and `gsm8k_test_n5.csv` from the upstream `gsm8k_test_n300.csv` for bounded smoke runs.
- Added a minimal `pyairports.airports` compatibility module inside the env because the installed `pyairports==0.0.1` wheel lacked the module required by `outlines`.

## Failures And Fixes

| Issue | Evidence | Fix | Method Behavior Changed? |
| --- | --- | --- | --- |
| Remote `git clone` failed with HTTP/2 framing errors. | remote clone logs during setup | cloned locally and transferred `git archive` source | no |
| Missing project dependencies in reused env. | import smoke | installed minimal pure-Python/runtime packages instead of full requirements | no |
| `sentence_transformers` import conflicted with local `datasets/` package and local embedding model was absent. | Graph import smoke | hash embedding fallback patch | yes for node-feature semantics in smoke |
| Upstream model registry routed `qwen` to Ollama. | code inspection and adapter smoke | `VLLMChat` adapter and `vllm:` prefix | no prompt/topology/eval change |
| `merge_multiple_messages` hard-coded Ollama `gemma2:9b`. | code inspection and forced-merge smoke | route merge calls through the configured `VLLMChat`; account those tokens under compressed counters | backend plumbing only |
| MOC detail JSON lacked per-sample merge source IDs. | unified trace extraction caveat | prepared `a8002-comm-trace-events.patch` to write sidecar JSONL events | no method behavior change expected |
| 4096-token vLLM context failed after the first forced-merge preflight reached final decision. | `/data/xuhaoming/yfy/research_workspace/logs/moc-forcedmerge-chain5-hop2-n1-20260613_1420_forcedmerge.log` | restarted vLLM with `--max-model-len 8192` | backend capacity only |
| vLLM returned 500 because `outlines` imported broken `pyairports`. | vLLM server log | added minimal compatibility module | no |

## Caveats

- This run did not reproduce the paper's reported results.
- The topology matrix did not trigger the LLM structural merge branch; the separate forced-merge smoke did.
- The sample size is too small to interpret topology quality.
- The result is still valuable as setup evidence: source, data, graph execution, local model serving, and evaluation all run end to end.

## Next Small Check

First apply `a8002-comm-trace-events.patch` and rerun a tiny forced-merge smoke with `MOC_COMM_TRACE_JSONL`; then run a modest `neighbor_hops=1` vs `neighbor_hops=2` comparison on shared samples and use the unified trace schema to inspect answer flips and merge-induced information loss.
