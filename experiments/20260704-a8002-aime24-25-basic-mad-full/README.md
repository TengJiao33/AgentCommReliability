# 20260704-a8002-aime24-25-basic-mad-full

## Purpose

Run the existing basic MAD runner on harder integer-answer AIME benchmarks after GSM8K appeared too easy for the selected models.

## Scope

- Benchmarks:
  - `aime24/train`, full 30 rows.
  - `aime25/test`, full 30 rows.
- Method: `MAD-3x1`, three agents, one revision round, majority vote.
- Baseline: direct single-agent answer with the same model.
- Models:
  - `/mnt/quarkfs/share_model/Qwen2.5-1.5B-Instruct`
  - `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
  - `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Evidence level: full available AIME24/AIME25 prepared splits for this local implementation; small sample, diagnostic baseline.

## Machine

- Host: `A800_2`
- GPU: target `7`
- Work dir: `/data/xuhaoming/yfy/research_workspace`

## Code

- Script: `scripts/run_basic_mad.py`
- Code changes for this run: none.
- Reason: AIME answers are integer strings, so the existing numeric evaluator is compatible.

## Environment

- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`
- Backend: vLLM

## Command Shape

The run executes each `(benchmark, model)` pair as a separate process so GPU memory is released between models.

```bash
WORK=/data/xuhaoming/yfy/research_workspace
RUN_ID=20260704-a8002-aime24-25-basic-mad-full
GPU_ID=7 nohup bash "$WORK/experiments/$RUN_ID/run_remote.sh" \
  > "$WORK/experiments/$RUN_ID/launcher.out.log" \
  2> "$WORK/experiments/$RUN_ID/launcher.err.log" &
```

## Outputs

- Remote run root: `/data/xuhaoming/yfy/research_workspace/experiments/20260704-a8002-aime24-25-basic-mad-full/`
- Per benchmark/model:
  - `<benchmark>-<model-key>/records.jsonl`
  - `<benchmark>-<model-key>/summary.json`
  - `<benchmark>-<model-key>/summary.md`

## Result

- Status: `COMPLETED`
- Main metric: direct accuracy vs MAD majority accuracy.

### Per Split

| Benchmark | Model | Rows | Direct | MAD | Tie rate | Parse fail |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| AIME24 | `qwen25-1_5b-instruct` | 30 | 1/30 | 1/30 | 11/30 | direct 2, MAD 0 |
| AIME24 | `qwen25-7b-instruct` | 30 | 4/30 | 3/30 | 7/30 | direct 0, MAD 0 |
| AIME24 | `qwen25-14b-instruct` | 30 | 3/30 | 4/30 | 6/30 | direct 0, MAD 0 |
| AIME25 | `qwen25-1_5b-instruct` | 30 | 0/30 | 0/30 | 13/30 | direct 0, MAD 0 |
| AIME25 | `qwen25-7b-instruct` | 30 | 1/30 | 1/30 | 8/30 | direct 1, MAD 0 |
| AIME25 | `qwen25-14b-instruct` | 30 | 3/30 | 3/30 | 3/30 | direct 0, MAD 0 |

### Combined AIME24+AIME25

| Model | Rows | Direct | MAD | Delta |
| --- | ---: | ---: | ---: | ---: |
| `qwen25-1_5b-instruct` | 60 | 1/60 = 0.0167 | 1/60 = 0.0167 | 0 |
| `qwen25-7b-instruct` | 60 | 5/60 = 0.0833 | 4/60 = 0.0667 | -0.0167 |
| `qwen25-14b-instruct` | 60 | 6/60 = 0.1000 | 7/60 = 0.1167 | +0.0167 |

The AIME run gives a much less saturated baseline than GSM8K. Scores are low and per-year deltas are noisy because each split has only 30 rows.
