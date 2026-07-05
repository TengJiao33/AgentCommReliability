# AgentCommReliability

本仓库是围绕 agent communication reliability 的实验与机制记录工作区。2026-07-03 之前的旧路线已从 live workspace 清理；当前 live surface 从 2026-07-04 起重新形成了 MATH/AIME 多 agent reasoning 的实验证据面。

## 当前状态

当前活跃问题是：多 agent 推理的可靠性瓶颈到底来自候选答案覆盖不足、候选识别失败，还是通信/聚合协议把有用分歧处理坏了。

最近证据集中在三组本地 full/smoke run：

- `experiments/20260704-a8002-math500-mad-mm-qwen25-7b-full/`：MAD-MM/MAD-M2 MATH-500 full 复现诊断。当前读数为 `naive` 375/500、`subjective` 369/500、`objective` 360/500；memory masking 没有优于 naive debate。
- `experiments/20260705-a8002-math500-basic-mad-qwen25-7b-full/`：basic MAD MATH-500 full 对照。Direct 347/500，basic MAD final majority 333/500。
- `experiments/20260705-a8002-math500-cqg-divergent-qwen25-7b-full/`：Consensus Quarantine Gate（CQG）MATH-500 full 诊断。记录内 same-run initial majority 320/500，CQG final 337/500，净增 17 题。
- `experiments/20260705-a8002-math500-cpac-dcac-qwen25-7b-full/`：CPAC+DCAC MATH-500 full 诊断。记录内 same-run initial majority 320/500，CPAC+DCAC final 325/500，净增 5 题；分支分解显示正净值来自 no-majority listwise 分支，不来自 DCAC。

这些结果都是 diagnostic evidence，不是最终方法 claim。尤其是 CQG 的正增益还不能归因于 appeal gate；当前更像是 blind re-solve/review 对 divergent cases 的作用。

## 当前机制词汇

- `CQG`：已实现并跑过 full split 的 Consensus Quarantine Gate。它把 non-unanimous initial majority 放入 quarantine，让 blind reviewers 在隐藏支持数后重新裁决。
- `DCAC`：Disagreement-Conditioned Admissibility Certificate。它把 2:1 多数/少数分歧转成候选答案差异诱导的准入证书，目标是区分 informative minority 和 seductive wrong minority。
- `CPAC`：Candidate-Pool Adaptive Consensus。它先诊断候选池状态，再决定早停、扩候选、调用 DCAC、或进入 list-wise discriminant identification。
- `MCE`：机制草图，Metacognitive Cue Exchange。它尝试交换 answer-free 的认知 cue，而不是最终答案或完整 rationale。

当前较稳的叙事是：CPAC 作为外层状态诊断框架，DCAC 作为 `unique=2` / minority-bearing 状态下的证书化决策分支；MCE 可作为 CPAC 在 collapse、minority-bearing、no-majority conflict 中调用的更细粒度通信动作。

`scripts/run_cpac_dcac.py` 已落下 CPAC+DCAC runner，并完成第一轮 MATH-500 full 诊断；当前结果仍不是 claim-bearing 方法证据。

## 重要 Caveat

当前 evaluator 与已写入部分 CQG summary 的判定口径存在小范围差异，集中在 `\pi`、矩阵/列向量、base notation、`\cot x` 等 representation-risk 格式。CQG 的记录内净增仍为 +17，但绝对准确率和 oracle/pool-state 分解在正式 claim 前需要统一 evaluator 口径。

## 入口

- `active/README.md`：当前活跃路线与机制假说。
- `reports/README.md`：报告和 idea 记录索引。
- `experiments/README.md`：实验 run 索引。
- `docs/`：机器、同步、资源和实验协议文档。
- `tests/`：本地 evaluator 与 CQG runner 的轻量单元测试。

## 操作元数据

保留的机器和流程来源：

- `docs/machine_quickstart.md`
- `docs/machine_handbook.md`
- `docs/server_resource_inventory.md`
- `docs/remote_sync_manifest.md`
- `docs/project_physical_management.md`
- `docs/experiment_protocol.md`
