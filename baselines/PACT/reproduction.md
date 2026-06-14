# PACT Reproduction Note

## Short Answer

PACT now runs end to end on A800_2. A 5-sample Qwen2.5-7B setup smoke completed, followed by a 50-sample Qwen2.5-14B HotpotQA quick-demo-scale run. The 50-sample run scored `17/50` exact match with average F1 `0.508`, and all required action-state fields appeared in all 200 agent turns.

## Scope

- method: PACT, Protocolized Action-state Communication and Transmission
- paper: https://arxiv.org/abs/2606.05304
- repo: https://github.com/iNLP-Lab/PACT
- commit: `91acf820f8a69fc7c181120b3120444a98823230`
- local path: `baselines/PACT/upstream`
- target setting: two-agent split-evidence HotpotQA
- evidence level: Level 3 short-subset run with concrete metrics and traces

## Environment

- machine: A800_2
- env path: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- model paths:
  - `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
  - `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- paper model: `Qwen/Qwen3-14B`
- data: `data/hotpot_dev_distractor_v1.json`

## Commands

Local syntax check:

```bash
cd baselines/PACT/upstream
python -m py_compile run.py methods/pact.py data.py models.py prompts.py utils.py
```

5-sample A800_2 smoke:

```bash
bash scripts/run_pact_hotpot_smoke_a8002.sh
```

50-sample Qwen2.5-14B run:

```bash
PACT_MODEL=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
PACT_MAX_SAMPLES=50 \
PACT_TIMEOUT=60m \
PACT_RUN_ID=pact-qwen25-14b-hotpot50-20260614_1100 \
PACT_OUT_NAME=pact_qwen25_14b_hotpot50.jsonl \
bash /data/xuhaoming/yfy/research_workspace/scripts/run_pact_hotpot_smoke_a8002.sh
```

## Outputs

- 5-sample local record: `experiments/20260614-1055-a8002-pact-qwen25-7b-hotpot5/`
- 50-sample local record: `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/`
- report: `reports/20260614-pact-hotpot-smoke.md`
- trace: upstream JSONL includes per-turn agent prompts, input token IDs/tokens, raw outputs, and token counts

## What Happened

| Method | Model | Task | Seed | Samples | EM | F1 | Avg comm tokens | Avg total tokens | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| PACT | Qwen2.5-7B-Instruct | HotpotQA split-evidence | 42 | 5 | 0.20 | 0.344 | 294.6 | 4129.0 | complete |
| PACT | Qwen2.5-14B-Instruct | HotpotQA split-evidence | 42 | 50 | 0.34 | 0.508 | 339.3 | 4746.8 | complete |

## Deviations From Upstream

- Runs use Qwen2.5-7B/14B because Qwen3-14B was not found on the shared model mount.
- Runs use `generate_bs=1` and `max_new_tokens=1024` to reduce first-run memory risk.
- The 50-sample run matches the upstream quick-demo sample count but not the exact model.

## Failures And Fixes

| Issue | Evidence | Fix | Method Behavior Changed? |
| --- | --- | --- | --- |
| Official CMU HotpotQA download hung on A800_2 and created a 0-byte file. | remote `wget` process stayed active while file size remained 0 | stopped the stalled download, downloaded the same file locally from Hugging Face, validated 7,405 JSON items, and copied it to A800_2 | no |
| A800_2 could not connect to Hugging Face directly. | remote `wget` to Hugging Face timed out during TCP connection | local download plus `scp` transfer | no |

## Diagnostics

- 50-sample format compliance:
  - `Action Required`: 200/200 turns.
  - `Environment State`: 200/200 turns.
  - `Action Result`: 200/200 turns.
  - `Final Answer`: 50/50 final turns.
  - `<think>` spans: 0/200 turns.
- Wrong-EM answer-surface signals:
  - 7 yes/no wrong-EM cases began with the correct yes/no answer but added a sentence.
  - 9 non-yes/no wrong-EM cases began with the normalized gold answer but added extra words.
  - These are diagnostic flags, not alternate official scores.

## Caveats

- The 50-sample run is a useful setup and trace diagnostic, not a paper-scale reproduction.
- Since Qwen2.5-14B is not Qwen3-14B, do not compare the score directly to the paper.
- The model did not emit `<think>` spans, so this run did not exercise private-reasoning stripping.

## Loose Threads

- Add a PACT trace extractor for the unified communication schema.
- Run a postprocessing-only final-answer audit before scaling.
- If closer reproduction matters, locate Qwen3-14B or run a larger Qwen2.5-14B slice.
