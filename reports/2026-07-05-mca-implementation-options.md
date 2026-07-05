# MCA 实现方案：从显式 cue 到底层状态通信

日期：2026-07-05

## 问题定义

这里的 `MCA` 暂按 **Metacognitive Communication / Activation** 理解：一个 agent 不只把最终答案传给另一个 agent，而是把“这题该注意什么、该检查什么、可能踩什么坑”的认知状态传过去，让 receiver 的推理过程发生变化。

关键实现问题不是“要不要提示 receiver”，而是通信载荷是什么：

- 显式文本：receiver 直接看到 cue。
- 连续向量：receiver 不看到 cue 文本，但输入 embedding 被条件化。
- KV/hidden state：receiver 接收 sender 的内部状态片段。
- activation steering：receiver 的中间层被注入某种 metacognitive direction。

因此 MCA 可以做成四个实现层级。它们不是互相排斥，而是从低风险到高底层程度逐步推进。

## 当前代码基础

当前仓库里最可复用的代码是：

- `scripts/run_cpac_dcac.py`：已有 initial agents、candidate pool state、DCAC/listwise branch 和 summary 结构。
- `scripts/run_consensus_quarantine.py`：已有 `independent_prompt`、`build_candidate_cards`、`generate_outputs`、`generate_plain_texts`、`reshape`。
- `scripts/run_basic_mad.py`：已有 evaluator、`majority_vote`、`normalize_numeric`、`is_correct`、`prompt_from_messages`。

这些代码适合支撑显式 text cue 版本。更底层的 soft prefix、KV/hidden、activation steering 不适合直接用 vLLM runner 做，因为需要访问 `inputs_embeds`、hidden states、hooks 或 `past_key_values`。这些版本更适合另开 HuggingFace backend runner。

## 方案总览

| 方案 | 通信载荷 | 是否显式改变 prompt | 后端 | 工程难度 | 用途 |
|---|---|---:|---|---:|---|
| MCA-T | answer-free text cue | 是 | vLLM | 低 | 快速验证 cue uptake 是否有信号 |
| MCA-P | continuous soft prefix | 否 | Transformers | 中 | 第一版底层机制主线 |
| MCA-KV | hidden state / KV cache | 否 | Transformers hooks | 高 | 更接近内部状态通信 |
| MCA-S | residual activation steering | 否 | Transformers hooks | 中高 | 测 metacognitive direction 是否可迁移 |

## 方案一：MCA-T，显式 Text Cue

MCA-T 是最容易落地的版本。它的目标不是作为最终“底层机制”，而是判断这个 idea 是否有行为信号：错误 agent 是否可能贡献有用 cue，cue-only communication 是否带来 recovery，同时 harm 是否可控。

源码入口建议新增：

- `scripts/run_mca_text.py`
- `tests/test_mca_text.py`

核心流程：

```text
initial_solve
  -> cue_extraction
  -> answer_leak / generic / duplicate filter
  -> cue_only_resolve
  -> majority aggregation
  -> transition metrics
```

主要函数：

```python
def cue_extraction_prompt(question, agent_output, cue_k): ...
def parse_cue_atoms(text): ...
def filter_cues(cues, candidate_cards): ...
def cue_resolve_prompt(question, kept_cues, reviewer_idx): ...
def parse_cue_resolve_output(text): ...
def summarize_mca_text_records(records): ...
```

记录字段：

```json
{
  "initial_outputs": [],
  "candidate_cards": [],
  "cue_atoms": [],
  "filtered_cues": [],
  "cue_resolve_outputs": [],
  "initial_majority_answer": "...",
  "mca_final_answer": "...",
  "transition": "MaW_to_C"
}
```

必须记录的指标：

- `cue_coverage_rate`
- `answer_leak_rate`
- `generic_cue_rate`
- `cue_uptake_self_report_rate`
- `initial_majority_accuracy`
- `mca_final_accuracy`
- `MaW_to_C`
- `MaC_to_W`
- 按 `collapse / minority_bearing / no_majority_conflict` 拆分的 recovery 和 harm。

这个方案的限制很明确：receiver 显式读到了 cue，因此它证明不了“底层通信”成立，只能证明“answer-free cue 作为通信单位可能有用”。

## 方案二：MCA-P，Soft Prefix / Continuous Cue

MCA-P 是我认为最适合作为底层第一版的实现。它不把 cue 文本交给 receiver，而是把 sender 的 metacognitive signal 压成连续 prefix vectors，拼到 receiver 的 embedding 前面。

源码入口建议新增：

- `scripts/run_mca_soft_prefix.py`
- `scripts/mca_hf_backend.py`
- `tests/test_mca_soft_prefix.py`

核心流程：

```text
sender initial solve
  -> collect sender hidden states or encode cue summary
  -> cue projector maps to K virtual token embeddings
  -> receiver input = [soft_prefix_embeds ; question_embeds]
  -> receiver generate answer
  -> majority aggregation / transition metrics
```

最小可实现版本不训练 projector，而是使用同一模型 embedding 空间构造 prefix：

```python
cue_text = extract_answer_free_cue_text(...)
cue_ids = tokenizer(cue_text)
cue_embeds = model.get_input_embeddings()(cue_ids)
soft_prefix = pool_or_truncate(cue_embeds, prefix_len)
inputs_embeds = torch.cat([soft_prefix, question_embeds], dim=1)
```

这个版本仍然从文本 cue 得到向量，但 receiver 没看到 cue tokens。它是 MCA-T 到真正 latent communication 的过渡实现。

更强版本可以加入 projector：

```python
source_hidden = mean_pool(sender_hidden[layer], cue_token_span)
soft_prefix = projector(source_hidden).view(prefix_len, hidden_size)
```

需要的后端能力：

- `transformers.AutoModelForCausalLM`
- `output_hidden_states=True`
- `model.generate(inputs_embeds=..., attention_mask=...)`
- 对 Qwen2.5 的 chat template 和 position ids 做一次 smoke。

主要风险：

- `generate(inputs_embeds=...)` 在不同模型实现里支持程度不同，需要本地 smoke。
- prefix 位置会影响 RoPE position，需要固定 prefix length，并让 question tokens 的 position 接在 prefix 后面。
- 如果 prefix 来自 cue text embedding，审稿时可能被认为仍是 text cue 的隐式形式。因此需要报告清楚：MCA-P 第一版是 continuous transport ablation，不是最终 hidden-state claim。

关键对照：

- text cue visible。
- same cue converted to soft prefix。
- random unrelated cue prefix。
- zero prefix。
- shuffled cue prefix。

如果 soft prefix 接近 text cue，且明显优于 random/zero prefix，说明 cue information 可以通过非显式 token 通道影响 receiver。

## 方案三：MCA-KV，Hidden State / KV Cache Communication

MCA-KV 是更底层的 agent-to-agent 内部状态通信。sender 解题时，系统抽取某些层的 hidden state 或 KV cache，receiver 解题时将其作为前缀状态注入。

源码入口建议新增：

- `scripts/run_mca_kv.py`
- `scripts/mca_state_transfer.py`
- `tests/test_mca_state_transfer.py`

两种实现路径：

```text
Hidden-state prefix:
sender hidden states -> projector -> receiver soft prefix embeddings

KV-prefix:
sender past_key_values -> adapter -> receiver past_key_values prefix
```

Hidden-state prefix 比 KV-prefix 稳。KV-prefix 的问题是每层、每个 head、position encoding 都要严格对齐；如果直接移植 sender KV，receiver question 的 position 和 cache position 很容易错位。

建议第一版不要直接做 KV transplant，而是先做 hidden-state-to-prefix：

```python
sender_outputs = model(..., output_hidden_states=True)
state = pool(sender_outputs.hidden_states[layer], selected_span)
soft_prefix = projector(state)
receiver_generate(inputs_embeds=[soft_prefix; question_embeds])
```

如果一定要做 KV-prefix，至少需要固定：

- 同一个模型、同一个 tokenizer。
- 同一层数、同一 hidden/head 维度。
- prefix cache length。
- receiver question 的 `position_ids` 从 prefix length 后开始。
- attention mask 覆盖 prefix cache 和 question tokens。

关键指标不是只看 accuracy，还要看：

- state transfer 后 parse fail 是否上升。
- receiver 是否出现格式崩坏。
- random sender state 是否同样提升。
- wrong sender state 是否带来 harm。
- same-question sender state 与 unrelated-question sender state 的差距。

MCA-KV 的论文味更强，但工程失败风险也最大。若 MCA-P 没有信号，不建议直接跳到 MCA-KV。

## 方案四：MCA-S，Activation Steering

MCA-S 不在单题内传 sender cue，而是从一批样本里估计“metacognitive direction”，然后在 receiver 解题时注入这个方向。

可选方向：

```text
representation_check_direction
constraint_awareness_direction
pitfall_avoidance_direction
sanity_check_direction
```

估计方式：

```text
positive traces: 有明确有效 cue 或人工标注为关键检查的 traces
negative traces: 普通 direct solve 或无效 cue traces
direction = mean(hidden_positive[layer]) - mean(hidden_negative[layer])
```

注入方式：

```python
hidden_states[layer][:, token_pos, :] += alpha * direction
```

这个方案需要 forward hook，而不是普通 `generate`。源码上要包装模型层：

```python
handle = model.model.layers[layer].register_forward_hook(steering_hook)
```

关键对照：

- no steering。
- random direction。
- wrong direction。
- layer sweep。
- alpha sweep。

MCA-S 的优势是机制很底层，也可能不依赖每题 sender。缺点是它偏“控制模型推理倾向”，不再是严格的 agent-to-agent communication。论文表述上应把它写成 MCA 的 extension 或 ablation，而不是主定义。

## 推荐实现顺序

建议顺序是：

```text
MCA-T -> MCA-P -> MCA-KV / MCA-S
```

具体原因：

1. MCA-T 用现有 vLLM runner 最快验证现象：answer-free cue 是否有 recovery/harm 信号。
2. MCA-P 是最合适的底层主线：receiver 不看 cue 文本，但工程上仍可控。
3. MCA-KV 最像内部状态通信，但容易被 RoPE/cache 对齐问题拖住。
4. MCA-S 很底层，但更像 steering，不完全等同 agent communication。

如果只能选一个更底层方案优先做，我建议选 MCA-P。它的实验问题最干净：

> 同一个 answer-free cue，不作为文字给 receiver，而作为 continuous prefix 注入时，是否仍能改善 receiver 的解题结果？

这个问题比“直接注入 KV cache 是否有效”更容易诊断，也比 text cue 更不容易被批评成 prompt engineering。

## 最小工程拆分

第一阶段可以只写 MCA-T 和 MCA-P 的公共评估壳：

```text
scripts/mca_records.py
  - transition metrics
  - pool-state split
  - records/summary writer

scripts/run_mca_text.py
  - vLLM text cue path

scripts/run_mca_soft_prefix.py
  - HF continuous prefix path
```

公共 records 字段保持一致：

```json
{
  "mca_variant": "text|soft_prefix|hidden_prefix|kv|steering",
  "initial": {},
  "communication_payload": {},
  "receiver_outputs": [],
  "final": {},
  "metrics_context": {
    "pool_state": "...",
    "oracle_initial_present": true,
    "representation_risks": []
  }
}
```

这样后续四种方案可以共用同一套分析脚本，不会每跑一版都重新解释指标。

## 验证边界

MCA-T 的正结果只能说明：显式 answer-free cue 可能有用。

MCA-P 的正结果可以说明：cue information 在非显式 token 通道中仍可影响 receiver。

MCA-KV 的正结果才更接近：agent 内部状态片段可以作为通信载荷。

MCA-S 的正结果说明：存在可注入的 metacognitive control direction，但不自动证明跨 agent 通信。

所有方案都必须同时报告 recovery 和 harm。只报告 final accuracy 会掩盖一个关键问题：cue/state 通信可能恢复错多数，也可能污染原本正确的 agent。

## 当前落地建议

当前最合理的源码落点是：

1. 先写 `run_mca_text.py`，拿行为信号和 failure cases。
2. 同时设计 records schema，使它能容纳 soft prefix 和 hidden-state payload。
3. 行为信号存在后，写 `run_mca_soft_prefix.py` 作为底层主版本。
4. 暂缓 KV transplant，除非 soft prefix 已经证明有稳定信号。

这份方案的核心不是让 MCA 停留在 prompt cue，而是用 prompt cue 做诊断，再把同一个通信对象降到 continuous prefix / hidden-state 层面。
