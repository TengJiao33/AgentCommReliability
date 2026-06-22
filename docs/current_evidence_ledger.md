# 当前证据总账

日期：2026-06-20

## 作用

这份文件是项目当前证据的权威入口。它只记录还会影响下一步决策的证据，不收录所有历史材料。

状态等级：

| 等级 | 含义 |
| --- | --- |
| 主证据 | 可以进入论文主表或主叙事的结果 |
| 诊断证据 | 能说明机制，但样本、对照或规模还不足 |
| 工程失败 | 运行环境、显存、脚本、同步等问题，不能解释为行为结果 |
| 设计失败 | 对照、数据、任务或问题设计没有回答原问题 |
| 真负结果 | 设计干净且结果确实不支持想法 |
| 冻结材料 | 暂时只作为背景、附表或防错 |

## 当前一句话判断

项目当前最重要的修正仍是公开基准优先。PerspectiveGap 官方全量 direct baseline 已补齐：Qwen2.5-14B official runner 默认提示在 `440` 行全网格上 combined strict `2/440`，其中 role assignment `0/220`，prompt writing `2/220`。PG40 本地 scope-projection rerank 预检显示 role-card affinity 是当前瓶颈：五行可闭合，full40 14B 旧输出可从 `11/40` 到 `17/40`，但仍低于透明贪心。随后 no-scope 规则 selector full40 model-only 是 `0/40`、utility `0.5243-0.5467`；GPU7 五行 pairwise selector 也是 `0/5`、utility `0.0000`，且 parse clean。现在最小结论是：手写 lexical / cost 规则和当前 no-scope pairwise prompt 都没有解决 target recipient assignment，下一步应修 role/recipient interface 或回到 PerspectiveGap official role-assignment arms。HSA 三十六行真跑是强内部机制信号，对外方法有效性必须由 PerspectiveGap 官方全量或清楚标注的公开切片承接。

## 活跃路线

| 路线 | 等级 | 最强证据 | 当前风险 | 下一步 |
| --- | --- | --- | --- | --- |
| PerspectiveGap official full-grid | 公开基准主线 | direct baseline 已完成：predictions `440`，scores `440`，status `ok: 440`；combined strict `2/440` | 这只是同模型 direct baseline，不是方法结果；direct 很弱，单独击败它不足以支撑方法 claim | 跑 full-grid no-gold system route，并和 source-ledger / transparent / oracle 控制同表 |
| PG40 tight-budget | 公开切片诊断 | 公开切片主表已成表；direct 五行 `0/5`；card-unit 五行 `1/5`、utility `0.8155`；scope-project + budget-prune 五行 `5/5`；full40 source-ledger 14B scope-project 后 `17/40`、utility `0.8845`；no-scope 规则 selector full40 `0/40`；pairwise selector 五行 `0/5`、utility `0.0000`、parse clean | scope projection 使用 PG40 `recipient_scope`，不是 official full-grid no-gold 方法行；规则式 no-scope selector 低于 source-ledger 和透明基线；当前 no-scope pairwise prompt 按表面 actor role 分配 | 停止 pairwise full40；修 role/recipient interface，或转回 official role-assignment arms |
| HSA-v0 | 诊断证据 | 三十六行真跑：`model_only 16/36`，`compiler 34/36`，阻断补全 `35/36`，支撑型窄补全 `36/36`，extra final cards `42`，全范围控制 `195`；旧 33/15 行重放干净 | 内部派生包；支撑型补全仍是诊断后处理；强制作答检出率 `0.5278` | 暂停扩包，保留为机制表和附表 |

## PerspectiveGap 官方全量证据卡

| 项 | 内容 |
| --- | --- |
| 当前状态 | 公开基准主线 direct baseline |
| 运行编号 | `20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b` |
| 路径 | `experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/` |
| 模型 | `Qwen2.5-14B-Instruct` via local vLLM |
| 官方网格 | `110` scenarios x seeds `1,42` x tasks `role_assignment,prompt_writing` |
| 验证 | predictions `440`；scores `440`；status `ok: 440`；scenario count `110` |
| role assignment | strict `0/220`；net match `0.1953`；coverage `0.6063`；precision `0.7714`；leakage `0.3409` |
| prompt writing | strict `2/220`；net match `0.2816`；coverage `0.5483`；precision `0.8970`；leakage `0.3136` |
| combined | `2/440 = 0.45%` |
| direct role -> deterministic prompt control | combined `0/440`；converted prompt writing `0/220` |
| score audit | official scorer local rerun JSON 完全一致；full-grid oracle 两任务均 `220/220`；direct role JSON parse `220/220` |
| 读法 | direct prompt 很弱；这是公开 full-grid baseline，不是方法结果 |
| 下一步 | full-grid no-gold system route必须改善 role assignment 本身，再 deterministic assignment-to-prompt 并交给 official scorer |

关键文件：

| 文件 | 用途 |
| --- | --- |
| `experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/README.md` | 运行记录 |
| `experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/predictions_official_fullgrid.jsonl` | raw predictions |
| `experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/scores_official_fullgrid.jsonl` | official scores |
| `experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/summary_official_fullgrid.txt` | official scorer summary |
| `experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/validation_official_fullgrid.json` | row-count validation |
| `experiments/20260619-local-perspectivegap-fullgrid-direct-role-to-prompt-qwen25-14b/README.md` | direct role-to-prompt control |
| `experiments/20260619-local-perspectivegap-fullgrid-score-audit/README.md` | 低分 scorer / parser 复核 |
| `reports/20260619-perspectivegap-official-fullgrid-direct-baseline.md` | 解释报告 |
| `reports/20260619-perspectivegap-fullgrid-score-audit.md` | 低分复核报告 |
| `reports/20260619-public-benchmark-compliance-audit.md` | 合规红线 |

## HSA-v0 证据卡

| 项 | 内容 |
| --- | --- |
| 当前最好运行编号 | `20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b` |
| 状态 | 诊断证据 |
| 路径 | `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b/` |
| 模型 | `Qwen2.5-14B-Instruct` |
| 行数 | `36` |
| 主对照 | 模型直出、硬准入、补全后硬准入 |
| 结果 | `model_only 16/36`，`compiler 34/36`，阻断补全后 `35/36`，支撑型窄补全后 `36/36` |
| 机制读法 | 硬准入修扰动行错误承诺；阻断补全修漏掉的阻断卡；支撑型窄补全修 task 5 Roberts 支撑卡 |
| 边界 | 支撑型补全是本地后处理诊断；强制作答检出率高 |

关键文件：

| 文件 | 用途 |
| --- | --- |
| `experiments/20260619-a8002-hsa-v0-sseac-full9-qwen25-14b/README.md` | 运行记录 |
| `experiments/20260619-a8002-hsa-v0-sseac-full9-qwen25-14b/summary_model_only.md` | 模型直出摘要 |
| `experiments/20260619-a8002-hsa-v0-sseac-full9-qwen25-14b/summary_compiler.md` | 硬准入摘要 |
| `reports/20260619-hsa-v0-full9-a8002.md` | 解释报告 |
| `experiments/20260619-a8002-hsa-v0-recall-sweep-full9-qwen25-14b/README.md` | recall_sweep 运行记录 |
| `experiments/20260619-a8002-hsa-v0-recall-sweep-full9-qwen25-14b/summary_compiler.md` | recall_sweep 摘要 |
| `reports/20260619-hsa-v0-recall-sweep-full9-a8002.md` | recall_sweep 解释报告 |
| `experiments/20260619-a8002-hsa-v0-focused-recall-full9-qwen25-14b/README.md` | focused_recall 运行记录 |
| `experiments/20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b/README.md` | constraint_recall 运行记录 |
| `experiments/20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b/summary_compiler.md` | constraint_recall 摘要 |
| `reports/20260619-hsa-v0-focused-constraint-full9-a8002.md` | focused / constraint 对比解释报告 |
| `experiments/20260619-local-hsa-v0-constraint-completion-postfilter/README.md` | constraint_completion 后置补全记录 |
| `experiments/20260619-local-hsa-v0-constraint-completion-postfilter/summary_compiler.md` | 当前最强 HSA 诊断摘要 |
| `reports/20260619-hsa-v0-constraint-completion-postfilter.md` | 后置补全解释报告 |
| `experiments/20260619-local-hsa-v0-seed-shortlist-gate/README.md` | seed shortlist 准入门 |
| `reports/20260619-hsa-v0-seed-shortlist-gate.md` | 扩 seed 前解释报告 |
| `experiments/20260619-local-hsa-v0-hb12-hb31-draft/README.md` | HB12/HB31 draft packet 记录 |
| `reports/20260619-hsa-v0-hb12-hb31-draft-packet.md` | HB12/HB31 draft 解释报告 |
| `experiments/20260619-local-hsa-v0-extended15-packet/README.md` | 15 行扩展包透明控制记录 |
| `reports/20260619-hsa-v0-extended15-packet-gate.md` | 15 行扩展包门禁解释报告 |
| `experiments/20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b/README.md` | 15 行模型真跑记录 |
| `reports/20260619-hsa-v0-constraint-recall-extended15-a8002.md` | 15 行真跑解释报告 |
| `experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft/README.md` | 33 行 P0/P1 输入包透明控制记录 |
| `reports/20260619-hsa-v0-p0p1-seed-expansion33-gate.md` | 33 行输入包门禁解释报告 |
| `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1-33-qwen25-14b/README.md` | 33 行模型真跑记录 |
| `reports/20260619-hsa-v0-constraint-recall-p0p1-33-a8002.md` | 33 行真跑解释报告 |
| `experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/README.md` | 36 行 P0/P1/P2 输入包透明控制记录 |
| `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b/README.md` | 36 行模型真跑记录 |
| `reports/20260619-hsa-v0-constraint-recall-p0p1p2-36-a8002.md` | 36 行真跑解释报告 |
| `docs/hsa_support_completion_method_component.md` | 支撑型窄补全组件规则和升级门槛 |
| `docs/hsa_larger_derived_packet_preflight.md` | 更大 HSA 派生包候选筛选门 |
| `docs/hsa_larger_derived_candidate_review.md` | 第一批候选人工复核 |

## PG40 证据卡

| 项 | 内容 |
| --- | --- |
| 当前状态 | 诊断证据 |
| 公开切片主表 | `docs/pg40_public_benchmark_main_table.md` |
| 强基线 | `utility_density_greedy_after_sseac_compiler` |
| 强基线结果 | `25/40` 严格正确，utility `0.9825` |
| 旧模型管线 | source-ledger 14B compiled `11/40` |
| direct baseline 运行 | `20260619-a8002-pg40-direct-routing-limit5-qwen25-14b` |
| direct baseline 结果 | strict `0/5`；coverage `0.1481`；precision `0.1481`；budget pass `0.4000`；utility `0.0987` |
| 当前最好行为运行 | `20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b` |
| 当前最好行为结果 | no-compiler `0/5`，compiler `1/5`；budget pass `0.0000 -> 1.0000`；utility `0.1803 -> 0.8155`；coverage `0.8148 -> 0.6667` |
| 最新诊断运行 | `20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b` |
| 最新诊断结果 | compiler `1/5`；budget pass `1.0000`；utility `0.7811`；exact role `0.5000` |
| scope projection 预检 | `20260620-local-pg40-scope-rerank-preflight` |
| scope projection 结果 | 五行 `5/5`；full40 14B `17/40`、utility `0.8845`；full40 7B `4/40`、utility `0.7250` |
| no-scope 规则预检 | `20260620-local-pg40-no-scope-role-affinity-preflight` |
| no-scope 规则结果 | hybrid model-only `0/40`、utility `0.5243`；cost model-only `0/40`、utility `0.5467`；hybrid + compiler `1/40`、utility `0.5243` |
| pairwise selector 预飞行 | `20260620-local-pg40-pairwise-selector-preflight`；full40 prompts `40`，禁用字段扫描 `0`，schema smoke 通过 |
| pairwise selector 真跑 | `20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b` |
| pairwise selector 结果 | model-only/compiler 都是 `0/5`、utility `0.0000`；parse ok `5/5`；prompt leak `0`；raw assignments `22`；compiler prevented out-of-scope `14`；admitted units `0` |
| 机制读法 | direct baseline 角色路由很弱；card-level unit contract 解决了多卡整组拒绝问题的一部分；scope projection 说明 role-card affinity 和跨 role 投影是下一瓶颈；规则式 no-scope selector 和当前 no-scope pairwise prompt 都没有学会 target recipient assignment |
| 下一步 | 不扩 pairwise full40；修 role/recipient interface，或转回 official role-assignment arms |

关键文件：

| 文件 | 用途 |
| --- | --- |
| `docs/pg40_public_benchmark_main_table.md` | PG40 公开切片基准测试主表 |
| `docs/pg40_public_benchmark_main_table.csv` | PG40 公开切片基准测试机器表 |
| `docs/pg40_tight_budget_numeric_main_table.md` | 数字专表 |
| `experiments/20260618-local-sseac-v0-pg40-prediction-converter/` | 强基线和旧管线转换结果 |
| `experiments/20260619-a8002-pg40-direct-routing-limit5-qwen25-14b/README.md` | direct routing 五行运行记录 |
| `experiments/20260619-a8002-sseac-v0-pg40-limit5-qwen25-14b/README.md` | 显存失败记录 |
| `experiments/20260619-a8002-sseac-v0-pg40-limit5-gpu7-rerun-qwen25-14b/README.md` | 五行行为运行记录 |
| `experiments/20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b/README.md` | 单卡候选契约五行记录 |
| `experiments/20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b/README.md` | 角色计划契约五行负结果 |
| `experiments/20260620-local-pg40-scope-rerank-preflight/README.md` | scope projection + budget prune 本地预检 |
| `experiments/20260620-local-pg40-no-scope-role-affinity-preflight/README.md` | no-scope 规则 role-affinity 负结果预检 |
| `experiments/20260620-local-pg40-pairwise-selector-preflight/README.md` | pairwise role-card selector launch preflight |
| `experiments/20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b/README.md` | pairwise role-card selector 五行负结果 |
| `reports/20260619-pg40-sseac-limit5-gpu7-rerun.md` | 五行解释报告 |
| `reports/20260619-pg40-direct-routing-limit5.md` | direct routing 五行解释报告 |
| `reports/20260619-pg40-sseac-cardunit-limit5.md` | 单卡候选契约解释报告 |
| `reports/20260619-pg40-sseac-roleplan-limit5.md` | 角色计划契约解释报告 |
| `reports/20260620-pg40-scope-projection-rerank-preflight.md` | scope projection 解释报告 |
| `reports/20260620-pg40-no-scope-role-affinity-preflight.md` | no-scope 规则 role-affinity 解释报告 |
| `reports/20260620-pg40-pairwise-selector-preflight.md` | pairwise selector 预飞行报告 |
| `reports/20260620-pg40-pairwise-selector-limit5.md` | pairwise selector 五行真跑解释报告 |
| `reports/20260619-hsa-pg40-a8002-small-run-status.md` | 当前停点说明 |

## 冻结材料

| 材料族 | 当前用途 | 解冻条件 |
| --- | --- | --- |
| State Admission V1/V2 | 方法候选背景和边界 | HSA/PG40 需要 unit construction 对照 |
| PACT / public state | 分裂证据设计背景 | HSA/PG40 出现稳定模型信号后，需要外部下游任务 |
| TypeCast / MATH | 机制显微镜和解析防错 | 外部 benchmark 暴露同类机制问题 |
| HiddenBench 大扩展 | HSA 来源和通信必要性背景 | HSA 9 行后需要更大样本 |
| MAD/DAR/MOC | 早期复现背景 | 只进附表或历史地图 |

## 更新规则

- 新结果先进入本文件，再进入论文表草稿。
- 工程失败必须留记录，但不能进入行为比较。
- 小样本结果默认是诊断证据，除非已有预注册对照和足够样本。
- 每条活跃路线最多保留一个下一步动作。
