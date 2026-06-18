# PerspectiveGap Hard Routing V0：下一步尝试

## 结论

我先做了一个不耗 GPU 的 benchmark 加压原型。它把 PerspectiveGap 从 `role -> fragment list` 升级成 state-card routing：每个角色要给 `fragment_id/source_id/visibility`，还要服从预算，并显式 reject distractors。

这一步还没有产生新模型行为证据；价值在于给后续模型 run 一把更硬的尺子。它已经把原来一个 precision/coverage 读数拆成 coverage、precision、budget、reject、leak 几个压力点。

## 关键读数

| 条件 | strict | coverage | precision | leak/eval | budget_pass | overrun | reject_recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| oracle | 220/220 | 1.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 |
| all_to_all | 0/220 | 1.000 | 0.318 | 3.800 | 0.000 | 128.464 | 0.000 |
| no_distractor_all_to_all | 0/220 | 1.000 | 0.350 | 0.000 | 0.000 | 117.064 | 1.000 |
| shared_only | 0/220 | 0.031 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 |
| budget_cheapest | 0/220 | 0.577 | 0.419 | 2.845 | 1.000 | 0.000 | 0.000 |

`shared_only` 的 precision 是 `1.000`，但 coverage 只有 `0.031`，平均每个 evaluation 还把 `8.800` 个 needed fragments 放进 rejected。这个读数直接回应了“7B 都能 0.8，benchmark 可能太简单”的担心：原来的高 precision 可能只是保守少发。

## 旧模型输出投影

我还把之前 stratified20 的 Qwen2.5 role-list 输出投影到 hard-card scorer 里。这里的 `source_id` 和 `visibility` 是按 fragment id 自动补齐的，所以它们只能当上界诊断，不能当模型会生成 provenance card 的证据。

| 条件 | strict | coverage | precision | leak/eval | budget_pass | overrun | reject_recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-7b legacy projected | 0/40 | 0.443 | 0.786 | 0.050 | 0.625 | 1.275 | 0.000 |
| qwen2.5-14b legacy projected | 0/40 | 0.615 | 0.808 | 0.450 | 0.400 | 4.725 | 0.000 |

这比原来的 role assignment 更有解释力。7B 的 `0.786` precision 放到 hard-routing 里，更像 conservative under-routing：coverage 只有 `0.443`，reject 行为为 `0`。14B coverage 到 `0.615`，同时 budget pass 掉到 `0.400`，leak 到 `0.450/eval`，说明更激进的路由开始踩边界。

## 方向判断

我现在倾向于这样判断：多 agent communication 这个大词确实饱和，`private evidence -> preference pollution` 这条线也太细；但问题本身还有空间，浅的是 task surface。我们需要先把 benchmark 做厚，让它自然承载 provenance、budget、selective admission、downstream execution。

现在这个 hard-routing V0 给了一个可执行入口：同一个 PerspectiveGap 数据面，先把“该给谁、给多少、凭什么给、哪些要拒绝”变成可测量约束。它还没到 A 会 idea，但能帮我们判断下一步有没有现象。

## 下一步

最直接的一步是跑 direct hard-card prompting：在同一个 stratified20 上让 7B/14B 直接输出 `fragment_id/source_id/visibility/rejected`，和 legacy projection 对齐比较。

我会看四个信号：

- strict 是否出现非零；
- reject_recall 是否从 `0` 抬起来；
- budget_pass 是否提高；
- coverage 是否没有塌掉。

如果 direct hard-card prompting 有结构性差异，再扩到 full220。若 strict 全零且错误全是格式/预算失败，先加一个 constrained arm：typed provenance router、DALA-style budgeted routing auction、source perturbation 三选一。这里我更偏向 source perturbation，因为它更容易把“来源身份”变成行为必要性，paper story 也更容易长出来。
