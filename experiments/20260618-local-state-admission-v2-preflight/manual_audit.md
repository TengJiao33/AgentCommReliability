# State Admission V2 Manual Audit

日期：2026-06-18

状态：local manual audit。这里没有 packet、runner、outputs、model prompt 或 GPU run。

## 审计判断

这轮只审计 `source_cards.preview.jsonl` 中的三条 seed。结果是：两条 HiddenBench row 通过第一轮人工压力检查，但仍只能保持 `partial`；`pg_000_scope_flip` 需要先按住，不能进入 V2 packet。

## 外部压力触点

外部压力把 V2 的位置压得很窄。DeLM 已经覆盖 shared verified context 和 task queue；CICL 已经覆盖 decision-aware memory-card packing；PerspectiveGap 已经覆盖 role-fragment orchestration benchmark；ProvenanceGuard 已经覆盖答后 source-aware factuality verification。当前候选只有在答前、recipient-specific、source/scope/verification/budget admission 和 rejection certificate 上成立，才值得继续。

核对入口：

- DeLM: https://arxiv.org/abs/2606.10662
- CICL: https://arxiv.org/abs/2606.08151
- PerspectiveGap: https://arxiv.org/html/2606.08878v1
- ProvenanceGuard: https://arxiv.org/abs/2606.18037

## 审计准则

一条 row 只有同时满足这些条件，才可以从 sketch 进入 packet materialization：

- source text 能从 `source_path` 和 `source_row_ref` 重建；
- downstream proxy 可以独立评分，不只重复 source-card strict；
- 至少一个 rejection 来自 source、scope、verification 或 budget，而不只是语义无关；
- admission units 是人可读的 task units，例如 blocker、enabler、precondition 或 dependency；
- prompt 里不能暴露 gold answer、oracle recipients、oracle units 或 oracle groups；
- shared-context 和 CICL-style baselines 有公平表示。

## Verdict Table

| Row | Verdict | Reason | Packet Action |
| --- | --- | --- | --- |
| `pg_000_scope_flip` | `hold` | 源 row 可重建，f2 的 source-scope rejection 也清楚；但下游代理太弱，coder/reviewer empty-state 很大程度来自 V1.1 synthetic utility 和 budget，而不是独立任务结果。它还容易退回 PerspectiveGap-style role assignment。 | 不进入首个 V2 packet。除非重新设计成有真实 downstream outcome 的 bug-report/review task，否则只保留为 synthetic stress note。 |
| `hiddenbench_emergency_supply_drop` | `partial` | 源 task 可重建，下游代理可以要求三类事实：Warehouse A distribution blocker、Warehouse B hazard blocker、Warehouse C road enabler。这个结构能压力测试 recommendation leakage，因为 shared facts 明显偏向 Warehouse B。 | 进入 full source extraction 候选。下一步必须把 gold option 从 prompt 中移除，并定义 fact-unit score。 |
| `hiddenbench_conference_relocation` | `partial` | 源 task 可重建，下游代理可以要求 City Library fuel blocker、Community Center chemical leak blocker、School Gym restroom-restoration enabler。它同时包含 disabling 和 enabling units，适合测试 admitted facts 是否支持最终 venue choice。 | 进入 full source extraction 候选。下一步必须让 scoring 同时需要 blocker 和 enabler，防止只猜 `School Gym`。 |

## Row Notes

### `pg_000_scope_flip`

这个 row 的价值是暴露 source/scope 与 role intuition 的冲突。问题是它目前没有一个独立于 V1.1 scorer 的 downstream proxy：`Audit the report you are given` 和 `Read the contest rules first` 能组成 coder bundle，但这个 bundle 的收益仍主要来自构造器给出的 utility、bundle closure 和 global budget。Reviewer empty-state 也可能被 reviewer bundle 的预算失败解释，而不是真实任务里“该拒绝”的可见证据。

可保留的东西：它可以作为 synthetic stress note，用来检查模型是否会把 eligible-looking reviewer fragments 乱塞给 reviewer。

不能保留的东西：它不能作为 V2 首包证据，尤其不能用来说明我们解决了外部压力下的 role-scoped admission。它离 PerspectiveGap role-fragment assignment 太近，缺少独立 action 或 decision readout。

### `hiddenbench_emergency_supply_drop`

这个 row 更像 V2 想要的自然压力。Shared facts 把 Warehouse B 做成明显诱饵；hidden facts 同时提供 A 的 distribution blocker、B 的 hazard blocker、C 的 distribution enabler。它允许 admission unit 被写成事实级 blocker/enabler，而不是 recommendation。

Promotion 条件：full extraction 中必须保留 `possible_answers` 作为 evaluator metadata，但不放入 model prompt 的 oracle channel；prompt 只能给 source-scoped facts 和任务描述。Downstream score 至少要检查三件事：是否拒绝 A、是否拒绝 B、是否支持 C。

Invalidation 条件：如果模型只需要看到 `correct_answer` 或 sender recommendation 就能过关，这条 row 失效。如果 fact-only/shared baseline 已经稳定拿满，V2 也只能把它作为 sanity row，不能当主证据。

### `hiddenbench_conference_relocation`

这个 row 的价值在于它同时要求阻断和修复。City Library 有 shared readiness 和 backup generator，但 hidden fuel fact 阻断它；Community Center shared 上看可行，但 chemical leak 阻断它；School Gym shared 上有 restroom concern，但 hidden restoration fact 把它重新打开。

Promotion 条件：scoring 必须同时检查阻断和启用。只答 `School Gym` 不算 admission 成功；至少要能解释为什么 City Library 与 Community Center 被拒绝，以及 School Gym 为什么被恢复为可用。

Invalidation 条件：如果 row 被简化成单选题准确率，它会退回 HiddenBench 原任务，不能支持 admission protocol 的价值。College Hall 不在 possible answers 中，full extraction 时应作为 reject-only 或 inert context，不应制造额外 gold obligation。

## 状态结论

这轮审计没有产生 `passed` row。更准确的状态是：`pg_000_scope_flip` 被按住；两条 HiddenBench row 通过第一轮人工压力检查，但还没有完成 full source extraction、oracle unit schema、rejection certificate 和 baseline fairness。

下一步不应继续扩 PerspectiveGap preview。更小的有效推进是先把两条 HiddenBench row 物化成 fact-unit extraction draft，再补一个同类型但不同结构的 HiddenBench row，凑够三条自然 downstream proxy 后再写 packet builder。

## 2026-06-18 Addendum: Perturbation Draft

后续本地推进已经补了第三条自然 row：`hiddenbench_evacuation_west_city`。它现在只能作为 sanity row，因为它的主结构是错误路线 blockers 加 West City shared enabler，hidden positive enabler 比 task 10/11 弱。

`source_scope_perturbations.draft.json` 为三条 HiddenBench row 写了 same-text perturbations。当前价值是让下一轮审计能问一个更硬的问题：同一条事实文本在 `verified`、`quarantined`、`recipient_scope_removed` 或 `dependency_edge_missing` 状态下，gold admission 是否真的改变。

这仍然不产生 `passed` row。只有当 perturbation audit 确认 admission delta 不是 trivial undecidable，并且 oracle/shared-context/CICL-style baselines 有 fair smoke，才可以进入 packet materialization。
