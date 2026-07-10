# MCA-Pre 前置潜状态通信实现记录

## 做法

1. MCA-Pre 先为每道题运行发送方前置阶段。发送方不进入完整答题流程，而是在接收方生成答案之前先产生一段不可见状态。

2. `question_only` 前置阶段只让发送方读题并形成内部表示。该阶段不生成额外标记，因此保存的是题目和前置指令对应的内部状态。

3. `early_plan` 前置阶段让发送方生成短的早期搜索状态。该阶段仍然不要求最终答案，但会留下由少量生成标记形成的 live KV 或激活轨迹。

4. 无通道基线先运行。3 个接收方分别从自己的题目提示词开始生成答案，不接收发送方状态；脚本解析 3 个答案并做多数投票，得到 baseline majority。

5. MCA-Pre-KV 条件下，发送方前置阶段产生的 `past_key_values` 被交给接收方。接收方提示词接在 sender past 之后继续生成，因此模型内部能访问发送方前置 pass 的注意力历史。

6. MCA-Pre-S 条件下，发送方前置阶段在指定层捕获 residual activation，并把捕获向量汇总成 steering vector。接收方从自己的题目提示词开始生成，在对应层注入该向量。

7. 每道题的接收方输出完成后，脚本解析答案，对 3 个接收方做多数投票，并与无通道多数答案比较。

8. 每条记录保存前置阶段类型、状态来源、发送方状态元数据、无通道输出、无通道多数答案、接收方输出、接收方状态元数据、最终多数答案和正误转移。

9. summary 汇总 baseline majority accuracy、final accuracy、baseline wrong recovery rate、baseline correct harm rate 和 answer change rate。

## 工程细节

- 共享运行器：`scripts/mca_pre_answer_runner.py`。
- KV 通道入口：`scripts/run_mca_pre_kv_cache.py`。
- 激活向量通道入口：`scripts/run_mca_pre_activation_steering.py`。
- 单元测试：`tests/test_mca_pre_answer_runner.py`。
- 复用模块：`scripts/mca_hidden_channel_runner.py` 的手写生成、KV continuation 和 activation steering 工具。
- 复用答案处理：`scripts/run_mad_mm.py` 的标准解题提示词和答案解析；`scripts/run_basic_mad.py` 的 majority vote、正确性判断和答案归一化。
- 前置阶段 `question_only`：发送方只读题并形成内部表示，不生成额外 token。
- 前置阶段 `early_plan`：发送方生成短早期搜索状态，但不进入最终答案阶段。
- MCA-Pre-KV：接收方生成时继续使用发送方前置 pass 产生的 KV cache。
- MCA-Pre-S：发送方前置 pass 在指定层捕获 residual activation，汇总成 steering vector；接收方从头解题时在对应层注入该向量。
- 默认激活配置：`layer=16`，`scale=1.0`。
- 每题处理顺序：题目出现；生成 pre-answer sender state；生成 no-channel baseline outputs；receiver 从头解题并接收 pre-answer latent state；比较 baseline majority 与 latent-channel majority。
- 每条记录字段：`mca_pre.pre_state_stage`、`state_source`、`sender_state_metadata`、`baseline_outputs`、`baseline_majority_answer`、`receiver_outputs`、`receiver_state_metadata`、`final_majority_answer`、`transition`。
- summary 指标：`baseline_majority_accuracy`、`final_accuracy`、`baseline_wrong_recovery_rate`、`baseline_correct_harm_rate`、`answer_change_rate`。

## 结果

| 检查项 | 状态 |
| --- | --- |
| 前置提示词单元测试 | 通过 |
| receiver prompt 单元测试 | 通过 |
| 答案解析单元测试 | 通过 |
| source pairing 单元测试 | 通过 |
| transition label 单元测试 | 通过 |
| `run_mca_pre_kv_cache.py --help` | 可正常显示参数 |

## 备注

KV cache 在自回归模型里对应前缀 token 状态。`question_only` 阶段不含发送方答案，但包含题目和前置 pass 指令；`early_plan` 阶段可能包含部分解题方向。MCA-Pre-S 的记录会保存捕获 token 数和向量范数等元数据。
