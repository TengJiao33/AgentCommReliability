# Skill-Guided State Admission V2 Preflight

日期：2026-06-18

## 核心判断

State Admission 现在是一个活的机制切口，但 V1.1 不能继续靠 prompt 微调推进。V1.1 已经说明两个事实：LLM 直接生成 admitted state 会破坏预算和拒绝边界；priority 加 deterministic executor 可以恢复合法性。它同时暴露了一个更强 caveat：当 admission units 被显式给出时，强符号 `group_density_global` baseline 已经达到 `32/40` strict 和 `0.9666` utility ratio。

下一步应做 V2 preflight，并优先于扩 V1.1 GPU。V2 的核心问题应收窄为：模型能否从 source ledger、recipient scope、dependency、verification 和 downstream task structure 中构造可执行 admission units；executor 能否把这些 candidate units 编译成合法的 role-local admitted state；这个 admitted state 是否带来 downstream decision 或 action proxy 的收益。

## 证据链

V1.1 direct admission 暴露了 `local usefulness versus admissibility`。Qwen2.5-14B default prompt 覆盖了所有 oracle 非空角色，但也填满了所有 oracle 空角色，strict `0/40`，global budget pass `0.0000`。budget-first prompt 降低过度承认，但丢掉必要覆盖，strict 仍是 `0/40`。证据在 `reports/20260618-state-admission-v1-qwen25-14b-pressure.md` 和 `experiments/20260618-local-state-admission-v1/README.md`。

Priority executor 说明合法执行面可以被程序层稳定控制。Qwen2.5-14B priority 加 `pair_group_primary` 离线重编译达到 `33/40` strict、global budget pass `1.0000`、closure violations `0.0000`；Qwen2.5-7B `fallback_required` 达到 `31/40` strict，也保持预算和 closure 干净。证据在 `reports/20260618-state-admission-v1-priority-executor-pressure.md` 和 `reports/20260618-state-admission-v1-priority-7b-replication.md`。

Ledger-first run 把断点压到了 unit construction。不给 bundle/group 表，只给 source ledger、budget、utility/hint 和 payload，Qwen2.5-7B 只有 `1/40` strict、utility ratio `0.0409`、closure violations `1.6750`。本地 ledger oracle 是 `40/40`，说明 compiler 上界存在；模型侧掉在从 source 组成完整 bundle 或 cross-role unit。证据在 `reports/20260618-state-admission-v1-ledger-hidden-unit-pressure.md` 和 `experiments/20260618-a8002-state-admission-v1-ledger-full40-qwen25-7b/README.md`。

HiddenBench 和 PerspectiveGap 给 V2 提供外部任务压力。HiddenBench full65 中 `shared_only` 是 `1/65`，`oracle_public_facts` 是 `56/65`，旧 exchange 是 `24/65`，fact-only 和 blind-minimal 是 `57/65`；PerspectiveGap stratified20 中 14B 比 7B coverage 高 `0.1722`，但 distractor leak 也高 `0.4000`。它们说明任务确实需要信息移动，也说明 routing/admission 的评价必须同时看 coverage、boundary precision、leak 和 downstream decision。

## 外部压力

DeLM 已经占住 shared verified context 和 task queue 方向。它的对象是全员共享的 verified progress substrate，压力点是不要把我们的贡献写成 shared context update。V2 应强调 recipient-specific local state：同一证据对不同角色有不同准入状态。

CICL 已经占住 decision-aware context selection、memory cards 和 budget packing。它的压力点是不要把 V2 做成 single-agent utility packing。V2 需要 role scope、source owner、dependency closure 和 cross-role budget conflict，让 CICL-style context selector 成为明确 baseline，避免只作为模糊邻居。

PerspectiveGap 已经占住 role-fragment assignment benchmark。它的压力点是不要把 role routing benchmark 当成贡献。V2 可以复用或扰动 PerspectiveGap fragments，但贡献必须落在 source/scope/verification/admission-unit construction，而非原始 role assignment。

ProvenanceGuard 已经占住 source-aware factuality verification。它的压力点是不要把 V2 写成 answer attribution verifier。我们的判断发生在答案生成前：某条 source-scoped evidence 是否能进入某个 recipient 的 local context。

外部核对入口：`https://arxiv.org/abs/2606.10662`、`https://arxiv.org/abs/2606.08151`、`https://arxiv.org/html/2606.08878v1`、`https://arxiv.org/abs/2606.18037`。

## A/B/C Story Gate

A 是 direct admitted-state generation 或 free-form shared context。模型直接输出每个 role 的 source cards，或者所有角色读同一个 shared context。

B 是有用性和准入合法性的错配。模型能识别局部有用 evidence，但不会稳定执行 recipient scope、empty-role rejection、dependency closure、fallback priority 和 global budget。V1.1 direct runs 支持这一点，ledger-first run 进一步说明 unit construction 是独立断点。

C 应是分层 admission protocol。第一阶段提出 candidate admission units，第二阶段 executor 验证 source/scope/dependency/budget，第三阶段输出 admitted state 和 rejection certificate，最后接 downstream decision 或 action proxy。

M 是 strict、required coverage、boundary precision、global budget pass、closure violations、reject recall、utility ratio 和 downstream decision score。

D 是失败模式诊断。成功时应看到 direct model 的预算/empty-role/closure 错误下降，同时 downstream score 不低于 shared context 或 CICL-style selector；失败时应能区分 unit construction 失败、priority 排序失败、executor policy 失败和 downstream evaluator 失败。

## V2 Preflight Contract

Purpose：判断 role-scoped evidence admission 是否比 shared verified context、decision-context packing 和 raw role routing 更能控制 source/scope/dependency 下的局部上下文。

Unit：packet row，其中每行包含多个 roles、source-scoped evidence、recipient eligibility、dependency edges、verification state、global budget 和 downstream decision proxy。

Primary contrast：two-stage unit-proposal plus executor 对比 direct admitted cards、shared-context baseline、CICL-style utility packing、PerspectiveGap role-assignment baseline、symbolic group-density baseline。

Secondary contrasts：exposed-unit priority、ledger-first source priority、oracle unit construction、oracle executor、source/scope perturbation、verification-gate ablation、no-budget ablation。

Success signal：two-stage protocol 在合法性指标上接近 oracle executor，并在 downstream decision proxy 上明显优于 shared-context 和 direct cards；同时 strong symbolic baseline 不能近似吃满任务。

Failure signal：group-density 或 CICL-style baseline 接近 oracle；hidden-unit two-stage 仍接近 ledger-first `1/40` collapse；downstream decision 与 admitted-state metrics 脱钩；source/scope perturbation 不改变模型准入行为。

Invalidation conditions：builder 合成 utility 成为唯一 reward；gold recipient 由 prompt 泄露；dependency closure 人工过强且人不可解释；parser/JSON repair 决定主要差异；shared-context baseline 没有认真调优；downstream proxy 只重复 scorer 标签。

Expected artifacts：`scripts/build_state_admission_v2_packet.py`、`scripts/score_state_admission_v2.py`、`scripts/run_state_admission_v2_*`、`experiments/20260618-local-state-admission-v2-preflight/README.md`、`reports/20260618-state-admission-v2-packet.md`。

## Packet Design Requirements

V2 必须包含 same-content source/scope perturbation。同一 evidence text 在不同 source owner、recipient scope 或 verification state 下，gold admitted recipients 应改变。否则它会退化成 semantic relevance selection。

V2 必须包含 downstream decision proxy。每个 row 要能检查 admitted evidence 是否支持一个最终 decision、action 或 prompt-writing outcome。只看 source-card strict 会让故事困在合成 scorer 里。

V2 必须包含 real unit hints。Admission units 应来自 task structure，例如 action precondition、option blocking fact、tool result dependency、case field schema 或 role-local deliverable requirement。不要再完全依赖 builder 注入的 pair-group utility。

V2 必须有强 baseline。至少包括 shared verified context、decision-aware card packing、role-fragment oracle/heuristic、source-level density、exposed-unit priority、symbolic group-density、oracle unit construction 和 oracle executor。

V2 必须有 reject certificate。评分不只看选中的 cards，也看应拒绝 source 是否被拒绝、拒绝原因是否和 source/scope/verification/budget 对齐。

## 不该马上做的事

不要再扩 V1.1 prompt sweep。`fallback_required` 已经说明 schema 能改善 7B strict，但没有解决 hidden unit construction 和 downstream validity。

不要把 V1.1 写成优化方法。`group_density_global` 目前 utility 高于 model priority，优化 claim 会被强 baseline 直接压住。

不要只跑 Qwen2.5-14B。它可以做 debug backbone，但任何 claim-bearing result 至少需要 7B/14B 对照，之后再接一个更强 open 或 closed frontier model。

不要把 MATH operator lifecycle 当主证据。它是机制显微镜，可以帮助解释错误类型转换，但不能承担 benchmark-first 的主 claim。

## 下一步

下一步的最小可执行动作是本地构造 V2 packet sketch，不上 GPU。先写 `experiments/20260618-local-state-admission-v2-preflight/README.md`，列出 8 到 12 个 concrete rows，每行人工检查 source/scope perturbation、dependency closure、downstream proxy、baseline oracle 和 rejection certificate。只有这个 packet audit 过关，才值得写 runner 或启动 A800。

如果 V2 packet audit 发现 downstream proxy 仍然只是重复合成标签，方向应回退到 HiddenBench fact-state admission 或 PerspectiveGap role-routing evaluation，不应继续造 State Admission 合成包。
