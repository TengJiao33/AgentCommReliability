# AgentCommReliability

本仓库记录 agent communication reliability 相关的实验、机制草图和运行材料。当前 live surface 聚焦 MATH/AIME 多 agent reasoning。

## 当前问题

核心问题是：多 agent 推理失败到底来自候选答案覆盖不足、候选识别失败，还是通信/聚合协议把有用分歧处理坏了。

当前保留两条机制线：

- `CPAC/DCAC/guard`：候选池状态诊断与受控翻案。先判断 `unique=1/2/3+` 候选池状态，再决定早停、证书化 minority 翻案、listwise 识别或其他动作。
- `MCA`：metacognitive communication/activation。通信对象不是最终答案，而是 answer-free 的认知 cue；实现版本包括 `MCA-T`、`MCA-P`、`MCA-KV`、`MCA-S`。

术语层级以 `reports/2026-07-05-current-mechanism-taxonomy.md` 为准。

## 当前证据

- 标准 MAD 4096 输出预算基线：`experiments/20260705-a8002-math500-standard-mad-qwen25-7b-full-4096/`。
- CPAC/DCAC guard-v1 标准配置诊断：`experiments/20260705-a8002-math500-cpac-dcac-guard-v1-standard-qwen25-7b-full-4096/`。
- MCA-T audit 标准配置诊断：`experiments/20260705-a8002-math500-mca-text-audit-standard-qwen25-7b-full-4096/`。
- MCA-P soft-prefix 标准配置诊断：`experiments/20260705-a8002-math500-mca-soft-prefix-standard-qwen25-7b-full-4096/`。

## 入口

- `active/README.md`：当前活跃机制线。
- `reports/README.md`：报告、术语表和文献表索引。
- `experiments/README.md`：当前实验 run 索引。
- `scripts/`：runner 源码。
- `tests/`：轻量单元测试。
- `docs/`：机器、同步、资源和实验协议文档。
