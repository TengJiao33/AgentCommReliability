# Standard MAD MATH500 full, 24064 config

## 目的

按当前重新约定的标准口径重跑 MATH-500 全量标准 MAD。

这次运行不再使用旧 `run_basic_mad.py` 的简化设置，而是使用 MAD-MM 官方仓库中的 MAD 基线口径：不做记忆遮罩，也就是 `prune_strategy=naive`。

## 设计

- 任务：`math500/test`，完整 500 题。
- 单位：一道 MATH-500 题。
- 模型：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`。
- 方法：`scripts/run_mad_mm.py`。
- 标准 MAD 定义：`prune_strategy=naive`，上一轮 3 个解法全部保留给下一轮。
- 智能体数：3。
- 总轮次：2。
- 温度：1.0。
- 采样范围：1.0。
- 最大输出长度：24064。
- 最大上下文长度：24064。
- 评测器：当前本地 MATH 归一化评测器。

## 实验门禁

主要用途是为新主实验矩阵建立标准 MAD 基线。旧的 `20260705-a8002-math500-basic-mad-qwen25-7b-full` 只保留为探索诊断，不再作为标准 MAD。

支持信号：运行完整 500 题，解析失败率正常，输出 `summary.json` 与 `records.jsonl`，可作为后续 MCA/MAD-MM 同配置比较基线。

失效条件：输出目录碰撞、MATH-500 行数不是 500、GPU 绑定错误、24064 输出上限与远端 vLLM 请求约束不兼容、运行超时或崩溃、最终解析失败率异常。

## 机器

- 主机：`A800_2`。
- 远端工作目录：`/data/xuhaoming/yfy/research_workspace`。
- Python 环境：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`。
- GPU：`4`。

## 启动

见 `run_remote.sh`。

## 状态

`RUNNING_GPU4`。

`2026-07-05T19:57:28+08:00` 启动完整运行：

- 外层超时保护进程：`3037229`。
- 实际推理进程：`3037230`。
- GPU：`4`。
- 启动后检查：GPU4 约 `66555 MiB` 显存占用，利用率约 `91%`。
- 日志显示模型已加载并进入生成阶段；`max_tokens=24064` 与 `max_model_len=24064` 没有在启动阶段触发 vLLM 参数错误。

## 预期输出

- `math500-qwen25-7b-instruct-naive/records.jsonl`
- `math500-qwen25-7b-instruct-naive/summary.json`
- `math500-qwen25-7b-instruct-naive/summary.md`
- `run_remote.nohup.log`
