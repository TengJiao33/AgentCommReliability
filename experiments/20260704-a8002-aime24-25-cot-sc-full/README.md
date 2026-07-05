# 20260704-a8002-aime24-25-cot-sc-full

## Purpose

Run CoT and CoT-SC baselines on the same harder AIME24/AIME25 full splits used for the basic MAD baseline.

## Scope

- Benchmarks:
  - `aime24/train`, full 30 rows.
  - `aime25/test`, full 30 rows.
- Methods:
  - CoT: one greedy step-by-step sample.
  - CoT-SC: 16 sampled step-by-step outputs, majority vote over parsed numeric answers.
- Models:
  - `/mnt/quarkfs/share_model/Qwen2.5-1.5B-Instruct`
  - `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
  - `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Evidence level: full available AIME24/AIME25 prepared splits for this local implementation; small-sample diagnostic baseline.

## Machine

- Host: `A800_2`
- GPU: target `7`
- Work dir: `/data/xuhaoming/yfy/research_workspace`

## Code

- Script: `scripts/run_cot_sc.py`
- Evaluator: numeric answer parser reused from `scripts/run_basic_mad.py`
- Reason: AIME answers are integer strings, so numeric evaluation is compatible.

## Environment

- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`
- Backend: vLLM

## Command Shape

```bash
WORK=/data/xuhaoming/yfy/research_workspace
RUN_ID=20260704-a8002-aime24-25-cot-sc-full
GPU_ID=7 nohup bash "$WORK/experiments/$RUN_ID/run_remote.sh" \
  > "$WORK/experiments/$RUN_ID/launcher.out.log" \
  2> "$WORK/experiments/$RUN_ID/launcher.err.log" &
```

## Outputs

- Remote run root: `/data/xuhaoming/yfy/research_workspace/experiments/20260704-a8002-aime24-25-cot-sc-full/`
- Per benchmark/model:
  - `<benchmark>-<model-key>/records.jsonl`
  - `<benchmark>-<model-key>/summary.json`
  - `<benchmark>-<model-key>/summary.md`

## Result

- Status: `COMPLETED`
- Main metric: CoT accuracy vs CoT-SC majority accuracy.

### Per Split

| Benchmark | Model | Rows | CoT | CoT-SC | SC tie rate | Parse fail |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| AIME24 | `qwen25-1_5b-instruct` | 30 | 1/30 | 1/30 | 15/30 | CoT 1, SC majority 0 |
| AIME24 | `qwen25-7b-instruct` | 30 | 3/30 | 5/30 | 8/30 | CoT 0, SC majority 0 |
| AIME24 | `qwen25-14b-instruct` | 30 | 3/30 | 4/30 | 4/30 | CoT 0, SC majority 0 |
| AIME25 | `qwen25-1_5b-instruct` | 30 | 0/30 | 0/30 | 16/30 | CoT 2, SC majority 0 |
| AIME25 | `qwen25-7b-instruct` | 30 | 3/30 | 1/30 | 12/30 | CoT 1, SC majority 0 |
| AIME25 | `qwen25-14b-instruct` | 30 | 2/30 | 5/30 | 2/30 | CoT 0, SC majority 0 |

### Combined AIME24+AIME25

| Model | Rows | CoT | CoT-SC | Delta |
| --- | ---: | ---: | ---: | ---: |
| `qwen25-1_5b-instruct` | 60 | 1/60 = 0.0167 | 1/60 = 0.0167 | 0 |
| `qwen25-7b-instruct` | 60 | 6/60 = 0.1000 | 6/60 = 0.1000 | 0 |
| `qwen25-14b-instruct` | 60 | 5/60 = 0.0833 | 9/60 = 0.1500 | +0.0667 |

CoT-SC gives a visible combined gain for the 14B model in this run. It does not consistently help every model or split: 7B improves on AIME24 but drops on AIME25, and 1.5B stays at floor.
