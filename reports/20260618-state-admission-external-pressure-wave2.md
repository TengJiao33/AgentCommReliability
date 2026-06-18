# State Admission External Pressure Wave 2

## 核心判断

这一轮外部压力把宽泛 story 继续压掉了。现在可守的对象应当收窄到 role-scoped evidence/state admission：给不同接收角色承认哪些 source-scoped evidence，并在 dependency、verification、visibility、global budget 下生成可执行的 admitted state 和 rejection certificate。

最强邻居是 DeLM 和 CICL。DeLM 已经占住 “shared verified context + admission-time verification” 的大方向；CICL 已经占住 “decision-critical context selection under budget” 的大方向。我们的空间还在，但只能靠 recipient-specific scope、source-level routing、legal executor、empty-role/reject 评测和强符号 baseline 压出来。

## 检索入口

本轮从 `D:\develop\ArXiv_Daily_Digest` 进入，已执行 `git pull --ff-only`，结果是 `Already up to date.`。重点扫 `2026-W25` 和 `2026-W24` 的 `agent-skills-harness`、`multi-agent-consistency`、`agent-policy-optimization`、`factuality-rule-guided-apps`，用 `state/context/tool/provenance/access/budget/verification/shared/admission` 等词做候选队列，再读最危险候选的全文关键段落。

相关本地入口：

- `D:\develop\ArXiv_Daily_Digest\data\multi-agent-consistency\2026-W25\papers.jsonl`
- `D:\develop\ArXiv_Daily_Digest\data\agent-skills-harness\2026-W25\papers.jsonl`
- `D:\develop\ArXiv_Daily_Digest\data\agent-skills-harness\2026-W24\papers.jsonl`
- `D:\develop\ArXiv_Daily_Digest\data\factuality-rule-guided-apps\2026-W25\papers.jsonl`

## 碰撞审计

| Paper | Object | Mechanism | Experiments | Claim | Overlap | What it pressures | How we differ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DeLM: Decentralized Multi-Agent Systems with Shared Context | 多 agent 共享问题状态 | shared verified context、task queue、compressed gists、admission-time verification | SWE-bench Verified、LongBench-v2、OOLONG | 通过 verified shared context 降低中心控制瓶颈，提升多 agent test-time scaling | partial overlap, strongest | 压力最大：它已经把 “admit verified updates into shared context” 讲清楚了 | 我们研究 recipient-specific local admission：不同角色看到不同 source/scope；核心指标是 source legality、empty-role precision、reject recall、预算和 closure |
| CICL: Decision-Aware Memory Cards | tool-using agent 的上下文选择/压缩 | context graph、八字段 schema、utility scoring、memory cards、budget packing | SWE-bench file retrieval、synthetic context suites、RepoBench-R | 选择会改变 action 的证据，并在 budget 下打包成 cards | partial overlap | 压 utility/context selection：只靠 synthetic utility 站不稳 | 我们要测 role-scoped admission，不只测单 agent action context；但应借鉴 action-shift 或 downstream task signal |
| ProvenanceGuard | MCP-grounded answer 的 source-attribution factuality | claim decomposition、claim-to-source routing、NLI/support、attribution block/repair | 281 medical MCP traces、held-out claims、source-conflation probes | factuality verifier 必须区分 pooled support 与 source ownership | useful prior / partial overlap | 压 source-aware framing：source ownership 已有人系统化 | 我们在 admission 前决定 source 能否进入角色上下文；ProvenanceGuard 在 answer 后验证 claim attribution |
| SAMOS / Securing MCP-based Agent Workflows | MCP workflow data leakage | gateway-level information-flow control、tool annotations、session taint tracking | GitHub MCP leakage case study | MCP agent workflow 需要 gateway enforcement | background neighbor | 压 generic compiler/gateway 叙事 | 我们处理 evidence admission 和 multi-role local context；对象并非工具级 IFC 或 confidential data leak policy |
| SCR / SkillReact skill-composition papers | agent skill ecosystems 的组合风险 | path-level capability flow、trust transfer、authorization confusion、install-time checks | SCR-Bench、ClawHub skill pairs、composition ablations | 单个 skill 安全不代表组合路径安全 | useful prior | 压 “gating/permission” 泛化叙事 | 我们的对象是 evidence/state admission，并非 skill capability union；但 rejection certificate 可以借鉴 path-level evidence reporting |

## 对我们的直接压力

第一，DeLM 逼我们别再讲 “shared verified context”。这个词组几乎已经被它占住。我们可以引用它做强 prior，然后明确转向 local role-scoped admitted state：shared context 是全员可见的通信 substrate；我们的 state card 是面向特定 recipient 的 evidence contract。

第二，CICL 逼我们别只讲 “选有用证据”。它已经把 decision-aware context、utility、budget packing、memory card 做成了完整故事。我们的 benchmark 需要展示 context selection 在多角色 source/scope 下会出现额外 failure：某个 source 对 A 合法、对 B 不合法；某个 pair-group 对全局 utility 高，但会关掉另一个角色的必要 bundle；某个 rejected source 需要被明确记录。

第三，ProvenanceGuard 逼我们把 source 讲准。source-aware 已经有成熟工作，claim-to-source attribution 也很系统。我们的贡献要落到 admission-time routing：在答案生成前，决定哪条 source 能以什么 visibility 进入哪个角色上下文；评分时看 role/source/visibility/reject，而不只看最后 claim 是否归因正确。

第四，SAMOS 和 skill-composition work 把 “compiler/gateway/least privilege” 这类包装压得很近。我们不能用 generic compiler 当新意。可守的新意是 admission executor 的对象更细：source-scoped evidence bundles、recipient scope、dependency closure、global budget、fallback priority、rejection certificate。

## 对实验设计的要求

State Admission V1.1 现在只够当机制探针。下一版要补三个外部压力缺口。

1. DeLM 对照：加入 shared-context baseline，让所有角色读同一个 verified gist/card，再和 role-local admission 比。
2. CICL 对照：加入 decision/context utility baseline，至少有 action-shift 或 downstream decision proxy，避免 utility 完全由 builder 规定。
3. Security/context 对照：加入 source/scope perturbation，同一 evidence 内容换 source owner、recipient visibility 或 dependency，观察 direct model、symbolic baseline、priority executor 的差异。

## 当前 story 边界

现在可说：我们发现 LLM 对 evidence utility 有偏好信号，但直接生成 admitted state 容易破坏 budget、scope 和 rejection；把偏好输出和合法执行拆开，在 State Admission V1.1 上跨 14B/7B 保住合法性，并把错误集中到 priority 质量。

现在还不能说：我们提出了通用多 agent 通信框架、通用 context selection 方法、通用 source-aware factuality verifier、或优于规划基线的优化方法。

下一步最有价值的压力对象是 “hidden-unit state admission”：不再显式给 pair group 表，让模型从 source ledger/trace schema 中提出 admission units；同时加入 DeLM-style shared context、CICL-style decision context、group-density symbolic baseline 三个外部参照。
