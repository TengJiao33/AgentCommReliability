# CQG 失败模式与进一步机制提炼

日期：2026-07-05

范围说明：本文只对照项目内的 CQG 全量 MATH500 结果与 `reports/2026-07-05-mad-mechanism-improvement-table.md` 进行机制提炼；“不撞”仅表示相对当前本地大表中的方法表述不直接重合，不能替代正式投稿前的扩展文献检索。

## 1. 核心观察

当前 CQG 在 MATH500 全量上的主要数值如下：

| 指标 | 数值 |
|---|---:|
| Initial majority | 320/500 = 0.640 |
| CQG final | 337/500 = 0.674 |
| 相对同 run initial majority | +17/500 = +3.4 pp |
| Quarantined | 189/500 = 0.378 |
| Answer changed | 73/500 = 0.146 |
| MaW -> C | 34 |
| MaC -> W | 17 |
| MaC preservation | 303/320 = 0.947 |
| MaW recovery | 34/180 = 0.189 |

这说明 CQG 的有效部分确实存在，但它并不是“稳定强机制”：

1. 它相对自己的 initial majority 有提升。
2. 它相对 basic MAD final 只高 4/500，涨幅很小，且不是严格同配置配对比较。
3. 它仍低于同模型 direct baseline 和 MAD-MM naive 的当前记录。

因此，后续机制不应被包装成“CQG 已经显著优于 MAD”，而应定位为：CQG 暴露了一个有价值但不稳定的切入点，即 **2:1 分歧中，少数派有时携带正确答案，但当前系统无法分辨“正确少数派”和“诱人的错误少数派”。**

## 2. CQG 的真实增益来源

从转移分解看，CQG 的增益主要不是来自 appeal gate。

在 quarantined 样本中：

| 转移 | 数量 |
|---|---:|
| MaC -> C | 95 |
| MaW -> W | 43 |
| MaW -> C | 34 |
| MaC -> W | 17 |

在 answer changed 样本中：

| 转移 | 数量 |
|---|---:|
| MaW -> C | 34 |
| MaW -> W | 22 |
| MaC -> W | 17 |

进一步看 final 是否来自 initial candidate cards：

| 转移 | final 在 initial cards 中 | final support |
|---|---:|---|
| MaW -> C | 30/34 | 30 个 support=1，4 个 support=0 |
| MaC -> W | 14/17 | 14 个 support=1，3 个 support=0 |
| MaW -> W | 43/43 | support=1 或 2 |
| MaC -> C | 95/95 | support=2 |

这很关键：**CQG 的主要动作是释放 1-vote minority candidate**。这同时贡献了大部分恢复，也贡献了大部分伤害。

因此，CQG 的下一步不是“更积极释放少数派”，也不是“更保守信多数派”，而是要建立一个能区分两类少数派的机制：

- correct minority：少数派的答案违反了多数压力，但携带真实约束。
- seductive wrong minority：少数派推理更像样、解释更完整，诱导 reviewer 推翻正确多数。

## 3. 失败模式

### 3.1 Minority-release ambiguity

相同的结构动作，即“让 blind reviewers 重新评估 minority”，产生了两种相反结果：

- `MaW -> C`：30/34 次最终选择 existing 1-vote minority candidate。
- `MaC -> W`：14/17 次最终也选择 existing 1-vote minority candidate。

这意味着“少数派存在”本身不是足够证据。当前 CQG 没有判断少数派是 informative dissent 还是 noisy dissent 的核心机制。

### 3.2 Appeal validity 不是方向性有效

当前 valid appeal 只是弱文本过滤，不能保证 appeal 真正在支持 challenger。

valid appeal cases 中：

| 转移 | 数量 |
|---|---:|
| MaC -> C | 18 |
| MaW -> W | 7 |
| MaC -> W | 5 |
| MaW -> C | 5 |

也就是说，valid appeal 对净增益几乎没有贡献。更严重的是，有些“valid appeal”实际上在支持 consensus 或批评 alternative answer，却仍被当作有效 appeal。

代表性失败：`test/number_theory/357.json` 中，gold 为 21，initial majority 为 21，minority 为 3，final 变成 3。minority 侧的 appeal 文本实际上包含“21 是正确答案、3 是错误替代”的意思，但系统把它当作 valid appeal，reviewer 最终仍以 2:1 选了 3。

这说明 CQG 需要的不只是 appeal，而是 **directional appeal admissibility**：appeal 必须明确支持自己的 challenger answer，并明确指出 provisional consensus 的具体缺陷。

### 3.3 Blind reviewer 会被漂亮的错误少数派吸引

当前 blind review 的优点是能重新解题，缺点是也会被候选卡片中的推理锚定。

典型恢复：

- `test/counting_and_probability/666.json`：gold 225，initial majority 为 5，minority 为 225，final 选 225。

典型伤害：

- `test/intermediate_algebra/1000.json`：gold 3，initial majority 为 3，minority 为 4，final 选 4。

这两个案例结构相同：2:1 多数，一张 minority card，reviewer 被要求裁决。区别不在流程，而在 minority card 是否携带了真实约束。当前 reviewer 没有被迫验证“候选答案之间到底在哪个可检验条件上分叉”。

### 3.4 Number theory / representation-risk 伤害明显

按主题看：

| 主题 | n | initial correct | final correct | delta | recovery | harm |
|---|---:|---:|---:|---:|---:|---:|
| algebra | 124 | 99 | 108 | +9 | 10 | 1 |
| counting_and_probability | 38 | 16 | 21 | +5 | 6 | 1 |
| geometry | 41 | 25 | 25 | 0 | 1 | 1 |
| intermediate_algebra | 97 | 48 | 49 | +1 | 4 | 3 |
| number_theory | 62 | 44 | 41 | -3 | 3 | 6 |
| prealgebra | 82 | 56 | 62 | +6 | 8 | 2 |
| precalculus | 56 | 32 | 31 | -1 | 2 | 3 |

Number theory 出现了 base notation / subscript-like answer 的风险，例如 `52_8`、`4343_6`。这类错误不一定只是模型推理错，也可能是 evaluator / answer normalization / reviewer 表达格式共同放大的表示风险。

因此，CQG 还需要一个较窄的 answer-representation-risk gate。它不是泛泛的 task routing，而是只针对“答案格式本身容易被归一化或候选卡片误读”的情况，要求保留 raw answer type 和可检验格式。

## 4. 与同行方法大表的避撞判断

当前本地大表中，最容易撞的方向有：

| 已有方向 | 大表编号 | 撞车风险 |
|---|---:|---|
| diversity pruning / misconception refutation | #5 | 若只说“保留/裁剪多样性”会撞 |
| majority vs belief update / conformist | #6 | 若只分析多数压力会偏综述，不够机制 |
| diversity-aware retention | #9 DAR | 若只强调保留 dissent 会撞 |
| process-centric verification | #15 DynaDebate | 若只说动态生成验证路径会撞 |
| confidence / disagreement / task relevance routing | #16/#18/#21/#23/#24/#35 | 若做 confidence gate 或 adaptive routing 会撞 |
| conformal abstain / safe set | #25 | 若做校准概率与 singleton/abstain 会撞 |
| learned minority flip classifier | #29 Minority Sentinel | 若用特征分类器预测是否推翻多数，会强撞 |
| response anonymization | #30 | 若只是匿名候选卡片会撞 |
| evidence-driven / Toulmin / external verifier | #32/#34 | 若只说证据验证或论证结构会撞 |

所以，CQG 的下一步机制应避免以下表述：

1. “训练一个模型判断 minority 是否该翻盘。”
2. “低置信度才 debate。”
3. “多样性保留。”
4. “动态路由到不同 agent。”
5. “匿名化再投票。”
6. “加入 verifier 检查证据。”

这些都太靠近已有表述。

## 5. 建议机制：Disagreement-Conditioned Admissibility Certificate

建议把 CQG 往 **DCAC：Disagreement-Conditioned Admissibility Certificate** 方向推进。

中文可称：**分歧条件准入证书**。

它的核心不是“少数派值得听”，而是：

> 当 2:1 分歧出现时，系统不直接重审完整推理，也不根据置信度或特征预测翻盘；它先从两个候选答案的差异中生成最小可判别条件，要求 challenger 提供方向正确的反多数缺陷声明，再由 reviewer 填写结构化证书。只有当证书显示多数答案违反了某个必要条件、且少数答案通过该条件时，才允许推翻多数。

### 5.1 机制流程

1. Initial agents 独立作答，得到 provisional majority 和 challenger minority。
2. 仅对 2:1 分歧进入 CQG-DCAC。
3. 系统抽取 candidate delta：
   - majority answer raw / normalized form
   - minority answer raw / normalized form
   - answer type：integer、fraction、radical、tuple、base notation、expression、set 等
   - 两个答案的最小差异：数值差、变量差、单位差、边界差、模数/进制差、符号差等
4. Challenger 必须提交 directional defect claim：
   - “我自己的答案为什么仍应存活？”
   - “provisional majority 具体违反了哪一个条件？”
   - 不允许只说“我不确定”或“另一边看起来也合理”。
5. Stance validator 判定 appeal admissibility：
   - `supports_challenger`
   - `supports_consensus`
   - `ambiguous`
   - `placeholder`
   只有 `supports_challenger` 进入下一步。
6. Discriminant generator 根据 candidate delta 生成 1-3 个必要条件检查，而不是生成完整解法。
   - 距离题：检查 squared distance。
   - 计数题：检查是否遗漏独立选择因子。
   - 整除题：检查 divisibility / maximality / residue。
   - 极值题：检查边界、导数、判别式或可行域。
   - base notation：检查 raw base semantics，而不是把 subscript 误读为普通整数。
7. Reviewer 不再自由投票，而是填写 certificate ledger：
   - condition
   - majority pass/fail/unknown
   - minority pass/fail/unknown
   - minimal calculation
8. 决策规则：
   - 若 minority 通过至少一个 discriminant，且 majority 在同一 discriminant 上失败，允许 flip。
   - 若只有 unknown 或双方都通过，保留 majority。
   - 若 answer type 属于 representation-risk，要求 raw-format preserving verification；否则 abstain/no-change。

### 5.2 它和现有方法的差异

DCAC 和本地大表中的相近方向区别如下：

| 相近方法 | 差异点 |
|---|---|
| Minority Sentinel (#29) | DCAC 不训练 flip classifier，不使用 fingerprint features，不输出 learned threshold；它用 candidate-delta 生成的必要条件证书来决定是否准入翻盘。 |
| DAR / diversity retention (#9) | DCAC 不以“保留 dissent”为核心；dissent 只是触发器，真正核心是 dissent 必须产出可判别缺陷。 |
| Confidence protocols (#23/#24/#35) | DCAC 不依赖 self-confidence 或 calibrated confidence。 |
| Dynamic routing / topology (#16/#18/#21/#26) | DCAC 是固定的局部准入协议，不改变 agent topology。 |
| Response anonymization (#30) | 匿名可以作为 hygiene，但不是核心贡献；核心是证书化的 answer-delta 检查。 |
| Evidence/Toulmin verifier (#32/#34) | DCAC 不要求完整论证证据链，也不做外部 evidence scoring；它只检查由候选答案差异诱导的最小必要条件。 |
| Conformal social choice (#25) | DCAC 不做概率校准、singleton set 或 conformal abstain；它是确定性的结构证书。 |

相对来说，这个机制的“新意支点”更窄也更清楚：**不是让 agent 更会辩论，而是把 2:1 分歧转化成候选答案之间的最小可判别测试。**

## 6. 为什么它能修 CQG 的主要问题

### 6.1 修复 minority-release ambiguity

当前 CQG 的恢复和伤害都来自释放 minority。DCAC 不阻止 minority 被听见，但要求 minority 先证明它不是单纯的 alternative rationale，而是能指出 majority 的某个必要条件失败。

这会把问题从：

> minority 是否说得更有道理？

改成：

> majority 和 minority 在哪个可检验条件上分叉？谁通过了这个条件？

### 6.2 修复 appeal stance invalidity

对 `test/number_theory/357.json` 这类 case，directional validator 会把“实际支持 consensus 的 appeal”判成 `supports_consensus`，不允许它作为 challenger appeal 触发翻盘。

这不是简单加强文本过滤，而是要求 appeal 的语义方向与候选答案一致。

### 6.3 降低 polished wrong minority 的诱导

Reviewer 不再直接读完整 candidate rationale 后投票，而是先执行 candidate-delta 诱导的必要检查。这样可以减少“错的 minority 解释更流畅”造成的锚定。

### 6.4 保留 CQG 的有效部分

不能简单要求“有 valid appeal 才 flip”，因为当前 34 个恢复里只有 5 个 valid appeal；这样会把 CQG 的实际收益砍掉。

DCAC 更适合做的是：把原本不稳定的 blind re-solve 恢复，改造成 discriminant certificate 恢复。也就是说，它不是取消 blind reviewer，而是改变 reviewer 的任务形态。

## 7. 可作为 ablation 的次级机制

### 7.1 Directional Appeal Admissibility

独立实现最简单：

1. 对每个 appeal 标注 stance。
2. 若 appeal 不支持 challenger，则不允许 challenger 翻盘。
3. 观察是否减少 `MaC -> W`。

风险：如果单独使用，它可能同时减少 recoveries，因为当前许多 recoveries 没有 valid appeal。因此它更适合作为 DCAC 的第一层，而不是最终机制。

### 7.2 Answer-Representation-Risk Gate

针对以下答案类型触发：

- base notation / subscript-like answer
- tuple / set / interval
- expression with variable binding
- units or modulo
- multiple equivalent raw forms

触发后：

1. 保留 raw answer string。
2. reviewer 必须解释答案格式。
3. 不允许 normalized scalar alone 决定翻盘。

这个机制很窄，但能直接解释 number theory 中的部分伤害。它可作为 DCAC 的安全子模块，而不是主贡献。

### 7.3 Contrastive Independence Review

把 reviewer 分成固定三类：

1. blind solver：只看题目，不看 candidate cards。
2. card auditor：只检查 candidate cards 中的关键步骤。
3. discriminant verifier：只填 certificate ledger。

最终不是多数投票，而是以 discriminant verifier 的证书作为是否允许 flip 的准入条件。

注意：这个方向容易和 role assignment / debate role 方法擦边，所以如果使用，应把它作为 DCAC 的实现细节，不作为论文主机制。

## 8. 推荐的下一版实验定义

最值得先做的是 **CQG-DCAC v0**，不要一开始做复杂学习器。

最小可运行版本：

1. 仅处理 2:1 divergent cases。
2. 用 prompt 生成 candidate delta 和 1 个 discriminant condition。
3. 用 stance validator 过滤 appeal。
4. reviewer 填写结构化 certificate。
5. 决策规则保守：
   - minority pass + majority fail：flip。
   - 其他情况：keep majority。
6. representation-risk case 默认 keep majority，除非 certificate 明确处理 raw format。

建议比较：

| 方法 | 目的 |
|---|---|
| Initial majority | 判断所有机制真实增益 |
| 当前 CQG divergent | 当前上限/下限混合体 |
| CQG + stance admissibility only | 测 stance 是否减少明显坏翻盘 |
| CQG + discriminant certificate only | 测 certificate 是否保留恢复 |
| CQG-DCAC | 测组合是否同时减少 harm 与保留 recovery |

核心指标不只看 final accuracy，还应报告：

- `MaW -> C`
- `MaC -> W`
- recovery/harm ratio
- flip precision = `MaW -> C / (MaW -> C + MaC -> W)`
- subject-wise delta
- representation-risk subset delta
- no-change rate

## 9. 一句话机制表述

如果要把机制压缩成论文里的核心 claim，可以写成：

> CQG-DCAC treats disagreement not as a signal to debate harder, but as a generator of candidate-specific admissibility tests: a minority answer may overturn a majority only after it produces a directionally valid defect claim and passes a discriminant certificate derived from the answer delta.

中文对应：

> CQG-DCAC 不把分歧当作“继续辩论”的信号，而把分歧转化为候选答案之间的最小可判别测试；少数派只有在提出方向正确的多数缺陷声明，并通过由答案差异诱导的证书检查后，才被允许推翻多数。

这个机制相对当前大表的优势是：它不依赖置信度、不训练少数派翻盘分类器、不做动态路由、不只是匿名化或保留多样性，也不是泛泛的 verifier；它抓住的是 CQG 实验暴露出的一个更细的失败结构：**错误恢复和错误翻盘共享同一个 minority-release 通道，必须用 answer-delta certificate 将两者拆开。**
