# 异构/不对称多 Agent 通信外部压力

日期：2026-06-19

## 核心判断

这个方向没有空白到可以随便命名，也没有被单篇 A 会论文完整吃掉。A 会已经接受了多 agent 信息不对称、讨论一致性、通信效率、拓扑稀疏、失败归因和 latent/thought communication 这些近邻；如果我们的 claim 只是“异构模型合作更强”或“多 agent 通信能提高性能”，空间基本已经没了。

仍然活着的切口更窄：在异构或能力不对称 agent 团队中，私有/角色可见事实进入下游决策前，需要经过 source、scope、recipient、verification、rejection、budget、evidence sufficiency 的准入。这个对象还没有在我看到的 A 会论文中被统一成一个可执行 benchmark/method claim。

## 本轮接触

本地 `D:\develop\ArXiv_Daily_Digest` 已执行 `git pull --ff-only`，从 `e47ea96` 更新到 `47e901899abddd5a96d88720175d11fe36bd3834`。W25 新增的高相关条目包括：

| Paper | Digest ID | 压力点 |
| --- | --- | --- |
| tap: A File-Based Protocol for Heterogeneous LLM Agent Collaboration | 2606.14445 | 异构 LLM agent 协作协议已经被明确提出；它压 harness/protocol novelty。 |
| How Task Structure Limits Multi-Agent Success | 2606.13733 | 多 agent 成功受任务结构和通信边界限制；它压“多 agent 总会更强”的叙事。 |
| Misinformation Propagation in Benign Multi-Agent Systems | 2606.16710 | 通信是扩散/污染通道；它压只看最终 accuracy 的设计。 |
| ProvenanceGuard | 2606.18037 | heterogeneous evidence source + source-aware verification 已经是近场热点；它压 provenance/source claim。 |
| CoffeeBench | 2606.16613 | heterogeneous long-horizon economies；它压长期协作和真实生态评测。 |
| EARS | 2606.18668 | coordinator 对 sub-agent 能力建模与 abstention；它压 sub-agent modeling/reliability。 |
| TickingCollabBench | 2606.15684 | heterogeneous + mandatory collaboration + timed complementary tasks；它压 benchmark novelty。 |
| MedLatentDx | 2606.13945 | latent communication under cross-institution private data；它压 latent/privacy collaboration。 |
| Trust Between AI Agents | 2606.14923 | costly verification 测 agent trust；它压 verification budget。 |
| SciOrch | 2606.15872 | heterogeneous expert LLM orchestration；它压“选择哪个专家/模型”的 claim。 |
| Parallel-Synthesis | 2606.14672 | KV/cache 级并行 agent 分支合成；它压“拼接文本是唯一通信层”的假设。 |

## A 会近邻

| Paper | Venue | Object | Mechanism | Overlap |
| --- | --- | --- | --- | --- |
| iAgents / InformativeBench | NeurIPS 2024 | LLM agents under information asymmetry | InfoNav + mixed memory + benchmark | partial overlap；占住“信息不对称协作 benchmark”大旗。 |
| M2CL: Context Learning for Multi-Agent Discussion | ICLR 2026 poster | multi-agent discussion inconsistency | 每轮动态 context generator | partial overlap；占住“讨论上下文动态调节”。 |
| MultiAgentBench | ACL 2025 long | collaboration/competition benchmark | 多场景、多拓扑、milestone KPI | useful prior；面广但不聚焦 source/scope/admission。 |
| Sparse Communication Topology | EMNLP Findings 2024 | MAD 通信拓扑 | sparse topology 降成本保性能 | useful prior；压 communication budget/topology。 |
| Optima | ACL Findings 2025 | LLM-MAS effectiveness/efficiency | generate-rank-select-train, task/token/readability reward | partial overlap；压“通信效率训练”路线。 |
| Thought Communication | NeurIPS 2025 spotlight | latent thought sharing | latent variable model, shared/private thoughts | partial overlap；压“超越自然语言通信”的理论路线。 |
| LatentMAS | ICML 2026 spotlight | latent-space MAS collaboration | hidden embedding + shared latent memory | partial overlap；压 latent collaboration 和效率 claim。 |
| Who&When | ICML 2025 | failed MAS attribution | agent/step failure labels | useful prior；压失败归因而非准入机制。 |

## Direct Collision 判断

没有看到直接 collision。直接 collision 需要同时共享：对象是答前 evidence admission；机制是 LLM propose units + deterministic compiler/gate；实验同时测 role/source/scope/verification/rejection/budget/evidence sufficiency/downstream decision；最终 claim 是准入层比自由文本或共享上下文更可靠。

目前最接近的压力来自三面：

1. iAgents 占住信息不对称协作，但它的对象是人类社交网络镜像和主动信息交换，不是 source-scoped evidence admission。
2. ProvenanceGuard 占住 source-aware factuality verification，但主要在 answer/evidence verification 层，不是答前 recipient-scoped 准入。
3. Optima/DALA/Sparse-MAD/LatentMAS 占住通信效率或通信表示层，但没有把 recipient-specific admissibility、rejection 和 sufficiency 作为统一执行对象。

## 现在领域的底部

第一层底部：多 agent 通信本身已经不是新东西。A 会已经承认 MAD、拓扑、benchmark、优化、失败归因；不能再写“我们研究多 agent 交流”。

第二层底部：信息不对称也已经不是空白。NeurIPS 2024 的 iAgents/InformativeBench 已经把这个问题正式化；新的贡献必须说明自己测的不是一般 private information exchange。

第三层底部：异构模型合作正在升温，但多停在三类对象：harness/protocol，如 tap；能力调度/专家编排，如 SciOrch；latent/cache 通信，如 LatentMAS、Thought Communication、Parallel-Synthesis。纯“强弱模型互补”会被这些工作压扁。

第四层底部：真正未稳定解决的是通信状态治理。外部工作共同指向一个更底层的问题：信息不只是要发出去，还要决定能否被谁看见、是否可信、是否足够、是否应该沉默或验证、是否会污染下游承诺。

## 对我们当前 story 的影响

如果继续走 SSEAC / HSA 线，claim 应收窄成：

```text
In heterogeneous or role-asymmetric multi-agent communication, useful private facts must be admitted into recipient-scoped decision state before downstream commitment. We separate semantic unit proposal from deterministic source/scope/verification/budget/sufficiency enforcement.
```

这个 claim 的危险 baseline 不是普通 free-form exchange，而是：

- shared verified context / DeLM-style context；
- source ledger prompt；
- CICL-style decision-aware card packing；
- budgeted router / DALA-style auction；
- provenance-aware verifier；
- oracle admissible facts / oracle executor。

## 下一步压力

下一步不该继续泛搜文献。应做一个 `12-24` 行的外部化 pressure packet，把 HiddenBench failure seeds、PerspectiveGap source-ledger 和 HSA perturbation 合成同一张小主表。

最小主表必须包含：

| Row | 目的 |
| --- | --- |
| shared_only / no communication | 通信必要性下界 |
| free exchange / old exchange | 自由文本污染对照 |
| all_scoped / copy_all | 过度共享投机对照 |
| source_ledger_model_only | 模型能否自己守 source/scope |
| shared_verified_context | 强邻居 baseline |
| CICL_style_card_packing | decision-aware context baseline |
| budgeted_greedy / DALA-style router | 成本/沉默 baseline |
| SSEAC_model_units + compiler | 我们的最小方法 |
| oracle_admissible_facts / oracle_executor | 上界 |

Go 条件：SSEAC 至少在一个自然外部 slice 上同时降低 over-share/leak/forced-commitment，并保住必要 coverage；如果只赢 weak prompt baseline，降级为 diagnostic/compiler note。

Retire 条件：shared_verified_context 或 CICL-style packing 接近 oracle，且 evidence sufficiency prompt 能解决 perturbation 行；那说明当前贡献太接近已有 context-selection/verification 工作。

## Sources

- ArXiv_Daily_Digest local repo: `D:\develop\ArXiv_Daily_Digest`, HEAD `47e901899abddd5a96d88720175d11fe36bd3834`
- iAgents / InformativeBench: https://proceedings.neurips.cc/paper_files/paper/2024/hash/0534abc9e6db91683d82186ef0d68202-Abstract-Conference.html
- M2CL: https://openreview.net/forum?id=EUu8TILWpR
- MultiAgentBench: https://aclanthology.org/2025.acl-long.421/
- Sparse-MAD: https://aclanthology.org/2024.findings-emnlp.427/
- Optima: https://aclanthology.org/2025.findings-acl.601/
- Thought Communication: https://openreview.net/forum?id=tq9lyV9Cml
- LatentMAS: https://arxiv.org/abs/2511.20639
- Guided Collaboration in Heterogeneous LLM-Based MAS: https://arxiv.org/abs/2602.13639
- AsymPuzl: https://openreview.net/forum?id=Uft46u0GRx
- Communication and Verification under Information Asymmetry: https://arxiv.org/abs/2510.25595
