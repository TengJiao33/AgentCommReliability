# 20260612-a8002-dar-qwen25-7b-arithmetics-short-matrix

## Short Answer

A bounded DAR arithmetics matrix completed on A800_2. In this setting, Basic MAD ended at `0.98`, Top-K uncertainty ended at `0.94`, and DAR `filter_critical` ended at `0.99`.

Evidence level: Level 3 short-subset evidence.

## Scope

- Model: `qwen2.5-7b`, mapped to `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Dataset: `arithmetics`
- Samples: `100`
- Seed: `42`
- Agents: `3`
- Debate rounds: `1`
- Machine: A800_2
- GPU: `4`
- Timeout per run: `30m`

## Code

- Upstream repo: https://github.com/DA2I2-SLM/DAR
- Commit: `f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0`
- Remote path: `/data/xuhaoming/yfy/research_workspace/baselines/DAR`
- Prior smoke record: `experiments/_archive/20260616-pruned/20260612-a8002-dar-qwen25-7b-arithmetics-smoke/`

## Local Patches

| Patch | Purpose |
| --- | --- |
| `baselines/DAR/patches/a8002-local-qwen-paths.patch` | use local Qwen model paths |
| `baselines/DAR/patches/a8002-arithmetic-escaped-brace-parser.patch` | parse Qwen escaped final-answer braces |
| `baselines/DAR/patches/a8002-respect-out-dir.patch` | write history and TSV under `--out_dir` |

## Commands

Basic MAD:

```bash
CUDA_VISIBLE_DEVICES=4 timeout 30m \
  /data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python src/main.py \
  --model qwen2.5-7b --num_agents 3 --data arithmetics --data_size 100 --debate_rounds 1 \
  --out_dir /data/xuhaoming/yfy/research_workspace/results/dar-short-basic-qwen25-7b-arith100-20260612_184301/out
```

Top-K uncertainty:

```bash
CUDA_VISIBLE_DEVICES=4 timeout 30m \
  /data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python src/main.py \
  --model qwen2.5-7b --num_agents 3 --data arithmetics --data_size 100 --debate_rounds 1 \
  --top_k_uncertainty 0.5 \
  --out_dir /data/xuhaoming/yfy/research_workspace/results/dar-short-topk05-qwen25-7b-arith100-20260612_184704/out
```

DAR `filter_critical`:

```bash
CUDA_VISIBLE_DEVICES=4 timeout 30m \
  /data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python src/main.py \
  --model qwen2.5-7b --num_agents 3 --data arithmetics --data_size 100 --debate_rounds 1 \
  --uncertainty_prompt True --vote_prompt True --m_role filter_critical \
  --out_dir /data/xuhaoming/yfy/research_workspace/results/dar-short-filtercritical-qwen25-7b-arith100-20260612_185017/out
```

## Result Snapshot

| Method | Round 0 Acc. | Round 1 Acc. | Runtime |
| --- | ---: | ---: | --- |
| Basic MAD | 0.99 | 0.98 | 1m 53s |
| Top-K uncertainty `0.5` | 0.97 | 0.94 | 1m 28s |
| DAR `filter_critical` | 0.99 | 0.99 | 2m 02s |

DAR `filter_critical` retained-ID rows:

| Retained IDs | Samples |
| ---: | ---: |
| 1 | 40 |
| 2 | 47 |
| 3 | 13 |

Filter-only token log for `filter_critical`:

| Input | Output | Total |
| ---: | ---: | ---: |
| 108,978 | 11,305 | 120,283 |

## Remote Artifacts

| Method | Log | Output |
| --- | --- | --- |
| Basic MAD | `/data/xuhaoming/yfy/research_workspace/logs/dar-short-basic-qwen25-7b-arith100-20260612_184301.log` | `/data/xuhaoming/yfy/research_workspace/results/dar-short-basic-qwen25-7b-arith100-20260612_184301/out` |
| Top-K uncertainty | `/data/xuhaoming/yfy/research_workspace/logs/dar-short-topk05-qwen25-7b-arith100-20260612_184704.log` | `/data/xuhaoming/yfy/research_workspace/results/dar-short-topk05-qwen25-7b-arith100-20260612_184704/out` |
| DAR `filter_critical` | `/data/xuhaoming/yfy/research_workspace/logs/dar-short-filtercritical-qwen25-7b-arith100-20260612_185017.log` | `/data/xuhaoming/yfy/research_workspace/results/dar-short-filtercritical-qwen25-7b-arith100-20260612_185017/out` |

## Caveats

- This is a generated arithmetic task, not GSM8K.
- The matrix uses one seed, one model, and one debate round.
- The three methods do not yet have matched total-token accounting; only DAR filter-token totals were extracted from `token_logs.jsonl`.
- Non-debug history stores only the first 10 samples.

## Next Step

Analyze per-sample flips from the saved histories and decide whether to run the same matrix on GSM8K.
