# State Admission V1.1 Ledger-First Hidden-Unit Pressure

## 核心判断

ledger-first 7B 把当前 story 的断点压出来了。不给 role-bundle 和 pair-group 表，只给 source ledger、budget、utility/hint 和 payload，让模型自己输出 source-level admission priority，Qwen2.5-7B 只到 `1/40` strict、`0.0409` utility。

执行器已经通过 smoke。新 compiler 的 oracle smoke 是 `40/40`，GPU run 的 budget、reject、scope 都干净。真正掉的是 admission-unit construction：source-level 选择没有稳定组成完整 role bundle，更无法组成 cross-role group。

## 证据链

| Condition | Strict | Coverage | Precision | Global budget pass | Utility ratio | Closure violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ledger oracle compiler | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| ledger utility-density local | 4/40 | 0.7362 | 0.5106 | 1.0000 | 0.4931 | 1.0500 |
| ledger hint-density local | 4/40 | 0.7055 | 0.4772 | 1.0000 | 0.4024 | 1.1000 |
| Qwen2.5-7B ledger-first | 1/40 | 0.4417 | 0.4645 | 1.0000 | 0.0409 | 1.6750 |
| Qwen2.5-7B fallback-required priority | 31/40 | 0.8344 | 0.8718 | 1.0000 | 0.8431 | 0.0000 |
| Qwen2.5-14B priority + pair-group-primary | 33/40 | 0.8712 | 0.9103 | 1.0000 | 0.9014 | 0.0000 |
| symbolic group-density baseline | 32/40 | 0.9018 | 1.0000 | 1.0000 | 0.9666 | 0.0000 |

Artifacts:

- `scripts/run_state_admission_v1_ledger_openai_compatible.py`
- `scripts/run_state_admission_v1_a8002.sh`
- `experiments/20260618-local-state-admission-v1/prompt_audit_ledger_utility_payload_full40.jsonl`
- `experiments/20260618-local-state-admission-v1/summary_ledger_oracle.md`
- `experiments/20260618-local-state-admission-v1/summary_ledger_utility_density.md`
- `experiments/20260618-local-state-admission-v1/summary_ledger_hint_density.md`
- `experiments/20260618-a8002-state-admission-v1-ledger-full40-qwen25-7b/README.md`
- `experiments/20260618-a8002-state-admission-v1-ledger-full40-qwen25-7b/summary.md`

## 机制解释

priority runs 让模型在已有 admission units 上排序。这个表面看起来像 prompt trick，但 7B fallback-required 从 `25/40` 到 `31/40`，说明可执行 priority schema 确实有作用。

ledger-first run 拿掉 admission units 后，合法性仍然由规则层托住，但 closure 直接崩。模型会列出一些看起来相关、合法、或高 hint 的 source；compiler 会过滤超预算或错 recipient 的项；剩下的 source 往往只覆盖 bundle 的一部分。State Admission 的 utility 需要完整 bundle 或完整 pair group，所以 utility 掉到 `0.0409`。

这给出一个更明确的三层分解：

1. Source scope legality：哪些 source 能进哪些 role。
2. Admission-unit construction：哪些 source 共同构成一个可得分的 role bundle 或 cross-role unit。
3. Legal execution：在预算、closure、visibility、reject 下执行 priority。

目前第 1 层和第 3 层能被规则层处理，第 2 层仍是最弱环节。

## 边界

这个结果不能直接说明模型从真实任务里学不会构造单位。V1.1 的 pair-group utility 是 benchmark builder 合成的，模型没有看到真实 downstream reward。ledger-first 只证明：在当前 V1.1 表面上，单靠 source ledger、payload 和 item utility/hint，很难恢复隐藏 bundle/group 结构。

这也解释了为什么当前结果还撑不起完整方法故事。我们现在有一个清楚的机制切口，但 benchmark 还太人工：强符号 baseline 很强，hidden units 又太隐，真实任务收益还没接上。

## 对故事的影响

这轮把 paper 形状从 “priority executor 方法” 推到 “admission protocol 分层”。

可守的说法是：State Admission 需要把 source legality、unit construction、legal execution 分开评测。LLM 对已暴露 admission units 有排序信号；规则执行器能保证合法 state；但从原始 source ledger 构造 admission units 仍然是当前断点。

这比“多 agent 通信更可靠”更具体，也比“加一个 compiler”更不空。它给了一个真正需要解决的问题：怎样从 recipient-scoped evidence 中构造可执行、可验证、可预算的 admission units。

## 下一步压力

下一步应该做 V2 packet，继续在 V1.1 上磨 prompt 的收益很低。

1. Unit construction V2：让 admission units 来自真实下游任务结构，例如 action dependency、tool precondition、case field schema，减少对 builder 合成 pair utility 的依赖。
2. DeLM/CICL controls：加入 shared verified context baseline 和 decision-context selection baseline，证明 role-local admission 解决的是额外问题。
3. Two-stage model protocol：先让模型提出 candidate units，再让 executor 评分/筛选；和 exposed-unit priority、ledger-first source priority、symbolic group-density 三者比较。
4. Downstream check：把 admitted state 接到任务答案或 decision proxy，避免只在 source-card metric 上循环。
