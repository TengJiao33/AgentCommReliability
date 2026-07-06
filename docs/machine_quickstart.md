# 机器快速检查

这是远程工作前的短命令清单。完整机器规则、文件放置、环境、下载和安全边界见 `docs/machine_handbook.md`。

## 远端项目根目录

```text
Falcon: /mnt/20t/xuhaoming/yfy/research_workspace
A800_2: /data/xuhaoming/yfy/research_workspace
```

## A800_2

连通性检查：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "hostname; whoami; pwd"
```

如果本地 SSH 配置不可用，使用直连形式：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -p 10622 xuhaoming@124.128.251.61 "hostname; whoami; pwd"
```

资源检查：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "date -Is; df -h /data /mnt/quarkfs; nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits"
```

项目根目录检查：

```bash
ssh A800_2 "mkdir -p /data/xuhaoming/yfy/research_workspace/{baselines,data,envs,logs,results} && ls -ld /data/xuhaoming/yfy/research_workspace"
```

## Falcon

默认入口：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 falcon-rev hostname
```

默认反向隧道不可用时，先确认 `docs/machine_handbook.md` 中的备用入口规则，再使用：

```bash
ssh -o HostKeyAlias=falcon-rev-48175 -J aliyun -p 48175 xhm@127.0.0.1 "hostname; whoami; pwd"
```

## GPU 任务启动前

先记录最低信息：

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

再按单 GPU 方式启动：

```bash
export CUDA_VISIBLE_DEVICES=<one-visible-gpu>
timeout 30m <python> <script> <args>
```

## 规则入口

- 文件放置、共享目录、禁止事项：见 `docs/machine_handbook.md`。
- 资源台账和模型/数据缓存：见 `docs/server_resource_inventory.md`。
- 实验记录格式：见 `docs/experiment_protocol.md`。
