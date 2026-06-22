# 自有结果表体系索引

Snapshot date: `2026-06-19`.

## 一句话判断

现在的大表体系已经从“填表阶段”推进到“主表候选 + 数字专表 + 附表地图”的形态。它仍然没有给出当前最强结果，但已经能看清三件事：哪些结果能进主表，哪些结果只解释机制，哪些历史实验只能保留为背景和防错。

## 当前表体系

| 文件 | 作用 | 当前状态 |
| --- | --- | --- |
| `docs/owned_results_main_table_coverage.md` | 覆盖审计：说明自有结果如何进入主表、附表、运行门 | 已刷新到数字专表之后的状态 |
| `docs/owned_results_main_table_snapshot.md` | 总快照：把自有结果分成主表候选、方法管线、强附表、历史地图 | 入口文档 |
| `docs/owned_results_main_table_rows.csv` | 总行表：35 行，自有结果族的机器可筛选版本 | 可继续填 |
| `docs/pg40_public_benchmark_main_table.md` | PG40 公开切片基准测试主表：同五行 direct、source-ledger、no compiler、compiled、transparent greedy、oracle | 已成表；当前我方候选仍低于源账本十四十亿参数和透明贪心 |
| `docs/pg40_public_benchmark_main_table.csv` | PG40 公开切片基准测试机器表 | 14 行，含同五行主表和四十行背景 |
| `docs/state_admission_v1_numeric_main_table.md` | 第一优先级数字专表：State Admission V1.1 | 主表候选最强 |
| `docs/state_admission_v1_numeric_rows.csv` | State Admission V1.1 行级 CSV，18 行 | 可直接进论文表草稿 |
| `docs/pg40_tight_budget_numeric_main_table.md` | 第二优先级数字专表：PG40 tight-budget | 强 baseline 压力 |
| `docs/pg40_tight_budget_numeric_rows.csv` | PG40 行级 CSV，15 行 | direct routing limit5 已加入；当前最好仍是 card-unit |
| `docs/hsa_v0_numeric_main_table.md` | 第三优先级数字专表：HSA-v0 | 三十六行真跑和支撑型补全结果已加入 |
| `docs/hsa_v0_numeric_rows.csv` | HSA-v0 行级 CSV，36 行 | transparent controls + baseline / recall / focused / constraint / completion full9 + extended15 + P0/P1 33-row + P0/P1/P2 36-row controls/model/support-completion rows |
| `docs/next_model_run_queue.md` | 下一批模型真跑队列：PG40 / PerspectiveGap 公开切片主表优先，HSA 扩包暂停 | 已刷新到对外报告口径修正之后的状态 |
| `docs/owned_report_gap_triage.md` | 报告差集审计：75 份 top-level 报告中 16 份未引用报告的处理 | 结果承载型缺口已补行 |
| `docs/owned_report_gap_triage_rows.csv` | 报告差集审计机器表 | 可筛选 |
| `docs/appendix_owned_results_map.md` | 附表地图：PACT、TypeCast/MATH、MAD/DAR/MOC、PeerRedaction | 附表层已压住 |
| `docs/appendix_owned_results_rows.csv` | 附表行级 CSV，18 行 | 可筛选附表证据 |

## 现在最重要的事实

| 问题 | 当前答案 | 证据表 |
| --- | --- | --- |
| 我们有没有当前最强结果 | 还没有 | 总快照；三张数字专表；PG40 公开切片主表 |
| 哪条线最像方法结果 | `State Admission V1.1` priority + executor | `state_admission_v1_numeric_main_table.md` |
| 哪条 baseline 最压人 | `PG40` 的 `utility_density_greedy`，`25/40` strict、utility `0.9825` | `pg40_public_benchmark_main_table.md`；`pg40_tight_budget_numeric_main_table.md` |
| 哪条线解释机制 | `HSA-v0`，已有三十六行真跑强诊断信号和支撑型补全边界 | `hsa_v0_numeric_main_table.md` |
| 旧强信号放哪里 | PACT/TypeCast/MATH/MAD/DAR/MOC 放附表 | `appendix_owned_results_map.md` |

## 后续填表顺序

1. PG40 公开切片主表已落在 `docs/pg40_public_benchmark_main_table.md`；下一步只做能改变该表的预算感知单卡重排或成对排序器。
2. `PG40 ranking restart only with new mechanism`：role-plan limit5 未超过 card-unit，PG40 只在有预算感知重排或成对排序器时重启。
3. `State Admission V2 / unit construction`：在 V1.1 断点基础上设计更自然的 candidate-unit construction。
4. `PACT-style pilot`：只在 PG40/HSA 有模型信号后启动，并把 evidence metrics 放在 EM/F1 旁边。

## 使用规则

任何新实验只有满足下面任一条件，才进入表体系：

| 进入位置 | 条件 |
| --- | --- |
| 主表 | 同一个 benchmark 上有 baseline、oracle 或 transparent control，并且有 Ours / model row |
| 数字专表 | 属于 `State Admission`、`PG40`、`HSA-v0` 三条证据线之一；对外主表优先使用公开基准 |
| 附表 | 暴露 output contract、gold/parser、operator uptake、retention/compression 等 confound |
| 历史地图 | 只作为旧 baseline 或旧路线防错，不能抢主线 |

这份索引的目的很简单：后面任何推进都必须能说清楚自己要填哪张表、哪一行、和哪个 baseline 对比。
