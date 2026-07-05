# 候选解空间与动态 agent 数机制：同行方法批判吸收

日期：2026-07-05

问题焦点：

1. 候选解空间如何构造、分歧、聚合。
2. 机制如何根据 agent 数量或题目状态动态适配。
3. 在已有工作密集覆盖的情况下，我们还能否提出不直接撞车的机制。

范围说明：本文深看了与当前问题最相关的几条主线，包括 Diversity-aware Initialization、DynaDebate、Maestro、M2CL、DAR、PEAR、DySCo、HCP-MAD、Dynamic Role Assignment。判断“撞车风险”仅基于当前已查阅文献和本地大表，不等价于最终投稿前的完整系统综述。

## 1. 总体判断

这条赛道已经从“多 agent debate 是否有用”转向更细的四个问题：

1. **coverage**：候选池里有没有正确/有信息量的解。
2. **divergence control**：候选之间是否真有独立性，而不是同一路径的措辞变化。
3. **identification**：当候选池里有正确解时，系统能否选出来。
4. **scale adaptation**：agent 数、通信边、轮数、采样深度是否按题目状态动态分配。

这与我们从 CQG 全量结果里看到的现象高度一致：

- 当前 3-agent 初始 oracle@3 为 369/500 = 73.8%，高于 initial majority 320/500 = 64.0%，说明 identification 有明显空间。
- 131/500 初始三答全错，说明 coverage collapse 也是真瓶颈。
- 89/500 是三方 unique answer tie，当前 CQG 没认真处理，说明 no-majority conflict 是一个被我们现有协议漏掉的区域。

因此，直接提出“先生成多样候选，再选择正确者”会撞车；但把问题收窄为 **candidate-pool state 诊断驱动的协议切换与 agent 预算分配**，仍有相对清楚的空间。

## 2. 方法逐项吸收

### 2.1 Demystifying MAD：diversity 改 prior，confidence 改 dynamics

来源：[Demystifying Multi-Agent Debate: The Role of Confidence and Diversity](https://arxiv.org/abs/2601.19921)。

核心机制：

- 先采样更大的候选池，再贪心选择 distinct answer 更多的子集初始化 debate。
- 把 diversity 和 confidence 分成两个阶段：diversity 决定初始候选分布中是否有正确 hypothesis；confidence 决定后续 belief update 如何加权。
- 理论上，diversity-aware initialization 不改变 debate martingale dynamics，而是改善初始状态的 prior success probability；confidence-weighted update 在正相关假设下把 martingale 变成 submartingale。
- 他们明确报告 naive temperature scaling 不足以增加 answer-level diversity，高温更多带来语言/风格变化和指令遵循下降。

可吸收点：

- 我们应采用 coverage / identification 语言来拆问题，而不是只讲“少数派”。
- 不能靠升温来声称构造正交候选；必须有目标化策略或诊断。
- 候选池多样性应和后续聚合机制分开评估：oracle@N 是 coverage，final accuracy 是 coverage × identification。

批判点：

- diversity 被近似为 distinct answer count，可能过浅。两个不同答案未必来自独立思路；同一答案也可能来自不同可验证路径。
- confidence 机制依赖训练和“confidence 与 correctness 正相关”的假设，落地成本较高。
- 它没有根据 observed pool state 切换不同协议，而是统一做 diverse init + confidence debate。

与我们的避撞边界：

- 不要提出“从大候选池里选更多 distinct answers 初始化 MAD”作为主机制。
- 可以吸收它的 coverage/identification 框架，但把新意放在 **pool-state-dependent protocol selection**。

### 2.2 DynaDebate：问题级 path generation + adaptive redundancy

来源：[DynaDebate](https://arxiv.org/abs/2601.05746)。

核心机制：

- debate 前设置 Path Generation Agent，为每题生成 diverse and logical solution paths。
- 生成路径要求 logical soundness 和 mutual independence。
- 若可行路径多，则 exploration mode：不同 agents 走不同路径。
- 若有效路径少，则 consistency check mode：多个 agents 共享路径，用 stochasticity 检查偶发错误。
- debate 阶段转为 process-centric audit，要求 agents 检查 atomic inference steps。
- 分歧触发 external verification agent。

可吸收点：

- “不同 agent 应被分配不同策略”已经是强基线。
- adaptive redundancy 很重要：如果只有 1-2 条真正可行路径，不应硬凑 3 条假路径。
- path coverage rate 比 single-path rate 高，可以作为候选池是否真的互补的证据。

批判点：

- path generator 自己可能生成伪独立策略；“互相独立”主要靠 prompt 约束。
- 机制主要围绕 3 agents 设计，虽然有 round-robin fallback，但不是真正按 agent 数和题目状态优化预算。
- 它的 verifier 更像工具增强，若我们也说“分歧时触发 verifier”，会很容易撞。

与我们的避撞边界：

- 不能把“生成多条 solution paths 并分配给 agents”作为主贡献。
- 可以吸收 adaptive redundancy，但把它变成 pool adequacy 诊断的一部分：当 observed pool collapse 时，才按未覆盖策略补采样；不是所有题都先 path generation。

### 2.3 Maestro：divergence/convergence 结构化解耦

来源：[Maestro](https://arxiv.org/abs/2511.06134)。

核心机制：

- 将协作显式拆成 divergence as collective exploration 和 convergence as list-wise synthesis。
- 多个 execution agents 生成 candidate pool。
- central agent 做 list-wise selection，而不是自己重新生成答案。
- 引入 coverage probability：候选池至少含一个正确解的概率。
- 引入 identification probability：候选池含正确解时 selector 选中正确解的概率。
- CLPO 将 decision tokens 和 rationale ranking 分开优化，避免把“选哪个候选”和“解释得像不像”混成一个 reward。
- 他们的实验显示 2 到 4 agents 增加通常提升，但超过 4 后收益饱和甚至下降；轮数过多会导致 herding 和 bias amplification。

可吸收点：

- coverage × identification 是非常好的分析坐标。
- selection 比 generation 更适合作为 convergence：让中心模型直接重写答案容易被长上下文和叙事连贯性误导。
- agent 数不是越多越好；候选越多，也会引入更多 plausible distractors，增加 selector 负担。

批判点：

- CLPO 需要训练 central selector，不适合我们当前快速验证。
- central selector 仍可能被 persuasive wrong rationales 吸引，除非有更细粒度的证据检查。
- 其“execution agents generate broad pool -> central select”总框架已经很完整，我们不能重复包装。

与我们的避撞边界：

- 不能把“execution agents + central selector + coverage/identification”作为主贡献。
- 我们可以把 Maestro 当成强竞争叙事，并强调我们不是训练 list-wise selector，而是根据候选池结构切换到不同判别协议，尤其处理 CQG 暴露出的 `unique=1 / unique=2 / unique=3` 三态。

### 2.4 M2CL：动态 context instruction 控制分歧与一致性

来源：[Context Learning for Multi-Agent Discussion](https://arxiv.org/abs/2602.02350)。

核心机制：

- 为每个 agent 学一个 context generator，每轮动态生成 agent-specific instruction。
- 目标是在 context coherence 和 output discrepancy 之间自适应平衡。
- 初始化阶段给不同 LLM 分配 diverse initial instructions，覆盖互补视角。
- 实验覆盖不同数量的 LLMs，并声称具有更好的 MAD scaling law。

可吸收点：

- 分歧不仅来自答案采样，也来自每个 agent 的 context/control signal。
- “agent-specific context”是比 persona 更细的控制变量。

批判点：

- 需要训练 context generator，工程和数据成本高。
- 如果我们只说“给不同 agent 不同上下文/角色”，会撞 M2CL 和 role/persona 系列。
- 它更关注 discussion consistency，不直接给出 answer-candidate pool 的状态诊断。

与我们的避撞边界：

- 不把 learned context generator 作为主机制。
- 可吸收“context 是分歧控制杆”，用于我们后续 collapse 状态下的 orthogonal strategy resampling。

### 2.5 DAR：保留分歧消息，而不是全量广播

来源：[Hear Both Sides: Efficient Multi-Agent Debate via Diversity-Aware Message Retention](https://arxiv.org/abs/2603.20640)。

核心机制：

- 每轮不是广播全部 peer responses，而是由 filter module 选择“彼此分歧最大且与多数票分歧最大”的响应。
- 输出 agent IDs，不改写原始消息，避免 LLM 编辑造成内容漂移。
- 理论上从 correlated estimators 解释：高相关响应会降低 effective sample size；保留 disagreement 提升独立信号数量。
- 强调“what agents hear is as important as what agents say”。

可吸收点：

- 随 agent 数增加，噪声/冗余会累积；动态保留比全量广播更合理。
- 保留原始消息的 index-based intervention 很干净，减少改写污染。
- diversity 应理解为降低错误相关性，而不只是数量更多。

批判点：

- 它是 message retention，不是候选空间 construction；如果初始池 collapse，它无能为力。
- disagreement 不是 correctness。错误少数派也可能被放大。
- 它主要处理“谁听到什么”，不是“下一步该增加几个 agent / 增加哪类 agent”。

与我们的避撞边界：

- 不把“保留 dissent / 过滤重复多数消息”作为主机制。
- 可吸收 effective sample size 的思想，但我们需要在上游诊断 candidate pool，而不是只在中游筛消息。

### 2.6 PEAR / DySCo：agent 数增长时，通信结构要动态稀疏

来源：

- [PEAR](https://arxiv.org/abs/2606.20621)
- [DySCo](https://arxiv.org/abs/2606.01828)

PEAR 核心机制：

- 每轮根据 agent state 动态重构 sparse topology 和 role assignment。
- 优化 targeted diversity、influence balancing、low-confidence filtering。
- 保证 permutation equivariance，避免固定拓扑的位置偏置。

DySCo 核心机制：

- 每轮为 potential communication edge 打分，考虑 historical trust、current confidence、answer/reasoning divergence、task dependency 和 token cost。
- 每个 receiver 只接收 top-k neighbors。
- 消息压缩成 current answer、关键支持理由、对 receiver 的反例/修订建议。
- 最后 trust-weighted aggregation，weighted answer entropy 低时早停。
- 相比 full communication，复杂度从近似 `O(n^2)` message 降到 `O(nk)`。

可吸收点：

- agent 数量变大后，关键不是“所有人都互相听”，而是保留高价值边。
- 动态 topology 处理的是规模适配问题，能显著降低成本。
- answer divergence 可以作为通信价值的一部分，但必须和 trust / task dependency 结合。

批判点：

- PEAR/DySCo主要解决通信和影响力分配，不直接解决 candidate coverage collapse。
- trust、confidence、verifier feedback 都可能是噪声信号；错误多数也会被当成稳定 consensus。
- 动态稀疏通信容易把“问题是否需要更多候选”混成“谁该和谁通信”，两者不是同一个问题。

与我们的避撞边界：

- 不把 dynamic sparse topology / trust-aware edge selection 作为主贡献。
- 我们的 agent 数适配应围绕 candidate-pool adequacy，而不是通信边优化。

### 2.7 HCP-MAD：共识驱动的 progressive escalation

来源：[HCP-MAD](https://arxiv.org/abs/2604.09679)。

核心机制：

- Stage 1：Heterogeneous Consensus Verification，两名异构 agents 先独立回答；若一致则早停。
- Stage 2：Heterogeneous Pair-Agent Debate，若不一致，两人进行轻量 pair debate，并用 answer exchange / persistent deadlock 检测低信息 debate。
- Stage 3：Escalated Collective Voting，对 unresolved tasks 招募更多 agents，分成 independent observers 和 contextual reviewers，做 weighted majority vote。
- 其核心假设是：简单题应低成本解决，复杂题才扩大协作。

可吸收点：

- 这是与我们“动态 agent 数适配”最接近的一条线。
- 它不是固定 n，而是先用小 agent set 探测题目状态，再按 unresolved 状态升级。
- 它明确发现复杂 GPQA 更需要 ECV，而简单 commonsense debate 可能引入噪声。

批判点：

- 它的核心状态信号是 two-agent consensus，但 consensus 可能是错误共识。
- 它对候选池结构分得不够细：一致/不一致只是二分，没有区分 collapse、minority-bearing、no-majority conflict。
- ECV 最后仍偏 voting，可能无法解决 plausible wrong majority 或 no-majority tie 的判别问题。

与我们的避撞边界：

- 不能简单提出“先两人一致早停，不一致再加更多人”。
- 我们可吸收 progressive escalation，但状态变量应改成更细的 candidate-pool adequacy，而不是单纯 consensus。

### 2.8 Dynamic Role Assignment：题目级 agent-role 匹配

来源：[Dynamic Role Assignment for Multi-Agent Debate](https://arxiv.org/abs/2601.17152)。

核心机制：

- 正式 debate 前做 Meta-Debate。
- 每个候选 agent 先尝试扮演每个 role 并提交 role-specific proposal。
- 所有 agents 再作为 evaluators，对每个 agent-role proposal 按 role-specific criteria 评分。
- 最终把每个 role 分配给最适合的 agent。

可吸收点：

- agent 的“个体能力”不等于“某个 debate role 的适配度”。
- 题目级 role assignment 比静态 role/persona 更合理。

批判点：

- 它需要异构模型或明确 role set；若我们只用同一 Qwen 采样，收益来源会弱。
- 它解决的是 agent-role matching，不是 candidate pool 的 coverage / identification。
- Meta-debate 本身成本不低。

与我们的避撞边界：

- 不把 role assignment 作为主机制。
- 可以借“能力-角色适配”作为 future extension：当 candidate pool 缺某类策略时，选择最适合补该策略的 agent/prompt。

## 3. 横向比较：构造、分歧、聚合、规模适配

| 方法 | 候选空间构造 | 分歧控制 | 聚合/识别 | agent 数适配 |
|---|---|---|---|---|
| Diversity-aware Initialization | 大池采样后选 distinct answers | answer-level diversity | confidence-modulated debate | 基本固定 n |
| DynaDebate | Path Generation Agent 生成独立策略 | logical soundness + mutual independence | process audit + trigger verifier | round-robin adaptive redundancy，但实验多为 3 agents |
| Maestro | execution agents 并行生成 candidate pool | exploration + epsilon anti-overconditioning | central list-wise selector / CLPO | 研究 2-4 agents，超过会饱和/下降 |
| M2CL | learned context generators | 控制 context coherence 与 output discrepancy | discussion convergence | 声称多 agent scaling，但需训练 |
| DAR | 不构造上游候选 | 保留 disagreeing messages | 原 MAD 聚合 | 随 n 增加抑制冗余/噪声 |
| PEAR | 不主攻候选构造 | dynamic sparse topology + targeted diversity | debate revision + aggregation | topology 随 n/round/state 变 |
| DySCo | 不主攻候选构造 | trust/confidence/divergence/task edge score | trust-weighted aggregation | O(nk) sparse communication |
| HCP-MAD | 先异构 pair，必要时扩展 | 异构 pair + observers/reviewers | progressive vote | 按 consensus/unresolved escalation |
| Dynamic Role Assignment | role-specific proposal | agent-role suitability | 选 agent 填 role 后再 debate | 适配 role assignment，不直接适配 n |

横向看，同行已经覆盖了三类大想法：

1. **先多样化生成**：Diversity-aware Initialization、DynaDebate、Maestro、M2CL。
2. **中间保留/路由分歧**：DAR、PEAR、DySCo。
3. **按任务复杂度调规模**：HCP-MAD、PEAR、DySCo、Maestro 的 agent-scaling analysis。

因此，我们不能把主贡献放在这些泛化口号上。

## 4. 仍然存在的空位

当前工作普遍缺一个很具体的中间层：**observed candidate pool state diagnosis**。

很多方法知道 coverage 重要，但常常直接做：

- 采更多；
- 生成多路径；
- 保留 dissent；
- 动态路由；
- 训练 central selector。

它们较少把已经生成出来的候选池先诊断成不同状态，然后用不同决策协议处理。我们的 CQG 数据恰好显示这个状态差异非常关键：

| pool state | 本地现象 | 当前 CQG 行为 | 更合理的机制 |
|---|---|---|---|
| collapse | `unique=1` 约 44%，其中有同错 | 不处理 | 判断是否低风险早停，或触发 targeted orthogonal expansion |
| minority-bearing | `unique=2` 约 38%，有明显 oracle 空间 | CQG 处理，但 flip 不稳 | DCAC / discriminant certificate |
| no-majority conflict | `unique=3` 约 18%，oracle 空间仍存在 | 全部 tie，不 quarantine | list-wise discriminant identification |

这说明我们的潜在新意不是“多样化生成”，而是：

> 将候选池结构作为显式状态变量，用它决定是否扩展候选空间、扩展多少 agent、扩展哪类策略、以及采用哪种聚合/识别协议。

## 5. 候选机制雏形：Candidate-Pool Adaptive Consensus

暂名：**CPAC：Candidate-Pool Adaptive Consensus**。

中文：**候选池自适应共识协议**。

### 5.1 核心思想

CPAC 不从固定 agent 数或固定 debate 流程开始，而从一个小规模初始池开始，然后诊断候选池状态：

1. 当前候选是否 collapse？
2. 当前候选是否形成 majority/minority？
3. 当前候选是否无多数、三方分歧？
4. 当前分歧是否覆盖了真正不同的 discriminant conditions？
5. 继续增加 agent 的边际收益是补 coverage，还是只会增加 distractors？

然后按状态切换协议。

### 5.2 状态诊断变量

可观测变量：

- `U`: unique normalized answers 数。
- `support_vector`: 各答案支持数，如 `[3]`, `[2,1]`, `[1,1,1]`。
- `answer_entropy`: 答案分布熵。
- `rationale_similarity`: reasoning token/embedding 相似度。
- `answer_type_risk`: base notation、tuple、set、interval、symbolic expression 等表示风险。
- `strategy_coverage`: 是否覆盖代数、几何、枚举、反证、模运算、构造、边界检查等策略族。
- `discriminant_coverage`: 候选之间是否已经提出可区分它们的必要条件。
- `confidence/logprob spread`: 只作弱信号，不作为单独决策依据。

### 5.3 状态到动作

| 状态 | 触发 | 动作 |
|---|---|---|
| Low-risk consensus | `U=1`，rationale similarity 低风险，answer type 低风险 | 早停，避免无谓 debate |
| Suspicious collapse | `U=1` 但题目高难/低 logprob/高表示风险/推理高度模板化 | 触发 orthogonal strategy expansion，不 debate |
| Minority-bearing | `U=2` 且 support `[n-1,1]` 或近似多数 | 用 DCAC：directional appeal + candidate-delta discriminant certificate |
| No-majority conflict | `U>=3` 或最高支持不足多数 | 用 list-wise discriminant identification，不套 majority/minority |
| Saturated noisy pool | U 高但 discriminant coverage 低，候选多为 plausible distractors | 不继续加 solver；改加 verifier / condition generator |
| Representation-risk pool | raw/normalized answer 可能混淆 | raw-format preserving check，必要时 no-change/abstain |

### 5.4 agent 数动态适配

CPAC 的 agent 数不是固定 `n=3/5/7`，也不是简单随题目难度加人，而是按“缺什么信号”加人：

- 缺候选：加 solver agent，但必须绑定未覆盖的策略族。
- 缺判别：加 discriminant generator / verifier，而不是再加 solver。
- 缺稳定性：对同一策略做 redundancy sampling。
- 候选已饱和：停止加人，防止 distractor 增多。

这吸收了 DynaDebate 的 adaptive redundancy、Maestro 的 agent-saturation 警告、HCP-MAD 的 progressive escalation，但状态变量更细。

## 6. 与同行的避撞表述

| 容易被质疑撞车的对象 | CPAC 的区分点 |
|---|---|
| Diversity-aware Initialization | 不是固定先采大池再选 distinct answers，而是先诊断 pool state，再决定是否扩池与怎么扩。 |
| DynaDebate | 不是所有题都先 path generation；只有 suspicious collapse 或 coverage 缺口才 targeted expansion。 |
| Maestro | 不训练 central list-wise selector；使用状态条件化的 discriminant certificate，特别处理 no-majority conflict。 |
| DAR | 不是中游 message retention；核心在候选池状态诊断和动作切换。 |
| PEAR/DySCo | 不做通信 topology/edge selection 主贡献；agent 数适配围绕候选池充分性，而非通信成本。 |
| HCP-MAD | 不只用 two-agent consensus 作为简单/复杂信号；区分 collapse、minority-bearing、no-majority conflict。 |
| Dynamic Role Assignment | 不解决 agent-role matching；只在需要补策略时选择对应 prompt/role 作为工具。 |
| Minority Sentinel | 不训练 flip classifier；2:1 只是 CPAC 的一个状态，且用证书而非 fingerprint threshold。 |

## 7. 批判吸收后的研究判断

第一，候选解空间的构造已经是热方向，不能作为宽泛新意。现有文献已经有 oversampling selection、path generation、execution-agent exploration、learned context generation 等方案。

第二，agent 数动态适配也已经有人做，但多数是从成本、通信拓扑、任务复杂度或 role matching 入手。真正围绕 **候选池状态** 来决定 agent 预算和聚合协议的工作还不明显。

第三，我们的 CQG 证据给了一个很好的切口：当前方法只处理 `unique=2` 的 majority/minority，却漏掉 `unique=1` 的 coverage collapse 和 `unique=3` 的 no-majority conflict。这个三态结构比“更多 diversity”更具体，也更容易形成可复现实验。

第四，最稳妥的论文机制不应叫“diverse initialization”或“dynamic path generation”，而应叫：

> Candidate-pool adequacy as a control signal for adaptive consensus.

或更短：

> Candidate-Pool Adaptive Consensus.

它的核心 claim 是：

> Multi-agent reliability is limited not only by how agents debate, but by whether the observed candidate pool is adequate for the decision protocol being applied. A fixed majority/minority protocol wastes collapse cases, mishandles no-majority conflicts, and over-debates saturated pools. CPAC diagnoses pool state first, then allocates agents and aggregation rules conditionally.

中文：

> 多 agent 可靠性不只取决于 agent 如何辩论，还取决于当前候选池是否适配后续决策协议。固定多数/少数协议会浪费 collapse 样本、误处理三方无多数分歧，并在候选已饱和时继续引入 distractor。CPAC 先诊断候选池状态，再条件化分配 agent 预算和聚合规则。

## 8. 可验证实验方向

这部分不是最终方案，只是把批判吸收转成可测试问题。

1. **Pool scaling probe**
   - 在 MATH500 上只跑初始采样，不跑 debate。
   - 比较 `n=3/5/7/9` 的 unique answer、oracle@N、marginal oracle gain、all-wrong rate。
   - 判断更多 agent 到底补 coverage，还是主要增加 distractors。

2. **State-conditioned intervention**
   - 对 `unique=1`：比较 keep vs orthogonal expansion。
   - 对 `unique=2`：比较 current CQG vs DCAC。
   - 对 `unique=3`：比较 arbitrary tie / majority prompt / list-wise discriminant certificate。

3. **Budget-matched baseline**
   - 与 self-consistency、diversity-aware init、DynaDebate-style path generation 做同 token budget 对比。
   - 只要不做 budget-matched，对方法有效性的解释会很弱。

4. **诊断指标**
   - coverage：oracle@candidate_pool。
   - identification：final correct / oracle-present。
   - distractor load：wrong unique candidates 数。
   - marginal utility：每新增 agent 带来的 oracle gain。
   - harm：candidate pool 原本有正确 majority，却被协议翻错。

## 9. 当前结论

批判吸收后的结论是：我们不应该放弃 CQG，而是要把 CQG 降级为 CPAC 中的一个分支。CQG/DCAC 只适用于 `minority-bearing` 状态；它不该承担 `collapse` 和 `no-majority conflict` 的问题。

更完整的机制应是：

1. 先小规模生成候选池。
2. 诊断 pool adequacy。
3. 根据 pool state 动态决定是否加 agent、加什么 agent、是否进入 CQG/DCAC、是否进入 list-wise discriminant selection、是否早停。

这条线吸收了同行对 diversity、coverage、dynamic scaling 的认识，但避开了把“多样化生成”或“动态路由”本身作为主贡献。它更像是在问：**给定一个已观察到的候选池，哪种集体决策协议才是合适的？**
