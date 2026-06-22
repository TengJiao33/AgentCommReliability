# HSA-v0 Extended15 Launch Gate

日期：2026-06-19

## 核心判断

下一步可以迈大一点，但应当把大步压在 HSA 十五行真跑上。这个实验已经具备发射条件：十五行包透明控制闭合，提示泄漏检查通过，评分器和编译器已在同一包上跑通。

本次没有启动远程模型运行。原因是 A800_2 上其他用户仍有活跃任务，虽然七号卡空闲，但零、一、二、三号卡有占用。按当前资源规则，先不抢跑。

## 实验目的

回答一个具体问题：同一个模型在十五行 HSA 包上，能否提出足够干净的候选证据，使硬准入和后置补全同时取得高严格正确率，并且多余最终卡片明显低于全范围信息控制。

## 实验单位

单位是 HSA 行。当前包共有 `15` 行：`5` 个基础行，`10` 个扰动行，覆盖 HiddenBench 任务 `1`、`10`、`11`、`12`、`31`。

## 主对照

| 对照 | 作用 |
| --- | --- |
| 模型直出 | 看模型直接写最终状态时的承诺错误和漏证据 |
| 硬准入 | 看编译器能否挡住范围、验证状态和充分性错误 |
| 后置补全 | 看可见已验证阻断卡补全能否修漏卡 |

## 已闭合控制

| 控制 | 严格正确 | 基础行 | 扰动行 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 理想准入 | `15/15` | `1.0000` | `1.0000` | `0.8400` | `0` | `0.0000` |
| 只给共享信息 | `10/15` | `0.0000` | `1.0000` | `0.1956` | `39` | `0.3333` |
| 全范围信息 | `15/15` | `1.0000` | `1.0000` | `0.8400` | `39` | `0.0000` |

提示泄漏检查：`15` 行，平均提示长度 `8185.2` 字符，评价专用字段命中 `0`。

## 成功线

强成功：

- 后置补全后严格正确达到 `15/15`；
- 基础行达到 `5/5`；
- 扰动行达到 `10/10`；
- 多余最终卡片显著低于全范围信息的 `39`，理想上不超过 `20`；
- 强制作答不高于九行诊断的同类水平。

可用信号：

- 后置补全后严格正确达到 `13/15` 或 `14/15`；
- 失败行能归因到候选证据召回、优先级或补全规则；
- 多余最终卡片没有接近 `39`。

## 失败线

需要暂停扩跑的情况：

- 严格正确接近只给共享信息控制，也就是约 `10/15`；
- 扰动行出现大量强制作答；
- 严格正确上升伴随多余最终卡片接近 `39`；
- 任一提示或输出路径发现评价专用字段泄漏；
- 失败来自脚本、同步、端口或模型服务异常时，只记录为工程失败。

## 远程发射前检查

当前远程检查：

```text
A800_2: 10-116-90-20
time: Fri Jun 19 14:18:53 CST 2026
gpu0: used 10615 MiB, util 43
gpu1: used 69595 MiB, util 0
gpu2: used 15287 MiB, util 71
gpu3: used 14207 MiB, util 0
gpu7: used 4 MiB, util 0
```

结论：七号卡空闲，但整机仍有人在跑任务。本次不启动。

下次启动前重新执行：

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "hostname; date; nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits"
```

## 必须同步

```powershell
scp scripts/run_hsa_v0_sseac_a8002.sh scripts/run_hsa_v0_sseac_openai_compatible.py scripts/compile_sseac_v0.py scripts/score_hsa_v0_compiled.py scripts/augment_hsa_predictions.py A800_2:/data/xuhaoming/yfy/research_workspace/scripts/
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "WORK=/data/xuhaoming/yfy/research_workspace; mkdir -p `$WORK/experiments/20260619-local-hsa-v0-extended15-packet"
scp experiments/20260619-local-hsa-v0-extended15-packet/hsa_v0_packet.jsonl A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-extended15-packet/
```

## 远程运行命令

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=constraint_recall \
GPU_ID=7 \
PORT=8074 \
RUN_ID=20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b \
LIMIT=0 \
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-extended15-packet/hsa_v0_packet.jsonl \
GPU_MEMORY_UTILIZATION=0.75 \
MAX_MODEL_LEN=8192 \
MAX_TOKENS=3072 \
RUN_TIMEOUT=1800 \
bash scripts/run_hsa_v0_sseac_a8002.sh
```

如果端口被占用，换一个空闲端口再跑。

## 后置补全命令

运行目录拉回后，在本地执行：

```powershell
python scripts\augment_hsa_predictions.py --packet experiments\20260619-local-hsa-v0-extended15-packet\hsa_v0_packet.jsonl --predictions experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\predictions.jsonl --out experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\predictions_completion.jsonl --summary-out experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\augmentation_summary.json

python scripts\compile_sseac_v0.py --packet experiments\20260619-local-hsa-v0-extended15-packet\hsa_v0_packet.jsonl --predictions experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\predictions_completion.jsonl --mode model_only --out experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\compiled_completion_model_only.jsonl --summary-out experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\compile_summary_completion_model_only.json

python scripts\compile_sseac_v0.py --packet experiments\20260619-local-hsa-v0-extended15-packet\hsa_v0_packet.jsonl --predictions experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\predictions_completion.jsonl --mode compiler --out experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\compiled_completion_compiler.jsonl --summary-out experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\compile_summary_completion_compiler.json
```

随后用 `scripts/score_hsa_v0_compiled.py` 分别评分模型直出、硬准入、补全模型直出和补全硬准入。

## 大步之后

若十五行信号干净，下一步直接扩到 seed gate 推荐的 `12` 个种子，形成约 `36` 行包。若十五行信号不干净，先做逐行错误归因，暂不扩样本。
