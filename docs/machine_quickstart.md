# Machine Quickstart

Use this as the checklist before remote work. Keep project files under the project-specific remote root.

## Preferred Remote Project Roots

```text
Falcon: /mnt/20t/xuhaoming/yfy/research_workspace
A800_2: /data/xuhaoming/yfy/research_workspace
```

## A800_2 Entry

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "hostname; whoami; pwd"
```

Direct form:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -p 10622 xuhaoming@124.128.251.61 "hostname; whoami; pwd"
```

Check GPUs:

```bash
ssh A800_2 "nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits"
```

Check project root:

```bash
ssh A800_2 "mkdir -p /data/xuhaoming/yfy/research_workspace/{baselines,data,envs,logs,results,scripts} && ls -ld /data/xuhaoming/yfy/research_workspace"
```

## Falcon Entry

Default:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 falcon-rev hostname
```

If default reverse tunnel is down, temporary alternate from 2026-06-06:

```bash
ssh -o HostKeyAlias=falcon-rev-48175 -J aliyun -p 48175 xhm@127.0.0.1 "hostname; whoami; pwd"
```

Use the alternate only after checking that the default route fails.

## Before Launching A GPU Job

Record these in an experiment note:

```text
machine:
gpu:
free memory:
method:
model:
dataset:
command:
timeout:
output path:
```

Then run:

```bash
export CUDA_VISIBLE_DEVICES=<one-visible-gpu>
timeout 30m <python> <script> <args>
```

## Do Not

- Do not put project files under `/home/xhm`.
- Do not modify shared model folders.
- Do not overwrite `/data/xuhaoming/EasyEdit`.
- Do not modify `/mnt/20t/xuhaoming/CCKS-archive` or `/mnt/20t/xuhaoming`.
- Do not install into shared conda envs.
- Do not run jobs without `CUDA_VISIBLE_DEVICES`.
- Do not kill other users' processes.
- Do not record passwords, private keys, tokens, or proxy config contents.

## Environment Rules

- Use task-local envs under `/data/xuhaoming/yfy/research_workspace/envs/`.
- Treat `/mnt/quarkfs/share_model` as read-only.
- Prefer one GPU for first reproductions.
- Use explicit `timeout` wrappers for model jobs.
- Record every new dataset/model download in the active run note.
