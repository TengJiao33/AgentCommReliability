# PerspectiveGap Benchmark Contact

## 核心判断

PerspectiveGap 值得进入当前 benchmark-first 主线。它直接测多 agent 编排时的角色信息分配：每个 sub-agent 应该拿到哪些 fragment，哪些上下文会构成泄露或干扰。

这条线比继续做 HiddenBench sender-format 小变体更有外部压力。HiddenBench 暴露 sender overtalk 和 recommendation leakage，PerspectiveGap 则把同一类问题移到一个 answer-keyed orchestration benchmark 上，并且有本地可运行 scorer。

## 做了什么

我从 digest 和外部检索中把 PerspectiveGap 提到 P0 contact。依据是它有公开 GitHub repo、HF 数据集、确定性 scorer，并且题目本身就是 multi-agent orchestration prompting。

本地浅克隆成功：

```text
baselines/PerspectiveGap/upstream
commit: 60b1dcaaeeb40619075f6cd8779c47fa4b344391
```

我没有调用模型 API。当前只做 benchmark contact、renderer/scorer 验证和透明 baseline。

## 关键证据

官方 fixture scorer 跑通，role assignment 和 prompt writing 都是 `1/1`。本地 renderer 生成了 `220` 条 evaluation，对应 `110` 个 scenario 和 seed `1, 42`。

我随后建了隔离 `.venv`，安装 upstream package 和 `pytest`，官方测试通过：`18 passed in 3.11s`。这说明 renderer、scorer、model runner 相关单元测试在本机可复现。

结构审计显示它不是一个太小的 toy：角色数从 `2` 到 `6`，fragment 数从 `7` 到 `13`，每行平均 `13.0` 个 role-fragment need events。每行都有且只有一个 distractor，而且 answer key 明确标记每个 role 需要哪些 fragment。

透明 baseline 给了最重要的压力：

| baseline | strict pass | coverage | precision | distractor leak/eval |
| --- | ---: | ---: | ---: | ---: |
| oracle | 220/220 | 1.000 | 1.000 | 0.000 |
| all_to_all | 0/220 | 1.000 | 0.318 | 3.800 |
| no_distractor_all_to_all | 0/220 | 1.000 | 0.350 | 0.000 |
| shared_intersection_only | 0/220 | 0.031 | 1.000 | 0.000 |
| role_name_heuristic | 0/220 | 0.568 | 0.280 | 3.714 |

这里最重要的是 `no_distractor_all_to_all`：就算去掉明显 distractor，把所有真实任务信息都给所有角色仍然 `0/220` strict pass。这说明 benchmark 真正在测角色边界，不只是测能否识别无关 prompt advice。

## 机制解释

PerspectiveGap 给了一个更大的问题表述：multi-agent 失败不只来自 agent 在讨论中污染偏好，也来自 orchestration 阶段把上下文路由错了。一个 role 得到不该看的评分标准、审查规则、调度规则或执行要求，就会改变后续工作流。

这个机制能接住我们之前的 HiddenBench 现象。HiddenBench 中 fact-only/blind-minimal 接近 oracle，说明自由文本消息容易把私有事实、建议、共享事实复述混在一起。PerspectiveGap 把这个问题变成可评分的 routing task：每个 fragment 是不是应该进入某个 role 的 prompt。

更准确地说，新的大问题可以写成：

```text
LLM agents need a state routing layer before they need a richer debate protocol.
The hard part is deciding which facts become visible to which role, with what source and scope.
```

## 边界

当前还没有模型行为结果。所有数字都来自 oracle 和 deterministic baselines，因此它证明的是 benchmark contact 成功，以及这个 benchmark 有合适的边界压力。

prompt-writing scorer 是 n-gram threshold 规则，未来模型 run 需要先从 `role_assignment` 做起。这个任务是 JSON assignment，解析更清楚，适合第一轮 model contact。

PerspectiveGap 测的是 prompt construction，不是完整 agent execution。它可以作为信息路由 benchmark，但不能单独证明下游 agent 执行是否更可靠。

## 旁路尝试

SCR-Bench 也值得继续关注。它的公开 README 说明三类组合风险：CapFlow、TrustLift、AuthBlur，并报告组合路径会暴露单技能审查看不到的风险。但今晚两次 `git clone` 都在 GitHub transport 阶段超时，我已经清理半成品目录。它适合作为后续 skill/workspace composition 风险 benchmark，不抢 PerspectiveGap 的 P0 位置。

## 下一步压力测试

下一步不要先做完整 220-row 模型 sweep。更好的接触是跑一个小而硬的 role-assignment model smoke：

```text
scenarios: pg_000, pg_004, pg_006, pg_070
task: role_assignment only
conditions: raw model, strict JSON repair if needed, maybe a typed-router prompt
readout: strict pass, coverage, boundary precision, distractor leakage
case audit: missing-needed, over-shared, distractor leak, role-confusion
```

如果小 smoke 显示 raw model 主要过度共享，typed-router 才有意义。若 raw model 已经很强，PerspectiveGap 的价值会转向 cross-model ranking 或 leakage taxonomy，而不是方法 claim。

## 当前结论

这次 contact 给主线带来一个更大的 benchmark 方向：从 sender message hygiene 转到 role-specific information routing。它不是最终故事，但它比继续围着“私有证据变偏好污染”更有空间，也更符合最近 digest 里 harness、workspace、provenance、governance 的趋势。
