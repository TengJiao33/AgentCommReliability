# SSEAC-v0 PG40 Prediction Converter 诊断

日期：2026-06-18

## 核心判断

SSEAC-v0 已经能接入 PG40 tight-budget slice 的已有预测，并回到 PG40 指标体系评分。这个进展把方法从文档推进到可比较 pipeline，但当前诊断没有给出方法优势证据。

最重要的读数是：`utility_density_greedy` 仍然强于旧 `source_ledger_14b_fullprompt_budget_compiled`。因此下一步不能继续复用旧 source-ledger 输出来代表 Ours，应该直接写 SSEAC prompt，让模型输出 priority、candidate_units 和 claimed_slots。

## 做了什么

我新增了两个脚本：

- `scripts/convert_perspectivegap_predictions_to_sseac.py`
- `scripts/score_sseac_pg40_compiled.py`

前者把 PG40 role-card 预测转成 SSEAC `candidate_units`。后者把 SSEAC compiled output 转回 PG40 scorer 能读的 role-card response，并报告 tight-budget 指标。

本地诊断产物在：

- `experiments/20260618-local-sseac-v0-pg40-prediction-converter/README.md`

## 结果

| Condition | Strict | Coverage | Precision | Budget pass | Utility ratio | Exact target role |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `oracle_utility` | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `eligible_all` after SSEAC compiler | 13/40 | 0.9112 | 0.9595 | 1.0000 | 0.9731 | 0.9133 |
| `eligible_cheapest` after SSEAC compiler | 14/40 | 0.8639 | 0.8439 | 1.0000 | 0.8927 | 0.7242 |
| `utility_density_greedy` after SSEAC compiler | 25/40 | 0.9497 | 0.9386 | 1.0000 | 0.9825 | 0.8775 |
| `source_ledger_7b_fullprompt_budget_compiled` | 2/40 | 0.4675 | 0.7783 | 1.0000 | 0.6034 | 0.3712 |
| `source_ledger_14b_fullprompt_budget_compiled` | 11/40 | 0.7515 | 0.9270 | 1.0000 | 0.8707 | 0.6842 |

## 解释

oracle 达到 `40/40` strict，说明 adapter、compiler、PG40 scorer 三者的 plumbing 已经打通。这个结果主要证明评测入口可用。

`utility_density_greedy` 达到 `25/40` strict 和 `0.9825` utility ratio，说明 PG40 tight-budget v0 对简单透明贪心仍偏友好。它会成为第一轮必须跨过的强 baseline。

`source_ledger_14b_fullprompt_budget_compiled` 只有 `11/40` strict。它的 coverage 是 `0.7515`，precision 是 `0.9270`，说明旧 source-ledger 输出更像高精度、低覆盖的 routing proposal。SSEAC-v0 若只包一层 compiler，无法自然追上透明贪心。

`eligible_all` 经 compiler 后 `budget_pass=1.0000`，但 strict 只有 `13/40`。这说明 hard executor 能压住预算，却会把必要事实按照输入顺序裁掉。priority 是关键变量，不能靠 executor 自动解决。

## 边界

这次没有启动新模型实验。所有输入来自已有 PG40 baseline / compiled source-ledger predictions。

PG40 的 SSEAC `downstream_ok` 是 synthetic routing-complete slot 检查，不对应真实任务 accuracy。

当前结果不能支持 SSEAC-v0 优于 baseline。它支持的是下一步实验设计：必须让模型按 SSEAC schema 直接输出 priority 和 claimed_slots，然后再与 `utility_density_greedy`、`source_ledger_model_only`、`priority_plus_executor` 同表比较。

## 下一步压力

下一步应做一个小样本 SSEAC prompt runner：

```text
输入：SSEAC PG40 packet 中的 SourceCard、role budgets、required slot descriptions。
输出：option_states、candidate_units、priority、claimed_slots、proposed_rejections。
规模：先 5-10 rows，不开大跑。
主对比：SSEAC prompt vs source_ledger_14b_fullprompt_budget_compiled vs utility_density_greedy。
成功信号：coverage 接近或高于 source_ledger 14B，precision/budget 保持，utility ratio 接近或超过 utility_density_greedy。
失败信号：SSEAC prompt 仍低于透明贪心，或只是减少分发导致 coverage 下降。
```

如果这个小样本没有过 `utility_density_greedy`，PG40 tight-budget v0 应继续作为 pipeline smoke 和 baseline pressure；方法 claim 需要转向更硬的 dependency / evidence-slot packet 或 Hidden-State Admission downstream slice。
