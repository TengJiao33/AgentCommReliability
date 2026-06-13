# MOC: Multi-Order Communication in LLM-based Multi-Agent Systems

## Link

- paper: https://arxiv.org/abs/2606.02359
- code: https://github.com/yao-guan/MOC
- local pdf: not downloaded yet

## One-Sentence Claim

MOC claims that multi-hop evidence streams plus structural message consolidation improve LLM multi-agent performance while reducing communication cost.

## Problem

Most LLM multi-agent communication schemes concatenate first-order neighbor responses. This can miss multi-hop dependencies and can dilute useful evidence when message volume grows.

## Method

MOC builds a structured multi-order evidence stream from graph neighbors and uses an iterative semantic merging procedure to consolidate messages under a token budget.

## Communication Variables

| Variable | Value / Design | Notes |
| --- | --- | --- |
| agents | task-specific role agents | e.g. GSM8K cycles through math solver, analyst, programmer, inspector |
| rounds | configurable `num_rounds` | smoke used `1` |
| topology | `Chain`, `FullConnected`, `Random` | masks generated in `get_kwargs` |
| message content | previous agent outputs | injected into downstream prompts |
| memory/context | spatial and temporal predecessors | temporal edges activate after round 0 |
| routing | fixed DAG masks or random DAG | no training in smoke |
| confidence/evidence | semantic similarity over embeddings | smoke used hash embeddings |
| judge/verifier | final decision agent | `FinalRefer` for GSM8K |
| stopping rule | fixed batches over dataset | no early stop in `run_experiment.py` |

## Baselines

The paper compares communication schemes/topologies across several tasks. Our local work has only reproduced a tiny topology smoke and has not checked paper baselines yet.

## Datasets / Tasks

Upstream includes preprocessed files for MMLU, MMLU-Pro, AQuA, GSM8K, SVAMP, and HumanEval.

## Code And Reproducibility

- repo: https://github.com/yao-guan/MOC
- commit inspected: `9c67c92507570704a7df73e452552a3f49e83897`
- license: not observed
- install difficulty: moderate; hidden Ollama/API/embedding assumptions
- smallest runnable command: see `baselines/MOC/reproduction.md`
- expected resource: one A800 is enough for Qwen2.5-7B smoke

## Implementation Details Worth Inspecting

- prompt templates: `src/prompt/*_prompt_set.py`
- message construction: `src/agents/*`
- filtering or merging: `Graph.iterative_semantic_merging_with_clustering`
- judge or verifier path: `FinalRefer`
- evaluation script: `experiments/common.py`
- hidden defaults: `use_neighbor_summary` defaults true; `merge_multiple_messages` hard-codes Ollama `gemma2:9b`

## Possible Ablations

- `neighbor_hops=1` vs `2`
- no summary vs ISM summary
- deterministic hash embeddings vs real `all-MiniLM-L6-v2`
- same topology with and without forced merge

## Caveats

- Our current run is smoke evidence only.
- The structural merge branch has not been reproduced locally yet.

## Project Fit

| Question | Answer |
| --- | --- |
| Which project axis does it touch? | communication topology, evidence routing, message compression |
| What would we learn by reproducing it? | whether multi-hop evidence and compression create measurable reliability/cost tradeoffs |
| What is the cheapest useful check? | force one merge on 1-5 GSM8K samples with Qwen2.5-7B |
| Should it be promoted to experiment? | yes, after merge backend adaptation |

## Open Questions

- Does semantic merging preserve minority-correct evidence or wash it out?
- Does multi-hop evidence help only when upstream agents disagree?
- How much of the paper gain is topology, and how much is message compression?

