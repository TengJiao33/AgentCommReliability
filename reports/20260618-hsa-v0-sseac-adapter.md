# HSA-v0 SSEAC Adapter Smoke

## 核心判断

`HSA-v0` 现在有了第一版可评分 SSEAC packet。它把三条 HiddenBench-derived fact-unit draft 转成 `source_cards`、`required_slots` 和 `expected_final_decision`，并跑通 oracle / shared-only / all-scoped 三个透明条件。

这一步仍是本地 adapter smoke。它支持下一步小样本模型 run，但还不能提供方法效果结论。

## 做了什么

新增脚本：

- `scripts/build_hsa_v0_sseac_packet.py`
- `scripts/score_hsa_v0_compiled.py`

生成 artifact：

- `experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl`
- `experiments/20260618-local-hsa-v0-sseac-adapter/predictions_*.jsonl`
- `experiments/20260618-local-hsa-v0-sseac-adapter/compiled_*.jsonl`
- `experiments/20260618-local-hsa-v0-sseac-adapter/scores_*.jsonl`

packet 当前有 `9` 行：`3` 个 base rows 和 `6` 个同文本 source/scope/verification perturbation rows。

## 结果

| Condition | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `oracle_admissible_facts` | 9/9 | 1.0000 | 1.0000 | 0.8333 | 0 | 0.0000 |
| `shared_only_verified` | 6/9 | 0.0000 | 1.0000 | 0.1759 | 24 | 0.3333 |
| `all_scoped_verified` | 9/9 | 1.0000 | 1.0000 | 0.8333 | 24 | 0.0000 |

## 解释

`oracle_admissible_facts` 9/9 说明 packet、compiler、scorer 的格式闭环成立。base rows 可由 admissible facts 支持 gold answer；perturbation rows 会因关键事实 unverified、quarantined 或缺 final_decider scope 而落到 `insufficient_evidence`。

`shared_only_verified` 的 base strict 为 0/3，说明 HSA-v0 继承了 HiddenBench 的通信必要性：只看共享事实无法支持正确决策。它在 perturbation rows 上达到 6/6，因为这些行的 gold decision 是证据不足。

`all_scoped_verified` 达到 9/9，同时产生 `24` 张 extra final cards。这个结果提醒我们：HSA-v0 的主表必须同时看 answer strict 和 evidence discipline。若一个 baseline 通过过度准入拿到正确答案，它仍然会在 extra cards / over-admission 指标上暴露问题。

## 边界

当前 HSA-v0 只有三条 HiddenBench draft，来自已有手工草稿。它还没有覆盖 seed_shortlist 里的 `HB31`，也没有接模型 prompt runner。

这个版本的 slots 仍有人工设计痕迹。它适合做机制压力和 prompt preflight，暂时不适合写成外部 benchmark claim。

## 下一步

下一步应补 `run_hsa_v0_sseac_openai_compatible.py`，让模型在看不到 `gold_answer`、`required_slots`、`oracle_unit_ids` 的情况下输出 `candidate_units`。

第一轮模型 run 建议只跑 3-5 行。成功信号应同时包含 schema 稳定、slot recall 合理、perturbation rows 能 abstain，以及 extra final cards 低于 `all_scoped_verified`；answer strict 只作为其中一个指标。
