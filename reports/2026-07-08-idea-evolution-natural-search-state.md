# Idea 演化记录：从显式讨论到自然搜索状态通信

日期：2026-07-08

## 一句话版本

这次 idea 的演化不是“让智能体写计划互相看”，而是逐步意识到：真正想验证的是 **自然解题过程中无意识产生的中间搜索状态，是否能作为低强度、非文本、可忽略的启发信号传给同题同伴**。

因此，最新实现从 `Pre-KV continuation` 转向了：

```text
普通解题轨迹 -> 捕获中间层状态变化量 -> 同题/错题/随机强对照 -> 低强度注入
```

## 阶段一：标准多智能体讨论是稳定基线

代表实验：

```text
experiments/standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/
```

结果：

```text
初始多数：364/500 = 0.728
最终讨论：378/500 = 0.756
```

含义：

```text
显式文本讨论确实有用；
但它混合了答案、理由、说服、纠错、投票等因素；
无法回答“中间搜索状态本身是否有信号”。
```

这给后续潜状态通信提供了目标：不要只复刻文本讨论，而要找更早、更细、更少主观干预的通信对象。

## 阶段二：候选池守门能保护一部分，但不是核心 idea

代表实验：

```text
experiments/cpac-dcac-guard-v1-math500-20260706-standard-fixed-qwen25-7b-full-4096-a8002/
```

结果：

```text
初始多数：364/500
守门后：368/500
```

含义：

```text
候选池、证书、保守守门能减少部分错误翻案；
但它仍然发生在答案已经出现之后；
它不是“中间搜索状态通信”。
```

这条线适合做可靠性保护层，不适合作为这次 idea 的主机制。

## 阶段三：文字线索失败，暴露自然语言通道的污染

代表报告：

```text
reports/2026-07-06-mca-t-failure-triage.md
```

结果：

```text
初始：364/500
文字线索后：357/500
```

主要问题：

```text
模型会把线索当成可自证的理由；
错误线索容易被包装成高置信答案；
文本通道太容易携带立场、答案和伪证明。
```

这推动我们转向非文本或弱文本的中间状态。

## 阶段四：Question-only KV 说明缓存能跑，但不是搜索信号

代表实验：

```text
experiments/20260706-a8002-math500-mca-pre-kv-question-only-standard-qwen25-7b-full/
experiments/20260706-a8002-math500-live-mca-pre-kv-then-mad-qwen25-7b-full/
```

同口径结果：

```text
无通信第一轮：347/500
Question-only Pre-KV 第一轮：349/500
净 +2
```

含义：

```text
KV 通道本身能影响接收方；
但 question-only 主要传的是题目阅读状态，不是解题搜索状态；
它不能证明“中间搜索信号”存在。
```

这一步的价值是工程打底，不是机制证明。

## 阶段五：Early-plan Pre-KV 看到局部信号，也看到强污染

代表报告：

```text
reports/2026-07-07-early-plan-pre-kv-case-audit.md
```

观察：

```text
有 BaW_to_C：相位平移、共轭根式、函数方程等题被救回；
也有 BaC_to_W：年金、计数、等比数列、几何等题被半截轨迹锚定。
```

这一步非常关键，因为它第一次说明：

```text
中间状态里可能确实有搜索方向；
但当前传法把搜索方向、半截文本、位置错位、发送方身份和局部错误混在一起。
```

因此，结论不是 idea 错，而是 Pre-KV 接续式实现不干净。

## 阶段六：Micro-commitment 被用户指出“不纯粹”

代表报告：

```text
reports/2026-07-07-hybrid-micro-gated-failure-audit.md
```

问题：

```text
要求发送方写 REPRESENTATION / FIRST_MOVE / CHECK；
这已经是主动计划生成；
64 tokens 经常截断；
接收方看到半截结构化文本，KV 也停在半截 assistant completion 里。
```

用户指出得很关键：

```text
不能要求发送方生成完整短计划；
这会主动干预发送方；
会破坏 idea 的纯粹性。
```

所以这一阶段之后，“计划”这个词被降级，不再作为主概念。

更准确的新概念是：

```text
自然中间状态
无意识搜索状态
搜索状态变化量
```

## 阶段七：Latent rounds 更接近，但仍依赖文字化私有思考

代表代码：

```text
scripts/run_mca_latent_rounds.py
```

代表报告：

```text
reports/2026-07-07-mca-latent-rounds-design.md
reports/2026-07-08-mca-latent-safe-variants-results.md
```

优点：

```text
不展示同伴文本；
默认最终答案阶段不注入 peer vector；
有范数裁剪、低强度注入、匹配种子。
```

结果大致是：

```text
小样本 +1/-1 附近；
没有形成稳定收益。
```

核心缺陷：

```text
它先让模型写 private thought；
再把 private thought 重新编码成一个向量；
这仍然不是纯自然 decode 轨迹里的无意识状态。
```

所以它比 Pre-KV 干净，但仍不是最终想要的实验对象。

## 阶段八：文献阅读把方向收窄

代表报告：

```text
reports/2026-07-08-latent-comm-literature-notes.md
```

关键启发：

```text
KVComm 说明缓存有效，但要选择性共享，不应前缀接续；
State Delta 说明状态变化量可能比绝对隐藏状态更稳；
Cross-context KV 说明位置错位是大问题；
Coconut 提醒训练免潜状态注入不能期待大幅稳定收益；
CIPHER 提醒软信念和非采样状态也可能有用。
```

因此下一步不应继续：

```text
显式计划；
固定前 64 tokens；
raw Pre-KV continuation；
最终阶段强注入。
```

而应转向：

```text
自然生成；
同步截点；
状态变化量；
强对照；
少层低强度。
```

## 阶段九：工程审计明确当前实现哪里不支持 idea

代表报告：

```text
reports/2026-07-08-natural-search-state-engineering-audit.md
```

明确问题：

```text
Pre-KV 是续写别人，不是旁路参考；
early_plan 和 micro-commitment 主动改变发送方；
question-only KV 不是搜索状态；
latent_rounds 仍依赖文字化 private thought；
第 16 层默认依据不足；
缺少同题、错题、随机、绝对状态等强对照。
```

这份审计把“为什么之前实验不够支持 idea”落到了代码路径上。

## 阶段十：当前落源码版本

新增代码：

```text
scripts/run_mca_natural_search_delta.py
tests/test_mca_natural_search_delta.py
experiments/20260708-a8002-mca-natural-search-delta-qwen25-7b/
```

当前协议：

```text
发送方正常解题；
使用普通 cot_prompt；
不要求写计划；
不展示同伴文本；
不使用 peer past_key_values；
在第 22 层、第 16/32/64/96 个 decode 步捕获自然状态；
主通信对象是 h_t - h_{t-1}；
对照包括同题 delta、错题 delta、随机同范数、高题绝对状态。
```

远端首跑：

```text
run_id = 20260708-a8002-mca-natural-search-delta-disagreement50-qwen25-7b
machine = A800_2
gpu = 7
split = mca_disagreement_v1
limit = 50
```

日志：

```text
/data/xuhaoming/yfy/research_workspace/logs/20260708-natural-search-delta-gpu7.nohup.log
```

## 当前判断

现在最谨慎的判断是：

```text
idea 还没被证明；
但已有案例显示中间状态里可能有搜索信号；
之前失败更多来自通信对象不纯和融合方式过强；
最新实验第一次比较接近原始问题本身。
```

如果最新实验显示：

```text
同题 delta > 错题 delta；
同题 delta > 随机同范数；
delta > 绝对状态；
BaW_to_C 增加而 BaC_to_W 不同步增加；
```

那么这个 idea 才开始有真正的工程证据。

如果最新实验显示：

```text
同题 delta 和随机差不多；
错题 delta 也能同样改变答案；
绝对状态和 delta 差不多；
救回和伤害同时上升；
```

那就说明当前训练免潜状态通信不支持这个 idea，至少不能作为主线继续扩大。

## 相关文档索引

```text
reports/2026-07-06-mca-t-failure-triage.md
reports/2026-07-07-early-plan-pre-kv-case-audit.md
reports/2026-07-07-hybrid-micro-gated-failure-audit.md
reports/2026-07-07-mca-latent-rounds-design.md
reports/2026-07-08-mca-latent-safe-variants-results.md
reports/2026-07-08-latent-comm-literature-notes.md
reports/2026-07-08-natural-search-state-engineering-audit.md
scripts/run_mca_natural_search_delta.py
```
