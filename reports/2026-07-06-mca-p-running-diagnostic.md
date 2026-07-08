# MCA-P 运行诊断

日期：2026-07-06

## 对象

远程运行：

```text
A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-soft-prefix-standard-madmm-aligned-qwen25-7b-full/
```

进程：

```text
PID = 1135755
timeout parent = 1135754
launcher = 1135742
GPU = 6
```

## 诊断问题

MCA-P full run 启动后长时间没有：

```text
records.jsonl
summary.json
进度日志
```

需要判断它是挂死，还是仍在生成阶段。

## 只读检查

观察时间：`2026-07-06T12:07+08:00` 左右。

```text
process state = R (running)
wall time ≈ 2.5h
main thread CPU ≈ 99.8%
GPU6 memory ≈ 31GB
GPU6 SM utilization ≈ 90%-96%
```

输出目录只有：

```text
run_remote.sh
launcher.pid
run_remote.nohup.log
```

没有：

```text
records.jsonl
summary.json
```

`run_remote.nohup.log` 最近内容停在模型 checkpoint 加载完成。

## 代码路径判断

当时远程 `scripts/run_mca_soft_prefix.py` 在写 records 前会顺序完成：

1. initial answer generation；
2. cue extraction generation；
3. soft-prefix receiver generation；
4. records / summary 写入。

旧版本没有阶段进度打印，也不会在 generation 中途写中间文件。

## 发现

执行层面：

- 没看到僵尸、sleep-only、IO wait 或 GPU 空转；
- GPU 和主线程都在持续计算；

实验层面：

- 该 run 用 transformers backend 跑 full MATH500，不是 vLLM；
- 500 个 initial prompts 每个 `max_new_tokens=4096`；
- 后面还有 cue generation 和 receiver generation；

对照口径：

- 该 run 没有 `--input-records`；
- 它重新采样 standard-mad prompt；
- 因此只能叫 prompt/config aligned，不能叫 same-initial-pool aligned。

## 已做修正

本地 `scripts/run_mca_soft_prefix.py` 加入进度日志：

```text
run start
loaded rows
model loaded
initial answers completed x/y
cue extraction completed x/y
soft-prefix resolve completed x/y
records written x/y
run complete
```

这个修正不影响已经在远程运行的 PID 1135755，只对后续重启有效。

本地验证：

```text
python -m py_compile scripts/run_mca_soft_prefix.py scripts/mca_hidden_channel_runner.py
python -m unittest discover -s tests -p "test_*.py"
46 tests passed
```

## 建议

如果目标是保留这次计算，可以继续等到 18h timeout 或自然完成。

如果目标是得到可复核 MCA-P 主结果，建议停止当前 run，等空 GPU 后用带进度日志的新 runner 重启，并优先传入 Standard MAD `records.jsonl` 作为 `--input-records`，把对照口径改成 same-initial-pool。
