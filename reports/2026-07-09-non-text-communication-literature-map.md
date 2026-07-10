# 非文本通信文献地图

日期：2026-07-09

## 电话记录里的研究任务

电话记录的核心结论不是“立刻扩大实验”，而是先把 idea 放回文献脉络里判断能否立住。导师反复追问的是：

1. 现有工作已经做了哪些非自然语言通信，例如 embedding、hidden state、KV cache。
2. 如果继续做 KV/hidden-state 通信，我们和 CIPHER、KVComm、activation communication 的本质区别是什么。
3. 不要把“通信介质”和“通信时机”两个创新点混在一起；先拆开验证。
4. 一个更稳的方向是：分析 hidden/KV 通信的性质，或者把 MAD-M2 的“信息过滤”思想迁移到 KV/hidden-state 通信质量控制上。

因此这份检索按 introduction 里的问题定义来组织，而不是只按标题相似度组织。

## 检索策略

检索日期：2026-07-09

主要检索式：

```text
"multi-agent" +"latent communication" +"LLM"
+"KV cache" +"communication" +"LLM agents"
+"hidden state" +"communication" +"language model agents"
+"embedding" +"multiagent debate"
+"continuous communication" +"multi-agent reinforcement learning"
+"latent reasoning" +"continuous latent space" +"LLM"
+"memory masking" +"multi-agent debate"
```

主要来源：arXiv、ACL Anthology、OpenReview、ICLR/ICML/NeurIPS/EMNLP 页面、USENIX 页面、论文官方 GitHub。当前阶段优先收录能确认题名、年份、作者或官方页面的文献；2025-2026 预印本文献需要后续逐篇核验版本和会议状态。

## Introduction 共同叙事

### 第一层：文本通信是默认方案，但有瓶颈

LLM-based MAS 的默认通信方式是自然语言：agent 生成文本，其他 agent 重新读入文本。Du et al. 的 multiagent debate 和 Liang et al. 的 MAD 都把“多个模型实例交换答案和理由”作为提高 factuality/reasoning 的机制。它们的 introduction 共同假设是：多个独立推理轨迹可以互相纠错。

但后续非文本通信论文把问题重新定义为 language bottleneck：sender 必须把高维内部状态压缩成离散 token，receiver 再把 token 编回连续空间。CIPHER 把这个压缩点定位在 token sampling；activation communication 把问题定位为 natural-language communication 成本高且 decoding 丢掉内部 activation 信息；KVComm 则进一步指出自然语言有高推理成本和信息损失，而 hidden-state 通信又有信息集中与低效问题。

### 第二层：从“说什么”转向“传什么表示”

经典非文本通信论文大致沿着 communicated object 展开：

```text
embedding / soft belief
  -> hidden state / activation
  -> state delta / trajectory
  -> KV cache / selected cache
  -> learned latent message / latent working memory
  -> hybrid latent-text / weight update / shared workspace
```

这对你的题目很重要：如果论文只说“我们不用文本”，已经不够新；需要具体说“为什么这个表示、这个时机、这个过滤/融合策略能解决某个已知瓶颈”。

### 第三层：从“能不能传”转向“怎么控制质量”

导师建议的方向在这里最自然：非文本通道不是天然干净。KV cache 可能携带错误 reasoning、position mismatch、sender identity、prompt artifacts；hidden state 可能过强 steering；embedding 可能保留 soft belief 但不保证 receiver 会正确解释。

所以更有论文味的切口是：

```text
hidden/KV 通信中，哪些信息有益，哪些信息有害？
能否像 MAD-M2 过滤文本 memory 一样，过滤 latent memory / KV memory？
能否在不损失效率优势的前提下提高 latent channel 的可靠性？
```

## 核心必读论文

| 优先级 | 论文 | 年份 | 通信对象 | 为什么读 |
|---|---:|---:|---|---|
| S | Improving Factuality and Reasoning in Language Models through Multiagent Debate | 2023/2024 | 文本答案与理由 | 文本 MAD 的源头基线，说明“多 agent 互相纠错”的原始问题设定。https://arxiv.org/abs/2305.14325 |
| S | Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate | 2023/2024 | 文本辩论 | introduction 里有 Degeneration-of-Thought，和你“答案生成后路径固化”很接近。https://arxiv.org/abs/2305.19118 |
| S | Let Models Speak Ciphers: Multiagent Debate through Embeddings | 2023/2024 | expectation of output embeddings | 第一个非常贴近“非文本 MAS 通信”的经典点：绕开 token sampling。https://arxiv.org/abs/2310.06272 |
| S | Communicating Activations Between Language Model Agents | 2025 | intermediate activations | 直接把 hidden activation 当语言，用 pause-and-combine 的方式通信。https://arxiv.org/abs/2501.14082 |
| S | Augmenting Multi-Agent Communication with State Delta Trajectory | 2025 | token-wise state delta trajectory | 关键启发：传绝对状态不如传状态变化轨迹，更像“搜索方向”。https://arxiv.org/abs/2506.19209 |
| S | KVComm: Enabling Efficient LLM Communication through Selective KV Sharing | 2025/2026 | selected KV pairs | 你的 KV 线必须对齐的核心文献：选择性共享，而不是 raw prefix continuation。https://arxiv.org/abs/2510.03346 |
| S | KVCOMM: Online Cross-context KV-cache Communication for Efficient LLM-based Multi-agent Systems | 2025 | cross-context KV cache | 更偏效率和上下文复用，但对 position/context mismatch 很有参考价值。https://arxiv.org/abs/2510.12872 |
| S | Multi-Agent Debate with Memory Masking | 2026 | 文本 memory filtering | 导师明确提到的可迁移思想：过滤有害 memory。https://arxiv.org/abs/2603.20215 |
| S | Beyond Tokens: A Unified Framework for Latent Communication in LLM-based Multi-Agent Systems | 2026 | survey / taxonomy | 入门地图：WHAT/WHICH/HOW 三轴整理 18 类 latent communication。https://arxiv.org/html/2606.05711 |

## 强相关扩展池

### Embedding / soft belief 通信

1. **CIPHER / Let Models Speak Ciphers**。传 token embedding expectation，本质是把 next-token distribution 的 soft belief 传给其他 agent。适合支撑“离散 token 会丢掉分布信息”的 intro 论证。
2. **Mixture of Thoughts: Learning to Aggregate What Experts Think, Not Just What They Say**。Beyond Tokens 综述列为 hidden/projection/cross-attention 类方法；需要后续核验原文。
3. **Soft / latent CoT 系列**。虽然不是 inter-agent communication，但能支撑“模型可以消费非离散 token 的连续表示”。

### Hidden state / activation 通信

1. **Communicating Activations Between Language Model Agents**。训练免、参数免，直接 pause receiver 的 forward，把 sender activation 合进来。
2. **State Delta Trajectory / SDE**。从 hidden state 转向 hidden-state change，是你“搜索方向而非局部答案”的最强相邻文献。
3. **Interlat / Enabling Agents to Communicate Entirely in Latent Space**。直接传 last hidden states，并训练 receiver 解释 latent message；还做 latent compression。https://arxiv.org/abs/2511.09149
4. **Thought Communication in Multiagent Collaboration**。把 latent thought formalize 成 latent variable model，强调 shared/private thoughts 的识别。https://arxiv.org/abs/2510.20733
5. **Dense Latent Communication Across Heterogeneous Agents**。2026 新文献，重点是 heterogeneous agent 的 dense KV/latent alignment。https://arxiv.org/abs/2606.13594

### KV cache 通信与复用

1. **KVComm: Selective KV Sharing**。层选择、注意力重要性、Gaussian prior，是“传哪些 KV”的直接参考。
2. **Online Cross-context KV-cache Communication**。看跨上下文复用如何处理不同上下文和在线通信。
3. **DroidSpeak: KV Cache Sharing for Cross-LLM Communication and Multi-LLM Serving**。系统方向，重点是同源 fine-tuned models 之间 KV cache reuse 与 selective recomputation。https://arxiv.org/abs/2411.02820
4. **Latent Cache Flow: Model-to-Model Communication Without Text**。通过小 adapter 翻译/压缩 KV，强调不同上下文 agent communication。https://arxiv.org/abs/2605.22863
5. **Latent Collaboration in Multi-Agent Systems / LatentMAS**。训练免，latent working memory，纯 latent collaboration。https://arxiv.org/abs/2511.20639
6. **Cache-to-Cache: Direct Semantic Communication Between LLMs**。Beyond Tokens 列为 KV-cache learned fuser 类，需要继续核验原文。
7. **Q-KVComm: Efficient Multi-Agent Communication via Adaptive KV Cache Compression**。Beyond Tokens 列为 compressed KV 类，需要继续核验原文。
8. **LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents**。Beyond Tokens 列为 multi-LoRA / same-backbone KV sharing 类，需要继续核验原文。
9. **RelayCaching: Accelerating LLM Collaboration via Decoding KV Cache Reuse**。Beyond Tokens 列为 decoding KV reuse 类，需要继续核验原文。
10. **Agent Memory Below the Prompt: Persistent Q4 KV Cache for Multi-Agent LLM Inference on Edge Devices**。偏部署/edge memory，可作为 KV compression 和 persistent latent memory 的背景。

### Hybrid latent-text / workspace / weight communication

1. **HyLaT: Efficient Multi-Agent Communication via Hybrid Latent-Text Protocol**。2026 新文献，明确提出 text interpretable but verbose、latent efficient but opaque 的 trilemma。https://arxiv.org/abs/2605.25421
2. **Good Agentic Friends Do Not Just Give Verbal Advice: They Can Update Your Weights**。通信对象变成权重/LoRA 更新，可作为“非文本通信更广义”的边界案例。https://arxiv.org/html/2605.13839
3. **BIGMAS / Brain-Inspired Graph Multi-Agent Systems for LLM Reasoning**。Beyond Tokens 归为 shared workspace / global workspace 类，需要核验原文。
4. **Vision Wormhole: Latent-Space Communication in Heterogeneous Multi-Agent Systems**。多模态 latent communication，适合放在相关工作但不作为主线。

### Single-agent latent reasoning，可做理论邻居

1. **Training Large Language Models to Reason in a Continuous Latent Space / Coconut**。单 agent latent CoT，但 introduction 的“language space may not be optimal for reasoning”可以支撑你对中间状态的动机。https://arxiv.org/abs/2412.06769
2. **Pause tokens / filler tokens / latent coprocessor / LatentSeek**。不是 agent communication，但说明 latent/soft computation 可作为 inference-time compute 的载体。
3. **System 1 and 2 communication for latent reasoning in LLMs**。更像 dual-system / soft-token budget 的分析，适合补“latent reasoning 不一定天然优于 text”的反证。

### 经典 MARL learned communication 祖先脉络

1. **Learning to Communicate with Deep Multi-Agent Reinforcement Learning / RIAL-DIAL**。端到端学习通信协议，DIAL 用 differentiable channel。https://arxiv.org/abs/1605.06676
2. **Learning Multiagent Communication with Backpropagation / CommNet**。连续通信向量，与现代 hidden-state 通信有概念祖先关系。https://arxiv.org/abs/1605.07736
3. **TarMAC: Targeted Multi-Agent Communication**。学习“发什么、发给谁”，对后续 latent channel routing 有启发。https://arxiv.org/abs/1810.11187
4. **IC3Net: Learning When to Communicate at Scale**。gating 机制，适合作为“不是所有状态都该传”的经典先例。https://arxiv.org/abs/1812.09755
5. **Emergent Multi-Agent Communication in Deep Reinforcement Learning**。离散 emergent language 脉络，主要用于相关工作背景。

## 对你的研究最有用的文献切线

### 切线 A：非文本通信的“信息过滤”问题

可写成：

```text
Existing latent communication methods reduce language bottlenecks, but they often assume the transmitted latent content is useful. In debate-style reasoning, however, previous work on memory masking shows that shared memories can be harmful when they contain erroneous reasoning. This raises a latent-channel analogue: which parts of hidden/KV memory should be shared, suppressed, or gated?
```

对应文献：MAD-M2、KVComm、SDE、AC、DIAL/IC3Net。

这条线最贴合导师建议，也比“提前通信一次”更容易和已有工作区分。

### 切线 B：从 raw KV continuation 改成 selective KV side-channel

你现有 Pre-KV 更像“接着 sender past 续写”，而 KVComm 更像“receiver 保持自己的上下文，同时可选择注意 sender 的 selected KV”。这两者在论文里必须严格区分。

可形成实验问题：

```text
Does selected, side-channel KV communication reduce harmful anchoring compared with raw prefix continuation?
```

对应文献：KVComm、Online Cross-context KVComm、DroidSpeak、LCF。

### 切线 C：时机不是固定 token 数，而是 latent state quality

导师担心“前 64 token / 第 16 层 / 22 层”这种选择太 ad hoc。文献里可借用的说法是：communication scheduling / gating / layer selection / state delta salience。

可形成实验问题：

```text
Can latent communication be triggered by state-quality or disagreement signals rather than fixed decoding steps?
```

对应文献：IC3Net、TarMAC、KVComm layer selection、SDE、MAD-M2。

### 切线 D：finding paper 方向

如果方法暂时不 work，可以转成分析类：

```text
Rethinking Latent Communication in LLM Debate:
When Does Hidden-State/KV Sharing Help or Hurt?
```

可能的 finding：

1. raw KV continuation 的收益主要来自特定题型/特定转移，不是稳定提升。
2. 错误 sender latent 会造成 anchoring，比文本错误更难过滤。
3. state delta 比 absolute state 更像方向信号。
4. 同题 latent 与随机/错题 latent 的差异决定这个方向是否成立。
5. natural-language debate 更稳，但 token cost 高；latent channel 更省但质量控制更难。

## 建议阅读顺序

第一批，建立主线：

1. Du et al. 2023/2024 Multiagent Debate
2. Liang et al. 2023/2024 MAD divergent thinking
3. MAD-M2 Memory Masking
4. CIPHER
5. Communicating Activations
6. State Delta Trajectory
7. KVComm selective KV sharing
8. Beyond Tokens survey

第二批，扩展 KV/latent 机制：

1. Online Cross-context KVComm
2. DroidSpeak
3. LatentMAS
4. Interlat
5. Latent Cache Flow
6. HyLaT
7. Thought Communication
8. Dense Latent Communication Across Heterogeneous Agents

第三批，补祖先和理论边界：

1. DIAL/RIAL
2. CommNet
3. TarMAC
4. IC3Net
5. Coconut
6. System 1/2 latent reasoning

## 下一步落地建议

短期不要再扩全量实验。先做一个文献驱动的小实验矩阵：

```text
baseline: no communication
raw prefix KV continuation: 你现在的 Pre-KV
selected side-channel KV: 尽量贴近 KVComm
state delta injection: 贴近 SDE
filtered latent/KV: 借鉴 MAD-M2，过滤 low-confidence / disagreement / harmful state
controls: same-question true latent, other-question latent, random latent, zero latent
```

评价不要只看总准确率，还要看：

```text
BaW_to_C
BaC_to_W
answer-change rate
latent channel 对原本正确样本的破坏率
同题 latent 相对 random/other-question latent 的净收益
token/latency cost
```

这能直接回答导师关心的两个问题：这个通道里有没有真实搜索信号，以及如何提高 latent/KV 传递质量。

