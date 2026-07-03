# Machine Handbook

> Source: distilled from `D:\develop\RA-Internship-Tasks`.
> Purpose: make machine access, file placement, and resource rules explicit before any experiment is launched.

This document intentionally records only operational facts and rules. It must not contain passwords, private keys, tokens, proxy config contents, or private contact details.

## Machine Summary

| Machine | Role | Status |
| --- | --- | --- |
| Falcon | Original RA server, 3 x A800 80GB observed. Often busy. | Use only when the reverse tunnel works and resources are free. |
| A800_2 | Alternate compute host from Herman, 8 x A800-SXM4-80GB observed. | Preferred for controlled small experiments when available. |

## Local Source Projects

| Local Path | Role |
| --- | --- |
| `D:\develop\RA-Internship-Tasks` | Source of current machine rules, EasyEdit RA worklogs, and command snippets. |
| `D:\develop\ArXiv_Daily_Digest` | Paper radar; use it for paper discovery and mentor brief generation. |
| `D:\develop\AgentCommReliability` | This project; local scaffold plus machine and resource notes. |

## Remote File Placement For This Project

Use a project-specific subdirectory. Do not mix this project into existing EasyEdit task roots without a reason.

### Falcon

Preferred project root:

```bash
/mnt/20t/xuhaoming/yfy/research_workspace
```

Suggested layout:

```text
/mnt/20t/xuhaoming/yfy/research_workspace/
  baselines/
  data/
  envs/
  logs/
  results/
```

Existing RA paths on Falcon:

```text
/mnt/20t/xuhaoming/yfy/EasyEdit
/mnt/20t/xuhaoming/yfy/conda_envs/easyedit-pr670
/mnt/20t/xuhaoming/yfy/conda_envs/easyedit-qwen35
/mnt/20t/xuhaoming/models/Qwen2.5-1.5B
/mnt/20t/xuhaoming/models/Qwen3.5-9B
```

Rules:

- Keep shared model directories read-only.
- Do not put project files under `/home/xhm`.
- Do not modify `/mnt/20t/xuhaoming/CCKS-archive` or `/mnt/20t/xuhaoming`.
- Do not reuse an unrelated dirty checkout.

### A800_2

Preferred project root:

```bash
/data/xuhaoming/yfy/research_workspace
```

Suggested layout:

```text
/data/xuhaoming/yfy/research_workspace/
  baselines/
  data/
  envs/
  logs/
  results/
```

Existing useful paths:

```text
/data/xuhaoming/yfy/EasyEdit
/data/xuhaoming/yfy/conda_envs/easyedit-qwen35
/mnt/quarkfs/share_model
/mnt/quarkfs/share_model/Qwen2.5-1.5B
/mnt/quarkfs/share_model/Qwen3.5-9B
```

Rules:

- Prefer `/data/xuhaoming/yfy/research_workspace` for this project.
- Treat `/mnt/quarkfs/share_model` as read-only.
- Do not overwrite `/data/xuhaoming/EasyEdit`; it was previously observed as old/dirty.
- Use `/data/xuhaoming/yfy` task-local caches and environments, not shared environments.

## Entering Machines

### Falcon Default Route

Configured alias:

```bash
ssh falcon-rev
```

Expected route:

```text
local machine -> aliyun -> 127.0.0.1:2222 on aliyun -> falcon
```

Basic check:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 falcon-rev hostname
```

If it fails with `channel 0: open failed: connect failed: Connection refused`, the jump host may be reachable but the reverse tunnel from Falcon to Aliyun is down.

Diagnostics:

```bash
ssh -G falcon-rev
ssh aliyun "hostname && (ss -ltnp 2>/dev/null || netstat -ltnp 2>/dev/null) | grep ':2222' || true"
ssh -vvv -o BatchMode=yes -o ConnectTimeout=8 falcon-rev hostname
```

Do not change credentials, proxy configs, or server-side SSH keys as a guess. Ask the server owner to restore the tunnel if needed.

### Falcon Temporary Alternate Port

On 2026-06-06, port `48175` was verified to reach Falcon as `xhm` when `2222` was down.

Temporary command:

```bash
ssh -o HostKeyAlias=falcon-rev-48175 -J aliyun -p 48175 xhm@127.0.0.1
```

Status rule:

- Treat `48175` as temporary unless Herman or the server owner confirms it is stable.
- Use it only after the default route fails and the alternate route is checked.

### A800_2

SSH config:

```text
Host A800_2
    HostName 124.128.251.61
    User xuhaoming
    Port 10622
```

Preferred check:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "hostname; whoami; pwd"
```

Direct form if local SSH config is not updated:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -p 10622 xuhaoming@124.128.251.61 "hostname; whoami; pwd"
```

Observed first-check facts from RA docs:

- Host reported `10-116-90-20`.
- 8 x A800-SXM4-80GB.
- `/data` had about `1.5T` free at first check.
- `/mnt/quarkfs` had about `9.5T` free at first check.
- `Qwen2.5-1.5B` and `Qwen3.5-9B` existed under `/mnt/quarkfs/share_model`.

## Preflight Before Any GPU Run

Always run checks before launching a job:

```bash
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
df -h
pgrep -af 'python|torchrun|accelerate|run_' || true
```

For A800_2 through SSH:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits"
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "df -h /data /mnt/quarkfs"
```

Before a project-specific run, record:

- method;
- target machine;
- target GPU;
- expected command;
- timeout;
- output path;
- whether any download or install is needed.

## GPU Rules

- GPU use is permitted, but only with controlled jobs.
- Always set `CUDA_VISIBLE_DEVICES`.
- Use explicit timeouts for long runs.
- Do not kill or disturb other users' processes.
- If a run is interrupted, only clean up the process started for this project.
- Start with small models, small datasets, and small round counts.
- Prefer one GPU for first reproductions.
- Do not launch full matrices until a smoke run passes.

Example single-GPU pattern:

```bash
export CUDA_VISIBLE_DEVICES=1
timeout 30m python path/to/new_runner.py --config path/to/config.yaml
```

## Environment Rules

- Do not install into shared conda environments unless explicitly approved.
- Create task-local envs under:
  - Falcon: `/mnt/20t/xuhaoming/yfy/research_workspace/envs/`
  - A800_2: `/data/xuhaoming/yfy/research_workspace/envs/`
- Use task-local caches:

Falcon:

```bash
export HF_HOME=/mnt/20t/xuhaoming/yfy/research_workspace/hf_home
export TORCH_HOME=/mnt/20t/xuhaoming/yfy/research_workspace/torch_home
export PIP_CACHE_DIR=/mnt/20t/xuhaoming/yfy/research_workspace/pip_cache
```

A800_2:

```bash
export HF_HOME=/data/xuhaoming/yfy/research_workspace/hf_home
export TORCH_HOME=/data/xuhaoming/yfy/research_workspace/torch_home
export PIP_CACHE_DIR=/data/xuhaoming/yfy/research_workspace/pip_cache
```

Prefer local model loading:

```python
local_files_only=True
```

## Network And Downloads

- Check disk before downloading.
- Record every new dataset/model download in the active experiment note.
- Prefer existing local models.
- Do not download large online models unless there is a clear experiment need and resource approval.
- On Falcon, GitHub access may need server-side proxy `http://127.0.0.1:7890`; do not read or copy proxy configuration.

## Git Rules

- Use clean task-specific clones under the project root.
- Check branch and dirty state before editing:

```bash
git status --short --branch
git log --oneline --decorate -3
```

- Stage explicit files only.
- Avoid `git add .`.
- Do not reset, clean, or switch branches inside unrelated repositories.

## Evidence Levels

Use precise wording:

| Evidence | What It Proves | What It Does Not Prove |
| --- | --- | --- |
| import check | package imports | method works |
| smoke run | code path executes | quality or robustness |
| small dataset run | integration path and metrics writing | benchmark-level result |
| ablation with repeated seeds | local trend under controlled setup | general claim |
| full benchmark | stronger empirical claim | theoretical guarantee |

## First Remote Setup Checklist For This Project

Only run this after deciding which machine to use.

```bash
# A800_2 example
ssh A800_2 "mkdir -p /data/xuhaoming/yfy/research_workspace/{baselines,data,envs,logs,results}"
ssh A800_2 "ls -ld /data/xuhaoming/yfy/research_workspace"
```

Then record durable resource facts in:

```text
docs/server_resource_inventory.md
```
