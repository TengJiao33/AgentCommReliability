# Server Resource Inventory

This is the single structured ledger for remote resources used by this project.

Update this file whenever we add or remove a large environment, model, benchmark, cache, or result directory. The goal is to keep project-owned storage bounded and make shared resources visible without confusing them with our own footprint.

## Snapshot

| Field | Value |
| --- | --- |
| Last checked | `2026-06-13 13:52 CST` |
| Machine | `A800_2` |
| Hostname | `10-116-90-20` |
| Project root | `/data/xuhaoming/yfy/research_workspace` |
| Shared model root | `/mnt/quarkfs/share_model` |
| Active project GPU jobs | none observed after MOC smoke; temporary vLLM on port `8021` was stopped |

## Disk Summary

| Mount | Size | Used | Available | Use | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| `/data` | `3.5T` | `1.7T` | `1.7T` | `51%` | project workspace lives here |
| `/mnt/quarkfs` | `10T` | `5.7T` | `4.4T` | `57%` | shared model/data filesystem |

Current project-owned workspace footprint:

| Path | Size | Ownership | Notes |
| --- | ---: | --- | --- |
| `/data/xuhaoming/yfy/research_workspace` | `11G` | project-owned | total tracked workspace footprint on A800_2 |
| `envs/` | `7.1G` | project-owned | one reused env: `mad-mm-vllm063` |
| `pip_cache/` | `3.2G` | project-owned/cache | largest cleanup candidate if storage pressure appears |
| `baselines/` | `75M` | project-owned | code archives/checkouts only, no large model weights |
| `results/` | `8.8M` | project-owned | MAD-MM, DAR, MOC outputs so far |
| `logs/` | `1.1M` | project-owned | small |
| `experiments/` | `216K` | project-owned | run notes/manifests |
| `hf_home/` | `20K` | project-owned/cache | effectively empty |
| `modelscope_cache/` | `8.0K` | project-owned/cache | effectively empty |
| `torch_home/` | `4.0K` | project-owned/cache | effectively empty |
| `scripts/` | `40K` | project-owned | launchers |
| `data/` | `4.0K` | project-owned | empty placeholder |

Largest project subpaths:

| Path | Size | Notes |
| --- | ---: | --- |
| `envs/mad-mm-vllm063` | `7.1G` | shared project env reused by MAD-MM, DAR, and MOC smoke |
| `pip_cache` | `3.2G` | removable cache if needed |
| `baselines/MAD-MM` | `36M` | embedded source and processed data |
| `baselines/DAR` | `3.8M` | source plus patches |
| `baselines/MOC` | `1.9M` | source plus small preprocessed data |
| `results/mad-mm-short-subset` | `6.5M` | largest result directory |
| `results/mad-mm-standard-main` | `1.2M` | early stopped standard run |
| `results/dar-debug-filtercritical-qwen25-7b-gsm8k100-20260612_195526` | `680K` | debug trace output |

## GPU Snapshot

As of the snapshot, only GPU 0 has non-project resident memory use. GPUs 1-7 were free after the MOC run.

| GPU | Model | Used | Free | Util | Notes |
| ---: | --- | ---: | ---: | ---: | --- |
| 0 | NVIDIA A800-SXM4-80GB | `6087 MiB` | `75066 MiB` | `0%` | existing database deploy processes; not ours |
| 1 | NVIDIA A800-SXM4-80GB | `4 MiB` | `81149 MiB` | `0%` | free after MOC vLLM stopped |
| 2 | NVIDIA A800-SXM4-80GB | `4 MiB` | `81149 MiB` | `0%` | free |
| 3 | NVIDIA A800-SXM4-80GB | `4 MiB` | `81149 MiB` | `0%` | free |
| 4 | NVIDIA A800-SXM4-80GB | `4 MiB` | `81149 MiB` | `0%` | free |
| 5 | NVIDIA A800-SXM4-80GB | `4 MiB` | `81149 MiB` | `0%` | free |
| 6 | NVIDIA A800-SXM4-80GB | `4 MiB` | `81149 MiB` | `0%` | free |
| 7 | NVIDIA A800-SXM4-80GB | `4 MiB` | `81149 MiB` | `0%` | free |

Observed non-project long-running services:

| Port / Process | Model | Ownership | Notes |
| --- | --- | --- | --- |
| `8014` swift rollout | `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct` | pre-existing / not ours | do not kill |
| `8012` swift rollout | `/mnt/quarkfs/share_model/Qwen3.5-9B` | pre-existing / not ours | do not kill |
| GPU 0 database deploy PIDs | unknown app | pre-existing / not ours | about `6G` total GPU memory |

## Model Inventory

Shared model root: `/mnt/quarkfs/share_model`.

Most models below are shared server resources. They should be recorded as available, but not counted as project-owned storage unless noted.

| Model / Directory | Size | Ownership Status | Project Use |
| --- | ---: | --- | --- |
| `Qwen2.5-1.5B` | `2.9G` | shared existing | DAR invalid non-Instruct smoke only |
| `Qwen2.5-7B-Instruct` | `15G` | shared existing | DAR and MOC smoke/main short runs |
| `Qwen2.5-14B-Instruct` | `28G` | shared existing | MAD-MM short subset |
| `Qwen2.5-32B-Instruct` | `78G` | project-touched shared model | found incomplete during MAD-MM setup, completed through ModelScope; record as project-touched |
| `Qwen2.5-72B-Instruct` | `136G` | shared existing | available, not used for completed short runs |
| `Qwen3.5-9B` | `19G` | shared existing | available; also used by pre-existing service on port `8012` |
| `Qwen3.5-27B` | `52G` | shared existing | available |
| `Qwen3-32B-AWQ` | `19G` | shared existing | available |
| `Qwen3-Coder-30B-A3B-Instruct` | `57G` | shared existing | available |
| `BGE-large-en-v1.5` | `3.8G` | shared existing | available |
| `bge-reranker-large` | `2.2G` | shared existing | available |
| `OLMo` | `31G` | shared existing | available |
| `OLMo_data` | `3.5T` | shared existing | not project-owned |
| `Ptyhia` | `455G` | shared existing | available |
| `Ptyhia_data` | `561G` | shared existing | not project-owned |
| `zhenqian_data` | size unavailable | shared existing / permission unknown | not project-owned |

Model/cache rule:

- Prefer `/mnt/quarkfs/share_model` models when available.
- Do not duplicate shared models into `/data/xuhaoming/yfy/research_workspace`.
- Any future project-owned model download over `1G` must be added to this table with ownership status.
- If we modify or complete a shared model directory, mark it `project-touched shared model`.

## Benchmark Inventory

These are local benchmark/data files already present on A800_2 and useful for offline reproduction. Sizes are small relative to models.

### MAD-MM Processed Benchmarks

Root: `/data/xuhaoming/yfy/research_workspace/baselines/MAD-MM/processed_data`

| Dataset | File | Samples | Size | Notes |
| --- | --- | ---: | ---: | --- |
| AIME 2024 | `aime24/aime24_test.jsonl` | `30` | `144K` | local processed JSONL |
| AIME 2025 | `aime25/aime25_test.jsonl` | `30` | `20K` | local processed JSONL |
| GSM8K | `gsm8k/gsm8k_test.jsonl` | `1,319` | `744K` | used as DAR offline fallback |
| MATH | `math/math_test.jsonl` | `5,000` | `4.0M` | local processed JSONL |
| MMLU-Pro | `mmlu_pro/mmlu_pro_test.jsonl` | `12,032` | `9.2M` | local processed JSONL |

### MOC Preprocessed Benchmarks

Root: `/data/xuhaoming/yfy/research_workspace/baselines/MOC/datasets/test`

| Dataset | File | Samples | Size | Notes |
| --- | --- | ---: | ---: | --- |
| AQuA | `aqua_test_n254.jsonl` | `254` | `128K` | upstream MOC test file |
| GSM8K | `gsm8k_test_n300.csv` | `300` | `160K` | upstream MOC test file |
| GSM8K smoke | `gsm8k_test_n1.csv` | `1` | `<4K` | project-created smoke subset |
| GSM8K smoke | `gsm8k_test_n5.csv` | `5` | `<4K` | project-created topology-smoke subset |
| HumanEval | `humaneval_test_n164.jsonl` | `164` | `208K` | upstream MOC test file |
| MMLU | `mmlu_test_n5.csv` | `285` | `108K` | upstream MOC test file |
| MMLU-Pro | `mmlu_pro_test_n20.csv` | `280` | `200K` | upstream MOC test file |
| SVAMP | `svamp_test_n300.json` | `300` | `160K` | upstream MOC test file |

Benchmark rule:

- Prefer reusing these local files when Hugging Face access is unreliable.
- Any new benchmark copy over `100M` should be added here before or immediately after creation.
- Smoke subsets are allowed but should remain tiny and named clearly.

## Project-Owned Remote Artifacts

Completed run families currently stored under `/data/xuhaoming/yfy/research_workspace/results`:

| Family | Approx. Size | Notes |
| --- | ---: | --- |
| MAD-MM short subset | `6.5M` | largest result family |
| MAD-MM standard main early stop | `1.2M` | early stopped; not a full benchmark run |
| DAR smoke/short/debug runs | `<1M` each | many small directories |
| MOC smoke results | stored under MOC repo `result/gsm8k`; tiny | should be copied into project results only if they grow |

Source archives under `baselines/`:

| Artifact | Size | Keep? | Notes |
| --- | ---: | --- | --- |
| `mad-mm-a8002.tar.gz` | `22M` | maybe | transfer archive; not urgent |
| `mad-mm-f02069a.bundle` | `11M` | maybe | source transfer bundle |
| `moc-repro-src.tar.gz` | `648K` | optional | superseded by clean archive |
| `moc-repro-src-clean.tar.gz` | `312K` | keep | clean source archive used for remote MOC |
| `moc-repro-src.bundle` | `324K` | optional | failed shallow bundle path; tiny |

## Storage Risk Assessment

Current risk is low.

- Project workspace is `11G`, which is small relative to `/data` free space (`1.7T`).
- The only meaningful project-owned growth is the Python env plus pip cache.
- Results, logs, and local benchmark files are tiny.
- The shared model filesystem is large, but most of it is pre-existing shared infrastructure.

Watch items:

| Item | Current | Risk | Action |
| --- | ---: | --- | --- |
| `pip_cache/` | `3.2G` | medium if many installs continue | can prune after env stabilizes |
| `envs/` | `7.1G` | medium if we create many envs | reuse env when compatible; record each new env |
| shared `Qwen2.5-32B-Instruct` | `78G` | ownership ambiguity | record as project-touched; avoid more shared-model modifications without note |
| raw traces | currently tiny | can grow quickly | record any run expected to exceed `1G` before launch |

Soft caps:

- Keep `/data/xuhaoming/yfy/research_workspace` under `50G` unless explicitly approved.
- Keep single-run outputs under `5G` unless the run is intentionally trace-heavy.
- Do not download or duplicate model weights into the project workspace.

## Update Checklist

Update this document when any of the following happens:

- a new model is downloaded, completed, or modified;
- a new benchmark dataset is copied or generated;
- a new env is created;
- any run writes more than `1G`;
- caches grow materially;
- a cleanup removes meaningful artifacts;
- a long-running service is started and left running.

## Refresh Commands

Run from local PowerShell:

```powershell
ssh A800_2 'hostname; date -Is; df -h /data /mnt/quarkfs; nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits'
```

Workspace sizes:

```powershell
ssh A800_2 'WORK=/data/xuhaoming/yfy/research_workspace; du -sh $WORK; du -sh $WORK/* 2>/dev/null | sort -h'
```

Shared model sizes:

```powershell
ssh A800_2 'du -sh /mnt/quarkfs/share_model/* 2>/dev/null | sort -h'
```

Benchmark sample counts, using parsers rather than `wc -l` for CSV:

```powershell
$code = @'
import json
from pathlib import Path
import pandas as pd

roots = [
    Path("/data/xuhaoming/yfy/research_workspace/baselines/MAD-MM/processed_data"),
    Path("/data/xuhaoming/yfy/research_workspace/baselines/MOC/datasets/test"),
]
for root in roots:
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix not in {".jsonl", ".json", ".csv"}:
            continue
        if p.suffix == ".csv":
            n = len(pd.read_csv(p))
        elif p.suffix == ".jsonl":
            n = sum(1 for _ in p.open("rb"))
        else:
            n = len(json.loads(p.read_text()))
        print(f"{p}\t{p.stat().st_size}\t{n}")
'@
$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($code))
ssh A800_2 "echo $b64 | base64 -d | /data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python"
```

