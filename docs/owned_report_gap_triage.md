# 自有报告覆盖差集审计

Snapshot date: `2026-06-18`.

机器可筛选版本见 `docs/owned_report_gap_triage_rows.csv`。

## 核心判断

当前 top-level `reports/` 里有 `75` 份非 README 报告。审计前，`docs/` 中已引用 `59` 份，还有 `16` 份没有进入表体系视野。

这 `16` 份并不都代表遗漏的主表结果。它们分成四类：外部压力/故事定位、preflight 或设计门、被 full run 吸收的 smoke、真正漏掉的结果行。本轮已把真正漏掉的结果行补进 `docs/owned_results_main_table_rows.csv` 和 `docs/appendix_owned_results_rows.csv`。

## 差集结果

| 类别 | 数量 | 处理 |
| --- | ---: | --- |
| 外部压力 / story / reviewer gate | 6 | 保留为相关工作、story pressure 或 claim boundary |
| Preflight / design gate / packet record | 5 | 保留为运行记录，不进 metric 表 |
| 被 full run 吸收的 smoke | 1 | 只保留 provenance，读数看 full65 或后续主表 |
| 漏掉的结果行 | 4 | 已补进自有结果行表或附表行表 |

## 已补的四个结果行

| 报告 | 补入位置 | 关键读数 | 判断 |
| --- | --- | --- | --- |
| `reports/20260617-hiddenbench-v2-stage4-qwen25-7b-pressure.md` | `docs/owned_results_main_table_rows.csv` | old exchange `16/50`；minimal 条件约 `47/50`；full-visibility minimal `46/50` | 给 HiddenBench fact-state story 增加 7B cross-model 压力 |
| `reports/20260617-math-operator-lifecycle-v1-qwen25-14b.md` | `docs/owned_results_main_table_rows.csv`; `docs/appendix_owned_results_rows.csv` | `166/166` completed；typed partial errors `3/16`；错误集中在两个 case | 机制显微镜，说明 answer removal 后仍有 operator/numeric-role uptake |
| `reports/20260618-state-admission-v2-smoke-gpu.md` | `docs/owned_results_main_table_rows.csv` | oracle `9/9`；shared-context `0/9`；model strict `0.0000`；unit recall `0.2222` | V2 diagnostic floor，支持 hidden unit construction 是断点 |
| `reports/20260618-state-admission-v2-abstention-gate-ablation.md` | `docs/owned_results_main_table_rows.csv` | strict `0.1111`；downstream `0.4444`；option-state recall `0.8148` | abstention gate 没有带来新增收益，适合作为 contract ablation |

## 不进 metric 表的报告

| 报告 | 原因 | 保留方式 |
| --- | --- | --- |
| `reports/20260616-external-novelty-pressure-epistemic-type-erasure.md` | 外部 novelty 定位 | 相关工作和 claim boundary |
| `reports/20260616-research-progress-synthesis.md` | 被当前表体系替代的阶段总结 | 历史 synthesis |
| `reports/20260617-a8002-docker-feasibility.md` | Docker 可行性和 TeamBench 约束 | benchmark feasibility |
| `reports/20260617-hiddenbench-stage2-external-pressure.md` | HiddenBench 外部压力 | HiddenBench novelty caveat |
| `reports/20260617-hiddenbench-v2-stage3-blind-sender-preflight.md` | preflight，无模型结果 | 运行记录 |
| `reports/20260617-hiddenbench-v2-stage4-sender-visibility-preflight.md` | preflight，无模型结果 | 运行记录 |
| `reports/20260617-hiddenbench-v2-stage4-sender-visibility-smoke12-qwen25-14b.md` | smoke 已被 full65 stage4 吸收 | provenance |
| `reports/20260617-math-operator-lifecycle-v1-packet.md` | packet audit | 附表上下文 |
| `reports/20260617-next-typecast-experiment-preflight.md` | TypeCast 设计门 | 停止扩大 TypeCast 的依据 |
| `reports/20260618-reviewer-verdict-state-admission-series.md` | reviewer-style critique | claim boundary |
| `reports/20260618-routing-story-reading-sprint.md` | reading sprint | benchmark/story pressure |
| `reports/20260618-skill-guided-state-admission-v2-preflight.md` | V2 preflight | launch gate 和设计依据 |

## 覆盖结论

审计后，top-level 报告的结果承载状态已经清楚：

| 层级 | 承接位置 |
| --- | --- |
| 主表数字 | `docs/state_admission_v1_numeric_main_table.md`; `docs/pg40_tight_budget_numeric_main_table.md`; `docs/hsa_v0_numeric_main_table.md` |
| 主表/背景行 | `docs/owned_results_main_table_rows.csv`; `docs/owned_results_main_table_snapshot.md` |
| 机制附表 | `docs/appendix_owned_results_map.md`; `docs/appendix_owned_results_rows.csv` |
| 下一批真跑 | `docs/next_model_run_queue.md`; `scripts/run_sseac_smoke_queue_openai_compatible.ps1` |
| 外部压力和运行门 | 当前差集审计和对应原始报告 |

所以答案更精确了：自有结果没有全部进入“最终主表”，也不应该全部进入最终主表；但当前结果承载型 top-level 报告已经被分派到主表行、数字专表、机制附表或运行门。

下一步最该做的是把已经跑出的 PG40/HSA 模型行继续压成决策：PG40 role-plan 已退休，暂停扩跑；HSA full9 显示 compiler paired delta，优先修候选证据召回。新分支扩张继续暂停。
