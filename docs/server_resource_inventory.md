# 服务器资源清单

这是远端资源的保留操作台账。

当前快照更新于 `2026-07-20`。配额来自 `vc info -u`，节点硬件来自首次登录时的现场查询；启动新任务前仍需刷新队列和目标作业节点状态。

交大 HPC 的使用和计费说明见 `docs/sjtu_hpc_guide.md`。

## 当前默认远端：SJTU_HPC

自 `2026-07-20` 起，后续新实验默认迁移到新开通的交大 HPC 账号。aTrust、SSH、JumpServer 资产、调度器、配额、共享盘和调试节点已经完成首次只读核验。

| 项目 | 当前记录 |
| --- | --- |
| 逻辑名 | `SJTU_HPC` |
| SSH/堡垒机 | `feiyang.ying@js-hpc.aispeech.com.cn:2222`；本机别名 `sjtu-hpc` |
| HPC Web 入口 | `http://js-hpc.aispeech.com.cn/` |
| aTrust 租户/初始化 | `https://trust.aispeech.com.cn:4430` |
| UM 账号 | `fy.ying_sjtu_buss`；改密入口 `http://p.aispeech.com.cn` |
| LDAP 自助改密 | `http://ldap-hpc.aispeech.com.cn` |
| 用户家目录 | `/hpc_stor03/sjtu_home/feiyang.ying` |
| 登录路由 | SSH 先进入 JumpServer；输入 `p` 后选资产 `1`，进入 `d6-hpc-debuggpu-001` |
| 调度 | `vc 2.0.3`，Volcano 风格；没有 Slurm 的 `sinfo/squeue/sbatch` |
| 账号配额 | 8 GPU、256 CPU、200 jobs |
| `pdgpu-a10` | 常规队列 23 台、小作业队列 3 台；每台 8 GPU、80 CPU、约 503 GiB RAM；实测 NVIDIA A10 24564 MiB，驱动 570.144；两卡拓扑为 `SYS`，没有 NVLink，CUDA P2P 读取可用 |
| `pdgpu-3090` | 未列在 `vc info -u` 中，但实测可提交；1 GPU 任务路由到 `pdgpu-3090-minijob`；实测 RTX 3090 24576 MiB，驱动 570.144；两卡拓扑为 `SYS`，NVLink 未激活 |
| `pdgpu-ezkws` | 2 台节点；每台 8 x RTX 2080 Ti 11 GB、80 CPU、约 503 GiB RAM；最小作业已完成 |
| CPU 分区 | `pdcpu` 13 台、`pdcpu-ezkws` 2 台；每台 112 CPU、约 1.47 TiB RAM；`pdcpu` 实测为双路 Xeon Gold 6258R |
| 存储 | `hpc_stor03` 配额 1 TB；部署项目后用量约 204.8 MB；家目录位于该共享存储 |
| 项目根目录 | `/hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability`；已部署提交 `d21e89b` |
| 调试节点 | `d6-hpc-debuggpu-001`：4 x RTX 2080 Ti 11 GB；80 逻辑 CPU；376 GiB RAM |
| 当前访问状态 | aTrust 隧道在线，SSH 密码认证成功，JumpServer 与唯一授权资产均可进入 |

凭据规则：实际值按用户要求保存在项目内、被 Git 忽略的 `.env.sjtu-hpc`。受版本控制的文档和 SSH 配置不记录密码。UM、HPC/SSH 与 aTrust 是不同用途，不能因字段名称相似而混用；完成改密后立即更新本地文件并移除旧值。

现有任务是 Qwen2.5-7B 推理和隐藏状态/KV 干预，不是全参数训练。单张 A10 或 RTX 3090 能容纳约 14–15 GB 的 BF16 权重；8192 token 上下文、1536 token 输出和逐 token 注意力归因仍可能超过 24 GB。先用 4096/256 和 1–5 道题测峰值显存，再放大参数。当前 runner 是单卡实现，8 张 GPU 应先用于独立数据分片或实验条件；这种并行不需要 NVLink。

## 2026-07-20 接入记录

- 管理员提供了 UM 账号、HPC/SSH 账号、SSH/Web 入口、LDAP 自助改密入口和家目录。
- 附件《零信任VPN接入指南》确认客户端为 aTrust；首次登录需要绑定终端并完成短信验证。
- aTrust 已连接 `https://trust.aispeech.com.cn:4430`；隧道建立后 `js-hpc.aispeech.com.cn` 的内网路由可用。
- 本机 SSH 配置已增加 `sjtu-hpc`，项目内另保留 `config/sjtu_hpc.ssh_config`。
- 未连接 aTrust 时，普通 DNS 查询经 Clash 返回 fake-IP；连接后 `js-hpc.aispeech.com.cn` 解析到 `10.12.4.127`，SSH 密码认证成功。
- SSH 入口是 JumpServer 堡垒机。当前唯一授权资产为 `d6-hpc-debuggpu-001`（连接目标 `10.24.19.254`）。
- `vc info -u` 返回 GPU 8、CPU 256、JOB 200；`vc list` 首登时为空。
- `pdgpu-ezkws` 最小作业在 `d6-hpc-gpu-033` 完成，实测为 RTX 2080 Ti 11 GB、驱动 570.144；所用镜像内 Python 为 3.10.20。
- `pdcpu` 最小作业在 `d6-hpc-cpu-005` 完成，实测为双路 Xeon Gold 6258R、56 个物理核心、112 个逻辑 CPU、约 1.5 TiB 内存；实际命令运行 12 秒。
- `pdcpu-ezkws` 最小作业在 `d6-hpc-cpu-013` 完成，硬件同为双路 Xeon Gold 6258R、112 个逻辑 CPU、约 1.5 TiB 内存；实际命令运行 15 秒。
- 1 GPU 的 A10 探测被路由到 `pdgpu-a10-minijob`，在 `d6-hpc-gpu-038` 上完成。实测为 NVIDIA A10 24564 MiB、驱动 570.144；排队约 14 分钟，实际命令运行 11 秒。
- 1 GPU 的 3090 探测通过 `pdgpu-3090` 提交，被路由到 `pdgpu-3090-minijob`，在 `d6-hpc-gpu-039` 上完成。实测为 RTX 3090 24576 MiB、驱动 570.144。
- 2 GPU 拓扑探测显示，A10 节点和 RTX 3090 节点的两卡连接均为 `SYS`，没有活动的 NVLink。A10 的 CUDA P2P 读取检查通过；3090 的 `nvidia-smi` P2P 查询返回芯片组不支持报告。
- 当前硬件探测镜像使用 Python 3.10.20，但没有安装 PyTorch、Transformers 或 vLLM。正式运行需要准备项目镜像。
- 公共目录 `/hpc_stor03/public/shared/models` 中有 Llama-3-8B、Vicuna-7B 等模型，没有 Qwen2.5-7B。正式实验仍需上传模型或取得管理员提供的共享路径。
- 管理员说明集群按使用时间计费。实测 `Pending` 且未分到节点的任务开始时间为空、持续时间为 0。具体单价、计费取整和容器准备阶段是否计费尚未确认。
- D6 当前有 99 台 Ready 节点，GPU 容量合计 613 张。5090、4090、V100 和 `pdgpu-tfg` 的最小提交均明确返回“没有队列权限”；其他 2080 Ti 子队列未测试。
- 项目现有 Hugging Face runner 把整个模型放到一张卡，vLLM runner 的 `tensor_parallel_size` 固定为 1。当前代码不能把单个模型切到多张卡。
- 钉钉“AI超算工单”提供队列权限、平台配额、存储配额、服务器权限和软件部署申请。队列权限与账号 GPU 总配额是两项独立配置。
- 《AI超算QA-0807》和《AI超算使用规范-beta-v1.1》创建于 2018 年，其中 Slurm、Lustre、旧登录地址和默认 2 TB 空间已经过时；账号、数据和调度纪律仍作为使用边界。
- 项目提交 `d21e89b` 已通过 SFTP、SHA-256 校验并解压到项目根目录；远端写有 `.deployed-commit` 标记。
- 系统 `python3` 为 3.6.8；模块提供 `anaconda/3`、`python/3.9.17`、多版本 CUDA 与 cuDNN，正式环境尚未安装到用户目录。
- `2026-07-12` 关于贵州超算、旧苏州入口和 `202.120.38.69:5566` 的排查已被本次明确入口取代，只作为历史背景保留在 Git 历史中。

## 远端根目录

| 机器 | 项目根目录 | 说明 |
| --- | --- | --- |
| `SJTU_HPC` | home: `/hpc_stor03/sjtu_home/feiyang.ying`；project: `/hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability` | `2026-07-20` 起的默认新实验目标；已部署提交 `d21e89b`。 |
| `A800_2` | `/data/xuhaoming/yfy/research_workspace` | 历史受控项目根目录；当前访问失效。 |
| `Falcon` | `/mnt/20t/xuhaoming/yfy/research_workspace` | 仅在路由可用且资源空闲时使用。 |

## A800_2 历史访问

本节保留历史 run 的复核信息。旧公钥已被删除，不再假设下列入口可用。

SSH 别名：

```text
A800_2
```

直连形式：

```text
ssh -p 10622 xuhaoming@124.128.251.61
```

最后已知主机标识：

```text
10-116-90-20
```

## A800_2 项目工作区清理

最近清理：`2026-07-03`。

远端项目根目录：

```text
/data/xuhaoming/yfy/research_workspace
```

远端项目文件夹已重置为最小骨架。旧实验、结果、日志、脚本、基线 checkout、报告、数据、测试框架文件、临时文件、备份和传输压缩包都已从该文件夹移除。

保留的可复用运行时/缓存目录：

| 路径 | 最近检查大小 | 原因 |
| --- | ---: | --- |
| `envs/` | `7.1G` | 可复用的项目 Python 环境 |
| `pip_cache/` | `3.2G` | 可复用包缓存 |
| `hf_home/` | `20K` | 可复用 Hugging Face 缓存根目录 |
| `modelscope_cache/` | `8.0K` | 可复用 ModelScope 缓存根目录 |
| `torch_home/` | `4.0K` | 可复用 Torch 缓存根目录 |

当前保留的骨架目录：

```text
active/
baselines/
docs/
experiments/
reports/
README.md
```

## 已准备基准数据

最近准备：`2026-07-03`。

远端位置：

```text
/data/xuhaoming/yfy/research_workspace/data/benchmarks
```

这些数据只放在项目根目录下。准备时 `A800_2` 无法访问 Hugging Face，因此基准 JSONL 文件是在本地生成后传入项目文件夹的。MMLU-Pro 源 parquet 快照也复制到了：

```text
/data/xuhaoming/yfy/research_workspace/data/source_repos/MMLU-Pro
```

| 基准 | 来源 | 划分 | 行数 |
| --- | --- | --- | ---: |
| `mmlu_pro` | `TIGER-Lab/MMLU-Pro` | `test`, `validation` | 12,102 |
| `gsm8k` | `openai/gsm8k`，配置 `main` | `train`, `test` | 8,792 |
| `math500` | `HuggingFaceH4/MATH-500` | `test` | 500 |
| `aime24` | `HuggingFaceH4/aime_2024` | `train` | 30 |
| `aime25` | `math-ai/aime25` | `test` | 30 |

## 共享资源规则

- 项目文件放在项目根目录下。
- 将 `/mnt/quarkfs/share_model` 视为共享只读目录，除非得到明确许可。
- 不要把大型模型权重重复复制到项目工作区。
- 不要安装到共享 conda 环境。
- 不要杀掉其他用户的进程。
- 任何新模型、数据集、环境、缓存或成本较高的结果目录，都要记录下来。

## 最后已知共享模型根目录

```text
/mnt/quarkfs/share_model
```

早期清单中已知有用的模型族：

- `Qwen2.5-*`
- `Qwen3*`
- `BGE-large-en-v1.5`
- `bge-reranker-large`

使用前刷新可用性。

## 刷新命令

```powershell
ssh A800_2 'hostname; date -Is; df -h /data /mnt/quarkfs; nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits'
ssh A800_2 'WORK=/data/xuhaoming/yfy/research_workspace; mkdir -p "$WORK"; du -sh "$WORK"; du -sh "$WORK"/* 2>/dev/null | sort -h'
ssh A800_2 'du -sh /mnt/quarkfs/share_model/* 2>/dev/null | sort -h'
```

## 更新检查清单

发生以下情况时更新本文档：

- 新模型被下载、完成、修改或作为依赖使用；
- 新数据集或基准副本被创建；
- 新环境或大型缓存被创建；
- 某次运行写入超过 `1G`；
- 清理操作移除了远端产物；
- 长期服务被启动并留在后台运行。
