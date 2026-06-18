# DAR GSM8K Short Matrix

## Short Answer

On a 100-sample GSM8K short run with Qwen2.5-7B-Instruct, Basic MAD ended at `0.95`, Top-K uncertainty `0.5` ended at `0.94`, and DAR `filter_critical` ended at `0.93`.

This differs from the generated-arithmetic short matrix, where `filter_critical` ended highest. The result is Level 3 short-subset evidence for one GSM8K setting.

## Scope

- Paper / method: DAR, Diversity-Aware Retention
- Model: `qwen2.5-7b`, local A800_2 path `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Dataset: GSM8K via project-local MAD-MM processed JSONL fallback
- Samples: `100`
- Seed: `42`
- Agents: `3`
- Debate rounds: `1`

## Sources

| Source | Type | Path |
| --- | --- | --- |
| DAR baseline note | baseline note | `baselines/DAR/reproduction.md` |
| GSM8K run record | run record | `experiments/_archive/20260616-pruned/20260612-a8002-dar-qwen25-7b-gsm8k-short-matrix/` |
| GSM8K summary | generated summary | `experiments/_archive/20260616-pruned/20260612-a8002-dar-qwen25-7b-gsm8k-short-matrix/summary.json` |
| Launcher | script | `scripts/run_dar_gsm8k_short_matrix_a8002.sh` |

## Results

| Method | Round 0 Acc. | Round 1 Acc. | Remote Output |
| --- | ---: | ---: | --- |
| Basic MAD | 0.95 | 0.95 | `/data/xuhaoming/yfy/research_workspace/results/dar-short-basic-qwen25-7b-gsm8k100-20260612_193240/out` |
| Top-K uncertainty `0.5` | 0.95 | 0.94 | `/data/xuhaoming/yfy/research_workspace/results/dar-short-topk05-qwen25-7b-gsm8k100-20260612_193240/out` |
| DAR `filter_critical` | 0.95 | 0.93 | `/data/xuhaoming/yfy/research_workspace/results/dar-short-filtercritical-qwen25-7b-gsm8k100-20260612_193240/out` |

DAR retained-ID counts from `token_logs.jsonl`:

| Retained IDs | Samples |
| ---: | ---: |
| 1 | 64 |
| 2 | 27 |
| 3 | 9 |

Filter-only token log for `filter_critical`:

| Input | Output | Total |
| ---: | ---: | ---: |
| 105,514 | 8,143 | 113,657 |

## Observations

- Basic MAD did not improve from round 0 to round 1 on this subset.
- Top-K uncertainty and `filter_critical` both reduced final accuracy relative to Basic MAD.
- `filter_critical` retained one agent ID for most samples, which makes it an aggressive communication filter in this setup.
- In the saved first 10 histories, one `filter_critical` case flipped from correct to wrong: saved index `5`, answer `5`, round 0 final answers `[5.0, 5.0, ""]`, round 1 final answers `["", "", 3.0]`.

## Caveats

- The run uses one seed and one model.
- GSM8K was loaded through an offline JSONL fallback because A800_2 could not reach Hugging Face.
- Non-debug matrix histories include only the first 10 samples.
- Token accounting is only extracted for the filter step, not all generation calls across methods.

## Next Small Check

Extract all flip cases from full logs if possible, or rerun `filter_critical` with full debug logging on a smaller targeted subset.
