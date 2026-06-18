# State Admission V1.1 Priority Executor 7B Replication

## 核心判断

7B replication 给了一个硬一点的信号：priority+executor 分解可以跨模型保住合法性，但小模型的 priority 质量明显掉。Qwen2.5-7B 在同一套 `pair_group_primary` 执行器下达到 `25/40` strict、`0.8530` utility，所有全局预算、角色预算和 closure 检查都通过。

归一化重编译只把 7B 从 `25/40` 推到 `26/40`，utility 从 `0.8530` 到 `0.8828`。所以 parser 噪声确实存在，但主瓶颈已经转到模型能否把 fallback bundle 写进可执行 JSON priority。

追加的 `fallback_required` schema 压力把 7B 推到 `31/40` strict，同时保持 global budget pass `1.0000` 和 closure violations `0.0000`。这个结果说明“可执行 priority 合约”本身是机制的一部分；代价是 precision 和 utility 下降，说明模型列了更多候选，执行器替它挡掉更多不可行项。

## 证据链

| Condition | Strict | Coverage | Precision | Global budget pass | Utility ratio | Closure violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-7B priority + pair-group-primary | 25/40 | 0.7546 | 0.9044 | 1.0000 | 0.8530 | 0.0000 |
| Qwen2.5-7B normalized recompile | 26/40 | 0.7853 | 0.9078 | 1.0000 | 0.8828 | 0.0000 |
| Qwen2.5-7B fallback-required priority | 31/40 | 0.8344 | 0.8718 | 1.0000 | 0.8431 | 0.0000 |
| Qwen2.5-14B priority + pair-group-primary | 33/40 | 0.8712 | 0.9103 | 1.0000 | 0.9014 | 0.0000 |
| symbolic group-density baseline | 32/40 | 0.9018 | 1.0000 | 1.0000 | 0.9666 | 0.0000 |
| oracle priority executor | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

Artifacts:

- `experiments/20260618-a8002-state-admission-v1-priority-full40-qwen25-7b/README.md`
- `experiments/20260618-a8002-state-admission-v1-priority-full40-qwen25-7b/summary.md`
- `experiments/20260618-a8002-state-admission-v1-priority-full40-qwen25-7b/summary_normalized_recompiled.md`
- `experiments/20260618-a8002-state-admission-v1-priority-fallback-full40-qwen25-7b/README.md`
- `experiments/20260618-a8002-state-admission-v1-priority-fallback-full40-qwen25-7b/summary.md`
- `experiments/20260618-a8002-state-admission-v1-priority-full40-qwen25-14b/summary_pair_group_primary_recompiled.md`
- `experiments/20260618-local-state-admission-v1/summary_priority_group_density.md`
- `scripts/run_state_admission_v1_priority_openai_compatible.py`

## 机制解释

这轮把 7B 的失败拆成两块。第一块是接口噪声：7B 会输出 `bundle_id=dispatcher:evidence_bundle`，也会把角色名里的空格改成下划线。保守归一化把 `unknown_unit` skip 从 `37` 降到 `3`。

第二块更重要：归一化以后只新增 1 条 strict pass。典型 case 是模型在解释文字里说“pair group 超预算，所以应该选某个单角色 bundle”，但 JSON priority 只保留了超预算 pair group。执行器只能编译 JSON 里的 priority，不能从解释文字里猜计划。

第三块来自 `fallback_required`：一旦 prompt 明确说明 explanation 不计分、JSON 必须包含 fallback bundles，7B 净增 5 条 strict pass。skip reason 里 `unknown_unit` 从 default 的 `37` 到 fallback 的 `0`，但 `global_budget` skip 从 `37` 到 `57`，`pair_group_primary_mode` 从 `100` 到 `143`。这说明 schema 让模型写出了更多可执行候选，执行器也承担了更多过滤工作。

这说明当前机制不能概括成“模型不会看成本和 utility”。更准确地说，模型能形成部分 admission preference，但小模型很难稳定把这个 preference 写成机器可执行的、有 fallback 的优先级序列；schema 能缓解这个问题，但不能替代真正的 priority quality。

## 边界

这个 replication 支持 protocol 形状，但还没有支持完整 paper claim。prompt 仍然把 bundle、group、cost、utility 都列出来了，模型还没有从原始多 agent trace 里自己构造 admission units。

强符号基线仍然压着我们。`group_density_global` 是 `32/40` strict、`0.9666` utility；14B pair-group-primary 是 `33/40` strict、`0.9014` utility；7B fallback-required 是 `31/40` strict、`0.8431` utility。现在的优势更多来自“把合法执行交给规则层”，还没有展示出模型偏好优于强规划启发式。

## 对故事的影响

这条线可以继续，但故事要收窄。宽泛的“多 agent 通信更可靠”太空，当前能被实验托住的说法是：

在 role-scoped state admission 里，LLM 直接输出 admitted state 容易过度承认；把模型输出对象改成 admission priority，再用确定性执行器处理预算、closure、reject 和 visibility，可以把失败面从合法性错误压缩到 priority 质量错误。

这个说法有机制，也有边界。它的 A/B/C 现在可以这样写：

- A：让模型直接生成每个角色的 admitted source cards。
- B：模型知道哪些 evidence 有用，但没有稳定执行全局 budget、recipient scope 和 fallback。
- C：让模型只给 admission priority，规则执行器负责合法承认和拒绝证明。
- M：strict、coverage、precision、utility、budget pass、closure violations。
- D：direct 14B 全局预算崩掉；priority+executor 在 14B/7B 上都保持 legal；normalized 7B 显示 parser 只解释小部分差距；fallback-required 7B 显示可执行 schema 能显著改善 strict，但 utility 仍受 priority 质量约束。

## 下一步压力

下一步要压两个更狠的地方。

1. Unit-construction 压力：逐步隐藏 group/bundle 表，让模型从 source ledger 或 trace schema 中提出 priority。只要性能大幅掉，就说明当前结果依赖人工 admission-unit 展示。
2. Baseline 压力：把 `group_density_global` 当强 baseline 保留。我们的 claim 不能说“优化更强”，只能先说“合法 admission 执行面更干净、更可诊断”。
3. Downstream 压力：把 admitted state 接到真实任务或 decision proxy，看 legal admission 是否带来最后任务收益，而不只是在 synthetic source-card metric 上更干净。
