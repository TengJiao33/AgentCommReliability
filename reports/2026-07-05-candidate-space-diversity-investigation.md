# Candidate Space Diversity 调查记录

日期：2026-07-05

问题：多 agent 是否真的产生了足够多的不同候选解/候选思路？如果候选池本身贫瘠，那么继续围绕 minority 做复杂机制的收益上限会很低。相应地，是否应把机制前移到“先构造正交/分歧候选方案，再识别正确者”？

## 1. 本地 CQG 证据

数据源：

- `experiments/20260705-a8002-math500-cqg-divergent-qwen25-7b-full/math500-qwen25-7b-instruct-cqg-divergent/records.jsonl`
- `experiments/20260705-a8002-math500-cqg-divergent-qwen25-7b-full/math500-qwen25-7b-instruct-cqg-divergent/summary.json`

### 1.1 初始候选答案数量

按 CQG 记录中的 `quarantine_decision.unique_answer_count` 统计：

| 初始 unique answer 数 | 样本数 | 占比 | 当前处理状态 |
|---:|---:|---:|---|
| 1 | 220 | 44.0% | 不 quarantine |
| 2 | 191 | 38.2% | 189 题 quarantine，主要是 2:1 majority/minority |
| 3 | 89 | 17.8% | 全部 initial tie / final tie，不 quarantine |

这说明当前 3-agent CQG 不是完全没有产生多候选；约 56% 的题至少产生 2 个不同答案。但当前方法几乎只利用了 `unique=2` 的 2:1 分歧，完全没有认真处理 `unique=3` 的三方分歧。

### 1.2 题内 oracle 空间

用 `parsed_answer` 对 gold 重新计算初始三答 oracle@3：

| 分组 | n | initial majority correct | oracle@3 | oracle 空间 |
|---:|---:|---:|---:|---:|
| 全部 | 500 | 320 = 64.0% | 369 = 73.8% | +49 = +9.8 pp |
| unique=1 | 220 | 188 = 85.5% | 189 = 85.9% | +1 |
| unique=2 | 191 | 113 = 59.2% | 144 = 75.4% | +31 |
| unique=3 | 89 | 19 = 21.3% | 36 = 40.4% | +17 |

解释：

1. 当前 3-agent 候选池里确实经常已经含有正确答案：oracle@3 比 initial majority 高约 9.8 pp。
2. `unique=2` 是当前 CQG 的主战场，池内 oracle 空间有 +31。
3. `unique=3` 虽然更难，但也有 +17 的池内选择空间；当前 CQG 把它当作 tie 放掉了。
4. 仍有 131/500 题初始三答全错，这类题即使有完美 selector 也无法从现有池内恢复，必须依赖更强的候选生成/正交策略探索。

### 1.3 对当前 CQG 的含义

目前 CQG 的问题不是“完全没有多候选”，而是：

- 候选池有时贫瘠：44% 是 unique=1，其中 31/220 或 32/220 近似全体同错。
- 候选池有时足够但没被利用：17.8% 是 unique=3，当前全部 tie，不进入 quarantine。
- 候选池有时含有正确 minority，但 selector 不稳：unique=2 中 oracle 空间明显，但当前 flip 会同时带来 recovery 和 harm。

所以，“minority 上做文章没有用”这个担心需要拆开：

1. 对 `unique=1 且全错`：确实没用，必须先扩候选池。
2. 对 `unique=2`：有用，但需要更好的识别机制。
3. 对 `unique=3`：不是 minority 问题，而是无多数时的候选识别问题，当前 CQG 漏掉了。

## 2. 同行是否已经做这件事

结论：已有工作已经明确把“候选解空间/初始观点多样性”当作机制主轴。因此，如果我们直接提出“先生成多个正交方案，再选择正确者”，会有较高撞车风险。

### 2.1 Self-Consistency / Tree of Thoughts：单模型多路径基线

Self-Consistency 提出采样多条 reasoning paths，再按答案一致性边缘化选择输出。它的基本直觉就是复杂问题存在多种思考路径，不能只取 greedy path。来源：[Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171)。

Tree of Thoughts 把 CoT 扩展为对多个 coherent thought units 的搜索，允许模型探索、评估、回溯多个 reasoning paths。来源：[Tree of Thoughts](https://arxiv.org/abs/2305.10601)。

这类方法不是 multi-agent debate，但它们已经覆盖了“多路径生成 + 选择”的基础思想。

### 2.2 Diversity-aware Initialization：直接针对 MAD 初始观点多样性

`Demystifying Multi-Agent Debate: The Role of Confidence and Diversity` 明确指出 vanilla MAD 缺两个机制：initial viewpoints 的 diversity 和 calibrated confidence。其 diversity-aware initialization 会先采样更大的 candidate pool，再贪心选择答案更多样的子集来初始化 debate。来源：[arXiv:2601.19921](https://arxiv.org/abs/2601.19921)。

该文还把机制分成两层：

- diversity affects what hypotheses are present；
- confidence affects how contributions influence aggregation。

这和我们现在讨论的“先确保池里有正交候选，再识别正确者”非常接近。

### 2.3 DynaDebate：动态 path generation + allocation

DynaDebate 的核心之一就是在 debate 前使用 Path Generation Agent，为每题生成 diverse and logical solution paths，并分配给不同 agents。它明确约束路径要 logical sound 和 mutually independent。来源：[DynaDebate](https://arxiv.org/abs/2601.05746)。

它和我们可能的“正交方案生成”很近，尤其是：

- 先为每题生成多条 solution paths；
- agent 按不同路径执行；
- 后续做 process-centric step audit；
- disagreement 时触发 verifier。

因此，若我们只说“给每个 agent 分配不同解题路径”，会和 DynaDebate 强撞。

### 2.4 Maestro：divergence/convergence 明确二分

Maestro 更直接：它把 multi-agent collaboration 拆成 divergence as collective exploration 和 convergence as list-wise synthesis。多个 execution agents 先生成 broad and diverse candidate pool，central agent 再做 list-wise selection。来源：[Maestro: Learning to Collaborate via Conditional Listwise Policy Optimization](https://arxiv.org/html/2511.06134v1)。

该文甚至显式提出两个指标：

- coverage：候选池是否至少包含一个正确解；
- identification：在候选池含正确解时，selector 是否选中正确解。

这与我们刚才对 CQG 的本地分析高度同构。因此，“coverage -> identification”这个总框架已经不能作为我们的新意。

### 2.5 RPD / 1PNS：训练侧的多解路径多样性

`Reasoning Path Divergence` 指出 test-time scaling 的收益依赖 reasoning path diversity；如果模型输出路径变化很小，额外采样收益有限。它提出 one problem, multiple solutions 训练范式，并用 RPD 度量语义级 reasoning path divergence。来源：[Reasoning Path Divergence](https://arxiv.org/html/2510.26122v1)。

这说明“候选路径贫瘠”不仅是 inference protocol 问题，也被训练数据的一题一解范式解释过。

### 2.6 SDRL / GFlowNet：训练模型面对分歧路径

SDRL 先采样多个 candidate solutions，再构造包含 diverse reasoning trajectories 的 debate context，让模型学习如何从分歧轨迹中修正。来源：[Self-Debate Reinforcement Learning](https://arxiv.org/html/2601.22297v1)。

PRM-guided GFlowNets 也把目标放在同时提升 accuracy 和 solution diversity，强调传统单一 reward 优化会收缩到较窄策略。来源：[Accurate and Diverse LLM Mathematical Reasoning via Automated PRM-Guided GFlowNets](https://arxiv.org/html/2504.19981v3)。

这些不是我们当前 test-time CQG 的直接竞品，但会占据“训练出多样高质量解法”这条叙事。

## 3. 避撞判断

宽泛机制已经拥挤：

| 可能表述 | 撞车对象 | 风险 |
|---|---|---|
| 多采样候选，再多数投票 | Self-Consistency | 高 |
| 多路径搜索/回溯 | Tree of Thoughts / Graph of Thoughts | 高 |
| 从大候选池选多样答案初始化 MAD | Demystifying MAD | 很高 |
| 让 Path Generator 生成互相独立的解题路径并分配 agents | DynaDebate | 很高 |
| divergent exploration + convergent selector | Maestro | 很高 |
| 用指标度量 reasoning path semantic diversity | RPD | 高 |
| 训练模型面对 diverse debate trajectories | SDRL | 高 |

因此，我们不能把主贡献写成“我们发现多 agent 应该先多样化生成候选”。这已经是同行正在写的东西。

## 4. 仍可切入的更窄问题

本地 CQG 的新缝隙不在“是否要多样性”，而在 **候选池状态诊断与协议切换**：

1. `unique=1`：没有分歧，CQG 不能直接工作；需要判断是否值得主动扩展候选池。
2. `unique=2`：有 majority/minority，适合 CQG/DCAC 类机制做 minority admissibility。
3. `unique=3`：没有 majority，当前 CQG 全部 tie；这里需要 list-wise identification，而不是 minority recovery。

这个三态分解比“多样化初始化”窄一些，也更贴近我们的失败记录。

可命名为 **Candidate Pool Adequacy Gate**，中文可称“候选池充分性门控”。它不直接声称发明多样候选生成，而是把每题进入后续机制前的状态分成：

| 状态 | 诊断 | 应用机制 |
|---|---|---|
| Collapse | 1 unique answer | 若题目难度/不确定性高，触发正交策略再采样；否则保留 |
| Minority-bearing | 2 unique answers | CQG/DCAC：少数派准入与判别证书 |
| No-majority conflict | 3+ unique answers | list-wise discriminant identification，不走 majority/minority 叙事 |

这条线的避撞点是：我们不是单纯增加 diversity，而是提出 **不同候选池状态需要不同的 consensus protocol**。尤其是 `unique=3` 这类“没有 majority 的分歧”在当前 CQG 结果里是明确漏斗。

## 5. 当前最值得验证的猜想

本轮调查支持一个更精确的猜想：

> MAD/CQG 的瓶颈可以分解为 coverage bottleneck 和 identification bottleneck。当前 CQG 只在 2:1 分歧上处理 identification，既没有修复 unique=1 的 coverage collapse，也没有处理 unique=3 的 no-majority identification。因此，继续只做 minority 识别会错过一大块候选池机制空间。

这个猜想有本地证据支撑：

- oracle@3 = 73.8%，高于 initial majority 64.0%，说明 identification 有空间。
- 131/500 初始三答全错，说明 coverage 也是真瓶颈。
- 89/500 是 3-way tie 且当前全部不 quarantine，说明当前 CQG 的协议覆盖面不足。

## 6. 对机制方向的临时结论

当前更稳妥的方向不是抛弃 CQG，而是把 CQG 放进更前置的候选池充分性框架：

1. 先诊断候选池是否 collapse / minority-bearing / no-majority conflict。
2. collapse 时，触发少量正交策略生成，不直接 debate。
3. minority-bearing 时，使用 CQG/DCAC，解决“正确 minority vs 错误 minority”。
4. no-majority conflict 时，使用 list-wise discriminant certificate，解决“三个候选谁满足必要条件”。

这比“多样化初始化”更贴近我们的实验发现，也比“minority sentinel”更宽一点：它不是只问是否推翻多数，而是先问当前题目的候选池结构到底允许哪种集体决策。

最终口径应保守：

- 已有同行明确研究 initial diversity / path generation / candidate coverage。
- 我们不能把“生成多样候选”当作主新意。
- 我们可能的贡献是 **coverage-aware consensus protocol**：把候选池结构作为协议切换变量，尤其补上 CQG 未处理的 no-majority conflict 区域。
