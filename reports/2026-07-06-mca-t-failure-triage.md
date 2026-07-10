# MCA-T 文本线索审计运行记录

## 做法

1. 运行先在 MATH-500 完整 500 题上生成与 Standard MAD prompt/config 对齐的初始答案池。每道题得到多个智能体初始答案、解析答案、初始多数答案和金标正误。

2. 脚本按初始答案池结构抽取文本线索。每题最多保留 2 条 cue，用来描述替代答案可能成立的方向。

3. 对每个候选替代答案，审计阶段调用模型生成证书。证书需要同时说明初始答案失败和替代答案通过，输出中由 `<initial>fail</initial>` 与 `<alternative>pass</alternative>` 标签承载。

4. `parse_audit_certificate` 解析审计文本，只把标签满足要求的证书记为 admissible certificate。

5. 聚合阶段忽略等于初始多数答案的替代答案，再按归一化后的 alternative 分组计票。

6. 某个 alternative 至少获得 2 个 admissible certificates 时，脚本接受改动，把该 alternative 作为最终答案；否则保留初始多数答案。

7. 每道题最终答案与初始多数答案、金标答案比较，记录 `MaC_to_C`、`MaC_to_W`、`MaW_to_C`、`MaW_to_W`。其中 `Ma` 表示初始多数。

8. 运行完成后，报告按整体、状态池分支和 accepted changes 类型拆分统计救回、伤害和错到错。

## 工程细节

- 远程输出：`A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-text-audit-standard-madmm-aligned-qwen25-7b-full/math500-qwen25-7b-instruct-mca-text-audit-all/`。
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`。
- 基准：MATH-500，500 题。
- 初始提示词：`standard-mad`。
- 采样温度：1.0。
- 最大生成长度：4096。
- 线索数量：`cue_k=2`。
- 接受改动门槛：`min_change_certificates=2`。
- 状态池范围：`pool_state_scope=all`。
- 审计温度：0.2。
- 输入记录：未使用 `--input-records`；本次为 prompt/config aligned with Standard MAD，不是 same-initial-pool aligned。
- 审计解析：`parse_audit_certificate` 读取模型生成的 `<initial>fail</initial>` 和 `<alternative>pass</alternative>` 标签。
- 聚合逻辑：忽略等于 initial answer 的 alternative，按 normalized alternative 计票。
- 运行状态：完整跑完，耗时约 3042 秒，`records.jsonl` 写完。

## 结果

| 指标 | 数值 |
| --- | ---: |
| 初始多数正确数 | 364/500 |
| 最终正确数 | 357/500 |
| 接受改动数 | 17/500 |
| admissible certificates | 81/1458 |
| `MaC_to_C` | 356 |
| `MaC_to_W` | 8 |
| `MaW_to_C` | 1 |
| `MaW_to_W` | 135 |
| correct-majority harm | 8/364 |
| wrong-majority recovery | 1/136 |

| 状态池 | 题数 | 接受改动 | 错到对 | 对到错 | 正确数变化 |
| --- | ---: | ---: | ---: | ---: | --- |
| `collapse` | 279 | 0 | 0 | 0 | 264/279 |
| `minority_bearing` | 134 | 10 | 0 | 7 | 86/134 到 79/134 |
| `no_majority_conflict` | 87 | 7 | 1 | 1 | 14/87 到 14/87 |

| accepted changes 类型 | 数量 |
| --- | ---: |
| useful correction | 1 |
| harmful flip | 8 |
| wrong-to-wrong | 8 |

## 备注

正确多数被推翻的例子：index 120，`even` 改为 `odd`；index 145，`-2` 改为 `130496`；index 238，`-4` 改为 `none`；index 323，`1/3` 改为 `1/2`；index 351，`1/16` 改为 `1/8`。

136 个 initial-wrong rows 中，9 次 accepted changes，1 次落到 gold。`minority_bearing` 分支中有 7 次对到错、0 次错到对。
