# PerspectiveGap Hard-Card Smoke4：结果判断

## 核心判断

这次小跑有价值，但它给出的主要结论是“现在还不能扩”。hard-card surface 能跑通，7B 会复制 source、守预算、少漏 distractor；同时它会保守少发、错 reject needed fragments，并且几乎不会正确理解 recipient-scope visibility。

第一轮还暴露了 prompt contract 歧义。模型把“某个 role 不需要”理解成 global rejected。我修了 prompt 后重跑，歧义缓解了一部分，但 parse 和 visibility 问题仍然在。

## 证据

第一轮 V0 prompt 跑 `4` 行，`strict=0/4`，coverage `0.467`，precision `0.875`，budget_pass `1.000`，source_accuracy `1.000`，visibility_accuracy `0.143`，reject_recall `1.000`，needed_rejected `2.500`。

第二轮 promptv2 明确了三件事：`rejected` 是全局拒绝；visibility 表示 intended recipient scope；同一 fragment 可以分配给多个 role。重跑同样 `4` 行后，`strict=0/4`，coverage `0.433`，precision `0.929`，distractor leakage `0.000`，budget_pass `1.000`，source_accuracy `1.000`，visibility_accuracy `0.154`，reject_recall `0.750`，needed_rejected `1.250`。

同一 `4` 行上，旧 role-list 的 7B legacy projection 是 coverage `0.500`，precision `0.577`，leak `0.250`，budget_pass `0.500`，reject_recall `0.000`。direct hard-card 的优势在边界和预算，代价是 coverage 与 visibility。

## 诊断

这不像单纯格式问题。promptv2 里确实有 `1/4` JSON malformed，但另外 `3` 行的错误也很稳定：模型倾向于把信息少发给 role，用高 precision 和预算合规换掉 recall。它还频繁把 role-private fragment 标成 `shared_all`，说明 visibility label 仍像抽象概念，未变成它能可靠操作的 routing state。

这也解释了为什么原来 `7B precision=0.786` 会让人烦。高 precision 未必代表聪明的 selective communication；它可能只是少发、保守、把复杂 scope 决策让掉。

## 下一步压力

我不建议直接扩 stratified20/full220。下一步应该先做两个小 gate：

1. 结构化输出 gate：用 guided JSON 或更硬的 schema，把 malformed JSON 从行为解释里拿掉。
2. 两阶段 routing gate：先只选 role-fragment edges，再给 selected fragments 标 visibility，看 scope confusion 是否仍存在。

如果这两个 gate 后 visibility 仍崩，才值得上 source perturbation。那时故事会更清楚：模型能读到 fragment 内容，但难以把来源/可见范围变成稳定的通信状态。
