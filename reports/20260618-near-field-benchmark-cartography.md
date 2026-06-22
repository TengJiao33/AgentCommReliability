# 近场 Benchmark 地图判断报告

日期：2026-06-18

## 核心判断

benchmark 问题现在确实是主瓶颈。项目已经有不少机制信号：HiddenBench 显示通信必要性，PerspectiveGap 显示角色边界和路由压力，State Admission 显示 source/scope/rejection/evidence sufficiency 的断点。但这些信号还没有被同一把外部尺子统一测量。

现在最合适的动作是做 benchmark cartography 和小样本 pilot matrix。全量刷近场 benchmark 会消耗大量工程时间，也未必回答主问题；完全不拉外部 benchmark 又会让研究继续在内部 packet 里循环。当前应先把每个 benchmark 能测什么、不能测什么、是否已经 ceiling、是否支持新 benchmark 缺口写清楚。

## 做了什么

我新增了两个文档：

- `docs/near_field_benchmark_cartography_plan.md`
- `docs/near_field_benchmark_table.md`

并把这两个文档挂进 `docs/active_research_map.md`，作为当前 active evidence surface 的一部分。

外部 benchmark 覆盖了 HiddenBench、PerspectiveGap、PACT-style split evidence、Silo-Bench、AgentLeak、SOTOPIA-TOM、TeamBench、DeLM、CICL、AgentDojo、OSWorld、AppWorld、WebArena、TheAgentCompany 和 tau-bench。表里每个对象都按同一组轴检查：hidden/private information、recipient-specific scope、source/provenance、verification/rejection、downstream decision、budget/constraint、本地状态和 claim 边界。

## 关键证据

HiddenBench 是当前最干净的通信必要性底座。已有 full65 显示 `shared_only` 只有 `1/65`，`full_info` 是 `59/65`，`oracle_public_facts` 是 `56/65`，旧 `exchange_then_decide` 是 `24/65`。这支持一个很清楚的判断：任务需要私有信息移动，普通自由文本讨论没有稳定把私有事实转成可用公共状态。

HiddenBench 的边界同样清楚。Stage 2/3/4 中 fact-only 或 blind-minimal 已经接近 oracle；继续在这个 benchmark 里追 prompt 小变体，很可能被 ceiling 压扁。HiddenBench 接下来更适合提供自然 case seeds，而不适合独自承担 source/scope/rejection/admission 的完整 claim。

PerspectiveGap 是当前最好的 role-specific routing 外部镜片。本地 220-row contact 显示 oracle 是 `220/220`，all-to-all 是 `0/220`，no-distractor all-to-all 仍是 `0/220`。这说明它真正测角色边界，不只是测能否避开明显 distractor。

PerspectiveGap 的 source-ledger 系列给出了更贴近方法的信号。rotated20 中，同一 fragment 文本的 recipient scope 被旋转后，旧 role-list 预测崩掉；14B source-ledger 恢复到 coverage `0.854`，但 budget_pass 只有 `0.225`。budget compiler 后 strict 到 `12/40`，precision 和 budget_pass 到 `1.000`。这支持“模型读通信状态，系统执行边界约束”的机制切口。

State Admission 是内部机制显微镜。V1 中 direct Qwen2.5-14B 是 `0/40` strict，coverage `1.000`，precision `0.4025`，global budget pass `0`；priority + executor 可以到 `28/40` 或离线 recompile `33/40`。ledger-first hidden-unit 只有 `1/40` 和 utility `0.0409`，说明 hidden admission-unit construction 是断点。

State Admission V2 又把问题压到 evidence sufficiency。visible-facts-first smoke9 中，模型列出的可见事实集合很准：visible precision `0.954`，visible recall `0.986`，但 downstream_ok 只有 `0.333`，扰动行 downstream_ok 为 `0`。这提示当前失败更接近证据充分性判定失败：模型看到可用事实后，仍会把背景事实或部分支撑当成足够证据。

## 外部压力

Silo-Bench 很适合补 HiddenBench 的 ceiling 问题，因为它测 distributed state integration 和 communication-reasoning gap。但它不天然测 source/scope/rejection。

AgentLeak 和 SOTOPIA-TOM 说明 privacy、internal-channel leakage、public/private channel policy 已经是外部热点。它们对我们形成压力：不能只看 final answer，也不能把“不给不该看的信息”当成一个内部喜好指标。

TeamBench 是最强工程级 role separation 压力，但当前 A800_2 无 Docker、Podman、Singularity、Apptainer、rootlesskit、newuidmap/newgidmap。它必须保持 blocked 状态，不能报告官方 OS-enforced role separation 结果。

DeLM、PACT、CICL 都是强 collision pressure。PACT 已经占住 action-state public communication；DeLM 已经占住 shared verified context 和 verified updates；CICL 已经占住 decision-critical context selection 和 typed memory cards。我们的空间不能写成“结构化公共状态”或“选择有用上下文”，必须压到 recipient-scoped source/scope/rejection/evidence sufficiency 的交叉处。

## 机制解释

目前最清楚的研究对象可以写成：

```text
private or role-scoped facts do not merely need to be communicated;
they need to be admitted into the right public or role state
with source, scope, verification, rejection, and sufficiency constraints
before downstream commitment.
```

Hidden 线已经告诉我们：通信必要性存在，自由文本讨论会污染，fact-only 会接近 oracle。

PerspectiveGap 告诉我们：信息路由不能靠内容语义猜测；source/scope 状态需要成为显式控制面。

State 线告诉我们：直接让 LLM 写 admitted state 会过度承认；让模型给 priority、让规则层执行合法性更稳；真正难点在 admission-unit construction 和 evidence sufficiency。

这三条线合在一起，才像一个可继续推进的 benchmark story。单独任何一条都不够。

## 边界

这份 cartography 不是模型实验结果。它是研究设计产物，主要价值是防止下一轮盲目跑 GPU。

表里很多 P1/P2 benchmark 目前只有 paper/source-level audit，还没有本地 fixture。Silo-Bench、AgentLeak、SOTOPIA-TOM 需要后续 contact 才能进入 claim-bearing 状态。

State Admission 仍是 synthetic / semi-synthetic。它暴露机制断点，但不能当外部有效性证据。

## 决策

我现在会把下一步压成四件小事。

1. 从 HiddenBench 抽 `8-12` 个 exchange fail / oracle public facts succeed 的自然 case，作为 Hidden-State Admission v0 seeds。
2. 对 PerspectiveGap stratified20 / source-ledger runs 写 case cards，区分 missing-needed、over-share、wrong-recipient、budget-overrun、distractor leak。
3. 把 State V2 改成 evidence-slot completeness scorer，让每个候选答案先声明必要支撑槽位和排除槽位。
4. 做 PACT-style split-evidence 的 10-20 row pilot preflight，先查 gold/parser/final-answer surface。

## 本轮结论

需要继续拉 benchmark，但方法要克制。最有价值的路线是先做 benchmark 地图和小样本诊断矩阵，再决定是否构造 `Hidden-State Admission Benchmark`。

当前缺口已经比较清楚：近场 benchmark 里还没有一个对象同时测 hidden/private facts、recipient-specific source/scope、verification/rejection、evidence sufficiency 和 downstream decision。这个缺口值得被认真构造，但 v0 应该小而硬，先做 `12-24` 行，不做大排行榜。
