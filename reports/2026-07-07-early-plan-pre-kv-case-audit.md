# Early-Plan Pre-KV 案例审计

## 做法

1. 审计对象是 `mca_disagreement_v1` 上 early-plan Pre-KV 的运行快照。快照包含 18 条 records，每条 record 对应一题。

2. 每题先运行无通道第一轮。3 个接收方各自从自己的解题提示词开始生成，`past_key_values=None`，不接收发送方缓存。

3. 同一题再运行 Pre-KV 第一轮。发送方先读题，并用 `early_plan` 前置提示词生成最多 64 个标记的私有早期草稿。

4. 发送方生成草稿时保留 `past_key_values`。缓存覆盖 sender system/user pre-state prompt，以及 sender assistant 生成出的早期草稿。

5. Pre-KV 接收方不直接看到 sender 文本；它的 receiver prompt 接在 sender past 后面。position ids 从 sender 的 `past_token_count` 之后开始，attention mask 同时覆盖 sender past 和 receiver prompt。

6. 同一题同一 agent 的 no-channel first-round 与 Pre-KV first-round 使用同一个 receiver seed。这样 A/B 差异主要来自 `past_key_values=None` 与接入 sender past。

7. 每题生成后，脚本分别对 no-channel first 和 Pre-KV first 的 3 个接收方答案做多数投票，并用金标判断正确性。

8. 审计按无通道多数答案到 Pre-KV 多数答案的正误转移分类，人工查看 `BaW_to_C` 和 `BaC_to_W` 案例中的 sender 草稿、receiver 输出和可能的锚定位置。

9. 记录同时检查 `sender_answer_tag_count` 和 `sender_gold_leak_count`。人工复核时区分真正答案泄漏与题面数字或中间表达式触发的 suspect。

## 工程细节

- 远端根目录：`/data/xuhaoming/yfy/research_workspace`。
- run id：`20260707-a8002-gpu1-mca-matrix-early-plan-disagreement-qwen25-7b`。
- 记录文件：`experiments/20260707-a8002-gpu1-mca-matrix-early-plan-disagreement-qwen25-7b/math500-qwen25-7b-instruct-mca-pre-kv-then-mad/records.jsonl`。
- 审计快照：18 条 records，审计时 run 仍在运行。
- 前置阶段：`pre_state_stage=early_plan`。
- 前置生成长度：`pre_state_tokens=64`。
- A/B 配对：同一题同一 agent 的 no-channel first-round 和 Pre-KV first-round 使用同一个 receiver seed。
- no-channel 分支：接收方从自己的解题提示词开始，`past_key_values=None`。
- Pre-KV 分支：发送方先生成短私有草稿并保留 `past_key_values`；接收方提示词接在 sender past 后面。
- KV continuation 细节：sender pre-state prompt token count + generated plan tokens 计入 `past_token_count`；receiver prompt tokens append after sender past；position ids 从 `past_token_count` 开始；attention mask 覆盖 sender past 和 receiver prompt。
- 实现检查：未发现 position ids、attention mask 或 past token count 的直接不一致。
- 泄漏检查：`sender_answer_tag_count=0`；`sender_gold_leak_count=5`。人工查看样例中，gold leak suspect 会被题面数字或中间表达式触发。

## 结果

| 指标 | 数值 |
| --- | ---: |
| 快照规模 | 18 records |
| `BaC_to_C` | 7 |
| `BaC_to_W` | 4 |
| `BaW_to_C` | 3 |
| `BaW_to_W` | 4 |
| no-channel first correct | 11/18 |
| Pre-KV first correct | 10/18 |
| Pre-KV - no-channel | -1 |

| 类型 | 案例 | 观测 |
| --- | --- | --- |
| 错到对 | `test/precalculus/1199.json` | sender plan 识别 amplitude、vertical shift、period、phase-shift analysis；Pre-KV majority 转向 `pi` |
| 错到对 | `test/intermediate_algebra/607.json` | sender plan 强调 `sqrt(7)-sqrt(5)` 的共轭表达式；Pre-KV receivers 转向 conjugate / integer-sum 路线 |
| 错到对 | `test/intermediate_algebra/1388.json` | sender plan 从 functional equation 和 `y=0`, `y=1` 代入开始；Pre-KV 输出转向 recurrence structure |
| 对到错 | `test/algebra/2427.json` | sender 草稿写出年金设置但未完成；Pre-KV 接收方被不完整草稿锚定 |
| 对到错 | `test/counting_and_probability/525.json` | Pre-KV 引入互相冲突计数，正确多数被冲散 |
| 对到错 | `test/algebra/1072.json` | sender plan 方向正确但 receiver 数值推导跑偏 |
| 对到错 | `test/geometry/627.json` | Pre-KV 分裂输出并形成错误多数票 |

## 备注

18 条快照中，早期草稿同时出现救回和伤害。被审计的错到对案例集中在 graph phase-shift、conjugate radical、functional equation；被审计的对到错案例集中在 annuity、counting、geometric sequence、geometry。raw KV channel 同时携带 sender prompt、题面、role text 和 partial reasoning；receiver output 可受 partial trajectory anchor 影响。
