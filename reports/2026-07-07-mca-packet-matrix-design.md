# MCA packet matrix design

日期：2026-07-07

## 目的

本记录定义下一轮 MCA/Pre-KV + MAD 诊断实验的 packet 口径。

当前要回答的问题不是一轮 `MCA-Pre-KV question_only` 能否直接超过两轮 Standard MAD，而是：

```text
在固定第一轮生成参数后，question-only Pre-KV 是否改善第一轮答案；若改善，该改善是否能传递到 MAD 文本讨论后的 final majority。
```

## 已知问题

旧 `MCA-Pre-KV question_only` 完整 run 的结果为 baseline 341/500，Pre-KV final 362/500，净增 +21。

该 +21 不是干净的同口径通道效应，因为旧 run 的 baseline 和 receiver 生成参数不同：

- baseline：`temperature=1.0`，`max_tokens=4096`；
- Pre-KV receiver：`resolve_temperature=0.2`，`resolve_max_tokens=1536`。

最新 `Pre-KV + MAD` bridge run 的第一轮是同口径比较：

- no-channel first：`temperature=0.2`，`first_round_max_tokens=1536`；
- Pre-KV first：`temperature=0.2`，`first_round_max_tokens=1536`。

该 run 的第一轮结果为 no-channel 347/500，Pre-KV 349/500，净增 +2。逐题统计显示 Pre-KV 改变了 138 题，其中救回 36 题、伤害 34 题。

因此，下一轮需要把三类因素拆开：

- 低温短输出本身的稳定化效果；
- question-only KV 的额外贡献；
- 第一轮变化是否能进入 MAD final。

## Packet 类型

### Label-free disagreement packet

该 packet 只使用 Standard MAD 第一轮的可见答案分歧来筛选，不使用 gold，也不使用任何 MCA 输出。

保留条件：

- Standard MAD 第一轮 3 个 agent 的规范化答案中，非空唯一答案数大于等于 2。

分层字段：

- `minority_bearing`：出现 2:1 结构；
- `no_majority_conflict`：三个非空答案互不相同；
- `parse_gap`：存在无法解析答案，同时还有至少一个可解析答案。

该 packet 可用于较干净地诊断：

```text
在 Standard MAD 第一轮已经存在分歧的题上，Pre-KV 是否改变第一轮和 final。
```

解释边界：

- 它不是完整 MATH500；
- 不能直接报告为整体 benchmark accuracy；
- 可以报告为分歧子集上的 conditional effect。

### Gold-stratified diagnostic packet

该 packet 使用 Standard MAD 第一轮 agent 答案与 gold 的关系来筛选。

丢弃：

- 3 个 agent 全对；
- 3 个 agent 全错。

保留：

- `majority_wrong_minority_correct`：majority 错，存在正确 minority；
- `majority_correct_minority_wrong`：majority 对，存在错误 minority；
- `no_majority_mixed`：无多数且正误混合；
- `mixed_other`：其他正误混合。

该 packet 用于诊断救回和伤害来源，尤其是 `BaW_to_C` 与 `BaC_to_W`。

解释边界：

- 该 packet 使用 gold 筛选，因此不是 claim-bearing 主包；
- 它适合解释机制，不适合单独声明超过 Standard MAD。

## 最小矩阵

第一轮先固定低温短输出，构造四个条件：

| 条件 | 第一轮参数 | Pre-KV | MAD 文本讨论 | 读数 |
| --- | --- | --- | --- | --- |
| A | `0.2 / 1536` | 否 | 否 | 低温 no-channel 第一轮 |
| B | `0.2 / 1536` | 是 | 否 | 低温 Pre-KV 第一轮 |
| C | `0.2 / 1536` | 否 | 是 | 低温 no-channel + MAD |
| D | `0.2 / 1536` | 是 | 是 | Pre-KV + MAD |

主比较：

```text
B - A：固定参数下 Pre-KV 是否改善第一轮。
D - C：固定参数下 Pre-KV 是否改善 MAD final。
```

次要比较：

```text
C - A：低温第一轮经过文本讨论后的变化。
D - B：Pre-KV 第一轮经过文本讨论后的变化。
```

## 参数约束

同一矩阵内必须固定：

- 模型路径；
- benchmark row；
- first-round temperature；
- first-round max tokens；
- top-p；
- agents/reviewers；
- prompt family；
- evaluator；
- gold source。

不同条件之间不能让 baseline 和 Pre-KV 使用不同温度或不同输出预算。

## 随机性约束

当前 runner 只在 run 开头设置全局 seed。由于手写 receiver 采样使用 `torch.multinomial`，前面阶段消耗的随机数会影响后续 receiver 采样。

下一轮矩阵若要比较不同条件，应记录并尽量使用局部 seed：

```text
seed = hash(base_seed, row_id, condition, stage, agent_id)
```

在局部 seed 改造完成前，packet 结果只能作为诊断，不应解释为严格同随机轨迹对照。

## 无效条件

以下情况会使结果不能支持机制判断：

- packet 选择使用了 MCA 输出，但结果被解释为泛化效果；
- label-free packet 与 gold-stratified packet 混在一起报告；
- no-channel 与 Pre-KV 的第一轮温度或输出预算不同；
- runner 未记录每题每条件的 seed 或生成顺序；
- packet row 与 Standard MAD 记录无法按 `id` 和 `index` 对齐；
- final 比较缺少同参数 no-channel + MAD 对照。

## 预期产物

Packet 构建产物：

- `data/benchmarks/math500/mca_disagreement_v1/canonical.jsonl`
- `data/benchmarks/math500/mca_disagreement_v1/manifest.json`
- `data/benchmarks/math500/mca_disagreement_v1/README.md`
- `data/benchmarks/math500/mca_gold_contrast_v1/canonical.jsonl`
- `data/benchmarks/math500/mca_gold_contrast_v1/manifest.json`
- `data/benchmarks/math500/mca_gold_contrast_v1/README.md`

审计记录：

- `experiments/20260707-mca-packet-matrix-prep/manifest.json`
- `experiments/20260707-mca-packet-matrix-prep/summary.md`

