# State admission 全文撞车审计第一波

## 核心判断

第一波真正压力后，我的判断更清楚：大词已经被占得很满，窄切口还活着。我们不能卖“公共状态更新”“共享 verified context”“通信省 token”“source-aware factuality”“decision-aware context cards”这些宽 claim；这些分别会撞 PACT、DeLM、DALA、ProvenanceGuard、CICL。

可活的 claim 要收窄到这里：多 agent 系统需要一个 recipient-specific state admission layer，在信息进入某个 agent 上下文前，根据 source、scope、recipient、budget、dependency、verification 状态决定准入。这个 claim 的关键现象应当是：同一段内容在 source/scope 改变后，正确接收者和准入策略会改变；模型容易按内容语义乱发，程序化 admission compiler 能守住硬边界。

## 判重表

| Paper | Object | Mechanism | Experiments | Claim | Overlap | 压力 | 我们怎么避开 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PACT | inter-agent message content | raw output -> ACTION/STATE/RESULT public message | split-evidence HotpotQA/2Wiki, sequential pipeline, OpenHands, SWE-agent | 共享历史应只保留 compact action-state | partial, broad public handoff 近直撞 | “what should agents say”“public action-state” 已被占 | 不讲通用 action-state；讲 recipient/source/scope 准入和同内容 scope perturbation |
| DeLM | decentralized coordination | shared verified context + task queue + admission-time verification | SWE-bench Verified, LongBench-v2, OOLONG | agents 通过 compact verified updates 协调 | partial, shared verified state 近直撞 | “shared verified context”“admission-time verification” 已被占 | 不讲全局共享上下文；讲每个 recipient 的可见性和预算约束 |
| CaMeL | prompt injection security | trusted control/data flow extraction + capability enforcement | AgentDojo security tasks | untrusted data cannot affect unsafe program/data flow | useful prior / security analogue | “programmatic enforcement”“capability/data-flow gate” 已有强安全版本 | 不讲安全保证；借鉴 enforcement 语言，落在 multi-agent evidence routing |
| PerspectiveGap | role-specific information routing | benchmark schema + deterministic scorer | 110 scenarios, assignment and prompt-writing | orchestration prompting is under-evaluated | partial, benchmark object 近 | role-fragment routing benchmark 已被占 | 我们作为扩展压力：source/scope perturbation、budget、compiler，不 claim 原始 benchmark |
| HiddenBench | distributed information integration | Hidden Profile + structured exchange protocol | 65 tasks, full/hidden profile, ablations | agents fail to surface unshared facts | partial | “latent information asymmetry”“surface unshared evidence” 已强 | 不讲一般 distributed-info exploration；讲 source/scope-authorized admission |
| DALA | communication bandwidth | value-density bids + auction + budget | 7 reasoning/code benchmarks, ablations | communication is scarce, strategic silence helps | partial | “budgeted communication / scarcity / auction” 已被占 | 不讲 budget 本身；budget 只是 admission 约束之一 |
| CICL | decision-critical context | utility scoring + typed memory cards + budget packing | SWE-bench retrieval, synthetic removal, compression | context should be ranked by decision utility | partial | “decision-aware context cards / budgeted evidence packing” 已被占 | 不讲通用 context utility；讲 role-scoped source admission |
| ProvenanceGuard | source-aware factuality | claim decomposition + source router + NLI + repair | MCP medical traces, conflation probes | source attribution is independent factuality axis | partial | “source-aware verification / source attribution” 已被占 | 不做 answer verifier；source 是准入权限和 recipient routing 的输入 |
| Trust Between AI Agents | inter-agent trust | costly verification against memoryless baseline | survival game, trust formation/breakage/recovery | trust can be measured by verification spending | background/useful prior | verification budget 和 teammate reliability 语言被占 | 可借 verification-cost idea；不做 trust lifecycle claim |
| MINT | benign misinformation propagation | misinformation injection + group composition + voting/consensus | CWQ/Ethics/WinoGrande, Llama/GLM | robustness depends on exposure, group, protocol | background/useful prior | private evidence pollution 会被它压成 exposure 子问题 | 把污染降级为 admission failure 的一种后果 |
| WhoFlips | answer stability | two-stage wrong-argument challenge | MMLU, attribution/source/length/MAXFLIP | correct answers can flip under argument-only challenge | background/useful prior | “source/argument influence” 已有漂亮协议 | 可学两阶段扰动设计；不讲 answer-flip 主线 |

## 真正危险的地方

第一危险是 PACT。它已经把“agent 输出进入共享历史前要被投影”讲得很像。我们如果说“通信前要过滤/压缩/结构化”，很容易显得像 PACT 的换壳。避法是把对象从 shared message content 改成 recipient-specific admission decision：同一 source 对 A 可见，对 B 不可见，或者对 A 要验证后可见，对 B 直接 reject。

第二危险是 DeLM。它已经有 shared verified context 和 admission-time verification。我们如果说“agent 共享 verified updates”，会直接被压住。避法是避免全局共享上下文 claim，强调每个 role 的可见上下文不同，准入结果是一个 role-source edge set。

第三危险是 CICL。它已经有 decision utility、typed memory cards、budget packing。我们如果继续做简单 utility + budget greedy，会显得浅。避法是让 utility 依赖 recipient scope、source ownership、dependency closure，而不能只做单个 evidence 的性价比排序。

第四危险是 CaMeL。它在安全侧把 programmatic enforcement 讲得非常强。我们可以借语言，但不能碰“安全保证”。我们的 compiler 只能说是 evaluation/protocol boundary executor，除非未来真的做 formal policy。

## ArXiv_Daily_Digest 补压

我进 `D:\develop\ArXiv_Daily_Digest` 做了 `git pull --ff-only`，结果是 `Already up to date`。W25 的 `multi-agent-consistency`、`agent-skills-harness`、`agent-policy-optimization` 里，最新一层压力直接打在 admission / gating / exposure 这组词上，比第一波还贴脸。

| Paper | 它占住的对象 | 对我们的压力 | 避法 |
| --- | --- | --- | --- |
| ToolMenuBench | visible tool menu construction, CMTF, tool exposure metrics | 如果我们讲“哪些工具/动作此刻可见”，会被它和 CMTF 压住 | 不做 action/tool menu；做 evidence-to-recipient admission |
| RACG / Capability Minimization | least-privilege tool exposure, high-risk authorization gate, provenance constraints | “gating + authorization + provenance” 已经有很强的 tool-action 版本 | source/provenance 只作为证据准入条件，不 claim tool safety primitive |
| MINIM | privacy-aware minimal UI observation, sensitivity/necessity, ternary disclosure | “最小可见上下文/本地 broker/必要性过滤” 已被占 | 不做 UI/state observation minimization；做 agent 间证据进入本地上下文 |
| Skill-Conditional Reputation | per-skill trust, cross-skill evidence laundering, evidence gate | 它把“证据借用会污染路由信任”讲得很清楚 | 可借 laundering 现象；我们的 source/scope 是证据权限，agent reputation 只是参考先验 |
| Verified Concurrency Anomalies | shared-state consistency, lost updates, verified runtime isolation | 共享状态一致性和 verified runtime 这条路很硬 | 避免 shared-memory consistency claim；只管准入前的 evidence boundary |
| StateGen | authoritative state manager, backend-is-truth invariant, sub-agents as tools | 全局 authoritative state manager 已有生产数据生成故事 | 不讲全局 truth manager；讲每个 recipient 的局部准入集合 |
| Diagnostic handoff gates | deterministic orchestration constraints, completeness gate, semantic-entropy gate | “formal gate blocks unsafe transition” 已有医疗场景版本 | 可学 gate narrative；V1 要做跨角色证据准入，而非单流程 phase gate |
| Trust-aware traceability KG | shared KG, confidence threshold gating, divergence detection | confidence as coordination signal 已被软件 traceability 管住一块 | 不做共享 KG confidence propagation；做 source/scope/dependency admission |

这层压力后的修正更狠：`compiler` 这个词容易把我们带到 tool gating、runtime isolation、state manager、policy enforcement 的战场。那里已经很挤。可活的对象应当叫 `role-scoped evidence admission`：输入是证据片段、来源、作用域、依赖、验证状态和跨角色预算；输出是每个 recipient 的 admitted evidence set。它的评测核心是“同一内容在不同 source/scope 下应进入不同 agent 的局部上下文”。

## 第一波后的定位

外部压力没有杀掉方向，但杀掉了很多宽表述。安全的叙事应当长这样：

```text
Existing MAS communication work controls how much agents say, how messages are summarized,
or how shared state is verified. It rarely tests recipient-specific admission:
whether a source-scoped piece of evidence is allowed to enter each agent's local context
under role, scope, budget, dependency, and verification constraints.
```

中文人话：别人已经在管“说什么、说多少、共享什么、验证什么”。我们要管“这条证据能不能进这个 agent 的脑子里”。核心压力来自准入边界：边界错了，正确内容会进入错误角色，错误来源也会获得不该有的权威。

## 对实验的直接要求

下一版 benchmark 必须让 DALA / PACT / CICL 式简单 baseline 不舒服。具体说：

1. 同一 text，换 source/scope 后 gold recipient 改变。
2. 同一 fragment，对不同 role 的准入状态不同。
3. 有 dependency closure：单发一个高 utility fragment 没用，必须成组准入。
4. 有 verification gate：某些 source 需要验证后才能进上下文。
5. 有 cross-role budget conflict：给 A 会占掉 B 的共享预算，不能独立贪心。
6. greedy utility-density 必须明显低于 oracle，否则 benchmark 仍然太浅。

## 目前结论

这波外部压力后的结论是：方向可活，宽 claim 不可活。名字应当从 budget compiler 收紧到 role-scoped evidence admission / state admission。下一步实验要构造能区分 PACT-style message projection、DALA-style budgeted speech、CICL-style utility packing、ToolMenuBench/RACG-style tool exposure gating、以及我们 role-scoped admission 的 V1，继续扩大 PerspectiveGap V0 的收益很有限。

## Sources Read

- DALA / Cost-Effective Communication: `papers/20260618-routing-story/extracted_text/dala-2511.13193.txt`
- PerspectiveGap: `papers/20260618-routing-story/extracted_text/perspectivegap-2606.08878.txt`
- ProvenanceGuard: `papers/20260618-routing-story/extracted_text/provenanceguard-2606.18037.txt`
- WhoFlips: `papers/20260618-routing-story/extracted_text/whoflips-2606.16011.txt`
- Trust Between AI Agents: `papers/20260618-routing-story/extracted_text/trust-between-ai-agents-2606.14923.txt`
- MINT: `papers/20260618-routing-story/extracted_text/misinformation-propagation-2606.16710.txt`
- HiddenBench: `papers/external-pressure-20260616/hiddenbench-2505.11556.txt`
- PACT: `papers/external-pressure-20260616/pact-action-state-2606.05304.txt`
- DeLM: `papers/external-pressure-20260616/delm-shared-context-2606.10662.txt`
- CaMeL: `papers/external-pressure-20260616/camel-prompt-injection-2503.18813.txt`
- CICL / Decision-Aware Memory Cards: `papers/20260618-routing-story/extracted_text/decision-aware-memory-2606.08151.txt`
- ArXiv_Daily_Digest local scan: `D:\develop\ArXiv_Daily_Digest\data\multi-agent-consistency\2026-W25\papers.jsonl`, `D:\develop\ArXiv_Daily_Digest\data\agent-skills-harness\2026-W25\papers.jsonl`, `D:\develop\ArXiv_Daily_Digest\data\agent-policy-optimization\2026-W25\papers.jsonl`
- ToolMenuBench: https://arxiv.org/html/2606.15508v1
- MINIM: https://arxiv.org/html/2606.13949v1
- RACG / Capability Minimization: https://arxiv.org/html/2606.13884v1
- Skill-Conditional Reputation: https://arxiv.org/html/2606.14200v1
- Verified Concurrency Anomalies: https://arxiv.org/html/2606.17182v1
- Diagnostic Handoff Gates: https://arxiv.org/html/2606.18068v1
- StateGen: https://arxiv.org/html/2606.16307v1
- Trust-Aware Traceability KG: https://arxiv.org/html/2606.17203v1
