# HSA-v0 focused / constraint 复跑结果

日期：2026-06-19

## 核心判断

HSA 当前最好的诊断行是 `constraint_recall compiler`：strict `8/9`，base strict `2/3`，perturbation strict `6/6`，extra final cards `10`。它没有突破到 `9/9`，但相比 `recall_sweep` 的 `8/9`、extra `19`，它把过度准入明显压低了。

## 原本想回答什么

`recall_sweep` 证明扩大证据扫描能提升 strict，但 extra final cards 太高。`focused_recall` 和 `constraint_recall` 要回答的是：能不能保留 `8/9` 的严格正确，同时减少被拒答案的普通支持卡进入 final_decider admitted state。

## 实际发生了什么

| 条件 | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline compiler | 7/9 | 0.3333 | 1.0000 | 0.7130 | 8 | 0.7778 |
| recall_sweep compiler | 8/9 | 0.6667 | 1.0000 | 0.7963 | 19 | 0.3333 |
| focused_recall compiler | 8/9 | 0.6667 | 1.0000 | 0.8148 | 12 | 0.5556 |
| constraint_recall compiler | 8/9 | 0.6667 | 1.0000 | 0.7963 | 10 | 0.5556 |

`focused_recall` 和 `constraint_recall` 都保住了 `8/9`，也都保持了扰动行 `6/6`。区别在于 extra final cards：`focused_recall` 是 `12`，`constraint_recall` 是 `10`。

## 为什么重要

这说明 HSA 的召回-精度权衡可以被压缩。`recall_sweep` 的问题是“多收”；`focused_recall` 和 `constraint_recall` 能把多收卡片降下来，同时不丢掉硬准入的防错能力。

这个结果比 PG40 更适合近期承接方法故事。PG40 还被强透明基线压住；HSA 至少已经出现了一个可解释的 pipeline 增量：model-only `5/9`，compiler `8/9`，并且过度准入比 all-scoped 的 `24` 低很多。

## 仍然失败在哪里

唯一没有解决的是 `hiddenbench_evacuation_west_city` base。`constraint_recall` 已经保留 `hb01_shared_3`，但仍漏掉 `hb01_hidden_2`。这张卡的语义很尴尬：它是 verified constraint，但模型不稳定地把它视为 final decision 必需证据。

这暴露出下一层瓶颈：提示很难稳定判断哪些间接约束卡需要进入 final_decider admitted state。继续堆自然语言提示可能收益变低，候选补全器或后置过滤器更值得考虑。

## 对论文故事的影响

HSA 现在可以写成“诊断性主线候选”：它展示了模型 proposal 和 compiler execution 的分工，也展示了 evidence discipline 指标的必要性。当前仍不能写成完整方法胜利，因为样本只有 9 行，而且 all-scoped 是 `9/9`。

更稳的表述是：SSEAC 在 HSA-v0 上把模型输出的候选证据转成更可靠的 admitted state；`constraint_recall` 达到 `8/9`，同时 extra final cards `10` 低于 all-scoped `24`。剩余错误来自间接约束卡召回。

## 下一步压力测试

下一步如果继续 HSA，应停止追加提示词层数，改做更可审计的候选补全或后置过滤：

| 方向 | 目的 |
| --- | --- |
| 约束卡补全器 | 自动补入 verified、final_decider-visible、低成本 constraint/background cards |
| 支持卡过滤器 | 去掉被拒答案的普通支持卡，保留阻断卡 |
| 同 9 行复跑 | 目标 strict `9/9` 或保持 `8/9` 且 extra final cards 接近 baseline 的 `8` |

如果补全器仍停在 `8/9`，HSA 可作为强诊断表；若到 `9/9` 且 extra 不高，就可以考虑扩 HiddenBench seed shortlist。

