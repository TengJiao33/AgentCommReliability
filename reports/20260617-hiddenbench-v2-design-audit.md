# HiddenBench v2 实验设计复审

## 核心判断

HiddenBench v2 不能直接做成一套看起来完整的协议。更稳的做法是先把失败来源拆开：旧 `exchange_then_decide` 到底是 agent public message 污染或遗漏了私有事实，还是 final decider 看到了事实也不会整合。

下一次实验应先跑一个小而可诊断的 v2 smoke。它只测试两个改动：fact-only message surface 和 constraint-style final decision。`typed_fact_card`、`admission_check`、`constraint_merge` 暂时作为第二阶段，不应在第一轮和 fact-only 同时上。

## Skill 约束

`research-experiment-gate` 要求这个实验先写清 purpose、unit、primary contrast、controls、success/failure signal 和 invalidation conditions。当前设计还没达到 full65 launch 标准，只达到本地实现和 limit12 smoke 的标准。

`reproduction-first-research` 要求不要把一个 prompt surface 变化立即包装成方法。HiddenBench v2 的第一轮应当是 contact/diagnostic：让外部 benchmark 告诉我们 failure surface 在哪里。

`research-story-synthesis` 要求 C 必须攻击或暴露 B。这里的候选 B 还不能直接叫 public-state protocol failure；更准确地说，B 可能是三种之一：agent message pollution、private fact omission、decider integration failure。第一轮实验要区分这三者。

## 现有证据

旧 full65 给出的外部压力是强的：`shared_only` 为 `1/65`，`oracle_public_facts` 为 `56/65`，`full_info` 为 `59/65`，corrected `exchange_then_decide` 为 `24/65`。这说明任务需要 hidden information，且干净事实进入公共上下文后模型可以完成很多任务。

现有 exchange 失败样例显示 public messages 经常混入推荐语和 shared-option 优势。比如 Task 10 中 noxious gas 风险已经出现，但其他消息反复推荐 Warehouse B，最终 decider 仍选 Warehouse B。Task 11 和 Task 12 也类似：关键负面事实或修复性事实出现了，但 final answer 被显眼推荐语或旧 shared advantage 吸走。

这个观察还不能证明 typed fact protocol 有效。它只说明第一轮应该隔离 message surface 与 final integration。

## Preflight Contract

Purpose: 判断 HiddenBench 普通 exchange 的失败主要来自 agent public message 污染/遗漏，还是来自 final decider 对已公开事实的整合失败。

Unit: HiddenBench task condition record。核心 paired unit 是同一个 task 在不同 communication condition 下的 final decision。

Primary contrast: `exchange_then_decide` 对比 `fact_only_exchange`。两者都由局部 agent 产生 public messages；差别只在 agent public message 是否允许推荐答案和复述 shared option advantages。

Secondary contrasts:

- `shared_only`: 无私有信息下限。
- `full_info`: 全信息上限。
- `oracle_public_facts`: 脚本化干净私有事实上限。
- `fact_only_constraint_decide`: 使用同一批 fact-only messages，但 final decider 必须先列 option constraint table，再给答案。

Success signal:

- `fact_only_exchange` 明显高于旧 `exchange_then_decide`，并且低于或接近 `oracle_public_facts`，说明 message surface 是主要瓶颈。
- 若 `fact_only_exchange` 改善有限，但 `fact_only_constraint_decide` 明显改善，说明 final integration prompt 是主要瓶颈。
- 若两者都接近 oracle-public-facts，才允许进入 typed fact card / admission check 第二阶段。

Failure signal:

- `fact_only_exchange` 与旧 `exchange_then_decide` 接近，且 constraint decider 也不改善：当前 v2 不应继续包装成协议。
- `fact_only_exchange` 达到 oracle，但 messages 基本是把 hidden facts 原样抄出：它只证明“禁止推荐语”有用，不证明复杂 typed protocol 有贡献。
- 改善集中在少数任务类型或少数 easy tasks：不能扩大 claim。

Invalidation conditions:

- parser 对 `Answer: <choice>` 的解析仍有 unparsed 或 prefix 错配，没有经过 corrected analyzer。
- v2 条件与 oracle 条件泄漏同样的脚本化事实，导致比较失去意义。
- `fact_only_constraint_decide` 重新生成了 messages，而没有复用同一批 fact-only messages，导致 content 不恒定。
- public messages 仍包含推荐答案、option ranking、shared facts 大段复述或超出 private fact 的编造内容。
- full65 前没有 limit12 prompt audit。

Expected artifacts:

- runner: `scripts/run_hiddenbench_communication_probe.py`
- analyzer: `scripts/analyze_hiddenbench_records.py`
- smoke run: `experiments/<run-id-hiddenbench-v2-smoke12>/`
- possible full run: `experiments/<run-id-hiddenbench-v2-full65>/`
- report: `reports/20260617-hiddenbench-v2-qwen25-14b.md`

## Revised Stage Plan

Stage 0 是本地实现和 prompt audit。先只生成 prompts 或用 `--include-prompts` 跑 tiny local/remote smoke，抽查每个 condition 至少两个 task。重点检查 fact-only messages 是否只携带 private fact，constraint prompt 是否没有暗示正确答案。

Stage 1 是 limit12 GPU smoke，条件只放五个：

- `shared_only`
- `full_info`
- `oracle_public_facts`
- `exchange_then_decide`
- `fact_only_exchange`
- `fact_only_constraint_decide`

`fact_only_constraint_decide` 必须复用 `fact_only_exchange` 生成的同一批 agent messages。这样才能把 communication content 和 final integration 分开。

Stage 2 只有在 Stage 1 有可解释改进后才做。新增 `typed_fact_card_light`，字段只允许：

- `source_agent`
- `verbatim_private_fact`
- `message_scope`，例如 `private_report`

第一版 typed card 不让 agent 输出 `option_affected`、`polarity`、`recommended_answer`。这些字段会把模型自己的解释或推荐放进 communication object，容易测到 schema hallucination。

Stage 3 才考虑 interpreted cards 和 admission check。那一阶段要单独评估 card 字段正确性、citation correctness 和 final answer accuracy，不能只看最终准确率。

## Required Metrics

第一轮 summary 不能只报 accuracy。至少要输出：

- condition accuracy 和 unparsed count；
- paired contrasts：`oracle_public_facts_correct_exchange_wrong`、`fact_only_correct_exchange_wrong`、`constraint_correct_fact_only_wrong`；
- public message audit：private fact coverage、recommendation leakage、shared-fact overtalk、invented fact flag；
- final decision audit：final answer 是否引用或忽略 blocking facts；
- token usage by condition。

message audit 可以先用启发式和少量手工样例，不必在第一轮做成完美 evaluator。但如果没有这个 audit，full65 结果只能算 accuracy probe。

## Launch Gate

当前远端资源允许跑：A800_2 GPU 1-7 空，`Qwen2.5-14B-Instruct` 可用，HiddenBench 65 task 数据已在远端，旧 launcher `scripts/run_hiddenbench_probe_a8002.sh` 可复用。

但 full65 还不该启动。必须先完成：

1. 本地实现新 condition。
2. 同步 `run_hiddenbench_communication_probe.py` 和 `analyze_hiddenbench_records.py` 到远端。
3. limit12 smoke，包含 `--include-prompts` 或保留 message sidecars。
4. corrected analyzer 跑通。
5. 抽查至少 3 个旧失败任务，例如 Task 10、11、12。

## 判读边界

Qwen2.5-14B 仍然只是 cheap diagnostic backbone。即使 v2 在 full65 上有效，也只能说这个协议候选值得跨模型压力，不能说它已经支撑最终 paper claim。

如果 fact-only surface 已经接近 oracle，那么 typed fact card 可能只是工程包装；下一步应该去 PACT-style split evidence 或更强模型，而不是继续在 HiddenBench 上加字段。

如果 fact-only 和 constraint decision 都救不动 exchange，那么当前 public-state 方向在 HiddenBench 上要降级，转向官方 group harness、SOTOPIA-TOM contact，或重新检查 benchmark/task parsing。

## 当前结论

下一步不是直接实现完整 HiddenBench v2。下一步是做一个可退役的 Stage 1：fact-only message surface 与 constraint final decision 的小型对照。只有这个对照能定位失败来源时，typed fact card 和 admission check 才值得继续。
