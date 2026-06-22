# PG40 SSEAC-v0 五行重跑解释

日期：2026-06-19

## 核心判断

这次 PG40 五行重跑给出了行为结果，但它是诊断证据。模型输出结构稳定，执行器能把预算修到合法；真正的问题是候选单元太粗，预算剪裁会连带删掉必要证据。

## 原本想回答什么

这次运行想回答：true SSEAC prompt 能否在 PG40 tight-budget 上形成一条可进入主表的方法行。主对照是 `structured_no_compiler` 与 `compiled` 的成对差。

## 实际发生了什么

运行编号是 `20260619-a8002-sseac-v0-pg40-limit5-gpu7-rerun-qwen25-14b`，使用 A800_2 的 GPU 7，Qwen2.5-14B，五行全部完成。

聚合结果：

| 条件 | Strict | Coverage | Precision | Budget pass | Utility |
| --- | ---: | ---: | ---: | ---: | ---: |
| structured no compiler | 0/5 | 0.7778 | 0.6562 | 0.0000 | 0.1803 |
| compiler | 0/5 | 0.3704 | 0.8333 | 1.0000 | 0.4635 |

成对差显示，compiler 把 budget pass 从 `0.0000` 提到 `1.0000`，utility 均值增加 `0.3412`，但 coverage 均值下降 `0.3714`，strict 仍为 `0/5`。

## 为什么它没有成为主表结果

PG40 的强透明基线是 `utility_density_greedy`：`25/40` strict，utility `0.9825`。当前五行 true prompt 的 compiled utility 只有 `0.4635`，strict 仍是 `0/5`。它离主表方法优势很远。

更关键的是失败形态很集中。模型会把多个卡片合成一个 candidate unit，例如把 dispatcher 需要的多张高成本卡绑在一起。executor 看到整组超预算后拒绝整组，导致本来可保留的必要卡也丢失。`pg_003__seed_1` 中三个 unit 都因为 over-budget 被拒绝，最终三个角色的必要证据全缺。

## 可以保留的东西

第一，schema 稳定性可以保留。五行都有可解析输出，compiler `ok_rows=5`。

第二，hard executor 价值可以保留。它确实把预算从崩溃修到合法，并且没有 distractor leak。

第三，问题定位可以保留。PG40 的当前断点是 unit construction 和 priority，而非 parser、远程服务或基础 compiler。

## 对论文故事的影响

PG40 暂时不能承担方法主证据。它更适合继续作为强压力尺子：任何方法行都要在这里证明自己不会只靠多塞候选、再让执行器粗暴删掉。

这次结果反而让 HSA 的意义更清楚。HSA 当前展示的是“证据不足时阻止错误承诺”；PG40 展示的是“预算合法性可以修，但候选证据构造仍会塌”。两者合起来，论文问题应更聚焦在证据准入的两个阶段：候选证据生成和硬准入执行。

## 下一步压力测试

下一步不扩 PG40 full40。先改五行上的 contract：

1. 一个 candidate unit 默认只允许一个 card。
2. 每个 role 必须输出预算内排序，而非全局混排。
3. 多卡 unit 必须声明依赖关系，且超预算时允许降级拆分。
4. 用同一五行复跑，目标是保持 budget pass `1.0`，同时把 coverage 拉回到接近编译前。

如果这五行仍然 strict `0/5` 且 coverage 低，PG40 路线应转为失败分析和强基线压力，不再作为近期主方法路线。

