# 自然搜索状态通信工程审计

日期：2026-07-08

## 要支持的原始想法

这里要支持的不是“发送方写一个计划给接收方”，而是：

```text
多个智能体自然解题时，会在中间状态里形成一些无意识的搜索方向；
这些状态不是刻意写出的计划，也不是最终答案；
如果把它以低强度、可忽略、可选择的方式传给同题同伴，可能启发对方跳出局部错误；
真正要验证的是：真实同题自然状态是否优于错题状态、随机状态和普通扰动。
```

所以工程实现必须避免三类主动干预：

```text
要求发送方生成显式计划；
让接收方续写发送方轨迹；
让通信直接支配最终答案生成。
```

## 现有实现审计

### 一、Pre-KV 当前不是旁路参考，而是前缀接续

相关代码：

```text
scripts/mca_hidden_channel_runner.py
scripts/mca_pre_answer_runner.py
scripts/run_mca_pre_kv_then_mad.py
```

关键路径：

```text
_manual_generate_sender_state(...)
  生成 sender pre-state；
  保留 past_key_values；
  past_token_count = sender prompt tokens + generated tokens。

_generate_receiver_from_state(channel="kv", ...)
  把 sender_state.past_key_values 传给 receiver；
  receiver prompt 的 position_ids 从 past_token_count 开始；
  attention_mask 覆盖 sender past + receiver prompt。
```

这意味着接收方不是“看到一个同伴状态旁路”，而是在模型内部被放到了发送方上下文之后。它继承了发送方的系统提示、题目编码、assistant 半截生成、位置编号和注意力历史。

这正好解释了已有伤害：

```text
hybrid micro-gated 里 retained KV 停在未完成 assistant completion 内部；
某些输出直接从公式中间继续写；
early-plan 中有救回，也有明显 partial trajectory anchor。
```

这条线不能直接拿来证明原始 idea。它只能证明“把别人前缀接到自己前面，有时有用，有时污染很大”。

改法：

```text
短期：停止把 Pre-KV 接续式结果作为 idea 主证据；
中期：如果继续做 KV，要改成同层旁路 memory，而不是 past 接续；
长期：实现选择性 KV 拼接或交叉注意力，让接收方保留自己的 position_ids 和 past。
```

### 二、early_plan 和 micro-commitment 主动改变发送方

相关代码：

```text
scripts/mca_pre_answer_runner.py
scripts/run_mca_pre_kv_then_mad.py
```

`pre_state_prompt(..., stage="early_plan")` 会要求：

```text
Privately sketch only the problem representation and first search direction.
Stop before final computation.
```

`visible_commitment_mode="micro"` 进一步要求结构化字段：

```text
REPRESENTATION
FIRST_MOVE
CHECK
```

这和用户强调的“不能是有意计划”冲突。它生成的是被 prompt 塑形过的文本中间产物，不是自然解题副产物。

更糟的是，`pre_state_tokens=64` 会造成大量截断。审计里已经看到：

```text
sender outputs = 51
REPRESENTATION present = 51
FIRST_MOVE present = 28
CHECK present = 2
likely truncated = 46
```

所以 micro 版本通信对象实际变成了：

```text
半截结构化文本 + 半截生成轨迹的 KV
```

这不是原始想法，也不是干净工程对象。

改法：

```text
不要再让发送方写计划字段；
不要再把固定 64 tokens 当作自然截点；
如果需要可读审计，只把文本作为事后日志，不作为通信通道；
发送方应该正常解题，状态捕获由外部 hook 完成。
```

### 三、question-only KV 的收益不能证明搜索信号

相关结果：

```text
同口径 no-channel first: 347/500
question-only Pre-KV first: 349/500
净 +2
```

这里 sender 不生成思考，`pre_state_tokens=0`，主要传的是题目阅读和提示上下文的 KV。它可以测试缓存工程是否能跑通，但不能说明“中间搜索状态有信号”。

而早期另一个 question-only 结果从 `341/500` 到 `362/500`，后来被温度和长度口径混杂影响，不能作为主证据。

改法：

```text
question-only 只保留为负对照；
它应该被明确命名为 read-state control；
真正的主实验必须捕获自然解题中的 decode 中间状态。
```

### 四、latent_rounds 更干净，但仍然不是纯自然潜状态

相关代码：

```text
scripts/run_mca_latent_rounds.py
```

它的优点：

```text
不展示同伴文本；
默认不在最终答案阶段注入同伴向量；
同伴消息有归一化、范数裁剪、低 scale；
baseline 和 latent 默认使用匹配种子；
记录了向量范数、clip 状态、答案标记审计。
```

这比 Pre-KV 更接近原始 idea。

但它仍有两个偏差：

```text
第一，它先要求模型生成 private thought 文本；
第二，它把整段 private thought 重新编码成一个 source-neutral 差向量。
```

`_thought_vector(...)` 做的是：

```text
source = Problem + Private thought
neutral = Problem + empty Private thought
vector = last_hidden(source) - last_hidden(neutral)
```

这更像“文本化私有思考的摘要方向”，不是模型自然 decode 过程里逐步产生的隐藏轨迹。它会丢掉很多时序信息，也会把文本表达习惯、提示模板和局部结论混在一起。

此外，`_generate_with_steering(...)` 的 hook 每次都改当前 forward 的最后一个 token hidden：

```text
steered[:, -1, :] += vector * steering_scale
```

这不是接收方选择性注意，而是直接加残差。虽然 scale 小，但仍然是硬注入。

改法：

```text
保留 latent_rounds 作为低强度基线；
新实现不要从 private thought 文本回编码向量；
改为在正常解题 decode 中直接捕获每步 hidden state 或 delta；
注入也应只在同步截点附近发生，而不是整个生成过程一直挂 hook。
```

### 五、层选择现在依据不足

当前默认：

```text
steering_layer = 16
```

但状态变化轨迹论文给 Qwen2.5-7B 的强候选是：

```text
22, 24, 9, 20, 12
```

我们之前第 16 层不是不能试，但不能作为主线默认。尤其在低强度注入实验里，层错了可能直接表现为零收益或噪声收益。

改法：

```text
默认主层改为 22；
小矩阵只试 22、22+24、22+24+9；
第 16 层保留为旧实现对照。
```

### 六、当前对照还不足以证明“搜索信号”

现有记录大多比较：

```text
无通信 vs 某种通信
```

但这只能回答“加这个东西是否改变结果”，不能回答“它是不是同题搜索信号”。

要支持原始 idea，必须加入：

```text
真实同题同伴状态；
同题但发送者打乱；
其他题状态；
随机高斯同范数状态；
零状态；
绝对状态；
状态变化量；
自己的历史状态。
```

成立标准也要改：

```text
真实同题状态 > 其他题状态；
真实同题状态 > 随机同范数状态；
状态变化量 > 绝对状态；
救回率上升但伤害率不能同步上升；
改变集中在原本分歧或低置信样本。
```

## 建议的新实现

### 新脚本：natural_search_delta_v0

建议新增：

```text
scripts/run_mca_natural_search_delta.py
tests/test_mca_natural_search_delta.py
```

它不应该复用 `early_plan` 或 `private_thought` 作为主通信对象。它应该复用底层生成工具，但新增一种“同步自然解题捕获器”。

### 核心数据结构

建议新增：

```text
AgentStepTrace:
  agent_index
  seed
  generated_token_ids
  generated_text_so_far
  layer_states[layer][step]
  layer_deltas[layer][step]
  logits_topk[step] 可选
  answer_marker_seen

PeerMessage:
  source_agent_index
  target_agent_index
  layer
  step
  kind = delta | absolute | random | other_question | zero
  raw_norm
  effective_norm
  clipped
  scale
```

必须记录每步元数据，否则后面无法判断是搜索信号还是扰动。

### 生成协议

不要先让一个人写完再给另一个人。改成同步协议：

```text
所有 agent 使用普通 cot_prompt 正常解题；
使用相同 prompt 家族，不加“写计划”“不要最终答案”等特殊要求；
每个 agent 逐 token 解码；
在截点 16、32、64、96 捕获选定层 last-token hidden；
计算 delta_t = h_t - h_{t-1}；
下一小段生成时，目标 agent 接收同题 peer delta 的低强度残差；
最终答案阶段默认不注入 peer delta，或者只作为显式开关。
```

这样才像：

```text
大家同时在解题；
某个自然中间状态被旁路泄露；
接收方轻微受启发，而不是续写别人。
```

### 捕获方式

当前 `_manual_generate_sender_state` 已经能用 forward hook 抓最后 token，但它最后把 captures 做均值。新实现不要均值掉。

应改成：

```text
每一步保存 selected_layers 的 last-token hidden；
每一步保存 h_t - h_{t-1}；
保存对应 token id 和局部文本；
如果已经出现 <answer> 或 \boxed，则后续状态标为 answer-contaminated。
```

层：

```text
主层：22
小矩阵：22、22+24、22+24+9
旧对照：16
```

### 注入方式

短期最小实现可以继续用 forward pre-hook，但必须改两个点：

```text
只在指定生成步注入，不要全程挂同一个向量；
只注入 delta，不优先注入 absolute state。
```

形式：

```text
hidden[:, -1, :] += scale * clipped(mean_peer_delta)
```

初始 scale：

```text
0.01, 0.03, 0.05
```

裁剪：

```text
按同层同题 delta 范数分位数裁剪；
先用 max_norm = 1.0 保守跑；
记录 raw_norm 和 effective_norm。
```

### 对照矩阵

先不要跑 full MATH500。跑：

```text
mca_disagreement_v1 前 50 条；
mca_gold_contrast_v1 前 50 条。
```

每题跑这些 condition：

```text
baseline_no_channel
same_question_peer_delta
same_question_peer_absolute
other_question_peer_delta
random_gaussian_same_norm
zero_delta
self_previous_delta
```

如果成本太高，第一轮只跑：

```text
baseline_no_channel
same_question_peer_delta
other_question_peer_delta
random_gaussian_same_norm
same_question_peer_absolute
```

### 指标

除了准确率，必须写入：

```text
BaW_to_C
BaC_to_W
BaC_to_C
BaW_to_W
answer_change_rate
same_question_advantage_vs_random
same_question_advantage_vs_other_question
delta_advantage_vs_absolute
harm_on_unanimous_baseline
recovery_on_split_baseline
```

记录层面要保存：

```text
每个 condition 的 majority answer；
每个 agent 的答案；
每个截点的 token 文本窗口；
每个截点的 peer message 范数；
是否 answer-contaminated；
是否 parser-suspect。
```

## 最小验收标准

如果要说“支持我们的 idea”，至少要看到：

```text
same_question_peer_delta 的净收益为正；
same_question_peer_delta 明显强于 other_question_peer_delta；
same_question_peer_delta 明显强于 random_gaussian_same_norm；
delta 强于 absolute；
BaC_to_W 没有随 BaW_to_C 同步上升；
救回案例里，截点文本窗口和状态注入时间能解释为搜索方向变化，而不是答案泄漏。
```

如果只看到：

```text
same_question_peer_delta 和 random 差不多；
absolute 与 delta 差不多；
救回和伤害同时增加；
主要改变来自最终答案阶段注入；
```

那就不支持原始 idea，只支持“潜向量扰动会改变采样结果”。

## 当前代码应保留和废弃的部分

保留：

```text
手写逐 token 生成；
稳定 seed；
matched baseline/latent 条件；
范数裁剪；
低 scale；
answer marker 审计；
transition 统计；
records.jsonl 详细留痕。
```

降级为对照：

```text
question-only KV；
第 16 层 steering；
整段 private thought 回编码向量；
mean peer activation；
residual peer-minus-own activation。
```

暂停作为主线：

```text
early_plan；
micro commitment；
Pre-KV continuation；
最终阶段 peer steering；
任何显式要求 REPRESENTATION/FIRST_MOVE/CHECK 的发送方协议。
```

## 下一步最小工程任务

最小可行改造不是实现选择性 KV，而是先实现自然状态 delta 诊断：

```text
1. 从 _manual_generate_with_optional_past 派生逐 token trace 生成器；
2. hook 第 22 层，保存每步 last-token hidden；
3. 计算 delta；
4. 支持按 step 注入 peer delta；
5. 加五个 condition 对照；
6. 先跑 50 条分歧子集；
7. 输出 case packet，人工看所有 BaW_to_C 和 BaC_to_W。
```

只有这一步证明真实同题 delta 优于随机/错题，再投入更重的 KV 旁路实现。
