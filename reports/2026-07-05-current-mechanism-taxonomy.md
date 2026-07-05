# 当前机制术语表

日期：2026-07-05

## 为什么需要这份表

此前材料里同时出现了 `MCE`、`MCA`、`MCA-T`、`MCA-P`、`CPAC`、`DCAC` 等名称。这份表统一当前命名层级。

当前统一为两条机制线：

1. `CPAC/DCAC/guard`：候选池状态诊断与受控翻案。
2. `MCA`：metacognitive communication/activation，包含四个实现版本。

## 机制线 A：CPAC/DCAC/guard

`CPAC` 是 Candidate-Pool Adaptive Consensus，是外层状态控制器：

- `unique=1`：候选池 collapse。重点是 coverage。
- `unique=2`：majority/minority。重点是区分 informative minority 和 seductive wrong minority。
- `unique=3+`：no-majority conflict。重点是 listwise/discriminant identification。

`DCAC` 是 Disagreement-Conditioned Admissibility Certificate，是 CPAC 在 `unique=2` 分支上的证书化翻案机制。

`guard` 是 DCAC 的保守准入层，目标是减少 MaC_to_W harm。

## 机制线 B：MCA

`MCA` 是 Metacognitive Communication / Activation。它的核心问题是：agent 之间是否可以传递“这题该注意什么”的认知 cue，而不是传递最终答案或完整 rationale。

四个实现版本：

| 名称 | 通信载荷 | 定义 |
|---|---|---|
| `MCA-T` | answer-free text cue | 显式文本 cue，主要用于验证 cue-level 行为信号。 |
| `MCA-P` | continuous soft prefix | 把 cue 信息转为 prefix embedding；当前最适合作为底层第一版。 |
| `MCA-KV` | hidden state / KV cache | 内部状态通信版本。 |
| `MCA-S` | activation steering direction | 更像推理倾向控制，适合作为 extension 或 ablation。 |

`MCE` 指 Metacognitive Cue Exchange，是 MCA 中“交换 answer-free cue”这一协议对象名。`MCA-P` 指 soft-prefix 实现版本。

## 当前优先级

- 近端主线：`CPAC/DCAC/guard`。
- MCA 实现顺序：`MCA-T/audit` -> `MCA-P` -> `MCA-KV` / `MCA-S`。
