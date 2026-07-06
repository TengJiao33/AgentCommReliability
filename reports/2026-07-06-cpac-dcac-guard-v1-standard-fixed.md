# CPAC/DCAC guard-v1 standard-fixed 结果诊断

日期：2026-07-06

## 证据来源

- 运行目录：`experiments/cpac-dcac-guard-v1-math500-20260706-standard-fixed-qwen25-7b-full-4096-a8002/`
- 摘要：`math500-qwen25-7b-instruct-cpac-dcac/summary.json`
- 明细：`math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`
- 对照：`experiments/standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/math500-qwen25-7b-instruct-naive/summary.json`

## 运行状态

运行日志显示远端环境为 `A800_2`，GPU `2`，模型 `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`，输出预算 4096，`max_model_len=24064`，500 题完整跑完，耗时 2367.8 秒。

检查时远端机器可连通，`/data` 使用 68%，`/mnt/quarkfs` 使用 70%。GPU 6/7 上有本账号正在跑的 20260706 MCA 任务；GPU 2 当时 37GB/99% 负载来自其他用户任务，不是这条已完成的 CPAC/DCAC 运行。

## 机制触发

500 题被分成：

- `collapse` / `keep_initial`：279 题；
- `minority_bearing` / `dcac`：134 题；
- `no_majority_conflict` / `listwise_discriminant`：87 题。

DCAC 分支中，53/134 题生成了有效方向性声明，159 个证书提示中有 12 个通过 guarded admissible flip，最终实际翻案 5 题。

Guard 层在证书级别有实际过滤：147 个证书被 guard 拒绝。主要拒绝原因包括 `certificate_tags_do_not_admit_flip`、`arithmetic_mismatch_in_calculation`、`challenger_answer_not_supported_by_certificate_text`、`blocked_representation_risk:matrix_or_vector` 和 `blocked_representation_risk:base_notation`。本轮没有出现 raw flip 达标但被 guard 整体拦下的案例，`dcac_guard_blocked_flips=0`。

## 结果拆解

整体 transition 为：

- `MaC_to_C`：363；
- `MaC_to_W`：1；
- `MaW_to_C`：5；
- `MaW_to_W`：131。

按机制分支看：

- `keep_initial`：264 个 `MaC_to_C`，15 个 `MaW_to_W`，没有改答案；
- `dcac`：2 个 `MaW_to_C`，1 个 `MaC_to_W`，2 个 `MaW_to_W`，其余不改；
- `listwise_discriminant`：3 个 `MaW_to_C`，18 个改后仍错，14 个 `MaC_to_C`，70 个 `MaW_to_W`。

DCAC 的 5 个翻案中，2 个恢复正确，1 个伤害正确多数，2 个从错改到另一个错。`listwise` 分支改了 21 题，其中 3 题恢复正确，18 题仍错。

## 具体恢复和损伤

5 个恢复正确案例：

- index 242，`listwise` 将 `34233` 改为正确答案 `32348`；
- index 348，DCAC 将 `4060` 改为正确答案 `4495`；
- index 358，DCAC 将 `circle` 改为正确答案 `ellipse`；
- index 429，`listwise` 将 `625` 改为正确答案 `50`；
- index 472，`listwise` 将 `56` 改为正确答案 `275/2`。

1 个损伤案例：

- index 206，DCAC 将正确初始多数 `(3/2, -13)` 翻到错误答案 `2`。该题带有 `compound_answer` 和 `symbolic_expression` 风险，说明当前 guard 对复合答案的保护还不够。