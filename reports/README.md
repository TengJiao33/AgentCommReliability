# Reports

本目录记录当前 live workspace 中会影响研究判断的报告、机制札记和文献吸收表。2026-07-04 之前的旧路线不在这里恢复；如需审计旧材料，应从 Git 历史取证。

## 实验诊断

- `2026-07-04-mad-mm-aime.md`：MAD-MM/MAD-M2 在 AIME24/25 上的 full split 复现诊断。当前结果没有支持继续扩大同一 memory masking 设置。
- `2026-07-04-mad-mm-math500.md`：MAD-MM/MAD-M2 在 MATH-500 上的 full split 复现诊断。`naive` 375/500 最好，`subjective` 369/500，`objective` 360/500。
- `2026-07-05-cqg-math500-full.md`：CQG 在 MATH-500 full split 上的第一轮完整诊断。记录内 initial majority 320/500，CQG final 337/500。
- `2026-07-05-cpac-dcac-math500-full.md`：CPAC+DCAC 在 MATH-500 full split 上的第一轮完整诊断。记录内 initial majority 320/500，CPAC+DCAC final 325/500；净增主要来自 listwise 分支，不来自 DCAC。
- `2026-07-05-cpac-dcac-raw-sample-investigation.md`：深入 CPAC+DCAC full run 的原始样本、claim/certificate、listwise 输出和分支作用链，说明 CPAC 有状态诊断价值，但当前 DCAC 分支为负贡献。
- `2026-07-05-cpac-dcac-guard-v1.md`：记录 DCAC 保守翻盘准入 v1 的源码改动、测试结果和基于旧 full records 的离线反事实回放；该回放显示旧证书下可挡住 4 个伤害和 3 个错到错，但不是新 full run。

## 机制提炼

- `2026-07-05-cqg-failure-mechanism-synthesis.md`：从 CQG 的恢复/伤害分解中提炼 DCAC。核心问题是 minority-release 同时带来 `MaW -> C` 和 `MaC -> W`。
- `2026-07-05-candidate-space-diversity-investigation.md`：分析初始候选池的 `unique=1/2/3` 三态、oracle@3 空间和 CQG 覆盖盲区。
- `2026-07-05-candidate-space-critical-absorption.md`：吸收 candidate diversity、dynamic debate、adaptive routing 等相关工作后，提出 CPAC 作为更窄的 candidate-pool state diagnosis 路线。
- `2026-07-05-metacognitive-cue-exchange.md`：记录 MCE 机制想法，即交换 answer-free metacognitive cue，而不是完整答案或 rationale。
- `2026-07-05-mca-implementation-options.md`：记录 MCA 的四档源码实现方案：显式 text cue、soft prefix、KV/hidden state communication、activation steering。
- `2026-07-05-mce-source-implementation-plan.md`：调研 MCE/MCA 的文献避撞和源码落地方式，建议先做 standalone diagnostic runner，再并入 CPAC action。

## 文献和对照

- `2026-07-05-mad-mechanism-improvement-table.md`：MAD 机制改善论文表，按方法、benchmark、正文可核验提升幅度整理。

## 读法 Caveat

这些报告应按 evidence record 阅读。CQG full run 有同 run 正增益，但不是最终方法 claim；DCAC、CPAC、MCE 当前是机制草图，还没有独立 full-run 证据。

当前 evaluator 对部分 representation-risk 答案存在口径差异。涉及 `\pi`、矩阵/列向量、base notation、函数表达式等结论时，需要回到原始 records 和 evaluator 版本核对。

## Templates

- `reports/_templates/short_report.md`
- `reports/_templates/objective_research_report.md`
