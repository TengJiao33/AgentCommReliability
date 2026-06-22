# PG40 Tight-Budget 数字主表

Snapshot date: `2026-06-20`.

机器可筛选版本见 `docs/pg40_tight_budget_numeric_rows.csv`。

## 核心判断

`PG40 tight-budget` 是当前最直接的 SSEAC baseline 压力。它已经有 oracle、透明启发式、旧 source-ledger model output、utility-aware source-ledger prompt、SSEAC compiler 接口，以及一条 true SSEAC prompt 五行诊断结果。现在的结论很硬：**当前还没有 SSEAC 方法优势结果；第一条必须跨过的 baseline 是 `utility_density_greedy` 的 `25/40` strict 和 `0.9825` utility。**

旧 source-ledger 14B 输出经过 compiler 后只有 `11/40` strict、`0.8707` utility。新 utility-aware source-ledger prompt raw 输出预算崩掉，compiler 后是 `10/40` strict、`0.8462` utility。这个结果说明 hard executor 能修预算，但 priority / unit ordering 仍然是关键变量。

2026-06-19 的 direct routing 五行补上了公开切片主表的直接提示基线：strict `0/5`，coverage `0.1481`，precision `0.1481`，budget pass `0.4000`，utility `0.0987`。它是很弱的直接基线，主要错在角色关系、必要碎片拒收和预算控制。

同日的 true SSEAC prompt 五行重跑进一步收窄了问题：compiler 把 budget pass 从 `0.0000` 修到 `1.0000`，但 strict 仍是 `0/5`，coverage 从 `0.7778` 降到 `0.3704`。失败集中在多卡 candidate unit 被 over-budget 整组拒绝，必要证据随之丢失。单卡候选契约复跑后，compiled strict 到 `1/5`，coverage 到 `0.6667`，utility 到 `0.8155`，说明 unit 粒度是实瓶颈，但仍未达到主表标准。角色计划契约复跑没有继续改善：compiled strict 仍是 `1/5`，utility 降到 `0.7811`。

2026-06-20 的本地 scope-projection rerank 预检进一步说明，PG40 当前瓶颈落在 role-card affinity 和预算内投影。五行上，`scope_project_cost_rank_pruned` 把 card-unit 输出从 `1/5` 推到 `5/5`；full40 旧 source-ledger 14B 输出从 `11/40` 推到 `17/40`，utility 从 `0.8707` 到 `0.8845`。这是一条强诊断线，但它使用 PG40/SSEAC packet 中可见的 `recipient_scope`，不能当 PerspectiveGap official full-grid no-gold 方法行。

同日的 no-scope role-affinity 规则预检给出负结果：不读取 `recipient_scope` 的 hybrid lexical selector 在 full40 model-only 下是 `0/40`、utility `0.5243`；cost-only selector 是 `0/40`、utility `0.5467`。随后 GPU7 五行 pairwise role-card selector 也给出负结果：parse clean，但 model-only 和 compiler 都是 `0/5`、utility `0.0000`，compiler 拦下 `14` 个 out-of-scope assignment 后没有 admitted units。它说明当前 no-scope pairwise prompt 会按表面 actor role 分配，缺少把信息送给目标 recipient 的任务上下文。

## 主数字表

| Family | Condition | Model | Strict | Coverage | Precision | Budget pass | Utility | Raw utility | Exact role | 角色 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| oracle | oracle_utility | deterministic | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 上界 |
| transparent | eligible_all + SSEAC compiler | deterministic | 13/40 | 0.9112 | 0.9595 | 1.0000 | 0.9731 | 0.9731 | 0.9133 | executor order baseline |
| transparent | eligible_cheapest + SSEAC compiler | deterministic | 14/40 | 0.8639 | 0.8439 | 1.0000 | 0.8927 | 0.8927 | 0.7242 | cheap-source baseline |
| transparent | utility_density_greedy + SSEAC compiler | deterministic | 25/40 | 0.9497 | 0.9386 | 1.0000 | 0.9825 | 0.9825 | 0.8775 | 当前强 baseline |
| old output | source_ledger_7b_fullprompt_budget_compiled | Qwen2.5-7B reused | 2/40 | 0.4675 | 0.7783 | 1.0000 | 0.6034 | 0.6034 | 0.3712 | 旧输出诊断 |
| old output | source_ledger_14b_fullprompt_budget_compiled | Qwen2.5-14B reused | 11/40 | 0.7515 | 0.9270 | 1.0000 | 0.8707 | 0.8707 | 0.6842 | 旧输出诊断 |
| diagnostic postprocessor | source_ledger_7b + scope projection + budget prune | Qwen2.5-7B reused + deterministic | 4/40 | 0.6805 | 0.8582 | 1.0000 | 0.7250 | 0.7250 | 0.4883 | weak-model projection diagnostic |
| diagnostic postprocessor | source_ledger_14b + scope projection + budget prune | Qwen2.5-14B reused + deterministic | 17/40 | 0.8550 | 0.9031 | 1.0000 | 0.8845 | 0.8845 | 0.7512 | scope projection diagnostic |
| diagnostic negative | no-scope hybrid selector model-only | deterministic | 0/40 | 0.5000 | 0.4605 | 1.0000 | 0.5243 | 0.5243 | 0.2275 | lexical no-scope selector too weak |
| diagnostic negative | no-scope cost selector model-only | deterministic | 0/40 | 0.5858 | 0.3882 | 1.0000 | 0.5467 | 0.5467 | 0.0750 | cost prior cannot solve role-card affinity |
| diagnostic negative | no-scope hybrid selector + compiler | deterministic + SSEAC compiler | 1/40 | 0.5000 | 0.7934 | 1.0000 | 0.5243 | 0.5243 | 0.2775 | compiler reads scope; diagnostic only |
| new output | utility-aware source-ledger raw | Qwen2.5-14B | 0/40 | 0.7781 | 0.5313 | 0.0250 | 0.1473 | 1.2052 | 0.1567 | raw budget failure |
| new output | utility-aware source-ledger + compiler | Qwen2.5-14B | 10/40 | 0.7041 | 0.9189 | 1.0000 | 0.8462 | 0.8462 | 0.6083 | compiler repair diagnostic |

## 五行 true SSEAC prompt 诊断

| Family | Condition | Model | Strict | Coverage | Precision | Budget pass | Utility | Raw utility | Exact role | 角色 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| direct | PG40 direct routing limit5 | Qwen2.5-14B | 0/5 | 0.1481 | 0.1481 | 0.4000 | 0.0987 | 0.1845 | 0.0000 | direct baseline; parse clean but routing weak |
| pilot | true SSEAC prompt no compiler limit5 | Qwen2.5-14B | 0/5 | 0.7778 | 0.6562 | 0.0000 | 0.1803 | 1.1717 | 0.2333 | raw over-budget diagnostic |
| pilot | true SSEAC prompt compiler limit5 | Qwen2.5-14B | 0/5 | 0.3704 | 0.8333 | 1.0000 | 0.4635 | 0.4635 | 0.3333 | compiler repair but coverage collapse |
| pilot | true SSEAC card-unit no compiler limit5 | Qwen2.5-14B | 0/5 | 0.8148 | 0.6667 | 0.0000 | 0.1803 | 1.2189 | 0.2333 | card-level raw still over-budget |
| pilot | true SSEAC card-unit compiler limit5 | Qwen2.5-14B | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.8155 | 0.8155 | 0.6000 | card-level unit improves but not enough |
| pilot | true SSEAC role-plan no compiler limit5 | Qwen2.5-14B | 0/5 | 0.7778 | 0.6774 | 0.0000 | 0.2918 | 1.1330 | 0.3000 | role-plan raw still over-budget |
| pilot | true SSEAC role-plan compiler limit5 | Qwen2.5-14B | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.7811 | 0.7811 | 0.5000 | role-plan retired; below card-unit utility |
| diagnostic postprocessor | card-unit cost-rank pruned limit5 | Qwen2.5-14B + deterministic | 2/5 | 0.8148 | 0.9565 | 1.0000 | 0.8755 | 0.8755 | 0.7000 | cost-aware rerank beats source-ledger同五行 utility |
| diagnostic postprocessor | card-unit scope-project cost-rank pruned limit5 | Qwen2.5-14B + deterministic | 5/5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | uses visible recipient_scope; diagnostic only |
| diagnostic negative | pairwise selector model-only limit5 | Qwen2.5-14B | 0/5 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | parse clean; surface actor roles miss target recipients |
| diagnostic negative | pairwise selector compiler limit5 | Qwen2.5-14B | 0/5 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | compiler blocks 14 out-of-scope assignments; no admitted units |

## 怎么读

第一，PG40 的 scorer 和 pipeline 是闭合的。`oracle_utility` 达到 `40/40`，说明 packet、SSEAC adapter、compiler 和 PG40 scorer 能同表工作。

第二，透明贪心很强。`utility_density_greedy` 是 `25/40` strict、`0.9825` utility，并且 budget pass 是 `1.0000`。它说明 PG40 tight-budget V0 仍然偏向可解释贪心，后续方法行必须把它当主对照。

第三，旧 source-ledger 输出不能代表 Ours。14B reused output 经 compiler 后是 `11/40` strict，低于 `eligible_all` 的 `13/40` 和 `utility_density_greedy` 的 `25/40`。它更像高 precision、低 coverage 的 routing proposal。

第四，新 utility-aware source-ledger prompt 没有解决 priority。raw 输出 raw utility 是 `1.2052`，但 budget pass 只有 `0.0250`，feasible utility 只剩 `0.1473`。compiler 后 budget pass 到 `1.0000`，strict 到 `10/40`，仍低于旧 14B compiled 和透明贪心。

第五，PG40 当前告诉我们：compiler 是必要组件，模型 proposal 还没有成形。下一步不能继续把旧 role-card/source-ledger 输出包进 SSEAC；要让模型直接按 SSEAC schema 输出 `candidate_units`、`priority`、`claimed_slots` 和 `proposed_rejections`。

第六，direct routing 五行说明普通直接提示基线很弱。五行解析干净，distractor leakage 是 `0.0000`，但模型经常拒掉必要碎片、把碎片送错角色，并在复杂行上超预算。这个结果补齐了公开主表基线，但不支持方法优势。

第七，true SSEAC prompt 五行已经说明 schema 稳定性不是当前主瓶颈。五行都能解析，distractor leakage 是 `0.0000`，budget pass 经 compiler 后是 `1.0000`。当前主瓶颈是 unit construction 和 role-specific ranking：多卡 unit 一旦超预算，executor 会整组拒绝；改成单卡 unit 后 coverage 和 utility 大幅回升，但 strict 只有 `1/5`。角色计划契约说明解释型排序不会自动带来更好的 candidate unit，后续应停止在 PG40 上堆解释提示。

第八，scope-projection rerank 把瓶颈再收窄到 role-card affinity。五行上 cost-rank pruned 已经到 `2/5` 和 utility `0.8755`；加入 recipient_scope projection 后到 `5/5`。full40 14B reused output 也从 `11/40` 到 `17/40`，说明这不是纯五行巧合。但它仍低于透明贪心 `25/40`，并且依赖 PG40 中可见的 `recipient_scope`，因此当前只能作为 transparent postprocessor / ablation。

第九，no-scope 规则 selector 失败排除了手写 role keyword / cost prior。纯 model-only 读数最高只有 utility `0.5467`，远低于 source-ledger 14B compiled 的 `0.8707`。这说明 role-card affinity 不能靠简单 role-name lexical rules 或低成本先验解决。

第十，pairwise selector 五行真跑进一步把问题定位到任务接口。模型输出 `22` 个 assignments，parse 全部成功，prompt leak 为 `0`，但 target recipient 全错位，compiler 拦下 `14` 个越界 assignment 后 admitted units 为 `0`。当前 prompt 只让模型看 role 名、预算和卡片文本，会诱导 actor-affinity；下一步需要 official scenario context 或 public recipient-context，不要把这条 no-scope prompt 扩到 full40。

## 与 State Admission V1.1 的关系

`State Admission V1.1` 已经显示 priority + executor 可以修复 direct admitted state 的合法性失败。`PG40 tight-budget` 则给出更严的外部 routing 压力：如果 SSEAC 在 PG40 上仍低于 `utility_density_greedy`，论文主张就要收窄到 diagnostic/compiler discipline。

这两张表合在一起，形成目前最清楚的路线：

| 表 | 当前信号 | 当前边界 |
| --- | --- | --- |
| `State Admission V1.1` | priority + executor 14B 到 `33/40`，7B fallback 到 `31/40` | synthetic packet；强符号 baseline utility 更高；无 downstream |
| `PG40 tight-budget` | compiler 能修预算；oracle/pipeline 闭合；true prompt 五行结构稳定 | 透明贪心 `25/40` 压住 model output；五行 true prompt strict 仍是 `0/5` |
| `PG40 scope projection` | 五行 postprocessor `5/5`；full40 14B reused output `17/40` | 使用 PG40 recipient_scope；不能直接迁移到 official full-grid no-gold |
| `PG40 no-scope selector` | 规则式 no-scope full40 model-only `0/40`，utility `0.5243-0.5467` | 负结果；淘汰手写 lexical / cost selector |
| `PG40 pairwise selector` | 五行 parse clean，但 model-only/compiler 都是 `0/5`、utility `0.0000` | 当前 no-scope prompt 缺少 role/recipient 转换上下文；不扩 full40 |

## 证据路径

| 证据 | 路径 |
| --- | --- |
| SSEAC PG40 converter diagnostic | `reports/20260618-sseac-v0-pg40-prediction-converter.md`; `experiments/20260618-local-sseac-v0-pg40-prediction-converter/README.md` |
| PG40 transparent baselines | `experiments/20260618-local-sseac-v0-pg40-prediction-converter/summary_pg40_*.md` |
| utility-aware source-ledger raw/compiled | `reports/20260618-perspectivegap-tight-budget-source-ledger.md`; `experiments/20260618-a8002-perspectivegap-tight-budget-source-ledger-rotated20-qwen25-14b/summary_raw.md`; `experiments/20260618-a8002-perspectivegap-tight-budget-source-ledger-rotated20-qwen25-14b/summary_budget_compiled.md` |
| pre-tight-budget source-ledger + compiler | `reports/20260618-perspectivegap-budget-compiled-source-ledger.md`; `reports/20260618-perspectivegap-source-ledger-rotated20.md` |
| limit5 SSEAC launch gate | `reports/20260618-sseac-v0-pg40-launch-gate.md`; `experiments/20260618-local-sseac-v0-pg40-launch-gate/README.md` |
| PG40 direct routing limit5 | `reports/20260619-pg40-direct-routing-limit5.md`; `experiments/20260619-a8002-pg40-direct-routing-limit5-qwen25-14b/README.md` |
| true SSEAC prompt limit5 rerun | `reports/20260619-pg40-sseac-limit5-gpu7-rerun.md`; `experiments/20260619-a8002-sseac-v0-pg40-limit5-gpu7-rerun-qwen25-14b/README.md` |
| true SSEAC card-unit limit5 rerun | `reports/20260619-pg40-sseac-cardunit-limit5.md`; `experiments/20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b/README.md` |
| true SSEAC role-plan limit5 rerun | `reports/20260619-pg40-sseac-roleplan-limit5.md`; `experiments/20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b/README.md` |
| scope projection rerank preflight | `reports/20260620-pg40-scope-projection-rerank-preflight.md`; `experiments/20260620-local-pg40-scope-rerank-preflight/README.md` |
| no-scope role-affinity 规则预检 | `reports/20260620-pg40-no-scope-role-affinity-preflight.md`; `experiments/20260620-local-pg40-no-scope-role-affinity-preflight/README.md` |
| pairwise selector preflight | `reports/20260620-pg40-pairwise-selector-preflight.md`; `experiments/20260620-local-pg40-pairwise-selector-preflight/README.md` |
| pairwise selector 五行真跑 | `reports/20260620-pg40-pairwise-selector-limit5.md`; `experiments/20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b/README.md` |

## 论文表位置

| 放置位置 | 内容 |
| --- | --- |
| Main table candidate | oracle、utility-density greedy、source-ledger 14B compiled、SSEAC prompt output |
| Baseline appendix | eligible_all、eligible_cheapest、source-ledger 7B compiled |
| Failure appendix | utility-aware raw output over-budget；compiler repair still below greedy |
| Pipeline appendix | SSEAC converter、compiler、PG40 scorer preflight |

## 下一步压力

1. `Role-plan retired`：当前角色计划契约低于单卡候选契约，不再作为 PG40 当前方向。
2. `Scope projection as transparent ablation`：scope-project + budget-prune 可以作为强诊断后处理，但不能写成 official no-gold 方法行。
3. `Direct baseline filled`：direct routing limit5 已完成；不扩 direct。
4. `No-scope lexical selector retired`：规则式 no-scope selector full40 model-only 是 `0/40`，utility 不到 `0.55`，不再继续调手写 keyword。
5. `Pairwise selector negative`：GPU7 五行已完成，parse clean，但 strict `0/5`、utility `0.0000`，compiler 拦下 `14` 个 out-of-scope assignment。
6. `Main contrast`：下一轮真正模型行不应沿用当前 no-scope pairwise prompt；要么回到 PerspectiveGap official role-assignment arms，要么构造不含 oracle-derived fields 的 public recipient-context prompt。
7. `Near-term action`：停止 pairwise full40；先解决 role/recipient interface，再谈 PG40 扩跑或 official full-grid。

这张表的意义是给 SSEAC 一把硬尺子。现在已经看到一个可用的 deterministic projection 诊断，但模型方法还没有跨过强透明 baseline。
