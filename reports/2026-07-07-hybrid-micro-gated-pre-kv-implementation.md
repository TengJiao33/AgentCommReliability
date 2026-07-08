# Hybrid Micro-Gated Pre-KV 实现说明

日期：2026-07-07

## 前置观察

- early-plan Pre-KV 审计包含 `BaW_to_C` 与 `BaC_to_W` 案例。
- raw KV 会携带 partial anchor。

## 实现位置

```text
scripts/run_mca_pre_kv_then_mad.py
```

新增两个可选机制：

```text
visible micro-commitment
first-round selection gate
```

## 1. 可见 micro-commitment

新参数：

```text
--visible-commitment-mode micro
```

当它和 `--pre-state-stage early_plan` 一起启用时，sender prompt 要求生成 compact non-answer sketch：

```text
REPRESENTATION: key variables, structure, or object to model.
FIRST_MOVE: the first equation, invariant, case split, or counting setup to try.
CHECK: one thing a later solver must verify independently.
```

这个 sketch 同时：

- 保留在 sender KV state；
- 作为可见提示展示给 paired Pre-KV receiver。

如果 sketch 含显式答案标记，则不展示：

```text
<answer>
Final answer:
####
\boxed{...}
```

## 2. 第一轮选择门控

新参数：

```text
--first-round-selection-policy pre_kv_unanimous_else_no_channel
```

规则：

```text
只有所有 Pre-KV agents 归一化后一致时，才使用 raw Pre-KV first-round outputs；
否则回退到 no-channel first-round outputs。
```

运行器仍记录 raw metrics：

- no-channel first；
- raw Pre-KV first；
- no-channel + MAD；
- raw Pre-KV + MAD。

另外记录门控指标：

- selected first；
- selected + MAD；
- selected source counts。

`selected + MAD` 不额外跑一遍 costly debate。它在已经生成的 `no-channel+MAD` 和 `raw Pre-KV+MAD` 之间，按 first-round selected source 选择。

## 实验入口

目录：

```text
experiments/20260707-a8002-mca-matrix-hybrid-micro-gated-gpu1-qwen25-7b/
```

脚本：

```text
run_remote_serial_hybrid_micro_gated.sh
```

主 run id：

```text
20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-disagreement-qwen25-7b
20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-gold-contrast-qwen25-7b
```

## 验证

本地单测覆盖：

- structured micro pre-state prompt；
- explicit answer marker 的 visible commitment blocking；
- Pre-KV unanimous gate 接受 unanimous Pre-KV；
- Pre-KV split 时 gate 回退到 no-channel。
