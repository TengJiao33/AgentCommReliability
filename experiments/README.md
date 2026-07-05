# Experiments

本目录保存当前 live workspace 的实验 run 记录、日志和结果文件。当前 MATH-500 横向比较只保留标准配置 run；非标准旧池实验已从当前 workspace 移除，避免污染结论。

## 最近 Run 索引

### 2026-07-05

- `20260705-a8002-math500-mca-soft-prefix-standard-qwen25-7b-full-4096/`
  - 状态：`RUNNING_GPU1`
  - 方法：MCA-P 连续前缀版，`scripts/run_mca_soft_prefix.py`
  - 配置：不复用旧 records，`initial_prompt_style=standard-mad`，主生成/cue/resolve 均为 `max_tokens=4096`，`max_model_len=24064`，temperature/top-p 均为 1.0
  - 读数：远端推理进程 PID `3644710`，GPU1 正在运行
  - 主要 caveat：完成后必须先检查 initial majority 是否回到 362/364 附近；若没有，该 run 只能作为 prompt/backend mismatch 诊断

- `20260705-a8002-math500-standard-mad-qwen25-7b-full-4096/`
  - 状态：`COMPLETED`
  - 方法：标准 MAD，`scripts/run_mad_mm.py`，`prune_strategy=naive`
  - 配置：`max_tokens=4096`，`max_model_len=24064`，temperature/top-p 均为 1.0
  - 读数：initial majority 364/500，standard MAD final 378/500，final parse fail 0
  - 主要 caveat：这是当前 4096 输出预算主口径下的标准 MAD 基线

### 2026-07-04

- `20260704-a8002-math500-mad-mm-qwen25-7b-full/`
  - 状态：`COMPLETED`
  - 方法：MAD-MM/MAD-M2 local reproduction，MATH-500 full
  - 读数：`naive` 375/500，`subjective` 369/500，`objective` 360/500
  - 主要 caveat：evaluator 在 2026-07-05 被修复后从 raw records 重算；仍是轻量 local evaluator，不是官方 MATH verifier

- `20260704-a8002-aime24-25-mad-mm-qwen25-7b-full/`
  - 状态：`COMPLETED`
  - 方法：MAD-MM/MAD-M2 local reproduction，AIME24/25 full splits
  - 读数：combined naive 5/60，subjective 5/60，objective 4/60
  - 主要 caveat：样本只有 60 题，适合作为集成诊断，不适合作广泛负结论

- `20260704-a8002-aime24-25-basic-mad-full/`
  - 状态：`COMPLETED`
  - 方法：basic MAD AIME24/25 baseline

- `20260704-a8002-aime24-25-cot-sc-full/`
  - 状态：`COMPLETED`
  - 方法：CoT self-consistency AIME24/25 baseline

- `20260704-a8002-gsm8k-basic-mad-full/`
  - 状态：`COMPLETED`
  - 方法：basic MAD GSM8K baseline

## 读法 Caveat

实验记录里的数字应优先和对应 run README、summary.json、records.jsonl 一起读。不同 runner 之间的 prompt、temperature、rounds、aggregation 和 evaluator 口径可能不同；除非同一报告明确声明 paired contrast，否则不要直接把绝对准确率当作方法优劣证明。

旧非标准初始池记录已从当前 workspace 移除。需要审计时从 Git 历史取证，不进入当前标准配置横向表。

## Templates

- `experiments/_templates/run_README.md`
- `experiments/_templates/manifest.json`
