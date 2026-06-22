# 近场 Benchmark 大表

Snapshot date: `2026-06-18`.

## 核心判断

近场 benchmark 已经足够多，但目前没有一个现成对象同时覆盖本项目最关心的五件事：`hidden/private information`、`recipient-specific scope`、`source/provenance`、`verification/rejection`、`downstream decision`。

这意味着 benchmark 问题确实是当前瓶颈。继续横向找更多 benchmark 有价值，但价值主要在于建立坐标图和排除伪方向；真正的下一步应是用这张表判断：哪些 benchmark 值得实跑 pilot，哪些只提供外部压力，哪些暴露出需要构造 `Hidden-State Admission Benchmark` 的空位。

## 读表规则

标记含义：

- `Y`: 原 benchmark 或本地 packet 明确覆盖。
- `P`: 部分覆盖，或需要本地改造后才覆盖。
- `N`: 基本不覆盖。
- `?`: 需要代码/数据进一步 audit。

状态含义：

- `run`: 本地已经有可解释模型或基线结果。
- `pilot`: 值得做小样本 contact。
- `audit only`: 当前主要用于外部压力或 related work，不优先跑模型。
- `blocked`: 环境条件不足，不能声称官方设置已复现。

## 总表

| 层级 | Benchmark / 对象 | 来源 | 本地状态 | hidden/private | recipient scope | source/provenance | verification/rejection | downstream decision | budget/constraint | 当前 verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | HiddenBench | [paper](https://arxiv.org/abs/2505.11556), [code](https://github.com/jonradoff/hiddenbench), HF dataset | `run`; 已有 full65 与多轮 ablation | Y | P | P | N | Y | N | 最干净的通信必要性外部底座，但 fact-only 已接近 ceiling |
| P0 | PerspectiveGap | [paper](https://arxiv.org/html/2606.08878v1), local clone | `run`; 220 contact, 40-row 7B/14B, source-ledger 系列 | P | Y | P via local perturbation | P via local reject/source scope | N | P via local budget | 最好的 role-specific routing 外部镜片，但缺 downstream execution |
| P0 | State Admission V1/V2 | local packet over PerspectiveGap / HiddenBench cases | `run`; V1 full40, V2 smoke9 | P | Y | Y | Y | P | Y | 内部机制显微镜；能暴露 admission 边界和证据充分性失败，不能单独当外部 benchmark |
| P1 | PACT-style split evidence | [PACT paper](https://arxiv.org/html/2606.05304v1), local PACT clone | `pilot`; 旧 PACT trace 多，真正 split-evidence 需重启 | P | P | P | P | Y | P | 好的 public-state / evidence handoff 压力；旧 saved-field 结果只能当背景 |
| P1 | Silo-Bench | [paper](https://arxiv.org/abs/2603.01045), [html](https://arxiv.org/html/2603.01045v2) | `pilot` candidate; 尚未 local contact | Y | N/P | N | N | Y | Y | 强测 distributed state integration；不测 source/scope/admission |
| P1 | AgentLeak | [paper](https://arxiv.org/abs/2602.11510), [code](https://github.com/Privatris/AgentLeak) | `audit only` now | Y | Y/P | P | P | P | P | 强 privacy / internal-channel leakage 压力；偏安全，不直接测 utility admission |
| P1 | SOTOPIA-TOM | [paper](https://arxiv.org/abs/2605.02307), [html](https://arxiv.org/html/2605.02307v1) | `audit only` now | Y | Y | P | P | P | P | 很贴近 disclosure / privacy / ToM；judge 与开放交互风险需先审计 |
| P1 | DeLM | [paper](https://arxiv.org/abs/2606.10662), [html](https://arxiv.org/html/2606.10662v1) | `audit only`; 方法邻居 | P | P | Y | Y | Y | P | shared verified context 已占住一部分 state-admission 语言；应作为 control/collision pressure |
| P1 | CICL / Decision-Aware Memory Cards | [paper](https://arxiv.org/abs/2606.08151) | `audit only`; 方法邻居 | N/P | N/P | Y | P | Y | Y | decision-critical context selection 很近；提醒我们必须打强 packing / utility baseline |
| P1 | PACT method itself | [paper](https://arxiv.org/html/2606.05304v1), local clone | `audit only` as method; local code可跑 | P | P | P | P | Y | Y | action-state communication 是强 collision；不能把结构化 public state 当新意 |
| P2 | TeamBench | [paper](https://arxiv.org/html/2605.07073v1), [site](https://teambench.github.io/) | `blocked`; A800_2 无 Docker/rootless prerequisites | Y/P | Y | P | P | Y | Y | 最强工程级 role separation 压力；当前不能报告官方隔离结果 |
| P2 | AgentDojo | [paper](https://arxiv.org/abs/2406.13352), [site](https://agentdojo.spylab.ai/) | `audit only` | P | P | P | Y | Y | Y | untrusted tool result / prompt injection 压力；用于安全侧 source boundary |
| P2 | CaMeL / control-data flow work | security related work | `audit only` | P | P | Y | Y | Y | P | 约束我们不能泛泛讲安全隔离；可借鉴 data/control flow 语言 |
| P2 | OSWorld | [paper](https://arxiv.org/abs/2404.07972), [site](https://os-world.github.io/) | `audit only` | N/P | N | P | P | Y | Y | 下游真实 agent 能力压力；太宽，不适合当前主尺度 |
| P2 | AppWorld | [paper](https://arxiv.org/abs/2407.18901) | `audit only` | P | N/P | P | P | Y | Y | app/tool execution 下游参照；不直接测 multi-agent state admission |
| P2 | WebArena / VisualWebArena | [WebArena](https://arxiv.org/abs/2307.13854), [VisualWebArena](https://arxiv.org/abs/2401.13649) | `audit only` | N/P | N | P | P | Y | Y | web agent 生态压力；当前不应吞掉主线工程时间 |
| P2 | TheAgentCompany | [paper](https://arxiv.org/html/2412.14161v2), [code](https://github.com/TheAgentCompany/TheAgentCompany) | `audit only` | P | P | P | P | Y | Y | 真实工作流强，但通信因素混在 browse/code/tool/coordination 中 |
| P2 | tau-bench | [paper](https://arxiv.org/abs/2406.12045) | `audit only` | P | N/P | P | Y | Y | Y | rule-following / tool-user interaction 下游参照；偏单 agent policy |

## P0 Audit Cards

### HiddenBench

本地证据：

- 数据：`data/external/hiddenbench/benchmark.json`
- 主报告：`reports/20260617-hiddenbench-communication-necessity-qwen25-14b.md`
- Stage 1/2/3/4 reports：`reports/20260617-hiddenbench-v2-*.md`

关键读数：

| Condition | Qwen2.5-14B full65 |
| --- | ---: |
| `shared_only` | 1/65 |
| `full_info` | 59/65 |
| `oracle_public_facts` | 56/65 |
| old `exchange_then_decide` | 24/65 |
| `fact_only_exchange` | 57/65 |

它能支持的 claim：

- 外部任务强烈支持 hidden/private information 移动是必要条件。
- 自由文本 exchange 的失败主要来自 message pollution、recommendation leakage 和 shared overtalk。
- 干净 fact-only public messages 能逼近 oracle public facts。

它不能支持的 claim：

- 它不能单独支撑 source/scope/rejection/admission 问题，因为官方任务没有 recipient-specific scope 和 verification lifecycle。
- 在 fact-only 条件接近 ceiling 后，它很难继续区分更细的 state protocol。

下一步：

- 抽取 HiddenBench failure families，转成 `Hidden-State Admission` v0 的自然 case seeds。
- 不继续单独扩 fact-only prompt variant。

### PerspectiveGap

本地证据：

- Upstream：`baselines/PerspectiveGap/upstream`
- contact：`experiments/20260618-local-perspectivegap-contact/`
- 报告：`reports/20260618-perspectivegap-benchmark-contact.md`
- source-ledger 系列：`reports/20260618-perspectivegap-source-ledger-rotated20.md`, `reports/20260618-perspectivegap-budget-compiled-source-ledger.md`, `reports/20260618-perspectivegap-tight-budget-source-ledger.md`

关键读数：

| Setting | Strict / 关键指标 |
| --- | --- |
| oracle deterministic baseline | 220/220 |
| all-to-all baseline | 0/220, coverage 1.000, precision 0.318 |
| no-distractor all-to-all | 0/220, coverage 1.000, precision 0.350 |
| 14B role assignment stratified20 | 0/40, coverage 0.615, precision 0.808, leak 0.450 |
| 14B source-ledger rotated20 | 3/40, coverage 0.854, precision 0.779, budget_pass 0.225 |
| 14B budget-compiled source-ledger | 12/40, coverage 0.854, precision 1.000, budget_pass 1.000 |
| tight-budget utility-density greedy | 25/40, utility ratio 0.982 |
| tight-budget 14B + compiler | 10/40, utility ratio 0.846 |

它能支持的 claim：

- role-specific routing 是真实外部压力，不是内部臆造。
- all-to-all 覆盖率高但 strict 失败，说明边界 precision 是硬指标。
- source/scope ledger 能显著改变模型行为；deterministic compiler 能稳定修复一部分边界执行问题。

它不能支持的 claim：

- 它不能直接支撑 downstream agent execution 更可靠，因为官方任务主要评 prompt construction。
- tight-budget V0 被简单 greedy baseline 打得很高，不能支撑复杂 admission method claim。

下一步：

- 做 case audit：missing-needed、over-shared、distractor leak、wrong-recipient、budget overrun。
- 若继续做 tight-budget，应引入 dependency closure 或 role-coupled constraints。

### State Admission V1/V2

本地证据：

- V1 local packet：`experiments/20260618-local-state-admission-v1/`
- V2 preflight：`experiments/20260618-local-state-admission-v2-preflight/`
- V2 smoke：`experiments/20260618-local-state-admission-v2-smoke/`
- reports：`reports/20260618-state-admission-v1-*.md`, `reports/20260618-state-admission-v2-*.md`

关键读数：

| Setting | Strict / 关键指标 |
| --- | --- |
| V1 group_density_global | 32/40, utility 0.967 |
| V1 direct Qwen2.5-14B | 0/40, coverage 1.000, precision 0.4025, budget_pass 0 |
| V1 budget-first Qwen2.5-14B | 0/40, coverage 0.7914, budget_pass 0.100 |
| V1 Qwen2.5-14B priority + executor | 28/40; offline pair-group recompile 33/40 |
| V1 Qwen2.5-7B fallback-required priority | 31/40 |
| V1 7B ledger-first hidden-unit | 1/40, utility 0.0409 |
| V2 visible-facts-first smoke9 | strict 0, downstream_ok 0.333, visible_precision 0.954, visible_recall 0.986 |

它能支持的 claim：

- 模型会识别许多有用 source，但 direct admitted state 会过度承认、超预算、填空角色。
- 模型在 exposed admission units 上有 priority 信号，规则执行器能保证合法性。
- hidden admission-unit construction 是断点；V2 又把断点推进到 evidence sufficiency。

它不能支持的 claim：

- 它是内部 synthetic / semi-synthetic pressure，不能单独作为外部 benchmark 主结果。
- 强 symbolic baseline 很强，因此不能用它讲复杂优化算法优势。

下一步：

- 把 V2 改成 evidence-slot completeness：候选答案先列必要支撑槽位、排除槽位，再判定是否证据充分。
- 从 HiddenBench / PerspectiveGap 抽真实 case seed，降低 synthetic 痕迹。

## P1 Audit Cards

### PACT-Style Split Evidence

本地证据：

- Upstream：`baselines/PACT/upstream`
- reproduction notes：`baselines/PACT/reproduction.md`
- 旧 PACT / field reports：`reports/20260615-pact-*.md`
- benchmark-first reset：`reports/20260617-benchmark-first-reckoning.md`

当前判断：

- PACT 是强方法邻居，action-state public communication 已经占住“结构化公共消息”表面。
- 可继续用的是 PACT-style split-evidence setting，例如 HotpotQA / 2Wiki 中 partial evidence agent 需要交换 supporting facts。
- 旧 saved-field re-answer 结果不能当官方 benchmark 结果。

下一步：

- 做一个真正 split-evidence pilot：partial evidence、full evidence、oracle public evidence、PACT/action-state、fact-card/admission condition。
- 先做 gold/parser smoke，尤其要避免 final-answer surface 把 QA 结果污染。

### Silo-Bench

外部定位：

- 30 个 algorithmic distributed coordination tasks。
- 三类 communication complexity levels。
- 重点是 communication-reasoning gap：agent 可能交换到足够信息，却无法整合 distributed state。

当前判断：

- 它非常适合测“获得信息以后能不能整合”，可作为 HiddenBench ceiling 后的补充压力。
- 它不天然测 source/scope/rejection，所以不能替代 State Admission。

下一步：

- audit repo / scorer / fixtures。
- 若依赖轻，先跑 official fixture 和 5-row transparent baseline。

### AgentLeak

外部定位：

- 1000 scenarios，覆盖 healthcare、finance、legal、corporate。
- 关注 multi-agent internal channels：inter-agent messages、shared memory、tool arguments 等。

当前判断：

- 它直接提醒我们不能只看 final output；内部通信泄露本身就是 failure。
- 它偏 privacy/security，适合作为 source/scope violation 的外部压力。

下一步：

- 先 audit taxonomy 和 channel labels，看能否映射到 `source_scope_violation`、`private_leakage`、`recipient_violation`。

### SOTOPIA-TOM

外部定位：

- 多方交互，public broadcast 和 private direct message。
- 160 human-reviewed scenarios，3 到 5 agents，private knowledge 和 channel-dependent sharing policies。

当前判断：

- 它贴近“什么时候该公开、私聊、追问或保密”的社会型信息管理。
- 评估可能依赖 judge 或开放交互，gold 稳定性要先审。

下一步：

- 做 read-only audit：scenario schema、private knowledge、sharing policy、scoring metrics。
- 若 scorer 足够稳定，再 tiny pilot。

## 缺口矩阵

| 能力轴 | HiddenBench | PerspectiveGap | State Admission | PACT-style | Silo-Bench | AgentLeak | SOTOPIA-TOM | TeamBench |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hidden/private information | Y | P | P | P | Y | Y | Y | P |
| recipient-specific scope | P | Y | Y | P | N/P | Y/P | Y | Y |
| source/provenance | P | P | Y | P | N | P | P | P |
| verification/rejection | N | P | Y | P | N | P | P | P |
| downstream decision | Y | N | P | Y | Y | P | P | Y |
| budget/communication constraint | N | P | Y | P | Y | P | P | Y |
| strong transparent baselines | Y | Y | Y | P | ? | ? | ? | P |
| local runnable now | Y | Y | Y | P | ? | ? | ? | N |

最重要的空位：

```text
hidden/private facts
+ recipient-specific source/scope
+ verification/rejection lifecycle
+ evidence sufficiency
+ downstream decision
+ strong transparent baselines
```

这正是 `Hidden-State Admission Benchmark` 应该瞄准的空间。

## Pilot 优先级

第一批只做已经有本地基础的对象：

| 顺序 | 对象 | 目标 | 最小动作 | 停止条件 |
| --- | --- | --- | --- | --- |
| 1 | HiddenBench failure extraction | 找真实 case seeds | 抽 8-12 个 fact-only ceiling / exchange fail cases | 若 case 无法自然转 source/scope/rejection，停止转写 |
| 2 | PerspectiveGap case audit | 明确 routing failure families | 对 40-row stratified20 写 case cards | 若错误都只是 prompt compliance，暂停方法化 |
| 3 | State V2 evidence-slot packet | 正式测 evidence sufficiency | 9-row smoke 扩为 slot-level scorer | 若槽位正确但 final 仍错，保留为核心失败 |
| 4 | PACT-style split-evidence pilot | 回到真实 QA downstream | 10-20 HotpotQA / 2Wiki split rows | 若 parser/gold surface 不稳，先修 evaluator |

第二批只做 contact：

| 顺序 | 对象 | 目标 | 最小动作 |
| --- | --- | --- | --- |
| 5 | Silo-Bench | 测 distributed state integration | official fixture + transparent baseline |
| 6 | AgentLeak | 映射 leakage metrics | taxonomy / channel label audit |
| 7 | SOTOPIA-TOM | 审 sharing policy 与 judge | schema + scorer audit |
| 8 | TeamBench | 等 Docker/rootless 条件 | 保持 blocked record，必要时找有 Docker 的机器 |

## 对 Hidden 和 State 两条线的判断

Hidden 线的瓶颈：

- 它已经强烈支持通信必要性。
- 它也支持自由文本 exchange 污染明显。
- 但 fact-only / blind-minimal 接近 oracle 后，继续在 HiddenBench 内部追 prompt 提升会被 ceiling 压扁。
- 它更适合提供自然 case seeds，而不是继续承担所有 state/admission claim。

State 线的瓶颈：

- 它把 source/scope/budget/rejection 机制拆得更清楚。
- 但 V1/V2 仍有 synthetic 痕迹，缺真实下游任务闭环。
- 当前最有价值的失败更接近这一点：模型看到可见事实后，仍不会稳定判断证据是否足够支撑最终承诺。

合并方向：

```text
HiddenBench 提供真实通信必要性和自然决策场景；
PerspectiveGap 提供 recipient-specific routing 和 boundary precision；
State Admission 提供 source/scope/rejection/evidence sufficiency 指标；
新的 v0 benchmark 应该只取三者交叉处，不做大而全排行榜。
```

## 本轮结论

近场 benchmark 版图支持你的直觉：当前推进发散，根因确实是尺度问题。最稳的动作是先用这张表把每个 benchmark 的可测 failure surface 固定下来，再决定哪些 prompt、protocol 或新 benchmark 值得继续投入。

下一步应落两个文档级产物：

1. `reports/20260618-near-field-benchmark-cartography.md`：面向人读的判断报告。
2. `data/hidden_state_admission_v0/README.md`：如果缺口成立，开始定义小而硬的新 benchmark v0。
