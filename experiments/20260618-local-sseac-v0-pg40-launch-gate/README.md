# SSEAC-v0 PG40 Limit5 Launch Gate

日期：2026-06-18

## 目的

这次 launch gate 把 `PG40 true SSEAC prompt` 推到可执行边界。它物化 `limit 5` prompt，核对 oracle 字段泄漏、baseline 对照、runner 静态检查和 endpoint 状态。

本记录没有调用模型。当前结论是：runner 和 prompt 已准备好，模型执行受 openai-compatible endpoint 缺失限制。

## Preflight Contract

```text
purpose:
  在 PG40 tight-budget 上跑第一轮 SSEAC-v0 proposer 小样本前，确认 packet、prompt、baseline 和执行入口。

unit:
  PerspectiveGap tight-budget 40-row slice 中的一个 SSEAC packet row。

primary_contrast:
  future SSEAC model output vs utility_density_greedy_after_sseac_compiler。

secondary_contrasts:
  oracle_utility, source_ledger_14b_fullprompt_budget_compiled, source_ledger_7b_fullprompt_budget_compiled, eligible_all, eligible_cheapest。

success_signal:
  模型输出可解析 JSON；compiler error rows 为 0；scope/budget 由 compiler 稳定执行；limit5 至少出现若干合理 candidate priorities。

failure_signal:
  输出无法解析；candidate_units 缺失；大量 invented card ids / roles；compiled strict 和 utility 明显低于 source_ledger_14b 或只靠少发提高 precision。

invalidation_conditions:
  prompt 泄漏 required_slots / acceptable_card_ids / expected_final_decision / gold_answer / oracle_unit_ids；
  使用了不同 PG40 packet；
  predictions 与 packet_id 无法对齐；
  小样本结果被写成主表结论。
```

## 已完成检查

```powershell
python -m py_compile scripts\run_sseac_v0_pg40_openai_compatible.py scripts\compile_sseac_v0.py scripts\score_sseac_pg40_compiled.py
```

结果：通过。

```powershell
python scripts\run_sseac_v0_pg40_openai_compatible.py `
  --packet experiments\20260618-local-sseac-v0-pg40-adapter\sseac_pg40_packet.jsonl `
  --limit 5 `
  --dry-run-prompts-out experiments\20260618-local-sseac-v0-pg40-launch-gate\dry_run_prompts_limit5.jsonl
```

结果：

```json
{
  "rows": 5,
  "dry_run_prompts_out": "experiments\\20260618-local-sseac-v0-pg40-launch-gate\\dry_run_prompts_limit5.jsonl"
}
```

## Limit5 Prompt Stats

| Metric | Value |
| --- | ---: |
| rows | 5 |
| prompt chars min | 6507 |
| prompt chars max | 10726 |
| prompt chars avg | 8349.2 |
| source cards min | 7 |
| source cards max | 9 |
| source cards avg | 7.4 |

Packet ids:

```text
pg_000__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0
pg_000__seed_42__source_rotated_scope_v0__tightbf55_rank_scope_v0
pg_002__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0
pg_002__seed_42__source_rotated_scope_v0__tightbf55_rank_scope_v0
pg_003__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0
```

## Leak Check

精确 evaluator-only 字段检查无命中：

```text
required_slots
acceptable_card_ids
slot_id
expected_final_decision
gold_answer
oracle_unit_ids
downstream_scoring_obligations
```

## Baseline To Beat

| Condition | Strict | Utility | Role |
| --- | ---: | ---: | --- |
| `oracle_utility` | 40/40 | 1.0000 | upper bound |
| `utility_density_greedy_after_sseac_compiler` | 25/40 | 0.9825 | strong baseline |
| `source_ledger_14b_fullprompt_budget_compiled` | 11/40 | 0.8707 | old source-ledger diagnostic |
| `source_ledger_7b_fullprompt_budget_compiled` | 2/40 | 0.6034 | old source-ledger diagnostic |

## Endpoint Status

当前环境没有配置可用 endpoint：

```text
OPENAI_API_KEY=<unset>
OPENAI_BASE_URL=<unset>
VLLM_BASE_URL=<unset>
LOCAL_OPENAI_BASE_URL=<unset>
A8002_BASE_URL=<unset>
```

常用本地 vLLM 端口检查结果：

```text
8000 closed
8001 closed
8002 closed
8008 closed
8010 closed
8047 closed
8051 closed
8053 closed
```

因此本轮停在 launch gate，不产生 behavior result。

## Ready Command

有 openai-compatible endpoint 后，执行：

```powershell
$env:OPENAI_API_KEY="<api-key-or-dummy-local-key>"

python scripts\run_sseac_v0_pg40_openai_compatible.py `
  --packet experiments\20260618-local-sseac-v0-pg40-adapter\sseac_pg40_packet.jsonl `
  --limit 5 `
  --base-url "<openai-compatible-base-url>" `
  --model "<served-model-name>" `
  --out experiments\20260618-local-sseac-v0-pg40-launch-gate\predictions_limit5.jsonl `
  --temperature 0 `
  --max-tokens 2048

python scripts\compile_sseac_v0.py `
  --packet experiments\20260618-local-sseac-v0-pg40-adapter\sseac_pg40_packet.jsonl `
  --predictions experiments\20260618-local-sseac-v0-pg40-launch-gate\predictions_limit5.jsonl `
  --out experiments\20260618-local-sseac-v0-pg40-launch-gate\compiled_limit5.jsonl `
  --summary-out experiments\20260618-local-sseac-v0-pg40-launch-gate\compile_summary_limit5.json

python scripts\score_sseac_pg40_compiled.py `
  --pg-packet experiments\20260618-local-perspectivegap-tight-budget-v0\tight_budget_rotated20.jsonl `
  --compiled experiments\20260618-local-sseac-v0-pg40-launch-gate\compiled_limit5.jsonl `
  --out experiments\20260618-local-sseac-v0-pg40-launch-gate\scores_limit5.jsonl `
  --summary-out experiments\20260618-local-sseac-v0-pg40-launch-gate\summary_limit5.md
```

## Status

`READY_FOR_ENDPOINT`。

下一步只有在 endpoint 可用时才启动模型调用。模型结果出来后，先写小样本 triage，暂不写主表结论。
