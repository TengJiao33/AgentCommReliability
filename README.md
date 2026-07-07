# AgentCommReliability

本仓库记录 agent communication reliability 相关的实验、机制草图和运行材料。当前 live surface 聚焦 MATH/AIME 多 agent reasoning。

## 当前问题

当前保留两条机制线：

- `CPAC/DCAC/guard`：候选池状态诊断与受控翻案。先判断 `unique=1/2/3+` 候选池状态，再决定早停、证书化 minority 翻案、listwise 识别或其他动作。
- `MCA`：metacognitive communication/activation。通信对象不是最终答案，而是 answer-free 的认知 cue；实现版本包括 `MCA-T`、`MCA-P`、`MCA-KV`、`MCA-S`。

术语层级以 `active/README.md` 的当前机制线说明为准。

## 当前证据：本地已归档

- 标准 MAD 4096 输出预算基线：`experiments/standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/`。
- CPAC/DCAC guard-v1 standard-fixed 诊断：`experiments/cpac-dcac-guard-v1-math500-20260706-standard-fixed-qwen25-7b-full-4096-a8002/`。
- MAD-MM/MAD-M2 MATH-500 复现：`experiments/mad-mm-math500-20260704-qwen25-7b-full-a8002/`。
- MAD-MM/MAD-M2 AIME24/25 复现：`experiments/mad-mm-aime24-25-20260704-qwen25-7b-full-a8002/`。

## 远端观察但本地未归档

- MCA-T audit aligned 远端结果：`A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-text-audit-standard-madmm-aligned-qwen25-7b-full/`。该 run 初始多数 364/500，最终 357/500。
- MCA-P soft-prefix aligned 远端运行中：`A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-soft-prefix-standard-madmm-aligned-qwen25-7b-full/`。

## 入口

- `active/README.md`：当前活跃机制线。
- `reports/README.md`：报告、术语表和文献表索引。
- `experiments/README.md`：当前实验 run 索引。
- `scripts/`：runner 源码。
- `tests/`：轻量单元测试。
- `docs/`：机器、同步、资源和实验协议文档。
