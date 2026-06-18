# 通信必要 benchmark 版图

## 核心判断

TeamBench 是当前看到的最硬工程型通信必要 benchmark：Planner、Executor、Verifier 被 OS 容器隔离，任何单个角色都缺少完成任务所需的全部权限。官方可信结果需要 Docker，因为 role separation 依赖容器挂载边界。

当前 A800_2 没有 Docker、Podman、Singularity、Apptainer，也没有免密 sudo。我们可以读 TeamBench 数据、跑 mock sanity，暂时无法在这台机器上得到它最关键的 OS-enforced 结果。可执行路线应先用 HiddenBench 和 PACT/HotpotQA split-evidence，把通信必要性和 public-state failure 做实。

## TeamBench

来源：

- project: `https://teambench.github.io/`
- paper: `https://arxiv.org/html/2605.07073v1`
- code: `https://github.com/ybkim95/TeamBench`

设计强度：

- 851 task templates，931 seeded instances，19 categories，5 ablation conditions。
- Planner 读 full spec，但不能编辑或执行。
- Executor 能编辑 workspace 和执行命令，但看不到 full spec。
- Verifier 读 full spec 和只读 workspace/test logs，但不能修改 workspace 或执行命令。
- 成功需要信息在角色间移动；pass rate 之外还计算 Teamwork Necessity Index。

Docker 结论：

- README 安装步骤包含 `docker compose build`，并明确写了 OS-enforced role separation requires Docker。
- 论文说明每个 role 在独立 container 中运行，边界通过 container bind mounts enforcing。
- mock 模式能测 grading + sandboxing pipeline，但官方核心 claim 依赖容器隔离。

对我们：

- P0 研究目标。
- 当前机器上不能正式跑。
- 如果能拿到 Docker 权限，优先跑 TeamBench-90 的 small model / mock / one real model sanity。

## HiddenBench

来源：

- paper: `https://arxiv.org/abs/2505.11556`
- repo: `https://github.com/jonradoff/hiddenbench`
- dataset: `https://huggingface.co/datasets/YuxuanLi1225/HiddenBench`

设计强度：

- 65 hidden-profile decision tasks。
- 每个 agent 拿 asymmetric/private information。
- 评估 pre-discussion、discussion、post-discussion、full-profile baseline。
- 任务目标就是 collective reasoning under distributed information。

对我们：

- 已能跑，无 Docker。
- 已跑 full 65：`shared_only` 1/65，`full_info` 59/65，`oracle_public_facts` 56/65，`exchange_then_decide` 24/65。
- 这是目前最适合继续推进的可执行通信必要 benchmark。

## PACT / Split-Evidence

来源：

- paper: `https://arxiv.org/html/2606.05304v1`
- code: `https://github.com/iNLP-Lab/PACT`
- HotpotQA: `https://hotpotqa.github.io/`

设计强度：

- Setting A 是 split-evidence interaction：两个 agent 各自只拿 partial evidence，必须交换 task-relevant evidence 才能答题。
- PACT 使用 HotpotQA 和 2WikiMultiHopQA 做 split-evidence interaction。
- Setting B 还用 AIME、GPQA-Diamond、OpenBookQA 做 sequential pipeline。
- 论文还把 PACT 接到 OpenHands 和 SWE-agent，在 SWE-bench Verified 上测 token efficiency。

对我们：

- 已有本地 PACT/HotpotQA 基础和 field-level public-state 结果。
- 它很适合验证 typed fact card、action/state/result、evidence admission。
- 原始 HotpotQA 天然形态偏单 agent；PACT-style 5/5 split 把它改造成通信必要条件。

## EnactToM

来源：

- paper: `https://arxiv.org/html/2605.09826v2`
- project: `https://enact-tom.github.io/`

设计强度：

- 300 embodied multi-agent tasks。
- 3D household，partial observability，private information，constrained communication。
- 每个任务有 formal solvability 和 required epistemic depth verification。
- hard split 上 7 个 frontier model 的 functional task completion Pass^3 为 0.0%。

对我们：

- 理念非常强，尤其是 private info + constrained communication + partner belief。
- 执行成本明显高于 HiddenBench；很可能需要 3D/simulator 依赖。
- 更适合作为论文相关工作和未来高压目标，短期不作为第一执行对象。

## MultiAgentBench / MARBLE

来源：

- paper: `https://arxiv.org/html/2503.01935v1`
- code: `https://github.com/MultiagentBench/MARBLE`

设计强度：

- 六类 interactive scenarios，包括 research co-authoring、Minecraft building、database error analysis、coding collaboration、Werewolf、bargaining。
- 指标包含 task score、milestone KPI、planning/communication score、competition score。

对我们：

- 面很广，适合证明“多 agent 互动”。
- 信息必要性不如 HiddenBench、TeamBench 干净；很多场景可能混入 planner quality、environment control、social behavior。
- 可以作为相关工作，不优先作为下一轮主实验。

## Collab-Overcooked

来源：

- paper: `https://arxiv.org/abs/2502.20073`
- code: `https://github.com/YusaeMeow/Collab-Overcooked`

设计强度：

- 基于 Overcooked-AI 的 interactive collaboration。
- 30 open-ended tasks，强调 natural language communication。
- 指标包括 initiate collaboration、respond collaboration、action matching、redundancy。

对我们：

- 很适合 active collaboration / continuous adaptation。
- 与我们现在的 public-state / fact transmission 主题距离略远。
- 不依赖 Docker，依赖 Python/Overcooked 环境；可以作为 P2。

## SOTOPIA

来源：

- paper: `https://arxiv.org/abs/2310.11667`
- platform: `https://sotopia.world/`

设计强度：

- social intelligence / role-play interaction。
- 每个 scenario 有 context、private social goals、character secrets 和 relationships。

对我们：

- 有 private goals 和 social communication。
- 评分更多依赖 social-goal evaluation，通信必要性和可复现 deterministic gold 较弱。
- 适合作为社会交互相关工作，不适合作为下一步主 benchmark。

## TheAgentCompany

来源：

- paper: `https://arxiv.org/abs/2412.14161`
- code: `https://github.com/TheAgentCompany/TheAgentCompany`

设计强度：

- 175 realistic professional tasks in a simulated software company。
- agent 需要 browse web、write code、run programs、communicate with coworkers。
- 使用 OpenHands CodeAct agent 和 OWL-RolePlay。

对我们：

- 外部真实度很强。
- 通信只是 workplace task 的一部分，单 agent 仍可能完成许多任务。
- 环境重，短期不适合作为通信必要性主实验。

## 推荐顺序

1. HiddenBench protocol v2：马上可跑，已经有 full 65 baseline，最适合验证 typed fact / admission / constraint merge。
2. PACT split-evidence HotpotQA/2Wiki：和我们已有 PACT field-state 工作连续，适合做 public-state reliability。
3. TeamBench：一旦有 Docker 权限，立刻升级成最强工程压力。
4. EnactToM：强相关但执行重，先做 paper/contact 和代码可运行性侦察。
5. Collab-Overcooked / MultiAgentBench / SOTOPIA / TheAgentCompany：用于版图和补充，不作为下一轮主线。

## 对论文故事的影响

MATH 继续留作 peer-influence microscope。真正支撑通信必要性的主线应转到 HiddenBench 和 PACT split-evidence；TeamBench 是后续工程级验证目标。我们当前最有价值的问题已经变成：当必要私有事实确实存在时，什么 public-state 协议能让事实被保留、被授权、被用于最终承诺。
