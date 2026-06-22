# A 会论文模板锚点地图

Snapshot date: `2026-06-18`.

## 核心判断

当前最适合本项目的模板应定位为三类 A 会写法的组合，单一冲榜论文只能作为旁支参考：

1. test-time system method：同一个模型下，通过新的推理/交互/反思协议稳定超过 direct prompting。
2. LLM + deterministic executor：模型负责语义分解或候选生成，程序负责执行、合法性和约束。
3. communication / agent evaluation：把一个被忽视的 agent failure surface 定义成可测对象，用强 baseline、cost、failure taxonomy 和 oracle/control gap 支撑贡献。

这三类模板合起来，最贴近我们现在的 `source-scoped evidence admission + compiler/executor + role-specific routing` 方向。

细读版模仿手册见 `docs/a_conference_imitation_close_reading.md`。

## 第一组：最像我们方法形状的模板

| 模板论文 | 会议信息 | 可借鉴的论文模式 | 对本项目的映射 |
| --- | --- | --- | --- |
| ReAct: Synergizing Reasoning and Acting in Language Models | ICLR 2023 notable top 5% | 把两个原本分开的能力合成一个 test-time protocol，并用 reasoning-only / acting-only / ReAct 做组件对照。 | 我们可以把 free-form exchange、role routing、source-scoped admission、compiler execution 拆成组件对照。 |
| PAL: Program-aided Language Models | ICML 2023 | LLM 只负责把自然语言问题翻译成 runnable intermediate program，求解交给 interpreter。 | 这是 `LLM proposes units, compiler admits state` 的强模板。我们应学习它如何强调“职责分工”，避免退化成纯 prompt trick。 |
| Decomposed Prompting | ICLR 2023 | 复杂任务拆成子任务，并允许子任务交给专门 prompt、模型或 symbolic function。 | SSEAC 可以写成 role/source/scope/evidence admission 的 decomposition framework。 |
| Chain-of-Verification | ACL Findings 2024 | 通过 draft -> verification questions -> independent answers -> final response 的协议减少 hallucination。 | 我们的 verification/admission 可以类似写成“先生成候选，再独立验证/准入，再生成公共状态”。 |
| Reflexion | NeurIPS 2023 | 不训练模型，用 verbal feedback 和 memory 改善 agent 行为，并做反馈来源/记忆方式 ablation。 | 适合作为 test-time wrapper 论文模板，说明 A 会接受同模型 inference-time system result。 |
| Tree of Thoughts | NeurIPS 2023 | 将 token-level left-to-right generation 扩展成 thought-level search，并用需要搜索的任务验证。 | 我们可以把 evidence unit / admitted state 当成比 free-form message 更稳定的中间对象。 |

## 第二组：最像我们实验表的模板

| 模板论文 | 会议信息 | 可借鉴的实验形状 | 对本项目的提醒 |
| --- | --- | --- | --- |
| ChatEval | ICLR 2024 | 多 agent debate 用在人类评价模拟，比较 single-agent 与 multi-agent communication strategies。 | 可以借鉴 agent-role / debate strategy / ablation table，但要避免只讲“多 agent 更好”。 |
| Improving Multi-Agent Debate with Sparse Communication Topology | EMNLP Findings 2024 | 在 MAD 里系统改变 communication topology，同时报告 performance 和 compute cost。 | 这是我们处理 communication graph / source visibility / budget 的近邻模板。 |
| AgentBench | ICLR 2024 | 先定义 agent evaluation gap，再建 benchmark、跑多模型、给 failure reasons。 | 如果我们走 benchmark-paper 或 diagnostic-paper，它是强模板。 |
| SWE-bench | ICLR 2024 oral | 用真实任务构造 evaluation framework，重点显示现有模型能力不足和失败类型。 | 如果 HSA / PerspectiveGap 扩成 benchmark contribution，可学习其真实任务、可执行 evaluator 和 failure taxonomy。 |
| MMLU-Pro | NeurIPS 2024 Datasets & Benchmarks | 旧 benchmark 饱和后，构造更难、更稳定、更能区分模型的新 benchmark。 | 如果我们主张现有 communication benchmarks 测不到 admission/scope，应学习它如何证明旧 benchmark 不够区分。 |
| ToolLLM / ToolBench | ICLR 2024 | 数据构造、系统方法和自动 evaluator 一起出现，围绕 tool-use 能力做完整 benchmark-method package。 | 若我们把 PerspectiveGap/HSA/SSEAC 打包成 framework，需要学习这种“数据 + evaluator + method”的结构。 |

## 最推荐对标的 5 篇

| 优先级 | 论文 | 为什么最值得当模板 |
| ---: | --- | --- |
| 1 | PAL | 最贴近我们的 LLM/compiler 职责分工。 |
| 2 | ReAct | 最适合学习如何讲 test-time protocol 的组件增益。 |
| 3 | Decomposed Prompting | 最适合学习 modular prompt/system decomposition。 |
| 4 | Sparse Communication Topology | 最贴近 multi-agent communication baseline ladder 和 cost 对照。 |
| 5 | AgentBench 或 SWE-bench | 最适合学习如何把 failure surface 升格成 evaluation object。 |

## 我们应该模仿的结构

引言结构可以按这个顺序写：

1. 现有 multi-agent communication 常把消息当自由文本上下文追加。
2. 在 role-specific / private-information / budgeted routing 设置下，自由文本会同时引入漏收、乱收、泄漏和过预算。
3. 关键对象应从 message transcript 转成 source-scoped admissible evidence state。
4. 我们提出一个 test-time system：模型生成候选 evidence units 和 priorities，deterministic compiler 执行 source/scope/budget/rejection 约束。
5. 实验用 same-backbone、same-budget、transparent heuristic、direct prompt、source-ledger、oracle/control gap 来验证机制。

主实验表应该按这个顺序组织：

| 行类型 | 必须出现的条件 |
| --- | --- |
| direct baseline | official/direct prompt、free-form exchange |
| prior mechanism | role-list、source-ledger、prompt-writing direct |
| transparent baseline | greedy utility / density / shared-only / all-scoped |
| ours decomposition | candidate generation、compiler only、full SSEAC |
| oracle/control | oracle admissible、oracle assignment-to-prompt、full-info |
| diagnostics | coverage、precision、leakage、budget pass、cost、downstream strict |

## 不能照搬的地方

这些模板有些依赖 GPT-4、ChatGPT 或 closed-source API。我们可以引用它们的论文形状，但主表应优先建立在 same-backbone comparison 上。闭源 frontier score 可以放在参考列或附录，不能当作当前主张成立的唯一 gate。

有些模板主要报告最终 task accuracy。我们的任务必须同时报告 evidence discipline：coverage、precision、leakage、budget pass、extra admitted cards、forced commitment 和 downstream strict。只看最终答案会奖励全收证据或 scorer artifact。

有些模板把 prompt protocol 当主贡献。我们的更强位置是 protocol + compiler/executor + evaluator 三者闭合。若只写 prompt wrapper，PG40 的 transparent heuristic 和 HSA 的 all-scoped baseline 会直接削弱贡献。

## 参考入口

| 论文 | URL |
| --- | --- |
| ReAct | https://openreview.net/forum?id=WE_vluYUL-X |
| PAL | https://proceedings.mlr.press/v202/gao23f.html |
| Decomposed Prompting | https://openreview.net/forum?id=_nGgzQjzaRy |
| Chain-of-Verification | https://aclanthology.org/2024.findings-acl.212/ |
| Reflexion | https://papers.nips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html |
| Tree of Thoughts | https://openreview.net/forum?id=5Xc1ecxO1h |
| ChatEval | https://openreview.net/forum?id=FQepisCUWu |
| Sparse Communication Topology | https://aclanthology.org/2024.findings-emnlp.427/ |
| AgentBench | https://openreview.net/forum?id=zAdUB0aCTQ |
| SWE-bench | https://openreview.net/forum?id=VTF8yNQM66 |
| MMLU-Pro | https://papers.nips.cc/paper_files/paper/2024/hash/ad236edc564f3e3156e1b2feafb99a24-Abstract-Datasets_and_Benchmarks_Track.html |
| ToolLLM | https://openreview.net/forum?id=dHng2O0Jjr |
