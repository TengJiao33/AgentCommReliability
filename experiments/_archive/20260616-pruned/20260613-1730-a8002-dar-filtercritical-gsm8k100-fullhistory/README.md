# DAR GSM8K100 Full-History Trace

## What We Tried

Reran the DAR GSM8K 100-sample `filter_critical` setting with the retention instrumentation patch and `--save_full_history`, so every sample has retained/dropped agent IDs in the history and unified communication trace.

## Scope

- Method: DAR `filter_critical`
- Model: Qwen2.5-7B-Instruct
- Dataset: GSM8K via the project-local MAD-MM JSONL fallback
- Seed: 42
- Samples: 100
- Agents: 3
- Debate rounds: 1

## Resource Notes

- Machine: A800_2
- GPU: 7
- Timeout: no explicit wrapper after launch; run completed in `0:02:13` after model load
- Started by: Codex
- GPU 7 was released after the run.

## Code

- Upstream repo: https://github.com/DA2I2-SLM/DAR
- Commit: `f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0`
- Required local patches:
  - `baselines/DAR/patches/a8002-local-qwen-paths.patch`
  - `baselines/DAR/patches/a8002-arithmetic-escaped-brace-parser.patch`
  - `baselines/DAR/patches/a8002-respect-out-dir.patch`
  - `baselines/DAR/patches/a8002-gsm8k-local-jsonl-fallback.patch`
  - `baselines/DAR/patches/a8002-filter-retention-history.patch`

## Environment

- Env path: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`

## Command

```bash
cd /data/xuhaoming/yfy/research_workspace/baselines/DAR
CUDA_VISIBLE_DEVICES=7 \
HF_HOME=/data/xuhaoming/yfy/research_workspace/hf_home \
/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python src/main.py \
  --model qwen2.5-7b \
  --num_agents 3 \
  --data gsm8k \
  --data_size 100 \
  --debate_rounds 1 \
  --uncertainty_prompt True \
  --vote_prompt True \
  --m_role filter_critical \
  --save_full_history \
  --out_dir /data/xuhaoming/yfy/research_workspace/results/dar-trace-filtercritical-gsm8k100-fullhistory-20260613_1730/out
```

## Remote Artifacts

| Artifact | Path |
| --- | --- |
| Log | `/data/xuhaoming/yfy/research_workspace/logs/dar-trace-filtercritical-gsm8k100-fullhistory-20260613_1730.log` |
| Full history | `/data/xuhaoming/yfy/research_workspace/results/dar-trace-filtercritical-gsm8k100-fullhistory-20260613_1730/out/history/gsm8k_100__qwen2.5-7b_N=3_R=1_P=True_V=True_K=None_M=filter_critical_S=42.jsonl` |
| Unified trace | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-trace-filtercritical-gsm8k100-fullhistory.comm_trace.jsonl` |

Small local copies:

- `comm_trace_dar.jsonl`
- `comm_trace_dar_v11.jsonl`
- `dar_history_gsm8k100_filtercritical.jsonl`
- `analysis_summary.json`
- `run.log`

## Derived Schema v1.1 Trace

Created locally without rerunning the model:

```bash
python scripts/extract_comm_trace_schema.py dar \
  --history-jsonl experiments/_archive/20260616-pruned/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/dar_history_gsm8k100_filtercritical.jsonl \
  --run-id 20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory-v11 \
  --method filter_critical \
  --task-regime saturated_arithmetic \
  --public-state-surface retained_full_reasoning \
  --communication-policy retained_subset \
  --out experiments/_archive/20260616-pruned/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/comm_trace_dar_v11.jsonl
```

Validation: 100 rows, schema `acr.comm_trace.v1.1`, with one derived `context_events` entry per row from `retention_events`.

## What Happened

| Metric | Value |
| --- | ---: |
| Round 0 accuracy | 0.95 |
| Round 1 accuracy | 0.93 |
| Unified trace rows | 100 |
| Retention events | 100 |
| Filter input tokens | 105,514 |
| Filter output tokens | 8,143 |
| Filter total tokens | 113,657 |

Transition counts:

| Transition | Count |
| --- | ---: |
| stable_right | 92 |
| right_to_wrong | 3 |
| wrong_to_right | 1 |
| stable_wrong | 4 |

Retention size:

| Retained IDs | Samples |
| ---: | ---: |
| 1 | 64 |
| 2 | 27 |
| 3 | 9 |

Correct-message handling:

| Count | Samples |
| --- | ---: |
| Any correct first-round agent dropped | 84 |
| All correct first-round agents dropped | 13 |

Right-to-wrong cases:

| Sample | Gold | Before | After | Retained Correct | Dropped Correct |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 5 | 5 | 3 | 2 | 0 |
| 20 | 7 | 7 | 700 | 0 | 1 |
| 22 | 131250 | 131250 | empty | 0 | 2 |

The single wrong-to-right case is sample `37`: before `1`, after `11`, gold `11`; the filter retained one correct agent and one wrong agent.

## Caveats

- This reruns only the `filter_critical` branch, not the whole Basic/Top-K/DAR matrix.
- It confirms and enriches the existing 100-sample GSM8K result, but still uses one seed and one model.
- Many samples drop at least one correct agent because multiple agents are often correct in round 0; the stronger signal is the three right-to-wrong cases and thirteen samples where all correct agents were dropped.

## Loose Threads

- Inspect whether the three right-to-wrong cases are caused by raw filter prompt behavior, answer parsing, or round-1 persuasion dynamics.
- Compare with a less aggressive retention rule on the same 100 samples.
