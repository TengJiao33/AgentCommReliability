# CPAC/DCAC guard-v1 standard-fixed 运行记录

## 做法

1. 运行先读取 Standard MAD 在 MATH-500 上的第一轮智能体答案。每道题都有 3 个初始答案、解析后的多数答案、金标答案和初始多数正误。

2. 脚本按第一轮答案结构给每道题分流。若 3 个智能体已经形成稳定多数且没有可用少数承载信息，则进入 `keep_initial`，直接保留初始多数答案。

3. 若存在少数意见并且少数答案可能携带有用方向，则进入 `dcac` 分支。该分支围绕多数答案和挑战答案生成方向性证书，检查挑战答案是否有足够证据替换初始多数。

4. DCAC 证书先经过标签和内容检查。证书需要支持翻案，且不能出现计算不匹配、挑战答案没有被证书文本支持、矩阵或进制表示风险等问题。

5. 只有通过守门检查的证书才允许触发翻案。翻案后脚本重新记录最终答案，并和初始多数答案比较正误转移。

6. 若题目没有稳定多数冲突结构，则进入 `listwise_discriminant` 分支。该分支把候选答案放在同一判别过程里比较，选择一个最终答案。

7. 所有分支结束后，脚本按 500 题汇总 `MaC_to_C`、`MaC_to_W`、`MaW_to_C`、`MaW_to_W`。其中 `Ma` 表示初始多数，后两个字母表示初始多数和机制输出的正误状态。

8. 明细写入 `records.jsonl`，summary 写入 `summary.json`。报告中的恢复案例和损伤案例都来自明细记录。

## 工程细节

- 运行目录：`experiments/cpac-dcac-guard-v1-math500-20260706-standard-fixed-qwen25-7b-full-4096-a8002/`。
- 摘要文件：`math500-qwen25-7b-instruct-cpac-dcac/summary.json`。
- 明细文件：`math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`。
- 标准 MAD 对照：`experiments/standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/math500-qwen25-7b-instruct-naive/summary.json`。
- 远端环境：`A800_2`，GPU `2`。
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`。
- 输出预算：4096。
- 上下文长度：`max_model_len=24064`。
- 样本量：MATH-500 完整 500 题。
- 耗时：2367.8 秒。
- 分支数量：`keep_initial` 279 题，`dcac` 134 题，`listwise_discriminant` 87 题。
- DCAC 证书：134 题中 53 题生成有效方向性声明；159 个证书提示中 12 个通过 guarded admissible flip；最终实际翻案 5 题。
- Guard 过滤：147 个证书被拒绝，主要原因包括 `certificate_tags_do_not_admit_flip`、`arithmetic_mismatch_in_calculation`、`challenger_answer_not_supported_by_certificate_text`、`blocked_representation_risk:matrix_or_vector`、`blocked_representation_risk:base_notation`。

## 结果

| 指标 | 数值 |
| --- | ---: |
| `MaC_to_C` | 363 |
| `MaC_to_W` | 1 |
| `MaW_to_C` | 5 |
| `MaW_to_W` | 131 |
| DCAC 翻案 | 5 |
| DCAC 错到对 | 2 |
| DCAC 对到错 | 1 |
| DCAC 错到错 | 2 |
| listwise 改答案 | 21 |
| listwise 错到对 | 3 |
| listwise 错到错 | 18 |
| `dcac_guard_blocked_flips` | 0 |

## 备注

恢复正确案例：index 242，`listwise` 将 `34233` 改为 `32348`；index 348，DCAC 将 `4060` 改为 `4495`；index 358，DCAC 将 `circle` 改为 `ellipse`；index 429，`listwise` 将 `625` 改为 `50`；index 472，`listwise` 将 `56` 改为 `275/2`。

损伤案例：index 206，DCAC 将正确初始多数 `(3/2, -13)` 改为错误答案 `2`。
