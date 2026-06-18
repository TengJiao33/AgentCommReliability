# Routing Story Reading Sprint

## 核心判断

方向没有死。真正弱的是旧切口：`private evidence -> preference pollution` 太细，太直觉，撑不起太多机制、设计和实验。外部阅读把主线推到一个更大的对象：`role/source-aware state routing under scarcity`。用人话讲，就是系统要在成本、角色、来源、验证预算约束下，决定哪些状态可以进入哪个 agent 的可见上下文，哪些状态应该沉默、延迟、验证或隔离。

多 agent debate / consensus 这块已经很挤。继续围着互相说服、投票、final-answer gain 做，很容易被 DALA、Sparse-MAD、MINT、WhoFlips、Cost of Consensus 这类已有故事吞掉。当前更有空间的位置在 orchestration / harness 层：有 gold 的 routing、source attribution、budgeted communication、artifact lineage、costly verification。

你的有趣门槛没有太高。我们现在觉得无聊，是因为旧 handle 还缺一个能改变实验结构的外部对象。PerspectiveGap、DALA、WhoFlips、Trust、tap 这些东西给了更硬的对象，不靠脑内拧概念。

## 本轮接触

ArXiv_Daily_Digest 已进入 `D:\develop\ArXiv_Daily_Digest` 并执行 `git pull --ff-only`，结果为 `Already up to date`，当前 HEAD 是 `e47ea96d4b0e0921abf75c2d0576edfca2a417b7`。W24 有 weekly digest 和 landscape，W25 当前主要是 `papers.jsonl`。

本项目新增/确认的论文缓存位于 `papers/20260618-routing-story/`。已拉下并抽取文本的 PDF 包括 PerspectiveGap、DALA、Sparse-MAD、ProvenanceGuard、Task Structure Limits、MINT、Context-Fractured、CAR、CICL，以及本轮新增的 tap、WhoFlips、CoffeeBench、Trust Between AI Agents、SciOrch、LLM-as-Code。

已 clone 的相近代码仓库：

| Repo | Local path | Commit | 读数 |
| --- | --- | --- | --- |
| DALA / Cost-Effective-Communication | `papers/20260618-routing-story/repos/Cost-Effective-Communication` | `d6f5939ab1409444348e62aceefa8dfedbeb9508` | 有 mock backend、33 tests、offline smoke。当前主环境缺 `pytest`、Lightning、OmegaConf，需隔离 venv 复现。 |
| PerspectiveGap | `baselines/PerspectiveGap/upstream` | `60b1dcaaeeb40619075f6cd8779c47fa4b344391` | 已完成官方 scorer、220-row render、18 tests、deterministic baselines、Qwen stratified20。 |
| WhoFlips | `papers/20260618-routing-story/repos/WhoFlips` | `9ea1189b05f38b52feecd9bf44ae94f4ae1a9c7e` | README 只有数据/协议入口，HF 数据集是主可复现对象。 |
| SciOrch | `papers/20260618-routing-story/repos/SciOrch` | `15afbfd82a7671827cf3dfa7c995ae846176c2bd` | 强 story 模板，但训练和专家模型调用较重。 |
| tap | `papers/20260618-routing-story/repos/tap` | `1c258e31e52e427085433307d03d6198cd83c460` | 文件化 agent 通信协议，npm `@hua-labs/tap` v0.5.2，可作为 harness 方向素材。 |
| Escape-room-v2 | `papers/20260618-routing-story/repos/Escape-room-v2` | `74f0fd1163b299b387efac9bfce6452c93697d18` | Trust paper 的 costly verification 环境，有示例日志和分析脚本。 |
| MINT | `papers/20260618-routing-story/repos/MINT` | 已 clone | 可用来做 misinformation exposure 的小 contact。 |
| CICL | `papers/20260618-routing-story/repos/CICL` | 已 clone | 决策相关 memory card 和 context utility，可借 schema。 |
| CAR | `papers/20260618-routing-story/repos/causal-agent-replay` | 已 clone | 后续用于失败归因，当前不应抢第一优先级。 |

CoffeeBench 论文写了 `github.com/SakanaAI/CoffeeBench`，但当前 `git ls-remote` 返回 repository not found。PDF 和 trajectory 链接已保留，先标为可读、暂不可直接复现。

## 优秀 story 的共同骨架

| Paper / System | 它的好 story | 证据形状 | 给我们的启发 |
| --- | --- | --- | --- |
| DALA | 免费发言导致低信噪比和高 token 成本；通信被改写成稀缺资源分配。 | auction、budget sweep、多 benchmark、strategic silence。 | 我现在最认可的 multi-agent communication 论文。机制简单，现象好记，可直接变成我们 PerspectiveGap 的 budgeted-router baseline。 |
| Sparse-MAD | fully-connected debate 作为默认设计会浪费通信；拓扑本身是变量。 | sparse topology vs full connectivity，accuracy/cost/rounds。 | 说明“更多通信”不应作为默认。我们的 router 应有 top-k、budget、silence 条件。 |
| PerspectiveGap | multi-agent orchestration 的核心失效可以提前到 prompt/routing 层评分。 | coverage、boundary precision、distractor leakage，110 scenarios。 | 它给了我们可评分的 role-routing 对象，比 final answer benchmark 清楚。 |
| ProvenanceGuard | pooled evidence 支持不了 source attribution；cross-source conflation 是独立错误轴。 | claim decomposition、source routing、NLI、repair。 | 我们的 fragment 需要 `source_id/scope/recipient`，光有内容正确还不够。 |
| CICL | 长上下文和语义相似度不能保证决策相关；context 应按 action utility 排序。 | context graph、utility score、memory card、SWE-bench retrieval。 | typed fact card 可以从“格式要求”升级为“决策效用和可见范围”的记录。 |
| WhoFlips | 标准准确率看不出模型面对合理反论时会不会改答案。 | 两阶段 challenge protocol、AFR、MAXFLIP、HF 数据集。 | 它把直觉现象做成 benchmark。我们也要把 source/role influence 做成控制协议。 |
| Trust Between AI Agents | agent trust 可以用 costly verification 测量，不靠自述。 | verification cost、formation/breakage/recovery、raw logs。 | 若走 out-of-box，可以把“该不该验证队友”变成通信预算问题。 |
| tap | 异构 agent 协作的痛点来自共享运行时假设和不可审计消息。 | 文件消息、worktree 隔离、27-day self-applied operation。 | 如果主线转 agent harness，file/artifact lineage 是比 chat transcript 更真实的通信层。 |
| SciOrch | 多专家编排的难点在 API 成本和选择性 delegation。 | lightweight orchestrator、MCTS、GRPO、accuracy/cost。 | 它的 story 是“学会何时委托谁”。我们当前可以先做规则/LLM router，再谈训练。 |
| CoffeeBench | 长周期多 agent 经济体需要通信、谈判、交易和行动。 | 90-day simulation、net income、idle-drift。 | 它提醒我们别只看 single-turn routing；长期任务里沉默也可能是 failure。 |
| MINT | misinformation 在 multi-agent debate 中会传播，群体组成和决策协议影响纠偏。 | exposed/unexposed composition、consensus/voting。 | `private evidence -> pollution` 可降级成 exposure composition 的一个子问题。 |
| CAR | agent 失败需要 causal replay，而非只看最终错在哪一步。 | intervention、rerun、Shapley、Who&When。 | 等我们有 richer traces 后再用它做归因。 |

## 对我们方向的审判

`private evidence -> preference pollution` 应降级成一个子 failure mode。它可以解释 HiddenBench 里推荐泄漏、共享事实 overtalk 和 MINT 里的 misinfo exposure，但它无法单独接住 budget、role boundary、source ownership、verification、artifact lineage 这些更大的变量。

benchmark 问题是真问题。MATH/TypeCast 这类 final-answer 或 re-answer packet 很容易把机制吞掉；它们适合做显微镜，不能再指挥主线。HiddenBench 和 PerspectiveGap 的价值在于它们把通信必要性或 routing correctness 提前成可评分对象。

我们现有证据刚好支持这个转向。HiddenBench Stage 2 full65 中，fact-only exchange 在 clean subset 上是 `55/55`，旧 exchange 是 `23/55`，说明推荐泄漏和共享事实 overtalk 会毁掉通信。PerspectiveGap stratified20 中，14B 相比 7B coverage 从 `0.443` 到 `0.615`，distractor leak 从 `0.050` 到 `0.450`，说明更强模型会更积极路由，也更容易夹带诱饵。这两个信号合起来，比旧的偏好污染更能长出 story。

当前最活的主问题可以写成：

```text
Multi-agent systems fail when communication is treated as free text sharing.
The harder object is constrained state routing:
which state, from which source, under which scope, to which recipient,
with what budget and verification policy.
```

## 下一步怎么走

第一步，复现 DALA offline。建隔离 venv，跑 `pytest -q` 和 `experiments/smoke.sh`，记录到 `baselines/DALA/reproduction.md`。目的很具体：确认 auction/budget/silence 代码路径能跑，然后把它改成 PerspectiveGap 的非训练 budgeted-router baseline。当前主环境只证明了依赖未就绪，不能当 DALA 失败。

第二步，在 PerspectiveGap stratified20 上做同一批样本的 router ladder：

| Arm | 含义 | 关键读数 |
| --- | --- | --- |
| raw router | 当前 Qwen role-assignment prompt | baseline coverage/precision/leak |
| typed card router | 每个 fragment 输出 recipient、scope、source、reason | 是否降低 role-boundary false positives |
| provenance card router | 强制 source_id 和 visibility label | 是否降低 distractor/source 混淆 |
| budgeted top-k router | 每个 role 限 fragment 数 | 是否用小 coverage 换大 precision |
| DALA-style auction router | fragment/role pair 先 bid，再按预算录取 | 是否出现有用的 strategic silence |

这一步先不跑 full 220。继续用 stratified20，固定 seeds `1, 42`，比较 7B/14B。成功信号是保住 14B 的 coverage，同时明显压低 distractor leak 和 false positives。失败信号是 typed/budgeted 全部只是在删信息，coverage 掉得比 leak 降得快。

第三步，把 WhoFlips 当 benchmark 设计课来用。先拉 HF `maxflip_mmlu`，做一个小 contact：同一模型先答对，再看匿名、self-attributed、cross-source argument 是否让它 flip。它与 multi-agent 有距离，但它提供了 source/argument perturbation 的干净协议。若我们后续做 peer/source influence，应该学它的两阶段设计和 AFR 指标，少写泛泛的“被同伴影响”。

第四步，MINT 和 Trust 作为两个分叉压力。MINT 用来测试 misinformation exposure composition；Trust 用来测试 verification budget 和 teammate reliability。如果 PerspectiveGap router ladder 没有长出足够机制，这两个比继续调 prompt 更值得开。

第五步，tap 和 SciOrch 保持阅读状态。tap 适合 agent harness / artifact communication 方向，SciOrch 适合学习“选择性委托和成本”的 paper story。它们当前不抢 P0，因为一个偏系统协议，一个偏重训练和专家 API。

## A 会 story 判断

现在还没到 A 会 story，但已经有活 handle。A 会 story 需要从下面两个方向选一个压实：

1. 方法路线：`budgeted provenance-aware state router` 在 PerspectiveGap/HiddenBench/PACT-style split evidence 上稳定减少 over-sharing 和 leakage，同时保住 required coverage。
2. benchmark/evaluation 路线：提出一个更清楚的 role/source routing evaluation，把 coverage、boundary、source attribution、budget、verification 统一进一个可复现实验面。

我更倾向先走方法路线的最小版，因为 DALA 和 PerspectiveGap 已经给了可拼接对象。若最小版失败，就把贡献重心转到 benchmark/evaluation，避免硬写一个普通 prompt method。

## Sources

- DALA / Cost-Effective Communication: https://arxiv.org/abs/2511.13193, https://github.com/waltstephen/Cost-Effective-Communication
- Sparse-MAD: https://aclanthology.org/2024.findings-emnlp.427/
- PerspectiveGap: https://arxiv.org/abs/2606.08878, https://github.com/WhymustIhaveaname/PerspectiveGap, https://huggingface.co/datasets/sun1245/PerspectiveGap
- ProvenanceGuard: https://arxiv.org/abs/2606.18037
- Task Structure Limits Multi-Agent Success: https://arxiv.org/abs/2606.13733
- MINT / Misinformation Propagation: https://arxiv.org/abs/2606.16710, https://github.com/jonas-becker/MINT
- CICL / Decision-Aware Memory Cards: https://arxiv.org/abs/2606.08151, https://github.com/stephen-guan-researcher/CICL
- CAR / Causal Agent Replay: https://arxiv.org/abs/2606.08275, https://github.com/jaineet17/causal-agent-replay
- tap: https://arxiv.org/abs/2606.14445, https://github.com/HUA-Labs/tap, https://www.npmjs.com/package/@hua-labs/tap
- WhoFlips: https://arxiv.org/abs/2606.16011, https://github.com/nafisenik/WhoFlips, https://huggingface.co/datasets/nafisehNik/WhoFlips
- Trust Between AI Agents: https://arxiv.org/abs/2606.14923, https://github.com/cyjabc2020/Escape-room-v2
- SciOrch: https://arxiv.org/abs/2606.15872, https://github.com/llexieguo/SciOrch
- CoffeeBench: https://arxiv.org/abs/2606.16613, https://pub.sakana.ai/coffeebench/trajectories.html
- LLM-as-Code: https://arxiv.org/abs/2606.15874
