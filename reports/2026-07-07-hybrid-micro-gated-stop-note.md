# Hybrid Micro-Gated 运行停止记录

日期：2026-07-07

## 停止的 run

```text
20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-disagreement-qwen25-7b
```

停止的进程链：

```text
1938713 -> 1938714 -> 1938715
```

替换运行：

```text
20260707-a8002-gpu1-mca-latent-rounds-disagreement-qwen25-7b
```

## 停止原因

27 条时的 partial result：

部分结果：

```text
A  no-channel first      = 14/27
B  raw hybrid Pre-KV     = 13/27
G  gated selected first  = 16/27

C  no-channel + MAD      = 13/27
D  raw hybrid + MAD      = 14/27
GD gated selected + MAD  = 15/27
```

raw hybrid Pre-KV branch 与对照：

```text
B - A = -1
D - C = +1
```

selected first 和 selected + MAD 使用 gate 在已生成分支之间选择，没有额外生成新 debate。

## 更深原因

hybrid micro-gated protocol 使用显式字段：

```text
REPRESENTATION
FIRST_MOVE
CHECK
```

这已经偏向可见规划协议，不再是原始的自然 pre-answer 潜状态交换。

审计记录显示，在 `pre_state_tokens=64` 下，sender 输出经常被截断：

```text
sender outputs = 51
REPRESENTATION present = 51
FIRST_MOVE present     = 28
CHECK present          = 2
likely truncated       = 46
```

产生的通信对象是：

```text
partial sketch + raw unfinished KV = high-risk anchor
```

多个 `BaC_to_W` case 涉及算术、顶点配对或代数验证错误。

## 替换方向

替换 runner：

```text
scripts/run_mca_latent_rounds.py
```

它实现多轮潜状态消息传递：

```text
Round 0:
  每个 agent 在答题前私下思考；
  不允许最终答案；
  捕获 latent activation state。

Round r > 0:
  每个 agent 接收 mean(peer activation states)；
  不展示 peer text；
  agent 私下更新 state。

Final:
  到这里才输出最终答案。
```

这个替换方向去掉了 hybrid micro-gated 里的几个干扰：

- 不展示同伴文本；
- 不使用 `REPRESENTATION/FIRST_MOVE/CHECK` 显式字段；
- 不拼接同伴 KV；
- 不让 receiver 续写另一个 agent 的半截 assistant completion。

交换对象变成潜状态激活向量，不是文本提示，也不是 raw generated-token KV。

## 状态

hybrid micro-gated 进程已经 kill。

GPU1 随后用于：

```text
20260707-a8002-gpu1-mca-latent-rounds-disagreement-qwen25-7b
```

新 run 启动时进入 `row 1/221`，并完成该 row 的 baseline private latent rounds。
