# MCA-P running diagnostic

日期：2026-07-06

## 对象

远端运行：

```text
A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-soft-prefix-standard-madmm-aligned-qwen25-7b-full/
```

进程：

```text
PID 1135755
timeout parent 1135754
launcher 1135742
GPU 6
```

## 诊断问题

该 MCA-P full run 启动后长时间没有 `records.jsonl`、`summary.json` 或日志进度，是否说明运行已经挂死或实验设置有问题？

## 只读检查

`2026-07-06T12:07+08:00` 左右观察：

- 进程状态：`R (running)`。
- 墙钟时间：约 2.5 小时。
- CPU：主线程约 99.8%。
- GPU 6：约 31GB 显存，SM 利用率约 90%-96%。
- stdout/stderr：都指向该 run 的 `run_remote.nohup.log`。
- 输出目录：只有 `run_remote.sh`、`launcher.pid`、`run_remote.nohup.log`；无 `records.jsonl` 或 `summary.json`。
- `run_remote.nohup.log` 最近内容停在模型 checkpoint 加载完成。

## 代码路径判断

当前远端 `scripts/run_mca_soft_prefix.py` 在写 records 前会顺序完成：

1. initial answer generation；
2. cue extraction generation；
3. soft-prefix receiver generation；
4. records/summary 写入。

旧版本没有阶段进度打印，也不会在 generation 中途写中间文件。因此“日志和文件长时间不变”不能单独证明挂死。

## 发现的问题

执行层面：

- 没有看到僵尸、sleep-only、IO wait 或 GPU 空转迹象；GPU 和主线程都在持续计算。
- 因此当前证据更像“还在 transformers generation 阶段”，不是硬挂死。

实验/工程层面：

- 该 run 用 transformers backend 跑 full MATH500，而不是 vLLM；1500 个 initial prompts 每个 `max_new_tokens=4096`，随后还有 cue 和 receiver generation，耗时可能显著长于 vLLM 基线。
- 该 run 没有 `--input-records`，因此不是复用 Standard MAD 已归档 initial outputs，而是重新采样 standard-mad prompt。它只能称为 prompt/config aligned，不能称为 same-initial-pool aligned。
- 旧 MCA-P run 也出现过“加载后无日志、无 summary”的模式，说明这是可观测性/运行设计缺陷的重复。

## 已做修正

本地 `scripts/run_mca_soft_prefix.py` 已加入进度日志：

- run start；
- loaded rows；
- model loaded；
- initial answers completed x/y；
- cue extraction completed x/y；
- soft-prefix resolve completed x/y；
- records written x/y；
- run complete。

该修正不影响已经在远端运行的 PID 1135755，只对后续重启有效。

本地验证：

```text
python -m py_compile scripts/run_mca_soft_prefix.py scripts/mca_hidden_channel_runner.py
python -m unittest discover -s tests -p "test_*.py"
46 tests passed
```

## 建议

若目标是保留计算尝试，可以继续等到 18h timeout 或自然完成；但该结果即使完成，也应标为 diagnostic，而不是强横向 claim。

若目标是得到可复核的 MCA-P 主结果，建议停止当前 run，等空 GPU 后用更新后的 progress runner 重启，并优先传入 Standard MAD `records.jsonl` 作为 `--input-records`，使对照变成 same-initial-pool。

