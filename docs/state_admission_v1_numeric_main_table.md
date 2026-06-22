# State Admission V1.1 数字主表

Snapshot date: `2026-06-18`.

机器可筛选版本见 `docs/state_admission_v1_numeric_rows.csv`。

## 核心判断

`State Admission V1.1` 是当前最接近“经典机制改善”的自有结果族。它给出的主信号很清楚：Qwen2.5-14B 直接生成 admitted state 时是 `0/40`；同一模型改成 priority proposal，再交给 deterministic executor 执行预算、closure、reject 和 visibility 后，到 `28/40`；离线换成 `pair_group_primary` executor 后到 `33/40`。

这个结果有方法味，但还不能当 SOTA。强符号 `group_density_global` baseline 已经有 `32/40` strict 和 `0.9666` utility；14B pair-group-primary 虽然 strict 多 1 行，但 utility 只有 `0.9014`。所以当前最稳的 claim 是：**把 LLM 输出对象从 admitted state 改成 executable priority，再用规则层执行合法准入，可以显著修复 direct state generation 的合法性失败。**

## 主数字表

| Family | Condition | Model | Strict | Coverage | Precision | Global budget | Utility | Closure | 角色 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| oracle | oracle | deterministic | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 上界 |
| naive | eligible_all | deterministic | 0/40 | 1.0000 | 0.3019 | 0.0000 | 0.0000 | 0.0000 | 过度准入下界 |
| item | item_density_per_role | deterministic | 0/40 | 0.8160 | 0.3833 | 0.0000 | 0.0000 | 1.1500 | 单片段失败 |
| item | item_density_global | deterministic | 0/40 | 0.5644 | 0.3274 | 1.0000 | 0.0411 | 2.0000 | 单片段失败 |
| bundle | bundle_density_global | deterministic | 14/40 | 0.5092 | 0.3739 | 1.0000 | 0.4492 | 0.0000 | bundle baseline |
| bundle | cheapest_bundle_global | deterministic | 14/40 | 0.4847 | 0.3496 | 1.0000 | 0.4243 | 0.0000 | bundle baseline |
| strong baseline | group_density_global | deterministic | 32/40 | 0.9018 | 1.0000 | 1.0000 | 0.9666 | 0.0000 | 强符号 baseline |
| direct | direct_default | Qwen2.5-14B | 0/40 | 1.0000 | 0.4025 | 0.0000 | 0.0000 | 0.0250 | direct state failure |
| direct | direct_budget_first | Qwen2.5-14B | 0/40 | 0.7914 | 0.4464 | 0.1000 | 0.0203 | 0.1500 | budget prompt failure |
| priority | priority_greedy | Qwen2.5-14B | 28/40 | 0.8957 | 0.8202 | 1.0000 | 0.9067 | 0.0000 | executor gain |
| priority | priority_pair_group_primary | Qwen2.5-14B | 33/40 | 0.8712 | 0.9103 | 1.0000 | 0.9014 | 0.0000 | 最强 method-shaped row |
| priority | priority_pair_group_primary | Qwen2.5-7B | 25/40 | 0.7546 | 0.9044 | 1.0000 | 0.8530 | 0.0000 | 跨模型协议信号 |
| priority | priority_normalized | Qwen2.5-7B | 26/40 | 0.7853 | 0.9078 | 1.0000 | 0.8828 | 0.0000 | parser friction control |
| priority | priority_fallback_required | Qwen2.5-7B | 31/40 | 0.8344 | 0.8718 | 1.0000 | 0.8431 | 0.0000 | executable schema gain |
| ledger | ledger_oracle_compiler | deterministic | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | ledger upper bound |
| ledger | ledger_utility_density | deterministic | 4/40 | 0.7362 | 0.5106 | 1.0000 | 0.4931 | 1.0500 | hidden-unit control |
| ledger | ledger_hint_density | deterministic | 4/40 | 0.7055 | 0.4772 | 1.0000 | 0.4024 | 1.1000 | hidden-unit control |
| ledger | ledger_first | Qwen2.5-7B | 1/40 | 0.4417 | 0.4645 | 1.0000 | 0.0409 | 1.6750 | unit-construction bottleneck |

## 怎么读

第一，V1.1 确实比早期 tight-budget V0 更锋利。单片段全局贪心在 V1.1 只有 `0/40` strict 和 `0.0411` utility，bundle 级 baseline 也只有 `14/40`。这说明 benchmark 已经开始测证据集合、closure 和跨角色组合，而非单纯按性价比挑 fragment。

第二，direct model 失败很干净。14B default 覆盖率 `1.0000`，但 global budget pass 是 `0.0000`，strict 是 `0/40`。这说明模型能找到很多必要 source，却会把局部有用证据过度承认进角色上下文。budget-first prompt 把 global budget pass 推到 `0.1000`，同时 coverage 掉到 `0.7914`，仍是 `0/40`。

第三，priority + executor 是当前最像方法的信号。14B priority greedy 到 `28/40`，pair-group-primary 到 `33/40`，并且 global budget、per-role budget、closure 全部干净。7B 的 default priority 是 `25/40`，fallback-required schema 到 `31/40`，说明 executable schema 本身是一个真实机制旋钮。

第四，强 baseline 仍然压着 claim。`group_density_global` 的 strict 是 `32/40`，utility 是 `0.9666`；14B pair-group-primary 的 strict 是 `33/40`，utility 是 `0.9014`。如果只看 strict，方法行略高；如果看 utility，强符号 baseline 更优。因此当前不能写“我们优于强 baseline”，只能写“LLM preference + executor 形成了合法、可诊断的 admission protocol”。

第五，ledger-first 暴露了下一瓶颈。给模型 source ledger、budget、utility/hint 和 payload，但隐藏 bundle/group 表时，7B 只有 `1/40` 和 `0.0409` utility。规则层能保证预算和 scope，closure 仍然崩。这说明 admission-unit construction 是后续核心断点。

## 证据路径

| 证据 | 路径 |
| --- | --- |
| local deterministic baselines | `reports/20260618-state-admission-v1-local-baselines.md`; `experiments/20260618-local-state-admission-v1/summary_*.md` |
| direct 14B failure | `reports/20260618-state-admission-v1-qwen25-14b-pressure.md`; `experiments/20260618-a8002-state-admission-v1-full40-qwen25-14b/summary.md`; `experiments/20260618-a8002-state-admission-v1-budgetfirst-full40-qwen25-14b/summary.md` |
| priority 14B executor | `reports/20260618-state-admission-v1-priority-executor-pressure.md`; `experiments/20260618-a8002-state-admission-v1-priority-full40-qwen25-14b/summary.md`; `experiments/20260618-a8002-state-admission-v1-priority-full40-qwen25-14b/summary_pair_group_primary_recompiled.md` |
| priority 7B replication | `reports/20260618-state-admission-v1-priority-7b-replication.md`; `experiments/20260618-a8002-state-admission-v1-priority-full40-qwen25-7b/summary.md`; `experiments/20260618-a8002-state-admission-v1-priority-fallback-full40-qwen25-7b/summary.md` |
| ledger-first pressure | `reports/20260618-state-admission-v1-ledger-hidden-unit-pressure.md`; `experiments/20260618-a8002-state-admission-v1-ledger-full40-qwen25-7b/summary.md` |

## 论文表位置

| 放置位置 | 内容 |
| --- | --- |
| Main table candidate | oracle、group-density、direct 14B、priority 14B、priority 7B fallback、ledger-first 7B |
| Ablation table | priority greedy vs pair-group-primary；7B default vs normalized vs fallback-required |
| Benchmark validity table | item / bundle / group deterministic baselines |
| Failure appendix | ledger-first hidden-unit pressure；direct empty-role over-admission |

## 下一步压力

1. `Unit construction V2`：让 admission units 来自真实下游任务结构，例如 action dependency、tool precondition、case field schema，减少合成 pair utility。
2. `External baseline controls`：加入 DeLM-style shared verified context、CICL-style evidence packing、group-density symbolic baseline，避免 claim 只在自造 packet 内成立。
3. `Two-stage protocol`：模型先提出 candidate units，再由 executor validate / score / reject；和 exposed-unit priority、ledger-first source priority、group-density 同表比较。
4. `Downstream check`：把 admitted state 接到任务答案或 decision proxy，报告 task success、evidence sufficiency、budget legality 和 over-admission。

当前这张表的价值是让方向变硬：我们已经有一条可以被 baseline 拷打的机制线，但它还需要自然任务结构和 downstream metric 才能成为主论文结果。
