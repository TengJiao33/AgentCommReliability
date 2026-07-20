# 交大 HPC 使用说明

更新时间：`2026-07-20`

当前账号已经完成 aTrust 接入、SSH 登录、JumpServer 授权、项目部署和最小作业测试。项目位于：

```text
/hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability
```

这套 HPC 由入口机和计算集群组成。登录后所在的 `d6-hpc-debuggpu-001` 是调试机；正式任务通过 `vc` 提交到 CPU 或 GPU 分区。

## 系统结构

```text
本机 → aTrust → JumpServer → 调试机 → vc 调度器 → 计算节点
```

| 组件 | 作用 |
| --- | --- |
| aTrust | 建立到 AISPEECH 内网的通道。 |
| JumpServer | 验证身份并显示授权资产。 |
| `d6-hpc-debuggpu-001` | 管理文件、提交任务、查看日志和做轻量调试。 |
| `vc` | 根据任务请求分配 CPU、GPU 和内存。当前版本为 `cloud-2.0.3`。 |
| 计算节点 | 运行 `vc submit` 提交的命令。 |

## 账号配额

`vc info -u -cluster D6` 返回：

| 资源 | 配额 |
| --- | ---: |
| GPU | 8 张 |
| CPU | 256 核 |
| 作业数 | 200 个 |
| `hpc_stor03` 存储 | 1 TB |

配额限制账号同时申请的资源总量。任务能否立即启动还取决于分区中的空闲资源。系统不允许资源超配。

D14 和 D2 也返回账号数字配额，但没有列出可提交分区。按 A100、A800、H800、H100 和 5090 等常见名称查询时，两个平台都返回“partition is not found”。当前实测成功的分区都在 D6；D14 和 D2 的资源目录需通过工单确认。

## 计算分区

| 分区 | 节点规模 | 实测硬件 | 当前判断 |
| --- | --- | --- | --- |
| `pdgpu-a10` | 常规队列 23 台，小作业队列 3 台；每台 8 GPU、80 CPU、约 503 GiB 内存 | NVIDIA A10，单卡 24564 MiB；驱动 570.144 | 正式 GPU 分区。1 GPU 探测被自动路由到 `pdgpu-a10-minijob`，排队约 14 分钟后运行 11 秒。 |
| `pdgpu-3090` | 常规及子队列共 24 台、188 GPU；小作业队列有 2 台、12 GPU | RTX 3090，单卡 24576 MiB；驱动 570.144 | 未列在 `vc info -u` 中，但 1 GPU 实测提交成功，并被路由到 `pdgpu-3090-minijob`。 |
| `pdgpu-ezkws` | 2 台；每台 8 GPU、80 CPU、约 503 GiB 内存 | RTX 2080 Ti，单卡 11 GiB；驱动 570.144 | 可运行小模型、短推理和兼容性测试。 |
| `pdcpu` | 13 台；每台 112 CPU、约 1.47 TiB 内存 | 双路 Xeon Gold 6258R；56 物理核、112 线程 | 数据处理、评测汇总和大内存 CPU 任务。 |
| `pdcpu-ezkws` | 2 台；每台 112 CPU、约 1.47 TiB 内存 | 双路 Xeon Gold 6258R；56 物理核、112 线程 | 与 `pdcpu` 同级的 CPU 任务分区。 |

表中的节点规模属于整个共享分区。账号最多同时申请 8 张 GPU 和 256 个 CPU。

### D6 集群的整体规模

Kubernetes 节点状态显示 D6 当前有 99 台 Ready 节点，其中 GPU 节点的容量合计为 613 张。容量表示节点安装的 GPU 数，不表示当前空闲数。

| 分区标签 | 节点数 | GPU 容量 | 当前账号实测 |
| --- | ---: | ---: | --- |
| `pdgpu-a10*` | 26 | 208 | 可提交；1 GPU 路由到小作业队列。 |
| `pdgpu-3090*` | 24 | 188 | 可提交；1 GPU 路由到小作业队列。 |
| `pdgpu-4090` | 8 | 64 | 返回“没有队列权限”。 |
| `pdgpu-5090` | 1 | 8 | 返回“没有队列权限”。 |
| `pdgpu-v100` | 5 | 40 | 返回“没有队列权限”。 |
| `pdgpu-2080ti*`，含 `ezkws` | 12 | 95 | `pdgpu-ezkws` 可提交；其他子队列未测试。 |
| `pdgpu-tfg`、`notebook-gpu` | 2 | 10 | `pdgpu-tfg` 返回“没有队列权限”。 |

`vc info -u` 只列出 A10、`ezkws` 和两个 CPU 分区，但 3090 实际可以提交。因此判断权限应以一次最小提交的服务端结果为准，不能只看 `vc info -u`。目前没有发现账号可用的 32 GB、48 GB 或 80 GB 单卡分区。

### 调试机

`d6-hpc-debuggpu-001` 的实测配置：

- 4 张 RTX 2080 Ti，每张 11 GiB 显存；
- 2 颗 Xeon Gold 6242R；
- 40 个物理核心、80 个逻辑 CPU；
- 约 376 GiB 内存。

调试机是共享入口，不属于 `vc` 分配的正式计算资源。长期实验提交到计算分区。

## 当前算力适用范围

RTX 2080 Ti 的单卡显存约为 11 GiB，适合小模型、少量样本、量化推理和运行链路验证。现有项目中的部分脚本按单张 A800 80 GB 和 bfloat16 编写，迁移到 2080 Ti 时需要降低显存占用并调整精度。2080 Ti 不支持原生 bfloat16 训练。

8 张 GPU 是账号上限，不是一块合并后的 88 GiB 显存。程序需要通过数据并行、张量并行、FSDP 或 DeepSpeed 等方案显式使用多卡。

A10 实测显存为 24564 MiB。NVIDIA 公布的 A10 规格为 24 GB GDDR6、31.2 TFLOPS FP32、125 TFLOPS BF16/FP16 Tensor Core 和 600 GB/s 显存带宽。A10 支持 bfloat16。账号最多可申请 8 张 A10，即 8 × 24 GB 物理显存；多卡显存需要分布式框架来使用。规格来源：[NVIDIA A10](https://www.nvidia.com/en-us/data-center/products/a10-gpu/)。

单张 A10 通常可以容纳 7B 模型的 FP16/BF16 权重，但推理还要为 KV cache 和运行时留出显存。全参数训练所需显存远高于 24 GB。现有 A800 80 GB 参数仍需缩小 batch、上下文长度或改用量化、LoRA 和多卡切分。

CPU 分区的单节点内存约为 1.47 TiB。数据预处理、索引构建和结果汇总可以在 CPU 分区完成，减少 GPU 作业中的非 GPU 时间。

### 本项目怎样使用这些 GPU

结论：当前任务能跑，硬件不构成严重限制。

项目当前要做的是 Qwen2.5-7B 推理、隐藏状态/KV 干预和条件对照，不是全参数训练。7B 模型的 BF16 权重约占 14–15 GB，能够装进单张 24 GB 的 A10 或 RTX 3090。程序使用 `torch.inference_mode()`，不会保存训练所需的梯度和优化器状态。

显存最紧张的部分是原实验参数：8192 token 上下文、最多生成 1536 token，并在逐 token 解码时读取注意力。该组合可能超过 24 GB，且 eager attention 会比 Flash Attention 更慢。先用 4096 token 上下文、256 token 输出和 1–5 道题测峰值显存；通过后再逐级恢复正式参数。

当前 runner 是单卡实现：

- Hugging Face 路径接收一个 `--gpu-id`，随后把整个模型放到 `cuda:0`；
- vLLM 路径把 `tensor_parallel_size` 固定为 1；
- 项目没有使用 Accelerate、DeepSpeed、FSDP 或 `torchrun` 来切分模型。

因此，现有代码一次只会使用一张 GPU。8 张 GPU 适合分别运行不同条件或数据分片。当前 runner 还没有行分片参数；正式并行前需要增加 `--shard-count` / `--shard-index`，或预先拆分输入数据，避免多个作业重复处理同一批题。

让一个模型同时使用多张卡需要改 runner。vLLM 路径可以增加张量并行参数；直接操作隐藏状态和 KV cache 的 Hugging Face 路径还要处理跨设备张量位置，不能只修改 `CUDA_VISIBLE_DEVICES`。

### GPU 互联实测

在 `d6-hpc-gpu-038` 上申请两张 A10、在 `d6-hpc-gpu-039` 上申请两张 RTX 3090 后，`nvidia-smi topo -m` 均显示两卡之间为 `SYS`，没有 `NV#`。`nvidia-smi nvlink -s` 在 3090 节点明确返回所有 NVLink 均未激活。A10 节点的 CUDA P2P 读取检查返回 `OK`，但数据仍通过 PCIe 和跨 NUMA 的 CPU 互联传输。

这对当前单卡 runner 没有影响。以后若把同一个模型切到多卡，NCCL 仍可通过 PCIe 工作，但张量并行的通信速度会低于 NVLink。独立的单卡作业之间不交换张量，不受 NVLink 缺失影响。

### 当前任务开跑顺序

1. 准备包含 PyTorch、Transformers 和项目依赖的内部镜像。当前硬件探测镜像只有 Python 3.10.20，实测没有 `torch`、`transformers` 或 `vllm`。
2. 把 Qwen2.5-7B-Instruct 放到 `hpc_stor03`，或请管理员提供已有的共享路径。当前公共模型目录 `/hpc_stor03/public/shared/models` 中没有 Qwen2.5；其中的 Llama-3-8B 和 Vicuna-7B 不能直接替代正式实验模型。
3. 在单张 A10 上跑 1–5 道题，记录峰值显存和单题耗时。
4. 若 4096/256 配置稳定，再依次增加输出长度、上下文长度和题数。不要一次恢复全部 A800 参数，否则无法判断是哪一项造成显存不足。
5. 单卡稳定后，把题目或条件分片到多张 GPU。没有 NVLink 不影响这种并行方式。

最小 smoke test 的提交形式如下。`<正式镜像>` 和 `<Qwen2.5-7B-Instruct 路径>` 准备好后即可替换：

```bash
vc submit \
  -p pdgpu-a10 \
  -i <正式镜像> \
  -j acr-qtoken-smoke \
  -n 1 \
  -c 8 \
  -m 64G \
  -g 1 \
  --project sjtu \
  --dir /hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability \
  --cmd 'python3 scripts/run_mca_question_token_anchored_delta.py \
    --work-dir /hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability \
    --run-id sjtu-qtoken-smoke \
    --benchmark math500 \
    --split mca_disagreement_v1 \
    --model-key qwen25-7b-instruct \
    --model-path <Qwen2.5-7B-Instruct 路径> \
    --agents 3 \
    --layers 22 \
    --conditions raw_delta,question_token_delta,question_token_random_same_norm \
    --attribution-method attention \
    --max-new-tokens 256 \
    --max-model-len 4096 \
    --dtype bfloat16 \
    --limit 3'
```

## 登录

1. 在 aTrust 中连接 AISPEECH 网络。
2. 从本机项目目录连接 JumpServer：

```bash
ssh sjtu-hpc
```

也可以使用项目内的 SSH 配置：

```bash
ssh -F config/sjtu_hpc.ssh_config sjtu-hpc
```

3. 在 JumpServer 输入 `p`，再选择资产 `1`，进入 `d6-hpc-debuggpu-001`。
4. 查看配额、活跃任务和项目目录：

```bash
vc info -u
vc list
cd /hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability
```

## 提交任务

### GPU 作业模板

```bash
vc submit \
  -p pdgpu-a10 \
  -i <内部镜像地址> \
  -j acr-smoke \
  -n 1 \
  -c 8 \
  -m 64G \
  -g 1 \
  --project sjtu \
  --dir /hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability \
  --cmd 'python3 <脚本> <参数>'
```

### CPU 作业模板

```bash
vc submit \
  -p pdcpu \
  -i <内部镜像地址> \
  -j acr-preprocess \
  -n 1 \
  -c 16 \
  -m 64G \
  -g 0 \
  --project sjtu \
  --dir /hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability \
  --cmd 'python3 <脚本> <参数>'
```

资源参数：

| 参数 | 含义 |
| --- | --- |
| `-p` | 计算分区。 |
| `-i` | 容器镜像。当前 `vc` 接受 `docker.v2.aispeech.com/...` 内部镜像。 |
| `-j` | 任务说明。提交后系统另行生成唯一 Job ID。 |
| `-n` | 任务副本数。 |
| `-c` | 每个副本申请的 CPU 数。 |
| `-m` | 每个副本申请的内存。 |
| `-g` | 每个副本申请的 GPU 数；CPU 作业填 0。 |
| `--project` | 项目归属。当前已验证 `sjtu`。 |
| `--dir` | 容器中的工作目录。 |
| `--cmd` | 作业实际执行的命令。命令结束后，作业进入 `Completed`。 |

模板中的资源数只是示例。任务应按实际需要申请资源。

## 查看任务和日志

`vc submit` 返回 Job ID，例如：

```text
job-178452177246203391178-feiyang-ying
```

查询作业：

```bash
# 当前活跃作业
vc list

# 最近一天的全部作业
vc list --show-all -d 1

# 一个 Job 的任务副本和所在节点
vc list -j <Job-ID> --show-all -d 1

# 提交、开始、结束时间和原始命令
vc info -j <Job-ID>
```

单副本作业的 Task ID 通常是：

```text
<Job-ID>-master-0
```

查看日志和资源用量：

```bash
vc logs -t <Task-ID> -l 200
vc logs -t <Task-ID> -f
vc top -t <Task-ID>
```

`vc logs -f` 持续显示新日志。按 `Ctrl+C` 结束日志跟随，不会停止后台作业。

诊断运行中的容器和启动错误：

```bash
vc exec -t <Task-ID>
vc describe -j <Job-ID>
```

`vc exec` 进入运行中的容器。`vc describe` 显示作业错误；部分尚未创建容器的 `Pending` 作业可能没有可显示的错误信息。

## 作业状态和计费

管理员说明集群按使用时间计费。当前系统显示作业运行时间，不显示价格。

| 状态 | 含义 | 资源处理 |
| --- | --- | --- |
| `Pending` | 等待资源，尚未分到节点 | 本次 A10 探测在排队阶段的开始时间为空，运行时间为 0。 |
| `ContainerCreating` | 已分配节点，正在准备容器或拉取镜像 | 是否进入计费时间尚未确认。 |
| `Running` | 命令正在计算节点上运行 | 已占用申请的 CPU、GPU 和内存。 |
| `Completed` | 命令正常结束 | 资源已释放。 |
| `Failed` | 作业失败 | 查询日志和错误后重新提交。 |
| `Canceled` | 作业被人工取消 | 资源已释放。 |

已完成的探测任务提供了四个时间样本：A10 运行 11 秒，2080 Ti 运行 13 秒，两个 CPU 探测分别运行 12 秒和 15 秒。计费单价、最小计费单位和取整方式仍需管理员确认。

后台作业由集群管理，退出 SSH 后继续运行。带有明确结束命令的作业会自然结束并释放资源。计划中的长实验可以跨夜运行；已经不再需要的作业应取消：

```bash
vc delete -j <Job-ID>
```

取消前先用 `vc info -j <Job-ID>` 核对任务说明和原始命令。

### `--sync`

默认的 `vc submit` 在后台提交作业。使用 `--sync` 时，提交命令会一直等待作业；实测在等待阶段按 `Ctrl+C` 会同时取消作业。长任务采用后台提交，再用 `vc list` 和 `vc logs` 跟踪。

## 存储和结果

个人目录和项目目录：

```text
/hpc_stor03/sjtu_home/feiyang.ying
/hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability
```

`vc` 默认把 `/hpc_stor03` 等共享存储挂载到容器中的相同路径。项目路径可以直接用于 `--dir`，结果也应写到该路径下。容器的 `/tmp` 用于临时文件。

`--nomount` 会关闭默认目录挂载。只有不需要共享文件时才使用。

查看个人存储配额和目录用量：

```bash
vc info -u
du -sh /hpc_stor03/sjtu_home/feiyang.ying/* 2>/dev/null
```

项目部署后，`hpc_stor03` 当前用量约为 204.8 MB。

## 容器和软件环境

作业中的 Python、PyTorch 和 CUDA 用户态库由容器镜像决定。当前硬件探测使用的镜像内含 Python 3.10.20；它是已有的 SJTU 镜像，不是本项目已经确定的正式环境。

调试机自身提供：

- 系统 Python 3.6.8；
- `anaconda/3`、`python/3.9.17` 模块；
- CUDA 10.0 至 12.2；
- cuDNN 8.9.7。

这些模块只影响调试机当前 shell。`vc` 作业仍以镜像环境为准。旧教程中的 `docker.hub.cm.cluster/...` 镜像地址已被当前版本拒绝；新作业使用 AISPEECH 内部镜像仓库。

## 文件传输

当前已验证 JumpServer SFTP。连接后显示的资产路径为：

```text
/Default/D6-HPC-guizhou/d6-hpc-debuggpu-001
```

进入资产后对应服务器家目录。上传后在 SSH 会话中用 `pwd` 和 `ls` 核对位置。当前项目快照已经完成 SHA-256 校验，并部署在项目目录中。

真实凭据保存在项目内、被 Git 忽略的 `.env.sjtu-hpc`。受版本控制的文档和 SSH 配置不保存密码。

## 入口和账号

| 用途 | 地址或账号 |
| --- | --- |
| aTrust 接入地址 | `https://trust.aispeech.com.cn:4430` |
| HPC Web/JumpServer | `http://js-hpc.aispeech.com.cn/` |
| SSH | `feiyang.ying@js-hpc.aispeech.com.cn:2222` |
| HPC/LDAP 账号 | `feiyang.ying` |
| LDAP 改密 | `http://ldap-hpc.aispeech.com.cn` |
| UM 账号 | `fy.ying_sjtu_buss` |
| UM 改密 | `http://p.aispeech.com.cn` |

HPC Web 地址位于 aTrust 内网中。它不是 aTrust 接入地址。Clash 可以代理普通互联网流量，但不能建立 HPC 内网通道。

## 申请更多资源和权限

钉钉工作台的“AI超算工单”提供以下申请入口：

| 工单 | 用途 |
| --- | --- |
| `AI超算队列权限申请` | 申请进入新的计算分区。当前 4090、5090、V100 和 `tfg` 提交均因队列权限被拒；需要更大或不同型号的 GPU 时走这个入口。 |
| `AI超算平台配额申请` | 提高账号的 GPU、CPU 或作业数上限。它改变当前 8 GPU、256 CPU、200 jobs 配额，不等同于新增队列权限。 |
| `AI超算存储配额申请` | 提高 `hpc_stor03` 的 1 TB 配额。 |
| `AI超算服务器权限申请` | 申请新的登录、调试、编译或专用服务器资产。 |
| `AI超算软件部署申请` | 申请平台软件、模块或容器环境支持。项目正式镜像可以从这里协调。 |
| `AI超算账户申请`、`AI超算账号注销申请` | 开通或注销账号。 |
| `AI超算基础问题` | 提交日常使用问题。 |

当前最直接的扩容路径：

1. 需要更多并发卡数：提交“AI超算平台配额申请”。
2. 需要 5090、4090 或其他分区：提交“AI超算队列权限申请”。
3. 需要 48 GB 或 80 GB 单卡：先在“AI超算基础问题”确认哪个平台或队列提供该型号，再申请对应的平台配额和队列权限。当前 D6 节点清单中没有发现 48 GB 或 80 GB GPU 分区。
4. 需要项目容器：提交“AI超算软件部署申请”，或向管理员确认内部镜像的构建与推送方式。

旧版 QA 说明权限配置完成后需要重新登录，以刷新用户环境。当前新增权限也应在退出 JumpServer 后重新登录，再用最小作业确认。

## 使用规则

现行操作遵循以下规则：

- 计算任务通过 `vc` 提交。调试机用于管理和诊断，不绕过调度器运行正式作业。
- 每人使用自己的账号，不共享账号和密码。
- 数据传出集群前确认授权范围。实验结果、模型和数据集按项目要求管理。
- 不使用 `sshfs` 挂载集群目录。
- 通过摆渡或 SFTP 传输大于 500 MB 的内容时，先打包再传输。
- 控制小文件数量，定期整理缓存和中间结果。
- 作业的 CPU 线程数与申请的 CPU 数一致。当前账号本身也显示“不允许超配”。

2018 年的规范要求在 `cu01` 编译机上编译软件。当前账号没有该资产，计算环境也已改为容器。现阶段通过内部镜像或“AI超算软件部署申请”准备依赖。

## `vc` 功能索引

| 命令 | 作用 |
| --- | --- |
| `vc submit` | 提交作业。 |
| `vc list` | 列出作业或任务副本。 |
| `vc info` | 查看配额、分区和作业详情。 |
| `vc logs` | 读取任务日志。 |
| `vc top` | 查看运行中任务的 CPU 和内存用量。 |
| `vc exec` | 进入运行中的容器。 |
| `vc describe` | 查看作业错误。 |
| `vc delete` | 取消 Job 或 Job Array。 |
| `vc update` | 调整优先级；支持 `priority-1` 至 `priority-10`。 |

`vc submit` 还支持作业数组、多副本、最少启动副本数、节点选择、任务亲和、RDMA、环境变量、宿主机网络和关闭默认挂载。这些选项面向批量任务或分布式训练，使用前可运行：

```bash
vc submit --help
```

## 每日操作清单

登录后：

```bash
vc info -u
vc list
cd /hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability
```

结束工作前：

```bash
vc list
vc list --show-all -d 1
```

保留仍需运行或排队的作业。确认不再需要的作业后，用 `vc delete -j <Job-ID>` 取消。`Completed` 作业已经释放资源，无需删除。

退出调试机和 JumpServer：

```bash
exit
exit
```

## 待确认事项

- 计费单价、最小计费单位和 `ContainerCreating` 阶段的计费规则。
- 本项目长期使用的容器镜像。
- 单张 A10/3090 运行当前 Qwen2.5-7B、8192 上下文和隐藏状态干预时的峰值显存。

## 内部帮助

- 使用手册：`https://pms.aispeech.com.cn/spaces/v2XJ9ujUqNP`
- 培训视频：`https://bsurl.cn/v2/1RxA3iQ2?showNav=false`
- HPC 问题：钉钉联系穆凯涛。
- VPN 问题：联系何沛文。

## 资料版本

本说明以 `2026-07-20` 的现场实测和当前钉钉工单为准。

用户补充的《AI超算QA-0807》和《AI超算使用规范-beta-v1.1》创建于 2018 年。两份 PDF 使用旧版 Slurm、Lustre、wiener 登录机和旧公网地址；其中 `srun`、`sbatch`、`squeue`、`scancel`、`/mnt/lustre`、默认 2 TB 空间和旧 IP 不适用于当前环境。账号纪律、调度器使用、数据管理、`sshfs` 禁令和大文件打包规则仍纳入本文。
