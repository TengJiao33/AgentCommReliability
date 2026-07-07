# MCA-T audit standard MATH500 full 4096 实验记录

## 目的

在当前标准 MATH-500 对比口径下运行保守的 text-based MCA audit。

该 run 使用 Standard MAD prompt family 重新采样初始答案，然后抽取不含答案的 cues，只允许通过 cue-derived audit certificates 改变答案。

## 设计

- 任务：`math500/test`，完整 500 题。
- 模型：`/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`。
- 方法：`scripts/run_mca_text_audit.py`。
- 协议：`mca-text-audit`。
- 初始 prompt style：`standard-mad`。
- 初始求解智能体：3 个独立样本。
- 复核者：3 个 audit reviewers。
- cue 数量：每条 source trace 2 个。
- 改变规则：需要 2 个 admissible change certificates。
- Pool-state 范围：`all`。
- 温度与 top-p：所有 generation temperature 为 `1.0`，top-p 为 `1.0`。
- 输出预算：initial、cue、audit 的 max tokens 均为 `4096`。
- 上下文预算：`max_model_len=24064`。

## 机器

- 主机：`A800_2`。
- 远端工作目录：`/data/xuhaoming/yfy/research_workspace`。
- Python 环境：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`。
- 计划 GPU：`7`。

## 启动

见 `run_remote.sh`。

## 状态

`NO_LOCAL_SUMMARY`。

第一次尝试在 GPU `0` 上启动，但 GPU 0 已有其他用户的常驻进程，因此手动停止。该次尝试没有产生有效 summary，部分日志归档为 `run_remote.stopped-gpu0-2322.log`。

重启后使用启动检查时为空的 GPU `7`。

- Launcher PID：`3867571`。
- Timeout PID：`3867606`。
- Python PID：`3867607`。
- 启动检查：evaluator smoke 与 audit aggregation smoke 通过；Qwen2.5-7B 以 `max_seq_len=24064` 加载；KV cache 初始化为 58001 个 GPU blocks；CUDA graph capture 完成。

本地目录没有 `summary.json` 或 `records.jsonl`。2026-07-06 远端另有 aligned MCA-T audit 完整结果：

```text
A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-text-audit-standard-madmm-aligned-qwen25-7b-full/
```

该 aligned run 的 summary 显示 initial majority 364/500，final 357/500；它是当前 MCA-T audit 的可读结果来源。

## 预期输出

- `math500-qwen25-7b-instruct-mca-text-audit-all/records.jsonl`
- `math500-qwen25-7b-instruct-mca-text-audit-all/summary.json`
- `math500-qwen25-7b-instruct-mca-text-audit-all/summary.md`
- `run_remote.nohup.log`
- `launcher.pid`
