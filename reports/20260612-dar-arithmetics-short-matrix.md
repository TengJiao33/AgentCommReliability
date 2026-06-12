# DAR Arithmetics Short Matrix

## Short Answer

On a 100-sample arithmetics short run with Qwen2.5-7B-Instruct, Basic MAD ended at `0.98`, Top-K uncertainty `0.5` ended at `0.94`, and DAR `filter_critical` ended at `0.99`.

This is Level 3 short-subset evidence for one generated arithmetic setting.

## Scope

- Paper / method: DAR, Diversity-Aware Retention
- Model: `qwen2.5-7b`, local A800_2 path `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Dataset: `arithmetics`
- Samples: `100`
- Seed: `42`
- Agents: `3`
- Debate rounds: `1`

## Sources

| Source | Type | Path |
| --- | --- | --- |
| DAR paper card | paper card | `papers/cards/dar.md` |
| DAR baseline note | baseline note | `baselines/DAR/reproduction.md` |
| smoke run | run record | `experiments/20260612-a8002-dar-qwen25-7b-arithmetics-smoke/` |
| short matrix | run record | `experiments/20260612-a8002-dar-qwen25-7b-arithmetics-short-matrix/` |

## Results

| Method | Round 0 Acc. | Round 1 Acc. | Remote Output |
| --- | ---: | ---: | --- |
| Basic MAD | 0.99 | 0.98 | `/data/xuhaoming/yfy/research_workspace/results/dar-short-basic-qwen25-7b-arith100-20260612_184301/out` |
| Top-K uncertainty `0.5` | 0.97 | 0.94 | `/data/xuhaoming/yfy/research_workspace/results/dar-short-topk05-qwen25-7b-arith100-20260612_184704/out` |
| DAR `filter_critical` | 0.99 | 0.99 | `/data/xuhaoming/yfy/research_workspace/results/dar-short-filtercritical-qwen25-7b-arith100-20260612_185017/out` |

DAR retained-ID counts from `token_logs.jsonl`:

| Retained IDs | Samples |
| ---: | ---: |
| 1 | 40 |
| 2 | 47 |
| 3 | 13 |

## Observations

- The 1.5B non-Instruct local model completed a smoke run but generated invalid repeated text; it is not used for the short matrix.
- Qwen2.5-7B-Instruct needed an arithmetic parser compatibility patch because some outputs escaped final-answer braces.
- Top-K uncertainty reduced the number of round-0 responses carried forward and had lower accuracy in this setting.
- `filter_critical` retained fewer than all three global agent IDs for 87/100 samples.

## Caveats

- The task is generated arithmetic, not GSM8K.
- The result uses one seed and one model.
- Only the first 10 histories are saved for non-debug runs.
- Total token accounting across all generation calls has not been normalized across methods.

## Next Small Check

Run a trace comparison on saved histories first. If the same instrumentation is adequate, run the same three-method matrix on GSM8K with `data_size=100`.
