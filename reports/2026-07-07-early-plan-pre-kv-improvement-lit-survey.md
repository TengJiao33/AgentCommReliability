# Early-Plan Pre-KV 改进方向与文献信号

日期：2026-07-07

这份记录把 early-plan Pre-KV 的 case audit 和相邻 latent communication 文献连起来，目的是决定下一步改什么。

## 当前 case pattern

快照：

```text
run_id = 20260707-a8002-gpu1-mca-matrix-early-plan-disagreement-qwen25-7b
records = 18

BaC_to_C = 7
BaC_to_W = 4
BaW_to_C = 3
BaW_to_W = 4
B - A = -1
```

BaW_to_C cases：

- graph phase-shift：Pre-KV 把 receivers 推到 `pi`；
- conjugate radical：Pre-KV 让两个 receivers 得到 `13535`；
- functional equation：Pre-KV 让两个 receivers 得到 `1,-2`。

BaC_to_W cases：

- annuity interest：no-channel 全对，Pre-KV 推到较低 rate；
- circular seating：no-channel majority 正确，Pre-KV 打散计数；
- geometric sequence：sender 识别 common ratio，但 Pre-KV 数值跑偏；
- parallelogram：no-channel majority 正确，Pre-KV 翻错 majority。

当前 case audit 中没有发现 answer-tag 泄漏。

## 文献信号

### 1. latent communication 已经是明确研究对象

`Beyond Tokens: A Unified Framework for Latent Communication in LLM-based Multi-Agent Systems`

链接：

```text
https://arxiv.org/html/2606.05711
```

信号：

```text
latent communication 可以交换 embeddings、hidden states、KV caches；
fusion 可以是 concat、prepend、addition、learned cross-attention、adapter。
```

对我们的动作：

```text
raw KV prepending 作为一个候选设计点保留。
```

### 2. state delta

`Augmenting Multi-Agent Communication with State Delta Trajectory`

链接：

```text
https://arxiv.org/html/2506.19209v1
```

信号：

```text
hidden-state 的变化量比绝对状态更能表示 hidden reasoning movement。
```

对我们的动作：

```text
sender raw KV 混有 prompt、题目、role text、partial reasoning；
delta over generated plan tokens 可能更接近真正思考移动。
```

### 3. latent receiver 需要 adapter 或 alignment

`Enabling Agents to Communicate Entirely in Latent Space`

链接：

```text
https://arxiv.org/html/2511.09149v1
```

信号：

```text
last hidden states 经过 lightweight self-attention 和 projection adapter 后再交给 receiver。
```

对我们的动作：

```text
直接把 sender KV 嫁接到 receiver pass 是 under-aligned；
同模型 agent 也可能需要 receiver-side interpretation transform。
```

### 4. hybrid text-latent 是自然修复方向

`HyLaT: Efficient Multi-Agent Communication via Hybrid Latent-Text Protocol`

链接：

```text
https://arxiv.org/pdf/2605.25421
```

信号：

```text
latent 用来传 dense cognitive content；
短文本用来传 critical signals。
```

对我们的动作：

```text
visible commitment 可作为 receiver 侧可检查对象。
```

### 5. continuous reasoning 文献提示 distribution mismatch

`Coconut`

```text
https://arxiv.org/abs/2412.06769
```

`Latent Thoughts Tuning`

```text
https://arxiv.org/html/2602.10229v1
```

信号：

```text
hidden states 作为 continuous thought tokens 会遇到 instability 和 distribution mismatch。
```

对我们的动作：

```text
harm cases 中出现 sender plan direction 与 receiver numerical continuation 分离。
```

### 6. KV sharing 需要 guard

`LCGuard`

```text
https://arxiv.org/abs/2605.22786
```

`When Latent Agents Lie`

```text
https://arxiv.org/html/2606.28958v1
```

信号：

```text
shared KV 需要记录 corruption / manipulation 条件下的行为。
```

对我们的动作：

```text
KV state 必须 gated、transformed、audited。
```

## 改进选项

### Option A: Hybrid KV + visible micro-commitment

保留 64-token early-plan KV，同时展示短 non-answer commitment：

```text
REPRESENTATION: key variables / structure
FIRST_MOVE: equation, invariant, or counting setup
CHECK: one thing later solver must verify
```

receiver prompt：

```text
You receive a private latent state from another solver and a short visible non-answer sketch.
Use it as a hint, but verify every algebraic or counting step independently.
If the sketch is incomplete or inconsistent, solve from scratch.
```

目标：

- rescue cases 保留搜索方向；
- harm cases 让 receiver 先检查 textual object；
- no-channel unanimous cases 不轻易被 Pre-KV 推翻。

### Option B: Consensus gate

不要总用 Pre-KV majority：

```text
if no_channel is unanimous and pre_kv is not unanimous:
    keep no_channel
elif pre_kv is unanimous and no_channel is not unanimous:
    use pre_kv
else:
    use normal majority / debate
```

这个可以 posthoc 算，是最低成本实验。

### Option C: Delta-state channel

用 generated plan tokens 上的 hidden/KV delta：

```text
delta_t = hidden_t - hidden_{t-1}
```

只注入 selected deltas 或 compressed trajectory，减少 prompt/context ballast。

### Option D: Layer and length ablation

小矩阵：

```text
pre_state_tokens: 16, 32, 64, 128
state object: full KV, generated-token-only KV/delta, last-hidden-state summary
receiver rule: always use, consensus-gated
```

只跑 `mca_disagreement_v1`，看 `BaW_to_C` vs `BaC_to_W`。

### Option E: Sender-role specialization

让三个 sender 产生不同非答案计划：

```text
agent 0: algebraic/formula setup
agent 1: boundary/check/invariant
agent 2: alternative solution route
```

现在 sender 经常产生相似 plan start，容易放大同一个 wrong anchor。

## 事后门控结果

20 条 live snapshot：

```text
A no-channel = 12/20
B Pre-KV    = 12/20
B - A       = 0
```

三个门控：

```text
gate1:
  use B if B is unanimous and A is not unanimous;
  keep A if A is unanimous and B is not unanimous;
  otherwise use B.

gate2:
  use B only if B is unanimous;
  otherwise keep A.

gate3:
  keep A if A is unanimous and B is not unanimous;
  otherwise use B.
```

结果：

```text
gate1 = 12/20
gate2 = 13/20
gate3 = 12/20
```

`gate2` 是该 snapshot 中唯一提高正确数的门控：

```text
gate2 = 13/20
A no-channel = 12/20
B Pre-KV = 12/20
```

## 后续实验选择

下一步候选：

1. hybrid KV + visible non-answer commitment + gate；
2. delta-state channel；
3. layer / length ablation。
