# CPAC-DCAC guard-v1 standard-fixed MATH500 full 4096 实验记录

## 目的

使用与 Standard MAD 基线相同的 chat-rendered Standard MAD 初始 prompt family，运行 guarded CPAC+DCAC 机制。

主要对比是同一运行内的初始多数结果与 guarded CPAC+DCAC 最终结果。

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
- 计划 GPU：`2`。

## 启动

见 `run_remote.sh`。

## 状态

`COMPLETED`。

已生成完整 `summary.json` 与 `records.jsonl`。

## 结果

- Rows：500。
- Initial majority：364/500 = 0.728。
- Final correct：368/500 = 0.736。
- Final majority ties：4/500 = 0.008。
- Final parse fail：0。
- 相对初始多数净变化：+4 题。
- elapsed seconds：2367.85。

## 机制诊断

- correct majority preservation rate：0.9973。
- keep initial：279。
- 该机制起作用，但提升幅度弱于当前 Standard MAD 基线。

## 输出

- `math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.json`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.md`
- `launcher.out.log`
- `launcher.err.log`
- `run_remote.sh`
