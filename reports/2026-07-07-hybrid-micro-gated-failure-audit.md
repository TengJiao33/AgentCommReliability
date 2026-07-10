# Hybrid Micro-Gated Pre-KV 运行审计

## 做法

1. 审计对象是 hybrid micro-gated Pre-KV 的 17 条早期 records。该版本仍从 early-plan Pre-KV 开始，但把发送方早期草稿改成带字段的 micro commitment。

2. 每题先生成 sender pre-state。发送方在 `early_plan` 阶段最多生成 64 个标记，并被提示输出 `REPRESENTATION`、`FIRST_MOVE`、`CHECK` 三个字段。

3. 发送方生成过程保留 raw `past_key_values`。由于 64 个标记经常不足以完成三个字段，缓存可能停在未完成 assistant completion 内部。

4. no-channel 分支中，接收方从自己的题目提示词直接生成第一轮答案，不接收 sender past。

5. raw Pre-KV 分支中，receiver prompt 接在 sender retained KV 后面继续生成。接收方可以受到 sender prompt、题面、role text 和半截结构化草稿共同影响。

6. 可见短承诺也会展示给 paired Pre-KV receiver，但如果短承诺包含 `<answer>`、`Final answer:`、`####` 或 `\boxed{...}` 等答案标记，则该可见文本被拦截。

7. 运行记录 raw hybrid Pre-KV first、gated selected first、raw hybrid + MAD 和 gated selected + MAD。门控优先检查 3 个 Pre-KV first answers 是否归一化后一致。

8. 若 3 个 Pre-KV first answers 一致，selected first 使用 raw Pre-KV 输出；若 Pre-KV 第一轮分裂，则 selected first 回退到 no-channel first。

9. 审计对 `BaC_to_W` 案例逐题查看 sender 草稿是否被截断、receiver 是否从半截公式或半截结构继续写，以及错误多数票怎样形成。

## 工程细节

- run id：`20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-disagreement-qwen25-7b`。
- 快照规模：17 条记录。
- 前置阶段：`pre_state_stage=early_plan`。
- 前置生成长度：`pre_state_tokens=64`。
- 可见短承诺字段：`REPRESENTATION`、`FIRST_MOVE`、`CHECK`。
- Pre-KV receiver 输入结构：sender system/user pre-state prompt；sender assistant generated partial sketch；receiver prompt 接在 retained `past_key_values` 后。
- sender 输出审计：51 个 sender outputs；`REPRESENTATION` present 51；`FIRST_MOVE` present 28；`CHECK` present 2；likely truncated 46。
- 续写伪影证据：geometric-sequence harm case 中，Pre-KV output 从公式片段 `\cdot 9}{3 \cdot 125} = ...` 开始。
- 门控信息：selected first 读数记录在停止记录中；门控主要影响 non-unanimous Pre-KV cases。

## 结果

| 指标 | 数值 |
| --- | ---: |
| 快照规模 | 17 |
| `BaC_to_C` | 7 |
| `BaC_to_W` | 4 |
| `BaW_to_C` | 0 |
| `BaW_to_W` | 6 |
| raw hybrid Pre-KV `BaW_to_C` | 0 |
| raw hybrid Pre-KV `BaC_to_W` | 4 |

| harm case | gold | no-channel | hybrid Pre-KV | 观测 |
| --- | --- | --- | --- | --- |
| `test/precalculus/990.json` | `6 - 5i` | `6 - 5i` | `3 + 3*sqrt(2)/2 - 2i` | visible sketch 在完整 `FIRST_MOVE` / `CHECK` 前截断；两个 Pre-KV agent 出现相同 translation error |
| `test/algebra/2427.json` | `10` | `10, 10, 10` | `5, 10, 5` | sketch 推向 ordinary annuity formula，但没有写到 concrete equation check |
| `test/algebra/1072.json` | `243/625` | `243/625, 243/625` | `27, 27/625, 69.4` | sketch 正确识别 geometric sequence 和 common ratio，但被截断在 `CHECK` 前 |
| `test/geometry/627.json` | `17` | `17, 8, 17` | `7, 7, 17` | 两个 Pre-KV agent 选 diagonal pairing，得到错误多数 |

## 备注

该快照中的通信对象实际为 partial sketch + raw unfinished KV。64 tokens 下结构化字段多数未完成，retained KV 可停在 unfinished assistant completion 内部。harm cases 涉及代数、数值求解和顶点配对。
