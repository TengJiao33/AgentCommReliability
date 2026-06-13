# MOC Source Note

## Upstream

- paper: https://arxiv.org/abs/2606.02359
- repo: https://github.com/yao-guan/MOC
- commit inspected: `9c67c92507570704a7df73e452552a3f49e83897`
- license: no license file observed in the source archive
- local path: not cloned locally; remote path `/data/xuhaoming/yfy/research_workspace/baselines/MOC`

## Why This Baseline

MOC directly targets the project question of agent communication reliability: it changes the communication receptive field from first-order neighbor concatenation to a multi-hop evidence stream, then tries to consolidate messages under token constraints.

## Smallest Runnable Path

The upstream README command is:

```bash
python experiments/run_experiment.py --domain mmlu --mode Random --edge_density 0.7 --agent_nums 7 --random_dag_seed 42 --neighbor_hops 2
```

For our A800_2 smoke, the smallest completed path was:

```bash
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

## Installation Notes

- environment reused: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- model server: temporary vLLM OpenAI-compatible server on GPU 1, port `8021`
- model path: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- code source transfer: direct remote `git clone` failed, so source was cloned locally and transferred via `git archive`
- minimal added packages: `tenacity`, `class-registry`, `ollama`, `shortuuid`, `setuptools==80.9.0`, `scikit-learn`, `torch-geometric`, `sentence-transformers`, `wikipedia`, `astunparse`
- vLLM/outlines compatibility: the installed `pyairports==0.0.1` wheel was broken, so a minimal `pyairports.airports.AIRPORT_LIST` module was added inside the project env

## Local Adaptation Patches

- `baselines/MOC/patches/a8002-smoke-embedding-fallback.patch`
  - purpose: use deterministic 384-dimensional hash embeddings when the upstream local sentence-transformer path is unavailable
  - method behavior: affects node feature embeddings for smoke runs; strict reproduction should install the real embedding model
- `baselines/MOC/patches/a8002-vllm-openai-adapter.patch`
  - purpose: add `VLLMChat` and route `--llm_name vllm:<served-model>` to an OpenAI-compatible local vLLM server
  - method behavior: backend plumbing only; prompts, topology, and evaluation remain upstream
- `baselines/MOC/patches/a8002-vllm-structural-merge.patch`
  - purpose: route `merge_multiple_messages` through the configured LLM registry / `VLLMChat` instead of hard-coded Ollama `gemma2:9b`
  - method behavior: backend plumbing for the structural merge branch; compressed-token counters are preserved separately from ordinary agent tokens
- `baselines/MOC/patches/a8002-comm-trace-events.patch`
  - purpose: write per-sample ISM merge/result events to `MOC_COMM_TRACE_JSONL`
  - method behavior: trace-only instrumentation; adds source IDs, merged IDs, direct retained IDs, dropped-direct IDs, and merge token deltas without changing prompts or decisions

## Code Map

| Component | File / Function | Notes |
| --- | --- | --- |
| entrypoint | `experiments/run_experiment.py` | dataset config, topology args, graph creation, result saving |
| dataset loader | `datasets/data_process.py` | expects preprocessed files named by `n_size`, e.g. `gsm8k_test_n300.csv` |
| topology construction | `experiments/run_experiment.py::get_kwargs` | `Chain`, `FullConnected`, `Random` DAG masks |
| graph execution | `src/graph/graph.py::arun` | builds spatial edges, executes nodes, then decision node |
| neighbor summary | `src/graph/graph.py::get_neighbor_summary_with_ism` | collects hop-neighbor outputs when `use_neighbor_summary` is true |
| message merging | `src/graph/graph.py::merge_multiple_messages` | upstream hard-codes Ollama `gemma2:9b`; local forced-merge smoke routes this through `VLLMChat` |
| agent prompts | `src/prompt/*_prompt_set.py` | task-specific roles, constraints, decision few-shot |
| LLM registry | `src/llm/llm_registry.py` | upstream routes `qwen` names to Ollama |
| evaluation | `experiments/common.py::evaluate_batch` | postprocesses final decision output and writes result JSON |

## Known Caveats

- The completed A800_2 runs are smoke/topology and forced-merge checks, not paper-scale reproduction.
- The 5-sample topology matrix used `neighbor_hops=1`; it did not exercise full multi-order hop depth.
- A separate 5-sample diagnostic run used `neighbor_hops=2`, 5 agents, and `ism_r=0` to force structural merge. That run recorded nonzero compressed-token counters.
- The embedding fallback is deterministic but not semantically equivalent to `all-MiniLM-L6-v2`.
- Upstream has hidden environment assumptions: local Ollama service, local sentence-transformer cache, and a non-standard API gateway option.

## Next Check

Apply `a8002-comm-trace-events.patch` on A800_2, run a tiny forced-merge check with `MOC_COMM_TRACE_JSONL` set, and extract MOC with `--comm-events-jsonl` before scaling the hop-depth comparison.
