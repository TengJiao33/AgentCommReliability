# 模型族与实验设置差距

## 核心判断

我们一直用 Qwen2.5-14B-Instruct，适合做 cheap diagnostic 和 packet debugging，但它离外部强 benchmark 的主实验设置差距很大。强论文通常做三件事：跨模型族、跨模型规模、跨协议条件；我们的多数结果目前是单模型、单温度、局部 packet 或 re-answer pressure。

这个差距会直接影响说服力。若一个现象只在 Qwen2.5-14B 上出现，评审会把它归因到模型局限、prompt artifact 或 evaluator setting。若它在 Qwen2.5-14B、Qwen3/DeepSeek/Llama 大模型、以及一个 closed frontier 模型上呈现同方向机制，才更像可写成 paper claim。

## 我们当前设置

主要 backbone：

- Qwen2.5-14B-Instruct，vLLM serving。
- 大多数 run 使用 temperature 0。
- PACT public-state field packet: max tokens 64，500 re-answer rows，HotpotQA offset slice。
- HiddenBench probe: max tokens 180，项目内 answer-first 协议，非官方 group-discussion harness。
- MATH authority/typecast 系列：receiver/re-answer packet，max tokens 768 或更低，单模型。

这意味着我们当前最强的证据对象是机制诊断，尚未达到 benchmark leaderboard 级证据。HiddenBench full 65 已经给出有价值外部压力，但仍需要 protocol v2 和 cross-model check。

## HiddenBench

来源：

- paper: `https://arxiv.org/html/2505.11556v2`
- repo: `https://github.com/jonradoff/hiddenbench`

外部设置：

- 65 hidden-profile tasks。
- 15 frontier LLMs，覆盖 OpenAI GPT、Google Gemini、Alibaba Qwen、Meta Llama 四个模型族。
- 每个模型每个 task 在 Hidden Profile 和 Full Profile 条件下各跑 10 sessions。
- 官方 repo 默认 4 agents、15 discussion rounds、temperature 0.7，并跑 full-profile baseline。

外部发现：

- Hidden Profile pre-discussion accuracy 在 0.082 到 0.217，说明单个局部 agent 低。
- Full Profile pre-discussion accuracy 在 0.435 到 0.981，说明信息完整时任务可解。
- Gemini-2.5-Pro 的 Hidden post-discussion accuracy 最高，约 0.671；Gemini-2.5-Flash 约 0.550。
- 论文明确说 model scale 和 reasoning augmentation 没有稳定转化成 collective reasoning。
- repo 示例里 Claude Opus 4.5 在 63 official tasks 上 post-discussion 89.3%，full-profile 95.6%。

和我们的差别：

- 我们跑 Qwen2.5-14B 单模型，且没有使用官方多轮 group harness。
- 我们的项目内 probe 更适合定位“干净事实 vs 生成式 exchange”的 gap。
- 下一步若继续 HiddenBench，至少要加入一个 Qwen3/DeepSeek/Llama 大模型和一个 Gemini/Claude/GPT frontier baseline。

## PACT

来源：

- paper: `https://arxiv.org/pdf/2606.05304`
- code: `https://github.com/iNLP-Lab/PACT`

外部设置：

- 模型只用 Qwen3 family，但做 scale sweep：Qwen3-8B、Qwen3-14B、Qwen3-32B。
- decoding: temperature 0.6，top-p 0.95。
- Setting A: HotpotQA / 2WikiMultiHopQA split-evidence，两个 agent，5-5 context split，每边一个 gold paragraph + 四个 distractors。
- Diagnostic 里最多 8 turns，max_new_tokens 8192；PACT experiments 用 4 alternating turns，max_new_tokens 4096。
- Setting B: Planner -> Critic -> Refiner -> Solver 四 agent pipeline，AIME2024/2025、GPQA-Diamond、OpenBookQA。

外部发现：

- Full Content 代价高且常常落后于其他通信策略。
- 短消息本身不够，关键是 action-centered information 加可复用 state。
- PACT 平均减少 38.7% token，同时保持或改善性能；SWE-agent tokens-per-resolved 约降 47%。

和我们的差别：

- 我们用 Qwen2.5-14B，外部 PACT 用 Qwen3-8/14/32B。
- 我们的 PACT run 多是 saved-field re-answer stress test，尚未完整复现 split-evidence multi-turn protocol。
- 我们 temperature 0、max tokens 64 的 field packet 更像严苛诊断；外部设置给了更长输出和采样空间。

## TeamBench

来源：

- paper: `https://arxiv.org/html/2605.07073v1`
- code: `https://github.com/ybkim95/TeamBench`

外部设置：

- OS-enforced Planner / Executor / Verifier role separation。
- Leaderboard 覆盖 Claude、GPT、Gemini、Gemma、gpt-oss、Qwen3 等模型族。
- 每个模型在 Solo、Restricted、No Plan、No Eval、Full 等条件下比较。

外部结果：

- Full 条件里 Claude Opus 4.7 约 37.8%，GPT-5.4 Mini、Claude Haiku 4.5、Gemini-3.1 Pro 约 28.9%。
- Gemma 4 31B Full 约 22.2%。
- Qwen3-14B Full 约 2.2%，Qwen3-32B Full 约 1.1%，Qwen3-8B Full 0.0%。
- 论文解释 Qwen3 family 低分主要来自 malformed tool calls 和 context overflow。

和我们的差别：

- TeamBench 是工具调用、文件系统隔离、角色权限三者耦合的工程 benchmark。
- 我们当前机器无 Docker，无法跑它最核心的 OS-enforced 版本。
- 14B 在这类 benchmark 上风险极高，可能测到 tool-use/runtime fragility，难以隔离通信协议本身。

## EnactToM

来源：

- paper: `https://arxiv.org/html/2605.09826v2`

外部设置：

- 300 embodied multi-agent tasks，standard/hard 各 150。
- partial observability、private information、constrained communication。
- 每个 task 跑 3 次，报告 Avg、Pass@3、Pass^3，强调 Pass^3。
- 模型包括 Gemini-Pro、Gemini-Flash、GPT-5.4、O3、Kimi-K2.5、GPT-5.4-mini、DeepSeek-v3.2。

外部结果：

- hard split 上所有 7 个 frontier models functional Pass^3 都是 0.0%。
- standard split 上 Gemini-Flash overall functional Avg 42.5%、Pass^3 22.5%，Gemini-Pro Avg 39.2%、Pass^3 12.5%。
- hard literal belief probe 上 Gemini-Pro 和 O3 较强，但 functional coordination 仍崩。

和我们的差别：

- 它测的是 embodied action + information routing，而我们当前多是文本 re-answer。
- 它的强点是把“会说出 belief”和“能用 belief 完成协作”分开。

## SOTOPIA-TOM

来源：

- paper: `https://arxiv.org/pdf/2605.02307`

外部设置：

- 160 human-reviewed scenarios，8 个行业，3 到 5 agents。
- public broadcast + private direct message channel。
- 每个 agent 有 role-specific private facts、sharing policy、do-not-share secrets。
- 六个 LLM backbones：GPT-4o、GPT-5-nano、GPT-5 high reasoning、Llama-4-Maverick、Qwen3-235B-A22B thinking、DeepSeek-R1。
- 四种 prompting/intervention：baseline、CoT-Privacy、ToM-Belief、ToM-Coach。

外部结果：

- 最好配置 INFOMGMT 只有 0.62。
- ToM-Belief 在五个模型上 overall 最强。
- ToM-Coach 最稳定地降低 privacy violations。
- Inquiry Alignment 是持续瓶颈，baseline direct-message 使用率低，信息交换集中在前几轮。

和我们的差别：

- 这个 benchmark 最贴近“谁知道什么、该问谁、该用公开还是私聊、什么不能泄露”。
- 它比 HiddenBench 多了 privacy/channel policy，但评估更依赖 LLM judge。
- 可以作为中期主线候选，尤其适合我们的 public-state admission 和 channel contract。

## Collab-Overcooked

来源：

- paper: `https://arxiv.org/html/2502.20073v3`

外部设置：

- 30 tasks，6 个复杂度 level，Overcooked-AI interactive environment。
- 13 个模型，覆盖 GPT、Claude、DeepSeek、Qwen2.5、Llama。

外部结果：

- Claude Sonnet 4 最强，Level 1 到 Level 6 success rate 从 100% 到 58%。
- o4-mini 和 DeepSeek-R1 很强，Level 6 仍有 54% 和 30% success rate。
- Qwen2.5-14B-Instruct 很弱：Level 1 success rate 32%，Level 2 4%，Level 3 到 Level 6 为 0%。
- Qwen2.5-72B 明显强于 14B，但高复杂度仍塌。

和我们的差别：

- 这是 active collaboration / continuous adaptation，和纯事实整合距离较远。
- 它直接提醒我们：Qwen2.5-14B 在交互协作任务上可能低估协议上限。

## TheAgentCompany

来源：

- arXiv version: `https://arxiv.org/html/2412.14161v1`
- NeurIPS dataset/benchmark version: `https://papers.nips.cc/paper_files/paper/2025/file/0d744742f6fac4d1134c019b7cef3c8a-Paper-Datasets_and_Benchmarks_Track.pdf`

外部设置：

- realistic software-company tasks，agent 需要 browse web、code、run programs、communicate with coworkers。
- 使用 OpenHands CodeAct agent。
- arXiv v1 报告 7 个 backbones；NeurIPS 版本报告 12 个 backbones。

外部结果：

- arXiv v1 中 Claude-3.5-Sonnet success 24.0%，score 34.4%；Qwen-2.5-72B success 5.7%，score 11.8%。
- NeurIPS 版本摘要中 Gemini 2.5 Pro success 30.3%，score 39.3%。
- open-weight 模型整体落后 closed frontier，且成本/步数并不自动更低。

和我们的差别：

- 这是完整 agent harness 任务，不只是通信必要性。
- 它适合说明真实工作流难度，但短期不适合承载我们最干净的机制 claim。

## 结论：14B 的定位

Qwen2.5-14B 现在应被降级为 debug / cheap diagnostic backbone。它可以帮我们快速发现协议是否漏答案、parser 是否可靠、packet 是否过脏、控制是否坏掉；它暂时不适合单独承载“多 agent 通信机制”的最终 claim。

下一轮主实验最好采用三层模型矩阵：

1. Cheap diagnostic: Qwen2.5-14B，沿用本地 vLLM。
2. Open stronger: Qwen3-32B、Qwen3-235B-A22B、DeepSeek-R1、Qwen2.5-72B、Llama 70B/405B 中至少一个。
3. Closed frontier: Gemini 2.5 Pro/Flash、Claude Sonnet/Opus、GPT-4o/GPT-5 high 中至少一个。

若资源有限，最小可发表路线是：

1. HiddenBench protocol v2 on Qwen2.5-14B，先证明 packet 与 evaluator 干净。
2. 同一协议跑 Qwen3-32B 或 Qwen2.5-72B，检查机制方向是否保留。
3. 同一协议跑一个 Gemini/Claude/GPT frontier baseline，判断协议是否只在 14B 上成立。
4. PACT split-evidence 用 Qwen3-14B 或 32B 对齐原论文设置，再比较我们的 field-contract/admission protocol。

如果 v2 只救 Qwen2.5-14B，结论只能写成模型诊断。如果 v2 同时救 open stronger 和 closed frontier，且 shared-only / full-info / oracle-public-facts controls 保持同样方向，那才接近真正有说服力的通信必要结果。
