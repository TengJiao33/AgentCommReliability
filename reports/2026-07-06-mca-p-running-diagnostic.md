# MCA-P soft-prefix 运行诊断

日期：2026-07-06

## 做法

1. MCA-P soft-prefix 运行先读取 MATH-500 题目，并使用与标准 MAD 对齐的初始提示词生成第一轮答案池。

2. 每道题先进入无通道路径。智能体从自己的题目提示词开始生成答案，不接收 soft-prefix、文本线索或同伴缓存。

3. 脚本随后从初始答案池和可用线索中构造 soft-prefix cue。这个 cue 不是直接追加为普通文本答案，而是作为 soft-prefix resolve 阶段的输入状态。

4. soft-prefix resolve 阶段让接收方在题目提示词基础上接收 soft-prefix 条件，再生成答案。该阶段的目标是观察 soft-prefix 是否改变最终解析答案。

5. 每题完成后，脚本解析无通道答案和 soft-prefix 答案，分别做多数投票，并记录答案是否改变、是否正确、是否平票和正误转移。

6. 远端诊断时，运行进程还在执行，但 `records.jsonl` 和 `summary.json` 尚未写出。检查重点放在进程状态、GPU 状态、日志进度和代码路径是否卡住。

7. 诊断确认远端 PID `1135755` 不是僵尸进程，也不是 sleep 或 I/O wait；GPU 仍有负载，说明主线程和模型计算仍在推进。

8. 本地后来给 `scripts/run_mca_soft_prefix.py` 增加进度日志，使日志能区分 run start、loaded rows、model loaded、initial answers completed、cue extraction completed、soft-prefix resolve completed、records written 和 run complete。

9. 本地编译和单元测试只验证代码可运行性，不改变远端已经运行的 PID `1135755`。

## 工程细节

- 诊断对象：远端 `scripts/run_mca_soft_prefix.py` 运行。
- 远端 PID：`1135755`。
- 当时状态：`records.jsonl` 和 `summary.json` 尚未写出。
- 检查项：进程状态、GPU 占用、是否 zombie、是否 sleep、是否 I/O wait、是否有 Python traceback。
- 本地改动文件：`scripts/run_mca_soft_prefix.py`。
- 新增进度日志节点：run start、loaded rows、model loaded、initial answers completed、cue extraction completed、soft-prefix resolve completed、records written、run complete。
- 本地编译：`python -m py_compile scripts/run_mca_soft_prefix.py scripts/mca_hidden_channel_runner.py`。
- 本地测试：`python -m unittest discover -s tests -p "test_*.py"`。

## 结果

| 检查项 | 结果 |
| --- | --- |
| 远端 PID `1135755` | 仍在运行 |
| zombie 状态 | 否 |
| sleep / I/O wait | 否 |
| GPU 状态 | 有负载 |
| `records.jsonl` | 当时尚未写出 |
| `summary.json` | 当时尚未写出 |
| 本地编译 | 通过 |
| 本地单元测试 | 46 tests passed |

## 备注

本地进度日志改动发生在远端 PID `1135755` 启动之后，因此不影响该远端进程的代码行为。该记录只说明运行诊断状态，不包含完整结果读数。
