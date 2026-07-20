# 机器快速检查

这是远程工作前的短命令清单。完整机器规则、文件放置、环境、下载和安全边界见 `docs/machine_handbook.md`。

## 默认远端

自 `2026-07-12` 起，后续新实验默认面向新获批的 X-LANCE 超算账号，本文先用逻辑名 `X_LANCE_HPC`。审批截图只给出账号和 Wiki，没有给出物理集群名。较新的 Wiki“基本工具”页把贵州超算列为当前超算入口，并明确要求同时申请超算账号和 VPN；因此当前最可能的物理目标是贵州超算，但仍需设备委员确认。

```text
用户: fyy05
Wiki: http://202.120.38.10:10780
VPN/SSH 入口: 待设备委员提供贵州超算当前网关和地址
项目根目录: 待首次成功登录并检查配额、磁盘和节点后确定
```

安全边界：

- 初始密码只用于首次交互登录，不写入仓库、脚本、SSH 配置或日志；首次成功登录后按集群要求改密并配置新的公钥。
- 先连接贵州超算指定的 VPN，再按当前教程使用 SSH/跳板；本机普通 Clash 代理不能替代该 VPN。
- 登录后只在调度分配或获准的计算节点运行实验，不在登录节点直接启动模型任务。
- 进入 GPU 节点后先检查实际 GPU 型号、显存、占用、磁盘和已有环境；旧 A800 参数不能直接照搬。

截至 `2026-07-12` 的本地检查结果：

- Wiki 账号可登录，说明账号和初始密码有效。
- Clash for Windows 正在使用 TUN + fake-IP；它会把未知域名显示成 `198.18.0.0/15` 地址，但绑定物理 WLAN、直查交大 DNS 后，旧苏州域名仍没有 A 记录，旧交大超算域名仍为 NXDOMAIN。
- 本机已安装 Sangfor aTrust `2.2.10.4`，但现有租户和资源属于重庆大学图书馆访问；没有 X-LANCE、AISpeech 或贵州超算配置。
- X-LANCE Wiki 的贵州超算用户文档需要相应 VPN 才能访问，飞书 v2.0 教程需要飞书登录。当前缺少的是 VPN 租户/网关和现行 SSH 地址，尚未进入超算密码认证。

## 远端项目根目录

```text
X_LANCE_HPC: 待核验
Falcon: /mnt/20t/xuhaoming/yfy/research_workspace
A800_2: /data/xuhaoming/yfy/research_workspace（历史路径，不再作为默认目标）
```

## A800_2（历史）

旧机器公钥已被删除，当前不可作为后续实验入口。以下命令仅保留用于理解历史 run；除非访问被明确恢复，不再执行。

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
