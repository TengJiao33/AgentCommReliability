# MCA-P MATH500 full

## 目的

运行 MCA-P 连续前缀版完整 MATH-500 诊断，检验“不把提示文字给复核者看，而把过滤后的不含答案提示转成连续前缀”是否仍能影响最终答案。

## 设计

- 任务：`math500/test`，完整 500 题。
- 单位：一道 MATH-500 题。
- 模型：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`。
- 方法：`scripts/run_mca_soft_prefix.py`。
- 初始输出来源：复用 `20260705-a8002-math500-cpac-dcac-qwen25-7b-full` 的 500 题、3 个初始智能体输出。
- 前缀来源：过滤后的不含答案提示。
- 前缀长度：32。
- 前缀填充：均值填充。
- 智能体数：3。
- 复核者数：3。
- 候选池状态范围：`all`。
- 主要对照：同一批初始多数正确率 vs MCA-P 最终正确率。
- 主要读数：恢复、伤害、提示覆盖率、前缀复核覆盖率、最终解析失败率。

## 实验门禁

这次运行是完整集合诊断，不直接作为最终方法结论。它可以回答：同一批不含答案提示通过连续前缀通道传入时，是否还保留 MCA-T 文本通道中的一部分恢复信号。

支持信号：最终正确率高于同一批初始多数，且错误初始多数恢复比例高于正确初始多数伤害比例。

削弱信号：最终正确率不高于初始多数，或伤害比例接近/超过恢复比例。

失效条件：连续前缀生成路径崩溃、输出目录碰撞、输入记录不是 500 行、GPU 绑定错误、远端环境缺少 `transformers`/`torch`、最终解析失败率异常、同一输出目录被多个进程同时写入。

## 机器

- 主机：`A800_2`。
- 远端工作目录：`/data/xuhaoming/yfy/research_workspace`。
- Python 环境：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`。
- GPU：`1`。

## 启动

见 `run_remote.sh`。

## 状态

`RUNNING_GPU1`。

`2026-07-05T19:23:20+08:00` 启动完整运行：

- 远端启动器 PID：`2885572`。
- 外层超时保护进程：`2885611`。
- 实际推理进程：`2885612`。
- GPU：`1`。
- 复查时 GPU1 占用约 `17821 MiB`，利用率约 `95%`。
- 冒烟运行 `20260705-a8002-math500-mca-soft-prefix-qwen25-7b-l2` 已完成，确认连续前缀路径能在远端模型上跑通。

## 预期输出

- `math500-qwen25-7b-instruct-mca-soft-prefix-cue-all/records.jsonl`
- `math500-qwen25-7b-instruct-mca-soft-prefix-cue-all/summary.json`
- `math500-qwen25-7b-instruct-mca-soft-prefix-cue-all/summary.md`
- `run_remote.nohup.log`

## 边界

MCA-P 第一版仍然用提示文本的词嵌入构造连续前缀，因此它是“非显式文字通道”诊断，不等于已经证明内部隐藏状态通信。真正的内部状态版本需要后续 MCA-KV 或隐藏状态前缀实验。
