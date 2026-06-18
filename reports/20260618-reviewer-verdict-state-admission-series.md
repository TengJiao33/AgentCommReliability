# Reviewer Verdict: State Admission Series

日期：2026-06-18

## 一句话审判

如果按 A 会审稿口径看，当前系列最容易被拒的点是问题对象还容易被读成“又一个 context routing / memory packing / role assignment 变体”。实验数量也偏少，但真正值得保留的是更窄的 failure object：模型能守住显式 scope，却会把局部事实的 blocker/enabler 极性接错，导致答前 admission unit 构造失败。

## Reviewer #2 会怎么打

第一条拒稿理由会是贡献边界不清。DeLM 已经把 shared verified context 和 task queue 讲得很完整；CICL 已经把 decision-aware evidence selection、typed memory cards 和 budget packing 占住；PerspectiveGap 已经把 multi-agent role-fragment assignment benchmark 占住；ProvenanceGuard 已经把 source-aware factuality verification 占住。我们如果继续说 State Admission 是一种“更可靠多 agent 通信协议”，会被直接归到这些邻域里。

第二条拒稿理由会是评价对象太人工。V1.1 的 bundle、group、cost、utility 来自 builder；强符号 `group_density_global` baseline 已经有 `32/40` strict 和 `0.9666` utility ratio。审稿人会说：你们的模型没有发现结构，最多是在一个人工规划表上排序。

第三条拒稿理由会是 downstream 太弱。V2 smoke 虽然接了 HiddenBench decision proxy，但只有 9 行，且第一版 prompt 没强制 per-option state。审稿人会担心 `unit_recall=0.2222` 只是格式或 prompt artifact。

第四条拒稿理由会是 claim 太像“模型失败学”。如果只展示 Qwen2.5-7B 在小包上 `0/9`，没有 14B/frontier 对照、没有 prompt/schema ablation、没有 strong context baselines，审稿人会说这只是小模型能力不足。

## 现在还能保留什么

V1.1 priority executor 可以保留为工具链证据。它说明 direct admitted-state generation 会爆 budget/empty-role 边界，确定性 executor 可以把合法性错误压下去。它不适合当主贡献。

V1.1 ledger-first collapse 可以保留为断点证据。Qwen2.5-7B 在隐藏 units 时只有 `1/40` strict 和 `0.0409` utility，它提示 unit construction 是独立难点。它不能单独说明真实任务也有同样难点。

V2 GPU smoke 可以保留为第一个自然任务行为信号。Qwen2.5-7B 在 9 行上 `scope_violations=0.0000`，但 `unit_recall=0.2222`、`downstream_ok=0.0000`。这比“模型乱共享”更窄：模型没有乱越权，主要错在事实极性和 option-level admission unit。

## 应该砍掉或降级的东西

不要再把 PerspectiveGap-derived synthetic rows 放在首包中心。它们太容易被 PerspectiveGap 原 benchmark 吸走贡献解释，只适合作为 source/scope stress supplement。

不要继续扩 V1.1 prompt sweep。V1.1 已经完成了它的任务：指出 direct state generation、priority executor、ledger-first hidden unit 三个层级的断点。

不要把 `State Admission` 当方法名先推。它现在更像问题对象或 benchmark slice。更好的标题候选是 `Role-Scoped Evidence Admission` 或 `Local Evidence Admission under Source and Scope`，先把 failure benchmark 站稳。

不要让 shared-context baseline 只是一个陪跑。Shared context 是外部压力最大的邻居，必须成为强 baseline 和失败诊断对象。

## Out-of-box 调整

把主问题从“选择哪些 facts 进入 role local context”改成“答前证据是否能形成正确的 option-state matrix”。每个 option 先判 `blocked`、`enabled`、`insufficient`，再由这些状态生成 admission units。这样可以把 semantic polarity failure 和 JSON unit formatting 分开。

把 contribution 从 protocol claim 改成 measurement claim。当前更可信的论文对象是一个 stress test：在 source ownership、recipient scope、verification state、dependency edge 变化时，模型是否保持局部证据的极性和准入状态一致。

把 baseline 重新排序。第一梯队应是 oracle option-state、shared verified context、CICL-style card packing、direct answer-from-all-facts、direct answer-from-admitted-facts、model option-state-first。Model protocol 只有在这些 baseline 后面。

把 external pressure 扩到权限与泄漏。AgentLeak 会问内部通道是否泄漏；OrgAccess/RBAC 类 benchmark 会问角色权限是否真的被执行。我们的 next packet 应加入至少一种 privacy/RBAC-style reject，而不只做 option choice。

把成败门槛变得更狠。下一轮 9-row GPU 对照如果 `option_state_first` 让 7B 大幅恢复，第一版失败主要是 schema/prompt artifact；如果 14B 仍错 polarity，才值得扩到 30-50 rows；如果 direct answer-from-all-facts 也错，说明 HiddenBench row 本身或任务语义可能太弱。

## 新实验形态

下一步应先跑同一 9 行的 schema ablation，暂时不要扩大样本：

1. `unit_first_7b`: 已完成，`strict=0.0000`、`unit_recall=0.2222`、`downstream_ok=0.0000`。
2. `option_state_first_7b`: 新 runner 已支持。要求模型先输出 per-option `blocked/enabled/insufficient`，再输出 admission units。
3. `option_state_first_14b`: 同一 packet、同一 prompt、同一 scorer，用来判断失败是否主要来自 7B 能力。
4. `direct_answer_all_facts`: 给所有 facts，不要求 admission，检查任务本身是否可由模型理解。
5. `direct_answer_admissible_facts`: 只给 oracle-admitted facts，检查 downstream task 是否被 admission units 正确支持。

这个设计能把四种失败分开：

- task understanding failure：direct answer all facts 也错；
- admission compression failure：all facts 对、admitted facts 错；
- option-state failure：option_state_first 也错；
- unit formatting failure：option_state 对、admission_units 错。

## 对外部工作的重新定位

DeLM 压 shared substrate，所以我们的 claim 必须强调同一事实对不同 recipient 的 admissibility 不同。来源：https://arxiv.org/html/2606.10662v1

CICL 压 decision-aware card packing，所以我们的 baseline 必须实现 budgeted evidence card packing，不能只口头比较。来源：https://arxiv.org/abs/2606.08151

PerspectiveGap 压 role-fragment assignment，所以我们应避免把 fragment assignment 当主要结果。来源：https://arxiv.org/html/2606.08878v1

ProvenanceGuard 压 source-aware answer verification，所以我们的时间点要固定在 answer 前的 admission，而不是 answer 后 attribution。来源：https://arxiv.org/abs/2606.18037

AgentLeak 和 OrgAccess 类压力提示 reviewer 会关心内部通道和权限合规。它们不会直接吃掉我们，但会要求我们把 privacy/RBAC-style rejection 加进 packet。来源：https://arxiv.org/html/2602.11510v3 和 https://openreview.net/forum?id=oyjdyS7hBZ

## 新的 go / no-go

Go 条件：`option_state_first_14b` 在同一 9 行上仍出现高比例 polarity/dependency 错误，且 direct-answer controls 能说明任务本身可解。满足这个条件后，扩到 30-50 rows 才有意义。

No-go 条件：`option_state_first` 一改就接近 oracle，且 direct-answer controls 都很强。这时 State Admission 不该继续当主线，应该降级为 prompt/schema engineering note。

Pivot 条件：如果 direct-answer controls 也不稳，HiddenBench-derived row 不适合承载 admission story。方向应转向 RBAC/privacy-style source-scope admission，因为那里 gold boundary 更自然，外部压力也更清楚。

## 立即动作

我已经把 `scripts/run_state_admission_v2_openai_compatible.py` 改成支持 `--prompt-style option_state_first`，把 `scripts/run_state_admission_v2_a8002.sh` 改成支持 `PROMPT_STYLE=option_state_first`，并在 `scripts/score_state_admission_v2.py` 中加入 `option_state_recall`。本地 oracle 在新指标下仍是 `9/9` strict，旧 7B 输出在 `option_state_recall` 上是 `0.0000`，这给下一次 GPU 对照留下了干净入口。
