# 服务器资源清单

这是远端资源的保留操作台账。

当前快照更新于 `2026-07-20`。配额来自 `vc info -u`，节点硬件来自首次登录时的现场查询；启动新任务前仍需刷新队列和目标作业节点状态。

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
| 可用分区 | `pdgpu-a10`、`pdgpu-ezkws`、`pdcpu`、`pdcpu-ezkws` |
| 存储 | `hpc_stor03` 配额 1 TB，首登用量 0；家目录位于该共享存储 |
| 计划项目根目录 | `/hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability`，尚未创建/同步 |
| 调试节点 | `d6-hpc-debuggpu-001`：4 x RTX 2080 Ti 11 GB；80 逻辑 CPU；376 GiB RAM |
| 当前访问状态 | aTrust 隧道在线，SSH 密码认证成功，JumpServer 与唯一授权资产均可进入 |

凭据规则：实际值按用户要求保存在项目内、被 Git 忽略的 `.env.sjtu-hpc`。受版本控制的文档和 SSH 配置不记录密码。UM、HPC/SSH 与 aTrust 是不同用途，不能因字段名称相似而混用；完成改密后立即更新本地文件并移除旧值。

现有 Qwen2.5-7B 脚本按单张 A800 80GB 和 bfloat16 编写。调试节点只有 11 GB 的 RTX 2080 Ti，不能复用单卡 A800 参数；正式运行前必须通过 `vc` 申请 GPU 分区，再在作业内核验实际 GPU 型号、显存和 bfloat16 支持。

## 2026-07-20 接入记录

- 管理员提供了 UM 账号、HPC/SSH 账号、SSH/Web 入口、LDAP 自助改密入口和家目录。
- 附件《零信任VPN接入指南》确认客户端为 aTrust；首次登录需要绑定终端并完成短信验证。
- aTrust 已连接 `https://trust.aispeech.com.cn:4430`；隧道建立后 `js-hpc.aispeech.com.cn` 的内网路由可用。
- 本机 SSH 配置已增加 `sjtu-hpc`，项目内另保留 `config/sjtu_hpc.ssh_config`。
- 未连接 aTrust 时，普通 DNS 查询经 Clash 返回 fake-IP；连接后 `js-hpc.aispeech.com.cn` 解析到 `10.12.4.127`，SSH 密码认证成功。
- SSH 入口是 JumpServer 堡垒机。当前唯一授权资产为 `d6-hpc-debuggpu-001`（连接目标 `10.24.19.254`）。
- `vc info -u` 返回 GPU 8、CPU 256、JOB 200；`vc list` 首登时为空。
- 系统 `python3` 为 3.6.8；模块提供 `anaconda/3`、`python/3.9.17`、多版本 CUDA 与 cuDNN，正式环境尚未安装到用户目录。
- `2026-07-12` 关于贵州超算、旧苏州入口和 `202.120.38.69:5566` 的排查已被本次明确入口取代，只作为历史背景保留在 Git 历史中。

## 远端根目录

| 机器 | 项目根目录 | 说明 |
| --- | --- | --- |
| `SJTU_HPC` | home: `/hpc_stor03/sjtu_home/feiyang.ying`；project: `/hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability`（计划） | `2026-07-20` 起的默认新实验目标；项目尚未同步。 |
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
