# PG40 No-Scope Role-Affinity Preflight

日期：2026-06-20

## 状态

`DIAGNOSTIC_NEGATIVE_LOCAL_SELECTOR`

这是一个本地、不烧 GPU 的规则式 selector 预检。它只使用 PG40/SSEAC packet 中的角色名、角色预算、卡片 id、卡片正文和 cost，显式不读取 `recipient_scope`、`required_slots`、`acceptable_card_ids`、`expected_final_decision`、PG40 need sets 或 utility gold 字段。

## Preflight Contract

purpose:

检验一个透明规则式 no-scope role-card selector 能否替代上一轮 `recipient_scope` projection 诊断中暴露出的 role-card affinity 缺口。

unit:

PG40 full40 row / PerspectiveGap tight-budget hard evaluation row。

primary_contrast:

`no_scope_hybrid_budget_pruned_model_only` vs `source_ledger_14b_scope_project_cost_rank_pruned_full40`。前者不读取 scope，后者读取 PG40 `recipient_scope`。

secondary_contrasts:

`no_scope_cost_budget_pruned_model_only`、预算裁剪后再交给 SSEAC compiler 的 hard-scope-gate variants、`eligible_cheapest`、`utility_density_greedy`。

success_signal:

在 full40 上 no-scope selector 接近或超过 scope-projection 诊断的 `17/40`、utility `0.8845`，并且不靠 rejected 噪声或 gold 字段。

failure_signal:

strict 仍接近 0，utility 明显低于 source-ledger 14B / transparent baselines，或结果主要来自 compiler 读取 `recipient_scope` 后过滤。

invalidation_conditions:

selector 读取 `recipient_scope`、`required_slots`、`acceptable_card_ids`、`expected_final_decision`、`reference_need_sets`、`candidate_need_sets`、`role_utilities`；unpruned all-pair proposals 产生大量 hard-rejected needed cards，导致 scorer rejected channel 被污染。

expected_artifacts:

本目录下 predictions、compiled rows、scores、summaries；解释报告 `reports/20260620-pg40-no-scope-role-affinity-preflight.md`。

## 方法

新增脚本：

```text
scripts/select_pg40_role_affinity_no_scope.py
```

可见字段：

```text
packet_id
roles
role_budgets
source_cards.card_id
source_cards.content
source_cards.cost
candidate_options
```

禁用字段：

```text
source_cards.recipient_scope
required_slots
acceptable_card_ids
expected_final_decision
reference_need_sets
candidate_need_sets
role_utilities
fragments.needed_by
fragments.eligible_by
fragments.target_needed_by
fragments.utility_by_recipient
```

策略：

1. `hybrid`: role name / role token / hand-written keyword / generic cue / cost ranking.
2. `cost`: only low-cost ranking, no text affinity.
3. `model_only` compile mode: selector 自己按预算裁剪，compiler 不用 scope 过滤，用来读纯 no-scope routing 能力。
4. `compiler` compile mode: 同样 selector 输出再交给 SSEAC hard constraints，用来读 scope gate 能补多少。

## Full40 结果

| 条件 | Compile mode | Strict | Coverage | Precision | Budget pass | Utility | Exact role | 读法 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| no_scope_hybrid_budget_pruned | model_only | 0/40 | 0.5000 | 0.4605 | 1.0000 | 0.5243 | 0.2275 | 纯 no-scope selector，没有学会 role-card affinity |
| no_scope_cost_budget_pruned | model_only | 0/40 | 0.5858 | 0.3882 | 1.0000 | 0.5467 | 0.0750 | cost-only 覆盖稍高但角色错配和 distractor 多 |
| no_scope_hybrid_budget_pruned | compiler | 1/40 | 0.5000 | 0.7934 | 1.0000 | 0.5243 | 0.2775 | hard scope gate 提升 precision，但没有恢复 coverage |
| no_scope_cost_budget_pruned | compiler | 0/40 | 0.5858 | 0.8722 | 1.0000 | 0.5467 | 0.1808 | scope gate 清掉 distractor，但 selector 排序仍弱 |

对照：

| 条件 | Strict | Utility | 读法 |
| --- | ---: | ---: | --- |
| source_ledger_14b_compiled | 11/40 | 0.8707 | 旧模型管线压力线 |
| source_ledger_14b_scope_project_cost_rank_pruned | 17/40 | 0.8845 | 使用 recipient_scope 的诊断后处理 |
| eligible_cheapest | 14/40 | 0.8927 | 透明廉价可行基线 |
| utility_density_greedy | 25/40 | 0.9825 | 当前强透明基线 |

## Invalidated Diagnostic

`cost_unpruned + compiler` 和 `hybrid_unpruned + compiler` 会把所有 role-card pair 交给 compiler。它们的 coverage / utility 看起来接近透明 baseline，但 scorer 会把大量 compiler hard-reject 写进 rejected channel：

```text
cost_unpruned + compiler: strict 0/40, utility 0.8927, needed_rejected 5.4500
hybrid_unpruned + compiler: strict 0/40, utility 0.8446, needed_rejected 5.5250
```

这两个读数不作为方法结果。它们只说明：如果把所有 pair 都抛给 hard-scope gate，scope 过滤本身能恢复一部分可行 utility，但 rejected 噪声会破坏 strict，并且这不等于 no-scope role-affinity predictor。

## 诊断

规则式 no-scope selector 被压下去了。它能守住预算，但无法可靠判断卡片应该给哪个角色；cost-only 甚至比 hybrid 文本规则更高 utility，说明手写 role keyword 没有抓住 PG40 的真实角色投影关系。

这个结果把下一步从“继续调规则”改成“做模型成对 role-card selector”。新的 selector 必须只读公开输入表面，例如 role names、fragment text、cost 和 possibly prompt arms 输出，不读 `recipient_scope` 或 need-set gold。

## 关键产物

| 文件 | 用途 |
| --- | --- |
| `predictions_hybrid_budget_pruned_full40.jsonl` | no-scope hybrid selector 输出 |
| `compiled_hybrid_budget_pruned_model_only_full40.jsonl` | 纯 no-scope model-only 编译 |
| `scores_hybrid_budget_pruned_model_only_full40.jsonl` | 纯 no-scope scorer 输出 |
| `summary_hybrid_budget_pruned_model_only_full40.md` | 纯 no-scope 摘要 |
| `compiled_hybrid_budget_pruned_compiler_full40.jsonl` | no-scope proposal + hard scope gate |
| `summary_hybrid_budget_pruned_compiler_full40.md` | hard scope gate 摘要 |
| `predictions_cost_budget_pruned_full40.jsonl` | cost-only selector 输出 |
| `summary_cost_budget_pruned_model_only_full40.md` | cost-only 纯 no-scope 摘要 |
| `summary_cost_budget_pruned_compiler_full40.md` | cost-only + hard scope gate 摘要 |

## 下一步

不要把规则式 no-scope selector 写成 Ours。下一步应做一个可审计的 pairwise role-card predictor：逐对判断 `role, fragment -> should_assign`，输出 confidence / rationale / abstain，再用 deterministic budget prune 和 official scorer 读数。晋级门槛仍是 full40 上先超过 `17/40`、utility `0.8845`，再向 `utility_density_greedy` 的 `25/40`、utility `0.9825` 靠近。
