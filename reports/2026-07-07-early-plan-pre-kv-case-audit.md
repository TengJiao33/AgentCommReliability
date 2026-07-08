# Early-Plan Pre-KV 案例审计

日期：2026-07-07

## 审计对象

```text
remote root = /data/xuhaoming/yfy/research_workspace
run_id = 20260707-a8002-gpu1-mca-matrix-early-plan-disagreement-qwen25-7b
records = experiments/20260707-a8002-gpu1-mca-matrix-early-plan-disagreement-qwen25-7b/math500-qwen25-7b-instruct-mca-pre-kv-then-mad/records.jsonl
snapshot = 18 records, run still active
```

## 结果

18 条快照读数：

```text
BaC_to_C = 7
BaC_to_W = 4
BaW_to_C = 3
BaW_to_W = 4

A no-channel first correct = 11
B pre-kv first correct     = 10
B - A = -1
```

早先小快照读数为 `+3`；18 条快照读数为 `B - A = -1`。

## 实现检查

A/B 是 paired seed。每个 agent 的 no-channel 和 Pre-KV first-round 使用同一个 receiver seed，主要差异就是 sender KV state。

sender 当前设置：

```text
pre_state_stage = early_plan
pre_state_tokens = 64
```

这不是旧的 question-only zero-token state。sender 会先生成短私有计划，保留 `past_key_values`，receiver prompt 接在这个 past state 后面。

KV continuation 使用：

- sender pre-state prompt token count + generated plan tokens；
- receiver prompt tokens appended after sender past；
- position ids 从 `past_token_count` 开始；
- attention mask 覆盖 sender past 和 receiver prompt。

实现路径检查未发现 position ids、attention mask 或 past token count 的直接不一致。

## 泄漏检查

answer tag 计数：

```text
sender_answer_tag_count = 0
sender_gold_leak_count  = 5
```

`sender_gold_leak_count` 是 parser-suspect 计数。人工看过的样例里，它会被题面数字或中间表达式触发。

## 救回案例

### `test/precalculus/1199.json`

```text
gold = \pi
no-channel majority = 3*pi/2
Pre-KV majority = pi
transition = BaW_to_C
```

sender plan 识别了 amplitude、vertical shift、period、phase-shift analysis。Pre-KV 输出都转向 `pi`。这是正例：early plan 把 receiver 推向正确 graph-parameter representation。

### `test/intermediate_algebra/607.json`

```text
gold = 13535
no-channel majority = 13419
Pre-KV majority = 13535
transition = BaW_to_C
```

sender plan 强调 `sqrt(7)-sqrt(5)` 的共轭表达式。Pre-KV receivers 转向 conjugate / integer-sum 路线，三个 agent 中两个得到 `13535`。

### `test/intermediate_algebra/1388.json`

```text
gold = 1,-2
no-channel majority = (0, 1)
Pre-KV majority = (1, -2)
transition = BaW_to_C
```

sender plan 从 functional equation 和 `y=0`, `y=1` 代入开始。Pre-KV 输出转向 recurrence structure，两个 agent 产出 gold set。

### `test/algebra/2427.json`

```text
gold = 10
no-channel majority = 10
Pre-KV majority = 8
transition = BaC_to_W
```

no-channel 全对。sender plan 写出年金设置但没算完。Pre-KV 接收方被不完整计划锚定，数值利率算错。

### `test/counting_and_probability/525.json`

```text
gold = 144
no-channel majority = 144
Pre-KV majority = 360
transition = BaC_to_W
```

Pre-KV 引入互相冲突的计数：

```text
360, 144, 576
```

正确 majority 被冲散。

### `test/algebra/1072.json`

```text
gold = 243/625
no-channel majority = 243/625
Pre-KV majority = 1736/25
transition = BaC_to_W
```

sender plan 方向正确，识别 common ratio；receiver 后续数值推导跑偏。正确 high-level plan 不保证 KV continuation 忠实执行。

### `test/geometry/627.json`

```text
gold = 17
no-channel majority = 17
Pre-KV majority = 7
transition = BaC_to_W
```

Pre-KV 分裂输出并形成错误多数票。这是 partial-plan anchor + noise，不是解析器问题。

## 观测摘要

当前 18 条快照中：

```text
BaW_to_C = 3；
BaC_to_W = 4；
first-round B - A = -1；
被审计的 BaW_to_C case 中包含 graph phase-shift、conjugate radical、functional equation；
被审计的 BaC_to_W case 中包含 annuity、counting、geometric sequence、geometry。
```

候选解释：

```text
raw KV channel 同时携带 sender prompt、题面、role text、partial reasoning；
receiver output 可受 partial plan anchor 影响。
```

## 下一步证据对象

需要对完整 `mca_disagreement_v1` 做 paired case packet：

- 全部 `BaW_to_C`；
- 全部 `BaC_to_W`；
- sender early-plan snippets；
- no-channel 和 Pre-KV first-round answers；
- 人工标签：`useful_plan`, `partial_anchor`, `wrong_anchor`, `no_visible_relation`。

后续 packet 统计 `useful_plan`、`partial_anchor`、`wrong_anchor`、`no_visible_relation` 四类标签的占比。
