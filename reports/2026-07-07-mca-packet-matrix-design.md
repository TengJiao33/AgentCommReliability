# MCA Packet Matrix 构建记录

日期：2026-07-07

## 做法

1. Packet Matrix 先从 Standard MAD 第一轮记录中构建诊断子集，而不是直接在完整 MATH-500 上筛结果。

2. `mca_disagreement_v1` 只使用 Standard MAD 第一轮答案分歧。脚本读取每题 3 个智能体的规范化答案，保留非空唯一答案数大于等于 2 的题，不读取金标，也不读取任何 MCA 输出。

3. `mca_disagreement_v1` 给保留题标注分层字段。若出现 2:1 结构，记为 `minority_bearing`；若三个非空答案互不相同，记为 `no_majority_conflict`；若存在解析失败且还有可解析答案，记为 `parse_gap`。

4. `mca_gold_contrast_v1` 使用 Standard MAD 第一轮答案与金标关系筛选。脚本丢弃 3 个智能体全对或全错的题，保留正误混合样本。

5. `mca_gold_contrast_v1` 对保留题标注 `majority_wrong_minority_correct`、`majority_correct_minority_wrong`、`no_majority_mixed` 和 `mixed_other`。

6. 两个 packet 写出 `canonical.jsonl`、`manifest.json` 和 README，使矩阵 run 直接读取固定子集。

7. 矩阵固定模型、题目、第一轮温度、第一轮输出预算、top-p、agent 数、reviewer 数、prompt family、evaluator 和 gold source。

8. A 条件生成低温无通道第一轮。接收方从自己的题目提示词开始生成，不接收 Pre-KV。

9. B 条件生成低温 Pre-KV 第一轮。发送方先产生 question-only KV，接收方接入该 KV 后生成第一轮答案。

10. C 条件把 A 的第一轮文本输出交给 MAD 第二阶段，生成无通道第一轮后的 final。

11. D 条件把 B 的第一轮文本输出交给 MAD 第二阶段，生成 Pre-KV 第一轮后的 final。

12. A/B 比较 Pre-KV 是否改变第一轮，D/C 比较 Pre-KV 第一轮输出进入文本 MAD 后是否改变最终多数答案。

## 工程细节

- 旧 `MCA-Pre-KV question_only` 完整 run 的读数为 baseline `341/500`，Pre-KV final `362/500`，净增 `+21`。
- 旧 run 的 baseline 使用 `temperature=1.0` 和 `max_tokens=4096`；Pre-KV receiver 使用 `resolve_temperature=0.2` 和 `resolve_max_tokens=1536`。这使旧 `+21` 同时包含参数差异和通道差异。
- 同口径 bridge run 固定第一轮参数为 `temperature=0.2`、`first_round_max_tokens=1536`，第一轮结果为 no-channel `347/500`，Pre-KV `349/500`。
- 同口径 bridge run 中，Pre-KV 改变了 138 题第一轮答案，其中 `BaW_to_C=36`，`BaC_to_W=34`。
- `mca_disagreement_v1` 只使用 Standard MAD 第一轮 3 个智能体的规范化答案。保留条件是非空唯一答案数大于等于 2。
- `mca_disagreement_v1` 的分层字段包括 `minority_bearing`、`no_majority_conflict` 和 `parse_gap`。
- `mca_gold_contrast_v1` 使用 Standard MAD 第一轮答案与金标的关系筛选，丢弃 3 个智能体全对或全错的题。
- `mca_gold_contrast_v1` 的分层字段包括 `majority_wrong_minority_correct`、`majority_correct_minority_wrong`、`no_majority_mixed` 和 `mixed_other`。
- 矩阵条件 A/B/C/D 固定模型、题目、第一轮温度、第一轮输出预算、top-p、agent 数、reviewer 数、prompt family、evaluator 和 gold source。
- A/B 比较 Pre-KV 是否改变第一轮；D/C 比较 Pre-KV 第一轮输出进入文本 MAD 后是否改变最终多数答案；C/A 和 D/B 记录文本讨论对两个第一轮条件的第二阶段影响。

## 结果

| 条件 | 第一轮参数 | Pre-KV | MAD 文本讨论 | 读数含义 |
| --- | --- | --- | --- | --- |
| A | `0.2 / 1536` | 否 | 否 | 低温无通道第一轮 |
| B | `0.2 / 1536` | 是 | 否 | 低温 Pre-KV 第一轮 |
| C | `0.2 / 1536` | 否 | 是 | 低温无通道第一轮后接 MAD |
| D | `0.2 / 1536` | 是 | 是 | Pre-KV 第一轮后接 MAD |

| 产物 | 路径 |
| --- | --- |
| 分歧包数据 | `data/benchmarks/math500/mca_disagreement_v1/canonical.jsonl` |
| 分歧包 manifest | `data/benchmarks/math500/mca_disagreement_v1/manifest.json` |
| 分歧包说明 | `data/benchmarks/math500/mca_disagreement_v1/README.md` |
| 金标对照包数据 | `data/benchmarks/math500/mca_gold_contrast_v1/canonical.jsonl` |
| 金标对照包 manifest | `data/benchmarks/math500/mca_gold_contrast_v1/manifest.json` |
| 金标对照包说明 | `data/benchmarks/math500/mca_gold_contrast_v1/README.md` |
| 构建审计 manifest | `experiments/20260707-mca-packet-matrix-prep/manifest.json` |
| 构建审计摘要 | `experiments/20260707-mca-packet-matrix-prep/summary.md` |

## 备注

Packet 结果只用于诊断样本结构和通道影响，不代表完整 MATH500 accuracy。label-free packet 与 gold-stratified packet 的筛选依据不同，报告时需要分开呈现。
