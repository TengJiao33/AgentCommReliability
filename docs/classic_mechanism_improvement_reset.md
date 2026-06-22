# 经典机制改善重置：把探索压回 Baseline、Benchmark 和指标

Snapshot date: `2026-06-18`.

## 核心判断

当前项目应切回经典机制改善论文的姿态：先冻结一个可运行的 `Ours` 条件，再把它放到近场 benchmark 上，与透明 baseline、强邻居 baseline、oracle/control 进行同表比较。

benchmark 确实是瓶颈，但瓶颈不主要来自 benchmark 名单不够多。真正卡住的是尺度没有冻结：哪些 benchmark 是主尺度，哪些 baseline 是主对照，哪些指标决定推进或退场，之前没有被压成同一张主表。因此新尝试即使有局部信号，也很难被读成“机制改善有效”。

这份文档把后续探索纪律改成一句话：

```text
每个实验都必须回答：Ours 相比哪个 baseline，在哪个 benchmark 的哪个指标上改善了什么，代价是什么。
```

## 之前的尝试到底算不算在这个方向上努力

算，但组织形态不够像经典机制改善论文。

已有工作已经在三个方向上接近这个目标：

- HiddenBench 线已经给出通信必要性和公共事实上界：`shared_only=1/65`，`full_info=59/65`，`oracle_public_facts=56/65`，旧 `exchange_then_decide=24/65`。这说明任务确实需要私有信息移动，也说明普通自由文本讨论不稳定。
- PerspectiveGap 线已经给出外部 role-routing 压力：官方风格 contact 中 oracle 可满分，而 all-to-all / copy-all 在 strict 上失败；本地 7B/14B smoke 显示 coverage、precision、distractor leak 之间存在张力。
- State Admission 线已经给出机制断点：direct admitted-state generation 会爆预算或过度承认，priority + executor 可以压低合法性错误；V2 中模型能列出大部分可见事实，却仍会在证据不足时强制作答。

问题在于这些结果没有汇入一张主表。Hidden 线像 benchmark 诊断，PerspectiveGap 线像 routing benchmark，State 线像内部机制显微镜；它们之间缺少同一套方法组、同一套指标族、同一套 go/no-go 规则。于是 baseline 看起来散，Ours 看起来也没有真正冻结。

## 新探索姿态

后续探索按经典机制改善论文推进。

1. 先冻结 `Ours`，再跑更多 variant。
2. 先画 baseline ladder，再决定 GPU run。
3. 每个 benchmark 只在能承载主表的一列或一组指标时进入实跑。
4. 每个 prompt、schema、executor 改动都必须对应一个 ablation 名称。
5. benchmark 构造只服务于测量缺口；它不能替代机制改善本身。
6. 新结果必须同时报告 task、routing、admission、sufficiency、cost，不能只报告 final answer。

这意味着“继续拓展新 benchmark”只有在一个条件下成立：现有近场 benchmark 无法测到 `source/scope/verification/rejection/evidence sufficiency/downstream decision` 的交叉缺口。否则应优先在已有 benchmark 上做干净对比。

## 当前应冻结的 Ours

建议暂名：

```text
Source-Scoped Evidence Admission Compiler
```

中文工作名：

```text
带来源与作用域的证据准入编译器
```

它的最小形态如下：

1. 输入是 source cards、recipient scope、verification / rejection state、role budget、候选答案或 role 任务。
2. 模型只负责提出 priority、candidate admission units、option-state 或 evidence-slot 判断。
3. 确定性 executor 负责执行 source/scope/budget/rejection 约束。
4. evidence sufficiency gate 在最终提交前检查证据槽位是否完整。
5. 输出包括 admitted units、rejected/quarantined units、final decision 或 insufficient evidence。

这个 Ours 的核心主张不该写成“让多智能体通信更可靠”这种大话。更稳的主张是：

```text
在角色可见性、来源归属、核验状态和上下文预算同时存在时，
把模型的语义判断与确定性准入执行分开，
能比自由文本通信、直接状态生成和普通共享上下文更稳定地控制证据进入下游决策。
```

## 主 benchmark 选择

主尺度先采用三层分工，避免把所有压力混成一锅。

| 层级 | Benchmark | 作用 | 当前读数 |
| --- | --- | --- | --- |
| 主机制尺度 | PerspectiveGap / source-ledger 变体 | 测 role-specific routing、coverage、precision、leak、budget | 外部 benchmark 接触最清楚，但不能单独证明 downstream decision |
| 主任务尺度 | HiddenBench clean subset / Hidden-State Admission v0 | 测 hidden/private facts 是否支持最终决策 | 通信必要性强，但原 benchmark 对 source/scope/rejection 不够完整 |
| 下游泛化尺度 | PACT-style split evidence pilot | 测 split evidence 能否通过结构化准入进入 QA | 需要先做 gold/parser/contact，不应直接大跑 |

当前不建议把 TeamBench、OSWorld、AppWorld、TheAgentCompany 作为主线首包。它们可以作为远期生态压力，但工程成本会掩盖机制问题。Docker-heavy benchmark 先保持 blocked 或 audit 状态。

## Baseline Ladder

后续主表至少包含这些条件。没有这些条件，结果不应被写成机制改善 claim。

| Condition | 作用 |
| --- | --- |
| `no_communication` / `shared_only` | 测通信必要性下界 |
| `full_info` | 测模型解题能力上界 |
| `oracle_public_facts` / `oracle_admissible_facts` | 测公共状态或准入状态表达上界 |
| `all_to_all` / `copy_all` | 测过度共享和泄漏 |
| `old_exchange` | 对照旧自由文本讨论 |
| `fact_only_exchange` | 测 message hygiene ceiling |
| `shared_verified_context` | 对 DeLM / PACT 类共享状态压力 |
| `CICL_style_card_packing` | 对 decision-aware evidence packing 压力 |
| `direct_admitted_state_generation` | 测 LLM 直接写 state 的边界 |
| `source_ledger_model_only` | 测模型是否能自行守住 source/scope |
| `priority_plus_executor` | 测模型偏好 + 确定性执行的增益 |
| `ours` | source-scoped evidence admission compiler |
| `oracle_executor` | 测 admission / packing 上界 |

`Ours` 必须与 `priority_plus_executor` 分清楚。如果 `Ours` 只是在 priority 后加一个普通预算裁剪，它缺少论文方法厚度；如果它加入 option-state / evidence-slot sufficiency gate，并且能解释 HiddenBench perturbation 的 abstention 问题，才有成为主方法的空间。

## 指标主表

后续所有 claim-bearing 实验统一映射到这些指标族。

| 指标族 | 读数 |
| --- | --- |
| Task success | final answer accuracy、EM/F1、downstream_ok、pass rate |
| Routing coverage | required fact recall、role-fragment coverage、missing-needed rate |
| Boundary precision | over-share rate、wrong-recipient rate、role precision |
| Leakage | distractor leak、private leak、scope violation |
| Source fidelity | source match、provenance correctness、citation correctness |
| Admission discipline | rejection recall、verification violation、quarantine respect |
| Evidence sufficiency | insufficient-evidence correctness、abstention correctness、slot completeness |
| Budget / cost | budget pass、tokens、messages、rounds、utility ratio |
| Oracle gap | 距 full_info、oracle_public_facts、oracle_executor 的差距 |

主表的首要目标是证明机制改变了正确的失败面：少过度共享，少泄漏，少不合规准入，同时不牺牲必要覆盖和最终任务。单纯让每一项都小涨没有足够论文价值。

## Hidden 线的瓶颈

Hidden 线的价值是自然任务与通信必要性。它已经证明自由文本讨论会污染，fact-only / oracle public facts 可以显著改善。

当前瓶颈是 ceiling 和指标不够细。HiddenBench 原形更擅长测最终决策和信息交换是否必要，不够擅长单独测 source、recipient scope、verification、rejection、evidence sufficiency。继续在原 HiddenBench 里追 sender prompt 小涨幅，很可能只是 message hygiene。

Hidden 线下一步应转为 task bridge：从已有 32 个 clean candidate 中抽 8-12 个，构造成小而硬的 Hidden-State Admission slice。这个 slice 必须带 source cards、scope rules、verification perturbation、evidence slots、expected abstention。它服务于 Ours 的下游验证，不能变成新的大 benchmark 工程泥潭。

## State 线的瓶颈

State 线的价值是机制显微镜。它已经暴露 direct state generation、priority executor、ledger-first hidden unit、option-state consistency、visible facts sufficiency 等断点。

当前瓶颈是人工度和外部有效性。V1/V2 的很多结构来自 builder，容易被审稿人读成 synthetic planning table。它可以帮助设计 Ours 和 ablation，但不能独自承载主 claim。

State 线下一步应收窄为两个问题：

1. 模型在显式 source/scope/verification 下，能否保持 option-state、admission units、rejections、final_decider state 的一致性。
2. executor / evidence-slot gate 是否把这种一致性失败转化为可测改善。

如果加入 explicit abstention 或 evidence-slot prompt 后 perturbation rows 接近 oracle，State 线应降级为 schema/control note。若 14B 在 option-state 已高的情况下仍然稳定失败于 rejection、absent units、abstention，一小包扩到 30-50 rows 才值得。

## Benchmark 的位置

benchmark 现在承担三件事：

1. 提供外部尺度，防止内部 packet 自洽。
2. 提供强 baseline 和 oracle/control，让方法改进能被读懂。
3. 暴露测量缺口，必要时支持小 benchmark construction。

benchmark 不应继续承担“让我们找到题目”的全部压力。题目现在已经收窄到 source-scoped evidence admission under downstream commitment。下一步要做的是用 benchmark 把这个题目测清楚。

## 立即停止的动作

- 停止新增无命名 prompt variant。
- 停止扩同款 State synthetic rows，除非它进入 baseline ladder 或 ablation 表。
- 停止把 MATH / TypeCast 当主 benchmark。
- 停止只报告 final answer。
- 停止没有 direct controls 的 HiddenBench 改写。
- 停止没有 packet audit / gold smoke / parser smoke 的 GPU run。
- 停止把 benchmark 大表继续扩成文献收集；大表下一步只服务于选择主尺度和 baseline。

## 下一步执行计划

### Step 1: 冻结主表骨架

产物：

- `docs/mechanism_baseline_matrix.md`

内容：

- 三个 benchmark 层级。
- baseline ladder。
- 每个 baseline 在每个 benchmark 上是否可跑、已跑、blocked。
- 每个指标的 scorer 来源。
- Ours 的固定配置。

完成条件：

```text
任何新 run 都能被填进这张表的一格。
```

当前状态：已落盘为 `docs/mechanism_baseline_matrix.md`，后续每次 claim-bearing run 都应先检查这张表。

### Step 2: 冻结 Ours v0

产物：

- `docs/source_scoped_evidence_admission_compiler_v0.md`

内容：

- 输入 schema。
- 输出 schema。
- executor 规则。
- evidence-slot sufficiency gate。
- 与 `priority_plus_executor`、`direct_admitted_state_generation` 的区别。

完成条件：

```text
同一份 Ours v0 可以在 PerspectiveGap slice、HiddenBench slice、PACT-style pilot 上复用，避免每个 benchmark 都重写一套方法。
```

当前状态：已落盘为 `docs/source_scoped_evidence_admission_compiler_v0.md`，下一步应实现 schema / compiler / PG40 adapter。

### Step 3: 做最小 baseline pilot

优先顺序：

1. PerspectiveGap 40-row source-ledger slice：先压 routing coverage / precision / leak / budget。
2. HiddenBench 8-12 seed admission slice：压 downstream decision / abstention / sufficiency。
3. PACT-style 10-20 row split evidence contact：只做 gold/parser/contact，不急着写 claim。

完成条件：

```text
至少一个 benchmark 上，Ours 相比 direct admitted state、old exchange、shared verified context、source-ledger model-only 显示非饱和差异。
```

### Step 4: Go / No-Go

Go 条件：

- Ours 在主机制尺度上同时改善 coverage/precision/leak/budget 中至少两个关键指标，且 task success 没有明显塌掉。
- Ours 在 HiddenBench slice 上减少不合规准入或错误强制作答。
- direct controls 显示任务本身可解，失败主要来自准入或证据充分性。

No-go 条件：

- `shared_verified_context` 或 `CICL_style_card_packing` 已经接近 oracle。
- Ours 只赢弱 prompt baseline，输给透明强 baseline。
- evidence-slot / abstention prompt 一改就解决主要失败。
- direct all-facts 或 oracle-admissible-facts 都不稳定，说明 benchmark slice 本身无法承载该 claim。

Pivot 条件：

- 若 Hidden / State 都被 ceiling 或 prompt artifact 压住，主线转向更自然的 RBAC / privacy / internal-channel admission。
- 若 PerspectiveGap 已足以承载 routing 机制，Hidden-State Admission v0 只保留为 downstream validation。

## 外部压力记录

当前外部压力可以这样读：

- DeLM / PACT 压 shared verified context 与 action-state public communication。
- CICL 压 decision-aware evidence packing 与 typed memory cards。
- PerspectiveGap 压 role-fragment assignment 与 leakage。
- ProvenanceGuard 压 answer 后 source-aware verification。
- DALA / Sparse-MAD / Cost of Consensus 压通信预算、拓扑和共识成本。
- AgentLeak / OrgAccess / RBAC 类工作会追问 internal channel、权限、泄漏与拒绝。

所以我们的空间必须固定在答前证据准入：同一事实对不同 recipient 的 admissibility 不同，且 admissibility 同时受 source、scope、verification、rejection、budget、evidence sufficiency 约束。

## 一句话纪律

以后不要再问“还能不能试一个新变体”。先问：

```text
这个变体能否成为 Ours、baseline、ablation 或 oracle/control 中的一项？
它会改变主表里的哪个指标？
如果结果出来，它会推进、削弱，还是终止当前机制 claim？
```

答不上来，就先不跑。
