# 异构 / 能力不对称多 Agent 论文大表（全文阅读版）

日期：2026-06-19  
口径：这轮只看“异构 / 能力不对称 / 信息不对称 / 权限不对称 / 工具与运行时不对称”的 multi-agent 工作；没有用我们自己的 SSEAC / 准入机制作为筛选器。候选来自本地 ArXiv_Daily_Digest 线索、项目 reading queue、外部主源检索，并下载 PDF 后转成全文文本检查。证据包在 `papers/heterogeneous-asymmetric-20260619/`，含 `pdfs/` 与 `texts/`。

## 一句话判断

这个方向已经很拥挤，尤其是 A 会层面：ReConcile（ACL 2024）、MetaGPT/ChatEval（ICLR 2024）、AutoGen（COLM 2024）、iAgents（NeurIPS 2024）、Mixture-of-Agents（ICLR 2025）、MasRouter（ACL 2025）、M2CL/TUMIX/AgentPO（ICLR 2026）都已经覆盖了“多模型/多角色/多工具/多上下文”的一部分。当前底层问题已经从“异构 agent 会不会更强”推进到四件硬事：

1. 谁该参与、用哪个模型、花多少钱：X-MAS、MasRouter、AMRO-S、ARMOR-MAD、SciOrch、Chimera。
2. 强弱 agent 如何协作：Guided HMAS、Teams Hold Experts Back、EARS、HACPO。
3. 异构到底是否有净收益：MoA 与 Self-MoA 对冲，Agent Scaling / Science of Scaling 给出负条件。
4. 信息不对称如何通信：iAgents、Communication & Verification、AsymPuzl、Memory Sharing。

我没有找到可信主源支持“ds + mimo + qwen 三模型合作达到 GPT-5.5 水平”这个精确说法。能找到的相邻学术脉络是 MoA / X-MAS / routing / tool-use mixture / latent communication，并没有一个公开主源把这个组合以论文形式写成该 claim。

## 主表

| # | 论文 / 主源 | 状态 | 异构 / 不对称对象 | 它解决的问题 | 核心机制 | 全文实验信号 / 读到的结论 | 对我们方向的压力 |
|---:|---|---|---|---|---|---|---|
| 1 | [X-MAS: Towards Building Multi-Agent Systems with Heterogeneous LLMs](https://arxiv.org/abs/2505.16997) | arXiv 2025 | 不同 LLM 在领域、功能上能力不同 | 同一 MAS 拓扑里，所有角色用同一个模型会浪费模型特长 | X-MAS-Bench 评估 27 个 LLM 在 5 类任务、5 类 MAS 功能上的能力；X-MAS-Design 替换各角色底层 LLM | 全文报告没有单一 LLM 在所有 domain/function 上最优；异构配置在 MATH、AIME 上显著优于强同质基线，文中写到 MATH 最高 +8.4%，AIME 系列有大幅提升 | 直接覆盖“异构 LLM 该如何组队”这一层；如果我们只说“模型不对称”，会撞上它 |
| 2 | [Guided Collaboration in Heterogeneous Multi-Agent Systems](https://arxiv.org/abs/2602.13639) | arXiv 2026 | 强模型 / 弱模型能力差 | 强弱组合经常比弱弱组合还差，弱 agent 无法吸收强 agent 指导 | Entropy-Based Adaptive Guidance：用表达、结构、相关性等熵指标估计弱 agent 理解状态，动态调节 guidance 强度；再加 RAG 记忆成功协作经验 | GSM8K、MBPP、CVRP 上强弱组合收益最大；全文给出多组从 baseline 到 guided/RAG 的提升，强弱协作的方差下降 | 它已经把“能力不对称协作失败”说成 cognitive mismatch；我们要避免只重述强弱帮助 |
| 3 | [Multi-Agent Teams Hold Experts Back](https://arxiv.org/abs/2602.01011) | arXiv；检索页显示 ICML 2026 accepted | 团队中有明显 expert / non-expert | 团队无法利用专家，甚至把专家拉低 | 诊断 expertise dilution：区分 non-expert deference、integrative compromise、expert persistence 等行为 | 全文结论很硬：团队常低于最佳个体，知道谁是专家也不够；损失最高可到 37.6%；团队变大更糟，但对恶意 agent 有一定鲁棒性 | 强负压：异构团队不是自动增益；要证明机制能保护专家信号 |
| 4 | [ReConcile: Round-Table Conference Improves Reasoning via Consensus among Diverse LLMs](https://aclanthology.org/2024.acl-long.381/) | ACL 2024 long | 不同 LLM / 不同解释 / 不同信心 | 多模型推理输出怎么合成，怎样从多样性里拿到稳定答案 | Round-table discussion，confidence、convincing sample、confidence-weighted voting | 7 个 benchmark 提升；ablation 里去掉 multiple models 损失最大；ANLI 上较 Debate 明显提升 | A 会已覆盖“多模型共识 + 加权投票”；不能把多模型 debate 当新点 |
| 5 | [Mixture-of-Agents Enhances Large Language Model Capabilities](https://openreview.net/forum?id=h0ZfDIrj7T) | ICLR 2025 | 多个 proposer LLM + aggregator LLM | 如何用多个 LLM 的互补输出提升生成质量 | 分层 MoA：每层多个 LLM proposer，后层看到前层输出，最终 aggregator 综合 | AlpacaEval 2.0、MT-Bench、FLASK 上强；开源 MoA 在 AlpacaEval 2.0 报告 65% 左右，超过 GPT-4o 基线；多样 proposer 有帮助但延迟上升 | 覆盖“异构模型堆叠能变强”；我们的贡献需要落在通信/可靠性/约束，而非简单混合 |
| 6 | [Rethinking Mixture-of-Agents: Is Mixing Different LLMs Beneficial?](https://arxiv.org/abs/2502.00674) | arXiv / OpenReview TMLR 页面 | 同模型多采样 vs 异模型混合 | 异构本身是否带来收益，还是高质量模型重复采样更好 | Self-MoA：只用同一个强模型产生多个响应再聚合；分析质量-多样性 trade-off | 全文给出 Self-MoA 常超过 Mixed-MoA；混入弱模型会拉低平均质量；多样性要受质量约束 | 很重要的反证：不能把 diversity 当无条件好东西 |
| 7 | [LLM-Blender: Ensembling Large Language Models with Pairwise Ranking and Generative Fusion](https://arxiv.org/abs/2306.02561) | ACL Findings 2023 / arXiv | 多个 LLM 输出质量不一 | 如何选择并融合多个模型候选答案 | PairRanker 成对比较候选，GenFuser 融合 top outputs | MixInstruct 上证明 rank + fuse 优于简单选择；是 MoA 前史 | 说明“多模型输出融合”很早就不是空白 |
| 8 | [Understanding Agent Scaling Laws Through the Lens of Agent Diversity](https://openreview.net/forum?id=9BN2W5BCfE) | ICLR 2026 Workshop | persona、model、full diversity | 多 agent 数量扩张为何有 diminishing returns，什么 diversity 有用 | information-theoretic usable evidence / effective channels K*；L1-L4 diversity 层级 | 全文结论：多样性在同 compute 下常胜过简单加 agent；正确路径多样性比总多样性更能预测表现；agent 过多可伤害 | 给我们一个评价压力：要说清“哪种不对称提供有用证据” |
| 9 | [Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296) | arXiv 2025 | 模型能力、拓扑、任务结构、异构配置 | 什么时候 MAS 比 SAS 强，什么时候 coordination overhead 吃掉收益 | 260 个配置，五类 architecture，三家模型家族；拟合 performance 与 capability/coordination/task metrics | R2CV 0.373，任务化能力指标 0.413；单 agent baseline 超过约 45% 后多 agent 常负收益；13 个异构配置没有绕开 capability-saturation | 负压很大：若任务不需要协作，异构 MAS 会变成成本噪声 |
| 10 | [MasRouter: Learning to Route LLMs for Multi-Agent Systems](https://aclanthology.org/2025.acl-long.757/) | ACL 2025 long | 不同 LLM、不同 role、不同 collaboration mode | MAS 中要同时决定协作模式、角色分配、模型选择 | 级联 controller：mode router、role router、model router；在 utility-cost 之间做选择 | MBPP/HumanEval/MMLU/MATH 等上提升；全文 ablation 显示 model routing 移除伤害最大；还能降成本 | 覆盖“异构 agent 选择/路由”主问题 |
| 11 | [AMRO-S: Efficient and Interpretable Multi-Agent LLM Routing via SLM and Ant Colony Optimization](https://arxiv.org/abs/2603.12933) | arXiv 2026 | heterogeneous agents with capability-cost profiles | 生产侧路由要低延迟、低成本、可解释 | 小模型语义 intent router + ant colony pheromone specialists | 全文表 1：AMRO-S 平均 87.83，MasRouter 85.93；MATH 78.15 vs 75.42，MBPP 86.3 vs 84.0；并发压力下最高 4.7x speedup | 如果我们涉及“按能力/成本选 agent”，它已经做得很系统 |
| 12 | [ARMOR-MAD: Adaptive Routing for Heterogeneous Multi-Agent Debate](https://arxiv.org/html/2606.13197v1) | arXiv 2026 | 不同模型家族 debate agents | 固定轮数异构 debate 成本高，而且分歧时不稳定 | WHO 选择异构模型池，WHEN 用 pre-debate agreement routing、early stopping、semantic outlier detection | 四个 benchmark 上优于固定轮 heterogeneous debate；在相同模型池下，收益来自 adaptive routing/stopping；还能减少额外 debate token | 覆盖“异构 debate 什么时候该启动/停止” |
| 13 | [Chimera: Serving Multi-Agent LLM Applications on Heterogeneous Clusters](https://arxiv.org/abs/2603.22206) | arXiv 2026 | 异构 LLM cluster，模型延迟/质量不同 | 多 agent workflow 的 serving 如何同时满足质量与时延 | semantic router、confidence estimate、output length prediction、activity monitor | 全文报告 latency-performance frontier 优于 vLLM 等基线；检索主源摘要给出 1.2-2.4x latency reduction 与 8.0-9.5pp performance gain | 系统侧已经把“异构模型池调度”往工程落地推进 |
| 14 | [SciOrch: Learning to Orchestrate Specialized Models for Scientific Reasoning](https://arxiv.org/abs/2606.15872) | arXiv 2026 | 科学子领域专家模型池 | 科学推理中，固定 MAS 成本线性增长，单路由器又不能分解/修正 | 8B orchestrator，经 MCTS trajectory + SFT/GRPO 训练，分解子问题并路由到 specialist commercial models | 240 题测试：平均 56.66%，高于 strongest single commercial 和 strongest multi-agent baseline；成本约 $10.42，低于强 self-consistency | 覆盖“专家模型池 + learned orchestrator”；如果我们讲专家异构，需要更微观的通信失败点 |
| 15 | [tap: A Protocol for Multi-Agent Collaboration Across Toolchains](https://arxiv.org/abs/2606.14445) | arXiv 2026 | vendor / runtime / toolchain 异构 | 不同供应商、不同运行环境的 agents 如何真正协作 | 文件协议：Markdown + YAML metadata；Tier 1 persistent file communication，Tier 2 notification；git worktree isolation | 27 天自用，209 PR，717 artifacts；review artifacts 中 heterogeneous pairs 的 defect/change 记录率高于 homogeneous pairs | 它把异构通信落到协议/工程层；我们若讲通信协议要避开“跨运行时文件协议” |
| 16 | [EARS: Explanatory Abstention in Enterprise LLM Sub-Agents](https://arxiv.org/abs/2606.18668) | arXiv 2026 | 中央 agent 与小型 domain sub-agents 能力边界不对称 | 弱/专门 sub-agent 遇到 ambiguous、missing capability、misrouting 时不该硬答 | taxonomy：Ambiguous Query、Insufficient Input、Missing Capability、Misrouting；fine-tune sub-agent 输出解释性 abstention | 生产电商 BI 场景，overall pass rate 68.5% -> 78.9%；abstention 变成 clarify/reroute/fallback 信号 | 非常接近“能力边界通信”；如果我们做 state admission，需要证明差异在任务结构和机制粒度 |
| 17 | [TUMIX: Multi-Agent Test-Time Scaling with Tool-Use Mixture](https://openreview.net/forum?id=HBm3MFtszH) | ICLR 2026 | 工具访问策略异构：text/code/search/dual-tool 等 | test-time scaling 下，不同工具策略怎么组合最划算 | 多 agent tool-use mixture，响应共享与 refinement，自动优化 agent design，early termination | 全文给出平均 +7.8% / +17.4% 提升，early termination 可用约 49% 成本接近最优；工具策略 diversity 很关键 | 覆盖“工具能力不对称”高地 |
| 18 | [iAgents: Informative Multi-Agent Systems for Collaborative Tasks](https://openreview.net/forum?id=mp6OWpDIJC) | NeurIPS 2024 | 多用户私有信息、社交网络信息不对称 | 每个 agent 只代表一个用户/局部信息，必须主动找信息 | iAgents 把 human social network 映射成 agent network；InfoNav 规划未知 rationale 与信息交换 | InformativeBench 上 GPT-4 仍有明显挑战；去掉 InfoNav 常大幅下降，mixed memory 与 recursive communication 有用 | 覆盖“信息不对称 + 主动通信”主线 |
| 19 | [Communication and Verification under Information Asymmetry](https://arxiv.org/abs/2510.25595) | arXiv 2025 | agent 间知识/技能/观测不对称 | 非对称信息下该怎么通信、怎样验证动作 | tabletop Einstein Puzzle；communication strategies：provide-only、seek-only、full exchange；environment/reasoning verifier | full exchange 通常最好；seek-only 有时优于 provide-only；verifier 减少错误；人类 100% 成功作为参照 | 它已把“非对称信息 + verifier”组合成 benchmark |
| 20 | [AsymPuzl: Benchmarking LLM Agents in Asymmetric Collaborative Puzzle Solving](https://arxiv.org/html/2512.03466v1) | arXiv / OpenReview withdrawn ICLR 2026 | 两个 agent 各自只看 puzzle 的不完整视图 | 如何隔离 asymmetric information 下的 communication failure | 双 agent puzzle，每个 agent 维护 working hypothesis 并通信；比较反馈粒度 | 即使共享所有信息，许多模型仍失败；GPT-4o 在反馈下从 43.3% 到 63.3%；过多 hypothesis feedback 会混淆 | 提供可控 benchmark 压力；我们若做 hidden/info asym benchmark，要说明区别 |
| 21 | [Multi-user Memory Sharing in Multi-Agent Systems](https://arxiv.org/abs/2505.18279) | arXiv 2025 | 用户/agent/resource 访问权限不对称 | 多用户多 agent 系统如何共享记忆同时遵守权限 | Collaborative Memory；用户-agent-resource bipartite access graph；private/shared memory tiers | 主贡献偏框架：动态访问控制、集体记忆、权限隔离 | 覆盖“权限不对称记忆通信” |
| 22 | [CoffeeBench: Benchmarking Long-Horizon LLM Agents in Heterogeneous Multi-Agent Economies](https://arxiv.org/abs/2606.16613) | arXiv 2026 | 经济角色异构：farmer/roaster/retailer | 长周期经济环境里，不同角色 agent 如何交易、沟通、管理现金/库存/定价 | 90 天 supply-chain simulation；被测模型控制一个 roaster，其它 firm 由背景 agent 控制 | GPT-5.5 与 Claude Opus 4.7 最高；多数模型正收益，但 best result 约只到 analytical headroom 的 13%；沟通、定价、库存纪律共同影响利润 | 角色/目标异构 benchmark；可作为“现实多 agent 不是纯 QA”的压力 |
| 23 | [TickingCollabBench](https://arxiv.org/abs/2606.15684) | arXiv 2026 | embodied agents 感知范围、速度、血量、工具不对称 | 时间敏感、部分可观测环境中，互补能力 agent 能否协作 | Minecraft benchmark/generator；feasibility verifier；centralized/distributed topology；communication manager | 全文结论是 LLM agents 在 partial observability + heterogeneity 下仍吃力；distributed topology 降低 overhead 但弱于 global-knowledge oracle | 说明异构能力在 embodied setting 里还没被解决 |
| 24 | [PCMA / MOMARL](https://arxiv.org/abs/2606.14693) | arXiv 2026 | MARL 中 observation、role、contribution、preference 不对称 | 多目标 MARL 中共享 preference vector 会让异构 agent 冲突 | Preference Coordinated Multi-agent Policy Optimization；每个 agent 有 preference planner 和 preference-conditioned actor；鼓励 preference diversity | cooperative multi-objective env 与 traffic 中多指标提升；理论分解 first-order team improvement | 非 LLM，但说明“角色/偏好异构”有成熟 MARL 视角 |
| 25 | [HACRL / HACPO: Heterogeneous Agent Collaborative Reinforcement Learning](https://arxiv.org/abs/2603.02604) | arXiv 2026 | 训练时 state/size/model 异构 | 不同 LLM agent 能否共享 verified rollouts 互相训练，同时避免能力差导致不稳 | cross-agent verified rollouts，capability-aware advantage estimator，model capability discrepancy coefficient | 7 个 benchmark、三类异构；平均 +3.6%，约半数 rollout compute；ablation 显示 discrepancy coefficient 关键 | 覆盖“训练期异构协作”，区别于 inference-time 通信 |
| 26 | [SkillGraph: Dynamic Multimodal Agent Graphs with Evolving Skills](https://arxiv.org/abs/2604.17503) | arXiv 2026 | multimodal agent skill / topology 异构 | 固定拓扑和静态专家无法随任务失败演化 | MMGT 根据图像/文本/skill embedding 预测 query-conditioned graph；Skill Designer 从失败例中提炼新 skills | 四个 VLM benchmark 上 dynamic topology + evolving skills 胜过固定拓扑/静态技能 | 覆盖“技能异构 + 拓扑演化” |
| 27 | [SMoA: Sparse Mixture-of-Agents](https://arxiv.org/abs/2411.03284) | arXiv 2024 | agent role descriptions 异构，信息流稀疏 | dense MoA 成本高、信息冗余，且可能损伤 diversity | Response Selection + Early Stopping 稀疏化信息流；给 agents 分配 distinct roles | reasoning/alignment/fairness benchmark 上接近 MoA 但成本更低；比 MAD 稳定 | 与 ARMOR-MAD 一起压住“全连接多轮通信”的空间 |
| 28 | [MASS: Multi-Agent Design, Optimizing Agents with Better Prompts and Topologies](https://arxiv.org/abs/2502.02533) | arXiv 2025 / Google Research | prompt role、topology、tool-use block 异构 | MAS 设计空间太大，手工 prompt/topology 试错不稳 | 三阶段搜索：block prompt optimization、workflow topology optimization、workflow-level prompt optimization | HotpotQA、MuSiQue、2WikiMQA、MBPP、HumanEval 等上显著胜过多类 baselines；ablation 显示 prompt optimization 是大头 | 它压住“角色/拓扑怎么设计”的自动化问题 |
| 29 | [MetaGPT: Meta Programming for Multi-Agent Collaborative Framework](https://openreview.net/forum?id=VtmBAGCN7o) | ICLR 2024 oral | 软件工程角色异构：PM/architect/engineer/QA 等 | naive agent chaining 会级联幻觉、产物不一致 | SOP，把团队协作压成结构化 artifact pipeline | 软件任务上展示更高一致性和可复用 artifact；核心价值是 role specialization + SOP | A 会早已覆盖“角色分工 + workflow artifact” |
| 30 | [AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation](https://arxiv.org/abs/2308.08155) | COLM 2024 | LLM/tool/human agent 能力异构 | 如何构建可编程、多类型 agent conversation app | conversable agents，conversation programming，group chat，tool execution | 论文偏 framework，展示多个应用；强调 agents 可由 LLM、tools、humans 构成 | 基础设施压力：很多异构应用可以直接建在 AutoGen 上 |
| 31 | [ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate](https://arxiv.org/abs/2308.07201) | ICLR 2024 | evaluator roles/personas 异构 | LLM-as-judge 如何更接近人类多角度评审 | 多 agent referee team，多角色 debate，多种 communication strategy | 文本评估场景中比单 evaluator 更接近人类偏好 | 早期 A 会角色异构 judging 工作 |
| 32 | [Context Learning for Multi-Agent Discussion / M2CL](https://openreview.net/forum?id=EUu8TILWpR) | ICLR 2026 | agent context / perspective 异构 | 多 agent discussion 会因上下文错位而无法共识 | 每个 agent 学一个 context generator；初始化产生多样视角，后续动态调整 context coherence / discrepancy | academic reasoning、embodied tasks、mobile control 上提升；context 可迁移到不同 LLM architecture | 覆盖“上下文异构/错位”问题；与信息包准入相邻但不是同一机制 |
| 33 | [AgentPO: Enhancing Multi-Agent Collaboration via Reinforcement Learning](https://openreview.net/forum?id=5L8uyzjn2l) | ICLR 2026 | 小 Collaborator / 大 Actor 能力与职责不对称 | 如何训练一个轻量 agent 辅助固定强 actor，而不是搜索整个 MAS | 只训练 Collaborator，用 GRPO 学 hint/critic 等辅助 policy，Actor 冻结 | 平均 +1.8% over Role Assignment、+7.2% over EvoAgent；推理成本约 EvoAgent 的 7.8% | 覆盖“小模型辅助大模型”的不对称协作 |
| 34 | [Thought Communication in Multiagent Collaboration](https://openreview.net/forum?id=tq9lyV9Cml) | NeurIPS 2025 spotlight | shared/private latent thoughts 不对称 | 自然语言通信有损、歧义，agent 内部状态有隐藏结构 | latent variable model，识别 shared/private thoughts 与共享结构，再把相关 thoughts 分配给 agent | 理论上给 identifiability，实验验证 latent thought communication 有协作优势 | 若我们讲“消息内容/隐藏状态”，要与 latent communication 切开 |
| 35 | [Latent Collaboration in Multi-Agent Systems / LatentMAS](https://arxiv.org/abs/2511.20639) | arXiv 2025；项目页称 ICML 2026 Spotlight | latent working memory；角色可异构但要求共享 latent 接口 | text-based MAS token 多、错误传播、延迟高 | agents 传 last-layer hidden embeddings 到 shared latent memory；training-free latent collaboration | 9 个 benchmark；最高 +14.6% accuracy，70.8%-83.7% output token reduction，4x-4.3x faster inference；全文 caveat：真正异构模型需 adapter | 通信介质压力：自然语言消息不是唯一通道 |
| 36 | [SIGMA: Conflict-Resilient Multi-Agent Reasoning via Signed Graph Modeling](https://arxiv.org/abs/2605.19418) | arXiv 2026 | agent 关系异构：trust/conflict/neutral | 多 agent 输出冲突时，普通图聚合会传播错误 | signed relational graph，confidence-weighted positive/negative edges，conflict-aware message passing | 六个 benchmark 上提升，恶意/冲突 agent 比例高时仍更鲁棒；ablation 显示 conflict-aware message passing 关键 | 关系异构/冲突建模已有人做；不要只说“不同 agent 有不同意见” |
| 37 | [DALA: Cost-Effective Communication, Auction-based Method](https://arxiv.org/abs/2511.13193) | arXiv 2025 | 通信资源 / 发言权不对称 | free-for-all communication token 成本爆炸，低价值消息淹没上下文 | 把通信 bandwidth 当 scarce resource；VCG / combinatorial auction 分配 speaking rights；MAPPO 学价值密度 | 7 个 reasoning benchmark；高准确低 token；MMLU/GSM8K 上 ablation 显示 cost penalty 和 dynamic valuation 重要 | 资源不对称通信已被市场机制处理；我们若谈通信预算要更具体 |

## 读完后的问题地图

| 问题簇 | 已有代表 | 已经解决到什么程度 | 还没彻底解决的部分 |
|---|---|---|---|
| 模型/角色选择 | X-MAS、MasRouter、AMRO-S、ARMOR-MAD、SciOrch、Chimera | 已经有 benchmark、router、routing+cost、serving 系统、科学专家 orchestrator | 多数把通信当可读文本或输出聚合；较少细粒度刻画“接收者该相信/拒绝哪个 sender state” |
| 强弱协作 | Guided HMAS、AgentPO、Teams Hold Experts Back、HACPO | 已经知道强弱组合会被 cognitive mismatch/expertise dilution 搞坏，也有 guidance / collaborator / RL 训练方案 | 很多方法靠任务级 accuracy 判定，缺少消息级失败分类和可审计通信协议 |
| 多样性是否有效 | MoA、Self-MoA、Agent Scaling、Science of Scaling | 已经有正反两边证据：heterogeneity 可增益，也可被弱模型/coordination overhead 拉垮 | 需要判定“有用 diversity”和“噪声 diversity”的可操作准则 |
| 信息不对称 | iAgents、Communication & Verification、AsymPuzl、Memory Sharing | 已有社交信息导航、puzzle benchmark、verifier、memory access graph | 大多在特定环境或 benchmark 内定义信息差，跨任务协议还不稳 |
| 工具/运行时异构 | TUMIX、tap、AutoGen、Chimera | 工具策略、跨供应商协议、serving 调度都有代表工作 | 从工具输出到 agent belief/state 的可靠传递还较少被独立评测 |
| 关系/冲突异构 | SIGMA、ReConcile、Sparse-MAD、DALA | trust/conflict、稀疏通信、拍卖发言权已被建模 | 多数机制服务最终答案聚合，较少服务于中间状态的准入/拒绝 |
| 通信介质 | Thought Communication、LatentMAS、M2CL | 语言以外的 latent/context 通信已成高压方向 | 真正跨模型异构 latent adapter 与可解释性仍是缺口 |

## A 会压力清单

| 会议 | 相关论文 | 对选题的压力 |
|---|---|---|
| ACL 2024 | ReConcile | 多模型共识、confidence-weighted voting 已经成熟 |
| ACL 2025 | MasRouter | MAS routing 进入主会长文，模式/角色/模型选择不能当空白 |
| ICLR 2024 | MetaGPT、ChatEval | 角色分工、SOP、多 agent judge 已经是早期 A 会基线 |
| COLM 2024 | AutoGen | 异构 agent framework 已经成为基础设施 |
| NeurIPS 2024 | iAgents | 信息不对称 multi-agent 已经有 benchmark 和方法 |
| ICLR 2025 | Mixture-of-Agents | 多模型聚合增益已被高能见度论文占住 |
| NeurIPS 2025 | Thought Communication | token 语言通信的局限已被 latent/thought communication 攻击 |
| ICLR 2026 | M2CL、TUMIX、AgentPO | context heterogeneity、tool-use mixture、小 Collaborator-大 Actor 都已进入主会 |
| ICML 2026 / arXiv | Multi-Agent Teams Hold Experts Back、LatentMAS | 专家被团队拉低、latent communication 都会压缩“能力不对称协作”的新颖空间 |

## 对“这个方向发展到了什么底部”的判断

底部共识一：异构已经是 design variable，不再只是 bonus。论文已经在问“哪个异构维度有用、何时有害、如何路由、如何省成本”。  
底部共识二：能力不对称的默认失败模式是强者被稀释、弱者听不懂、通信成本吃掉收益、异构噪声压过互补信息。  
底部共识三：A 会论文的主战场已经从“多 agent debate”转向 routing、tool-use mixture、context learning、latent communication、expertise dilution diagnosis。  
底部共识四：真正还松动的地方在消息级/状态级可靠性：发送者知道什么、能不能说清楚、接收者什么时候接纳、什么时候要求澄清、什么时候拒绝或降级。这一点与 EARS、Communication & Verification、AsymPuzl、iAgents 相邻，但它们多半把问题放在任务级 protocol、benchmark 或 abstention taxonomy 上。

## 降权引用的边界压力论文

| 论文 | 为什么只作边界压力 |
|---|---|
| [Sparse-MAD](https://aclanthology.org/2024.findings-emnlp.427/) | 重点是通信拓扑稀疏化，不以模型/能力异构为主；但它显示“少通信也许更好”。 |
| [When Single-Agent with Skills Replace Multi-Agent Systems](https://arxiv.org/abs/2601.04748) | 它攻击 MAS 必要性：可编译的 MAS 用 single-agent skills 可保留性能并平均减少约 54% tokens、50% latency。适合作为反证，不算异构 MAS 主线。 |
| [Conflict-Resilient SIGMA](https://arxiv.org/abs/2605.19418) | 已列入主表的关系异构行；主体是 trust/conflict/neutral 关系建模，不是能力不对称主线，写 claim 时需要降权引用。 |

## 本地证据索引

全文文本在 `papers/heterogeneous-asymmetric-20260619/texts/`。本报告主要读过并引用的本地文件包括：

`x-mas-2505.16997.txt`, `guided-collaboration-hmas-2602.13639.txt`, `teams-hold-experts-back-2602.01011.txt`, `reconcile-2309.13007.txt`, `mixture-of-agents-2406.04692.txt`, `self-moa-2502.00674.txt`, `llm-blender-2306.02561.txt`, `agent-scaling-diversity-2602.03794.txt`, `science-scaling-agent-systems-2512.08296.txt`, `masrouter-2502.11133.txt`, `amro-s-2603.12933.txt`, `armor-mad-2606.13197.txt`, `chimera-2603.22206.txt`, `sciorch-2606.15872.txt`, `tap-2606.14445.txt`, `ears-2606.18668.txt`, `tumix-openreview.txt`, `iagents-2406.14928.txt`, `comm-verification-info-asym-2510.25595.txt`, `asympuzl-2512.03466.txt`, `memory-sharing-2505.18279.txt`, `coffeebench-2606.16613.txt`, `tickingcollabbench-2606.15684.txt`, `pcma-momarl-2606.14693.txt`, `hacrl-2603.02604.txt`, `skillgraph-2604.17503.txt`, `smoa-2411.03284.txt`, `mass-2502.02533.txt`, `metagpt-2308.00352.txt`, `autogen-2308.08155.txt`, `chateval-2308.07201.txt`, `m2cl-openreview.txt`, `agentpo-openreview.txt`, `thought-communication-2510.20733.txt`, `latentmas-2511.20639.txt`, `dala-2511.13193.txt`, `single-agent-skills-replace-mas-2601.04748.txt`。
