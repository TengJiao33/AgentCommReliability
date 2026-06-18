# PerspectiveGap Model Smoke and Paper Story Pressure

## 核心判断

今晚的新增证据把主线从“私有证据污染偏好”推宽了一格：更有空间的题眼是 role-specific information routing。系统要决定哪些事实、规则、评分标准、工具输出、来源标签进入哪个 agent 的可见状态；错误既可能是过度共享，也可能是覆盖不足。

这条路有外部 benchmark 接触，也能接上优秀论文的 story。多 agent 通信方向里，最强的近期故事把通信当成受约束的信息流：带宽稀缺、拓扑稀疏、任务割限制、source ownership、artifact provenance 都可测。

## 新跑的模型接触

我在 A800_2 上先用官方 PerspectiveGap runner 跑了两个小 smoke。范围保持一致：`pg_000`, `pg_004`, `pg_006`, `pg_070`，shuffle seed `1`，只跑 `role_assignment`。

| Model | Strict | Coverage | Precision | Distractor leak/eval | Counts |
| --- | ---: | ---: | ---: | ---: | --- |
| Qwen2.5-7B-Instruct | 0/4 | 0.549 | 0.903 | 0.000 | tp=28, fp=3, fn=23, leak=0 |
| Qwen2.5-14B-Instruct | 0/4 | 0.667 | 0.872 | 0.250 | tp=34, fp=5, fn=17, leak=1 |

Artifacts:

- `experiments/20260618-a8002-perspectivegap-role-assignment-smoke-qwen25-7b/`
- `experiments/20260618-a8002-perspectivegap-role-assignment-smoke-qwen25-14b/`
- paired diff: `experiments/20260618-a8002-perspectivegap-role-assignment-smoke-qwen25-14b/case_diffs.md`
- paired JSON: `experiments/20260618-a8002-perspectivegap-role-assignment-smoke-qwen25-14b/paired_summary.json`

两次 run 都完成 `4/4` 请求，runner stderr 为空。GPU 7 和端口 `8061/8062` 都在 run 后清理干净。

随后我加了一个很薄的 zero-temperature 项目 runner：`scripts/run_perspectivegap_role_assignment_openai_compatible.py`。它复用 PerspectiveGap upstream renderer 和 scorer 输出格式，只暴露 `temperature/max_tokens`。用它跑了 `20 scenarios x 2 seeds` 的 stratified subset，覆盖 role count `2, 3, 4, 5, 6`，每个模型 `40` 条请求。

| Model | Strict | Coverage | Precision | Distractor leak/eval | Counts |
| --- | ---: | ---: | ---: | ---: | --- |
| Qwen2.5-7B-Instruct | 0/40 | 0.443 | 0.786 | 0.050 | tp=239, fp=65, fn=301, leak=2 |
| Qwen2.5-14B-Instruct | 0/40 | 0.615 | 0.808 | 0.450 | tp=332, fp=79, fn=208, leak=18 |

Stratified artifacts:

- `experiments/20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b/`
- summary: `experiments/20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b/stratified_summary.md`
- JSON: `experiments/20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b/stratified_summary.json`

## 机制读数

7B 的主要失败形态是 under-routing：它倾向于只给每个角色最显然的片段，漏掉共享背景、循环规则、写作约束等跨角色需要的状态。它几乎不乱给，precision 很高，distractor leak 为 0。

14B 的主要变化是 recall 上升：它多找回了 6 个 required events，fn 从 23 降到 17。但这个提升伴随更多 false positive，且在 `pg_000` 把 distractor `f2` 给了 reviewer。这个小样本提示一个值得追的现象：模型变强后可能更敢分发上下文，role boundary 风险随之上升。

stratified20 强化了这个读数。14B 相比 7B 多了 `93` 个 true positive，fn 少了 `93` 个；同时 distractor leak 从 `2` 增到 `18`。precision 在这个子集上 14B 略高，说明它的额外风险来自更强覆盖中夹带更多诱饵。这个现象比旧的偏好污染更可写。它提出了一个可评分的张力：orchestrator 必须同时优化 required coverage、boundary precision 和 source/distractor rejection。PerspectiveGap 正好惩罚两端失败，HiddenBench 则提供下游决策的通信必要性压力。

## ArXiv_Daily_Digest 和外部 story

ArXiv_Daily_Digest 已经拉到最新，当前 `2026-W25` 有 JSONL，但尚未生成 weekly digest。W24/W25 的高价值信号集中在四类：

- communication budget: DALA / auction-based communication，把带宽当稀缺资源，诱发 strategic silence；
- topology: Sparse-MAD 系统比较通信连通性，说明 fully-connected 不应作为免检默认设计；
- task structure: information-theoretic work 把 multi-agent success 绑定到 task constraint graph 的 cut cost；
- provenance/source ownership: ProvenanceGuard、Context-Fractured Decomposition、Misinformation Propagation 都把来源、artifact lineage、错误传播作为主变量。

外部锚点：

- PerspectiveGap: https://arxiv.org/abs/2606.08878
- DALA / Cost-Effective Communication: https://arxiv.org/abs/2511.13193
- AAAI DALA paper PDF: https://ojs.aaai.org/index.php/AAAI/article/view/40182/44143
- Sparse-MAD: https://aclanthology.org/2024.findings-emnlp.427/
- Task-structure bound: https://arxiv.org/abs/2606.13733
- ProvenanceGuard: https://arxiv.org/abs/2606.18037
- Context-Fractured Decomposition: https://arxiv.org/abs/2606.09084
- Misinformation Propagation: https://arxiv.org/abs/2606.16710

如果你问“多 agent 通信我现在最认可哪篇”，我会选 DALA 这条 AAAI story。它的优点是问题锋利：free-for-all communication 造成 token 成本和低信噪比；机制简单：agents 通过拍卖争取发言权；现象好记：resource constraint 诱发 strategic silence；评测覆盖多个 reasoning benchmarks。Sparse-MAD 也优秀，但它更像拓扑消融；DALA 更像一个能长出方法论的通信机制。

## 方向判断

多 agent 通信作为“辩论/共识/互相说服”已经拥挤，而且很多 benchmark 容易饱和。继续在 MATH 或 GSM8K 上调消息格式，容易把故事做浅。

role-specific routing 还没那么饱和，因为它把失败从最终答案提前到编排层：什么信息应该进入哪个 role 的 prompt，什么信息必须带 source/scope，什么信息应该保持不可见。这个问题可以连到 agent harness、workspace、MCP provenance、技能供应链和真实工程工作流。

benchmark 的问题确实存在。若 benchmark 只看 final answer，通信机制会被单模型能力、parser、prompt surface 吞掉。更合适的 benchmark 要同时惩罚 missing-needed 和 over-sharing，并且有 answer key 或 trace key。PerspectiveGap 和 ProvenanceGuard 这类题型更适合当前阶段。

## 下一步

我建议下一步直接在 stratified20 上加两个 controlled router arms：

- typed-router prompt，要求每个 fragment 标注 `recipient`, `scope`, `source`, `reason`；
- budgeted-router prompt，每个 role 有 fragment budget，测试是否能提高 precision 但保持 coverage；
- optional provenance-router，把每个 fragment 先转成带 `source`, `scope`, `visibility` 的 state card。

读数不要只看 strict pass。最重要的是 coverage/precision/leak 三角、跨模型的 aggression shift，以及 typed/budgeted router 是否把 14B 的 recall 保住同时压低 false positives。

如果这组成立，新的 A 会 idea 可以写成：multi-agent orchestration needs a state-routing layer under communication scarcity and provenance constraints。它比“私有证据变偏好污染”更大，也更能接住 benchmark、机制、设计和实验。
