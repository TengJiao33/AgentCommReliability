# Server Resource Inventory

This is the retained operational ledger for remote resources.

The latest detailed snapshot in this file was reset on 2026-07-03 from earlier notes. Treat machine sizes and model availability as last-known facts; refresh them before launching any new job.

## Remote Roots

| Machine | Project Root | Notes |
| --- | --- | --- |
| `A800_2` | `/data/xuhaoming/yfy/research_workspace` | Preferred controlled project root. |
| `Falcon` | `/mnt/20t/xuhaoming/yfy/research_workspace` | Use only when the route works and resources are free. |

## A800_2 Access

SSH alias:

```text
A800_2
```

Direct form:

```text
ssh -p 10622 xuhaoming@124.128.251.61
```

Last-known host identity:

```text
10-116-90-20
```

## A800_2 Project Workspace Cleanup

Last cleanup: `2026-07-03`.

Remote project root:

```text
/data/xuhaoming/yfy/research_workspace
```

The remote project folder was reset to a minimal scaffold. Old experiments, results, logs, scripts, baseline checkouts, reports, data, harness files, temporary files, backups, and transfer archives were removed from that folder.

Preserved reusable runtime/cache directories:

| Path | Last checked size | Reason |
| --- | ---: | --- |
| `envs/` | `7.1G` | reusable project Python environment |
| `pip_cache/` | `3.2G` | reusable package cache |
| `hf_home/` | `20K` | reusable Hugging Face cache root |
| `modelscope_cache/` | `8.0K` | reusable ModelScope cache root |
| `torch_home/` | `4.0K` | reusable Torch cache root |

Current retained scaffold directories:

```text
active/
baselines/
docs/
experiments/
reports/
README.md
```

## Prepared Benchmark Data

Last prepared: `2026-07-03`.

Remote location:

```text
/data/xuhaoming/yfy/research_workspace/data/benchmarks
```

Prepared under the project root only. Hugging Face access from `A800_2` was
unavailable during preparation, so the benchmark JSONL files were generated
locally and transferred into the project folder. The MMLU-Pro source parquet
snapshot was also copied to:

```text
/data/xuhaoming/yfy/research_workspace/data/source_repos/MMLU-Pro
```

| Benchmark | Source | Splits | Rows |
| --- | --- | --- | ---: |
| `mmlu_pro` | `TIGER-Lab/MMLU-Pro` | `test`, `validation` | 12,102 |
| `gsm8k` | `openai/gsm8k`, config `main` | `train`, `test` | 8,792 |
| `math500` | `HuggingFaceH4/MATH-500` | `test` | 500 |
| `aime24` | `HuggingFaceH4/aime_2024` | `train` | 30 |
| `aime25` | `math-ai/aime25` | `test` | 30 |

## Shared Resource Rules

- Keep project files under the project root.
- Treat `/mnt/quarkfs/share_model` as shared and read-only unless explicitly approved.
- Do not duplicate large model weights into the project workspace.
- Do not install into shared conda environments.
- Do not kill other users' processes.
- Record any new model, dataset, environment, cache, or result directory that may be expensive to recreate.

## Last-Known Shared Model Root

```text
/mnt/quarkfs/share_model
```

Known useful model families from earlier inventory:

- `Qwen2.5-*`
- `Qwen3*`
- `BGE-large-en-v1.5`
- `bge-reranker-large`

Refresh availability before use.

## Refresh Commands

```powershell
ssh A800_2 'hostname; date -Is; df -h /data /mnt/quarkfs; nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits'
ssh A800_2 'WORK=/data/xuhaoming/yfy/research_workspace; mkdir -p "$WORK"; du -sh "$WORK"; du -sh "$WORK"/* 2>/dev/null | sort -h'
ssh A800_2 'du -sh /mnt/quarkfs/share_model/* 2>/dev/null | sort -h'
```

## Update Checklist

Update this document when:

- a new model is downloaded, completed, modified, or relied on;
- a new dataset or benchmark copy is created;
- a new environment or large cache is created;
- a run writes more than `1G`;
- a cleanup removes remote artifacts;
- a long-running service is started and left running.
