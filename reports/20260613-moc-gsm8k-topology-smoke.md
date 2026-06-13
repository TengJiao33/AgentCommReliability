# MOC GSM8K Topology Smoke

## Short Answer

MOC now runs end to end on A800_2 with local Qwen2.5-7B-Instruct via vLLM. On a 5-sample GSM8K smoke, `Chain`, `FullConnected`, and `Random` topologies all scored `5/5`.

This is setup evidence, not a scientific result about topology quality.

## Scope

- Paper / method: MOC, Multi-Order Communication
- Model: Qwen2.5-7B-Instruct, `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Dataset: MOC upstream preprocessed GSM8K CSV
- Samples: `5`
- Agents: `3`
- Rounds: `1`
- Neighbor hops: `1`

## Sources

| Source | Type | Path |
| --- | --- | --- |
| Paper | arXiv | https://arxiv.org/abs/2606.02359 |
| Code | GitHub | https://github.com/yao-guan/MOC |
| Baseline note | local | `baselines/MOC/reproduction.md` |
| Run record | local | `experiments/20260613-a8002-moc-qwen25-7b-gsm8k-topology5/` |

## Results

| Mode | Accuracy | Total tokens | Runtime |
| --- | ---: | ---: | ---: |
| Chain | 1.0 | 14,529 | 34.474s |
| FullConnected | 1.0 | 14,042 | 26.863s |
| Random | 1.0 | 13,967 | 26.208s |

One 1-sample preflight also completed:

| Mode | Accuracy | Total tokens | Runtime |
| --- | ---: | ---: | ---: |
| Chain | 1.0 | 2,991 | 9.187s |

## Observations

- The upstream code is runnable with small backend and environment adaptations.
- The source has several hidden assumptions: Ollama for `qwen`/`gemma` names, a custom non-OpenAI API gateway for GPT-style names, and a local sentence-transformer path.
- In this tiny run, topology did not separate accuracy. Token use and runtime were slightly higher for `Chain`.
- The MOC structural merge mechanism was not tested: compressed-token counters stayed at `0`.

## Interpretation

The useful result is not that all topologies got `1.0`; five GSM8K rows are too few. The useful result is that MOC exposes a different control surface from MAD-MM and DAR: topology/hop depth plus explicit neighbor evidence consolidation. That makes it a good next candidate once we adapt the merge backend and run a forced-merge smoke.

## Caveats

- `neighbor_hops=1`; this is not full multi-order evidence propagation.
- Hash embeddings were used in place of the upstream local sentence-transformer.
- The LLM merge branch still hard-codes Ollama in upstream code and was not triggered.
- The run used one model, one seed, and five examples.

## Next Small Check

Patch `merge_multiple_messages` to use the configured `VLLMChat` backend, then run a 1- to 5-sample `neighbor_hops=2` case that forces at least one merge and records compressed-token behavior.

