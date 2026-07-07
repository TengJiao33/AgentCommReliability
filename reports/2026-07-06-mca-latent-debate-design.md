# MCA 潜状态多轮讨论设计记录

日期：2026-07-06

## 背景

当前 `MCA-Pre-KV question_only` 不是多轮讨论机制。它只做一件事：sender 在不生成答案、不生成理由的情况下读题，receiver 接收这个读题后的 KV cache，然后独立生成一次答案。

因此，它不能直接和 Standard MAD final 做同层级比较。Standard MAD final 包含两轮文本讨论：第一轮 agent 生成答案和理由，第二轮 agent 看到其他 agent 的文本输出后再修正。当前 `MCA-Pre-KV question_only` 只对应“前置潜状态增强的一轮解题”。

## 已观察到的参照水平

当前主口径的 Standard MAD 基线：

- 路径：`experiments/standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/`
- 任务：`math500/test`
- 模型：`Qwen2.5-7B-Instruct`
- 智能体数：3
- 轮数：2
- 输出预算：4096
- 初始多数：364/500 = 0.728
- Standard MAD final：378/500 = 0.756

`MCA-Pre-KV question_only` 完整运行结果：

- baseline：341/500 = 0.6820
- final：362/500 = 0.7240
- delta：+21
- transition：`BaC_to_C=317`，`BaC_to_W=24`，`BaW_to_C=45`，`BaW_to_W=114`

这个完整结果说明 question-only KV 对自身一轮 baseline 有正向影响，但没有超过 Standard MAD final。

## 术语边界

本文档中 `sender`、`receiver` 和 `debate agent` 的含义如下：

- `sender`：只读题并产生 KV cache 的状态来源。`question_only` 设置下，sender 的 `generated_tokens=0`，不生成答案、不生成理由、不生成可读线索。
- `receiver`：接收 sender 的 KV cache 后从头解题并生成第一轮答案的 agent。
- `debate agent`：读取第一轮可读文本答案后，按 Standard MAD 文本讨论 prompt 生成第二轮答案的 agent。

因此，`Pre-KV + Standard MAD` 是一个两阶段桥接机制：

```text
第一阶段：前置潜状态通信，通信对象是 live KV；
第二阶段：文本讨论，通信对象是第一阶段 receiver 输出的可读答案/理由。
```

它不是纯潜状态多轮讨论。纯潜状态多轮讨论要求后续轮次继续传递 KV 或 hidden state，而不是把第一轮输出文本作为 debate memory。

## 设计问题

真正需要回答的问题不是：

```text
一轮 MCA-Pre-KV 能不能赢两轮 Standard MAD？
```

更合理的问题是：

```text
前置潜状态通信能否增强多轮讨论？
```

这里的“多轮讨论”不能简单退回 MCA-T 的文本 patch。MCA 语境下的核心约束仍然是：通信机制应尽量发生在答案形成之前或答案形成过程中，而不是在答案已经固定后做格式化审计和提示修补。

## 方案 A：Pre-KV 作为 Standard MAD 前置层

这是最直接的可检验方案。

流程：

```text
题目出现
-> 3 个 sender 只读题，生成 question-only KV
-> 3 个 agent 带各自或配对的 KV 生成第一轮答案
-> 按 Standard MAD，把第一轮答案和理由广播给其他 agent
-> 第二轮正常讨论和修正
-> final majority
```

该方案回答：

```text
question-only KV 能否改善 Standard MAD 的第一轮初始状态，并让第二轮文本讨论获得更好的 final majority？
```

主对照：

```text
Standard MAD final: 378/500
Pre-KV + Standard MAD final: ?/500
```

次要读数：

- 第一轮 majority 是否高于 Standard MAD initial 364/500；
- 第二轮 final 是否高于 Standard MAD final 378/500；
- Pre-KV 是否减少 Standard MAD 的后续伤害；
- Pre-KV 是否改变第二轮文本讨论中的错误传播模式。

技术边界：

- 第二轮仍然是文本讨论，所以这不是纯潜状态讨论；
- 但第一轮答案形成前发生了潜状态通信，因此它可以检验“潜状态前置是否能增强现有 MAD”；
- 如果该方案没有提升，则说明 question-only KV 很可能不能直接作为 Standard MAD 的无痛前置模块。

已完成运行：

- 路径：`experiments/20260706-a8002-math500-live-mca-pre-kv-then-mad-qwen25-7b-full/`
- no-channel 第一轮：347/500 = 0.6940
- Pre-KV 第一轮：349/500 = 0.6980
- debate final：363/500 = 0.7260
- Pre-KV 相对 no-channel：+2
- debate 相对 no-channel：+16
- debate 相对 Pre-KV 第一轮：+14

该结果没有超过 Standard MAD 主基线 final 378/500。它说明当前 bridge 版本可以完成流程，但没有证明 question-only Pre-KV 能作为 Standard MAD 的直接增强模块。该结果也显示，同进程 bridge 中的 Pre-KV 第一轮增益明显小于此前独立 `MCA-Pre-KV question_only` 运行的 +21，需要把两者的运行口径和生成参数差异分开审计。

## 方案 B：多源 Pre-KV 门控

当前 `MCA-Pre-KV question_only` 的简化结构是：3 个 sender state，3 个 receiver，每个 receiver 接收一个 sender 的 KV。它没有判断哪个 sender state 更可靠，也没有把多个 sender state 作为候选通信对象进行选择。

多源门控版本把通信对象从“固定配对”改成“候选状态集合”。

流程：

```text
题目出现
-> 3 个 sender 只读题，得到 3 个 question-only KV
-> receiver 分别接收不同 sender KV 生成候选答案
-> 使用非答案泄漏的门控信号选择或加权候选
-> 输出 majority 或 gated majority
```

可用门控信号必须避免直接使用 gold 或答案正确性。候选信号包括：

- receiver 输出的解析成功与否；
- final answer 格式是否稳定；
- 多个 receiver 是否收敛到同一答案；
- 输出长度、置信度 proxy、平均选中 token logprob；
- baseline 与 KV receiver 的一致性或分歧模式。

主对照：

```text
固定配对 Pre-KV final
多源门控 Pre-KV final
```

技术边界：

- 如果门控使用生成后的答案文本，它仍然不是纯前置机制；
- 但它不是后验给模型提示修改答案，而是对多个潜状态解题轨迹做选择；
- 该方案重点处理当前结果中的 `BaC_to_W` 伤害问题。

## 方案 C：多轮 KV-state 讨论

这是更接近 MCA 原意的版本。每轮传递的不是答案文本，而是新的潜状态。

流程：

```text
Round 0:
每个 agent 只读题，得到 state_0

Round 1:
每个 receiver 接收其他 agent 的 state_0
从头解题或形成新的中间状态 state_1

Round 2:
receiver 再接收 state_1
形成 state_2 或最终答案

Final:
只在最后阶段生成 final answer
```

这个方案回答：

```text
在不广播文本答案和文本理由的情况下，多个 agent 的潜状态能否经过多轮交换产生更好的问题表示？
```

可能的通信结构：

- one-to-one：receiver 只接收一个 sender state；
- all-to-one multi-run：receiver 分别接收多个 sender state，生成多个候选，再投票；
- KV concat：把多个 sender KV 拼成一个 prefix；
- KV selection：根据非答案门控选择一个 sender KV；
- state distillation：把多个 sender state 压缩成一个共享潜状态。

主要风险：

- KV concat 可能引入位置编码和上下文长度问题；
- 多轮 state 可能放大错误题型先验；
- 如果每轮都生成可读文本，再把文本喂回去，就会退回 Standard MAD 或 MCA-T；
- 如果 receiver 在第一轮已经生成最终答案，再做 state exchange，就会重新变成后验 patch。

## 方案 D：生成过程中的交错潜状态通信

这是最底层、也最接近“真实解题过程中交流”的版本。

流程：

```text
所有 agent 同时开始生成
每生成 N 个 token 暂停
捕获各自当前 KV 或 hidden state
交换或写入共享 latent memory
继续生成下一段
重复若干次
最后输出答案
```

该方案和方案 C 的区别是：方案 C 每轮通常从头解题或重新生成；方案 D 在同一次解题轨迹中插入通信。

它回答：

```text
通信发生在答案生成过程中，而非答案生成之前或之后时，是否能减少错误分叉并提高最终答案？
```

主要技术难点：

- 需要改写 generation loop；
- 不同 agent 的生成长度不同，暂停点难以对齐；
- KV cache 的 batch 组织和内存占用会快速增长；
- 一个 agent 的错误轨迹可能在中途污染其他 agent；
- hidden state 注入若没有门控和归一化，可能重复 MCA-Pre-S 当前的破坏性结果。

## 与 MCA-T 的边界

以下操作不应算作 MCA 潜状态讨论：

- 生成初始答案后，再广播文本 cue；
- 让模型写 certificate、audit、XML 或格式化自证；
- 根据别人的最终答案写反驳或修正；
- 使用 benchmark 专属角色或题型专属 prompt；
- 让 receiver 看到 sender 的最终答案，但声称这是潜状态通信。

允许作为对照但不能作为主机制解释的操作：

- Standard MAD 文本讨论；
- Pre-KV + Standard MAD；
- 生成后 rerank；
- 答案一致性过滤；
- 文本 verifier。

## 可检验对照

最低可用对照矩阵：

| 机制 | 是否有前置潜状态 | 是否有文本讨论 | 主要读数 |
| --- | --- | --- | --- |
| No-channel one-round | 否 | 否 | 一轮 majority |
| MCA-Pre-KV one-round | 是 | 否 | 前置潜状态对一轮解题的影响 |
| Standard MAD | 否 | 是 | 文本讨论基线 |
| MCA-Pre-KV + Standard MAD | 是 | 是 | 前置潜状态是否增强文本讨论 |
| Multi-round KV-state | 是 | 否 | 多轮潜状态交换是否有效 |

主 claim 只有在同口径比较下才成立。尤其需要避免把一轮 Pre-KV 和两轮 Standard MAD 直接解释成同一层级竞争。

## 需要记录的字段

多轮版本需要保存比当前 `mca_pre` 更细的轨迹：

- 每题每轮的 agent id；
- 每轮的输入 state 来源；
- 每轮是否生成可读文本；
- 每轮是否生成最终答案；
- 每轮 KV 的 prompt token 数、generated token 数、past token 数；
- receiver 使用了哪个 sender state；
- baseline answer、每轮 answer、final answer；
- transition：baseline 到 final 的正误变化；
- 对于多源或门控版本，保存门控输入、门控输出和被选 state。

如果方案声称“不广播答案”，记录中必须能复核 sender 在通信阶段没有生成答案文本。

## 当前判断

`MCA-Pre-KV question_only` 目前更像一个有正信号的前置通信原型，而不是已经完成的 MAD 替代方案。

它的直接价值在于：在不广播答案、不广播理由、不进行文本讨论的条件下，question-only KV 能让一轮 receiver majority 相对自身 baseline 提升。它的不足在于：当前结果尚未超过 Standard MAD final，且存在 `BaC_to_W` 伤害样本。

多轮方向的关键实验不是继续和 Standard MAD final 做口头比较，而是构造同口径实验：

```text
Standard MAD
vs
MCA-Pre-KV + Standard MAD
```

如果前置潜状态能提高 Standard MAD final，说明它可以作为现有多智能体讨论的底层增强模块。如果不能，则需要转向多源门控或真正的多轮潜状态交换。
