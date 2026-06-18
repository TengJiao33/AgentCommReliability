# 20260612-a8002-dar-qwen25-7b-gsm8k-short-matrix

## Short Answer

DAR GSM8K smoke and a 100-sample short matrix completed on A800_2 with Qwen2.5-7B-Instruct after adding an offline GSM8K JSONL loader fallback. In the 100-sample matrix, Basic MAD ended at `0.95`, Top-K uncertainty `0.5` ended at `0.94`, and DAR `filter_critical` ended at `0.93`.

Evidence level: Level 3 short-subset evidence.

## Scope

- Method: DAR / Diversity-Aware Retention
- Model: `qwen2.5-7b`, mapped to `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Dataset: GSM8K
- Seed: `42`
- Samples: smoke `2`, matrix `100`
- Agents: `3`
- Debate rounds: `1`
- Comparison target: Basic MAD, Top-K uncertainty `0.5`, DAR `filter_critical`

## Resource Budget

- Machine: A800_2
- GPU IDs: `5`
- Timeout: `20m` per smoke, `45m` per matrix method
- Started by: Codex from local PowerShell through SSH

## Code

- Upstream repo: https://github.com/DA2I2-SLM/DAR
- Commit: `f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0`
- Remote path: `/data/xuhaoming/yfy/research_workspace/baselines/DAR`
- Local changes:
  - `baselines/DAR/patches/a8002-local-qwen-paths.patch`
  - `baselines/DAR/patches/a8002-arithmetic-escaped-brace-parser.patch`
  - `baselines/DAR/patches/a8002-respect-out-dir.patch`
  - `baselines/DAR/patches/a8002-gsm8k-local-jsonl-fallback.patch`

## Environment

- Env path: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- Inference: vLLM through DAR `engine_vllm_batch`
- GPU mode: single visible GPU via `CUDA_VISIBLE_DEVICES=5`

## Data

- Primary upstream loader: `datasets.load_dataset('openai/gsm8k', 'main')`
- A800_2 issue: Hugging Face was unreachable and no `openai/gsm8k` cache entry existed.
- Offline fallback: `/data/xuhaoming/yfy/research_workspace/baselines/MAD-MM/processed_data/gsm8k/gsm8k_test.jsonl`
- Sampling: DAR loader shuffles with `random_state=0` and takes `.head(data_size)` for non-train split.

## Command

Matrix launcher:

```bash
DAR_GPU_ID=5 DAR_TIMEOUT=45m DAR_STAMP=20260612_193240 \
  /data/xuhaoming/yfy/research_workspace/scripts/run_dar_gsm8k_short_matrix_a8002.sh
```

Smoke commands were the same setting with `--data_size 2 --debug`, run once for Basic MAD and once for `filter_critical`.

## Remote Artifacts

Driver log:

- `/data/xuhaoming/yfy/research_workspace/logs/dar-gsm8k-short-matrix-driver-20260612_193240.log`

Smoke logs:

- `/data/xuhaoming/yfy/research_workspace/logs/dar-smoke-basic-qwen25-7b-gsm8k2-20260612_192702.log`
- `/data/xuhaoming/yfy/research_workspace/logs/dar-smoke-filtercritical-qwen25-7b-gsm8k2-20260612_192839.log`

Matrix logs:

- `/data/xuhaoming/yfy/research_workspace/logs/dar-short-basic-qwen25-7b-gsm8k100-20260612_193240.log`
- `/data/xuhaoming/yfy/research_workspace/logs/dar-short-topk05-qwen25-7b-gsm8k100-20260612_193240.log`
- `/data/xuhaoming/yfy/research_workspace/logs/dar-short-filtercritical-qwen25-7b-gsm8k100-20260612_193240.log`

Matrix outputs:

- `/data/xuhaoming/yfy/research_workspace/results/dar-short-basic-qwen25-7b-gsm8k100-20260612_193240/out`
- `/data/xuhaoming/yfy/research_workspace/results/dar-short-topk05-qwen25-7b-gsm8k100-20260612_193240/out`
- `/data/xuhaoming/yfy/research_workspace/results/dar-short-filtercritical-qwen25-7b-gsm8k100-20260612_193240/out`

## Result

Smoke:

| Method | Samples | Round 0 Acc. | Round 1 Acc. | Status |
| --- | ---: | ---: | ---: | --- |
| Basic MAD | 2 | 1.00 | 1.00 | complete |
| DAR `filter_critical` | 2 | 1.00 | 0.50 | complete |

100-sample matrix:

| Method | Round 0 Acc. | Round 1 Acc. | Runtime |
| --- | ---: | ---: | --- |
| Basic MAD | 0.95 | 0.95 | 1m 54s |
| Top-K uncertainty `0.5` | 0.95 | 0.94 | 1m 39s |
| DAR `filter_critical` | 0.95 | 0.93 | 2m 14s |

DAR `filter_critical` retained-ID distribution:

| Retained IDs | Samples |
| ---: | ---: |
| 1 | 64 |
| 2 | 27 |
| 3 | 9 |

Filter-only token log for `filter_critical`:

| Input | Output | Total |
| ---: | ---: | ---: |
| 105,514 | 8,143 | 113,657 |

## Status Timeline

- `2026-06-12 19:27`: Basic GSM8K 2-sample smoke completed.
- `2026-06-12 19:28`: `filter_critical` GSM8K 2-sample smoke completed.
- `2026-06-12 19:32`: 100-sample matrix launched in tmux.
- `2026-06-12 19:38`: 100-sample matrix completed; tmux exited.

## Caveats

- This is a 100-sample short subset, not a full paper reproduction.
- The GSM8K data path uses a project-local MAD-MM processed JSONL fallback because remote Hugging Face access failed.
- Non-debug matrix runs save only the first 10 histories; retained-ID token logs exist for all 100 `filter_critical` samples.
- `result/token_logs.jsonl` and `result/debate_logs.jsonl` are append-only upstream paths, so analysis must filter by `fname`.
- `filter_critical` underperformed Basic MAD in this run; this is a factual reproduction result, not yet a mechanism claim.

## Next Step

- Analyze flips and retained IDs for `filter_critical`, especially cases where round 0 was correct and round 1 became wrong.
