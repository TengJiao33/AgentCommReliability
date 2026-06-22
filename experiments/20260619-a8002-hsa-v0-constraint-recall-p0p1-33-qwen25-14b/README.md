# HSA-v0 P0/P1 33-Row Constraint Recall Run

日期：2026-06-19

## 核心判断

这次三十三行真跑把 HSA 从十五行诊断推进到更接近论文表格的扩样证据。模型直出为 `15/33`，硬准入为 `32/33`，补全后硬准入为 `33/33`。多余最终卡片为 `37`，低于全范围信息控制的 `111`。

这个结果支持当前机制切口：模型负责提出候选证据，硬准入规则负责执行来源、范围、验证状态、拒绝和充分性约束。它已经可以作为强诊断证据登记，但还需要处理 P2 长档案种子，并补同读数基线，才能进入完整主表。

## 运行信息

| 项 | 值 |
| --- | --- |
| run id | `20260619-a8002-hsa-v0-constraint-recall-p0p1-33-qwen25-14b` |
| 远程路径 | `/data/xuhaoming/yfy/research_workspace/experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1-33-qwen25-14b` |
| 本地路径 | `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1-33-qwen25-14b/` |
| 模型 | `Qwen2.5-14B-Instruct` |
| 服务名 | `qwen2.5-14b-hsa-v0-sseac` |
| 机器 | `A800_2` |
| GPU | `7` |
| 端口 | `8074` |
| 输入包 | `experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft/packet/hsa_v0_packet.jsonl` |
| 提示契约 | `constraint_recall` |
| 行数 | `33` |
| 基础行 | `11` |
| 扰动行 | `22` |

## 发射命令

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=constraint_recall GPU_ID=7 PORT=8074 RUN_ID=20260619-a8002-hsa-v0-constraint-recall-p0p1-33-qwen25-14b LIMIT=0 PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft/packet/hsa_v0_packet.jsonl GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 RUN_TIMEOUT=2700 bash scripts/run_hsa_v0_sseac_a8002.sh
```

运行结束后已拉回本地，远程服务已清理，GPU 7 已释放。

## 透明控制

透明控制来自本地输入包门禁：

| 控制 | 严格正确 | 基础行 | 扰动行 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 理想准入 | `33/33` | `1.0000` | `1.0000` | `0.8394` | `0` | `0.0000` |
| 只给共享信息 | `22/33` | `0.0000` | `1.0000` | `0.0818` | `111` | `0.3333` |
| 全范围信息 | `33/33` | `1.0000` | `1.0000` | `0.8394` | `111` | `0.0000` |

## 模型结果

| 路径 | 严格正确 | 基础行 | 扰动行 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 模型直出 | `15/33` | `0.9091` | `0.2273` | `0.9591` | `40` | `0.0909` |
| 硬准入 | `32/33` | `0.9091` | `1.0000` | `0.8273` | `37` | `0.5455` |
| 补全后模型直出 | `15/33` | `0.9091` | `0.2273` | `0.9712` | `40` | `0.0606` |
| 补全后硬准入 | `33/33` | `1.0000` | `1.0000` | `0.8394` | `37` | `0.5152` |

成对差异：

| 对照 | 严格正确变化 | 改善行 | 变差行 | 持平行 |
| --- | ---: | ---: | ---: | ---: |
| 原始硬准入相对模型直出 | `0.4545 -> 0.9697` | `18` | `1` | `14` |
| 补全硬准入相对补全模型直出 | `0.4545 -> 1.0000` | `18` | `0` | `15` |

## 补全诊断

补全策略为 `visible_verified_blocker_completion`。它只新增 `2` 个单元，涉及 `2` 行，新增卡片均为 `hb03_hidden_2`。

| 行 | 效果 |
| --- | --- |
| `hiddenbench_evacuation_east_town__hb03_base_verified_role_scoped__hsa_v0` | 补上 `hb03_hidden_2`，硬准入从 `insufficient_evidence` 变成 `East Town` |
| `hiddenbench_evacuation_east_town__hb03_north_mudslide_no_final_scope__hsa_v0` | 补上一个可见阻断卡，最终仍为 `insufficient_evidence` |

差异明细见 `completion_delta_rows.json`。

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
| `augmentation_summary.json` | 补全摘要 |
| `completion_delta_rows.json` | 补全改变的具体行 |

## 边界

- 这仍是项目内构造的 HSA 包，不能直接声称外部基准上的通用优势。
- P2 的 `baker_2010` 已隔离，需要单独写长档案型证据单元。
- 强制作答检出率仍高，说明模型本体仍有在证据不足时给答案的倾向。
- 多余最终卡片从十五行的 `10` 增加到三十三行的 `37`，但低于全范围控制 `111`。

## 下一步

先补 P2 长档案种子，形成完整 `36` 行包；随后用同一读数补主表所需的模型直出、硬准入、补全后硬准入、共享信息下界、全范围信息对照和理想准入。若 `36` 行仍保持高严格正确且多余卡片远低于全范围控制，再进入更大基准评测。
