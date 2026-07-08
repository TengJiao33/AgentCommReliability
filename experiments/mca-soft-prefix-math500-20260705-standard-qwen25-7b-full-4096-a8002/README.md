# MCA-P standard MATH500 full 4096 实验记录

## 目的

按当前标准口径重新运行 MCA-P，不复用任何旧 records，避免非标准旧池污染当前横向比较。该 run 自己重新采样 3 路初始答案，但初始 prompt 使用 Standard MAD prompt family，目标是使 initial majority 落在当前 Standard MAD 水平附近。

## 设计

- 任务：`math500/test`，完整 500 题。
- 模型：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`。
- 方法：`scripts/run_mca_soft_prefix.py`。
- 初始输出来源：本 run 独立重采样，不使用 `--input-records`。
- 初始 prompt：`--initial-prompt-style standard-mad`。
- 前缀来源：过滤后的不含答案提示。
- 前缀长度：32。
- 前缀填充：均值填充。
- 智能体数：3。
- 复核者数：3。
- 候选池状态范围：`all`。
- 温度：1.0。
- cue 温度：1.0。
- resolve 温度：1.0。
- top-p：1.0。
- 最大生成输出长度：4096。
- cue 抽取最大输出长度：4096。
- cue-only 重新求解最大输出长度：4096。
- 最大上下文长度：24064。

## 实验门禁

主要用途是生成当前标准口径下的 MCA-P full diagnostic，与 Standard MAD 4096 和 MAD-MM 362-level records 分开读。

## 机器

- 主机：`A800_2`。
- 远端工作目录：`/data/xuhaoming/yfy/research_workspace`。
- Python 环境：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`。
- GPU：`1`。

## 启动

见 `run_remote.sh`。

## 状态

`NO_LOCAL_SUMMARY`。

`2026-07-05T22:22+08:00` 启动完整运行：

- 远端启动器 PID：`3644693`。
- 外层超时保护进程：`3644709`。
- 实际推理进程：`3644710`。
- GPU：`1`。
- 启动后检查：evaluator smoke 与 import smoke 通过，MATH-500 行数为 500；模型权重已开始加载。
- 运行命令不传 `--input-records`，显式使用 `--initial-prompt-style standard-mad`、主生成/cue/resolve `max_tokens=4096`、`max_model_len=24064`，temperature/top-p 均为 1.0。

本地目录没有 `summary.json` 或 `records.jsonl`。2026-07-06 远端另有 aligned MCA-P soft-prefix 运行：

```text
A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-soft-prefix-standard-madmm-aligned-qwen25-7b-full/
```

最近一次只读检查时，该 aligned run 仍在 GPU 6 上运行，尚未看到 summary。

## 预期输出

- `math500-qwen25-7b-instruct-mca-soft-prefix-cue-all/records.jsonl`
- `math500-qwen25-7b-instruct-mca-soft-prefix-cue-all/summary.json`
- `math500-qwen25-7b-instruct-mca-soft-prefix-cue-all/summary.md`
- `run_remote.nohup.log`
