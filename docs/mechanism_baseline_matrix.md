# 机制改善主表骨架：Benchmark、Baseline、指标与运行门

Snapshot date: `2026-06-18`.

## 核心判断

这份文档定义后续论文主表的骨架。它目前的定位是运行约束和填表规则；最终结果表需要按冻结后的 evaluator、prompt contract 和 baseline ladder 重跑后生成。

当前项目最需要补的是同一把尺子：同一个 `Ours` 条件、同一条 baseline ladder、同一组近场 benchmark、同一套指标族。后续新实验只有能落进这张矩阵，才算真正推进经典机制改善路线。

旧实验信号的取舍见 `reports/20260618-experiment-signal-audit.md`。这张主表优先继承三类仍有价值的旧信号：HiddenBench fact-state discipline、State Admission priority + executor、PerspectiveGap source/scope ledger + compiler。

## 状态标记

| 标记 | 含义 |
| --- | --- |
| `DONE` | 已有本地结果或报告，可作为背景证据；进入主表前仍需复核同一 evaluator / prompt contract。 |
| `READY` | builder、runner 或 scorer 已存在，尚未按冻结主表重跑。 |
| `DRAFT` | 设计方向清楚，但 packet、gold、parser 或 controls 还没冻结。 |
| `TODO` | 需要实现或补 baseline。 |
| `BLOCKED` | 受环境或外部依赖阻塞。 |
| `N/A` | 该 benchmark 的任务形态不自然支持这个 condition。 |

## 主 Benchmark 层级

| ID | Benchmark / Slice | 角色 | 当前状态 | 关键 artifacts |
| --- | --- | --- | --- | --- |
| `PG40` | PerspectiveGap source-ledger / tight-budget 40-row slice | 主机制尺度：role-specific routing、coverage、precision、leak、budget | `DONE` + `READY` | `reports/20260618-perspectivegap-source-ledger-rotated20.md`; `reports/20260618-perspectivegap-tight-budget-source-ledger.md`; `reports/20260618-sseac-v0-pg40-runner-preflight.md`; `scripts/run_perspectivegap_source_ledger_router_openai_compatible.py`; `scripts/run_sseac_v0_pg40_openai_compatible.py`; `scripts/score_perspectivegap_tight_budget.py` |
| `HB65` | HiddenBench full65 and clean failure seeds | 主任务尺度背景：hidden/private information 与 communication necessity | `DONE` | `reports/20260617-hiddenbench-v2-stage1-full65-qwen25-14b.md`; `reports/20260618-hiddenbench-failure-seeds-for-state-admission.md`; `experiments/20260618-local-hiddenbench-failure-seeds/` |
| `HSA-v0` | Hidden-State Admission small slice | 主任务尺度候选：source/scope/verification/rejection/evidence sufficiency + downstream decision | `DONE` 36-row diagnostic + `READY` support-completion replay audit | `experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/`; `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b/`; `reports/20260619-hsa-v0-constraint-recall-p0p1p2-36-a8002.md`; `scripts/build_hsa_p0p1_seed_expansion_drafts.py`; `scripts/build_hsa_v0_sseac_packet.py`; `scripts/run_hsa_v0_sseac_openai_compatible.py`; `scripts/score_hsa_v0_compiled.py` |
| `SA-V2` | State Admission V2 diagnostic slice | 内部机制显微镜：option-state、admission units、rejections、abstention | `DONE` diagnostic | `reports/20260618-state-admission-v2-option-state-and-direct-controls.md`; `reports/20260618-state-admission-v2-visible-facts-ablation.md`; `scripts/run_state_admission_v2_openai_compatible.py`; `scripts/score_state_admission_v2.py` |
| `PACT-pilot` | PACT-style split evidence pilot | 下游泛化尺度：split evidence QA 是否能通过准入层进入最终回答 | `DRAFT` | existing PACT audit scripts under `scripts/audit_pact_*`; pilot packet not frozen |
| `TeamBench` | OS-enforced role separation | 远期工程生态压力 | `BLOCKED` | blocked by Docker/rootless container support |

## 主 Baseline Ladder

| Condition | 定义 | 论文作用 | 必须报告的指标 |
| --- | --- | --- | --- |
| `no_communication` / `shared_only` | final decider 只看共享信息或自身信息 | 通信必要性下界 | task success, oracle gap |
| `full_info` | final decider 获得所有相关事实 | 解题能力上界 | task success, full-info gap |
| `oracle_public_facts` / `oracle_admissible_facts` | 只给 gold 可公开或可准入事实 | 表达上界和 downstream upper bound | task success, abstention correctness |
| `all_to_all` / `copy_all` | 所有事实发给所有 role | 过度共享、泄漏和 distractor 压力 | coverage, precision, leak, task success |
| `old_exchange` | 旧自由文本交换协议 | 旧系统对照 | task success, contamination cases |
| `fact_only_exchange` | sender 只输出事实，不输出推荐或偏好 | message hygiene ceiling | task success, oracle gap |
| `shared_verified_context` | 统一共享已核验上下文 | DeLM / PACT 邻域压力 | task success, over-share, cost |
| `CICL_style_card_packing` | decision-aware evidence cards + budget packing | CICL 邻域压力 | coverage, precision, budget, task success |
| `direct_admitted_state_generation` | LLM 直接写 admitted state 或 role assignment | 直接生成状态的边界 | scope violation, budget pass, rejection recall |
| `source_ledger_model_only` | 给 source/scope ledger，让模型自己分配 | 测模型是否能自行守住来源和作用域 | coverage, precision, leak, budget |
| `priority_plus_executor` | 模型给 priority，确定性 executor 执行 scope/budget/rejection | 测语义偏好 + 规则执行的增益 | coverage, precision, leak, budget, rejection |
| `ours_sseac_v0` | Source-Scoped Evidence Admission Compiler v0 | 主方法条件 | all metric families |
| `oracle_executor` | gold units / gold slots + executor | 准入/打包上界 | oracle gap, budget pass |

## Benchmark x Baseline 状态矩阵

| Condition | `PG40` | `HB65` / `HSA-v0` | `SA-V2` | `PACT-pilot` |
| --- | --- | --- | --- | --- |
| `no_communication` / `shared_only` | `N/A` for routing; optional empty-assignment floor | `DONE` on HB65 shared-only | `N/A` | `TODO` |
| `full_info` | `N/A` | `DONE` on HB65 full-info | `DONE` as direct all-facts diagnostic | `TODO` |
| `oracle_public_facts` / `oracle_admissible_facts` | `DONE` oracle routing / oracle executor | `DONE` on HB65 oracle-public-facts; `READY` HSA-v0 oracle-admissible 9-row smoke | `DONE` direct admissible diagnostic, weak downstream | `TODO` |
| `all_to_all` / `copy_all` | `DONE` all-to-all/copy-all style controls | `DRAFT` reveal-all needs same scorer alignment | `DONE` direct all-facts as diagnostic | `TODO` |
| `old_exchange` | `N/A` | `DONE` exchange-then-decide | `N/A` | `TODO` |
| `fact_only_exchange` | `N/A` | `DONE` fact-only exchange and clean seed extraction | `N/A` | `TODO` |
| `shared_verified_context` | `TODO` map to verified shared cards | `TODO` | `READY` via visible/admissible facts diagnostics | `DRAFT` from old public-state field work |
| `CICL_style_card_packing` | `TODO` implement simple budgeted card packing | `TODO` | `TODO` | `TODO` |
| `direct_admitted_state_generation` | `DONE` role assignment / hard routing model outputs | `DRAFT` HSA-v0 direct state | `DONE` unit-first / option-state-first diagnostics | `TODO` |
| `source_ledger_model_only` | `DONE` source-ledger 7B/14B | `DRAFT` HSA-v0 source cards | `READY` with source/scope prompt | `TODO` |
| `priority_plus_executor` | `DONE` budget-compiled / tight-budget style evidence | `TODO` | `READY` from V1 priority executor, V2 adaptation needed | `TODO` |
| `ours_sseac_v0` | `READY` core compiler + PG40 adapter + prediction converter diagnostic + runner preflight; `TODO` small model run | `DONE` HSA-v0 36-row diagnostic; `TODO` support-completion replay audit | `READY` core compiler; `TODO` SA-V2 adapter | `READY` core compiler; `TODO` after contact |
| `oracle_executor` | `DONE` | `DRAFT` HSA-v0 gold slots | `READY` scorer oracle / expected states | `TODO` |

## 指标绑定

| 指标族 | `PG40` | `HB65` / `HSA-v0` | `SA-V2` | `PACT-pilot` |
| --- | --- | --- | --- | --- |
| Task success | no native final task for PG routing slice | HB decision accuracy; HSA downstream_ok / insufficient | downstream_ok / direct answer ok | EM/F1 / answer exact |
| Routing coverage | required role-fragment coverage | required source-card recall in HSA | unit_recall / visible recall | supporting evidence recall |
| Boundary precision | role precision / wrong-recipient | scope violation / over-share | scope violation / absent-unit errors | irrelevant evidence admission |
| Leakage | distractor leak | private or rejected fact leak | rejected/quarantined unit admission | distractor evidence leak |
| Source fidelity | source_id match | source-card provenance | unit source match | document/source match |
| Admission discipline | budget pass, source/scope pass | verification/rejection respect | rejection recall, verification violation | evidence card validity |
| Evidence sufficiency | partial: coverage + budget proxy | abstention correctness, slot completeness | option_state_recall, slot completeness, abstention | answerability / missing support |
| Budget / cost | role budget pass, token cost | admitted card cost, messages | budget pass, prompt/output tokens | context budget, token cost |
| Oracle gap | oracle routing gap | full-info / oracle-public / oracle-admissible gap | oracle-state gap | oracle evidence / full context gap |

## 第一张主表的最小版本

第一张主表先不要追求全覆盖。推荐最小范围：

| Benchmark | 必跑 conditions | 可暂缓 conditions |
| --- | --- | --- |
| `PG40` | `all_to_all`, `direct_admitted_state_generation`, `source_ledger_model_only`, `priority_plus_executor`, `ours_sseac_v0`, `oracle_executor` | `shared_verified_context`, `CICL_style_card_packing` |
| `HSA-v0` | `shared_only`, `full_info`, `oracle_admissible_facts`, `old_exchange`, `fact_only_exchange`, `direct_admitted_state_generation`, `ours_sseac_v0` | `CICL_style_card_packing`, `priority_plus_executor` if schema not stable |
| `SA-V2` | `direct_allfacts`, `direct_admissible`, `option_state_first`, `abstention_explicit`, `ours_sseac_v0`, `oracle_executor` | old exchange style conditions |
| `PACT-pilot` | `full_context`, `split_no_comm`, `shared_verified_context`, `ours_sseac_v0` smoke | full baseline ladder |

第一张主表的任务是判断机制是否值得扩；最终论文实验分阶段补齐。

## 运行门

任何 claim-bearing run 启动前，必须在 run README 或 preflight report 写清楚：

```text
purpose:
unit:
primary_contrast:
secondary_contrasts:
success_signal:
failure_signal:
invalidation_conditions:
packet_path:
output_path:
scorer_path:
expected_row_count:
manual_audit_rows:
```

默认 invalidation conditions：

- packet 没有 paired baseline rows；
- gold answer、oracle state 或 expected slots 未手查；
- scorer 不能区分 parser failure 与 semantic failure；
- prompt 泄漏 oracle labels；
- direct controls 显示任务本身不可解；
- baseline 使用的 evaluator 和 Ours 不兼容；
- 结果只在 final answer 上变化，routing/admission/sufficiency 指标没有对应读数。

## 下一步填表顺序

1. 冻结 `ours_sseac_v0` 方法规格。当前已完成文档规格和本地 compiler smoke。
2. 在 `PG40` 上用 SSEAC runner 跑小样本模型预测，接 `compile_sseac_v0.py` 和 `score_sseac_pg40_compiled.py`。
3. 在 `HSA-v0` 上准备更大派生包预飞行；当前已有 36 行模型真跑、支撑型补全诊断、旧包重放和组件说明。
4. 只在 `PG40` 和 `HSA-v0` 都有可解释差异后，再启动 PACT-style split evidence pilot。
5. 若 `shared_verified_context` 或 `CICL_style_card_packing` 接近 oracle，立即把 Ours claim 降级或转向更窄的 RBAC/privacy admission。

## 当前禁止项

- 不跑没有 baseline ladder 的 GPU。
- 不把 `DONE` 背景结果直接写进最终主表，除非 evaluator / prompt contract 被复核。
- 不让 `PACT-pilot` 抢占主线，直到 gold/parser/contact 通过。
- 不把 State synthetic 分数当外部有效性。
- 不新增 benchmark 名单，除非它能填补当前矩阵中的明确空格。
