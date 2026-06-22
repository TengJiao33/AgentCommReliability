# PG40 作用域投影排序预检

日期：2026-06-20

## 核心判断

这次本地预检把 PG40 的下一处瓶颈压清楚了：当前模型候选不只缺预算排序，也缺同一证据卡到多个允许角色的投影。`scope_project_cost_rank_pruned` 在已有五行 card-unit 输出上达到 `5/5`，在 full40 旧 source-ledger 14B 输出上从 `11/40` 提到 `17/40`。

这个结果仍然不能写成公开方法优势。它使用 PG40/SSEAC packet 里显式的 `recipient_scope`，而 PerspectiveGap official full-grid 的 no-gold route 不能读取这类 derived scope 字段；同时 full40 结果仍低于透明贪心 `25/40` 和 utility `0.9825`。

## 做了什么

我新增了一个本地后处理脚本：

```text
scripts/rerank_sseac_pg40_predictions.py
```

它只使用模型候选输出和 packet 中对预测时可见的字段：`card_id`、`recipient_scope`、`verification_state`、`evidence_type`、`cost`、`roles`、模型 `candidate_units` 和模型 `proposed_rejections`。脚本明确不读取 `required_slots`、`acceptable_card_ids`、`expected_final_decision`、`reference_need_sets`、`candidate_need_sets` 或 `role_utilities`。

后处理分两步。第一步把模型已经选中的单卡 candidate unit 投影到该卡允许进入的所有 recipient scope。第二步用 `model_priority - 3.0 * card_cost - 0.25 * projected` 做预算感知排序，并在输出前按 role budget 裁剪，避免 compiler 生成重复 over-budget rejected units。

## 发生了什么

在已有五行 `true_sseac_cardunit` 输出上，原 compiler 行是 `1/5`、coverage `0.6667`、utility `0.8155`。只做 cost-rank pruned 后变成 `2/5`、coverage `0.8148`、utility `0.8755`，已经超过 source-ledger 14B 同五行 utility `0.8498`。加上 scope projection 和预算裁剪后，五行达到 `5/5`、coverage `1.0000`、precision `1.0000`、utility `1.0000`。

在 full40 旧 source-ledger 14B 转换输出上，scope projection + budget prune 把 strict 从 `11/40` 提到 `17/40`，coverage 从 `0.7515` 到 `0.8550`，utility 从 `0.8707` 到 `0.8845`。7B 旧输出也从 `2/40`、utility `0.6034` 到 `4/40`、utility `0.7250`。

## 机制解释

五行失败具体说明了为什么这个后处理有效。原 card-unit 输出经常已经选中了正确卡，但只送给一个 role。例如 `pg_000__seed_1` 里 `f5` 进入 coder，却没有进入 reviewer；`pg_002__seed_1` 里 `f5` 进入 dispatcher，却没有进入 reviewer。scope projection 修的是这个缺口。

budget prune 修的是另一类缺口。模型会把高成本但语义宽泛的卡排在前面，例如 `pg_000__seed_42` 的 reviewer `f1` 或 `pg_002__seed_1` 的 dispatcher `f4`。按成本惩罚后，低成本且被模型认为相关的卡更容易保留下来，compiler 不再靠 over-budget rejection 才把结果裁回来。

## 边界

最重要的边界是字段可用性。PG40/SSEAC packet 里的 `recipient_scope` 是当前诊断的可见字段，但 official full-grid no-gold system route 明确不能读 PG40 `recipient_scope` 或 evaluator-derived fields。所以这次结果证明的是“若能得到可靠 role-card scope，后续排序可以改善”，还没有证明模型能在 official full-grid 上自己推出这个 scope。

第二个边界是强 baseline。full40 14B 后处理到 `17/40`，高于 source-ledger 14B 的 `11/40`，但仍低于 `utility_density_greedy` 的 `25/40`。所以它是一个可用的机制组件候选或 transparent ablation，不是主方法胜利。

第三个边界是输入来源。full40 增益来自旧 source-ledger 转换输出，不是新模型生成输出。它说明后处理值得进入下一轮设计，但不替代真正的 model-facing candidate construction。

## 对论文故事的影响

这次结果把 SSEAC 的当前路线从“写更长 prompt”进一步收窄到“role-card affinity construction + budgeted projection”。它支持 PAL 式分层：模型给出候选卡，确定性层负责 scope projection、预算裁剪和硬约束执行。它也提醒我们，若 scope 是 evaluator-derived，审稿人会把这行读成透明规则 baseline，而非模型方法。

因此当前 A 会路线更像 diagnostic/compiler route。要升级成 method-improvement route，下一步必须让模型或 no-gold system route 预测 role-card affinity，不能读取 PG40 的 derived `recipient_scope`。

## 下一步压力

后续已做一个不读 `recipient_scope` 的 pairwise role-card selector 五行真跑，见 `reports/20260620-pg40-pairwise-selector-limit5.md`。它 parse clean，但 model-only/compiler 都是 `0/5`、utility `0.0000`；模型按表面 actor role 分配，target recipient 错位。

下一步应修 role/recipient interface，或回到 PerspectiveGap official role-assignment arms。新接口仍要先在五行上超过 card-unit compiled 的 `1/5`、utility `0.8155`，再谈 full40 是否接近 source-ledger 14B scope-projection 后处理的 `17/40`、utility `0.8845`。

## 证据路径

| 证据 | 路径 |
| --- | --- |
| run record | `experiments/20260620-local-pg40-scope-rerank-preflight/README.md` |
| 五行 scope projection score | `experiments/20260620-local-pg40-scope-rerank-preflight/summary_scope_project_cost_rank_pruned.md` |
| full40 14B scope projection score | `experiments/20260620-local-pg40-scope-rerank-preflight/summary_source_ledger14_scope_project_cost_rank_pruned_full40.md` |
| full40 7B scope projection score | `experiments/20260620-local-pg40-scope-rerank-preflight/summary_source_ledger7_scope_project_cost_rank_pruned_full40.md` |
| reranker script | `scripts/rerank_sseac_pg40_predictions.py` |
