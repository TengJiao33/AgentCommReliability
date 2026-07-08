# Pre-KV 结果记录与下一版实现

日期：2026-07-07

## 结果摘要

当前 `question_only` Pre-KV 的同口径读数：

```text
no-channel first = 347/500
Pre-KV first     = 349/500
delta            = +2
```

该版本传递的是 zero-token read-pass KV prefix；sender 没有生成 early plan tokens。

## 已停止的运行

按人工决策，停止 A800_2 GPU1 上的 source-gated matrix run：

```text
20260707-a8002-gpu1-mca-matrix-matched-disagreement-qwen25-7b
```

停止前记录：

```text
packet = mca_disagreement_v1
progress ≈ 93/221 rows
process chain = 4050883 -> 4050909 -> 4050910
after stop GPU1 ≈ 4 MB memory, 0% utilization
```

停止前 partial 读数：

```text
first_round_transition:
BaC_to_C = 35
BaC_to_W = 7
BaW_to_C = 9
BaW_to_W = 42

pre_kv_debate_transition_from_first_round:
PKC_to_C = 42
PKC_to_W = 2
PKW_to_C = 0
PKW_to_W = 49
```

question-only Pre-KV 第一轮 `delta=+2`；进入 MAD 文本讨论后的 final gain 未出现在该 partial 读数中。

## 旧 +21 为什么不再作为证据

旧完整 run：

```text
MCA-Pre-KV question_only:
baseline = 341/500
final    = 362/500
delta    = +21
```

旧 run 的 baseline 和 receiver 生成参数不同：

```text
baseline:
  temperature = 1.0
  max_tokens = 4096

receiver:
  resolve_temperature = 0.2
  resolve_max_tokens = 1536
```

后续同进程 bridge run 固定第一轮参数后：

```text
no-channel first = 347/500
Pre-KV first     = 349/500
delta            = +2
```

旧 `+21` 同时包含温度、输出长度、生成路径和随机轨迹差异。

`question_only` sender 的设置：

```text
pre_state_tokens = 0
generated_tokens = 0
```

sender 没有生成早期计划、局部检查、搜索方向或任何新 token。

实际传递内容：

```text
sender chat prefix containing the problem
-> no generated thought
-> receiver solves the same problem again
```

该 prefix 和 receiver 自己的题目 prompt 高度重复。

## 下一版实现

本地开始改造：

```text
scripts/run_mca_pre_kv_then_mad.py
```

新增：

```text
--pre-state-stage {question_only,early_plan}
--pre-state-tokens
```

`early_plan` 会让 sender 生成短的 pre-answer private plan，再把 live KV 传给 receiver。

每条 record 保存：

```text
sender_state_outputs
sender_answer_tag_count
sender_gold_leak_count
```

summary 写出 sender answer-tag / gold-leak 计数。

新的问题是：

```text
一个不直接广播答案的早期搜索状态，
是否比 zero-token read-pass KV 更能改变 receiver 的解题轨迹？
```

## 下一步判定条件

```text
early-plan 有增益但 sender 泄漏答案：
  标记为 answer leakage case。

early-plan 没有增益且泄漏计数低：
  记录为 KV-prefix low-gain case。

early-plan 有增益且泄漏计数低：
  进入多源门控或 embedding/logit-level 通信测试。
```
