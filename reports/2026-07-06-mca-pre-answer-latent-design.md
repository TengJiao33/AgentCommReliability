# MCA-Pre：前置潜状态通信设计记录

日期：2026-07-06

## 背景

MCA-Pre 的核心约束是：通信发生在答案形成之前，通信内容不是文本答案、文本理由或人工设计的审计格式。

## 设计目标

MCA-Pre 要回答的问题是：

```text
在 agent 形成最终答案之前，另一个 agent 的内部问题表示或早期搜索状态，能否改变 receiver 的独立解题结果？
```

这里的“改变”不是指让 receiver revision 一个已写出的答案，而是让 receiver 从头解题时带着一个不可见的前置潜状态。

## 必须满足的约束

- 不使用 `certificate`。
- 不抽取文本 cue。
- 不广播 sender 的最终答案。
- 不广播 sender 的完整推理文本。
- 不在 initial answers 全部生成之后再修补答案。
- 不使用 MATH500 专属角色，例如代数路线、反例检查、边界条件专家。
- 方法应能迁移到 MATH、GSM8K、MMLU-Pro、化学、社会科学或工程问题。

## 新机制

### MCA-Pre-KV

sender 在答案形成之前运行一个前置 pass。receiver 生成答案时，继续使用 sender 这个前置 pass 产生的 KV cache。

当前源码支持两个阶段：

- `question_only`：sender 只读题并形成内部表示，不生成额外 token。
- `early_plan`：sender 生成很短的早期搜索状态，但不进入最终答案阶段。

KV 的技术边界：

- KV cache 在自回归模型里本质上仍然对应一段前缀 token。
- 因此 MCA-Pre-KV 不是纯向量消息。
- `question_only` 阶段不含 sender 答案，但仍包含题目和通用前置 pass 指令。
- `early_plan` 阶段可能已经包含部分解题方向，因此需要和 `question_only` 分开解释。

### MCA-Pre-S

sender 在答案形成之前运行一个前置 pass。源码在指定层捕获 residual activation，并把这些 activation 汇总成 steering vector。receiver 从头解题时，在对应层注入这个 vector。

S 的技术边界：

- receiver 看不到 sender 文本。
- record 会保存 sender state 的元数据，例如捕获 token 数和向量范数。
- 当前默认 `layer=16, scale=1.0` 只是可运行配置，不代表已经校准。

## 运行结构

每一题按如下顺序处理：

```text
题目出现
-> 生成 pre-answer sender state
-> 生成 no-channel baseline outputs
-> receiver 从头解题，并接收 pre-answer latent state
-> 比较 baseline majority 与 latent-channel majority
```

这种结构避免了“先得到三个答案，再广播线索”的后验问题。

## 记录口径

每条 record 使用 `mca_pre` 字段，主要内容包括：

- `pre_state_stage`：前置状态阶段；
- `state_source`：固定为 `pre_answer_sender_pass`；
- `sender_state_metadata`：前置状态的长度、捕获数、向量范数等；
- `baseline_outputs`：无通道独立解题输出；
- `baseline_majority_answer`：无通道多数答案；
- `receiver_outputs`：接收潜状态后的输出；
- `receiver_state_metadata`：使用哪个 sender state；
- `final_majority_answer`：潜状态通道多数答案；
- `transition`：从 baseline 正误到 latent-channel 正误的转移。

summary 指标使用 baseline 作为对照：

- `baseline_majority_accuracy`：无通道多数准确率；
- `final_accuracy`：潜状态通道准确率；
- `baseline_wrong_recovery_rate`：无通道多数错误时被救回的比例；
- `baseline_correct_harm_rate`：`BaC_to_W` 比例；
- `answer_change_rate`：多数答案变化率。

## 新增源码

新增：

- `scripts/mca_pre_answer_runner.py`
- `scripts/run_mca_pre_kv_cache.py`
- `scripts/run_mca_pre_activation_steering.py`
- `tests/test_mca_pre_answer_runner.py`

复用：

- `scripts/mca_hidden_channel_runner.py` 中的手写生成、KV continuation 和 activation steering 工具；
- `scripts/run_mad_mm.py` 中的标准解题 prompt 和答案解析；
- `scripts/run_basic_mad.py` 中的 majority vote、正确性判断和规范化。

## 示例命令

MCA-Pre-KV，question-only：

```bash
python scripts/run_mca_pre_kv_cache.py \
  --work-dir /data/xuhaoming/yfy/research_workspace \
  --run-id 20260706-a8002-smoke-mca-pre-kv-question-only \
  --benchmark math500 \
  --split test \
  --model-key qwen25-7b-instruct \
  --model-path /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct \
  --agents 3 \
  --reviewers 3 \
  --pre-state-stage question_only \
  --channel-mode state \
  --temperature 1.0 \
  --resolve-temperature 0.2 \
  --top-p 1.0 \
  --max-tokens 4096 \
  --resolve-max-tokens 1536 \
  --max-model-len 8192 \
  --dtype bfloat16
```

MCA-Pre-S，early-plan：

```bash
python scripts/run_mca_pre_activation_steering.py \
  --work-dir /data/xuhaoming/yfy/research_workspace \
  --run-id 20260706-a8002-smoke-mca-pre-s-early-plan \
  --benchmark math500 \
  --split test \
  --model-key qwen25-7b-instruct \
  --model-path /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct \
  --agents 3 \
  --reviewers 3 \
  --pre-state-stage early_plan \
  --pre-state-tokens 64 \
  --channel-mode state \
  --temperature 1.0 \
  --resolve-temperature 0.2 \
  --top-p 1.0 \
  --max-tokens 4096 \
  --resolve-max-tokens 1536 \
  --max-model-len 8192 \
  --dtype bfloat16 \
  --steering-layer 16 \
  --steering-scale 1.0
```

## 当前验证

已验证：

- 新增单元测试覆盖前置 prompt、receiver prompt、答案解析、source pairing 和 transition label。
- `run_mca_pre_kv_cache.py --help` 可正常显示参数。

当前缺口：

- 尚未做 GPU smoke。
- 尚未校准 MCA-Pre-S 的层、尺度和是否归一化。
- MCA-Pre-KV 的 KV 前缀仍然属于不可见上下文状态。
