# 近场 Benchmark 地图计划

Snapshot date: `2026-06-18`.

## 核心判断

当前主线最大风险是尺度不清。Hidden、state、routing、admission、typed public state 等尝试已经给出若干机制信号，但这些信号分散在不同实验体系里；如果不把近场 benchmark 拉成一张外部坐标图，后续尝试很容易继续变成 prompt variant、局部 packet 修补或内部指标自洽。

这份计划的目标是做一次 `near-field benchmark cartography sprint`：系统梳理并小规模接触最相关的外部 benchmark，判断它们各自测到什么失败、能不能承载我们的研究问题、哪些需要实跑、哪些只做外部压力记录。

本计划不以刷榜为目标。它要回答的是：

```text
我们的研究对象到底应被哪一类 benchmark 测量？
已有 benchmark 是否已经测到 hidden/private information、role-specific routing、source/scope、verification/rejection 和 downstream decision？
如果没有，缺口是否足够清楚，足够支持我们构造一个小而硬的新 benchmark？
```

## 研究问题

本轮 benchmark 地图只围绕五个问题展开。

1. 哪些 benchmark 真正要求信息在 agent / role / channel 之间移动？
2. 哪些 benchmark 能区分 coverage、boundary precision、leakage、verification violation 和 final task success？
3. 哪些 benchmark 已经被简单协议打到 ceiling，继续扩 prompt variant 会失去分辨率？
4. 哪些 benchmark 暴露出 direct generation admitted state 的问题，支持 executor / verifier / compiler 层存在必要性？
5. 哪些外部 benchmark 留下了一个未被覆盖的空位：hidden/private facts 需要经过 source/scope/verification/rejection 后进入 downstream decision？

## 工作原则

- 先做 benchmark audit，再做 GPU run。
- 每个 benchmark 进入实跑前必须有明确 primary contrast。
- 所有 claim-bearing run 都要记录 packet、gold、parser、controls、outputs 和 caveat。
- Docker / OS sandbox 受阻的 benchmark 先做 read-only audit、mock contact 或 blocked record，不把环境失败解释成模型行为。
- 不用 full run 代替问题设计。full run 只有在 pilot 已经显示 benchmark 有分辨率时才启动。
- 不把内部 synthetic packet 的高分当成外部有效性。内部 packet 只用于机制诊断和新 benchmark 草图。

## Benchmark 分层

| 层级 | Benchmark | 当前作用 | 本轮动作 | 是否优先实跑 |
| --- | --- | --- | --- | --- |
| P0 | HiddenBench | hidden/private information 与 communication necessity 的外部底座 | 复核现有 full65，抽取 failure families，设计 cross-benchmark metric schema | 是，小样本和已有 full65 复用 |
| P0 | PerspectiveGap | role-specific information routing 与 leakage | 复核 220 deterministic contact，整理 40-row model smoke，补 case audit | 是，先 pilot 不 full sweep |
| P0 | State Admission V1/V2 | source/scope/admission/rejection 的内部机制显微镜 | 统一成 benchmark 缺口说明，抽取可迁移 task schema | 是，但只作内部诊断 |
| P1 | PACT-style split evidence | public action-state 与 split evidence communication | 从旧 PACT trace 转向真正 split-evidence setting audit | pilot，可跑小样本 |
| P1 | Silo-Bench | communication complexity / distributed reasoning | readme、data、scorer audit，判断是否能接我们的 facts-to-state 指标 | 视依赖决定 |
| P1 | AgentLeak | multi-agent privacy leakage | 审计 internal channel、leakage metric 与我们 source/scope violation 的关系 | 先 audit，后 pilot |
| P1 | SOTOPIA-TOM | multi-party belief / disclosure / privacy | 审计 gold、judge 稳定性和 private fact 可测性 | 先 audit |
| P1 | PACT / DeLM / CICL | 方法邻居与 collision pressure | 作为外部方法压力，不直接当 benchmark 主体 | 不优先实跑 |
| P2 | TeamBench | OS-enforced role separation，工程级通信必要性 | 保持 blocked record；若 Docker 权限到位再 small contact | 当前 blocked |
| P2 | AgentDojo / InjecAgent / CaMeL | tool / prompt-injection / control-data flow 安全压力 | 只记录与 source-aware admission 的关系 | 暂不实跑 |
| P2 | OSWorld / AppWorld / TheAgentCompany | 下游真实 agent task | 判断是否能作为最终 ecological validity | 暂不实跑 |

## 统一审计表

每个 benchmark 都要填一行 audit card，字段如下：

```text
benchmark_id:
source:
local_path:
task_unit:
agent_or_role_structure:
hidden_private_information: yes/no/partial
recipient_specific_scope: yes/no/partial
source_or_provenance: yes/no/partial
verification_or_rejection: yes/no/partial
downstream_decision: yes/no/partial
budget_or_communication_constraint: yes/no/partial
gold_type:
scorer_type:
parser_risk:
known_baselines:
local_run_status:
docker_or_env_blocker:
primary_contrast_for_us:
metric_mapping:
ceiling_or_floor_risk:
claim_it_can_support:
claim_it_cannot_support:
next_action:
```

## 统一指标映射

本项目后续不应只看 final accuracy。所有近场 benchmark 尽量映射到下面的指标族。

| 指标族 | 问题 | 典型读数 |
| --- | --- | --- |
| task success | 最终任务有没有做对 | exact match, pass rate, downstream decision ok |
| information coverage | 该进入 public/admitted state 的信息是否进入 | required fact recall, role-fragment coverage |
| boundary precision | 不该进入某个角色的信息是否被过度共享 | role precision, over-share rate |
| leakage | distractor/private/unscoped 信息是否泄露 | distractor leak, privacy leak, scope violation |
| source fidelity | 信息是否带着正确 source / provenance | source match, citation correctness |
| verification discipline | unverifiable / rejected facts 是否被阻断 | rejection recall, verification violation |
| evidence sufficiency | 模型是否知道证据够不够 | abstention correctness, insufficiency detection |
| budget discipline | 通信或上下文预算是否被遵守 | budget pass, utility ratio |
| protocol sensitivity | 方法差异是否真的来自 protocol | paired delta, control gap, oracle gap |

## 阶段计划

### Phase 0: 建地图

目标：先知道每个 benchmark 在测什么，是否能给我们尺度。

产物：

- `docs/near_field_benchmark_table.md`
- 每个 P0/P1 benchmark 一张 audit card
- blocked benchmark 的环境记录
- 初版 metric mapping

完成条件：

- 至少覆盖 HiddenBench、PerspectiveGap、State Admission、PACT-style split evidence、Silo-Bench、AgentLeak、SOTOPIA-TOM、TeamBench。
- 每个 benchmark 明确标注 `run`, `pilot`, `audit only`, `blocked` 四类状态之一。
- 每个 benchmark 都写出它能支持和不能支持的 claim。

### Phase 1: 做 contact，不做大跑

目标：让 benchmark 的 renderer、scorer、gold、parser 先过门。

优先动作：

- HiddenBench：复核已有 full65 条件、抽取 clean subset 和 ceiling 条件。
- PerspectiveGap：复核 deterministic baseline、整理 7B/14B 40-row role assignment 结果、补 case audit。
- PACT-style split evidence：找出最小可跑 HotpotQA / 2Wiki split setup，避免继续依赖 saved-field re-answer。
- Silo-Bench / AgentLeak / SOTOPIA-TOM：先跑官方 fixture 或 tiny sample；若依赖复杂，记录 blocker。

完成条件：

- 每个实跑 benchmark 都有 oracle 或 fixture smoke。
- 每个 benchmark 都有至少一个 transparent baseline。
- 每个 parser-sensitive benchmark 至少手查 5 条样本。

### Phase 2: 做 pilot matrix

目标：用统一方法组在不同 benchmark 上看 failure surface 是否一致。

推荐方法组：

| 方法 | 用途 |
| --- | --- |
| no communication / shared only | 测通信必要性下界 |
| full info | 测模型解题能力上界 |
| oracle public facts | 测 public-state 表达上界 |
| naive all-to-all | 测过度共享和 leakage |
| old exchange | 对照旧自由文本讨论失败 |
| fact-only exchange | 测 message hygiene ceiling |
| direct admitted state | 测 LLM 直接生成 state 的边界 |
| source-ledger / role-router | 测 source/scope routing |
| priority + executor | 测 model preference + symbolic execution |
| oracle executor | 测 admission/packing 上界 |

建议规模：

- 每个 benchmark 先 `20-40` 个 task units。
- 优先 paired design，同一 case 覆盖多个 method。
- 只在 pilot 显示分辨率后扩到 full。

完成条件：

- 每个 P0 benchmark 至少出现一个能区分方法的非饱和指标。
- 若 fact-only 或 symbolic baseline 已接近 oracle，要明确标注 ceiling。
- 若 direct admitted state 系统性违反 scope/budget/rejection，要保存 case cards。

### Phase 3: 决定新 benchmark 是否成立

目标：判断我们是否真的需要构造自己的 benchmark。

新 benchmark 成立条件：

- 近场 benchmark 没有同时覆盖 `hidden/private information + recipient-specific scope + source/provenance + verification/rejection + downstream decision`。
- 现有 benchmark 的主要指标会把我们关心的 failure 压扁，比如只看 final accuracy 或只看 role assignment。
- 我们已有实验能提供可复用的 case family，而非临时拼题。
- symbolic / transparent baselines 可以很强，避免 benchmark 只测 prompt cleverness。
- 人工 gold 可审计，perturbation 可成对构造。

若成立，推荐新对象暂名：

```text
Hidden-State Admission Benchmark
```

核心 task：

```text
given role-private facts, source cards, scope rules, verification state, dependency edges, and a downstream decision,
decide which units may be admitted into each public/role state, which must be rejected or quarantined, and what final decision is justified.
```

首版规模：

- `12-24` 条 high-quality rows。
- 每条至少有 `base`, `scope_flip`, `missing_support`, `quarantine`, `candidate_anchor` 五类 perturbation 中的若干种。
- 先做 deterministic baselines、oracle executor 和 gold smoke，再跑模型。

## 本轮不做的事

- 不追求覆盖所有 agent benchmark。
- 不先跑 Docker-heavy full benchmark。
- 不把 leaderboard score 当主目标。
- 不继续扩 MATH / TypeCast 作为主 benchmark。
- 不用单一 Qwen2.5-14B 结果承载最终故事。
- 不把 prompt wording 小涨幅写成方法贡献。

## 决策门

本轮结束后要给出三个判断。

```text
J1: 现有 benchmark 中，哪一个最适合作为主尺度？
J2: hidden/state 两条线中，哪些失败是 benchmark ceiling，哪些失败是方法本身？
J3: 是否需要构造 Hidden-State Admission Benchmark；若需要，最小 v0 应该长什么样？
```

若 J1 有明确答案，优先在该 benchmark 上做 method pressure。

若 J1 没有明确答案，但 J3 成立，进入新 benchmark v0 builder。

若 J1 和 J3 都不成立，说明当前研究对象需要重新收窄，不能继续靠内部实验推进。

## 预期产物

- `docs/near_field_benchmark_table.md`
- `reports/20260618-near-field-benchmark-cartography.md`
- `experiments/<run-id>/README.md` for each claim-bearing contact or pilot
- `docs/evidence_register.md` 新增 benchmark audit evidence rows
- 若新 benchmark 成立：`data/hidden_state_admission_v0/README.md` 与 builder/scorer skeleton

## 一句话目标

把近场 benchmark 全部拉到桌面上，先看清楚尺度，再决定继续压 Hidden、推进 State，还是构造一把新的尺子。
