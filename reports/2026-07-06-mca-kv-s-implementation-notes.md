# MCA-KV / MCA-S 实现记录

## 做法

1. 运行按题目逐行处理。每道题先进入发送方生成阶段，发送方使用标准解题提示词正常生成答案文本；这一阶段的目的不是把文本展示给接收方，而是在生成过程中捕获发送方的内部状态。

2. MCA-KV 通道在发送方生成时保留 `past_key_values`。这份缓存包含发送方提示词和已生成标记的注意力历史，作为接收方生成时的不可见状态来源。

3. MCA-S 通道在发送方生成时给指定 transformer 层注册前向钩子。钩子捕获发送方生成过程中的 residual input activation，并把一批捕获到的激活向量汇总为一个 steering vector。

4. 对照条件使用 `--channel-mode none`。此时接收方只读取自己的题目提示词，从头生成答案，不接收发送方文本、KV cache 或激活向量。

5. MCA-KV 条件下，接收方提示词本身不包含发送方文本。生成函数把发送方 `past_key_values` 传入 receiver，使接收方在模型内部延续发送方缓存后的状态生成。

6. MCA-S 条件下，接收方同样从自己的题目提示词开始生成。生成时在同一 transformer 层注册 steering hook，把发送方汇总向量注入接收方当前标记的 residual stream。

7. 每题完成后，运行器立即写出 record。record 同时保存发送方状态元数据、接收方输出、是否使用 hidden channel、解析答案、多数投票结果和正误转移。

8. summary 复用 MATH evaluator、majority vote、transition label 和 summary 指标。smoke run 只检查能否完整写出 `records.jsonl` 和 `summary.json`，不解释准确率。

## 工程细节

- 共享运行器：`scripts/mca_hidden_channel_runner.py`。
- KV 通道入口：`scripts/run_mca_kv_cache.py`。
- 激活向量通道入口：`scripts/run_mca_activation_steering.py`。
- 单元测试：`tests/test_mca_hidden_channels.py`。
- 共同流程：每题流式执行 sender generation、状态捕获、receiver generation、record 写入。
- MCA-KV：发送方解题提示词和已生成 tokens 对应的 `past_key_values` 传给 receiver。
- MCA-S：发送方真实生成过程中用 hook 捕获指定 transformer layer 的 residual input activation；默认取捕获向量均值作为 steering vector；接收方生成时在同层把该向量注入当前 token 的 residual stream。
- 对照通道：`--channel-mode none` 提供 no-channel control。
- 复用口径：MATH evaluator、majority vote、transition label 和 summary 指标。
- 进度日志：`[mca-hidden] row ...`、`sender generation ...`、`receiver generation ...`、`records written ...`。
- 最小 smoke 命令保存在原始运行记录中，检查目标是能写出 `records.jsonl` 和 `summary.json`。

## 结果

| 检查项 | 结果 |
| --- | --- |
| Python compile | pass |
| `run_mca_kv_cache.py --help` | pass |
| `run_mca_activation_steering.py --help` | pass |
| 全量单元测试 | 47 tests passed |
| MCA-KV smoke | 2 rows，93.0s，records 和 summary 写出 |
| MCA-S first smoke | row 2 receiver generation 时 CUDA OOM |
| MCA-S rerun | 2 rows，102.1s，records 和 summary 写出 |

## 备注

MCA-KV 属于强 hidden-state transfer，可能携带发送方 reasoning / answer 信息。MCA-S first smoke 后做过两处实现修正：receiver manual generation 进入 `torch.inference_mode()`；MCA-S sender state 不再保留未使用的 sender KV caches。MCA-S rerun 中两个 smoke rows 都发生答案改变，并出现 `final answer only` 被解析成答案的格式污染。
