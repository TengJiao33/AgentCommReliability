# MCA-KV / MCA-S 实现记录

日期：2026-07-06

## 目的

把 `active/README.md` 中已经命名但尚未源码化的两个 MCA 版本落成可执行 runner：

```text
MCA-KV: 传 sender 真实解题过程中的 past_key_values
MCA-S: 传 sender 真实解题过程中的 residual activation steering vector
```

2026-07-06 之后，通信对象改成 sender 的真实解题状态，不再用 cue-derived text state。

## 文献依据

### CIPHER / embedding debate

自然语言采样会压缩模型在词表上的 belief。embedding / hidden 表示可以作为非文本通信介质。

链接：

```text
https://arxiv.org/abs/2310.06272
```

### Activation Addition / activation engineering

用 forward activation 构造 steering vector，在推理时注入 residual stream。

链接：

```text
https://arxiv.org/abs/2308.10248
```

### EquiMem

共享记忆和隐藏状态更新需要校准和 trust discount。

链接：

```text
https://arxiv.org/abs/2605.09278
```

### KG-CFR

把 private planning buffer 和 public speech 分层。MCA-KV/S 沿用这个分层，避免把 cue 文本直接放进 receiver prompt。

链接：

```text
https://arxiv.org/abs/2606.10475
```

## 新增源码

```text
scripts/mca_hidden_channel_runner.py
scripts/run_mca_kv_cache.py
scripts/run_mca_activation_steering.py
tests/test_mca_hidden_channels.py
```

## 共同设计

- 不再把 text-only `records.jsonl` 当成真实 hidden-state 来源；
- 每题按 row 流式执行：生成 sender、捕获真实状态、传给 receiver、立即写出 record；
- 复用当前 MATH evaluator、majority vote、transition label 和 summary 口径；
- receiver prompt 不包含 sender text，只提示可能存在不可见 hidden channel；
- `--channel-mode none` 提供 no-channel control。

## MCA-KV

```text
sender 解题 prompt + generated tokens 的真实 past_key_values 传给 receiver
```

这个通道可能包含 sender 的 reasoning / answer 信息，属于强 hidden-state transfer，不是 answer-free cue。

summary protocol：

```text
mca-kv-cache
```

## MCA-S

```text
在 sender 真实生成过程中用 hook 捕获指定 transformer layer 的 residual input activation；
默认取 sender pass 中捕获向量的均值作为 steering vector；
receiver 生成时在同一层把 vector 注入当前 token 的 residual stream。
```

summary protocol：

```text
mca-activation-steering
```

## 本地验证

```text
python compile: pass
run_mca_kv_cache.py --help: pass
run_mca_activation_steering.py --help: pass
python -m unittest discover -s tests -p "test_*.py": 47 tests passed
```

`mca_hidden_channel_runner.py` 已加入可见进度日志：

```text
[mca-hidden] row ...
[mca-hidden] sender generation ...
[mca-hidden] receiver generation ...
[mca-hidden] records written ...
```

## GPU Smoke

### MCA-KV smoke

```text
machine = A800_2
gpu = 6
run = /data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-smoke-mca-kv-live-state-qwen25-7b/
rows = 2
elapsed = 93.0s
status = records and summary written
```

这个 smoke 只检查可运行性。

### MCA-S first smoke

```text
machine = A800_2
gpu = 6
run = /data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-smoke-mca-s-live-state-qwen25-7b/
failure = CUDA OOM during row 2 receiver generation
```

修正：

```text
receiver manual generation runs under torch.inference_mode()
MCA-S sender state no longer retains unused sender KV caches
```

### MCA-S rerun

```text
machine = A800_2
gpu = 6
run = /data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-smoke-mca-s-live-state-qwen25-7b-rerun1/
rows = 2
elapsed = 102.1s
status = records and summary written
```

行为记录：

```text
当前 scale/layer 设置不能直接扩成完整实验；
两个 smoke rows 都被改变；
出现 `final answer only` 被解析成答案的格式污染。
```

## 最小 smoke 命令

MCA-KV：

```bash
python scripts/run_mca_kv_cache.py --work-dir /data/xuhaoming/yfy/research_workspace --run-id 20260706-a8002-smoke-mca-kv-live-state --benchmark math500 --split test --model-key qwen25-7b-instruct --model-path /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct --initial-prompt-style standard-mad --pool-state-scope all --limit 2 --max-tokens 512 --resolve-max-tokens 512 --max-model-len 4096 --dtype bfloat16 --channel-mode state
```

MCA-S：

```bash
python scripts/run_mca_activation_steering.py --work-dir /data/xuhaoming/yfy/research_workspace --run-id 20260706-a8002-smoke-mca-s-live-state --benchmark math500 --split test --model-key qwen25-7b-instruct --model-path /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct --initial-prompt-style standard-mad --pool-state-scope all --limit 2 --max-tokens 512 --resolve-max-tokens 512 --max-model-len 4096 --dtype bfloat16 --channel-mode state --steering-layer 16 --steering-scale 1.0
```

smoke 只检查能否完整写出 `records.jsonl` 和 `summary.json`，不解释准确率。
