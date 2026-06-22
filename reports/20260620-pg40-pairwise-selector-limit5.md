# PG40 Pairwise Selector 五行真跑解释

## 核心判断

pairwise role-card selector 五行真跑给出一个干净负结果：`0/5` strict，utility `0.0000`，parse `5/5` 干净，prompt leak `0`。这次失败不是工程事故；它暴露的是当前 no-scope pairwise prompt 缺少 role/recipient 转换上下文。

我的判断是：不要扩 full40。下一步应修任务接口，或者回到 PerspectiveGap official role-assignment 设定，避免继续在这个 PG40 no-scope prompt 上堆提示词。

## 原本想回答什么

这次运行承接 no-scope 规则 selector 的负结果。手写 lexical / cost selector 在 full40 model-only 下都是 `0/40`，utility 只有 `0.5243-0.5467`；pairwise selector 想验证模型是否能逐对判断 `role, card -> assign`，在不读取 `recipient_scope`、need sets、required slots 或 utility gold 的条件下超过 card-unit compiled 的 `1/5`、utility `0.8155`。

运行编号是 `20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b`。A800_2 GPU 7 跑 Qwen2.5-14B，limit `5`，服务模型名 `qwen2.5-14b-pg40-pairwise-selector`。远程 `py_compile` 和 `bash -n` 都通过，运行结束后 GPU 清干净。

## 实际发生了什么

两条读数都是零：

| 条件 | Strict | Coverage | Precision | Budget pass | Utility | Exact role |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pairwise model-only | 0/5 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |
| pairwise + compiler | 0/5 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 |

triage 更关键：五行全部 parse ok，prompt leak 为 `0`，模型一共输出 `22` 个 raw assignments。compiler 拦下 `14` 个 out-of-scope assignment，最终 admitted units 是 `0`，satisfied slots 是 `0`。

## 为什么这是诊断负结果

模型确实在做选择，但它选择的是表面 actor role。比如 `pg_000__seed_1` 中模型给 `coder f1/f6/f7` 和 `reviewer f3/f4`，期望却是 `coder::f3`、`coder::f5`、`reviewer::f1`、`reviewer::f5`。再如 `pg_003__seed_1`，模型给 `dispatcher f2/f5`、`coder f3`、`reviewer f4/f8/f9`，期望是 `dispatcher::f1/f4/f6`、`coder::f2`、`reviewer::f1/f3/f6`。

这说明 PG40 `source_rotated_scope` 的目标 recipient 不能从 card text 里的角色名直接推出来。当前 prompt 只给 role 名、预算和卡片文本，因此模型会把“卡片说的是谁”当成“卡片该给谁”。compiler 的零 admitted units 是正确拦截，说明 hard gate 在防止越界证据进入最终状态。

## 对论文路线的影响

这个结果削弱了“no-scope pairwise role-card predictor 可以直接接 PG40 tight-budget”的路线。它不削弱 SSEAC compiler 的价值，也不说明 official PerspectiveGap role assignment 没机会，因为 official setting 会给 scenario 和任务上下文，而当前 PG40 prompt 刻意拿掉了 recipient-scope 线索。

PG40 当前仍适合作为失败分析和强压力表。它已经告诉我们三件事：card-level unit 有帮助，scope projection 是关键瓶颈，简单 no-scope lexical / cost / pairwise prompt 都接不住 rotated recipient assignment。

## 下一步压力

下一步不跑 full40 pairwise selector。更小、更尖的动作有两个：

1. 回到 PerspectiveGap official role-assignment arms，用官方 scenario context 生成 role assignment，再 deterministic assignment-to-prompt 并交给 official scorer。
2. 若继续 PG40，先设计 public recipient-context prompt，让模型判断“信息应该给哪个 recipient”，同时仍禁止读取 `recipient_scope`、need sets、required slots 和 utility gold。

这次结果应记为 `DIAGNOSTIC_NEGATIVE_RESULT`。当前最重要的推进不在多烧一轮 GPU；应把 role/recipient interface 改到能回答原问题。
