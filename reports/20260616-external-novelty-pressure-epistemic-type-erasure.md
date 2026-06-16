# 外部压力对齐报告：这个切口到底新不新

日期：2026-06-16

状态：基于本地阶段性结果和 2026-06-16 当日联网检索。本文只做研究定位和
新颖性压力测试，不包含新的 GPU 实验。

## 一句话结论

这个切口有新颖性，但它不是“完全无人区”。

如果把它说成：

```text
多智能体应该用结构化通信。
```

那基本不新，PACT、DeLM、ReAgent、CTHA、多智能体通信 survey 都已经覆盖
了很大一部分。

如果把它说成：

```text
不可信上下文会污染智能体，所以要做 provenance / control-data separation。
```

那也不够新，CaMeL、ARGUS、semantic laundering、tool receipts 这些工作
已经把安全边界、工具边界、claim provenance、epistemic warrant 讲得很近。

但如果把它收窄成：

```text
跨智能体通信中，发送方的中间计算产物在跨边界时被压平成自然语言或公共
状态；接收方随后把它错误转换成更强的认识论对象。这个错误转换不只表现为
复制错误答案，还表现为继承错误算子、错误数字角色、错误关系骨架、错误
任务契约、错误记忆状态或伪验证结果。
```

这个切口仍然有比较明确的新颖空间。

我现在的判断是：

```text
弱名称新颖性，中强问题定义新颖性，中等实验操作化新颖性，潜在 A 会诊断/
benchmark/protocol 论文味道。
```

也就是说，它现在不是一个“我发明了结构化 agent 通信”的故事，而更像：

```text
LLM 多智能体通信里的 invalid epistemic casts：定义、测量、案例机制和
协议边界。
```

## 我们不能再声称什么

外部压力之后，有几类 claim 需要主动放弃或降级。

### 不能声称：结构化消息本身是新点

PACT 的核心已经非常接近“inter-agent communication 应该被投影成更紧凑的
action-state record”。它强调自然语言消息太自由、太长、太不稳定，下游
接收方需要保留 action、task-relevant state、result，而不是保留完整中间
内容。

这直接压住了我们早期“消息应该怎么保留”的宽泛说法。

参考：

- [What Should Agents Say? Action-state Communication for Efficient Multi-Agent Systems](https://arxiv.org/html/2606.05304v1)

### 不能声称：共享 verified context 是新点

DeLM 已经明确提出多个 agent 通过 shared verified context 和 task queue
异步协作，agent 读取累计进度并写回 compact verified updates。这个工作把
“公共可验证上下文作为通信 substrate”讲得非常正。

所以我们不能把故事写成“我们发现共享状态需要验证”。这已经是附近工作的
主战场。

参考：

- [Decentralized Multi-Agent Systems with Shared Context](https://arxiv.org/abs/2606.10662)

### 不能声称：typed messages 是新点

ReAgent 已经有 assert、inform、reject、challenge 之类的 typed messaging
语义，并且把 backtracking、conflict resolution、结构化 JSON 输出放进多跳
QA 流程。CTHA 也提出 typed summary、plan、policy packets 和 authority
manifold constraints。

所以“给消息加类型标签”不是我们的贡献。

参考：

- [ReAgent: Reversible Multi-Agent Reasoning for Knowledge-Enhanced Multi-Hop QA](https://arxiv.org/abs/2503.06951)
- [CTHA: Constrained Temporal Hierarchical Architecture for Stable Multi-Agent LLM Systems](https://arxiv.org/abs/2601.10738)

### 不能声称：prompt injection / context poisoning 风险是新点

CaMeL 已经从 control flow / data flow 的角度防 prompt injection；ARGUS
已经从 influence provenance graph 和 decision auditing 的角度追踪不可信
上下文如何影响 agent 决策。

所以如果我们把问题写成“不可信文本会影响 agent”，会被安全论文直接覆盖。

参考：

- [Defeating Prompt Injections by Design](https://arxiv.org/abs/2503.18813)
- [ARGUS: Defending LLM Agents Against Context-Aware Prompt Injection](https://arxiv.org/abs/2605.03378)

### 不能声称：epistemic typing / warrant 这个哲学方向没人讲

这一点最危险。

Semantic Laundering 这篇位置论文已经非常接近我们的一部分语言：它说 agent
架构会把 information transport mechanism 和 epistemic justification
混在一起，工具边界会把弱 warrant 的 proposition 洗成高 epistemic status。
它还明确使用了 epistemic typing、warrant erosion、LLM-as-judge circular
justification 这些概念。

NabaOS / Tool Receipts 也把 agent claim 按 epistemic source 分类，比如直接
工具输出、推理、外部 testimony、absence、ungrounded opinion。

所以“epistemic type”这个词不能当成独占创新点。

参考：

- [Semantic Laundering in AI Agent Architectures](https://arxiv.org/html/2601.08333v1)
- [Tool Receipts, Not Zero-Knowledge Proofs: Practical Hallucination Detection for AI Agents](https://arxiv.org/abs/2603.10060)

### 不能声称：peer influence / debate persuasion 是新点

多智能体 debate 里“正确模型被错误同伴说服”已经有人系统做。Talk Isn't
Always Cheap 讲 peer reasoning 让模型从对变错；When Persuasion Overrides
Truth 直接用 persuasion override rate 衡量错误说服；The Cost of Consensus
也在打“共识不一定提高推理”。

所以“同伴错误会影响模型”不是我们的新点。

参考：

- [Talk Isn't Always Cheap: Understanding Failure Modes in Multi-Agent Debate](https://arxiv.org/abs/2509.05396)
- [When Persuasion Overrides Truth in Multi-Agent LLM Debates](https://arxiv.org/abs/2504.00374)
- [The Cost of Consensus](https://arxiv.org/html/2605.00914v1)

## 真正还能站住的新颖点

外部压力挤完之后，剩下来的东西反而更清楚。

### 新颖点一：不是消息结构，而是跨边界后的“允许转换”

PACT 问的是：

```text
agent 之间应该说什么，怎么把消息压成 action-state record。
```

我们更应该问的是：

```text
接收方被允许对发送方产物做什么类型转换。
```

同一段内容可以是：

- 私有草稿；
- 同伴消息；
- 共享工作区条目；
- 已接纳状态；
- 记忆；
- verifier 结果；
- 低置信假设；
- 非承诺推理；
- 可见候选答案；
- 隐藏 metadata。

这些不是同一种东西。真正的问题不是“有没有结构”，而是：

```text
一个对象从 hypothesis / candidate / derivation / memory-candidate /
verifier-like prose 变成 fact / commitment / reusable operator /
persistent memory / procedural approval 的时候，有没有合法授权。
```

这个“合法 cast / 非法 cast”的角度，比单纯 typed message 更尖。

### 新颖点二：非复制型算子继承

外部的 debate / persuasion 工作主要看答案被说服、观点转移、准确率下降、
confidence 错置。我们的 MATH 结果里最有价值的不是“模型复制了错误答案”，
而是：

```text
模型没有复制同伴错误最终答案，却继承了错误关系、错误方程表面、错误数字
角色或错误计数边界。
```

本地证据：

- MATH 权威阶梯里 `57` 张违规卡，直接错误答案采纳只有 `14` 张。
- 其余 `43` 张是非复制型算子候选。
- 错误方程表面、错误数字角色绑定、错误关系骨架三类加起来构成主要机制。
- `math121` 的代表案例不是复制同伴错误答案 `36√2`，而是从正确 `18√3`
  漂到 `18√2`。

这个点很重要，因为它说明现有“copy rate / answer uptake / persuasion
override”指标会低估通信失败。

### 新颖点三：通信生命周期，而不是孤立上下文影响

CaMeL、ARGUS、semantic laundering 都更偏工具边界、安全边界或一般 agent
架构。我们的实验证据更具体地指向：

```text
同一发送方产物在不同通信生命周期状态下，会诱发不同接收方行为。
```

本地证据：

- PACT typed-boundary split：候选答案隐藏或省略时，能救大量 wrong-contract
  和 forged-final 失败；候选可见时，新增权威违规明显上升。
- MATH type-erasure v2：共享工作区条目比普通同伴消息更容易出现非复制型
  算子漂移。
- sender-receiver micro-protocol：已接纳状态、擦除消息、类型化消息、隔离
  拒收、控制组之间出现不同错误模式。

这个 lifecycle 维度让它不像单纯 prompt injection，也不像普通上下文污染。

### 新颖点四：把“类型安全”从规范口号变成可测诊断

Semantic Laundering 讲得很近，但它主要是 position / formal architecture
style；NabaOS 主要是 tool receipt / claim verification。我们的潜在贡献可以
更实证：

```text
给定同一 artifact，改变其通信类型、接纳状态、候选可见性和生命周期位置，
测 receiver 是否发生 invalid cast。
```

如果我们把评估器做成：

- answer copy；
- operator uptake；
- boundary obedience；
- useful evidence retention；
- admitted-state misuse；
- hidden-metadata leakage control；
- verifier-prose-as-approval；
- memory-candidate-as-memory；

那它就从“哲学上应该区分 warrant”变成了“LLM-MAS 里可复现实验诊断”。

这才是它有 A 会味道的地方。

## 新颖性评分

下面是我比较冷酷的评分。

| 维度 | 评分 | 判断 |
| --- | ---: | --- |
| 名称新颖性 | 2/5 | “epistemic type”附近已经有人用，“type erasure”也容易撞 PL 语义。名称别押太重。 |
| 问题定义新颖性 | 4/5 | “跨智能体产物的 invalid epistemic cast”目前没有被相邻工作完整吃掉。 |
| 实验操作化新颖性 | 3.5/5 | 非复制型算子继承、同内容多生命周期状态对照比较有意思，但样本还集中。 |
| 方法新颖性 | 2.5/5 | 目前还不是完整方法，typed protocol 也容易被说成已有结构化通信。 |
| 诊断/benchmark 新颖性 | 4/5 | 如果做成 TypeCastArena + boundary obedience + operator uptake，空间很不错。 |
| A 会潜力 | 3.5/5 | 有味道，但必须把证据去集中化，并证明它解释了现有指标看不见的失败。 |

综合：

```text
不是强方法论文雏形，像强诊断论文雏形。
```

## 最可能被审稿人攻击的地方

### 攻击一：这不就是 prompt injection 吗

这个攻击一定会来。

回应口径：

```text
prompt injection 研究通常关心恶意不可信数据越权影响工具调用、控制流或
敏感动作。我们研究的是非对抗性多智能体协作中，peer-generated intermediate
artifacts 被接收方误转成更强认识论对象。很多失败不涉及攻击指令，也不涉及
工具权限，而是数学推理里的 operator inheritance。
```

还要主动承认：

```text
安全边界和 provenance 工作是重要相邻工作，我们不是替代它们，而是补上
reasoning communication 的类型转换诊断。
```

### 攻击二：这不就是 PACT 吗

回应口径：

```text
PACT 解决“agent 应该说什么”和“如何把自由文本投影成 action-state public
record”。我们问的是 public record 或 peer artifact 进入 receiver 后，会被
允许或不允许做哪些 epistemic cast。PACT 是一种强相邻协议；我们的贡献是
诊断 PACT 类公共状态仍会发生 candidate-as-commitment、task-contract-as-
answer-contract、partial-derivation-as-operator 等错误转换。
```

最好的证据是 PACT typed-boundary split：同样 typed public state，候选答案
可见和不可见差异很大。这说明问题不只是“有没有结构化字段”。

### 攻击三：这不就是 typed speech acts / ReAgent 吗

回应口径：

```text
typed messages 已经存在。我们的 claim 不是发明 typed messages，而是发现
LLM receivers 不稳定地遵守这些类型，并且会在答案不复制的情况下继承下游
算子。我们把类型系统的关注点从 sender-side schema 转到 receiver-side cast
behavior。
```

换句话说：

```text
已有工作定义 message type；我们测 type 是否真的约束了 receiver 的继承行为。
```

### 攻击四：这不就是 debate persuasion 吗

回应口径：

```text
debate persuasion 主要衡量 peer reasoning 让最终答案或判断从对变错。我们的
关键指标不是最终答案复制，而是错误 artifact 对内部求解算子的影响。receiver
可以输出一个既不是金标、也不是 peer final answer 的第三答案，这恰恰是普通
persuasion/copy 指标漏掉的地方。
```

本地 MATH 机制审计就是这里的核心证据。

### 攻击五：Semantic Laundering 已经讲了 epistemic warrant

这是最强的撞点之一。

回应口径：

```text
Semantic Laundering 给出了架构层面的 warrant / tool-boundary formalization，
主要论证“工具边界不自动提供 epistemic warrant”。我们的工作可以承认并继承
这个视角，但贡献放在 multi-agent communication artifacts 的 empirical cast
failures：同一 sender artifact 在 message、workspace、memory、verifier、
candidate、quarantine 等通信生命周期状态中的 receiver behavior。
```

换句话说，它更像上位理论压力；我们要做下位实证和诊断工具。

### 攻击六：样本太挑，case 太集中

这个攻击目前成立。

本地 MATH 机制里 `math159`、`math121`、`math96` 贡献很重。当前结果适合
说“机制存在”，不适合说“自然分布中频率很高”。

回应不能硬顶，只能说：

```text
当前阶段是 mechanism discovery。下一阶段需要 deconcentrated TypeCastArena：
限制单 case 贡献，扩大 artifact families，并报告 leave-one-case-out 结果。
```

### 攻击七：最新 live TypeCastArena 不是零违规吗

这个攻击也会来。

回应口径：

```text
最新 live sender/receiver run 是负向诊断：它说明那批 live sender artifacts
对 Qwen2.5-14B receiver 太容易，或重算保护太强，不足以诱发 final-answer
level violation。它不是推翻机制，而是暴露现有评分只看最终答案，缺少
boundary obedience 和 unauthorized-use 指标。
```

这个不能吹。它应该被写成“arena framework validated, pressure too weak,
metrics incomplete”。

## 最建议的论文定位

我建议不要把主名押在 “Epistemic Type Erasure” 上。这个名字漂亮，但撞点
太多，而且容易被认为只是 PL 类比或哲学包装。

更稳的标题方向：

```text
Invalid Casts in LLM Agent Communication
```

或者：

```text
Communication-Boundary Type Safety for LLM Multi-Agent Systems
```

或者：

```text
When Peer Artifacts Become State: Measuring Invalid Epistemic Casts in
LLM Multi-Agent Communication
```

中文内部名可以继续叫“认识论类型擦除”，但对外更建议用：

```text
cross-agent epistemic cast failures
```

或：

```text
communication-boundary type safety
```

这样能避开“我发明 epistemic type”这个不必要的战场。

## 推荐摘要骨架

一个更抗打的摘要句式可以是：

```text
LLM multi-agent systems increasingly communicate through peer messages,
shared workspaces, memories, verifier outputs, and public state. Existing
protocols often structure what agents say, but leave underspecified what
receivers may inherit from peer artifacts. We identify invalid epistemic casts
as a failure mode: receivers treat hypotheses as facts, candidates as
commitments, partial derivations as reusable operators, or verifier-like prose
as procedural approval. Across controlled QA and MATH probes, we show that
these failures are not captured by answer-copy metrics; many manifest as
non-copy operator inheritance. We introduce a diagnostic arena for measuring
cast failures across communication lifecycle states and evaluate typed/admission
protocols that reduce some casts while preserving useful evidence.
```

这个版本把 claim 收得比较准：

- 不说自己发明 structured communication；
- 不说自己解决 prompt injection；
- 不说“类型标签万能”；
- 把新点放在 receiver-side cast behavior；
- 把 MATH 的非复制型算子继承放进主贡献。

## 当前证据和外部工作的对应关系

| 我们的证据 | 外部相邻工作会怎么压 | 剩余可讲空间 |
| --- | --- | --- |
| PACT typed-boundary split | PACT 本身已经讲 action-state communication | 我们显示 candidate visibility 和 public-state authority 不是结构化字段能自动解决的 |
| MATH authority genesis | debate/persuasion 会说 peer influence 已知 | 我们强调非复制型算子继承，而非最终答案复制 |
| type-erasure v2 | typed message / CTHA 会说 type packets 已知 | 我们测 receiver 是否遵守类型，而不是只设计 sender schema |
| sender-receiver micro-protocol | DeLM 会说 shared verified context 已知 | 我们拆 admission lifecycle：message、workspace、memory、verifier、quarantine 的不同 cast 风险 |
| latest live TypeCastArena 零违规 | 审稿人会说效应不稳 | 我们承认为压力太弱，并把下一步转向 boundary obedience 和去集中化样本 |

## 下一步最关键的非 GPU 工作

现在最值得做的不是再包装概念，而是把“cast”变成可审计对象。

### 一，写 cast 类型表

最少要定义：

| 源类型 | 非法 cast | 例子 |
| --- | --- | --- |
| hypothesis | hypothesis -> fact | 同伴猜测被当成证据事实 |
| candidate answer | candidate -> commitment | 可见候选变最终答案锚点 |
| partial derivation | derivation -> reusable operator | 局部方程表面被继承 |
| peer rationale | rationale -> evidence | 同伴解释被当成外部观察 |
| memory candidate | candidate -> persistent memory | 临时文本被当长期状态 |
| verifier prose | prose -> procedural approval | 生成式“通过”被当程序验证 |
| task interpretation | local interpretation -> answer contract | 同伴任务理解覆盖原问题 |

### 二，补 boundary obedience 指标

最新 TypeCastArena 零最终答案违规，但它可能仍有：

- 在 not-admitted 条件下引用 Agent A；
- 在 quarantine 条件下使用被拒收内容；
- 在 typed noncommitment 条件下把候选当最终承诺；
- 在 partial derivation 条件下不重新推导，直接沿用局部算子。

这类指标不需要 GPU，可以先对现有 `204` 行做本地文本分析和人工审计。

### 三，做去集中化 packet 设计

现有关键案例太集中。下一包应该在设计上限制：

- 每个 MATH case 最多贡献固定数量；
- artifact family 均衡：final answer、equation surface、numeric role、
  relation skeleton、task contract、verifier prose、memory candidate；
- 每个 artifact 都有 inert / message / workspace / memory / verifier /
  typed / quarantine 对照。

### 四，加入 useful evidence arm

否则协议可能被批评成“把所有同伴信息都删掉当然安全”。

必须证明：

```text
好的协议不只是减少错误 cast，还能保留有用证据的合法继承。
```

这决定它是 reliability paper，还是单纯的 prompt hardening note。

## 最终判断

这个切口的新颖性不是“世界上没人讲 epistemic type”。有人讲，而且讲得不浅。

它的新颖性在于：

```text
把 epistemic typing / warrant / structured communication 这些上位概念，
压到 LLM 多智能体通信中的 receiver-side invalid cast 行为，并用同一 sender
artifact 在不同生命周期状态下的行为差异来测量。
```

最值得赌的核心句是：

```text
多智能体通信失败不只是错误消息被复制，而是发送方产物被接收方转换成了
不该拥有的认识论权力。
```

如果我们能把这个句子用去集中化样本、boundary obedience 指标、operator
uptake 指标和 useful-evidence retention 立住，它就有 A 会味道。

如果立不住，它会退化成“上下文权威 / prompt injection / structured
communication 的一个漂亮说法”。

所以现在最准确的状态是：

```text
切口有新颖性，但新颖性集中在诊断对象和评估粒度，不在宽泛概念和结构化
协议本身。值得迈大步，但下一步必须更像 benchmark/diagnostic science，
不要再像 prompt variant exploration。
```
