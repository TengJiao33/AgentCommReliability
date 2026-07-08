# MCA Matrix Source Gate 审计

日期：2026-07-07

对应矩阵为：

| 条件 | 含义 | 主读数 |
| --- | --- | --- |
| A | no-channel first | 第一轮无通道基线 |
| B | Pre-KV first | 第一轮 Pre-KV 效果 |
| C | no-channel first + MAD | 无通道进入 MAD 后的 final |
| D | Pre-KV first + MAD | Pre-KV 进入 MAD 后的 final |

## 已停止的 partial run

已停止 run：

- `20260707-a8002-gpu7-mca-matrix-disagreement-qwen25-7b`
- `20260707-a8002-gpu7-mca-matrix-gold-contrast-qwen25-7b`

启动记录目录：

- `experiments/20260707-a8002-mca-packet-matrix-serial-gpu7-qwen25-7b/`

该 run 在 `mca_disagreement_v1` 上写出 partial records 后停止。

停止原因是源码口径不满足唯一变量要求：

- A/no-channel first 使用 batched HF `generate`；
- B/Pre-KV first 使用 sequential manual generation with KV；
- C/D debate 使用 batched HF `generate`；
- run-level random stream 和 batch 形态会把生成顺序、批处理实现、随机数消耗混入条件差异。

## 源码审计结论

### Pre-KV sender 状态

`question_only` sender prompt 来自 `scripts/mca_pre_answer_runner.py::pre_state_prompt`。

该 prompt 只要求读题并形成内部表示：

```text
Read the problem and form an internal representation for a later solver pass.
```

在 `scripts/run_mca_pre_kv_then_mad.py` 中，sender state 使用：

```text
max_new_tokens=0
keep_past_key_values=True
```

因此 question-only Pre-KV 不生成文本答案；它保留的是读题 prompt 的 KV state。这个设计符合“pre-answer latent state”的实验语义。

### 第一轮 A/B 对照

修正前，A 和 B 的差异不止是 KV state。

修正后，本地 `scripts/run_mca_pre_kv_then_mad.py` 已改为：

- A/no-channel first：逐 agent 调用 `_generate_receiver_from_state(..., channel_mode="none")`；
- B/Pre-KV first：逐 agent 调用 `_generate_receiver_from_state(..., channel_mode="state")`；
- 同一 row、同一 agent 的 A 与 B 使用同一个 local seed；
- A/B 使用同一手写采样函数、同一 temperature、top-p、max tokens、prompt text；
- A/B 的目标差异只剩 `past_key_values=None` vs `past_key_values=sender_state.past_key_values`。

### MAD C/D 对照

修正后，本地 runner 已改为：

- C/no-channel + MAD：逐 debate agent 手写生成；
- D/Pre-KV + MAD：逐 debate agent 手写生成；
- 同一 row、同一 debate agent 的 C 与 D 使用同一个 local seed；
- C/D 的目标差异是 debate prompt 中可见的第一轮 agent outputs 来自 A 还是 B。

这回答的是“Pre-KV 改变第一轮文本输出后，是否通过普通 MAD 文本讨论影响 final majority”。

### 随机性

本地 runner 已加入 `_stable_seed(base_seed, benchmark, split, row, stage, agent)`。

每条 record 写入：

- `generation_seeds.base_seed`
- `generation_seeds.seed_key`
- `generation_seeds.sender_pre_state`
- `generation_seeds.first_round_agents`
- `generation_seeds.debate_agents`

这消除了全局随机流中“前一个条件消耗多少随机数影响后一个条件”的主要问题。

## Packet 与 gold/parser 审计

### Packet 语义

`mca_disagreement_v1`：

- 221 rows；
- 只按 Standard MAD 第一轮答案分歧筛选；
- `selection_uses_gold=false`；
- 适合作为主诊断包；
- 不能代表完整 MATH500 accuracy。

`mca_gold_contrast_v1`：

- 142 rows；
- 使用 gold 筛掉全对/全错；

### Gold smoke

本地 gold self-check 结果：

- `mca_disagreement_v1`: 221 rows, `gold_self_fail=0`
- `mca_gold_contrast_v1`: 142 rows, `gold_self_fail=0`

即 packet 内 gold 用当前 `is_correct`/`normalize_numeric` 判自己均为正确。

## 这个矩阵能回答什么

在修正后的 runner 和 packet 上，结果可以回答：

- no-channel 第一轮经过一轮 MAD 后的变化；
- Pre-KV 第一轮经过一轮 MAD 后的变化；
- `D - C` 是否为正，即 Pre-KV 是否给 MAD final 带来同口径增益；

## 这个矩阵不能回答什么

该 packet run 不能直接回答：

- 完整 MATH500 上是否超过 Standard MAD；
- 是否超过 2026-07-05 那个 exact Standard MAD full baseline；
- 纯 latent multi-round debate 是否有效；
- 旧 Pre-KV `+21` 是否是真实通道效应。

原因：

- packet 不是完整 MATH500；
- D 使用的是 Pre-KV first outputs 后接文本 MAD，不是纯 latent debate；
- exact Standard MAD baseline 的参数和这次低温第一轮矩阵不同；
- 旧 `+21` 的 baseline 和 receiver 参数不同，仍然是历史混杂结果。

## 重跑前源码条件

重跑必须满足：

- 使用修正后的 `scripts/run_mca_pre_kv_then_mad.py`；
- A/B/C/D 都走 sequential manual generation；
- A/B 同 row 同 agent 共用 local seed；
- C/D 同 row 同 debate agent 共用 local seed；
- record 中写入 `generation_seeds`；
- 不使用旧 partial run 的 `records.jsonl` resume；
- 使用新的 run id 或清空旧 output dir。

## 当前验证

本地轻量验证通过：

```text
python -m py_compile scripts/run_mca_pre_kv_then_mad.py
python -m unittest tests.test_build_mca_packets tests.test_mca_pre_answer_runner tests.test_mca_hidden_channels tests.test_mca_pre_kv_then_mad
```

结果：

```text
Ran 18 tests
OK
```

