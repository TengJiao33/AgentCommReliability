# HiddenBench Failure Seeds For State Admission

日期：2026-06-18

## 核心判断

HiddenBench 现在最有价值的用法是提供自然 case seeds，而不是继续追 fact-only prompt 提升。已有 full65 结果里有 `32` 个 case 满足：`full_info` 正确、`oracle_public_facts` 正确、旧 `exchange_then_decide` 错、`fact_only_exchange` 正确。

这组 case 支持一个更具体的下一步：把 HiddenBench 的自然决策任务转写成 `source cards + scope + verification/rejection + evidence slots + downstream decision`，用来构造小而硬的 `Hidden-State Admission v0`。

## 证据

离线抽取产物在：

- `experiments/20260618-local-hiddenbench-failure-seeds/README.md`
- `experiments/20260618-local-hiddenbench-failure-seeds/summary.json`
- `experiments/20260618-local-hiddenbench-failure-seeds/case_cards.jsonl`
- `experiments/20260618-local-hiddenbench-failure-seeds/seed_shortlist.md`

抽取规则：

```text
full_info_correct
+ oracle_public_facts_correct
+ exchange_then_decide_wrong
+ fact_only_exchange_correct
```

汇总结果：

| Signal | Count |
| --- | ---: |
| extracted candidates | 32 |
| recommended v0 seeds | 12 |
| recommendation_leakage | 32/32 |
| shared_overtalk | 22/32 |
| private_fact_not_exact | 31/32 |
| fact_surface_changes_decision | 32/32 |
| shared_prior_preserved | 21/32 |

推荐 seed 包括 `HB03`, `HB05`, `HB10`, `HB11`, `HB12`, `HB21`, `HB27`, `HB31`, `HB44`, `HB51`, `HB54`, `HB56`。

## 机制解释

这组 case 的共同形态很清楚：私有事实在自由文本 public message 里经常被推荐语、共享事实复述、候选答案偏好和改写压扁。最终决策者不缺解题能力，因为 `full_info` 和 `oracle_public_facts` 已经正确；它缺的是一个可靠的 admission surface。

这也解释了为什么 HiddenBench 内继续做 sender prompt 小改动空间有限。fact-only 已经把许多 clean case 拉到 oracle 附近；下一步要看的不是“还能不能让 sender 少说两句”，而是“事实进入公共/角色状态之前，能否被标 source、scope、verification 和 sufficiency”。

## 对新 Benchmark 的影响

`Hidden-State Admission v0` 不应该从零编故事。它可以从这些 HiddenBench case 中抽真实决策结构，然后做小扰动：

- 把每条 private fact 变成 source card。
- 给 source card 增加 recipient scope。
- 给关键 fact 设置 verified、unverified、quarantined 或 rejected 状态。
- 给每个候选答案写 evidence slots。
- 最终输出允许 `insufficient evidence`，而不是强制作答。

最小 v0 可以先从 `HB10`, `HB11`, `HB12`, `HB31` 开始。它们分别覆盖 hazard quarantine、repair/support sufficiency、route exclusion、unverified note/known access path 等不同机制。

## 边界

这不是新模型实验，也不是官方 HiddenBench 分数。它是对已有本地 full65 run 的离线诊断。message audit 标签是启发式，需要人工复核后才能成为 benchmark gold。

`baker_2010` 很有 hidden-profile 味道，但事实面太长，可能适合压力测试，不适合作 v0 的第一批人工 gold。

## 下一步

下一步应做一个 `data/hidden_state_admission_v0/README.md` 和 4-case draft schema。先不要跑模型。先把 `HB10`, `HB11`, `HB12`, `HB31` 各自转成 source cards、scope rules、verification perturbations、evidence slots 和 expected downstream decision。
