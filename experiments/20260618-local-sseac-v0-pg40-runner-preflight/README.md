# SSEAC-v0 PG40 Runner Preflight

日期：2026-06-18

## 目的

这次本地 preflight 补齐 `PG40` 上的 `ours_sseac_v0` 模型入口：`run_sseac_v0_pg40_openai_compatible.py`。它负责把 SSEAC packet 渲染成 openai-compatible chat prompt，并要求模型直接输出 `candidate_units`、`option_states`、`proposed_rejections` 和 `final_decision`。

本记录没有调用模型，也不形成方法结果。它验证 runner、prompt 边界和全量 prompt materialization 是否能进入下一步小样本模型 run。

## Preflight Contract

```text
purpose:
  为 PG40 SSEAC-v0 补模型预测入口，让模型直接提出 admission candidate units。

unit:
  PerspectiveGap tight-budget 40-row slice 中的一个 SSEAC packet row。

primary_contrast:
  未来模型输出经 SSEAC compiler 后，与 utility_density_greedy、source_ledger_14b_compiled、oracle 比较。

secondary_contrasts:
  source_ledger_7b_compiled、eligible_cheapest、eligible_all。

success_signal:
  runner 能生成 40 行 prompt；prompt 不暴露 required_slots / acceptable_card_ids / expected_final_decision；脚本通过 py_compile；输出格式能供 compile_sseac_v0.py 使用。

failure_signal:
  prompt 暴露 oracle fields；runner 输出缺 packet_id/response；prompt 过长到第一轮小样本无法运行；模型输出 schema 与 compiler 不兼容。

invalidation_conditions:
  将 required_slots 或 acceptable_card_ids 喂给模型；使用了不同 PG40 packet；compiler/scorer 与 prediction packet_id 无法对齐；把 dry-run 当成方法效果。

expected artifacts:
  script: scripts/run_sseac_v0_pg40_openai_compatible.py
  packet: experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl
  dry_run_prompts: experiments/20260618-local-sseac-v0-pg40-runner-preflight/dry_run_prompts_full40.jsonl
```

## 命令

```powershell
python -m py_compile scripts/run_sseac_v0_pg40_openai_compatible.py scripts/compile_sseac_v0.py scripts/score_sseac_pg40_compiled.py
python scripts/run_sseac_v0_pg40_openai_compatible.py --packet experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl --dry-run-prompts-out experiments/20260618-local-sseac-v0-pg40-runner-preflight/dry_run_prompts_full40.jsonl
Select-String -Path experiments/20260618-local-sseac-v0-pg40-runner-preflight/dry_run_prompts_full40.jsonl -Pattern 'required_slots|acceptable_card_ids|slot_id|expected_final_decision'
```

## 结果

`py_compile` 通过。

全量 dry-run prompt 生成结果：

```json
{
  "rows": 40,
  "dry_run_prompts_out": "experiments\\20260618-local-sseac-v0-pg40-runner-preflight\\dry_run_prompts_full40.jsonl"
}
```

prompt 规模：

```json
{
  "rows": 40,
  "prompt_chars_min": 6507,
  "prompt_chars_max": 16081,
  "prompt_chars_avg": 12249.75,
  "source_cards_min": 7,
  "source_cards_max": 13,
  "source_cards_avg": 10.25
}
```

oracle-field search 无命中：

```text
required_slots
acceptable_card_ids
slot_id
expected_final_decision
```

## 读法

runner 已经让 `PG40` 的 `ours_sseac_v0` 从“只有 adapter/compiler/scorer”推进到“可发起模型预测”。这一步仍属于 pipeline preflight，尚未回答方法是否超过 baseline。

prompt 给模型 `source_cards`、`recipient_scope`、`verification_state`、`evidence_type`、`cost` 和内容摘要；它不提供 `required_slots`、`acceptable_card_ids` 或 `expected_final_decision`。这保留了 source/scope-ledger 方法设定，同时避免 oracle slot 泄漏。

## 下一步

第一轮模型 run 只跑小样本，例如 `--limit 5`，并立刻接：

```powershell
python scripts/compile_sseac_v0.py --packet experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl --predictions <sseac_model_predictions.jsonl> --out <compiled.jsonl> --summary-out <compile_summary.json>
python scripts/score_sseac_pg40_compiled.py --pg-packet experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl --compiled <compiled.jsonl> --out <scores.jsonl> --summary-out <summary.md>
```

第一轮只看 schema adherence、budget rejection、forced commitment 和具体 case，不把小样本数值写成主表结论。
