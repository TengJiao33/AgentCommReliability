# MCA Matrix source gate 审计记录

日期：2026-07-07

## 做法

1. 审计对象是 Pre-KV + MAD 的 A/B/C/D 矩阵。A 表示无通道第一轮，B 表示 Pre-KV 第一轮，C 表示无通道第一轮后接 MAD 文本讨论，D 表示 Pre-KV 第一轮后接 MAD 文本讨论。

2. 旧 partial run 先被检查。A 条件使用 batched HF `generate`，B 条件使用带 KV 的逐智能体手写生成，C/D debate 又回到 batched HF `generate`。这使条件差异混入批处理形态和随机数消耗。

3. 本地 runner 随后改成逐智能体生成。每个 row、stage、agent 都通过 `_stable_seed(base_seed, benchmark, split, row, stage, agent)` 得到局部种子。

4. 发送方 pre-state 使用 `question_only`。sender prompt 来自 `scripts/mca_pre_answer_runner.py::pre_state_prompt`，只要求模型读题形成内部表示。

5. `question_only` sender 使用 `max_new_tokens=0` 和 `keep_past_key_values=True`。因此 sender 不生成文本答案，只保存读题 prompt 的 KV state。

6. A/B 第一轮都调用 `_generate_receiver_from_state`。A 使用 `channel_mode="none"`，即 `past_key_values=None`；B 使用 `channel_mode="state"`，即接入 sender 的 `past_key_values`。

7. A/B 在同一题同一 agent 上共用同一个局部种子、同一个手写采样函数、同一个 temperature、top-p、max token 和 receiver prompt。两者目标差异只剩是否接入 sender KV。

8. C/D debate 也改成逐智能体手写生成。C 的 debate prompt 读取 A 的第一轮输出，D 的 debate prompt 读取 B 的第一轮输出。

9. C/D 在同一题同一 debate agent 上共用同一个局部种子。两者目标差异是进入文本 MAD 的第一轮材料来自 A 还是 B。

10. 每条 record 写入 generation seeds，便于复核同一题同一阶段是否使用匹配种子。

## 工程细节

- 已停止的运行包括 `20260707-a8002-gpu7-mca-matrix-disagreement-qwen25-7b` 和 `20260707-a8002-gpu7-mca-matrix-gold-contrast-qwen25-7b`。
- 启动记录目录为 `experiments/20260707-a8002-mca-packet-matrix-serial-gpu7-qwen25-7b/`。
- 旧 partial run 中，A 条件使用 batched HF `generate`，B 条件使用带 KV 的逐智能体手写生成，C/D debate 又使用 batched HF `generate`。这种组合会把批处理形态和随机数消耗混进条件差异。
- `question_only` sender prompt 来自 `scripts/mca_pre_answer_runner.py::pre_state_prompt`，文本要求模型读题并形成内部表示。
- 在 `scripts/run_mca_pre_kv_then_mad.py` 中，`question_only` sender 使用 `max_new_tokens=0` 和 `keep_past_key_values=True`，因此保存的是读题 prompt 的 KV state，没有生成文本答案。
- 修正后的 A/B 第一轮都调用 `_generate_receiver_from_state`。A 使用 `channel_mode="none"`，B 使用 `channel_mode="state"`。
- 修正后的 A/B 在同一题同一智能体上共用同一个局部种子、同一个手写采样函数、同一个 temperature、top-p、max token 和 receiver prompt。目标差异只剩 `past_key_values=None` 与 `past_key_values=sender_state.past_key_values`。
- 修正后的 C/D debate 都使用逐智能体手写生成。C 读取 A 的第一轮输出，D 读取 B 的第一轮输出；同一题同一 debate agent 共用同一个局部种子。
- 局部种子由 `_stable_seed(base_seed, benchmark, split, row, stage, agent)` 构造。每条记录写入 `generation_seeds.base_seed`、`generation_seeds.seed_key`、`generation_seeds.sender_pre_state`、`generation_seeds.first_round_agents` 和 `generation_seeds.debate_agents`。
- `mca_disagreement_v1` 包含 221 行，只按 Standard MAD 第一轮答案分歧筛选，`selection_uses_gold=false`。
- `mca_gold_contrast_v1` 包含 142 行，使用金标筛掉全对和全错样本，保留正误混合样本。

## 结果

| 项目 | 结果 |
| --- | --- |
| 旧 partial run | 已停止；不作为矩阵读数 |
| 停止原因 | A/B/C/D 的生成路径和随机数消耗不一致 |
| `mca_disagreement_v1` gold self-check | 221 行，`gold_self_fail=0` |
| `mca_gold_contrast_v1` gold self-check | 142 行，`gold_self_fail=0` |
| 本地编译 | `scripts/run_mca_pre_kv_then_mad.py` 通过 `py_compile` |
| 本地单测 | `tests.test_build_mca_packets`、`tests.test_mca_pre_answer_runner`、`tests.test_mca_hidden_channels`、`tests.test_mca_pre_kv_then_mad` 共 18 项通过 |

修正后的矩阵读数可以比较无通道第一轮、Pre-KV 第一轮、无通道进入 MAD 后的最终答案、Pre-KV 进入 MAD 后的最终答案。它不能直接替代完整 MATH500 accuracy，也不能证明旧 `+21` 是真实通道增益。

## 备注

旧 `+21` 仍保留为历史混杂结果。原因是旧 baseline 与 receiver 的温度、输出长度和生成路径不同。这个 source gate 审计对应的矩阵工程口径更接近“唯一变量”为 Pre-KV 状态。
