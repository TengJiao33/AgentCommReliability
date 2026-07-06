# 机器手册

> 目的：在启动任何实验前，明确机器访问、文件放置和资源使用规则。

快速连通、磁盘、GPU 检查命令见 `docs/machine_quickstart.md`。本文保留完整规则和背景。

## 机器概览

| 机器 | 角色 | 状态 |
| --- | --- | --- |
| Falcon | 原 RA 服务器，观察到 3 张 A800 80GB，常处于繁忙状态。 | 仅在反向隧道可用且资源空闲时使用。 |
| A800_2 | 徐浩铭师兄提供的备用计算主机，观察到 8 张 A800-SXM4-80GB。 | 可用时优先用于受控小实验。 |

### Falcon 放置规则

首选项目根目录：

```bash
/mnt/20t/xuhaoming/yfy/research_workspace
```

规则：

- 共享模型目录保持只读。
- 不要把项目文件放在 `/home/xhm` 下。
- 不要修改 `/mnt/20t/xuhaoming/CCKS-archive` 或 `/mnt/20t/xuhaoming`。
- 不要复用无关的脏 checkout。

### A800_2 放置规则

首选项目根目录：

```bash
/data/xuhaoming/yfy/research_workspace
```

规则：

- 本项目优先使用 `/data/xuhaoming/yfy/research_workspace`。
- 将 `/mnt/quarkfs/share_model` 视为只读目录。
- 不要覆盖 `/data/xuhaoming/EasyEdit`；该目录此前被观察为旧且脏。
- 使用 `/data/xuhaoming/yfy` 下的任务局部缓存和环境，不使用共享环境。

## 进入机器

### Falcon 默认路由

已配置别名：

```bash
ssh falcon-rev
```

预期路由：

```text
local machine -> aliyun -> 127.0.0.1:2222 on aliyun -> falcon
```

基础检查：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 falcon-rev hostname
```

如果失败信息包含 `channel 0: open failed: connect failed: Connection refused`，说明跳板机可能可达，但 Falcon 到 Aliyun 的反向隧道已断开。

诊断命令：

```bash
ssh -G falcon-rev
ssh aliyun "hostname && (ss -ltnp 2>/dev/null || netstat -ltnp 2>/dev/null) | grep ':2222' || true"
ssh -vvv -o BatchMode=yes -o ConnectTimeout=8 falcon-rev hostname
```

不要凭猜测修改凭证、代理配置或服务器端 SSH key。需要时请服务器所有者恢复隧道。

### Falcon 临时备用端口

2026-06-06 曾验证端口 `48175` 可以在 `2222` 不可用时以 `xhm` 身份进入 Falcon。

临时命令：

```bash
ssh -o HostKeyAlias=falcon-rev-48175 -J aliyun -p 48175 xhm@127.0.0.1
```

状态规则：

- 除非 Herman 或服务器所有者确认稳定，否则将 `48175` 视为临时入口。
- 只有在默认路由失败且备用路由检查通过后才使用。

### A800_2 入口

SSH 配置：

```text
Host A800_2
    HostName 124.128.251.61
    User xuhaoming
    Port 10622
```

首选检查：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "hostname; whoami; pwd"
```

如果本地 SSH 配置未更新，使用直连形式：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -p 10622 xuhaoming@124.128.251.61 "hostname; whoami; pwd"
```

## GPU 运行前检查

启动任何任务前都要检查：

```bash
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
df -h
pgrep -af 'python|torchrun|accelerate|run_' || true
```

通过 SSH 检查 A800_2：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits"
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "df -h /data /mnt/quarkfs"
```

项目任务启动前记录：

- 方法；
- 目标机器；
- 目标 GPU；
- 预期命令；
- 超时时间；
- 输出路径；
- 是否需要下载或安装。

## GPU 规则

- 可以使用 GPU，但只能运行受控任务。
- 必须设置 `CUDA_VISIBLE_DEVICES`。
- 长任务必须显式设置超时。
- 不要杀掉或干扰其他用户的进程。
- 如果运行被中断，只清理本项目启动的进程。
- 首次复现优先使用单 GPU。

单 GPU 示例：

```bash
export CUDA_VISIBLE_DEVICES=1
timeout 30m python path/to/new_runner.py --config path/to/config.yaml
```

## 环境规则

- 除非明确获准，不要安装到共享 conda 环境。
- 在任务局部目录创建环境：
  - Falcon：`/mnt/20t/xuhaoming/yfy/research_workspace/envs/`
  - A800_2：`/data/xuhaoming/yfy/research_workspace/envs/`
- 使用任务局部缓存。

Falcon：

```bash
export HF_HOME=/mnt/20t/xuhaoming/yfy/research_workspace/hf_home
export TORCH_HOME=/mnt/20t/xuhaoming/yfy/research_workspace/torch_home
export PIP_CACHE_DIR=/mnt/20t/xuhaoming/yfy/research_workspace/pip_cache
```

A800_2：

```bash
export HF_HOME=/data/xuhaoming/yfy/research_workspace/hf_home
export TORCH_HOME=/data/xuhaoming/yfy/research_workspace/torch_home
export PIP_CACHE_DIR=/data/xuhaoming/yfy/research_workspace/pip_cache
```

优先使用本地模型加载：

```python
local_files_only=True
```

## 网络和下载

- 下载前检查磁盘。
- 每次新增数据集或模型下载，都记录到当前实验说明中。
- 优先使用已有本地模型。
- 没有明确实验需要和资源许可时，不要下载大型在线模型。
- Falcon 上 GitHub 访问可能需要服务器侧代理 `http://127.0.0.1:7890`；不要读取或复制代理配置。

## Git 规则

- 在项目根目录下使用干净的任务专属 clone。
- 编辑前检查分支和脏状态：

```bash
git status --short --branch
git log --oneline --decorate -3
```

- 只 stage 明确文件。
- 避免 `git add .`。
- 不要在无关仓库里 reset、clean 或切换分支。

## 本项目首次远程设置检查清单

只在决定使用哪台机器后运行。

```bash
# A800_2 示例
ssh A800_2 "mkdir -p /data/xuhaoming/yfy/research_workspace/{baselines,data,envs,logs,results}"
ssh A800_2 "ls -ld /data/xuhaoming/yfy/research_workspace"
```

然后把可长期复核的资源事实记录到：

```text
docs/server_resource_inventory.md
```
