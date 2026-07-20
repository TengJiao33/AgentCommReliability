# 机器手册

> 目的：在启动任何实验前，明确机器访问、文件放置和资源使用规则。

快速连通、磁盘、GPU 检查命令见 `docs/machine_quickstart.md`。本文保留完整规则和背景。

## 机器概览

| 机器 | 角色 | 状态 |
| --- | --- | --- |
| SJTU_HPC | 新开通的交大 HPC 账号，入口由 AISPEECH 提供。 | `2026-07-20` 起作为后续新实验的默认远端；aTrust、SSH、JumpServer、配额和调试节点已实测。 |
| Falcon | 原 RA 服务器，观察到 3 张 A800 80GB，常处于繁忙状态。 | 仅在反向隧道可用且资源空闲时使用。 |
| A800_2 | 徐浩铭师兄提供的旧计算主机，观察到 8 张 A800-SXM4-80GB。 | 公钥已被删除；仅保留历史 run 和路径记录，不再作为默认目标。 |

### SJTU_HPC 规则

当前已确认入口：

```text
逻辑名: SJTU_HPC
SSH 别名: sjtu-hpc
SSH/堡垒机: feiyang.ying@js-hpc.aispeech.com.cn:2222
HPC Web 入口: http://js-hpc.aispeech.com.cn/
aTrust 租户/初始化地址: https://trust.aispeech.com.cn:4430
UM 账号: fy.ying_sjtu_buss
UM 改密入口: http://p.aispeech.com.cn
LDAP 自助改密: http://ldap-hpc.aispeech.com.cn
用户家目录: /hpc_stor03/sjtu_home/feiyang.ying
计划项目根目录: /hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability
```

已知边界：

- 附件《零信任VPN接入指南》要求通过 aTrust 登录；首次登录需要绑定终端并完成短信验证。
- UM 初始密码和 HPC/LDAP 密码属于不同入口，不能混作同一凭据；两处改密均需按各自页面完成。
- 用户要求项目内保存凭据；实际值只保存在被 Git 忽略的 `.env.sjtu-hpc`，不进入受版本控制的文档、脚本或 SSH 配置。完成改密后立即更新本地文件并删除旧初始密码。
- 本机 `~/.ssh/config` 已配置 `sjtu-hpc`；项目内另有 `config/sjtu_hpc.ssh_config` 作为可复核的无密码配置。
- SSH 先进入 JumpServer，当前只有资产 `d6-hpc-debuggpu-001`；输入 `p` 后选择 `1` 进入。
- 集群使用 `vc 2.0.3`/Volcano 调度，不提供 Slurm 命令。登录资产只做调试和轻量检查，正式实验通过 `vc submit` 申请资源。
- 首登确认账号配额为 8 GPU、256 CPU、200 jobs，`hpc_stor03` 存储配额为 1 TB。

`2026-07-12` 关于贵州超算和旧交大入口的排查仅作为历史记录；`2026-07-20` 收到的 `js-hpc.aispeech.com.cn:2222` 是当前应使用的明确入口。

### VPN 与普通代理不要混用

| 层次 | 本机状态 | 用途 |
| --- | --- | --- |
| Clash TUN/fake-IP | 已启用，端口 `127.0.0.1:7890` | 普通互联网代理；会干扰域名诊断，不等于超算 VPN |
| AISPEECH aTrust | 已连接 `https://trust.aispeech.com.cn:4430`，隧道可用 | 建立到交大 HPC 内网的访问路径；Clash 不能替代它 |

附件指定 `https://trust.aispeech.com.cn:4430` 作为 aTrust 租户/初始化地址。`http://js-hpc.aispeech.com.cn/` 是 VPN 内的 HPC Web/堡垒机入口，不是 aTrust 网关；HPC/SSH 密码也不能据此认定为 aTrust 密码。

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

### SJTU_HPC 默认路由

首次连接顺序：

1. 在 aTrust 中连接 `https://trust.aispeech.com.cn:4430`。
2. 确认客户端显示在线且隧道可用。
3. 执行 `ssh sjtu-hpc`。
4. 在 JumpServer 输入 `p`，再输入 `1` 进入 `d6-hpc-debuggpu-001`。

如果不使用本机 SSH 别名，可从项目根目录执行：

```bash
ssh -F config/sjtu_hpc.ssh_config sjtu-hpc
```

首登实测节点为 `d6-hpc-debuggpu-001`，有 4 张 RTX 2080 Ti 11 GB、80 个逻辑 CPU 和 376 GiB RAM。该节点不是 A800 替代品；正式实验应使用 `vc info -u`、`vc list` 和 `vc submit`，并在作业内重新核验 GPU。不要把旧 A800 参数直接迁入。

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

### A800_2 入口（历史）

以下配置只解释历史记录。旧公钥已失效，除非机器所有者恢复访问，不再把它用于新任务。

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

对当前默认 `SJTU_HPC`，登录和配额已确认；下一步是在计划项目根目录同步代码、用最小 `vc` 作业确认 GPU 分区镜像与挂载，再决定模型放置和运行参数。在完成小作业验证前不上传大模型。

```bash
# A800_2 示例
ssh A800_2 "mkdir -p /data/xuhaoming/yfy/research_workspace/{baselines,data,envs,logs,results}"
ssh A800_2 "ls -ld /data/xuhaoming/yfy/research_workspace"
```

然后把可长期复核的资源事实记录到：

```text
docs/server_resource_inventory.md
```
