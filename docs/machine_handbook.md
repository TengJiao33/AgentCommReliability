# 机器手册

> 目的：在启动任何实验前，明确机器访问、文件放置和资源使用规则。

快速连通、磁盘、GPU 检查命令见 `docs/machine_quickstart.md`。本文保留完整规则和背景。

## 机器概览

| 机器 | 角色 | 状态 |
| --- | --- | --- |
| X_LANCE_HPC | 新获批的 X-LANCE 超算账号；较新 Wiki 指向贵州超算。 | `2026-07-12` 起作为后续新实验的默认远端；Wiki 账号有效，VPN/SSH 首登尚未完成。 |
| Falcon | 原 RA 服务器，观察到 3 张 A800 80GB，常处于繁忙状态。 | 仅在反向隧道可用且资源空闲时使用。 |
| A800_2 | 徐浩铭师兄提供的旧计算主机，观察到 8 张 A800-SXM4-80GB。 | 公钥已被删除；仅保留历史 run 和路径记录，不再作为默认目标。 |

### X_LANCE_HPC 规则

当前线索：

```text
较新入口: 贵州超算，需要超算账号和 VPN；现行 VPN/SSH 地址待确认
历史入口: 苏州超算 hpc.ai-research.cn:5232（旧 Wiki，DNS 已失效）
历史入口: 交大超算 login.hpc.sjtu.edu.cn:22（旧 Wiki，DNS 已失效）
小集群入口: 202.120.38.69:5566（不是当前默认超算目标）
```

已知边界：

- `202.120.38.10:10780` 是 X-LANCE Wiki，不是 SSH 主机。
- 审批标题是“wiki 和超算申请”，因此默认把新资源视为超算账号，不把交大小集群误写成已经确认的物理目标。
- `resources:tools` 页面在 `2024-05-29` 更新，明确列出“贵州超算用户文档”和“Tutorial 贵州超算使用 v2.0”，并要求先加入钉钉群、申请超算账号和 VPN。
- `resources:clusters:start` 页面最后修改于 `2023-02-13`，其中苏州和交大入口只能作为历史线索。
- 交大小集群的外部入口落到 `gauss`；Wiki 明确禁止在 `gauss` 上运行程序，必须再跳转到具体计算节点。
- Wiki 中的入口和硬件表属于最后已知资料，不能代替管理员确认与首登实测。
- 项目根目录、磁盘配额、可用模型、Python 环境和外网能力均尚未核验。
- 初始密码不得写入仓库或自动化命令。首次成功登录后应改密并安装当前用户的新公钥。

`2026-07-12` 连接检查：Wiki 账号认证成功；旧苏州、交大超算和小集群候选均未进入密码认证。绑定 WLAN 绕过 Clash 后，交大 DNS 也确认旧苏州域名没有 A 记录、旧交大超算域名为 NXDOMAIN。当前最可信的阻塞是缺少贵州超算对应的 VPN 配置和现行入口。

### 三类代理不要混用

| 层次 | 本机状态 | 用途 |
| --- | --- | --- |
| Clash TUN/fake-IP | 已启用，端口 `127.0.0.1:7890` | 普通互联网代理；会干扰域名诊断，不等于超算 VPN |
| X-LANCE 公共代理 | Wiki 有单独配置，凭据不写入仓库 | 可能用于登录后的 GitHub、包下载等外网访问，不负责授予超算内网路由 |
| 贵州超算 VPN | 尚未配置 | 建立到超算内网的访问路径；需要设备委员提供租户/网关和权限 |

本机 aTrust `2.2.10.4` 当前只有重庆大学图书馆资源配置，没有 X-LANCE/AISpeech/贵州超算租户。不要因为客户端已安装就判断 VPN 已具备。

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

### X_LANCE_HPC 默认路由

设备委员提供贵州超算 VPN 租户/网关、现行 SSH 主机和端口后：

```bash
1. 在 aTrust 或指定 VPN 客户端中登录 X-LANCE/贵州超算租户
2. 验证目标内网路由和 DNS
3. 使用管理员提供的 SSH 主机、端口和用户 fyy05 首登
```

如果设备委员明确说明分配的是交大小集群，才改用下面的入口；成功进入 `gauss` 后只做登录路由和轻量检查，再按集群 Wiki 进入获准的 GPU 节点：

```bash
ssh -p 5566 fyy05@202.120.38.69
hostname
whoami
ssh <gpu-node>
```

到达 GPU 节点后再执行本文的 GPU、磁盘和进程检查。不要预先创建旧 A800 路径，也不要在不知道节点共享存储规则时同步大文件。

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

对当前默认 `X_LANCE_HPC`，先确认物理集群，再在 Slurm 分配或具体 GPU 节点中确认 home、共享盘、配额和清理规则，最后确定项目根目录；在此之前不创建目录、不上传模型。

```bash
# A800_2 示例
ssh A800_2 "mkdir -p /data/xuhaoming/yfy/research_workspace/{baselines,data,envs,logs,results}"
ssh A800_2 "ls -ld /data/xuhaoming/yfy/research_workspace"
```

然后把可长期复核的资源事实记录到：

```text
docs/server_resource_inventory.md
```
