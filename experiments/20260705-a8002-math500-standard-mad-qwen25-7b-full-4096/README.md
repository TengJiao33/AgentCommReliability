# Standard MAD MATH500 full, 4096 output config

## 目的

按新的主实验输出预算重跑 MATH-500 全量标准 MAD。该 run 是当前 MATH-500 标准 MAD 主基线。

## 设计

- 任务：`math500/test`，完整 500 题。
- 模型：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`。
- 方法：`scripts/run_mad_mm.py`。
- 标准 MAD 定义：`prune_strategy=naive`，上一轮 3 个解法全部保留给下一轮。
- 智能体数：3。
- 总轮次：2。
- 温度：1.0。
- 采样范围：1.0。
- 最大输出长度：4096。
- 最大上下文长度：24064。
- 评测器：当前本地 MATH 归一化评测器。

## 实验门禁

主要用途是为新主实验矩阵建立标准 MAD 基线。本 run 使用 4096 输出预算和 24064 上下文预算。

支持信号：运行完整 500 题，解析失败率正常，输出 `summary.json` 与 `records.jsonl`。

失效条件：输出目录碰撞、MATH-500 行数不是 500、GPU 绑定错误、运行超时或崩溃、最终解析失败率异常。

## 机器

- 主机：`A800_2`。
- 远端工作目录：`/data/xuhaoming/yfy/research_workspace`。
- Python 环境：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`。
- GPU：`4`。

## 启动

见 `run_remote.sh`。

## 状态

`COMPLETED`。

`2026-07-05T20:50+08:00` 启动完整运行：

- 远端启动器 PID：`3402264`。
- 外层超时保护进程：`3402327`。
- 实际推理进程：`3402328`。
- GPU：`4`。
- 启动后检查：GPU4 约 `66705 MiB` 显存占用，利用率约 `91%`。
- 日志显示模型已加载并进入生成阶段；运行命令使用 `max_tokens=4096` 与 `max_model_len=24064`。

`2026-07-05T21:59+08:00` 轮询发现运行完成：

- Rows：500。
- Initial majority：364/500 = 0.728。
- Standard MAD final：378/500 = 0.756。
- final majority ties：19/500。
- final parse fail：0。
- memory retention rate：1.0。
- agent final accuracy：0.752、0.744、0.748。
- elapsed seconds：3977.8。

## 预期输出

- `math500-qwen25-7b-instruct-naive/records.jsonl`
- `math500-qwen25-7b-instruct-naive/summary.json`
- `math500-qwen25-7b-instruct-naive/summary.md`
- `run_remote.nohup.log`

## 边界

该 run 是 4096 输出预算主口径。非此口径的废弃尝试不进入主比较。
