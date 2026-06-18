# PerspectiveGap Edge Router Stratified20：结果判断

## 核心判断

这一步把实验从 4-row smoke 推到 stratified20，并且换成了更像 protocol 的设计：模型只选 role-fragment edges，`source_id` 和 `visibility` 由编译器生成。结果说明 compiled scope 能缓解手写 visibility label 的问题，但 hard edge-router prompt 把 edge selection 做差了。

现在我不建议继续沿着“更复杂 hard prompt”扩 full220。更有价值的下一步是把 source perturbation 或 budget 外化成环境约束，让现象从 prompt compliance 变成任务必要性。

## 证据

同一 `40` 行 stratified20 上，旧 role-list 7B projection 是 coverage `0.443`、precision `0.786`、leak `0.050`、budget_pass `0.625`、reject_recall `0.000`。edge-router 7B 变成 coverage `0.331`、precision `0.613`、leak `0.200`、budget_pass `0.575`、reject_recall `0.550`、needed_rejected `1.900`。它学会 reject，但把很多 needed fragment 也 reject 掉。

14B 的趋势更清楚。旧 role-list 14B projection 是 coverage `0.615`、precision `0.808`、leak `0.450`、budget_pass `0.400`。edge-router 14B 是 coverage `0.513`、precision `0.669`、leak `0.600`、budget_pass `0.100`、needed_rejected `1.350`。模型更大后 coverage 高于 7B，但预算和泄漏明显变差。

两个 edge-router run 都是 `40/40` status ok，parse-error rows 都是 `0`。格式失败解释不了这次结果；失败主要来自 edge selection、needed rejection、budget overrun 和 distractor leak。

## 机制解释

compiled scope 把 direct hard-card 里的一个问题拆开了：之前 7B 直接写 visibility 时只有 `0.154` 左右的 visibility accuracy；edge-router 编译后，7B/14B 都到 `0.75` 左右。这说明“让模型手写 scope label”确实是坏接口。

但真正阻塞的是另一层：一旦 prompt 明确强调预算和全局 reject，模型会把 routing 变成保守筛选或激进过发。7B 走保守少发，14B 走更激进过发。这个 tradeoff 比单纯的 visibility label 更值得盯。

## 对 idea 的影响

这次让我更不想继续做“多 agent 通信 prompt 改良”。可保留的现象是：当通信协议同时要求覆盖、边界、预算、reject 时，模型会在这些约束之间错配；模型规模扩大也不会自然解决，只是换一种错法。

这个现象如果要成为 story，需要一个更硬的任务必要性。PerspectiveGap 现在更适合当 routing microscope；下一步要用 source perturbation 或 downstream execution，把错误路由变成可观察的任务损失。

## 下一步

我建议暂停 full220 hard prompt 扩展，直接做一个 source perturbation gate：

1. 固定 role-list edge selection，构造同内容不同 source/scope 的 fragment 对。
2. 让模型必须根据 source/scope 决定收件 role，而不能只靠 fragment 内容语义。
3. 对比 original role-list、edge-router、compiled-scope、oracle 四个条件。

如果这个 gate 里 source/scope 仍然不稳定，我们就有一个更像 paper story 的核心张力：LLM 能读懂内容，但不能把通信状态当作可靠对象来操作。
