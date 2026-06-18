# HiddenBench Stage 2 External Pressure

## 核心判断

这个 idea 已经有形，但它的宽表述很容易撞车。外部文献已经覆盖了 hidden-profile 失败、共享信息偏置、结构化公共状态、verified shared context、schema-grounded state mutation。我们能保留的空间更窄：LLM sender 在 hidden-profile 对话中把私有事实加工成推荐、共享优势复述、或不精确事实；这个加工过程可以被拆开测量，并可由 fact-state admission protocol 直接压力测试。

当前最危险的 reviewer 反应会是：“这很直觉，hidden-profile 文献早说过要交换 unshared information；agent protocol 文献也早说过要结构化 shared state。”所以我们后续必须把贡献压在 LLM-specific decomposition 和跨 benchmark transfer 上，避免泛泛宣称“多智能体需要分享事实”。

## 已被外部占掉的空间

Hidden-profile 大现象已经被经典社会心理学占掉。Stasser & Titus 的 1985 论文已经指出，群体讨论会被 shared information 和已有偏好支配，并延续成员的扭曲图景，未能自动修正它。Lu, Yuan, and McLeod 的 2012 meta-analysis 总结了 `65` 个 hidden-profile studies，报告 common information 被提及显著多于 unique information，hidden-profile groups 比 full-information groups 更难找到解，且 unique-information coverage 和决策质量正相关。

HiddenBench 已经把这个现象搬到 LLM multi-agent benchmark。它明确说 HiddenBench 是 grounded in Hidden Profile paradigm 的 `65` task benchmark，并发现 15 个 LLM 中 multi-agent systems 仍然不能可靠整合 distributed information；communication 有帮助，但 distributed condition 和 full-information condition 之间仍有显著 gap。

PACT 已经占住了“agent 应该说什么 / public state-update”这个大方法方向。PACT 把 inter-agent communication 当作 public state-update problem，把 raw output 投影成 compact action-state record；它的 ablation 也强调 action、state、result 的完整 handoff。我们的 fact-state admission 如果只写成“把消息结构化”，会直接被 PACT 压住。

PatchBoard 和 DeLM 又从 shared state / verified context 侧面压过来。PatchBoard 用 schema-grounded JSON Patch mutation 代替自然语言 inter-agent dialogue，并由 deterministic kernel 校验 schema、role-specific write contracts 和 runtime invariants。DeLM 使用 shared verified context 和 task queue，让 agents 写回 compact verified updates，作为所有 agents 可见的 reusable problem state。

## 我们还剩下的空间

第一，HiddenBench 原文主要证明 multi-agent LLM 在 hidden-profile 上失败；我们的 Stage 2 进一步定位 sender public-message failure。Full65 clean subset 上，旧 exchange `23/55`，禁推荐 `28/55`，禁共享复述 `31/55`，fact-only `55/55`。这个 decomposition 比“模型没整合信息”更具体。

第二，PACT/PatchBoard/DeLM 强在 public-state architecture，但它们不一定解释 hidden-profile sender 为什么失败。我们的机制指向三种 sender-level 转换：preference compression、shared-advantage replay、private-fact transfer loss。这个 failure taxonomy 如果能稳定复现，就有比“结构化消息更好”更细的诊断价值。

第三，单独禁推荐解释不了 fact-only 在 clean subset 上的强信号。`no_recommendation_exchange` 已经把 recommendation leakage 从 `225/253` 压到 `12/253`，但 clean accuracy 只有 `28/55`；`no_shared_repeat_exchange` 把 shared overtalk 降到 `28/253`，但 clean accuracy 只有 `31/55`。fact-only 同时达到 `0/253` recommendation leakage、`4/253` shared overtalk、`198/253` private-exact messages，对应 clean `55/55`。这个组合信号是我们目前最能打的证据。

## 最危险的质疑

最强质疑一：fact-only 太像 oracle public facts。Sender 拿到的 private fact 本身就是任务构造里的隐藏事实；让模型“只报告私有事实”可能只是把 benchmark annotation 直接搬进 public channel。要回应这个质疑，必须测试 free-form sender outputs 经 admission/extraction 后能不能接近 fact-only，不能只测试手写强约束 prompt。

最强质疑二：local protocol 可能过于 prompt-specific。当前结果来自 Qwen2.5-14B、temperature `0`、project-local HiddenBench protocol。需要至少一个不同模型族，或至少一个不同 benchmark 形态，才能让 story 走出“这个 prompt 在这个 benchmark 上很好”。

最强质疑三：public-state protocol 已经被 PACT/PatchBoard/DeLM 覆盖。要避免撞车，我们不能把方法命名成 generic structured communication。更好的切口是 fact-state admission for hidden private evidence：只 admission 私有事实、来源和必要条件，延迟所有 recommendation / ranking / elimination。

最强质疑四：直觉太强。人类 hidden-profile 文献早知道 groups 要交换 unshared information；工程上也早知道 shared memory 需要 verified context。我们的论文故事必须展示：LLM agents 的失败不止是少说 unique facts，还会把 unique facts 转成 answer preference 或 shared-decoy rationale；这个转换可以被自动 audit，并且局部禁令无法修复。

## 下一步压力测试

第一步，做 admission version，先暂停继续加 prompt variant。保留 old exchange sender，让 sender 自由写；再加入 admission module，把消息拆成 admitted private facts、rejected recommendation、rejected shared-repeat、unsupported inference。Final decider 只看 admitted facts。如果这个接近 fact-only，就开始像方法。

第二步，把 PACT 当强 baseline。做一个 HiddenBench-PactStyle condition：sender 输出 `Action`, `State`, `Result`，或者直接跑 PACT-style projection，把 raw message 转成 action-state。若 PACT-style 已经接近 fact-only，我们的独立方法空间会变小；若 PACT-style 仍被 recommendation/shared-repeat 污染，fact-state admission 的必要性更强。

第三步，跨到 PACT-style split evidence 或 SOTOPIA-TOM。HiddenBench 能支持机制发现，但完整 story 需要另一种 communication-necessary task。目标应从追求更高分转成检验同一个 sender failure taxonomy 是否出现：推荐泄漏、共享/上下文复述、私有证据搬运不精确。

第四步，换一个模型族。Qwen2.5-14B 只能当 cheap diagnostic backbone。至少需要一个强 closed/open 模型做 small matrix：old exchange、fact-only、admission、PACT-style baseline。若方向不迁移，idea 退回 Qwen-specific protocol artifact。

## 当前可讲版本

保守版本：

```text
Hidden-profile tasks expose a sender-side public-state failure in LLM multi-agent communication. Free-form exchange does not merely omit private facts; it transforms them into preference-bearing and shared-decoy-heavy messages. Fact-state admission separates private evidence transfer from premature recommendation and yields a measurable recovery on HiddenBench.
```

中文人话版本：

```text
这个现象的直觉大家都知道：hidden-profile 要交换私有信息。我们现在能说的更窄：LLM sender 在自由对话里不会稳定地把私有事实搬进公共状态，反而会把它加工成推荐、共享诱饵理由或不精确转述。这个加工过程可以拆开测，单独禁推荐或禁共享复述都不够，必须先做 fact-state admission。
```

## Sources

- HiddenBench: https://arxiv.org/html/2505.11556v2
- Stasser & Titus 1985: https://www.uni-muenster.de/imperia/md/content/psyifp/aeechterhoff/vorlesungkommunikation/stasser_titus_unsharedinfogroupdisc_jpsp1985.pdf
- Lu, Yuan & McLeod 2012 meta-analysis: https://journals.sagepub.com/doi/10.1177/1088868311417243
- PACT: https://arxiv.org/html/2606.05304v1
- PatchBoard: https://arxiv.org/html/2605.29313v1
- DeLM: https://arxiv.org/html/2606.10662v1
