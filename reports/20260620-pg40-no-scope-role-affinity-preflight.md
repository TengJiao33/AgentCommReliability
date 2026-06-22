# PG40 No-Scope Role-Affinity 预检

## 核心判断

规则式 no-scope role-affinity selector 没有接住 PG40 的当前瓶颈。它不读取 `recipient_scope` 时，full40 上最干净的两条 model-only 读数都是 `0/40`，utility 只有 `0.5243` 到 `0.5467`，明显低于 source-ledger 14B、scope-projection 诊断和透明贪心。

这个结果不是方法失败的最终结论，但它淘汰了一个便宜路线：继续手写 lexical / keyword / cost 规则不值得。下一步应该做模型成对 role-card predictor，并继续禁读 `recipient_scope`、need sets 和 utility gold。

## 做了什么

我新增了 `scripts/select_pg40_role_affinity_no_scope.py`。脚本只读 `roles`、`role_budgets`、`source_cards.card_id`、`source_cards.content`、`source_cards.cost` 和 `candidate_options`，输出 SSEAC `candidate_units`。

这次跑了两类评估。第一类用 `compile_sseac_v0.py --mode model_only`，读 selector 自己按预算裁剪后的纯 no-scope routing 能力。第二类用 `--mode compiler`，把同一个 proposal 交给 SSEAC hard constraints，读 hard scope gate 能补多少。

## 发生了什么

| 条件 | Compile mode | Strict | Coverage | Precision | Budget pass | Utility | Exact role |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| no_scope_hybrid_budget_pruned | model_only | 0/40 | 0.5000 | 0.4605 | 1.0000 | 0.5243 | 0.2275 |
| no_scope_cost_budget_pruned | model_only | 0/40 | 0.5858 | 0.3882 | 1.0000 | 0.5467 | 0.0750 |
| no_scope_hybrid_budget_pruned | compiler | 1/40 | 0.5000 | 0.7934 | 1.0000 | 0.5243 | 0.2775 |
| no_scope_cost_budget_pruned | compiler | 0/40 | 0.5858 | 0.8722 | 1.0000 | 0.5467 | 0.1808 |

主要对照是上一轮 scope-projection 诊断：source-ledger 14B reused output 读取 `recipient_scope` projection 后是 `17/40`、utility `0.8845`。强透明基线 `utility_density_greedy` 是 `25/40`、utility `0.9825`。这次 no-scope 规则 selector 离这两条线都很远。

## 机制解释

结果支持一个窄判断：PG40 当前真正难点落在 role-card affinity。规则 selector 已经能预算通过 `1.0000`，但不知道同一张 fragment 应该送给哪个 role。`cost` 控制比 `hybrid` 规则 utility 更高，说明手写 role keyword 没有捕捉到数据里的角色投影关系。

把 no-scope proposal 交给 compiler 后，precision 明显提升，但 utility 没有提升。这说明 hard scope gate 能清掉错角色和 distractor，却不能凭空补回被 selector 排序漏掉的必要卡。

## 失败和边界

这是一条诊断负结果，不是 PG40 方法线的终局。它只淘汰透明规则式 no-scope selector，不淘汰模型 pairwise predictor。

另一个边界是 unpruned all-pair diagnostic。把所有 role-card pair 都交给 compiler 时，coverage / utility 会接近 `eligible_cheapest`，但 scorer 会记录大量 compiler hard-reject，`needed_rejected` 超过 `5`，strict 变成 `0/40`。这条读数主要说明 hard scope gate 很强，不能当 no-scope predictor 的成功。

## 对论文故事的影响

这次结果让故事更收窄。当前可说的是：SSEAC compiler 和 scope projection 是有诊断价值的执行层，PG40 暴露出的缺口是 proposal 层的 role-card affinity。现在还不能说我们有公开切片方法优势。

更好的贡献形状可能是：把 direct/free-form assignment 的失败拆成 pairwise role-card 判断、预算裁剪和 deterministic execution 三部分，再用 ablation 证明哪一部分解决了 role affinity，哪一部分解决了预算和 rejected noise。

## 后续更新

该报告建议的模型 pairwise role-card selector 已在 `20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b` 中跑完五行。结果为 model-only/compiler `0/5`、utility `0.0000`、parse clean；失败集中在 target recipient 错位，而非 parser 或 GPU 事故。

这条后续结果说明，问题已经从“需要模型 pairwise predictor”推进到“需要 role/recipient interface”。当前 no-scope prompt 只给 role 名、预算和卡片文本，容易诱导模型按表面 actor role 分配。

## 下一步压力测试

下一步应设计 public recipient-context prompt，或回到 PerspectiveGap official role-assignment arms。新接口先用五行验证 coverage 和 utility，过 card-unit compiled 的 `1/5`、utility `0.8155` 后再考虑 `20` 行或 full40。
