# CPAC-DCAC guard-v1 standard MATH500 full, 24064 config

## 目的

按新主实验标准配置重跑 CPAC+DCAC guard-v1，避免旧参数体系污染正式比较。

这次运行保留 CPAC+DCAC guard-v1 机制本身，但统一生成配置：温度、采样范围、最大输出长度、最大上下文长度都对齐标准 MAD 口径。

## 设计

- 任务：`math500/test`，完整 500 题。
- 单位：一道 MATH-500 题。
- 模型：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`。
- 方法：`scripts/run_cpac_dcac.py`。
- 协议：CPAC+DCAC guard-v1。
- 初始智能体数：3。
- 复核者数：3。
- 无多数分支动作：`listwise`。
- DCAC 翻转规则：需要 2 个通过 guard-v1 的翻转证书。
- 温度：1.0。
- 声明温度：1.0。
- 证书温度：1.0。
- 列表复核温度：1.0。
- 采样范围：1.0。
- 初始最大输出长度：24064。
- 声明最大输出长度：24064。
- 证书最大输出长度：24064。
- 列表复核最大输出长度：24064。
- 最大上下文长度：24064。
- 评测器：当前本地 MATH 归一化评测器。

## 实验门禁

主要用途是进入新主实验矩阵，作为同配置下的 CPAC+DCAC guard-v1 结果。

主要对照：

- 标准 MAD：`20260705-a8002-math500-standard-mad-qwen25-7b-full-24064`。
- 同一运行内初始多数正确率。

支持信号：最终正确率高于同一运行内初始多数，且正确初始多数伤害率明显低于错误初始多数恢复率。

失效条件：输出目录碰撞、MATH-500 行数不是 500、GPU 绑定错误、24064 输出/上下文上限触发 vLLM 参数错误、运行超时或崩溃、最终解析失败率异常、同一输出目录被多个进程同时写入。

## 机器

- 主机：`A800_2`。
- 远端工作目录：`/data/xuhaoming/yfy/research_workspace`。
- Python 环境：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`。
- GPU：`6`。

## 启动

见 `run_remote.sh`。

## 状态

`RUNNING_GPU6`。

`2026-07-05T20:04:33+08:00` 启动完整运行：

- 外层超时保护进程：`3087782`。
- 实际推理进程：`3087783`。
- GPU：`6`。
- 启动后检查：GPU6 约 `66513 MiB` 显存占用，利用率约 `77%`。
- 日志显示模型已加载，`max_tokens=24064` 与 `max_model_len=24064` 没有在启动阶段触发 vLLM 参数错误。

## 预期输出

- `math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.json`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.md`
- `run_remote.nohup.log`
