# MCA 潜状态安全变体结果记录

日期：2026-07-08

## 做法

1. 运行读取两个数据子集：`mca_disagreement_v1` 前 50 题和 `mca_gold_contrast_v1` 前 50 题。

2. 每个子集分别运行 residual 和 per-peer branch 两种同伴模式，共形成四个 run。

3. 每个 run 都使用 3 个智能体、2 轮私有思考、每轮 96 个标记。私有思考提示为 natural，thought temperature 为 0.7，最终答案 temperature 为 0.2。

4. 基线条件中，智能体只生成自己的私有思考和最终答案，不接收同伴向量。

5. 潜状态条件中，第 0 轮先生成私有思考；之后脚本从私有思考构造第 16 层状态向量，并在下一轮私有思考中注入同伴消息。

6. residual 模式使用同伴状态减本智能体状态后的均值；per-peer branch 模式先对每个同伴状态生成短分支，再把分支转为状态向量后融合。

7. 所有同伴消息都经过归一化和范数 1.0 裁剪。注入时把向量乘以 0.05 加到第 16 层当前最后标记隐藏状态。

8. 基线和潜状态条件默认使用匹配种子。最终答案阶段不注入同伴向量，只读取本智能体私有思考轨迹。

9. 每题完成后，脚本对 3 个智能体最终答案做多数投票，并记录 baseline correct、latent correct、majority tie、答案标记审计和正误转移。

10. 四个 run 完成后，报告按同伴模式和数据子集汇总正确数、净变化、救回数和伤害数。

## 工程细节

- 模型为 `Qwen2.5-7B-Instruct`，benchmark 为 `math500`。
- 数据子集为 `mca_disagreement_v1` 和 `mca_gold_contrast_v1`，每个组合取 50 题。
- 固定参数为 `latent_rounds=2`、`thought_tokens_per_round=96`、`final_max_tokens=1536`、`thought_temperature=0.7`、`final_temperature=0.2`、`top_p=1.0`。
- steering 参数为 `steering_layer=16`、`steering_scale=0.05`、`normalize_steering=true`、`peer_fusion=mean`、`peer_message_max_norm=1.0`。
- 随机性参数为 `same_seed_conditions=true`、`seed=42`。
- `residual` 模式把同伴状态减去本智能体状态后取均值。
- `per_peer_branch` 模式对每个同伴状态单独生成短私有分支，再把分支思考转为状态并融合。
- 最终核查时间为 2026-07-08 16:31 +08:00。
- 远端产物保存在四个 run 目录：`20260708-a8002-gpu1-mca-latent-residual-disagreement50-qwen25-7b`、`20260708-a8002-gpu1-mca-latent-residual-gold-contrast50-qwen25-7b`、`20260708-a8002-gpu1-mca-latent-per-peer-branch-disagreement50-qwen25-7b`、`20260708-a8002-gpu1-mca-latent-per-peer-branch-gold-contrast50-qwen25-7b`。

## 结果

| 同伴模式 | 数据子集 | 行数 | 基线正确数 | 潜状态正确数 | 净变化 | `BaW_to_C` | `BaC_to_W` | `BaC_to_C` | `BaW_to_W` |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| residual | `mca_disagreement_v1` | 50 | 22/50 | 21/50 | -1 | 1 | 2 | 20 | 27 |
| residual | `mca_gold_contrast_v1` | 50 | 34/50 | 35/50 | +1 | 3 | 2 | 32 | 13 |
| per_peer_branch | `mca_disagreement_v1` | 50 | 22/50 | 23/50 | +1 | 2 | 1 | 21 | 26 |
| per_peer_branch | `mca_gold_contrast_v1` | 50 | 34/50 | 32/50 | -2 | 2 | 4 | 30 | 14 |

| 审计项 | 数值 |
| --- | ---: |
| baseline 私有思考答案标记计数 | 0 |
| latent 私有思考答案标记计数 | 0 |
| 净变化范围 | -2 到 +1 |

四个 50 题 run 均已完成。两个同伴模式在目标分歧子集上没有形成稳定增益；结果作为近零或负向效应记录保留。

## 备注

本轮保留 `records.jsonl`、`summary.json` 和 `summary.md`。`mca_gold_contrast_v1` 使用金标筛选，不能与 `mca_disagreement_v1` 混作同一个总体读数。
