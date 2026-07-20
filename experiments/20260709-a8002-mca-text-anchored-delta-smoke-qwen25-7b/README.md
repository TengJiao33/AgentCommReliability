# MCA Text-Anchored Delta Smoke

日期：2026-07-09

目的：验证 `mca-text-anchored-delta-v0` 能否在远端模型上完成最小首跑，并检查短文本锚点、sender work-span hidden delta、anchor-position prefill 注入和各对照条件是否能产生完整记录。

核心约束：

```text
发送方生成结构化 unit；
接收方只看到短 anchor，不看到 sender work；
hidden delta 来自 sender <work> span；
latent 只在 receiver prompt 中对应 anchor token 位置注入；
不使用 peer past_key_values；
对照包含 anchor_only、raw_delta、anchor_delta、anchor_random_same_norm、anchor_other_question_delta；
最多使用一张 GPU。
```

默认首跑：

```text
split = mca_disagreement_v1
limit = 5
layers = 22
conditions = anchor_only,raw_delta,anchor_delta,anchor_random_same_norm,anchor_other_question_delta
max_anchors = 4
steering_scale = 0.03
message_max_norm = 1.0
```

## 问题

这次运行只回答工程问题：新协议是否能稳定生成 anchor、提取非空 payload，并在同一输出目录下写出 `records.jsonl`、`summary.json`、`summary.md`。如果成功，再决定是否扩大到 50 题。

## 范围

- 任务：MATH-500 disagreement split 小样本诊断。
- 方法或干预：Text-Anchored Hidden Delta。
- 基线：无通信 baseline、纯 anchor、raw delta、随机同范数、无关题 delta。
- 模型：Qwen2.5-7B-Instruct。
- 数据集或输入来源：`math500/mca_disagreement_v1`。
- 样本数：5。

## 机器

- 历史运行主机：A800_2 / `10-116-90-20`。
- 历史 GPU：GPU 1；启动前 GPU 1 和 GPU 4 均为 81149 MiB free。
- 历史工作目录：`/data/xuhaoming/yfy/research_workspace`。
- 重跑默认目标（2026-07-12）：逻辑远端 `X_LANCE_HPC`，账号 `fyy05`；物理超算、GPU 节点、项目根目录和运行参数待设备委员确认及首登实测。

## 代码

- 仓库或脚本：`scripts/run_mca_text_anchored_delta.py`。
- 提交：`36278ef`。
- 本地改动：新增 text-anchored delta runner 和对应轻量测试；远端只同步当前 runner 文件。

## 环境

- Python：`/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`，Python 3.10.20。
- 关键包：沿用项目远端环境。
- 后端：Hugging Face Transformers，bfloat16。

## 命令

```bash
bash experiments/20260709-a8002-mca-text-anchored-delta-smoke-qwen25-7b/run_remote_smoke.sh
```

## 输出

- 远端目录：`/data/xuhaoming/yfy/research_workspace/experiments/20260709-a8002-mca-text-anchored-delta-smoke-qwen25-7b/math500-qwen25-7b-instruct-mca-text-anchored-delta`
- 日志：`/data/xuhaoming/yfy/research_workspace/experiments/20260709-a8002-mca-text-anchored-delta-smoke-qwen25-7b/run_remote_smoke.nohup.log`
- 原始结果：等待运行生成 `records.jsonl`。
- 摘要：等待运行生成 `summary.json` 和 `summary.md`。

## 结果

- 状态：STOPPED_BY_RESOURCE
- 远端 PID：`1616298`
- 启动时间：2026-07-09T16:32:43+08:00
- 停止情况：运行在第 5 题 `anchor_only` 第 1 个 agent 后输出 `Terminated`，未生成 `summary.json`。
- 终止诊断：日志没有 Python traceback、CUDA OOM、`Killed` 或正常结束标记；`journalctl --user` 在 2026-07-09 17:26:29 记录到一次 `xuhaoming` SSH 连接断开，时间接近 `Terminated`；可访问系统日志中未见 OOM / NVIDIA Xid 记录。当前只能判断为外部 SIGTERM 风格终止，不能确定具体发起者。
- 已写结果：`records.jsonl` 4 行。
- 主指标：部分结果为 baseline `1/4`，`anchor_delta 2/4`，`anchor_only 1/4`，`anchor_other_question_delta 2/4`，`anchor_random_same_norm 2/4`，`raw_delta 2/4`。该读数不是完整 smoke 结果。
- 墙钟时间：约 53 分钟后停止。
- 令牌或计算成本：未汇总。
- 迁移状态（2026-07-12）：旧 A800 公钥已失效；新集群 Wiki 登录成功，但 SSH 尚未进入认证。该 run 保留 `STOPPED_BY_RESOURCE` 历史状态，完整 5 题 smoke 仍待在新默认集群重跑。

## 清理

- 保留：run README、启动脚本、日志、summary、records。
- 删除：无。
