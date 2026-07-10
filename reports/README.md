# 报告索引与写作规则

本目录保存实验报告、工程审计、综述表、会议记录和展示产物。默认语言为中文；`GPU`、`benchmark`、`KV cache`、`hidden state`、`records.jsonl` 等不适合中文化的术语保留英文。

## 统一格式

普通实验报告和工程审计统一使用四段结构：

```md
# 标题

日期：YYYY-MM-DD

## 做法

用编号步骤说明这次实验或实现实际怎样运行。必须写到别人能复现流程：输入从哪里来，先运行哪个条件，生成函数怎样调用，通信对象怎样构造，接收方怎样使用，对照条件怎样保持一致，最终怎样统计。

做法段不能只写摘要。例如“运行 Pre-KV 并比较无通道”不够；需要写成“发送方先读题并保存 `past_key_values`；无通道接收方从自己的提示词生成；Pre-KV 接收方在相同提示词下接入发送方缓存；两边使用同一温度、同一输出预算和同一局部种子；最后对 3 个接收方答案多数投票”。

## 工程细节

- 写清楚入口脚本、关键函数、数据子集、参数、随机种子、记录字段和运行产物。
- 按真实执行顺序写步骤，不使用抽象包装词替代工程细节。

## 结果

| 条件 | 指标 | 数值 |
| --- | --- | ---: |
| ... | ... | ... |

结果段只放已发生的读数、转移、异常和停止状态。

## 备注

记录特殊边界、混杂来源、审计口径或样例。没有特殊信息时写“无”。
```

写作时不写计划、建议、下一步、主观判断或防御性叙述。需要表达边界时，写成可复核事实，例如“该 run 的 baseline 与 receiver 温度不同”，不要写成“所以应该重跑”。不要用“不是而是”式包装标题；直接说明对象、路径和读数。

## 例外文档

以下文档不强制使用四段实验报告结构：

- 文献综述和论文表：`mad-mechanism-improvement-table.md`、`2026-07-07-early-plan-pre-kv-improvement-lit-survey.md`、`2026-07-08-latent-comm-literature-notes.md`。
- 会议和电话记录：`2026-07-08-meeting-transcript-cleaned.md`。
- 展示产物和生成文件：`mca_progress_presentation.html`、`generated/`。
- 模板：`_templates/`。

例外文档仍应尽量避免无依据的计划口吻；如果保留原始讲话或阅读笔记中的判断，需要能看出它属于原始材料。

## 当前必读

- `mad-mechanism-improvement-table.md`：MAD 机制改善论文表，按方法、benchmark、正文可核验提升幅度整理。
- `2026-07-08-idea-evolution-natural-search-state.md`：MCA idea 从文本讨论到自然搜索状态通信的演化脉络。
- `2026-07-08-meeting-transcript-cleaned.md`：与老师交流后的清理版转写。

## 复现与基线

- `2026-07-04-mad-mm-math500.md`：MAD-MM / MAD-M2 在 MATH-500 上的复现记录。
- `2026-07-04-mad-mm-aime.md`：MAD-MM / MAD-M2 在 AIME24/25 上的复现记录。
- `2026-07-06-cpac-dcac-guard-v1-standard-fixed.md`：CPAC/DCAC guard-v1 standard-fixed 运行记录。

## MCA 实验记录

- `2026-07-06-mca-pre-answer-latent-design.md`：MCA-Pre 前置潜状态通信实现记录。
- `2026-07-06-mca-latent-debate-design.md`：MCA 潜状态多轮讨论边界记录。
- `2026-07-06-mca-pre-run-pruning.md`：MCA-Pre 运行裁剪记录。
- `2026-07-06-mca-kv-s-implementation-notes.md`：MCA-KV / MCA-S 实现记录。
- `2026-07-06-mca-t-failure-triage.md`：MCA-T 文本线索审计运行记录。
- `2026-07-06-mca-p-running-diagnostic.md`：MCA-P soft-prefix 运行诊断。
- `2026-07-07-early-plan-pre-kv-case-audit.md`：Early-Plan Pre-KV 案例审计。
- `2026-07-07-hybrid-micro-gated-failure-audit.md`：Hybrid Micro-Gated Pre-KV 运行审计。
- `2026-07-07-hybrid-micro-gated-pre-kv-implementation.md`：Hybrid Micro-Gated Pre-KV 实现记录。
- `2026-07-07-hybrid-micro-gated-stop-note.md`：Hybrid Micro-Gated 运行停止记录。
- `2026-07-07-mca-latent-rounds-design.md`：MCA 潜状态轮次实现记录。
- `2026-07-07-mca-packet-matrix-design.md`：MCA Packet Matrix 构建记录。
- `2026-07-07-mca-matrix-source-gate-audit.md`：MCA Matrix source gate 审计记录。
- `2026-07-07-pre-kv-null-result-and-next-implementation.md`：Question-only Pre-KV 结果与 early-plan 实现记录。
- `2026-07-08-mca-latent-safe-variants-progress.md`：MCA 潜状态安全变体运行记录。
- `2026-07-08-mca-latent-safe-variants-results.md`：MCA 潜状态安全变体结果记录。
- `2026-07-08-natural-search-state-engineering-audit.md`：自然搜索状态通信工程审计。
- `2026-07-08-natural-search-delta-results.md`：Natural Search Delta 首跑结果记录。
