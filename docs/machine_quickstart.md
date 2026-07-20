# 机器快速检查

这是远程工作前的短命令清单。完整机器规则、文件放置、环境、下载和安全边界见 `docs/machine_handbook.md`。

## 默认远端

自 `2026-07-20` 起，后续新实验默认面向新开通的交大 HPC，逻辑名为 `SJTU_HPC`，本机 SSH 别名为 `sjtu-hpc`。

```text
SSH/堡垒机: feiyang.ying@js-hpc.aispeech.com.cn:2222
HPC Web 入口: http://js-hpc.aispeech.com.cn/
aTrust 租户/初始化地址: https://trust.aispeech.com.cn:4430
UM 账号: fy.ying_sjtu_buss
UM 改密入口: http://p.aispeech.com.cn
LDAP 自助改密: http://ldap-hpc.aispeech.com.cn
用户家目录: /hpc_stor03/sjtu_home/feiyang.ying
计划项目根目录: /hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability
```

安全边界：

- 实际凭据按用户要求保存在项目内的 `.env.sjtu-hpc`；该文件已被 Git 忽略。HPC/SSH 凭据与 aTrust 登录凭据按用途分开记录，不要把内容复制到受版本控制的文档、脚本、命令行或日志。
- 先在 aTrust 连接 AISPEECH 零信任网络，再连接 SSH。当前终端已经完成首次绑定并可建立隧道；Clash 只能代理普通互联网流量，不能替代 aTrust。
- UM 与 HPC/LDAP 分别通过各自入口改密。改密完成后立即更新 `.env.sjtu-hpc` 并移除旧初始密码。
- 登录后只在调度分配或获准的计算节点运行实验，不在登录节点直接启动模型任务。
- 进入 GPU 节点后先检查实际 GPU 型号、显存、占用、磁盘和已有环境；旧 A800 参数不能直接照搬。

首次连接：

```bash
# 先在 aTrust 中连接 https://trust.aispeech.com.cn:4430
ssh sjtu-hpc
# JumpServer 中输入 p 查看资产，再输入 1 进入当前唯一授权主机
```

项目内配置形式：

```bash
ssh -F config/sjtu_hpc.ssh_config sjtu-hpc
```

`2026-07-20` 实测：aTrust 建立到 AISPEECH 租户的隧道后，`js-hpc.aispeech.com.cn` 解析为内网地址并可完成 SSH 密码认证。该 SSH 地址首先进入 JumpServer 堡垒机；当前账号只有一个授权资产 `d6-hpc-debuggpu-001`，不是直接落到计算分区。

资源摘要：

```text
调度器: vc 2.0.3（Volcano 风格），不是 Slurm；本机没有 sinfo/squeue/sbatch
账号配额: 8 GPU / 256 CPU / 200 jobs
分区: pdgpu-a10, pdgpu-ezkws, pdcpu, pdcpu-ezkws
存储: hpc_stor03 1 TB；当前用量 0
调试节点: 4 x RTX 2080 Ti 11 GB，80 逻辑 CPU，376 GiB RAM
环境模块: anaconda/3, python/3.9.17, CUDA 10.0--12.2, cuDNN 8.9.7 等
```

常用只读命令：

```bash
vc info -u
vc list
module avail
nvidia-smi
```

## 远端项目根目录

```text
SJTU_HPC home: /hpc_stor03/sjtu_home/feiyang.ying
SJTU_HPC project: /hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability（计划路径，尚未同步）
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
