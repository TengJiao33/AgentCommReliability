# Question-only Pre-KV 结果与 early-plan 实现记录

日期：2026-07-07

## 做法

1. Question-only Pre-KV 的发送方只运行读题 pass。`pre_state_tokens=0`，`generated_tokens=0`，所以发送方不生成草稿、不生成推理、不生成答案。

2. 发送方保存的是包含题面和前置指令的 chat prefix KV。该 KV 主要表示“读过这道题”的缓存状态。

3. 无通道第一轮中，3 个接收方各自从自己的题目提示词开始生成，`past_key_values=None`。

4. Pre-KV 第一轮中，3 个接收方分别接入发送方保存的 question-only KV，再生成第一轮答案。

5. 同口径 bridge run 固定第一轮参数为 temperature 0.2 和 first_round_max_tokens 1536。no-channel first 与 Pre-KV first 在同一题同一 agent 上使用匹配生成口径。

6. 两个第一轮条件完成后，脚本分别做多数投票，比较 no-channel first 与 Pre-KV first 的正确数和正误转移。

7. source-gated matrix partial run 继续把第一轮输出接入 MAD 文本讨论。C 使用 no-channel first outputs，D 使用 Pre-KV first outputs。

8. partial run 停止前，记录了 first-round transition 和 Pre-KV debate transition。进入 MAD 后的 final gain 没有出现在该 partial 读数中。

9. 本地 runner 加入 `early_plan` 阶段。该阶段让 sender 生成短私有早期草稿，再把 live KV 传给 receiver。

10. 为了审计早期草稿是否泄漏答案，record 新增 `sender_state_outputs`、`sender_answer_tag_count` 和 `sender_gold_leak_count`，summary 也写入对应计数。

## 工程细节

- `question_only` sender 使用 `pre_state_tokens=0` 和 `generated_tokens=0`。
- 发送方实际保存的是包含题目的 chat prefix KV；没有生成早期草稿、局部检查、搜索方向或任何新 token。
- 接收方求解同一道题，因此 sender prefix 与 receiver prompt 高度重复。
- 同口径 bridge run 固定第一轮参数为 `temperature=0.2` 和 `first_round_max_tokens=1536`。
- 已停止的 source-gated matrix run 为 `20260707-a8002-gpu1-mca-matrix-matched-disagreement-qwen25-7b`。
- 停止前使用的 packet 为 `mca_disagreement_v1`，进度约 `93/221` 行。
- 停止前进程链为 `4050883 -> 4050909 -> 4050910`；停止后 GPU1 约 `4 MB` 显存占用、`0%` 利用率。
- 本地修改文件为 `scripts/run_mca_pre_kv_then_mad.py`。
- 新增参数为 `--pre-state-stage {question_only,early_plan}` 和 `--pre-state-tokens`。
- `early_plan` 阶段让 sender 生成短的 pre-answer private plan，再把生成过程留下的 live KV 传给 receiver。
- 每条记录新增 `sender_state_outputs`、`sender_answer_tag_count` 和 `sender_gold_leak_count`。
- summary 写入 sender answer-tag 计数和 gold-leak 计数，用来区分早期搜索状态与显式答案泄漏。

## 结果

| 读数 | 数值 |
| --- | ---: |
| 同口径 no-channel first | 347/500 |
| 同口径 Pre-KV first | 349/500 |
| 第一轮净变化 | +2 |
| 旧完整 run baseline | 341/500 |
| 旧完整 run Pre-KV final | 362/500 |
| 旧完整 run 净变化 | +21 |

| 停止前 partial 读数 | 数值 |
| --- | ---: |
| `BaC_to_C` | 35 |
| `BaC_to_W` | 7 |
| `BaW_to_C` | 9 |
| `BaW_to_W` | 42 |
| `PKC_to_C` | 42 |
| `PKC_to_W` | 2 |
| `PKW_to_C` | 0 |
| `PKW_to_W` | 49 |

进入 MAD 文本讨论后的 final gain 没有出现在该 partial 读数中。旧 `+21` 同时包含温度、输出长度、生成路径和随机轨迹差异，只作为历史混杂结果保留。

## 备注

`early_plan` 的记录字段用于审计发送方是否在私有阶段已经写出最终答案或疑似金标。这个版本的核心差异是从 zero-token read-pass KV 转向短私有草稿留下的 live KV。
