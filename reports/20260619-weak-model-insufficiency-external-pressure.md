# 弱模型能力不足：外部压力与待检验 handle

日期：2026-06-19  
本地证据包：`papers/weak-model-pressure-20260619/`  
雷达来源：`D:\develop\ArXiv_Daily_Digest\data\multi-agent-consistency\2026-W23..W25`

## 当前判断边界

“如何让弱模型参与强任务”已经不是空白。外部已经从四面包过来了：router/cascade 决定谁来答，abstention/selective prediction 决定该不该答，weak-to-strong/scalable oversight 研究弱监督强，Prover-Verifier 研究强输出怎样让弱 verifier 看得懂，AgentDropoutV2/Weaver/ProvenanceGuard 研究测试时拦截、弱 verifier 聚合和事实来源验证。

下面不是 novelty claim，只是外部压力之后暂时还值得验证的 handle：这些工作多数以“query、answer、final judgment、candidate response”为基本单位；我们可以继续压力测试一个更窄对象：在异构/能力不对称多 agent 通信里，一个弱 agent 产生的局部片段如何被限制权限、结构化提交、隔离、验证、再按字段进入接收方状态。它现在只能算候选研究缝隙，需要靠全文 collision、baseline 和实验再决定能不能站住。

## 先把最危险的撞车点摆出来

| 压力线 | 代表工作 | 它已经解决了什么 | 它会怎样打我们 | 仍需验证是否存在的空隙 |
|---|---|---|---|---|
| 异构 MAD 自适应控制 | ARMOR-MAD, HCP-MAD, Aggregated Confidence | 用异构模型池、预辩论路由、早停、离群降权、置信融合提升准确率/效率 | 审稿人会说“你这就是异构辩论路由/聚合” | 它们处理的是是否辩论、何时停止、最终答案如何聚合；较少处理弱 agent 的中间字段如何写入共享状态 |
| 错误传播拦截 | AgentDropoutV2 | 测试时拦截 agent 输出，纠错，无法修复就剪枝，阻断错误级联 | 会撞上“active firewall / rectify-or-reject”表述 | 它拦截的是 agent output；我们的机会是把 output 拆成 typed atoms，做字段级 allow/block/quarantine |
| query routing / cascade | FrugalGPT, RouteLLM, Hybrid LLM routing, dynamic routing survey | 把 easy query 给便宜/弱模型，hard query 升级给强模型，优化质量-成本 | 会把我们压成“路由器又一版” | routing 的单位是 query/model choice；我们要做 message/state-fragment admission，而不是任务分配 |
| abstention / selective prediction | LM Mostly Know, Abstention survey, AbstentionBench, SelectiveNet | 让模型知道什么时候不该答，给风险-覆盖曲线 | 会说“弱模型不足就 abstain/defer” | 多数工作停在模型是否回答；我们可把 abstention 变成通信动作：ask, request tool, submit partial atom, quarantine |
| weak-to-strong / scalable oversight | Weak-to-Strong Generalization, weak LLM judges, Weak Critics | 弱监督、弱 judge、弱 critic 如何帮助强模型 | 会说“弱模型监督强模型已有完整路线” | 需要检查它们是否已经覆盖运行时跨 agent 状态写入权限；目前看主要对象是训练信号、judge 协议、critique 蒸馏 |
| Prover-Verifier / legibility | Prover-Verifier Games, Decoupled PVG | 强模型输出能否被较小 verifier 检查，如何提升 legibility | 会说“强模型让弱模型可检查已经有人做” | 需要检查“弱 agent 只提交可验证微证据/微约束”是否只是 PVG 的自然实例 |
| 结构化 pipeline | Decomposed Prompting, DSPy, PAL | 把任务拆成模块、签名、程序、工具执行，降低 LLM 承担的自由推理负担 | 会说“micro-contract 只是 decomposition/signature” | 这些工作没有把能力不对称下的 state write 权限、污染风险和隔离区作为对象 |
| fact-level verification | Self-RAG, FActScore, SAFE, FacTool, RARR, ProvenanceGuard | 原子事实、来源、support、repair-and-reverify 已经很成熟 | 会说“你只是事实验证/来源验证” | 它们多在最终答案事实性；我们要看多 agent 通信过程中的 claim ownership、scope 和接收方状态污染 |
| 多弱 verifier 聚合 | Weaver | 多个弱 verifier 通过弱监督加权，接近强 verifier，节省验证成本 | 会撞上“弱模型传感器集成” | 它是 response selection/verifier ensemble；我们可做多弱 sender 的 state-fragment admission 和 downstream causal value |
| 异构 latent/protocol 通信 | Dense Latent Communication, TAP | 异构模型间的 KV-cache 对齐、文件式协议、跨运行时协作 | 会说“异构通信协议/latent communication 已经有了” | 它们强调通信载体/协议互操作；我们强调语义权限：哪些内容可被接收、何时进入状态 |

## 从 ArXiv_Daily_Digest 看到的近期雷达

这里的近期雷达很重要，因为它说明“异构/弱模型/多 agent 通信”正在迅速拥挤，不能再用宽泛题名。

| Digest 命中 | 关键点 | 对我们的压力 |
|---|---|---|
| ARMOR-MAD: Adaptive Routing for Heterogeneous Multi-Agent Debate | 真实异构 + 一致性路由 + 早停 + 离群降权，在 MATH/GSM8K/MMLU/MMLU-Pro 上优于固定轮次异构辩论 | 我们不能只讲“异构模型合作更好”；暂时要把问题从最终答案路由/聚合里剥出来 |
| See What I See, Know What I Think | Qwen3 4B/8B/14B 之间做异构 KV-cache dense alignment，降低文本通信成本 | “异构通信”这个词已经很热；我们的贡献不应落在通信带宽/latent alignment |
| Multiagent Protocols with Aggregated Confidence Signals | 跨模型置信度转化后软投票/贝叶斯融合，提升 AUARC | 标量 confidence 聚合已有人做；我们要做 typed confidence/action，而非单一系统置信 |
| AgentDropoutV2 | 拦截、纠错、拒绝 agent 输出，防止错误传播 | “防火墙/剪枝”已有人做；我们要强调字段级 admission，不是整条消息剪枝 |
| Weak Critics Make Strong Learners | 弱模型不做 judge，只给 non-misleading revision direction | 这非常接近“弱模型不是 solver”；可借它支撑，但要把 critic 变成通信动作/状态片段 |
| TAP file-based protocol | Claude/Codex 异构协作，文件保留原始消息，异构 pair 缺陷审查比例更高 | 协议层已有实践；我们要补语义层的 admission/ownership |
| ProvenanceGuard | 原子 claim + source-aware verification + allow/block/repair；强调 cross-source conflation | 这是最贴近 source-ledger 的强压力；如果要继续，差异要被实验证明为多 agent 运行时共享状态，而非最终答案来源验证 |
| Weak Critics / Weaver / Aggregated Confidence 一组 | 都在把弱信号变成可用监督/置信/验证 | “弱信号可用”不是新结论；可试探的对象是弱信号如何被授权进入状态 |

## 大家实际上都得出的共同结论

第一，弱模型不能被当成完整求解器。无论是 routing/cascade、abstention、Weak Critics，还是 small LM self-correction，都在承认一个事实：弱模型在难题上会乱答、误判、过度自信，直接让它输出最终答案或者做最终 judge 很危险。已有方法的主流做法是降低它的职责：只处理 easy query，只给 critique direction，只做 verifier 的一部分，只做局部模块。

第二，弱模型仍然有可用信号。FrugalGPT/RouteLLM 说明弱模型可覆盖一部分低难样本；Weak Critics 说明弱模型可能无法判对错，但能给“不误导的修改方向”；Weaver 说明多个弱 verifier 的噪声可以被加权聚合；FActScore/SAFE/Self-RAG 说明把长输出拆成原子事实后，局部判断比整答案判断稳很多。也就是说，弱模型的价值通常不在“最后拍板”，而在局部、低权限、可验证、可聚合的信号。

第三，一个可压力测试的动机是弱信号可能污染公共状态。Scalable oversight 里的弱 judge 会被强 consultant 说服；多 agent debate 会出现有害从众、相关错误放大、过早共识；AgentDropoutV2 明确把错误 agent output 当作会级联传播的风险；ProvenanceGuard 指出“有支持但归错源”也是独立错误。这些只能支持一个保守动机：通信不是只要信息越多越好，接收方状态也许需要 admission control。

第四，待验证的可能空隙是“准入单位”。很多工作在 query 级、answer 级、candidate response 级、agent output 级做路由/拒绝/选择。事实验证线虽然已经 atomize，但它多处理最终答案或 RAG 输出。多 agent 通信里，一个弱 sender 的“局部可用事实、局部错误推理、来源、可见范围、预算占用、需要追问的空洞”混在同一条自然语言消息里；这是否足以构成独立 state transition 问题，还要靠 baseline 对照确认。

## 待检验的研究 handle

我现在只把它当作值得继续压的 handle，不把它写成已有贡献。

**1. 弱模型的能力边界可以做成字段级权限。**  
例如弱模型不能提交 final answer，但可以提交 `observed_fact`、`source_pointer`、`counterexample_candidate`、`uncertainty_tag`、`need_info`、`easy_subproblem_result`。每个字段有不同验证器、预算和提升规则。这个比“弱模型该不该回答”细，也比“整条消息剪枝”细。

**2. Quarantine-first state 是一个自然机制。**  
弱 agent 的输出先进入隔离区，不直接写入 receiver context。只有通过 schema、source、support、scope、budget、conflict check 的片段能 promoted 到 public/private state。没有通过的片段也不必丢弃，可以触发追问、工具调用、强模型复核或保留为负证据。

**3. 把 abstention 变成动作空间，而不是终止符。**  
现有 abstention 多是“答/不答”。在多 agent 通信里，弱模型的“不足”应该输出结构化行动：`ask_sender`, `ask_stronger_agent`, `request_tool`, `submit_partial`, `mark_ambiguous`, `defer_final`. 这会把弱模型的无能变成系统可利用的路由信号。

**4. 评估指标要看污染与保留，而不只看最终准确率。**  
建议指标包括：wrong atom admission rate、useful weak atom recall、state contamination rate、downstream reversal caused by weak atom、quarantine recovery rate、ask/defer calibration、budget-normalized utility。这样才能避开一堆只报 accuracy/cost 的异构 MAD。

**5. 弱模型可以作为“反事实状态候选源”。**  
不要问弱模型“答案是什么”，而是问“如果把这个局部片段加入状态，会改变强模型的哪一步？”用 counterfactual admission 测量弱消息的 causal value。这个比 verifier ensemble 更像多 agent 通信研究。

## 暂时可压力测试的 story 版本

一个保守版本可以这样落，前提是后续实验确实显示它不同于 routing、防火墙和 fact verification：

> Existing heterogeneous multi-agent methods mostly decide which model should answer, whether debate should continue, or how final answers should be aggregated. We study a different unit of control: state admission. In capability-asymmetric communication, weak agents often produce mixtures of useful local signals and harmful unsupported reasoning. We introduce a typed quarantine-and-admission protocol that limits weak agents to verifiable micro-claims/actions and promotes only admissible state fragments into the receiver context.

中文说法：

> 现有异构多智能体方法主要控制“谁来答、要不要继续辩论、最后怎么聚合”。我们控制的是更小的单位：弱 agent 产生的状态片段能不能进入接收方上下文。弱模型常常同时带来有用局部信号和有害推理污染，所以系统需要一个 typed quarantine/admission 协议，把弱模型限制在可验证微片段和可执行通信动作上。

## 审稿人可能的攻击与防守

| 攻击 | 防守方式 |
|---|---|
| 这就是 routing/cascade | 明确实验单元不是 query-to-model assignment，而是 message/state-fragment-to-context admission |
| 这就是 AgentDropoutV2 | 做字段级 promotion/quarantine，而不是整条 agent output rectify/reject；报告 useful atom recall 与 contamination |
| 这就是 ProvenanceGuard/FActScore | 研究多 agent 运行时 shared state，而不是最终答案 fact-check；加入 sender ownership、receiver visibility、state transition |
| 这就是 Weak Critics | 借用“non-misleading direction”作为先验，但把 critic 输出变成 typed communication action |
| 这就是 DSPy/Decomp/PAL | 模块化 pipeline 是实现工具；候选变量是能力不对称下的准入权限和状态污染，但需要实验把它和普通 module signature 区分开 |
| 这只是 prompt engineering | 需要有可执行 schema、deterministic admission compiler、可复现实验矩阵和 ablation：free text / whole-output reject / typed quarantine / oracle admission |

## 建议下一轮外部压力实验

1. 固定同一批弱 sender 输出，比较四种接收策略：free transcript、whole-output reject/accept、typed quarantine、oracle admission。
2. 模型组合用同构和异构都做：Qwen small/large、DeepSeek/MiMo/Qwen 或本地可跑的 open model pair；不要只押一个传闻组合。
3. 每个样本记录 atom-level fate：submitted, quarantined, promoted, rejected, used in final, caused reversal。
4. 特别做“弱模型能力不足”切片：弱 sender 初答错但含有一个可用局部事实；弱 sender 初答对但推理污染；弱 sender 正确 abstain/错误 abstain。
5. 和 AgentDropoutV2、ARMOR-MAD、ProvenanceGuard 分别建立边界 baseline：整条输出防火墙、异构辩论路由、最终答案来源验证。

## 参考主源

近期/直接压力：
- ARMOR-MAD: https://arxiv.org/abs/2606.13197
- See What I See, Know What I Think: https://arxiv.org/abs/2606.13594
- Weak Critics Make Strong Learners: https://arxiv.org/abs/2606.00424
- TAP file-based protocol: https://arxiv.org/abs/2606.14445
- ProvenanceGuard: https://arxiv.org/abs/2606.18037
- Multiagent Protocols with Aggregated Confidence Signals: https://arxiv.org/abs/2606.13591
- AgentDropoutV2: https://arxiv.org/abs/2602.23258
- Weaver: https://arxiv.org/abs/2506.18203

基础/邻近压力：
- FrugalGPT: https://arxiv.org/abs/2305.05176
- RouteLLM: https://arxiv.org/abs/2406.18665
- Hybrid LLM routing: https://arxiv.org/abs/2404.14618
- Dynamic model routing survey: https://arxiv.org/abs/2603.04445
- Language Models Mostly Know What They Know: https://arxiv.org/abs/2207.05221
- Know Your Limits: https://arxiv.org/abs/2407.18418
- AbstentionBench: https://arxiv.org/abs/2506.09038
- Weak-to-Strong Generalization: https://arxiv.org/abs/2312.09390
- Prover-Verifier Games Improve Legibility: https://arxiv.org/abs/2407.13692
- Scalable oversight with weak LLM judges: https://openreview.net/forum?id=O1fp9nVraj
- Decomposed Prompting: https://arxiv.org/abs/2210.02406
- DSPy: https://arxiv.org/abs/2310.03714
- PAL: https://arxiv.org/abs/2211.10435
- Self-RAG: https://arxiv.org/abs/2310.11511
- FActScore: https://arxiv.org/abs/2305.14251
- SAFE long-form factuality: https://arxiv.org/abs/2403.18802
- FacTool: https://arxiv.org/abs/2307.13528
- RARR: https://arxiv.org/abs/2210.08726
