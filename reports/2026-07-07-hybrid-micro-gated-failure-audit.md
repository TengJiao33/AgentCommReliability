# Hybrid Micro-Gated Pre-KV 运行审计

日期：2026-07-07

## Run

```text
20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-disagreement-qwen25-7b
```

快照：

```text
N = 17
BaC_to_C = 7
BaC_to_W = 4
BaW_to_C = 0
BaW_to_W = 6
```

raw hybrid Pre-KV branch 在这个快照里的读数：

```text
BaW_to_C = 0
BaC_to_W = 4
```

门控后的 selected first 读数另见停止记录。

## 主因

sender micro-commitment 在多数样本中未完成。`pre_state_tokens=64` 下，sender 输出常停在字段中间、句子中间或公式中间。

17 条记录审计：

```text
sender outputs = 51
REPRESENTATION present = 51
FIRST_MOVE present     = 28
CHECK present          = 2
likely truncated       = 46
```

receiver 看到的不是完整结构化承诺，而是 partial representation。保留下来的 KV state 也停在未完成 assistant completion 内部。

## 结构问题

Pre-KV receiver 的输入接在以下 sender state 后：

```text
system/user pre-state prompt
assistant generated partial sketch
```

然后 receiver prompt 接在 retained `past_key_values` 后面。sender assistant text 未结束时，receiver output 中可出现 continuation artifact。

证据：geometric-sequence harm case 中，Pre-KV output 直接从公式中间开始：

```text
\cdot 9}{3 \cdot 125} = ...
```

这是续写伪影。

## Harm Cases

### `test/precalculus/990.json`

```text
gold = 6 - 5i
no-channel = 6 - 5i
hybrid Pre-KV = 3 + 3*sqrt(2)/2 - 2i
```

visible sketch 在完整 `FIRST_MOVE` 或 `CHECK` 前被截断。两个 Pre-KV agent 出现同一个 translation error：

```text
z - c = sqrt(2) - (3sqrt(2) - 3)i
```

正确 translation：

```text
z - c = sqrt(2) - 3sqrt(2)i
```

sketch 给了正确高层操作，但没有强制代数检查，receiver 沿着错误 partial trajectory 走。

### `test/algebra/2427.json`

```text
gold = 10
no-channel = 10, 10, 10
hybrid Pre-KV = 5, 10, 5
```

visible sketch 推向 ordinary annuity formula，但没有写到 concrete equation check。两个 Pre-KV agent 解：

```text
3.31 = ((1+r)^3 - 1) / r
```

然后声称 numerical solver 给 `r = 0.05`，这是错的。正确 rate 是 `0.10`。

### `test/algebra/1072.json`

```text
gold = 243/625
no-channel = 243/625, 243/625
hybrid Pre-KV = 27, 27/625, 69.4
```

visible sketch 正确识别 geometric sequence 和 common ratio，但被截断在 `CHECK` 前。两个 Pre-KV agent 进入退化化简循环：

```text
273375/703125 -> 729/1875 -> 27/69.4444 -> ...
```

问题不在 first move，而在 receiver 被 partial trajectory 锚定后缺少算术验证。

### `test/geometry/627.json`

```text
gold = 17
no-channel = 17, 8, 17
hybrid Pre-KV = 7, 7, 17
```

visible sketch 提到 diagonal-midpoint property。两个 Pre-KV agent 选 diagonal pairing，得到 `x=6`，reject 后取 `x=8` 且保留 `y=-1`，最后得到 `7`。

## 观测摘要

当前方法的观测项：

1. `REPRESENTATION/FIRST_MOVE/CHECK` 在 64 tokens 下经常不完整。
2. retained KV 可停在 unfinished assistant completion 内。
3. harm cases 涉及 algebra、numeric solving、vertex pairing。

门控主要改变 non-unanimous Pre-KV cases。

## 后续处理

当前通信对象：

```text
partial sketch + raw unfinished KV
```

下一版只能走这些方向：

- 完整 text micro-commitment，不使用 raw generated-token KV；
- 强制 sender state 在 clean boundary 结束；
- 对 completed sketch 做 read/encoding pass，只取 encoding KV，不取 live generation trajectory。
