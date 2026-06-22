# HSA-v0 约束卡补全后置诊断

日期：2026-06-19

## 核心判断

HSA 当前最明确的推进是：剩余的 `8/9 -> 9/9` 缺口可以由一个可审计后置规则补上。规则只补入预测时可见、已验证、面向最终决策者的阻断卡；在同一份 `constraint_recall` 模型输出上，compiler 从 `8/9` 到 `9/9`，extra final cards 保持 `10`。

这个结果提高了 HSA 作为机制切口的可信度，但仍然是诊断证据。它证明了漏卡类型可以被规则化处理，还需要更大 seed shortlist 证明规则不会泛化成过度收卡。

## 实验设计

输入固定为 `20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b` 的原始预测。新增脚本 `scripts/augment_hsa_predictions.py` 只看 packet 中预测时可见的 `source_cards` 字段：`card_id`、来源、范围、验证状态、证据类型、成本和内容。它不读取 `required_slots`、`expected_final_decision` 或评测义务字段。

补全策略为 `visible_verified_blocker_completion`：如果某张卡是 `blocker`、状态为 `verified`、且 `recipient_scope` 包含 `final_decider`，同时它尚未出现在最终决策者候选单元中，就追加一个低一档优先级的单卡候选单元。预算、范围和验证约束仍由原 SSEAC 编译器执行。

## 结果

补全器只增加了 2 个候选单元，且都指向同一张卡 `hb01_hidden_2`：一个在西城基础行，一个在西城桥梁未验证扰动行。没有解析错误。

| 条件 | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| constraint_recall compiler | `8/9` | `0.6667` | `1.0000` | `0.7963` | `10` | `0.5556` |
| completion compiler | `9/9` | `1.0000` | `1.0000` | `0.8333` | `10` | `0.4444` |

成对比较里，增强后的 model-only 仍是 `5/9`，compiler 是 `9/9`。strict 平均提升 `+0.4444`，extra final cards 平均不变。forced commitment detected 上升表示编译器在证据不足行中挡住了模型具体承诺，属于防错读数。

## 机制解释

这次结果把 HSA 的失败点压得更窄了。`constraint_recall` 已经能让模型找到大多数支持、阻断和背景约束，但它仍会漏掉“不直接命名目标选项”的阻断卡。后置补全规则利用了一个更稳定的结构信号：卡片已经被标成 verified blocker，且对最终决策者可见。

因此，当前机制更像“模型生成候选 + 可审计结构补漏 + 硬准入执行”。这比继续写更长自然语言提示更可控，也更接近可论文复现的系统部件。

## 边界

这个结果还不能写成主表结论。第一，HSA 只有 9 行；第二，后置规则是在已有模型输出上运行；第三，规则目前只验证了可见阻断卡，不覆盖背景约束卡和支持卡漏召回。它最适合作为下一轮扩 seed 的 launch gate。

## 下一步压力

下一步应构造 HiddenBench seed shortlist 上的补全压力测试。成功信号是：completion compiler 继续保持高 strict，extra final cards 不向 all-scoped 的 `24` 靠近；失败信号是：规则在新行里大量加入不必要 blocker，或在证据不足行中把错误选项启用。

当前最该停住的是继续堆提示词。更有价值的推进是把补全规则写成明确可审计模块，并在更多行上观察 precision、extra cards 和 insufficient-evidence 稳定性。
