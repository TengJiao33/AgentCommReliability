# A 会方向下一步推进计划

Snapshot date: `2026-06-18`.

## 核心判断

下一步要把模板细读转成两个实物：一张能跑的 paper-facing baseline table，以及一个两页论文骨架。当前不宜继续扩宽 benchmark，也不宜直接冲 closed-source leaderboard。最小有效动作是让 `PAL + Sparse MAD + Decomposed Prompting` 的模仿规则进入 PG40 / HSA / State Admission 的实验设计。

## 未来 72 小时目标

### 1. 冻结论文 claim v0

暂定 claim：

```text
In role-specific multi-agent communication, free-form message exchange entangles evidence discovery with source/scope/budget admission. We propose a source-scoped evidence admission pipeline where LLMs propose candidate evidence units and priorities, while a deterministic compiler enforces admission constraints before downstream use.
```

这句话决定后续实验只服务一个对象：`source-scoped evidence admission`。新想法只有能填进这句话，才进入当前队列。

### 2. 冻结主表行

每个主 benchmark 至少包含这些行：

| Row family | Required condition |
| --- | --- |
| direct | direct answer / direct admitted state |
| free communication | free-form exchange / all-to-all |
| structured text | role-list / source-ledger |
| model-only admission | structured output without compiler |
| compiler route | model candidate units + deterministic compiler |
| transparent baseline | utility-density greedy / all-scoped / eligible-all |
| oracle/control | oracle admissible / oracle assignment |

这张表直接模仿 PAL：必须能区分 prompt/schema 的收益和 compiler/interpreter 的收益。

### 3. 先补 PG40 和 HSA 的 missing rows

PG40 当前缺口：

| 缺口 | 目的 |
| --- | --- |
| `structured_no_compiler` | 判断模型直接输出 SSEAC state 是否仍然过预算或乱收 |
| `SSEAC_model_units + compiler` | 判断 compiler 是否修复 budget / precision / strict |
| `SSEAC_oracle_units + compiler` | 判断上限是否在 unit proposal 还是 compiler |
| `cost/admitted-card metrics` | 对齐 Sparse MAD 的 quality-cost 读法 |

HSA 当前缺口：

| 缺口 | 目的 |
| --- | --- |
| `SSEAC_model_units + compiler` | 判断 base rows 能否超过 shared-only |
| `structured_no_compiler` | 判断模型是否会全收 evidence 或 forced commitment |
| `extra final cards` | 防止 all-scoped 投机策略 |
| `perturb abstention` | 判断 insufficient-evidence 是否稳定 |

### 4. 写两页 paper skeleton

两页骨架已落盘为 `docs/sseac_paper_skeleton_v0.md`。它先固定五段：

1. Problem: free-form agent communication hides admission failure.
2. Mechanism: source/scope/budget/rejection constraints need executable admission.
3. Method: LLM candidate units + deterministic compiler + admitted public state.
4. Experiments: PG40, HSA, State Admission with same-backbone baseline ladder.
5. Boundary: current claim depends on beating strong transparent baselines or at least showing compiler-diagnostic value.

## 决策门

| 结果 | 论文方向 |
| --- | --- |
| SSEAC 在 PG40 或 HSA 至少一条超过强 transparent baseline | 写成 method improvement paper |
| SSEAC 没超过强 baseline，但 compiler 稳定修 budget/leakage/forced commitment | 写成 diagnostic/compiler discipline paper |
| schema 不稳或 unit proposal 太弱 | 暂停扩跑，回到 unit construction 和 handler decomposition |
| 只有 closed-source frontier 分高 | 作为 reference ceiling，不改变主线 |

## 立即动作顺序

1. 检查 PG40/HSA runner 是否已经能输出 `structured_no_compiler` 和 `compiled` 两套 artifacts。已完成，见 `reports/20260618-sseac-pal-ablation-interface.md`。
2. 若缺 runner 分支，先补 runner / scorer 接口，不启动模型。已补齐 `compile_sseac_v0.py --mode model_only|compiler` 与 smoke queue 分支。
3. PG40/HSA 小样本模型行已跑出：PG40 三轮 limit5 仍低于强基线，HSA full9 有 `3/9 -> 7/9` 成对信号。
4. 先修 HSA 候选证据召回；PG40 只在有预算感知排序机制时重启。
5. 用 triage 结果更新 `docs/sseac_paper_skeleton_v0.md`，决定是否扩 HSA 或回到 unit construction。
