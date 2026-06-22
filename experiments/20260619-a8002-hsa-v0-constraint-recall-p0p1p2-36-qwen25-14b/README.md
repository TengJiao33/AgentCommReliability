# HSA-v0 P0/P1/P2 36-Row Constraint Recall Run

日期：2026-06-19

## 核心判断

这次三十六行真跑把 P2 长档案种子纳入 HSA。模型直出为 `16/36`，硬准入为 `34/36`，阻断补全后硬准入为 `35/36`，支撑型窄补全后硬准入为 `36/36`。扰动行在硬准入和两种补全后都是 `24/24`，说明范围、验证和证据不足规则仍然稳住。

这个结果支持 HSA 继续作为主机制线推进，但也要把支撑型窄补全标成诊断后处理。它修掉了长档案中的 Roberts 正向支撑卡漏召回，extra final cards 从 `40` 到 `42`，仍低于全范围控制 `195`。

## 运行信息

| 项 | 值 |
| --- | --- |
| run id | `20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b` |
| 远程路径 | `/data/xuhaoming/yfy/research_workspace/experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b` |
| 本地路径 | `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b/` |
| 模型 | `Qwen2.5-14B-Instruct` |
| 服务名 | `qwen2.5-14b-hsa-v0-sseac` |
| 机器 | `A800_2` |
| GPU | `7` |
| 端口 | `8076` |
| 输入包 | `experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl` |
| 提示契约 | `constraint_recall` |
| 行数 | `36` |
| 基础行 | `12` |
| 扰动行 | `24` |
| max model len | `16384` |
| max tokens | `3072` |

## 发射命令

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=constraint_recall GPU_ID=7 PORT=8076 RUN_ID=20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b LIMIT=0 PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl GPU_MEMORY_UTILIZATION=0.80 MAX_MODEL_LEN=16384 MAX_TOKENS=3072 RUN_TIMEOUT=3600 bash scripts/run_hsa_v0_sseac_a8002.sh
```

运行结束后已拉回本地，远程服务已清理，GPU 7 已释放。

## 透明控制

透明控制来自本地输入包门禁：

| 控制 | 严格正确 | 基础行 | 扰动行 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 理想准入 | `36/36` | `1.0000` | `1.0000` | `0.8477` | `0` | `0.0000` |
| 只给共享信息 | `24/36` | `0.0000` | `1.0000` | `0.0750` | `129` | `0.3333` |
| 全范围信息 | `36/36` | `1.0000` | `1.0000` | `0.8477` | `195` | `0.0000` |

## 模型结果

| 路径 | 严格正确 | 基础行 | 扰动行 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 模型直出 | `16/36` | `0.9167` | `0.2083` | `0.9271` | `43` | `0.1667` |
| 硬准入 | `34/36` | `0.8333` | `1.0000` | `0.8038` | `40` | `0.5833` |
| 补全后模型直出 | `16/36` | `0.9167` | `0.2083` | `0.9458` | `43` | `0.1389` |
| 阻断补全后硬准入 | `35/36` | `0.9167` | `1.0000` | `0.8225` | `40` | `0.5556` |
| 支撑型补全后模型直出 | `16/36` | `0.9167` | `0.2083` | `0.9711` | `45` | `0.0833` |
| 支撑型补全后硬准入 | `36/36` | `1.0000` | `1.0000` | `0.8477` | `42` | `0.5278` |

成对差异：

| 对照 | 严格正确变化 | 改善行 | 变差行 | 持平行 |
| --- | ---: | ---: | ---: | ---: |
| 原始硬准入相对模型直出 | `0.4444 -> 0.9444` | `20` | `2` | `14` |
| 补全硬准入相对补全模型直出 | `0.4444 -> 0.9722` | `20` | `1` | `15` |
| 支撑型补全硬准入相对支撑型补全模型直出 | `0.4444 -> 1.0000` | `20` | `0` | `16` |

## 补全诊断

阻断补全策略为 `visible_verified_blocker_completion`。它新增 `5` 个单元，涉及 `5` 行，没有解析错误。

| 新增卡片 | 涉及行 | 作用 |
| --- | ---: | --- |
| `hb03_hidden_2` | `2` | 修东镇基础行漏掉的 North Hill 阻断卡，并提高一个扰动行召回 |
| `hb05_hidden_stevens_no_fundraising` | `3` | 补 task 5 的 Stevens fundraising 阻断卡 |

阻断补全后仍失败的行是 `hiddenbench_baker_2010__hb05_base_verified_profile_scoped__hsa_v0`。缺失卡片为：

```text
hb05_hidden_roberts_collaborative
hb05_hidden_roberts_diversity
hb05_hidden_roberts_excellent_teacher
hb05_hidden_roberts_federal_grant
hb05_hidden_roberts_research_productivity
```

支撑型窄补全策略为 `visible_verified_blocker_and_decision_support_completion`。它在模型已经选择具体答案时，补可见、已验证、面向最终决策者、且匹配模型答案的支撑卡。该策略把 task 5 基础行修为 `Roberts`，同时保持两个 task 5 扰动行为 `insufficient_evidence`。

## 产物

| 文件 | 用途 |
| --- | --- |
| `predictions.jsonl` | 原始模型输出 |
| `predictions_completion.jsonl` | 补全后模型输出 |
| `compiled_model_only.jsonl` | 模型直出编译视图 |
| `compiled_compiler.jsonl` | 硬准入编译视图 |
| `compiled_completion_model_only.jsonl` | 补全后模型直出编译视图 |
| `compiled_completion_compiler.jsonl` | 补全后硬准入编译视图 |
| `scores_model_only.jsonl` | 模型直出评分 |
| `scores_compiler.jsonl` | 硬准入评分 |
| `scores_completion_model_only.jsonl` | 补全后模型直出评分 |
| `scores_completion_compiler.jsonl` | 补全后硬准入评分 |
| `paired_delta.md` | 原始成对差异 |
| `paired_delta_completion.md` | 补全后成对差异 |
| `paired_delta_support_completion.md` | 支撑型补全后成对差异 |
| `augmentation_summary.json` | 补全摘要 |
| `support_augmentation_summary.json` | 支撑型补全摘要 |
| `completion_delta_rows.json` | 补全改变的具体行 |
| `support_completion_delta_rows.json` | 支撑型补全改变的具体行 |

## 边界

- 这是项目内 HSA 包，尚不能直接替代公开大基准结果。
- task 5 使用 profile-level 拆卡，评估压力更强，但金标证据要求也更硬。
- 支撑型窄补全目前是本地后处理诊断，进入主方法前需要复核是否会在其他包上过度补卡。
- 强制作答检出率仍高，说明模型本体仍倾向在证据不足时给具体答案。

## 下一步

支撑型窄补全已经在旧 33 行包和 15 行包上重放：33 行保持 `33/33`、extra final cards `37`；15 行保持 `15/15`、extra final cards `10`。下一步应把该规则写成明确方法组件，并准备更大包或同读数主表。
