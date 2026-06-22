# 旧实验信号审计：哪些还值得带进主线

Snapshot date: `2026-06-18`.

## 核心判断

旧实验里确实有很多真实信号。它们大多分散在不同尺度上：有的证明通信对象会污染下游判断，有的证明输出契约能显著改变分数，有的证明模型能读懂 source/scope ledger，有的证明确定性 executor 能把非法选择压下去。它们共同指向一个方向：多智能体通信可靠性里的关键难点，是把私有、不完整、带来源约束的信息转成可准入的 public state，再让下游任务只使用这部分状态。

当前卡住的地方也清楚：旧信号缺少同一张主表。很多报告当时能说“信号强”，因为它们在本地对照里有大 gap；但它们没有同时满足外部 benchmark、强 baseline、冻结 Ours、统一 evaluator、下游 task metric 这五个条件。所以它们能支持研究方向，暂时不能直接组成 SOTA 结果。

因此现在的动作应理解为信号升格，而非“重新填表把旧东西清零”：把旧实验里最有价值的机制信号，迁移到可比较的 benchmark x baseline x metric 矩阵里。能升格的留下，暂时无法升格的保留为失败解释和设计约束。

## 信号分层

| 层级 | 含义 | 当前判断 |
| --- | --- | --- |
| A. 主张候选 | 有明确 baseline gap，并且能迁移到当前主表 | HiddenBench fact-state discipline；State Admission V1.1 priority + executor；PerspectiveGap source/scope ledger + compiler |
| B. 机制显微镜 | 能解释失败机制，但样本、任务或 evaluator 暂不适合做主结果 | TypeCast / MATH operator lifecycle；PACT final-answer contract；State Admission V2 小切片 |
| C. 归档经验 | 给过方向感，但已有更强或更干净的后续证据 | 早期 MAD-MM、DAR、MOC、小规模 peer-redaction / authority probes |

## A 层：最值得带进主线的旧信号

### 1. HiddenBench：fact-state discipline 是真信号

HiddenBench V2 Stage 1 到 Stage 4 是旧报告里最干净的外部任务信号。Full65 上，`shared_only` 只有 `1/65`，`full_info` 是 `59/65`，`oracle_public_facts` 是 `56/65`，说明任务确实需要私有信息被正确移动到公共状态。旧的自由文本 `exchange_then_decide` 只有 `24/65`，在 clean subset 上是 `23/55`；`fact_only_exchange` 能到 `55/55`。

后续 ablation 也有价值。单纯禁止推荐不够，`no_recommendation` 只有 `28/55`；`no_shared_repeat` 是 `31/55`。Stage 3 的 `blind_minimal_exchange` 到 `55/55`，Stage 4 里多种最小事实可见性条件也接近满分。这说明关键瓶颈包含 sender 输出对象的类型：自由文本讨论容易混进推荐、共享信息复述和解释性污染；事实状态卡片能把下游判断拉到 oracle-public-facts 级别。

这个信号的边界也必须保留。HiddenBench clean subset 已经被 fact-only / blind-minimal 打到 `55/55`，所以它更适合作为 HSA-v0 的种子和 oracle-gap 校准，不适合单独承担“新方法大幅超过强 baseline”的最终表格。

主要证据：`reports/20260617-hiddenbench-v2-stage1-full65-qwen25-14b.md`，`reports/20260617-hiddenbench-v2-stage2-sender-ablation-full65-qwen25-14b.md`，`reports/20260617-hiddenbench-v2-stage3-blind-sender-full65-qwen25-14b.md`，`reports/20260617-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b.md`。

### 2. State Admission V1.1：priority + executor 是最像方法的信号

State Admission V1.1 是当前最像“经典机制改善”的旧信号。14B direct generation 在 40 行上是 `0/40`，因为模型会超预算或选错单位；priority + deterministic executor 到 `28/40`，pair-group-primary recompile 到 `33/40`。7B 复现里，priority + pair-group-primary 是 `25/40`，normalized 是 `26/40`，fallback-required 到 `31/40`。它的价值超过 final-answer prompt tweak：它把“模型负责语义偏好，程序负责 scope/budget/rejection”的边界跑出了可重复的增益。

这个信号最值得升格，因为它天然对应当前 SSEAC 的方法形状：LLM 产出候选证据与优先级，compiler/executor 负责合法准入、预算和拒绝。它也能解释为什么我们现在必须做 compiler，而不能继续让模型直接写 admitted state。

边界同样很硬。V1.1 是 synthetic，bundle/group/cost/utility 都暴露得太清楚；`group_density_global` baseline 已经有 `32/40` 且 utility `0.9666`，压住了不少方法空间。也就是说，V1.1 证明“LLM + executor”方向成立，但它不能单独证明比强符号 baseline 更好。

主要证据：`reports/20260618-state-admission-v1-local-baselines.md`，`reports/20260618-state-admission-v1-priority-executor-pressure.md`，`reports/20260618-state-admission-v1-priority-7b-replication.md`，`reports/20260618-state-admission-v1-ledger-hidden-unit-pressure.md`。

### 3. PerspectiveGap：source/scope ledger 与 compiler 有真实价值

PerspectiveGap 是更接近外部压力的 routing/admission benchmark。Rotated source/scope 条件下，旧 role-list 方法崩得很厉害：7B coverage `0.076`、precision `0.135`；14B coverage `0.150`、precision `0.197`。Source-ledger 让 7B 到 coverage `0.574`、precision `0.745`，14B 到 coverage `0.854`、precision `0.779`，并且 reject recall 为 `1.0`。这说明 source/scope ledger 真的改变模型能否在角色约束下移动信息。

Budget compiler 又把另一个问题打清楚。14B raw source-ledger strict 只有 `3/40`，budget pass `0.225`；compiler 后 strict 到 `12/40`，coverage 保持 `0.854`，precision 和 budget pass 都到 `1.000`。这和 State Admission 的结论一致：模型能给有用候选，但预算、来源、scope 约束需要确定性层接管。

PG40 的坏消息也很重要。tight-budget V0 里 `utility_density_greedy` 已经是 `25/40`、utility `0.9825`；source-ledger 14B compiled 只有 `11/40`、utility `0.8707`。所以 PG40 当前告诉我们：现有 Ours 还没有赢，强 baseline 很强，下一步要跑 SSEAC prompt runner，旧 source-ledger 数字只能作为机制背景。

主要证据：`reports/20260618-perspectivegap-source-ledger-rotated20.md`，`reports/20260618-perspectivegap-budget-compiled-source-ledger.md`，`reports/20260618-perspectivegap-tight-budget-source-ledger.md`，`reports/20260618-sseac-v0-pg40-prediction-converter.md`。

## B 层：保留为机制显微镜的旧信号

### 4. State Admission V2：自然化方向对，但规模太小

V2 把 synthetic admission 往 HiddenBench-derived option-state 迁移，是方向正确的桥。9 行切片里，7B option-state-first 的 option_state_recall 是 `0.611`、downstream `0.222`；14B option-state-first strict 是 `0.111`、option_state_recall `0.9259`、downstream `0.4444`。visible-facts ablation 里，visible facts precision `0.9544`、recall `0.9861`，但 perturbation downstream 为 `0`。

这组结果很有诊断价值：模型能抽到大量可见事实，却仍不能保证下游充分性和最终决策，说明瓶颈已经从“能不能看见事实”推进到“准入状态是否足以支持任务”。但它只有 9 行，不能当主结果。它应该变成 HSA-v0 的设计输入，尤其是 abstention、slot completeness、evidence sufficiency 指标。

主要证据：`reports/20260618-state-admission-v2-option-state-and-direct-controls.md`，`reports/20260618-state-admission-v2-visible-facts-ablation.md`，`reports/20260618-state-admission-v2-abstention-gate-ablation.md`。

### 5. TypeCast / MATH：operator-level boundary 是有价值词汇

TypeCast 和 MATH 线已经退下主线，但留下了重要机制词汇。MATH operator lifecycle v1 在 166 行里 controls 稳定，161 行 correct，5 行 wrong；typed partial derivation 出现 `3/16` operator candidates/errors，shared workspace 与 verifier-visible final artifact 有 direct uptake。Repaired TypeCast control-stable117 上，quarantine / self / unrelated 是 `0/11`，但 inert visible scratch、direct peer、shared、verifier 都是 `2/11`，typed-rederive 是 `1/11`。

这些结果说明 answer removal 不能保证安全，operator、equation、numeric role、relation skeleton 仍可能被 receiver 继承。它们对当前主线的价值，是提醒我们在 benchmark 里不能只看 final answer，要看 evidence unit、source、scope、admission、sufficiency。

这条线不能继续承担主 benchmark。原因是旧 MATH200 raw-gold diagnosis 发现 trace gold 和 raw boxed answer 不一致达到 `98/200`，而且很多结果受 parser、prompt contract 和样本集中影响。它适合解释失败，不适合继续扩 GPU。

主要证据：`reports/20260617-math-operator-lifecycle-v1-qwen25-14b.md`，`reports/20260617-typecast-repaired-controlstable117-qwen25-14b.md`，`reports/20260616-typecast-math200-clean-rawgold-diagnosis.md`。

### 6. PACT final-answer contract：强提醒，弱主张

PACT final-answer contract 在 HotpotQA50 上给过很大的表面提升：original `17/50` EM、avg F1 `0.508`；contract 后 `34/50` EM、avg F1 `0.792`，wrong-to-right 有 20 例，right-to-wrong 有 3 例。这是非常强的“输出契约会改变结果”的提醒。

但它的主张承载力有限。这个结果同时改变了 final-answer surface、generation contract 和评测形态，样本只有 50 行，不能说明通信协议本身改善了 evidence exchange。它适合作为 PACT-style split evidence pilot 的警报：未来必须同时报告 supporting evidence recall、irrelevant evidence admission、answerability 和 EM/F1，不能只看最终字符串。

主要证据：`reports/_archive/20260616-pruned/20260614-pact-final-answer-contract-gpu.md`。

## C 层：归档但不要遗忘

MAD-MM、DAR、MOC、早期 peer-redaction、field-authority、answer-contract verifier 等报告不该重新变成主线。它们的价值在于给过 taste：多智能体通信失败常常来自消息保留、角色混淆、错误 surface 继承、final-answer artifact 和 budget/context shape 的共同作用。

这些旧线索如果要复活，必须满足一个条件：它们能填进当前主表的一个空格。比如 DAR 的 guarded answer diversity 可以作为 `old_exchange` 或 `answer-diversity control` 的对照；MAD-MM 只能作为 reproduction contact；MOC 只能作为 merge topology 的背景。没有 benchmark cell，就不要再给它们开新分支。

主要证据：`docs/evidence_register.md` 的 E-017、E-021、E-023、E-044，以及 `reports/_archive/20260616-pruned/` 下的早期报告。

## 为什么以前“信号很多”，现在又觉得没有结果

第一，以前很多信号是 local contrast signal。它们在本地对照里非常明显，比如 `23/55` 到 `55/55`、`0/40` 到 `33/40`、`3/40` 到 `12/40`、`17/50` 到 `34/50`。这些都该被尊重。

第二，这些信号没有被同一把尺子收束。不同实验用了不同任务、样本、evaluator、prompt contract、oracle 控制和 baseline。它们能说明“这里有机制”，却很难直接比较“哪个方法强”。

第三，一些旧信号被强 baseline 压住了。State V1.1 里 group-density baseline 很强；PG40 里 utility-density greedy 很强；HiddenBench clean subset 里 fact-only 已经打到 oracle 级别。强 baseline 的存在让故事更健康，也让 claim 更窄。

第四，外部 benchmark 压力改变了我们对价值的排序。TypeCast/MATH 的机制很有意思，但外部任务不够自然；HiddenBench/PerspectiveGap 更贴近 role-specific routing、partial observability、信息准入和通信必要性，所以更适合带主线。

## 现在该怎样用旧信号

当前主线应该保留三根骨头：

1. HiddenBench 告诉我们：公共事实状态的输出契约可以把自由文本 exchange 的失败大幅压下去。
2. State Admission 告诉我们：模型负责语义候选，compiler/executor 负责合法准入，是比 direct admitted state 更可靠的机制形状。
3. PerspectiveGap 告诉我们：source/scope ledger 在外部 routing 压力下有价值，但 tight-budget 强 baseline 会直接检验这个机制是否足够强。

这三根骨头合起来，才是当前 SSEAC / HSA 方向的合理来源。它们并没有证明我们已经有 SOTA；它们证明我们有一个值得冻结、重跑、和强 baseline 硬碰的 classic mechanism improvement 候选。

## 对当前大表的影响

当前大表仍处在填表和冻结阶段，但它的实质更接近“旧信号升格”，而非低价值的行政填表。它是在把旧信号从零散报告升级为可比较结果。最小主表应该优先填：

| Benchmark | 最该带入的旧信号 | 必须补齐的对照 |
| --- | --- | --- |
| `PG40` | source/scope ledger + compiler；tight-budget scorer | utility-density greedy；oracle；SSEAC prompt runner |
| `HSA-v0` | HiddenBench fact-only / blind-minimal / old exchange 差距 | shared-only；full-info；oracle-admissible；SSEAC |
| `SA-V2` | option-state / visible-facts / sufficiency failure | direct allfacts；direct admissible；oracle executor；SSEAC adapter |
| `PACT-pilot` | final-answer contract 警报 | full-context；split no-comm；shared verified context；evidence recall |

## 最短下一步

先不要再开新的宽 benchmark。先把旧信号升格成两条可运行主表线：

1. 在 `PG40` 上补 `ours_sseac_v0` prompt runner，直接和 `utility_density_greedy`、`source_ledger_14b_compiled`、oracle 比。
2. 从 HiddenBench clean failures 生成 `HSA-v0` 小切片，保留 `old_exchange`、`fact_only`、`oracle_admissible`、`ours_sseac_v0` 四个核心条件。

如果这两条线都没有超过强 baseline，就该把论文主张收窄到“source-scoped evidence admission as a diagnostic/compiler discipline”。如果至少一条线在强 baseline 下出现稳定增益，再谈扩 benchmark、跨模型和主论文表。
