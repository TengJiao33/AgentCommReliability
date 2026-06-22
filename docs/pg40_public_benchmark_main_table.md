# PG40 公开切片基准测试主表

日期：2026-06-20

机器可筛选版本见 `docs/pg40_public_benchmark_main_table.csv`。更大的数值专表见 `docs/pg40_tight_budget_numeric_main_table.md`。

## 核心判断

PG40 同五行基准测试表已经成表，并新增了一个本地 transparent postprocessor 诊断。当前判断很硬：我方当前模型方法候选强于直接路由和无编译器结构化输出，但仍低于源账本十四十亿参数复用输出，也低于透明贪心和上界。

这张表支持一个有限结论：编译器能把预算控制修回来，候选证据排序、role-card affinity 和跨 role scope projection 是主瓶颈。它暂不支持公开基准上的方法优势结论。

2026-06-20 的 no-scope role-affinity 规则预检给出负结果：不读取 `recipient_scope` 的 hybrid / cost selector 在 full40 model-only 下都是 `0/40`，utility 只有 `0.5243` 到 `0.5467`。同日 GPU7 五行 pairwise role-card selector 也给出负结果：parse clean，prompt leak `0`，但 model-only 和 compiler 都是 `0/5`、utility `0.0000`。这个结果把瓶颈从“缺少模型 pairwise 判断”推进到“当前 no-scope prompt 缺少 role/recipient 转换上下文”。

最危险的风险是切片本身。前五行对透明贪心和廉价可行选择过于友好，所以同五行 `scope_project_cost_rank_pruned` 的 `5/5` 只能作为机制诊断，不能包装成完整 PG40 结论。

## 同五行对齐主表

| 范围 | 行族 | 条件 | 模型 | 严格正确 | 覆盖 | 精确 | 预算通过 | 可行效用 | 原始效用 | 角色命中 | 读法 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 同五行 | 上界 | oracle_utility | deterministic | 5/5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 评分器、输入包和上界闭合 |
| 同五行 | 强透明基线 | utility_density_greedy | deterministic | 5/5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 前五行太友好，不能代表完整胜利 |
| 同五行 | 机制前身 | source_ledger_14b_compiled | Qwen2.5-14B reused | 2/5 | 0.8148 | 0.9565 | 1.0000 | 0.8498 | 0.8498 | 0.7667 | 高精确、低严格正确，仍强于当前我方候选 |
| 同五行 | 直接基线 | pg40_direct_routing | Qwen2.5-14B | 0/5 | 0.1481 | 0.1481 | 0.4000 | 0.0987 | 0.1845 | 0.0000 | 直接提示路由很弱，错在必要碎片拒收和送错角色 |
| 同五行 | 去编译器消融 | true_sseac_cardunit_model_only | Qwen2.5-14B | 0/5 | 0.8148 | 0.6667 | 0.0000 | 0.1803 | 1.2189 | 0.2333 | 模型能找一批相关碎片，但预算崩掉 |
| 同五行 | 我方当前方法候选 | true_sseac_cardunit_compiled | Qwen2.5-14B | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.8155 | 0.8155 | 0.6000 | 编译器修预算，单卡候选改善明显，仍未跨过源账本和透明贪心 |
| 同五行 | 退休诊断 | true_sseac_roleplan_compiled | Qwen2.5-14B | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.7811 | 0.7811 | 0.5000 | 角色计划解释层未继续带来收益，当前不作为我方主行 |
| 同五行 | 透明后处理诊断 | true_sseac_cardunit_scope_project_cost_rank_pruned | Qwen2.5-14B + deterministic | 5/5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 使用 PG40 recipient_scope；只说明 scope projection + budget prune 能闭合五行 |
| 同五行 | 负结果诊断 | pg40_pairwise_selector_model_only | Qwen2.5-14B | 0/5 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | parse clean；按表面 actor role 分配，目标 recipient 错位 |
| 同五行 | 负结果诊断 | pg40_pairwise_selector_compiled | Qwen2.5-14B | 0/5 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | compiler 拦下 14 个越界 assignment，admitted units 为 0 |

## 完整四十行背景

| 范围 | 条件 | 模型 | 严格正确 | 覆盖 | 精确 | 预算通过 | 可行效用 | 角色命中 | 读法 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 四十行 | oracle_utility | deterministic | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 上界 |
| 四十行 | utility_density_greedy | deterministic | 25/40 | 0.9497 | 0.9386 | 1.0000 | 0.9825 | 0.8775 | 当前最强透明基线 |
| 四十行 | eligible_all | deterministic | 13/40 | 0.9112 | 0.9595 | 1.0000 | 0.9731 | 0.9133 | 执行器顺序基线 |
| 四十行 | eligible_cheapest | deterministic | 14/40 | 0.8639 | 0.8439 | 1.0000 | 0.8927 | 0.7242 | 廉价可行选择基线 |
| 四十行 | source_ledger_14b_compiled | Qwen2.5-14B reused | 11/40 | 0.7515 | 0.9270 | 1.0000 | 0.8707 | 0.6842 | 机制前身压力线 |
| 四十行 | source_ledger_14b_scope_project_cost_rank_pruned | Qwen2.5-14B reused + deterministic | 17/40 | 0.8550 | 0.9031 | 1.0000 | 0.8845 | 0.7512 | 透明后处理诊断，仍低于 utility-density greedy |
| 四十行 | no_scope_hybrid_budget_pruned_model_only | deterministic | 0/40 | 0.5000 | 0.4605 | 1.0000 | 0.5243 | 0.2275 | 不读 recipient_scope 的规则 selector，负结果 |
| 四十行 | no_scope_cost_budget_pruned_model_only | deterministic | 0/40 | 0.5858 | 0.3882 | 1.0000 | 0.5467 | 0.0750 | cost-only no-scope selector，仍远低于强基线 |
| 四十行 | no_scope_hybrid_budget_pruned_compiler | deterministic + SSEAC compiler | 1/40 | 0.5000 | 0.7934 | 1.0000 | 0.5243 | 0.2775 | selector 不读 scope，但 compiler 读 scope；只作 gate 诊断 |
| 四十行 | source_ledger_7b_compiled | Qwen2.5-7B reused | 2/40 | 0.4675 | 0.7783 | 1.0000 | 0.6034 | 0.3712 | 弱模型旧输出诊断 |
| 四十行 | source_ledger_7b_scope_project_cost_rank_pruned | Qwen2.5-7B reused + deterministic | 4/40 | 0.6805 | 0.8582 | 1.0000 | 0.7250 | 0.4883 | 弱模型也受益，但仍远低于强基线 |
| 四十行 | utility_aware_source_ledger_compiled | Qwen2.5-14B | 10/40 | 0.7041 | 0.9189 | 1.0000 | 0.8462 | 0.6083 | 新提示经编译器修预算，但仍低于旧源账本十四十亿参数和透明贪心 |

## 机制身份

当前我方方法候选是“模型提出单卡候选证据单元，编译器执行来源、范围、预算、拒收和充分性约束”。在这张表里，它对应 `true_sseac_cardunit_compiled`。

`source_ledger_14b_compiled` 不算当前我方方法候选。它是机制前身加编译器后的复用输出，适合当压力对照。它很重要，因为它告诉我们：当前新机制至少要跨过旧源账本十四十亿参数，否则论文主线很难说成方法进步。

`direct routing` 是同模型直接基线。它回答“直接让模型做路由会怎样”。现在结果很弱，所以它只能说明直接提示不足，不能替代强基线。

`true_sseac_cardunit_model_only` 是去编译器消融。它回答“只让模型按结构输出是否足够”。现在结果显示：结构化输出能找到相关碎片，但预算不可控，因此编译器是必要组件。

`scope_project_cost_rank_pruned` 是透明后处理诊断。它回答“如果模型已经选中某张卡，系统能否根据可见 recipient_scope 把它投影到其他允许角色，并在预算内排序”。它不算当前我方方法候选，因为 official full-grid no-gold route 不能读取 PG40 recipient_scope。

## 撞车测试状态

现在已经有四类基础撞车测试。

| 撞车对象 | 当前状态 | 说明 |
| --- | --- | --- |
| 直接提示 | 已补五行 | 直接路由 `0/5`，可行效用 `0.0987` |
| 去编译器结构化输出 | 已补五行 | 覆盖 `0.8148`，但预算通过 `0.0000` |
| 机制前身源账本 | 已有同五行和四十行 | 同五行可行效用 `0.8498`，四十行 `0.8707`，目前压住我方候选 |
| 透明 scope projection | 已补五行和四十行诊断 | 同五行 `5/5`；四十行 source-ledger 14B 到 `17/40`、utility `0.8845`；依赖 PG40 recipient_scope |
| 透明贪心 | 已有同五行和四十行 | 同五行满分，四十行严格正确 `25/40`、可行效用 `0.9825`，是当前最强压力 |

规则式 no-scope 撞车测试已补，结果是负的：hybrid lexical selector full40 model-only `0/40`、utility `0.5243`，cost-only `0/40`、utility `0.5467`。模型驱动的 no-gold pairwise role-card selector 五行也已补，结果仍是负的：model-only/compiler `0/5`、utility `0.0000`，compiler 拦下 `14` 个 out-of-scope assignment。当前不扩 pairwise full40。

## 下一步压力

下一步不该直接跑当前 pairwise prompt 的 full40。更小的压力点是修 role/recipient interface：要么回到 PerspectiveGap official role-assignment arms，使用官方 scenario context；要么为 PG40 设计 public recipient-context prompt，同时继续禁止读取 `recipient_scope`、need sets、required slots 和 utility gold。

当前 PG40 方法族的诚实结论是：编译器和 scope projection 有诊断价值，但现有 no-scope prompt 没有学会 target recipient assignment。若新接口在五行上恢复 coverage 和 utility，再考虑 PerspectiveGap official full-grid no-gold route。

## 证据路径

| 证据 | 路径 |
| --- | --- |
| 机器表 | `docs/pg40_public_benchmark_main_table.csv` |
| 数字专表 | `docs/pg40_tight_budget_numeric_main_table.md` |
| 强基线和旧源账本转换结果 | `experiments/20260618-local-sseac-v0-pg40-prediction-converter/` |
| 直接路由五行结果 | `experiments/20260619-a8002-pg40-direct-routing-limit5-qwen25-14b/summary_direct.md` |
| 单卡候选五行结果 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b/summary_compiler.md` |
| 去编译器单卡候选五行结果 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b/summary_model_only.md` |
| 角色计划五行结果 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b/summary_compiler.md` |
| scope projection rerank 结果 | `reports/20260620-pg40-scope-projection-rerank-preflight.md`; `experiments/20260620-local-pg40-scope-rerank-preflight/README.md` |
| no-scope role-affinity 规则预检 | `reports/20260620-pg40-no-scope-role-affinity-preflight.md`; `experiments/20260620-local-pg40-no-scope-role-affinity-preflight/README.md` |
| pairwise selector 预飞行 | `reports/20260620-pg40-pairwise-selector-preflight.md`; `experiments/20260620-local-pg40-pairwise-selector-preflight/README.md` |
| pairwise selector 五行真跑 | `reports/20260620-pg40-pairwise-selector-limit5.md`; `experiments/20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b/README.md` |
