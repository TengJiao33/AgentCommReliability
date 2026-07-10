# 自然搜索状态通信工程审计

日期：2026-07-08

## 做法

1. 审计先检查 Pre-KV 路径。发送方通过 `_manual_generate_sender_state` 生成 pre-state 并保留 `past_key_values`；接收方通过 `_generate_receiver_from_state(channel="kv")` 接入这段 past。

2. Pre-KV 接入时，receiver prompt 的 position ids 从 sender 的 `past_token_count` 后面开始，attention mask 覆盖 sender past 和 receiver prompt。审计据此把 Pre-KV 记录为前缀接续路径。

3. 审计随后检查 question-only Pre-KV。该路径中 `pre_state_tokens=0`，发送方不生成思考或答案，只保存读题 prompt 的 KV state。

4. 审计再检查 early-plan Pre-KV。发送方被提示写问题表示和第一搜索方向，生成短私有草稿后留下 live KV；接收方接在这段 live KV 后生成。

5. 审计继续检查 micro-commitment。发送方被要求写 `REPRESENTATION`、`FIRST_MOVE`、`CHECK`，但 64 个标记下大量输出停在半截结构化文本中。

6. 审计检查 latent-rounds。该路径不展示同伴文本，也不在最终答案阶段默认注入同伴向量；但状态向量来自“题目 + 私有思考”和“题目 + 空私有思考”的隐藏状态差值，因此仍依赖文本化私有思考。

7. 审计最后对应到 natural-search-delta。该路径使用普通 CoT prompt 逐 token 解码，不要求发送方写显式草稿，记录字段固定 `sender_prompt_intervention=false`。

8. natural-search-delta 的 `_generate_trace` 在指定层注册 forward pre-hook。每步生成时保存 last-token hidden，在截点保存 absolute state、delta state、范数、token id 和 token window。

9. natural-search-delta 的 `_build_schedule` 按条件构造消息：同题 delta 取同一题同伴 `state.delta`，无关题 delta 取相邻题 `state.delta`，随机同范数以同题 delta 为范数参考采样高斯向量，同题绝对状态取 `state.absolute`。

10. 注入时只在指定生成步和指定层生效，hook 把裁剪后的向量乘以 `steering_scale` 加到当前最后一个标记的隐藏状态。

11. 审计把这些路径按通信对象和工程副作用对齐，记录每条线的读数、污染来源和自然搜索状态实现中的对应修正。

## 工程细节

- Pre-KV 相关代码包括 `scripts/mca_hidden_channel_runner.py`、`scripts/mca_pre_answer_runner.py` 和 `scripts/run_mca_pre_kv_then_mad.py`。
- Pre-KV sender 通过 `_manual_generate_sender_state` 生成 pre-state，并保留 `past_key_values`。receiver 通过 `_generate_receiver_from_state(channel="kv")` 接入 sender 的 `past_key_values`，receiver prompt 的 `position_ids` 从 `past_token_count` 之后开始，attention mask 覆盖 sender past 与 receiver prompt。
- 这种路径把接收方放在发送方上下文之后，接收方继承发送方系统提示、题目编码、assistant 半截生成、位置编号和注意力历史。hybrid micro-gated 与 early-plan 的伤害样例都与这种前缀接续有关。
- `question_only` Pre-KV 使用 `pre_state_tokens=0`，收益读数为 no-channel first `347/500`、Pre-KV first `349/500`。它主要传递读题 prompt 的 KV state，不能证明自然解题中间状态存在搜索信号。
- early-plan 的 `pre_state_prompt(..., stage="early_plan")` 要求发送方私下写问题表示和第一搜索方向。micro-commitment 进一步要求 `REPRESENTATION`、`FIRST_MOVE`、`CHECK` 三个字段。
- micro-commitment 审计中，`sender outputs=51`，`REPRESENTATION present=51`，`FIRST_MOVE present=28`，`CHECK present=2`，`likely truncated=46`。通信对象实际混合了半截结构化文本和半截生成轨迹 KV。
- latent-rounds 相关代码为 `scripts/run_mca_latent_rounds.py`。它不展示同伴文本，默认不在最终答案阶段注入同伴向量，并记录向量范数、裁剪状态和答案标记审计。
- latent-rounds 的 `_thought_vector` 使用“题目 + 私有思考”和“题目 + 空私有思考”两段文本，在指定层取最后位置隐藏状态差值。它更接近文本化私有思考的摘要方向，而不是普通解题 decode 过程中逐步产生的隐藏状态轨迹。
- natural-search-delta 的实现文件为 `scripts/run_mca_natural_search_delta.py`，协议字段为 `mca-natural-search-delta-v0`。
- natural-search-delta 使用普通 CoT prompt 逐 token 解码，不要求发送方生成显式草稿字段，记录 `sender_prompt_intervention=false`。
- `_generate_trace` 在指定 transformer layer 注册 forward pre-hook。每个生成步保存 last-token hidden；在截点保存 absolute state、delta state、范数、token id 和 token window。
- 默认条件包括 `same_question_peer_delta`、`other_question_peer_delta`、`random_gaussian_same_norm` 和 `same_question_peer_absolute`，代码还支持 `zero_delta` 和 `self_previous_delta`。
- `_build_schedule` 在第 16、32、64、96 个生成标记等截点构造注入日程。同题 delta 使用同一题其他智能体的 `state.delta`；无关题 delta 使用相邻行智能体的 `state.delta`；随机同范数向量以同题 delta 为范数参考生成；绝对状态使用同题同伴的 `state.absolute`。
- 注入时只在对应生成步和对应层生效。hook 把裁剪后的向量乘以 `steering_scale` 加到当前最后一个标记的隐藏状态：`hidden[:, -1, :] += vector * steering_scale`。
- 每条 record 写入 baseline 输出、baseline trace metadata、condition outputs、message metadata、condition trace metadata、majority answer、majority tie、correct、transition 和 answer_changed_vs_baseline。

## 结果

| 线路 | 工程对象 | 关键读数或审计事实 | 记录含义 |
| --- | --- | --- | --- |
| question-only Pre-KV | 读题 prompt 的 KV prefix | no-channel first `347/500`，Pre-KV first `349/500` | 缓存路径可运行，但搜索状态信号不足 |
| early-plan Pre-KV | 发送方短私有草稿的 live KV | 存在救回，也存在 partial trajectory anchor | 通信对象被提示词塑形 |
| micro-commitment | 结构化字段与截断 KV | 51 条 sender 输出中 46 条疑似截断 | 工程对象混入半截文本轨迹 |
| latent-rounds | 私有思考文本回编码差向量 | safe variants 净变化范围 -2 到 +1 | 比 Pre-KV 干净，但仍依赖文本化私有思考 |
| natural-search-delta | 普通 CoT decode trace 的隐藏状态 delta | 同题 delta `26/50`，随机同范数 `26/50`，无关题 delta `23/50`，绝对状态 `23/50` | 能区分部分对照，但未拉开同题 delta 与随机扰动 |

## 备注

第 22 层来自状态变化轨迹相关记录中的候选层；第 16 层保留为 latent-rounds 旧实现对照。natural-search-delta 首跑把状态来源明确记录为 `ordinary_cot_decode_trace`，并把 `uses_peer_past_key_values` 固定为 `false`，用于区别 Pre-KV 前缀接续。
