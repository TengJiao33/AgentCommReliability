# 20260704-a8002-gsm8k-basic-mad-full

## Question

Can a minimal multi-agent debate baseline be reproduced on a standard full GSM8K test split with common local instruct models?

## Scope

- Task: GSM8K test, full `1319` rows.
- Method: `MAD-3x1`, three agents, one revision round, majority vote.
- Baseline: direct single-agent answer with the same model.
- Models:
  - `/mnt/quarkfs/share_model/Qwen2.5-1.5B-Instruct`
  - `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
  - `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Dataset path: `/data/xuhaoming/yfy/research_workspace/data/benchmarks/gsm8k/test/canonical.jsonl`
- Evidence level: full benchmark reproduction for this local implementation; not a paper claim.

## Machine

- Host: `A800_2`
- GPU: default target `7`
- Work dir: `/data/xuhaoming/yfy/research_workspace`

## Code

- Script: `scripts/run_basic_mad.py`
- Implementation: local minimal MAD runner using vLLM.
- Local modifications: new script and this run note.

## Environment

- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`
- Backend: vLLM

## Command

Run one model per process so GPU memory is released between models.

```bash
WORK=/data/xuhaoming/yfy/research_workspace
RUN_ID=20260704-a8002-gsm8k-basic-mad-full
GPU_ID=7 nohup bash "$WORK/scripts/run_basic_mad_gsm8k_full.sh" \
  > "$WORK/experiments/$RUN_ID/launcher.out.log" \
  2> "$WORK/experiments/$RUN_ID/launcher.err.log" &
```

## Outputs

- Remote run root: `/data/xuhaoming/yfy/research_workspace/experiments/20260704-a8002-gsm8k-basic-mad-full/`
- Per model:
  - `<model-key>/records.jsonl`
  - `<model-key>/summary.json`
  - `<model-key>/summary.md`

## Result

- Status: `COMPLETED`
- Main metric: direct accuracy vs MAD majority accuracy.

| Model | Rows | Direct acc. | MAD acc. | Delta | Tie rate | Parse fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `qwen25-1_5b-instruct` | 1319 | 0.6975 | 0.7157 | +0.0182 | 0.0629 | direct 2, MAD 0 |
| `qwen25-7b-instruct` | 1319 | 0.8999 | 0.9166 | +0.0167 | 0.0068 | direct 0, MAD 0 |
| `qwen25-14b-instruct` | 1319 | 0.9371 | 0.9515 | +0.0144 | 0.0030 | direct 0, MAD 0 |

All three local Qwen2.5 instruct sizes showed a positive MAD majority-vote delta on the full GSM8K test split.

## Cleanup

- Keep: script, run README, summaries, records.
- Delete: failed partial model directories only if they contain no completed summary.
