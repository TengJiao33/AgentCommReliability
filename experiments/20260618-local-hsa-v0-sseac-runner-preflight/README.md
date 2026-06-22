# HSA-v0 SSEAC Runner Preflight

日期：2026-06-18

## 目的

这次本地 preflight 补齐 `HSA-v0` 的 openai-compatible 模型入口：`run_hsa_v0_sseac_openai_compatible.py`。它把 HiddenBench-derived HSA packet 渲染成 prompt，要求模型输出 SSEAC `candidate_units`，再交给 `compile_sseac_v0.py` 和 `score_hsa_v0_compiled.py`。

本记录没有调用模型，只验证 prompt materialization、runner 编译和 evaluator-only 字段泄漏。

## Preflight Contract

```text
purpose:
  为 HSA-v0 补模型预测入口，让模型在看不到 gold / oracle slots 的情况下提出 admissible evidence units。

unit:
  一个 HSA-v0 SSEAC packet row。当前为 9 rows：3 base + 6 perturbation。

primary contrast:
  后续模型输出 vs oracle_admissible_facts / shared_only_verified / all_scoped_verified。

success_signal:
  runner 通过 py_compile；9 行 prompt 成功生成；prompt 不暴露 required_slots、gold_answer、oracle_unit_ids、expected_final_decision。

failure_signal:
  prompt 泄漏 evaluator-only 字段；模型入口缺 packet_id/response；prompt 长到无法小样本运行。

invalidation_conditions:
  把 hsa_meta、required_slots、expected_final_decision、gold_answer、oracle_unit_ids 或 downstream_scoring_obligations 渲染给模型；把 dry-run 当成方法效果。
```

## 命令

```powershell
python -m py_compile scripts/run_hsa_v0_sseac_openai_compatible.py scripts/build_hsa_v0_sseac_packet.py scripts/score_hsa_v0_compiled.py scripts/compile_sseac_v0.py
python scripts/run_hsa_v0_sseac_openai_compatible.py --packet experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl --dry-run-prompts-out experiments/20260618-local-hsa-v0-sseac-runner-preflight/dry_run_prompts_full9.jsonl
Select-String -Path experiments/20260618-local-hsa-v0-sseac-runner-preflight/dry_run_prompts_full9.jsonl -Pattern 'required_slots|acceptable_card_ids|slot_id|expected_final_decision|gold_answer|oracle_unit_ids|downstream_scoring_obligations'
```

## 结果

`py_compile` 通过。

全量 dry-run prompt 生成成功：

```json
{
  "rows": 9,
  "dry_run_prompts_out": "experiments\\20260618-local-hsa-v0-sseac-runner-preflight\\dry_run_prompts_full9.jsonl"
}
```

prompt 规模：

```json
{
  "rows": 9,
  "conditions": {
    "base": 3,
    "perturbation": 6
  },
  "prompt_chars_min": 5499,
  "prompt_chars_max": 5994,
  "prompt_chars_avg": 5691.56,
  "source_cards_min": 7,
  "source_cards_max": 8,
  "source_cards_avg": 7.67
}
```

oracle-field search 无命中：

```text
required_slots
acceptable_card_ids
slot_id
expected_final_decision
gold_answer
oracle_unit_ids
downstream_scoring_obligations
```

## 读法

HSA-v0 的下一步已经可以直接小样本跑模型。prompt 给模型 answer options、source cards、recipient scope、verification state、evidence type 和 cost；gold answer、required slots 和 oracle units 都留在 evaluator 侧。

这个 runner 的第一轮用途是查 schema adherence、slot recall、perturbation abstention 和 extra final cards。answer strict 只能作为其中一个指标。

## 下一步

如果有 openai-compatible endpoint，先跑 `--limit 3`：

```powershell
python scripts/run_hsa_v0_sseac_openai_compatible.py --packet experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl --base-url <base-url> --model <model> --out experiments/20260618-a8002-hsa-v0-sseac-smoke/predictions.jsonl --limit 3
```

随后接：

```powershell
python scripts/compile_sseac_v0.py --packet experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl --predictions <predictions.jsonl> --out <compiled.jsonl> --summary-out <compile_summary.json>
python scripts/score_hsa_v0_compiled.py --packet experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl --compiled <compiled.jsonl> --out <scores.jsonl> --summary-out <summary.md>
```
