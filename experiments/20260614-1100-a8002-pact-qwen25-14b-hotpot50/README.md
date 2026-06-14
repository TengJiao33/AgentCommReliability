# 20260614-1100-a8002-pact-qwen25-14b-hotpot50

## What We Tried

Ran the PACT split-evidence HotpotQA path on the upstream quick-demo scale, using local Qwen2.5-14B-Instruct as the closest available 14B model to the paper's Qwen3-14B setting.

## Scope

- Method: PACT
- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Dataset: HotpotQA dev-distractor, first 50 shuffled-by-loader samples
- Seed: 42
- Samples: 50
- Comparison target, if any: upstream quick-demo scale, not paper-scale reproduction

## Resource Notes

- Machine: A800_2
- GPU IDs: 1
- Timeout: 60m
- Expected duration: under 20 minutes including model load
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
- NumPy: `1.26.4`
- tqdm: `4.67.0`

## Data

- Data path: `/data/xuhaoming/yfy/research_workspace/baselines/PACT/data/hotpot_dev_distractor_v1.json`
- Split: HotpotQA dev-distractor
- Size available: 7,405 items
- Sampling: upstream loader order after deterministic internal context shuffle, first 50 items

## Command

```bash
PACT_MODEL=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
PACT_MAX_SAMPLES=50 \
PACT_TIMEOUT=60m \
PACT_RUN_ID=pact-qwen25-14b-hotpot50-20260614_1100 \
PACT_OUT_NAME=pact_qwen25_14b_hotpot50.jsonl \
bash /data/xuhaoming/yfy/research_workspace/scripts/run_pact_hotpot_smoke_a8002.sh
```

## Remote Artifacts

- Main log: `/data/xuhaoming/yfy/research_workspace/results/pact-qwen25-14b-hotpot50-20260614_1100/run.log`
- Result JSON: `/data/xuhaoming/yfy/research_workspace/results/pact-qwen25-14b-hotpot50-20260614_1100/pact_qwen25_14b_hotpot50.jsonl`
- Local copies: `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/`

## What Happened

- Status: completed, `RC=0`
- Exact match: `0.34` (`17/50`)
- Average F1: `0.508`
- Average communication tokens: `339.3`
- Average total tokens: `4746.8`
- Average output tokens per turn: `84.8`
- Evaluation time: `388.94s`
- Time per sample: `7.7788s`

## Diagnostics

- All 200 agent turns contained `Action Required`, `Environment State`, and `Action Result`.
- All 50 final turns contained `Final Answer`.
- No `<think>` spans were emitted, so this run mainly tests concise public action-state messaging, not private-thought stripping.
- Among non-EM predictions, 7 yes/no cases began with the correct `yes` or `no` but failed exact match because the model answered in a full sentence.
- Another 9 non-yes/no cases began with the normalized gold answer but added extra words.
- These are not alternate official scores; they indicate an answer-surface and extraction problem worth testing before interpreting EM as pure reasoning failure.

## Caveats

- This is not an author-style reproduction: model is Qwen2.5-14B, not Qwen3-14B.
- It is a 50-sample quick-demo run, not the full 7,405-item dev set.
- The upstream prompt enforces action-state fields well, but the final answer field is still too verbose for strict HotpotQA EM in many cases.

## Loose Threads

- Run a postprocessing-only audit for final-answer extraction, especially yes/no answers.
- If closer reproduction matters, locate Qwen3-14B or run Qwen2.5-14B on a larger slice.
- Add a unified PACT trace extractor so public evidence fields can be compared against DAR answer-only/full retained surfaces.
