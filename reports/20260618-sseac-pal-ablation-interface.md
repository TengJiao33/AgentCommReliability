# SSEAC PAL 式 ablation 接口补齐

Snapshot date: `2026-06-18`.

## 核心判断

当前 SSEAC smoke queue 已经能产生 PAL 式关键对照：`structured_no_compiler` 与 `ours_sseac_v0`。这让下一次 PG40 / HSA 小样本真跑可以直接回答一个方法论文需要的问题：收益来自模型输出 schema，还是来自 deterministic compiler / sufficiency gate。

## 做了什么

`scripts/compile_sseac_v0.py` 新增 `--mode`：

| Mode | Condition | 含义 |
| --- | --- | --- |
| `compiler` | `ours_sseac_v0` | 原有路径：执行 source/scope/verification/budget hard constraints，再做 sufficiency gate。 |
| `model_only` | `structured_no_compiler` | 新增路径：把模型 candidate units 直接作为 admitted units，保留模型 final_decision，用 gate 只做诊断。 |

`scripts/run_sseac_smoke_queue_openai_compatible.ps1` 也已更新。每次 PG40/HSA 预测后，队列会先编译并评分 `structured_no_compiler`，再编译并评分默认 `compiler` 路径。

新增 paired-delta 汇总入口：

```text
scripts/summarize_sseac_paired_delta.py
```

它读取 `scores_structured_no_compiler_limit<N>.jsonl` 和 `scores_limit<N>.jsonl`，输出 `paired_delta_limit<N>.json/md`。这一步把 `compiled - structured_no_compiler` 直接变成 paper-facing 表格读数。

## 验证结果

语法检查通过：

```powershell
python -m py_compile scripts\compile_sseac_v0.py scripts\run_sseac_v0_pg40_openai_compatible.py scripts\run_hsa_v0_sseac_openai_compatible.py scripts\score_sseac_pg40_compiled.py scripts\score_hsa_v0_compiled.py
```

本地 compiler smoke 的 `model_only` mode 可运行：

```text
rows: 2
ok_rows: 2
error_rows: 0
forced_commitment_rate: 1.0
downstream_ok: 0.0
```

这个 smoke 显示去掉 compiler/gate 后，模型 final decision 会暴露 forced commitment，说明这个 ablation 有辨识力。

PG40 现有 source-ledger 14B 预测也能走 `model_only` mode 并被 scorer 接收：

```text
strict_pass_count: 11/40
required_coverage: 0.7515
boundary_precision: 0.9270
budget_pass: 1.0000
utility_ratio: 0.8707
```

这一路没有拉开差距，原因是该输入已经是 budget-compiled 形态的旧预测，适合作为兼容性检查，不能说明 no-compiler ablation 在真实 SSEAC 模型输出上无效。

队列 dry-run 已确认会产出四套核心 artifacts：

```text
pg40/structured_no_compiler_limit5.jsonl
pg40/compiled_limit5.jsonl
hsa_v0/structured_no_compiler_limit3.jsonl
hsa_v0/compiled_limit3.jsonl
pg40/paired_delta_limit5.json/md
hsa_v0/paired_delta_limit3.json/md
```

paired-delta 脚本 smoke 已通过。PG40 使用 source-ledger 14B 的 no-compiler/compiled 兼容性文件配对，得到 `40` paired rows；HSA 使用 oracle score 自配对，得到 `9` paired rows。两者都是零 delta smoke，只验证配对、汇总和 markdown/json 输出链路。

## 对论文故事的影响

这次接口补齐让我们更像 PAL 模板。后续主表可以直接放：

| 行 | 作用 |
| --- | --- |
| direct / free exchange | 常规基线 |
| source-ledger | 结构化文本基线 |
| structured_no_compiler | 模型自己守 admission 约束 |
| ours_sseac_v0 | 模型提候选，compiler 执行约束 |
| transparent heuristic | 强可复现 baseline |
| oracle | 上界 |

如果 `ours_sseac_v0` 稳定优于 `structured_no_compiler`，我们可以把贡献写成 executable admission decomposition。如果两者接近，说明 compiler 还没有带来足够方法增量，下一步应回到 unit proposal 和 task construction。

## 下一步

1. 已运行 PG40 limit5 三轮和 HSA full9，并更新 PG40/HSA 数字表。
2. 继续读 `structured_no_compiler` 与 `compiled` 的 paired delta，最终 strict 只作为其中一个指标。
3. 下一步优先 HSA 候选证据召回；PG40 只在有新排序机制时重启。
