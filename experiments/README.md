# Experiments

本目录保存当前 live workspace 的实验 run 记录、日志和结果文件。每个 claim-bearing 或 diagnostic run 应在自己的 `experiments/<run-id>/README.md` 中记录目的、设计、机器、输出、结果和 caveat。

## 最近 Run 索引

### 2026-07-05

- `20260705-a8002-math500-mca-soft-prefix-qwen25-7b-full/`
  - 状态：`RUNNING_GPU1`
  - 方法：MCA-P 连续前缀版，复用 CPAC 完整运行里的 500 题初始三路输出，`limit=0`
  - 读数：远端推理进程 PID `2885612`，GPU1 正在运行
  - 主要 caveat：这是提示词嵌入构造的连续前缀通道诊断，不等同于隐藏状态直接通信

- `20260705-a8002-math500-standard-mad-qwen25-7b-full-24064/`
  - 状态：`RUNNING_GPU4`
  - 方法：标准 MAD，`scripts/run_mad_mm.py`，`prune_strategy=naive`，24064 输出/上下文配置
  - 读数：远端推理进程 PID `3037230`，截至 2026-07-05T20:20+08:00 仍在运行，尚无本地 `summary.json`
  - 主要 caveat：这是新主实验矩阵的标准配置基线，完成前不能替代旧 MAD-MM 读数

- `20260705-a8002-math500-cpac-dcac-guard-v1-standard-qwen25-7b-full-24064/`
  - 状态：`RUNNING_GPU6`
  - 方法：CPAC+DCAC guard-v1，`scripts/run_cpac_dcac.py`，24064 输出/上下文配置
  - 读数：远端推理进程 PID `3087783`，截至 2026-07-05T20:20+08:00 仍在运行，尚无本地 `summary.json`
  - 主要 caveat：完成后才可和同配置标准 MAD 进入主比较

- `20260705-a8002-math500-mca-soft-prefix-qwen25-7b-l2/`
  - 状态：`COMPLETED`
  - 方法：MCA-P 远端运行冒烟，`limit=2`
  - 读数：初始多数 2/2，最终 1/2；连续前缀路径和结果写入已验证
  - 主要 caveat：2 题冒烟不是方法质量证据

- `20260705-a8002-math500-mca-text-audit-qwen25-7b-full/`
  - 状态：`COMPLETED`
  - 方法：MCA-T 保守审查版，复用 CPAC 完整运行里的 500 题初始三路输出，`limit=0`
  - 读数：same-run initial majority 320/500，MCA-T 审查版 final 330/500；`MaW_to_C=11`，`MaC_to_W=1`
  - 主要 caveat：这是固定初始候选池上的审查机制诊断，不是重新采样初始解的独立重复实验

- `20260705-a8002-math500-mca-text-qwen25-7b-l20/`
  - 状态：`COMPLETED`
  - 方法：MCA-T，answer-free text cue extraction + anonymous cue-only re-solve，`limit=20`
  - 读数：initial majority 14/20，MCA-T final 11/20；`MaW_to_C=1`，`MaC_to_W=4`
  - 主要 caveat：integration smoke，不是方法 claim；当前 prompt/filter 设置下 harm 明显高于 recovery

- `20260705-a8002-math500-cpac-dcac-qwen25-7b-full/`
  - 状态：`COMPLETED`
  - 方法：CPAC+DCAC，no-majority action 为 `listwise`，DCAC 至少 2 个 admissible flip certificates 才翻盘
  - 读数：same-run initial majority 320/500，CPAC+DCAC final 325/500，净增 5 题
  - 主要 caveat：净增来自 listwise 分支；DCAC 分支本身为负净值，当前不是方法 claim

- `20260705-a8002-math500-cpac-dcac-guard-v1-qwen25-7b-full/`
  - 状态：`COMPLETED`
  - 方法：CPAC+DCAC guard-v1，旧参数配置
  - 读数：same-run initial majority 320/500，guard-v1 final 332/500；`MaC_to_W` 从旧 CPAC+DCAC 的 10 降到 3
  - 主要 caveat：仍是旧参数体系诊断，不进入新主实验矩阵

- `20260705-a8002-math500-cqg-divergent-qwen25-7b-full/`
  - 状态：`COMPLETED`
  - 方法：CQG，`quarantine-mode=divergent`
  - 读数：记录内 same-run initial majority 320/500，CQG final 337/500，净增 17 题
  - 主要 caveat：valid appeal rate 35/189，机制增益暂不能归因于 appeal gate

- `20260705-a8002-math500-basic-mad-qwen25-7b-full/`
  - 状态：`COMPLETED`
  - 方法：basic MAD，3 agents，1 revision round
  - 读数：direct 347/500，MAD final majority 333/500
  - 主要 caveat：与 MAD-MM/CQG 的 prompt、temperature、rounds、context length 不同，不能直接做方法优劣证明

- `20260705-a8002-math500-cqg-smoke-qwen25-7b-l20/`
  - 状态：diagnostic smoke
  - 方法：CQG `never` / `divergent` smoke
  - 作用：验证 runner、appeal sentinel、XML placeholder 和 evaluator smoke；不是 benchmark-level method claim

- `20260705-a8002-math500-cqg-smoke-qwen25-7b-l20-v2/`
  - 状态：diagnostic smoke
  - 作用：修复 appeal sentinel 后的 CQG integration check

- `20260705-a8002-math500-cqg-smoke-qwen25-7b-l20-v3/`
  - 状态：diagnostic smoke
  - 作用：修复 XML placeholder 后的 CQG integration check；记录了一个 blind re-solve recovery 和一个 over-trigger harm case

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

当前 CQG full run 的记录内 summary 与当前工作树 evaluator 对少数 representation-risk 答案的重算存在差异。正式比较前需要统一 evaluator 版本并重写受影响 summary。

## Templates

- `experiments/_templates/run_README.md`
- `experiments/_templates/manifest.json`
