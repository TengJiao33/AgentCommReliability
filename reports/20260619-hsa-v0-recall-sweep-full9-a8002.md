# HSA-v0 recall_sweep 九行结果

日期：2026-06-19

## 核心判断

`recall_sweep` 是 HSA 目前最有价值的一次正向推进。它把 compiler strict 从 `7/9` 提到 `8/9`，base strict 从 `1/3` 提到 `2/3`，perturbation strict 继续保持 `6/6`。但它也把 extra final cards 从 `8` 推到 `19`，所以它是“召回增强成功、准入精度变差”的诊断结果。

## 原本想回答什么

上一轮 HSA full9 的问题很具体：两个 base 行模型答案正确，但候选证据少提必需卡，compiler 按充分性规则退回证据不足。本次只改提示契约，让模型先做每个候选答案的支持、阻断、背景约束扫描，再输出单卡候选单元。

## 实际发生了什么

运行编号是 `20260619-a8002-hsa-v0-recall-sweep-full9-qwen25-14b`，使用 A800_2 的 GPU 7、Qwen2.5-14B，9 行全部完成，解析失败为 0。

| 条件 | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline model_only | 3/9 | 0.6667 | 0.1667 | 0.8148 | 8 | 0.5556 |
| baseline compiler | 7/9 | 0.3333 | 1.0000 | 0.7130 | 8 | 0.7778 |
| recall_sweep model_only | 5/9 | 0.6667 | 0.5000 | 0.9259 | 19 | 0.0000 |
| recall_sweep compiler | 8/9 | 0.6667 | 1.0000 | 0.7963 | 19 | 0.3333 |

最重要的行级变化是 `hiddenbench_conference_relocation` 的 base 行被修好：上一轮漏掉 `hb11_shared_3`，这次召回后通过。唯一仍失败的是 `hiddenbench_evacuation_west_city` 的 base 行：模型召回了 `hb01_hidden_2`，但漏掉 `hb01_shared_3`，并把 West City 判成 blocked。

## 为什么重要

这次结果说明 HSA 的瓶颈主要落在候选证据是否被模型提全。只要把证据扫描显式化，base 行立刻从 `1/3` 到 `2/3`，同时扰动行的防错能力没有丢。

这对方法故事有帮助：SSEAC 的核心可以写成“模型负责语义召回，硬规则负责合法准入”。这次 run 同时展示了两边都需要：召回契约给了更多候选，compiler 又挡住了范围越界和无效证据。

## 为什么还不能当主结果

过度准入变重是最大风险。extra final cards 从 `8` 增加到 `19`，已经接近 all-scoped control 的 `24`。如果只看 strict，`8/9` 会显得漂亮；但 evidence discipline 指标会提醒我们：这条路可能靠“多收卡”换分。

唯一失败行也暴露了新的机制问题。模型把阻断卡归属到错误选项上，导致 West City 被错误判成 blocked。这说明下一步不能继续单纯扩大召回，而要做 focused recall：只收所选答案的支持卡、其他答案的阻断卡和必要背景约束，普通支持卡不要全塞进 final_decider。

## 对论文故事的影响

HSA 现在比 PG40 更像近期可推进主线。PG40 目前被强透明基线压住，role-plan 负结果也说明解释型提示收益有限；HSA 则出现了可解释的成对提升：`7/9 -> 8/9`，且 perturbation 仍为 `6/6`。

但 HSA 仍是诊断证据。它的表述应是：召回契约和硬准入组合能改善小型 HiddenBench-derived admission packet，并暴露召回-精度权衡。它还不能写成已完成的 A 会方法结果。

## 下一步压力测试

下一步做 `focused_recall`，同样只跑 full9。成功门槛应更严：

| 指标 | 目标 |
| --- | --- |
| strict | 保持或超过 `8/9` |
| base strict | 至少 `2/3`，最好 `3/3` |
| perturb strict | 保持 `6/6` |
| extra final cards | 从 `19` 明显降下来，目标接近 `8` |
| slot recall | 不低于 `0.7963` |

如果 focused recall 不能降 extra final cards，这条线就需要转向排序器或后置过滤，继续改提示的收益会很低。
