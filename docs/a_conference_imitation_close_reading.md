# A 会模板细读：本项目应如何模仿

Snapshot date: `2026-06-18`.

## 核心判断

我们要模仿论文的压法，题面只作参考。最合适的主模板是 `PAL + Sparse MAD + Decomposed Prompting`：PAL 给出 LLM/compiler 职责分工，Sparse MAD 给出通信结构变量和 cost-aware 表格，Decomposed Prompting 给出模块化系统和可替换 handler 的叙事。ReAct 适合模仿 introduction 和 component ablation；AgentBench / SWE-bench 适合在 HSA 或 PerspectiveGap 扩成 benchmark contribution 时参考。

这意味着我们的论文应写成一个 test-time system / mechanism paper：模型负责提出 source-scoped evidence candidates 和 priorities，deterministic compiler 负责 source/scope/budget/rejection admission，下游 receiver 只使用 admitted public state。主表要证明这个分工在 same-backbone comparison 中比 free-form exchange、direct admitted-state prompting、source-ledger、transparent heuristic 更稳。

## 模板 1：PAL 的模仿方式

PAL 的问题定义很干净：CoT 让 LLM 同时负责分解和执行，模型能写出看似合理的步骤，却会在 arithmetic / symbolic execution 上犯错。PAL 的方法是让 LLM 生成 runnable intermediate program，把执行交给 Python interpreter。论文主表用同一个 Codex backend 比 DIRECT、COT、PAL，同时把 PaLM-540B 等大模型结果作为参考；关键 ablation 证明收益来自 interpreter，单纯 Python-style prompt 不足以解释收益。

我们应直接模仿这个逻辑。我们的对应问题是：free-form multi-agent exchange 让 LLM 同时负责发现证据、判断来源合法性、控制预算、拒绝无关信息和生成下游答案。已有信号显示模型可以产生有用候选，但 direct admitted state 会过预算、填空角色、乱收 evidence；compiler/executor 可以把预算和 closure 修干净。我们的 PAL 式写法应是：LLM is good at proposing candidate evidence, but unreliable at enforcing admission constraints; SSEAC offloads admission execution to a deterministic compiler.

PAL 的表格模仿规则：

| PAL 表格位置 | 我们的对应表格 |
| --- | --- |
| DIRECT | direct/free-form exchange 或 direct admitted state |
| COT | source-ledger / role-list / explicit reasoning prompt |
| PAL | SSEAC candidate generation + deterministic compiler |
| Python prompt without interpreter | model emits structured state but compiler disabled |
| meaningful variable-name ablation | source/scope/role/card id names removed 或 anonymized unit ablation |
| GSM-HARD stress | tight-budget PG40 / hidden-unit HSA stress |

最关键的一条：PAL 不只展示“代码 prompt 更好”，它专门证明 interpreter 是收益来源。我们也必须证明 compiler 是收益来源，所以要有 `structured_no_compiler`、`compiler_with_model_units`、`compiler_with_oracle_units`、`transparent_greedy` 四行。

## 模板 2：Sparse MAD 的模仿方式

Sparse MAD 的问题定义是：已有 multi-agent debate 多数使用 fully-connected communication，每个 agent 都能看到所有其他 agent 的回答，性能可能提高但 token cost 很高。论文把 communication topology 明确成图变量，用 density `D` 表示连接强度，比较 CoT、self-consistency、fully-connected MAD 和不同 sparse topology。它的强点在于同模型、同任务、同初始回答下比较 topology，并同时报告 accuracy 和 cost saving。

我们应模仿它把“通信方式”变成主变量。我们的对应变量是 evidence visibility / admission policy：free transcript、all-to-all evidence、shared-only、source-ledger、SSEAC admitted state、oracle admitted state。Sparse MAD 还固定 first-round individual responses 来降低方差，这对我们很有启发：做 routing/admission 对照时，应固定候选 source cards、固定 row order、固定 model seed / temperature，把变化集中到 admission policy。

Sparse MAD 的表格模仿规则：

| Sparse MAD 行 | 我们的对应行 |
| --- | --- |
| CoT | no-communication / direct answer |
| Self-consistency | multi-sample direct 或 prompt-arm voting |
| Fully-connected MAD | free-form exchange / all-to-all context |
| Sparse MAD D values | admitted-state policies with different visibility budgets |
| Accuracy | downstream strict / task success |
| Cost saving | input tokens / admitted card count / budget pass |

最该借的是它的审稿说服力：communication restriction 可以同时保住质量、降低成本、改善可诊断性。我们的主张也应是：source-scoped admission 可以在不全收上下文的情况下提高 reliability，并降低 leakage / over-admission / budget violation。

## 模板 3：Decomposed Prompting 的模仿方式

Decomposed Prompting 的核心是软件库式分解。它把复杂任务拆成 top-level decomposer 和 sub-task handlers，每个 handler 可以单独调 prompt、替换成 trained model 或 symbolic function。论文把 handler 的可 debug、可替换、可复用写成贡献，而没有停在“分解有效”的表层叙述。

我们应模仿它的系统图和方法章节。SSEAC 可以写成四个 handler：candidate-unit generator、source/scope validator、priority estimator、admission compiler。前两个可以是 LLM prompt，后两个可以部分符号化；compiler 是固定接口。这样写，SSEAC 会呈现为一个可替换的 admission pipeline，避免退化成大 prompt。

Decomposed 的表格模仿规则：

| Decomposed 组件 | 我们的对应组件 |
| --- | --- |
| decomposer prompt | task-to-evidence-unit generator |
| sub-task handler | source/scope checker, priority estimator, downstream answerer |
| symbolic retrieval function | deterministic compiler / budget executor |
| NoDecomp-Ctxt baseline | direct full-context / all-scoped baseline |
| Decomp-Ctxt model | SSEAC admitted-state route |
| post-processing handler | repair / JSON normalizer / deterministic prompt writer |

这条模板要求我们把接口写清楚：输入是什么，输出 schema 是什么，哪些字段是 prediction-time allowed，哪些字段是 evaluator-only forbidden。这样 reviewer 会把我们看成 method system，减少 prompt collection 的质疑。

## 模板 4：ReAct 的模仿方式

ReAct 的引言方法是先指出两个能力长期分开研究：reasoning 和 acting。它提出 interleaved thought-action-observation trajectory，再用 Standard、CoT、Act、ReAct 做组件对照。它的实验覆盖 QA、fact verification、interactive decision-making，并且强调 interpretability 和 diagnosability。

我们可以模仿它的开场结构。我们的两个分裂能力是 communication 和 admission：现有 multi-agent work 关注 agent 如何交换文本，较少把“哪些信息可以进入公共状态”作为可执行对象；state-admission / verifier 类工作关注状态合法性，但没有足够放到 role-specific communication benchmark。我们提出 source-scoped evidence admission，把 evidence proposal 和 admission execution 组合成可检查 trajectory。

ReAct 的 ablation 对我们很重要：

| ReAct ablation | 我们的对应 ablation |
| --- | --- |
| Standard | direct no-communication |
| CoT | reasoning-only / source-ledger text |
| Act | route/action-only without admission reasoning |
| ReAct | candidate evidence + admission compiler + downstream answer |
| prompt robustness | seed / prompt-arm / model-family robustness |
| human inspectability | violation cards and admitted-state trace |

这条模板适合写 Introduction 和 Figure 1。Figure 1 应展示 free transcript 如何导致 leakage / over-admission，以及 SSEAC trajectory 如何把 evidence candidates、rejections、admitted state、downstream answer 串起来。

## 模板 5：ChatEval 的模仿方式

ChatEval 的可借点是 role diversity 和 communication strategy ablation。它比较 single-agent、multi-agent without diverse role prompts、multi-agent with diverse role prompts，并研究 communication strategies、role numbers 和 discussion turns，给多 agent 设置提供了可拆 ablation。

这给我们的提醒是：如果使用 role-specific routing，就必须把 role 本身当 ablation。PerspectiveGap 的 raw 7B/14B 结果已经显示，coverage 提高可能伴随 distractor leakage 上升。我们的表格要把 role-aware routing、role-agnostic routing、all-role flooding、source-scoped routing 放在一起，并报告 leakage。

ChatEval 可模仿的部分很有限。它主要用于 LLM-as-evaluator，容易把多 agent 讨论的好处写得偏软。我们只能借 role/communication ablation 的形状，不能借它当主理论。

## 模板 6：AgentBench / SWE-bench 的模仿方式

AgentBench 和 SWE-bench 是 benchmark-paper 模板。AgentBench 的贡献是多环境 agent benchmark、29 个模型评测和 failure reasons；SWE-bench 的贡献是真实 GitHub issue、可执行环境、Fail-to-Pass tests 和强烈的模型能力缺口。它们都没有把“赢闭源榜首”当作论文成立条件，重点是定义一个 frontier capability gap 并提供可复现 evaluator。

如果 HSA-v0 或 PerspectiveGap 后续扩展成我们的 benchmark contribution，这两篇是模板。我们要证明现有 communication benchmarks 测不到 admission/scope/rejection，要给可执行 scorer、oracle/control rows、failure taxonomy 和 released artifacts。当前阶段更适合 method paper，benchmark paper 作为 P2 路线保留。

Benchmark 模板对应规则：

| Benchmark-paper 元素 | 我们的对应元素 |
| --- | --- |
| real or externally motivated tasks | HiddenBench / PerspectiveGap / PACT-style split evidence |
| executable evaluator | PG scorer / HSA scorer / compiler checks |
| frontier gap | direct exchange fails on strict admission or leakage |
| model sweep | Qwen2.5 7B/14B, Mistral, Llama, optional closed reference |
| failure taxonomy | missing evidence, distractor leakage, over-budget, forced commitment, unsupported answer |

## 我们的论文骨架应长这样

暂定题目方向：

```text
Source-Scoped Evidence Admission for Reliable Multi-Agent Communication
```

Introduction 结构：

1. Multi-agent LLM systems increasingly rely on agents exchanging natural-language messages.
2. In role-specific and partially observed tasks, the hard part is not only what agents say, but which source-scoped evidence is allowed to become public state.
3. Free-form transcripts entangle evidence discovery, source authorization, budget control, rejection, and downstream answering, causing missing evidence, distractor leakage, over-admission, and unsupported commitments.
4. We propose SSEAC, a test-time admission pipeline where LLMs propose candidate evidence units and priorities, while a deterministic compiler enforces source/scope/budget/rejection constraints.
5. Across PerspectiveGap/PG40, HSA-v0, and State Admission slices, we compare against direct prompting, free exchange, source-ledger prompts, transparent heuristics, and oracle controls using strict task metrics plus evidence-discipline metrics.

Main method figure：

```text
private/source cards
-> LLM candidate evidence proposal
-> source/scope/priority schema
-> deterministic admission compiler
-> admitted public evidence state
-> downstream answer / abstention
-> violation card diagnostics
```

Main table layout：

| Row family | Conditions |
| --- | --- |
| no communication | direct answer / shared-only |
| free communication | old exchange / all-to-all transcript |
| text-structured communication | role-list / source-ledger |
| model-only admission | direct admitted state / structured no compiler |
| transparent baseline | utility-density greedy / all-scoped / eligible-all |
| ours | SSEAC model units + compiler |
| oracle | oracle admissible / oracle assignment-to-prompt |

Metrics layout：

| Metric group | Metrics |
| --- | --- |
| task | strict pass, downstream answer accuracy, abstention correctness |
| evidence | coverage, precision, slot recall |
| safety | distractor leakage, extra final cards, forced commitment |
| execution | budget pass, closure violations, compile rate |
| efficiency | prompt tokens, admitted cards, cost |

## 立即影响到实验方向

第一，PG40/HSA 小样本模型 run 要优先产生 `structured_no_compiler` 和 `SSEAC+compiler` 两行。PAL 模板要求我们证明 compiler 是真正变量。

第二，所有 communication 对照都要加入 cost 或 budget 指标。Sparse MAD 模板要求我们别只看 strict，必须报告 admitted card count、budget pass、input token 或 over-admission。

第三，PerspectiveGap official full grid 可以当 ReAct 式 “diverse benchmark” 的一部分，但它不能抢走主线。它应服务于 same-backbone component ablation。

第四，如果模型输出暂时输给 transparent heuristic，论文仍可能成立，但 claim 要收窄到 compiler/admission decomposition 和 failure taxonomy。若 SSEAC 在 PG40 或 HSA 上超过强 baseline，主张就能升级成 method improvement。

## 参考源

| 论文 | 入口 |
| --- | --- |
| PAL: Program-aided Language Models | https://proceedings.mlr.press/v202/gao23f.html |
| ReAct: Synergizing Reasoning and Acting in Language Models | https://openreview.net/forum?id=WE_vluYUL-X |
| Decomposed Prompting | https://openreview.net/forum?id=_nGgzQjzaRy |
| Improving Multi-Agent Debate with Sparse Communication Topology | https://aclanthology.org/2024.findings-emnlp.427/ |
| ChatEval | https://openreview.net/forum?id=FQepisCUWu |
| AgentBench | https://openreview.net/forum?id=zAdUB0aCTQ |
| SWE-bench | https://openreview.net/forum?id=VTF8yNQM66 |
