# MCA-P MATH500 远端冒烟

## 目的

验证 `scripts/run_mca_soft_prefix.py` 能在 A800_2 上真实加载 Qwen2.5-7B-Instruct，并走通“提示抽取、提示过滤、连续前缀生成、复核生成、汇总写入”链路。

## 设计

- 任务：`math500/test`，前 2 题。
- 模型：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`。
- 方法：MCA-P，连续前缀版。
- 初始输出来源：复用 CPAC 完整运行的 `records.jsonl`。
- 前缀来源：过滤后的不含答案提示。
- 前缀长度：32。
- 候选池状态范围：`all`。
- GPU：`1`。

## 状态

`COMPLETED`。

## 结果

- 远端启动器 PID：`2879463`。
- 实际运行进程：`2879487`。
- 用时：70.9 秒。
- 行数：2。
- 初始多数正确：2/2。
- MCA-P 最终正确：1/2。
- 转移：`MaC_to_C=1`，`MaC_to_W=1`。
- 提示覆盖：2/2。
- 连续前缀复核输出：6。
- 最终解析失败：0/2。

这只是远端运行冒烟。它证明连续前缀生成路径可运行并能写出记录，不作为方法质量证据。

## 预期输出

- `math500-qwen25-7b-instruct-mca-soft-prefix-cue-all/records.jsonl`
- `math500-qwen25-7b-instruct-mca-soft-prefix-cue-all/summary.json`
- `math500-qwen25-7b-instruct-mca-soft-prefix-cue-all/summary.md`
- `run_remote.nohup.log`

## 边界

这只是运行冒烟，不作为方法质量证据。
