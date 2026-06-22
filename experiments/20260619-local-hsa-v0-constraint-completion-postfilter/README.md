# HSA-v0 Constraint Completion Postfilter

日期：2026-06-19

## 核心判断

这次本地诊断把 `constraint_recall` 的同一份模型输出固定住，只增加一个可审计后置补全规则：补入预测时可见、已验证、面向 `final_decider` 的阻断卡。结果从 compiler `8/9` 到 `9/9`，extra final cards 保持 `10`。

这说明剩余失败点确实是可见阻断卡漏召回。它暂时仍是诊断结果，因为规则只在 9 行小表上验证，且复用了已有模型输出。

## 输入

| 项 | 内容 |
| --- | --- |
| 来源运行 | `experiments/20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b/` |
| packet | `experiments/20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b/packet_limit0.jsonl` |
| 原始预测 | `experiments/20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b/predictions.jsonl` |
| 补全脚本 | `scripts/augment_hsa_predictions.py` |
| 策略 | `visible_verified_blocker_completion` |

## 补全规则

对每行预测：

1. 读取 `source_cards` 中预测时可见的字段。
2. 选择 `evidence_type == blocker`、`verification_state == verified`、且 `recipient_scope` 包含 `final_decider` 的卡片。
3. 若该卡尚未出现在面向 `final_decider` 的候选单元中，则追加一个单卡候选单元。
4. 追加单元优先级为 `9.5`，低于模型常用高优先级 `10.0`，预算、范围和验证约束仍交给原编译器执行。

补全摘要：

| 指标 | 值 |
| --- | ---: |
| prediction rows | `9` |
| rows with added units | `2` |
| added unit count | `2` |
| parse errors | `0` |

新增的两处都是 `hb01_hidden_2`：

| packet | card |
| --- | --- |
| `hiddenbench_evacuation_west_city__hb01_base_verified_role_scoped__hsa_v0` | `hb01_hidden_2` |
| `hiddenbench_evacuation_west_city__hb01_west_bridge_unverified__hsa_v0` | `hb01_hidden_2` |

## 命令

```powershell
python scripts\augment_hsa_predictions.py --packet experiments\20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b\packet_limit0.jsonl --predictions experiments\20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b\predictions.jsonl --out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\predictions_augmented.jsonl --summary-out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\augmentation_summary.json
python scripts\compile_sseac_v0.py --packet experiments\20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b\packet_limit0.jsonl --predictions experiments\20260619-local-hsa-v0-constraint-completion-postfilter\predictions_augmented.jsonl --mode compiler --out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\compiled_compiler.jsonl --summary-out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\compile_summary_compiler.json
python scripts\compile_sseac_v0.py --packet experiments\20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b\packet_limit0.jsonl --predictions experiments\20260619-local-hsa-v0-constraint-completion-postfilter\predictions_augmented.jsonl --mode model_only --out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\compiled_model_only.jsonl --summary-out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\compile_summary_model_only.json
python scripts\score_hsa_v0_compiled.py --packet experiments\20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b\packet_limit0.jsonl --compiled experiments\20260619-local-hsa-v0-constraint-completion-postfilter\compiled_compiler.jsonl --out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\scores_compiler.jsonl --summary-out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\summary_compiler.md
python scripts\score_hsa_v0_compiled.py --packet experiments\20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b\packet_limit0.jsonl --compiled experiments\20260619-local-hsa-v0-constraint-completion-postfilter\compiled_model_only.jsonl --out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\scores_model_only.jsonl --summary-out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\summary_model_only.md
python scripts\summarize_sseac_paired_delta.py --benchmark hsa --no-compiler-scores experiments\20260619-local-hsa-v0-constraint-completion-postfilter\scores_model_only.jsonl --compiled-scores experiments\20260619-local-hsa-v0-constraint-completion-postfilter\scores_compiler.jsonl --out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\paired_delta_full9.json --summary-out experiments\20260619-local-hsa-v0-constraint-completion-postfilter\paired_delta_full9.md
```

## 结果

| 条件 | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| augmented model-only | `5/9` | `1.0000` | `0.3333` | `0.9352` | `10` | `0.1111` |
| augmented compiler | `9/9` | `1.0000` | `1.0000` | `0.8333` | `10` | `0.4444` |

成对差分：

| 指标 | model-only | compiler | delta |
| --- | ---: | ---: | ---: |
| strict | `0.5556` | `1.0000` | `+0.4444` |
| slot recall | `0.9352` | `0.8333` | `-0.1019` |
| extra final cards | `1.1111` | `1.1111` | `0.0000` |
| forced commitment detected | `0.1111` | `0.4444` | `+0.3333` |

这里的 forced commitment detected 表示模型曾提出具体答案，但编译器在证据不足行中挡回了该承诺；在 HSA 扰动行里这是防错信号。

## 边界

- 这是本地后置补全诊断，没有新增模型生成。
- 补全规则只使用预测时可见字段，没有读取 `required_slots`、`expected_final_decision` 或评测义务字段。
- 样本只有 9 行，当前不能作为论文主结论。
- 下一步需要在更大 HiddenBench seed shortlist 上复核：该规则是否仍能补漏，并且不把无关阻断卡变成额外证据。
