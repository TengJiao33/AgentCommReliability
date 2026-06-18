# TypeCastArena repaired control-stable packet

## 核心判断

这个 packet 现在更像一个可以上 GPU 的窄诊断切片，而不是新的行为证据。它修复了上一轮 `315` 行 receiver run 暴露出的主要问题：baseline/self/unrelated 控制太不稳定，导致 inert、quarantine、typed 和 admitted/verifier 之间无法解释。

## 我们做了什么

我从 `20260617-0033-a8002-typecast-math200-inert-receiver315-qwen25-14b` 的评估结果中筛出 `13` 个 control-stable case：这些 case 在 `baseline_previous_solution`、`control_self_revision_no_sender`、`control_unrelated_sender_message` 三个条件下都语义正确。基于它们重建了 `117` 行 receiver packet，每个 future signal 各 `13` 行，并把 final-answer 输出契约改成更强的 mandatory final line。

关键文件：

- `experiments/20260617-local-typecast-arena-math200-repaired-controlstable-receiver-packet/typecast_math_receiver_packet.jsonl`
- `experiments/20260617-local-typecast-arena-math200-repaired-controlstable-receiver-packet/summary.json`
- `scripts/build_typecast_receiver_repair_packet.py`
- `scripts/analyze_typecast_boundary_obedience.py`

## 本地门禁结果

本地结构检查通过：packet 有 `117` 行、`117` 个唯一 packet id，每个 future signal 各 `13` 行，所有 prompts 都包含新的 strict final-answer contract，且不再包含旧的尾部输出指令。

Gold-smoke 也通过：用 `{final answer: <gold>}` 走同一个 evaluator 后，结果是 `117/117` semantic correct、`0` semantic wrong、`0` semantic unknown。Boundary-obedience gold-smoke 进一步给出 `0/117` concern cards，说明分析器在金标输出上不会制造误报队列。

## 为什么重要

上一轮 `315` 行 run 的结论是控制门失败，不是 lifecycle 正信号：baseline 只有 `16/35` 正确，inert、unrelated、quarantine、typed 的失败率和 admitted/verifier 接近。这个 repaired packet 把问题压窄到一个更可解释的条件：如果模型在 baseline/self/unrelated 已经稳定的 case 上，仍然只在 admitted/verifier 或 direct peer 中表现出明显边界违背，而 inert/quarantine/typed 保持干净，才有资格继续讨论 communication lifecycle。

## 还不能说什么

不能把这个 packet 本身当成模型行为证据。它是从同一个 Qwen2.5-14B `315` 行失败 run 中后验筛出来的 `13` 个 case，样本更小，也可能偏向该模型容易稳定回答的题型。因此它适合作为下一次小心 GPU run 的门票，不适合作为总体率估计或论文主张。

## 下一步压力

下一步不应该马上扩大规模。合理的 GPU 门禁是：只用一张 A800，跑这 `117` 行，要求 baseline/self/unrelated 继续干净；然后同时看 MATH evaluator 和 boundary-obedience cards。如果 inert、quarantine、typed 仍然和 admitted/verifier 一样坏，就把它继续记为控制失败；只有 target channels 和 controls 明显分离，才进入人工卡片审计和机制解释。
