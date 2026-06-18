# State Admission V1.1 Priority Executor Pressure

## 核心判断

这轮把 State Admission 的失败拆开了。Qwen2.5-14B 直接输出 source-card 时 strict 是 `0/40`；同一个模型只输出 group/bundle 优先级，再交给规则执行器处理预算、closure、reject 和 visibility，strict 到了 `28/40`。离线换成更贴合主目标的 `pair_group_primary` 执行策略后，strict 到了 `33/40`。

这个结果让方向更清楚：模型的高层 admission preference 已经有用，最脆的环节是把偏好变成合法状态。规则执行器能直接消掉全局预算爆炸和 closure 违规，把 failure surface 缩小到少数 group/bundle 排序错误。

## 证据链

| Condition | Strict | Coverage | Precision | Global budget pass | Utility ratio | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| direct default Qwen2.5-14B | 0/40 | 1.0000 | 0.4025 | 0.0000 | 0.0000 | 必要 source 全覆盖，但空角色也全填 |
| direct budget-first Qwen2.5-14B | 0/40 | 0.7914 | 0.4464 | 0.1000 | 0.0203 | 少填一些空角色，同时漏掉必要 bundle |
| priority + greedy executor | 28/40 | 0.8957 | 0.8202 | 1.0000 | 0.9067 | GPU run，40/40 parsed |
| priority + pair-group-primary recompile | 33/40 | 0.8712 | 0.9103 | 1.0000 | 0.9014 | 同一批 priority response 离线重编译 |
| symbolic group-density baseline | 32/40 | 0.9018 | 1.0000 | 1.0000 | 0.9666 | 强符号基线 |
| oracle priority executor | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 执行器上界 smoke |

Artifacts:

- `scripts/run_state_admission_v1_priority_openai_compatible.py`
- `scripts/run_state_admission_v1_a8002.sh`
- `experiments/20260618-a8002-state-admission-v1-priority-full40-qwen25-14b/README.md`
- `experiments/20260618-a8002-state-admission-v1-priority-full40-qwen25-14b/summary.md`
- `experiments/20260618-a8002-state-admission-v1-priority-full40-qwen25-14b/summary_pair_group_primary_recompiled.md`
- `experiments/20260618-local-state-admission-v1/summary_priority_oracle.md`
- `experiments/20260618-local-state-admission-v1/summary_priority_group_density.md`

## 机制解释

direct prompt 的失败是“有用就塞”。模型能覆盖必要 source，但没有稳定执行全局 admission。priority prompt 改变了输出对象：模型只负责把 pair group 和 role bundle 排序，规则层负责可行性。结果里 global budget pass 从 `0.0000/0.1000` 变成 `1.0000`，closure violations 变成 `0.0000`，说明规则层确实打中了上一轮的主要失效点。

`pair_group_primary` 的提升也很有机制味。greedy executor 在一些行里已经接受正确 pair group，又继续接收剩余预算里的单角色 bundle，导致 utility 仍高但 strict 被 extra 打掉。pair-group-primary policy 规定先尝试 pair group；只在没有 group 被接受时 fallback 到单 bundle。这个 policy 把 strict 从 `28/40` 推到 `33/40`，说明“规则执行器的 admission semantics”本身是贡献形状的一部分。

## 边界

这个结果还不能直接变成 paper 方法 claim。当前 priority prompt 明示了 role bundle、pair group、cost 和 utility，模型没有从原始多 agent trace 中自己发现 admission units。`group_density_global` 的 utility 仍高于 model-priority executor，说明符号规划基线很强。

更准确的当前 claim 是：在 State Admission V1.1 这个压力对象上，LLM 直接承认状态会爆预算；把输出对象提升为 admission priority，再用确定性规则执行，能大幅恢复合法性和 strict score。它支持一个 live protocol candidate，但还需要更自然的 admission-unit construction 和跨模型复现。

## 下一步压力

下一步应该压两个方向：

1. 复现：用同一 priority+executor 跑 7B，判断这个分解是否只适合 14B。
2. 构造：把 bundle/group table 逐步隐藏或弱化，让模型从 source ledger 或 trace schema 里提出 priority，看性能从哪里开始掉。
3. 方法化：把规则执行器写成明确 protocol：preference proposal -> deterministic admission executor -> rejected-state certificate。评价不只看 strict，也看 budget legality、empty-role precision、needed rejection 和 utility。

我的当前判断：这条线比“让模型自己通信得更好”更像能写出机制。机制点是“偏好可以交给模型，合法承认必须交给规则层”。
