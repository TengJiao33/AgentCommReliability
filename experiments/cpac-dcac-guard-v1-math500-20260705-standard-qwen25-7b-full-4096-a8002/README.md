# CPAC-DCAC guard-v1 standard MATH500 full 4096 实验记录

## 目的

在当前标准 MATH-500 对比口径下运行带 guard 的 CPAC+DCAC 机制。

主要对比是同一运行内的初始多数结果与 guarded CPAC+DCAC 最终结果。该运行用于把旧的 guard-v1 诊断放到当前 Standard MAD 4096 / 24064 设置下比较。

## 设计

- 任务：`math500/test`，完整 500 题。
- 模型：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`。
- 方法：`scripts/run_cpac_dcac.py`。
- 协议：Candidate-Pool Adaptive Consensus，并在 minority-bearing 分支使用 guarded DCAC。
- 初始求解智能体：3 个独立样本。
- 复核者：3 个 certificate/listwise reviewer。
- 无多数动作：`listwise`。
- DCAC 翻转规则：需要 2 个 guarded admissible flip certificates。
- 温度与 top-p：所有 generation temperature 为 `1.0`，top-p 为 `1.0`。
- 输出预算：initial、claim、certificate、listwise 的 max tokens 均为 `4096`。
- 上下文预算：`max_model_len=24064`。

## 机器

- 主机：`A800_2`。
- 远端工作目录：`/data/xuhaoming/yfy/research_workspace`。
- Python 环境：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`。
- 计划 GPU：`5`。

## 启动

见 `run_remote.sh`。

## 状态

`REMOTE_COMPLETED_LOCAL_SUMMARY_NOT_SYNCED`。

2026-07-05 23:07 CST 启动。

- 第一次尝试在 GPU `6` 上已加载模型，但在 vLLM KV-cache 分配阶段因 `gpu_memory_utilization=0.85` 触发 CUDA OOM；没有产生 records 或 summary。
- 重启后使用 GPU `5`，`gpu_memory_utilization=0.55`，模型、prompt、温度、token budget 和 `max_model_len=24064` 保持不变。
- Launcher PID：`3832761`。
- Timeout PID：`3832798`。
- Python PID：`3832799`。
- GPU：`5`。
- 日志：`/data/xuhaoming/yfy/research_workspace/experiments/cpac-dcac-guard-v1-math500-20260705-standard-qwen25-7b-full-4096-a8002/run_remote.nohup.log`。
- 启动检查：evaluator smoke 和 guard smoke 通过；Qwen2.5-7B 以 `max_seq_len=24064` 加载；KV cache 初始化为 30177 个 GPU blocks；CUDA graph capture 完成。
- 第一次失败日志归档为 `run_remote.oom-gpu6-2307.log`。

远端在 `A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260705-a8002-math500-cpac-dcac-guard-v1-standard-qwen25-7b-full-4096/` 有 summary：

- Rows：500。
- Initial majority：313/500 = 0.626。
- Final correct：327/500 = 0.654。
- Final majority ties：4/500 = 0.008。
- Final parse fail：0。
- Answer changed：52/500 = 0.104。
- CPAC pool states：collapse 201，minority-bearing 183，no-majority conflict 116。
- DCAC flips：7；guard blocked flips：6；guard rejected certificates：183。

## 预期输出

- `math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.json`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.md`
- `run_remote.nohup.log`
- `launcher.pid`
