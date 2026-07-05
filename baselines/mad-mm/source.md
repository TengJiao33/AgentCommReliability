# MAD-M2 Source Note

## Upstream

- paper: Multi-Agent Debate with Memory Masking, arXiv:2603.20215, ICLR 2026.
- repo: https://github.com/HongduanTian/MAD-MM
- commit inspected: f02069a
- license: MIT in upstream repository.
- local inspection path: `.tmp/mad-mm-upstream` (ignored, not committed).

## Why Pick This Up

The method directly extends multi-agent debate by evaluating the previous round's memories before the next debate round. It is close enough to the current MAD and CoT-SC baselines that AIME24/25 can be reused without changing the benchmark boundary.

## Smallest Runnable Path

- model: Qwen2.5-7B-Instruct.
- dataset/task: AIME24 and AIME25 full test sets.
- command: `scripts/run_mad_mm.py` with `--prune-strategy naive|subjective|objective`.
- expected output: `experiments/<run-id>/<benchmark>-<model>-<strategy>/summary.json` and `records.jsonl`.
- expected resource: one A800 GPU, vLLM 0.6.3 environment already prepared.

## Installation Details

- environment: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`.
- core dependencies: vLLM, torch, transformers; no extra dependency is needed for AIME numeric evaluation in this local runner.
- data download: uses prepared `data/benchmarks/aime24/test/canonical.jsonl` and `data/benchmarks/aime25/test/canonical.jsonl`.
- model path: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`.
- known version constraints: upstream pins vLLM 0.6.3 and Transformers 4.46.2.

## Code Map

| Component | File / Function | Details |
| --- | --- | --- |
| prompt templates | upstream `src/prompts.py`; local `scripts/run_mad_mm.py` | CoT, debate, and prune prompts mirror upstream text. |
| agent loop | upstream `src/reasoning_models.py::MultiAgentDebate`; local `main` loop | Default is 3 agents and 2 total debate rounds. |
| communication | `debate_prompt` | All retained previous-round memories are given to every agent. |
| memory/context | `rounds[].memory_mask` in `records.jsonl` | Per-row masks and retained counts are persisted. |
| routing/filtering | `subjective_mask`, `objective_mask`, `naive_mask` | Subjective keeps YES and, unless strict, NOT SURE. Objective follows upstream code behavior by retaining responses above the median sequence score. |
| evaluation | imported numeric evaluator from `run_basic_mad.py` | Suited for GSM8K/AIME numeric answers; MMLU-Pro is not the first reproduction target. |

## Loose Threads

- Add MATH symbolic scoring if we want to reproduce the sampled MATH setting.
- Add multi-seed sampled GSM8K/MATH/MMLU-Pro runs if we want to mirror the full paper table.
