# 20260614-1055-a8002-pact-qwen25-7b-hotpot5

## What We Tried

Ran the PACT split-evidence HotpotQA path end to end on A800_2 with Qwen2.5-7B-Instruct, using 5 samples as a setup smoke before scaling.

## Scope

- Method: PACT
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Dataset: HotpotQA dev-distractor, first 5 shuffled-by-loader samples
- Seed: 42
- Samples: 5
- Comparison target, if any: setup viability only

## Resource Notes

- Machine: A800_2
- GPU IDs: 1
- Timeout: 30m
- Expected duration: under 10 minutes including model load
- Started by: Codex

## Code

- Upstream repo: https://github.com/iNLP-Lab/PACT
- Commit: `91acf820f8a69fc7c181120b3120444a98823230`
- Local changes: none on the remote source

## Environment

- Env path: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- Python: env Python 3.10
- vLLM: `dev` with missing `vllm._version` warning
- PyTorch: `2.4.0+cu121`
- Transformers: `4.46.2`

## Data

- Data path: `/data/xuhaoming/yfy/research_workspace/baselines/PACT/data/hotpot_dev_distractor_v1.json`
- Split: HotpotQA dev-distractor
- Sampling: upstream loader order after deterministic internal context shuffle, first 5 items

## Command

```bash
bash /data/xuhaoming/yfy/research_workspace/scripts/run_pact_hotpot_smoke_a8002.sh
```

## Remote Artifacts

- Main log: `/data/xuhaoming/yfy/research_workspace/results/pact-qwen25-7b-hotpot5-20260614_105542/run.log`
- Result JSON: `/data/xuhaoming/yfy/research_workspace/results/pact-qwen25-7b-hotpot5-20260614_105542/pact_qwen25_7b_hotpot5.jsonl`
- Local copies: `experiments/20260614-1055-a8002-pact-qwen25-7b-hotpot5/`

## What Happened

- Status: completed, `RC=0`
- Exact match: `0.20` (`1/5`)
- Average F1: `0.344`
- Average communication tokens: `294.6`
- Average total tokens: `4129.0`
- Evaluation time: `18.70s`
- Time per sample: `3.7408s`

## Diagnostics

- All 20 agent turns contained `Action Required`, `Environment State`, and `Action Result`.
- All 5 final turns contained `Final Answer`.
- No `<think>` spans were emitted, so this smoke did not exercise hidden-reasoning stripping.
- Three wrong-EM cases contained the normalized gold answer as a substring of the prediction, which points to final-answer formatting/extraction pressure rather than only evidence failure.

## Caveats

- This is a smoke run only.
- The model differs from the paper's Qwen3-14B setting.
- The sample size is too small for method claims.

## Loose Threads

- See the 50-sample Qwen2.5-14B run for a more useful first diagnostic.
