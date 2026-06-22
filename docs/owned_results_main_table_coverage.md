# 自有实验结果进入主表的覆盖审计

Snapshot date: `2026-06-19`.

## 核心判断

自有结果已经从“散在报告里”推进到“主表快照 + 三张数字专表 + 机制附表 + 报告差集审计”的形态。最终主表仍然只应承接当前 claim 的直接证据；历史探索、preflight、外部压力和机制显微镜需要留在附表或运行门。

当前没有 SOTA 结果。最接近方法结果的是 `State Admission V1.1` priority + executor，但它仍受 synthetic packet、显式 admission units、强符号 baseline 和无真实 downstream task 的限制。PG40 已有 direct、true prompt、card-unit、role-plan 四轮五行模型压力，单卡契约是当前最好但仍低于强基线；HSA-v0 已有三十六行成对信号，但它属于内部机制诊断。接下来优先做 PG40 预算感知重排或成对排序器，HSA 扩包暂停。

## 当前覆盖状态

| 覆盖层 | 文件 | 状态 |
| --- | --- | --- |
| 总快照 | `docs/owned_results_main_table_snapshot.md` | 已把主要自有结果分成主表候选、主表背景、方法管线、强附表、历史地图 |
| 行级总表 | `docs/owned_results_main_table_rows.csv` | 已补入 HiddenBench 7B、SA-V2 smoke、SA-V2 abstention、MATH operator lifecycle |
| SA-V1.1 数字专表 | `docs/state_admission_v1_numeric_main_table.md`; `docs/state_admission_v1_numeric_rows.csv` | 18 行，当前最强 method-shaped 自有结果族 |
| PG40 数字专表 | `docs/pg40_tight_budget_numeric_main_table.md`; `docs/pg40_tight_budget_numeric_rows.csv` | 15 行，当前最硬 baseline 压力；direct 已补齐，role-plan 已退休 |
| HSA-v0 数字专表 | `docs/hsa_v0_numeric_main_table.md`; `docs/hsa_v0_numeric_rows.csv` | 36 行，承接 HiddenBench 的 admission packet，36 行支撑型补全诊断行已加入 |
| 机制附表 | `docs/appendix_owned_results_map.md`; `docs/appendix_owned_results_rows.csv` | 已补入 MATH operator lifecycle |
| 报告差集审计 | `docs/owned_report_gap_triage.md`; `docs/owned_report_gap_triage_rows.csv` | 75 份 top-level 报告中，原先 16 份未引用报告已完成分派 |
| 下一批真跑 | `docs/next_model_run_queue.md`; `scripts/run_sseac_smoke_queue_openai_compatible.ps1` | PG40 / PerspectiveGap 公开切片主表优先；HSA 扩包暂停 |

## 覆盖等级

| 覆盖等级 | 含义 |
| --- | --- |
| `主表数字` | 已有同 benchmark 的 baseline、oracle/control、模型或 deterministic row，可进入论文主表草稿 |
| `主表背景` | 支撑 benchmark 选择、baseline ladder 或机制方向，等待 Ours/model row |
| `方法管线` | builder、adapter、runner、scorer 已打通，尚未产生模型效果 |
| `强附表` | 数值强、机制有价值，但任务或 evaluator 形态限制主张承载力 |
| `机制显微镜` | 用来解释 failure surface、parser/gold/contract 风险 |
| `外部压力/运行门` | 文献、Docker、preflight、reviewer gate、story sprint，不进 metric 表 |
| `历史地图` | 旧 reproduction、trace、retention/compression 经验，只在填补当前 baseline 空格时复活 |

## 自有结果覆盖表

| 结果族 | 代表性自有结果 | 当前覆盖 | 应放位置 |
| --- | --- | --- | --- |
| `State Admission V1.1` | oracle `40/40`；group-density `32/40`；14B direct `0/40`；14B priority pair-group-primary `33/40`；7B fallback `31/40`；ledger-first `1/40` | 已入数字专表和行级总表 | 主表候选 |
| `PG40 / PerspectiveGap tight-budget` | oracle `40/40`；utility-density greedy `25/40`；source-ledger 14B compiled `11/40`；direct routing limit5 `0/5`，utility `0.0987`；card-unit compiled limit5 `1/5`，utility `0.8155`；role-plan compiled limit5 `1/5`，utility `0.7811` | 已入数字专表和行级总表 | 诊断证据 / 强压力表 |
| `HSA-v0 / HiddenBench-derived` | 36 行 shared-only base `0/12`；all-scoped `36/36` 但 extra final cards `195`；model-only `16/36`；compiler `34/36`；support completion compiler `36/36`，extra final cards `42` | 已入数字专表 | 内部机制诊断和附表 |
| `HiddenBench full65` | 14B old exchange `23/55` clean vs fact-only `55/55`；7B old exchange `16/50` vs minimal `47/50` | 已入行级总表和 gap triage | 主表背景 |
| `State Admission V2` | 7B smoke strict `0.0000`、unit recall `0.2222`；14B abstention gate strict `0.1111`、option-state recall `0.8148` | 已补入行级总表 | 强附表 / HSA 设计依据 |
| `PACT / HotpotQA field-contract` | HotpotQA50 EM `17/50 -> 34/50`；offset50 EM `26/50 -> 28/50` | 已入附表地图 | Output contract warning |
| `TypeCast / MATH operator lifecycle` | repaired117 self/unrelated/quarantine `0/11`；MATH operator lifecycle typed partial errors `3/16`；raw-gold mismatch `98/200` | 已入附表行表 | 机制显微镜 |
| `MAD-MM / DAR / MOC` | MAD-MM MATH50 objective `0.66`；DAR arithmetic `0.99`、GSM8K `0.93`；MOC role-preservation `19/30` vs `4/30` | 已入附表地图 | 历史地图 |
| `Peer-redacted / source-label / typed-public-state` | leakage `16/44 -> 8/44`；typed-public-state harm低于 full rationale但低 utility | 已入附表或 evidence register 背景 | 机制显微镜 / 退役边界 |
| `外部压力 / collision / reviewer gate` | PerspectiveGap、DALA、ProvenanceGuard、TeamBench/Docker、State Admission reviewer verdict | 已入近场地图或差集审计 | 相关工作和实验设计依据 |

## 当前主表优先级

| 优先级 | 表 | 为什么压这里 |
| --- | --- | --- |
| 1 | `State Admission V1.1` | 当前最像 method-shaped result，但必须贴着 group-density baseline 和 synthetic caveat |
| 2 | `PG40 tight-budget` | 直接给 SSEAC 一个外部 routing / budget / utility 压力 |
| 3 | `HSA-v0` | 把 HiddenBench 的 fact-state signal 转成可评分 admission packet |
| 4 | `State Admission V2` | 只作为 hidden-unit / downstream consistency 诊断，不抢主 claim |
| 5 | `PACT / TypeCast / MAD-DAR-MOC` | 解释 output surface、parser/gold、operator uptake、retention/compression 风险 |

## 还缺什么

| 缺口 | 当前状态 | 下一步 |
| --- | --- | --- |
| `PG40 ranking mechanism` | true prompt、card-unit、role-plan limit5 都已完成；role-plan 未超过 card-unit | 只在有预算感知重排或成对排序器时重启 |
| `公开基准主表` | PG40 已有 oracle、transparent greedy、source-ledger、direct、五行 SSEAC 诊断；当前缺的是能超过 card-unit 的排序机制 | 优先做预算感知重排或成对排序器 |
| `State Admission V1.1 paper-ready table` | 数字专表 ready | 写成最终主表草稿时压缩为 oracle / strong baseline / Ours / failure row |
| `附表 prose` | 行表 ready | 写论文时把 PACT、TypeCast/MATH、MAD/DAR/MOC 合并为 2-3 张 appendix |

## 结论

所有重要自有结果现在都有去处：主表数字、主表背景、机制附表、历史地图、外部压力或运行门。最终主表不承接所有历史实验；它只承接当前 claim 的直接证据。

因此当前推进姿态应保持公开基准评测优先：PG40 / PerspectiveGap 承接对外方法有效性，HSA-v0 保留为机制解释。若公开切片上仍低于强基线，研究问题要回到 schema、unit construction、priority 和 admission contract。
