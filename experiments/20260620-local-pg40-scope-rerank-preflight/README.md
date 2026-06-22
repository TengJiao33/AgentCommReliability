# PG40 Scope Projection Rerank Preflight

日期：2026-06-20

## 状态

`DIAGNOSTIC_LOCAL_POSTPROCESSOR_RESULT`

这是一个不烧 GPU 的本地预检。它复用已有 PG40 五行 `true_sseac_cardunit` 模型输出，以及已有 full40 source-ledger 转换输出，只改变候选证据单元的后处理顺序和 role projection。它不代表新的模型生成结果。

## Preflight Contract

purpose:

验证 PG40 当前瓶颈是否主要来自预算内排序和同一证据卡没有投影到所有允许 recipient，而非 compiler 或 scorer 管道问题。

unit:

PG40 row / PerspectiveGap tight-budget hard evaluation row。

primary_contrast:

`scope_project_cost_rank_pruned` vs 原 `true_sseac_cardunit_compiled` 五行结果。

secondary_contrasts:

`cost_rank_pruned`、source-ledger 14B full40 reused output、source-ledger 7B full40 reused output、utility-density greedy、oracle。

success_signal:

同五行 utility 超过 `true_sseac_cardunit_compiled` 的 `0.8155`，最好超过 source-ledger 14B 同五行 `0.8498`；full40 上相对 source-ledger reused output 有非平凡增益。

failure_signal:

只在五行上改善，full40 没有改善；或改善来自 scorer artifact、needed rejected 伪阳性、gold/references 泄漏。

invalidation_conditions:

后处理读取 `required_slots`、`acceptable_card_ids`、`expected_final_decision`、`reference_need_sets`、`candidate_need_sets`、`role_utilities`；compiler / scorer 路径不兼容；预算裁剪前后产生全局 rejected 噪声导致分数虚高。

expected_artifacts:

本目录下的 reranked predictions、compiled rows、scores、summaries；解释报告 `reports/20260620-pg40-scope-projection-rerank-preflight.md`。

## 方法

新增脚本：

```text
scripts/rerank_sseac_pg40_predictions.py
```

可见字段：

```text
source_cards.card_id
source_cards.recipient_scope
source_cards.verification_state
source_cards.evidence_type
source_cards.cost
roles
model candidate_units
model proposed_rejections
```

禁用字段：

```text
required_slots
acceptable_card_ids
expected_final_decision
reference_need_sets
candidate_need_sets
role_utilities
```

策略：

1. 保留模型已经选中的单卡 candidate units。
2. 可选地把被模型选中的卡投影到该卡 `recipient_scope` 中所有允许角色。
3. 用 `model_priority - 3.0 * card_cost - 0.25 * projected` 排序。
4. 在输出前按 role budget 做预算内裁剪，避免 compiler 生成重复 over-budget rejected units。
5. 再交给原 `compile_sseac_v0.py` 和 `score_sseac_pg40_compiled.py`。

## 五行结果

| 条件 | Strict | Coverage | Precision | Budget pass | Utility | Exact role | 读法 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| true_sseac_cardunit_compiled | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.8155 | 0.6000 | 当前模型候选行 |
| cost_rank_pruned | 2/5 | 0.8148 | 0.9565 | 1.0000 | 0.8755 | 0.7000 | 只改预算排序，已超过 source-ledger 同五行 utility |
| scope_project_cost_rank_pruned | 5/5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 投影 + 预算裁剪闭合五行 |

五行闭合细节：

- `pg_000__seed_1`: reviewer 从 `f6` 修到 `f5`。
- `pg_000__seed_42`: reviewer 从高成本/错误卡修到 `f2,f3`。
- `pg_002__seed_1`: dispatcher 修到 `f3,f5,f6`，reviewer 补 `f5`。
- `pg_002__seed_42`: reviewer 补 `f6,f7`。
- `pg_003__seed_1`: 保持原先 exact。

## Full40 旧输出诊断

| 输入输出族 | 原结果 | scope_project_cost_rank_pruned | 读法 |
| --- | ---: | ---: | --- |
| source-ledger 14B reused | 11/40, utility 0.8707 | 17/40, utility 0.8845 | 有非平凡增益，但仍低于透明贪心 |
| source-ledger 7B reused | 2/40, utility 0.6034 | 4/40, utility 0.7250 | 弱模型也改善，但远未达主表标准 |

full40 14B 关键读数：

```text
strict_pass: 17/40
required_coverage: 0.8550
boundary_precision: 0.9031
budget_pass: 1.0000
utility_ratio: 0.8845
exact_target_role_rate: 0.7512
```

## 诊断

这个结果支持一个窄判断：PG40 的当前 proposal 瓶颈不只在“选哪张卡”，还在“同一张已选卡应该进入哪些 role”以及“预算内如何裁掉高成本候选”。scope projection 和预算裁剪可以显著修复这两点。

这个结果不支持公开方法优势结论。第一，五行本来对透明贪心友好，utility-density greedy 同五行也是 `5/5`。第二，full40 14B 只到 `17/40`，仍低于 utility-density greedy 的 `25/40` 和 utility `0.9825`。第三，策略使用 PG40/SSEAC packet 中显式可见的 `recipient_scope`，不能直接迁移到 PerspectiveGap official full-grid 的 no-gold route。

## 关键产物

| 文件 | 用途 |
| --- | --- |
| `predictions_scope_project_cost_rank_pruned.jsonl` | 五行投影 + 预算裁剪预测 |
| `compiled_scope_project_cost_rank_pruned.jsonl` | 五行 compiler 输出 |
| `scores_scope_project_cost_rank_pruned.jsonl` | 五行 PG40 scorer 输出 |
| `summary_scope_project_cost_rank_pruned.md` | 五行摘要 |
| `predictions_source_ledger14_scope_project_cost_rank_pruned_full40.jsonl` | full40 14B 旧输出投影 + 预算裁剪预测 |
| `scores_source_ledger14_scope_project_cost_rank_pruned_full40.jsonl` | full40 14B scorer 输出 |
| `summary_source_ledger14_scope_project_cost_rank_pruned_full40.md` | full40 14B 摘要 |
| `predictions_source_ledger7_scope_project_cost_rank_pruned_full40.jsonl` | full40 7B 旧输出投影 + 预算裁剪预测 |
| `summary_source_ledger7_scope_project_cost_rank_pruned_full40.md` | full40 7B 摘要 |

## 下一步

下一步不应直接把这行写成 Ours。更合适的推进是把 `scope projection + budget prune` 固定为 transparent postprocessor / ablation，再设计一个不依赖 evaluator-derived `recipient_scope` 的 role-affinity predictor 或 pairwise role-card selector。只有当该 selector 在 full40 上接近或超过透明贪心，才值得进入 PerspectiveGap official full-grid no-gold system route。
