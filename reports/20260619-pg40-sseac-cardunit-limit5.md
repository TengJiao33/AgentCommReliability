# PG40 单卡候选契约复跑解释

日期：2026-06-19

## 核心判断

单卡候选契约有效，但还不够强。它把 PG40 五行 compiled strict 从 `0/5` 提到 `1/5`，utility 从 `0.4635` 提到 `0.8155`，coverage 从 `0.3704` 提到 `0.6667`，同时 budget pass 保持 `1.0000`。

## 原本想回答什么

上一轮 true SSEAC prompt 的主要失败是多卡 candidate unit 被 over-budget 整组拒绝，必要证据随之丢失。这次只改提示词，要求一个 unit 只含一个 card，并按 role 分别排序。它要回答：失败是否主要来自 unit 粒度。

## 实际发生了什么

运行编号是 `20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b`，使用 A800_2 的 GPU 7，Qwen2.5-14B，五行全部完成。

| 条件 | Strict | Coverage | Precision | Budget pass | Utility |
| --- | ---: | ---: | ---: | ---: | ---: |
| 上轮 compiled | 0/5 | 0.3704 | 0.8333 | 1.0000 | 0.4635 |
| 单卡 compiled | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.8155 |

成对差也更好：utility 均值提升 `0.6118`，exact role 均值提升 `0.3667`，strict 出现 1 个正例。

## 为什么重要

这说明 PG40 上的方法失败不是纯粹来自 compiler 过于保守。候选对象的粒度本身会决定 hard executor 是否有可裁剪空间。多卡 unit 把有用证据和超预算证据绑在一起；单卡 unit 给了 executor 更细的选择单位。

这个结果让机制故事更具体：SSEAC 不能只说“模型提议，规则执行”。它还必须规定模型提议对象的粒度，否则规则执行会把坏候选放大成 coverage 损失。

## 为什么还不能当主结果

单卡契约仍然只有 `1/5` strict。它的 utility `0.8155` 低于旧 source-ledger 14B compiled 的 `0.8707`，也明显低于 utility-density greedy 的 `0.9825`。因此 PG40 还不能作为方法优势表。

剩余错误集中在 role-specific semantic ranking。模型能避免 distractor leak，也能输出可裁剪单元，但它仍会把高成本或语义相近的卡放错角色，或者漏掉 shared setup card。

## 下一步压力

后续更新：这个方向已经在 `20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b` 中复跑。role-plan compiled 仍是 `1/5`，utility 降到 `0.7811`，低于本报告的单卡契约 `0.8155`。

因此 PG40 当前停在强压力表和失败分析位置，不承担近期主方法结果。后续若重启 PG40，应换成预算感知重排或成对排序器，而不是继续加解释型提示。
