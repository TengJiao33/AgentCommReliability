# Reports

本目录记录当前 live workspace 中会影响研究判断的报告、机制札记和文献吸收表。2026-07-04 之前的旧路线不在这里恢复；如需审计旧材料，应从 Git 历史取证。

## 实验诊断

- `2026-07-04-mad-mm-aime.md`：MAD-MM/MAD-M2 在 AIME24/25 上的 full split 复现诊断。当前结果没有支持继续扩大同一 memory masking 设置。
- `2026-07-04-mad-mm-math500.md`：MAD-MM/MAD-M2 在 MATH-500 上的 full split 复现诊断。`naive` 375/500 最好，`subjective` 369/500，`objective` 360/500。

## 机制提炼

旧 320/313 初始池上的 2026-07-05 CPAC/CQG/MCA 机制报告已从当前 workspace 移除，避免污染标准配置比较。需要审计时从 Git 历史取证。

## 文献和对照

- `2026-07-05-mad-mechanism-improvement-table.md`：MAD 机制改善论文表，按方法、benchmark、正文可核验提升幅度整理。

## 读法 Caveat

这些报告应按 evidence record 阅读。当前标准配置比较只应使用 362/364 水平初始池及其明确标注的后续 run；旧 320/313 初始池数据不进入当前横向结论。

## Templates

- `reports/_templates/short_report.md`
- `reports/_templates/objective_research_report.md`
