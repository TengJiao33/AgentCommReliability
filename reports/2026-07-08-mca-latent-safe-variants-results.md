# MCA 潜状态安全变体结果记录

日期：2026-07-08

## 实验设置

共同设置：

```text
model = Qwen2.5-7B-Instruct
benchmark = math500
agents = 3
latent_rounds = 2
thought_tokens_per_round = 96
private_thought_style = natural
final_max_tokens = 1536
thought_temperature = 0.7
final_temperature = 0.2
top_p = 1.0
steering_layer = 16
steering_scale = 0.05
normalize_steering = true
peer_fusion = mean
peer_message_max_norm = 1.0
same_seed_conditions = true
apply_peer_on_final = false
seed = 42
```

变量：

```text
peer_mode ∈ {residual, per_peer_branch}
split ∈ {mca_disagreement_v1, mca_gold_contrast_v1}
```

`residual`：

```text
message = mean(peer_state - own_state)
```

`per_peer_branch`：

```text
对每个 peer state 单独生成 branch；
把 branch thought 转回 state；
融合 branch states。
```

## 结果表

快照时间：2026-07-08 08:59 +08:00。

| 同伴模式 | 数据子集 | 行数 | 基线正确数 | 潜状态正确数 | 净变化 | BaW_to_C | BaC_to_W | BaC_to_C | BaW_to_W | 状态 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| residual | mca_disagreement_v1 | 50 | 22/50 | 21/50 | -1 | 1 | 2 | 20 | 27 | 完成 |
| residual | mca_gold_contrast_v1 | 50 | 34/50 | 35/50 | +1 | 3 | 2 | 32 | 13 | 完成 |
| per_peer_branch | mca_disagreement_v1 | 50 | 22/50 | 23/50 | +1 | 2 | 1 | 21 | 26 | 完成 |
| per_peer_branch | mca_gold_contrast_v1 | 34 | 23/34 | 22/34 | -1 | 2 | 3 | 20 | 9 | 运行中快照 |

私有思考答案标记计数：

```text
baseline_thought_answer_marker_count = 0
latent_thought_answer_marker_count = 0
```

## 汇总读数

已完成的 50 条 run：

```text
residual / mca_disagreement_v1:
  baseline_correct = 22
  latent_correct = 21
  delta = -1
  BaW_to_C = 1
  BaC_to_W = 2

residual / mca_gold_contrast_v1:
  baseline_correct = 34
  latent_correct = 35
  delta = +1
  BaW_to_C = 3
  BaC_to_W = 2

per_peer_branch / mca_disagreement_v1:
  baseline_correct = 22
  latent_correct = 23
  delta = +1
  BaW_to_C = 2
  BaC_to_W = 1
```

运行中快照：

```text
per_peer_branch / mca_gold_contrast_v1, 34/50:
  baseline_correct = 23
  latent_correct = 22
  delta = -1
  BaW_to_C = 2
  BaC_to_W = 3
```

## 扩大条件检查

预设扩大条件：

```text
BaW_to_C > BaC_to_W
latent_correct > baseline_correct
在 mca_disagreement_v1 上满足以上条件
```

已完成 run 对照：

| 同伴模式 | 数据子集 | BaW_to_C > BaC_to_W | latent_correct > baseline_correct |
|---|---:|---:|---:|
| residual | mca_disagreement_v1 | 否 | 否 |
| residual | mca_gold_contrast_v1 | 是 | 是 |
| per_peer_branch | mca_disagreement_v1 | 是 | 是 |

运行中快照：

| 同伴模式 | 数据子集 | BaW_to_C > BaC_to_W | latent_correct > baseline_correct |
|---|---:|---:|---:|
| per_peer_branch | mca_gold_contrast_v1 | 否 | 否 |

## 后续处理

```text
1. 等 per_peer_branch / mca_gold_contrast_v1 跑完，补全 50 条结果。
2. 在最终结果补齐前，不启动 full MATH500。
3. 若补齐后仍未同时满足扩大条件，则不扩大这两个 peer_mode。
4. 保留 records.jsonl、summary.json、summary.md 作为负向或近零效应记录。
```
