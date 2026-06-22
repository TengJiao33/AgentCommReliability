# PerspectiveGap 公开榜单与论文比较路线校正

Snapshot date: `2026-06-18`.

## 核心判断

这份计划需要校正：PerspectiveGap 官方榜单可以作为外部参考和可选冲榜路线，但不应成为当前 A 会论文的 P0 硬目标。把 `openai/gpt-5.5` 的 `273/440 = 62.0%` 当作必须超过的门槛，会把项目导向和闭源 frontier model 拼榜单，而这并不是当前机制论文最稳的评价方式。

当前 P0 应回到 paper-facing protocol：同一 backbone、同一预算、同一 released grid 或同一公开切片下，比强可复现 baseline、transparent control、oracle/control gap 和我们自己的 system decomposition。PG40、HSA-v0、State Admission 与 PerspectiveGap official full grid 的关系应是方法开发、外部压力和可复现对照，而不是单一闭源榜单攻坚。

## 当前证据

本地官方 benchmark 接触是干净的。`baselines/PerspectiveGap/upstream` 当前 commit 是 `60b1dcaaeeb40619075f6cd8779c47fa4b344391`，`git ls-remote` 显示远端 HEAD 也是同一个 commit。官方测试用本地 venv 重跑通过：`18 passed in 2.57s`。

官方提交规则也已经核清。`SUBMIT_RESULTS.md` 要求 full released grid：`110` 个 scenarios、shuffle seeds `1` 和 `42`、两个任务 `role_assignment` 和 `prompt_writing`，共 `440` 个 prediction rows 和 `440` 个 score rows。官方还要求提交 raw prediction JSONL、score JSONL、summary text 和完整 run metadata。

本地已有结果说明 Qwen2.5 直接 prompt 还离 SOTA 很远。PerspectiveGap stratified20 上，Qwen2.5-7B role assignment 是 strict `0/40`、coverage `0.443`、precision `0.786`、leak `0.050`；Qwen2.5-14B 是 strict `0/40`、coverage `0.615`、precision `0.808`、leak `0.450`。这提示直接把本地 7B/14B 扩 full220 不会冲榜。

## 新增组件

我新增了一个本地工具：

```text
scripts/perspectivegap_assignment_to_prompt_predictions.py
```

它把 PerspectiveGap role-assignment prediction JSONL 转成 prompt-writing prediction JSONL：每个 role 一个 markdown section，section 内按预测 fragment id 展开完整 fragment block，并用中性 `<fragment id="...">...</fragment>` 标签阻断跨片段 n-gram 假阳性。

本地 scorer smoke 已通过。oracle role assignment 经过这个工具转成 prompt-writing 后，官方 prompt-writing scorer 是 `220/220` strict、coverage `1.0000`、precision `1.0000`、distractor leakage `0.0000`。这说明 prompt-writing 可以作为路由结果的确定性展开，而不必完全交给模型自由写。

真实模型输出也能接上这个工具。此前 stratified20 的 Qwen2.5-7B / 14B role-assignment predictions 都能 `40/40` 转换成功。转换后的 prompt-writing 分数保留了原路由轮廓：7B prompt-writing coverage `0.4426`、precision `0.8536`、leak `0.0500`；14B coverage `0.6148`、precision `0.8078`、leak `0.4500`。

我又新增了一个 no-gold ensemble 工具：

```text
scripts/perspectivegap_ensemble_role_assignments.py
```

它只读取已有 prediction 的 response、官方 rendered roles 和 fragment ids，不读取 `reference_need_sets`、score rows 或 oracle 派生字段。用已有 7B/14B stratified20 做 union 和 intersection 后，union 的 role-assignment coverage 到 `0.6648`、precision `0.7606`、leak `0.4500`；intersection 的 precision 到 `0.9680`、coverage 降到 `0.3926`、leak `0.0500`。两者 strict 仍是 `0/40`。

这个结果把下一步压力变清楚了。简单 set-level ensemble 可以调 coverage/precision tradeoff，但不能解决 exact-row pass。SOTA 路线需要更多样的 prompt arms、强模型或 row-level repair；仅靠 7B/14B union/intersection 不值得扩 full220。

## 论文比较路线

第一条路线是同模型公平比较。用同一个 open model 或同一个 openai-compatible endpoint，在官方 direct prompt、recall-heavy prompt、precision-guarded prompt、source-ledger、deterministic prompt writer、repair/ensemble router、SSEAC-style admission route 之间做 paired comparison。主指标仍可保留 strict pass、coverage、precision、leakage 和 cost，但核心读法是同条件下机制分解是否带来增益。

第二条路线是强可复现 baseline ladder。PerspectiveGap official direct、all-to-all、no-distractor、shared-intersection、utility/coverage oriented transparent heuristic、source-ledger compiled、SSEAC compiled、oracle assignment-to-prompt 都应在同表出现。这样 reviewer 能判断提升来自 routing/admission mechanism，而不是来自 prompt surface、post-processing 或模型规模。

第三条路线是公开榜单参考。`273/440` 可以保留为 frontier ceiling 和 optional leaderboard route。如果我们后来有强 endpoint、clean metadata、full grid artifacts，并且 system route 在同模型表里已经站住，再提交榜单或报告 transparent system score。这个分数不该决定当前是否有论文故事。

## 必须守住的边界

官方 scenario markdown 的 frontmatter 里包含 `reference_need_sets`。这对 scorer 和 oracle smoke 是合法的，对 prediction-time system 是禁区。任何官方或 paper-facing run 都不能读取 `reference_need_sets`、SSEAC `required_slots`、PG40 `recipient_scope`、oracle assignment、derived gold labels 或 scorer输出。

PG40 / SSEAC packet 也不能直接作为官方预测输入。它包含从 reference 派生出的 `recipient_scope`、`required_slots` 和 `reference_need_sets`，适合作为方法开发压力和 ablation，不适合作为 PerspectiveGap 官方提交。

所有 wrapper、retry、repair、post-processing 和 deterministic prompt writer 都必须在 run metadata 里明示。若官方只收 direct model results，我们把它标成 system result；若官方接受 equivalent runner with post-processing，再按官方提交规则准备 artifacts。

## 下一轮实验门

Purpose: 判断一个不读 gold 的 PerspectiveGap system route 能否在 same-backbone / same-budget 设置下，稳定超过 direct upstream prompt 和强可复现 routing/admission baselines。

Unit: 一个 PerspectiveGap task request，官方 full grid 共 `440` rows。

Primary contrast: `system_role_assignment + deterministic_prompt_writer` versus same model direct upstream runner。

Secondary contrasts: direct role assignment、direct prompt writing、conservative router、recall-heavy router、ensemble/repair router、oracle assignment-to-prompt smoke。

Success signal: 在 same-model fair table 中比 direct upstream runner 和主要 reproducible baselines 明显提高，同时 leakage 不上升；若 full grid combined pass 接近或超过公开 frontier 分数，再把它标成 optional leaderboard result。

Failure signal: 提升只来自泄漏、oracle-derived fields、answer-key exposure、scorer artifact；或 system route 只改善连续 coverage/precision，却不能带来 strict pass、leakage、cost 或 downstream prompt-writing 的实质增益。

Invalidation conditions: prediction-time 读取 `reference_need_sets` 或 derived oracle fields；row count 不是 `440`；scenario/seed/task 覆盖不完整；score rows 与 prediction rows 不对应；post-processing 未记录；prompt-writing 只优化 n-gram scorer 且破坏 full-block instruction。

Expected artifacts:

```text
experiments/<run-id>/predictions_<system>.jsonl
experiments/<run-id>/scores_<system>.jsonl
experiments/<run-id>/summary_<system>.txt
experiments/<run-id>/README.md
reports/<date>-perspectivegap-official-sota-run.md
```

## 立即动作

1. 先跑 same-endpoint direct baseline，优先 full grid；资源不足时先用 stratified20 / PG40 做 paired pilot。
2. 做 no-gold role-assignment system wrapper：多路 prompt arm 输出 role->fragment JSON，repair 只允许基于 response 语法、role list、fragment ids 和 prompt文本。
3. 避免只做 7B/14B set voting。已有 union/intersection smoke 显示它只改变连续指标，不能产生 strict pass。
4. 把 system role assignment 接 `scripts/perspectivegap_assignment_to_prompt_predictions.py`，生成 prompt-writing rows。
5. 拼接 role-assignment rows 和 deterministic prompt-writing rows，跑官方 scorer，检查 row 完整性、leakage、cost 和 prompt-writing 保真。
6. 若 same-model table 出现稳定增益，再扩 full grid 和跨模型；若只接近公开 frontier 分数，再考虑榜单提交。
