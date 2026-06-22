# HSA-v0 Constraint Recall Extended15

日期：2026-06-19

## 核心判断

这次远程十五行真跑给出了目前最强的 HSA 信号。`constraint_recall` 模型输出经过硬准入后达到 `14/15`，再套可见已验证阻断卡补全后达到 `15/15`。多余最终卡片保持 `10`，明显低于全范围信息控制的 `39`。

这个结果可以支撑下一步扩到更多 seed。它仍然是小样本机制证据，不能直接写成规模性结论。

## 运行信息

| 项 | 内容 |
| --- | --- |
| remote | `A800_2:/data/xuhaoming/yfy/research_workspace` |
| local copy | `experiments/20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b/` |
| model | `Qwen2.5-14B-Instruct` |
| served model | `qwen2.5-14b-hsa-v0-sseac` |
| GPU | `7` |
| port | `8074` |
| prompt contract | `constraint_recall` |
| packet | `experiments/20260619-local-hsa-v0-extended15-packet/hsa_v0_packet.jsonl` |
| rows | `15` |
| max model len | `8192` |
| max tokens | `3072` |
| temperature | `0` |

## 命令

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

后置补全：

```powershell
python scripts\augment_hsa_predictions.py --packet experiments\20260619-local-hsa-v0-extended15-packet\hsa_v0_packet.jsonl --predictions experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\predictions.jsonl --out experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\predictions_completion.jsonl --summary-out experiments\20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b\augmentation_summary.json
```

## 主结果

| 行 | 严格正确 | 基础行 | 扰动行 | 槽位召回 | 多余最终卡片 | 强制作答检出 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 模型直出 | `7/15` | `1.0000` | `0.2000` | `0.9389` | `13` | `0.1333` |
| 硬准入 | `14/15` | `0.8000` | `1.0000` | `0.8178` | `10` | `0.6000` |
| 补全后模型直出 | `7/15` | `1.0000` | `0.2000` | `0.9611` | `13` | `0.0667` |
| 补全后硬准入 | `15/15` | `1.0000` | `1.0000` | `0.8400` | `10` | `0.5333` |

透明控制参照：

| 控制 | 严格正确 | 多余最终卡片 |
| --- | ---: | ---: |
| 理想准入 | `15/15` | `0` |
| 只给共享信息 | `10/15` | `39` |
| 全范围信息 | `15/15` | `39` |

## 补全行为

后置补全新增 `2` 个候选单元，涉及 `2` 行，均为 `hb01_hidden_2`：

| packet | card |
| --- | --- |
| `hiddenbench_evacuation_west_city__hb01_base_verified_role_scoped__hsa_v0` | `hb01_hidden_2` |
| `hiddenbench_evacuation_west_city__hb01_west_bridge_unverified__hsa_v0` | `hb01_hidden_2` |

补全修掉的唯一严格错误：

| packet | 修复前 | 修复后 | 缺失卡 |
| --- | --- | --- | --- |
| `hiddenbench_evacuation_west_city__hb01_base_verified_role_scoped__hsa_v0` | `insufficient_evidence` | `West City` | `hb01_hidden_2` |

## 机制读法

硬准入的主要收益在扰动行。模型直出扰动行只有 `2/10`，硬准入把扰动行推到 `10/10`，说明范围、验证状态和充分性规则确实挡住了错误承诺。

后置补全的收益集中在漏卡。它没有把 HB12/HB31 的新增行扩散补入，新增卡只落在已知的 HB01 路径阻断卡上，因此这次没有出现多余最终卡片增长。

## 边界

- 样本仍是 `15` 行，属于强诊断证据。
- 强制作答检出率仍高，补全后硬准入为 `0.5333`。这说明模型本体仍会在证据不足时尝试给出答案，硬准入在承担主要防错工作。
- 当前后置补全只处理可见、已验证、面向最终决策者的阻断卡。它还需要在更多 seed 上检验精度。

## 下一步

1. 扩到 seed gate 推荐的 `12` 个 seed，目标约 `36` 行。
2. 保留同一读数：模型直出、硬准入、补全后硬准入、共享信息下界、全范围信息对照。
3. 若 `36` 行仍保持高严格正确和低多余卡片，再整理主表候选。
