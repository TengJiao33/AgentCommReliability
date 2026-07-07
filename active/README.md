# Active

当前有两条活跃机制线。两条线共享同一个诊断问题：候选答案、局部认知 cue 和最终聚合之间，哪一层才是多 agent reasoning 的可靠性瓶颈。

## 机制线 A：CPAC/DCAC/guard

`CPAC` 是外层候选池状态控制器。它先诊断初始答案池，再选择后续协议：

- `unique=1`：候选池 collapse。若全体同错，纯 CQG/DCAC 没有分歧抓手。
- `unique=2`：majority/minority。这里对应 minority-bearing 分支。
- `unique=3+`：no-majority conflict。需要 listwise 或其他识别动作。

`DCAC` 是 CPAC 在 `unique=2` 状态下的证书化翻案分支。`guard` 是 DCAC 的保守准入层，用来降低 MaC_to_W harm。

## 机制线 B：MCA

`MCA` 是 metacognitive communication/activation 总框架，目标是传递“这题该注意什么”的认知 cue，而不是传递最终答案。

当前四个实现版本：

- `MCA-T`：显式 text cue，用于快速验证 cue 是否有行为信号。
- `MCA-P`：soft prefix / continuous cue，是当前最适合作为底层主实现的版本。
- `MCA-KV`：hidden state / KV cache transfer。
- `MCA-S`：activation steering，更像推理倾向控制，适合作为 extension/ablation。

`MCE` 指 Metacognitive Cue Exchange，是 MCA 中的 cue exchange 协议对象名；`MCA-P` 指 soft-prefix 实现版本。

## 材料

- `reports/mad-mechanism-improvement-table.md`
- `reports/2026-07-06-cpac-dcac-guard-v1-standard-fixed.md`
- `experiments/standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/`
- `experiments/cpac-dcac-guard-v1-math500-20260706-standard-fixed-qwen25-7b-full-4096-a8002/`
- 远端 MCA-T audit aligned：`A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-text-audit-standard-madmm-aligned-qwen25-7b-full/`
- 远端 MCA-P soft-prefix aligned：`A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-soft-prefix-standard-madmm-aligned-qwen25-7b-full/`
