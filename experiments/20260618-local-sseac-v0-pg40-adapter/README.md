# SSEAC-v0 PG40 Adapter Oracle Smoke

日期：2026-06-18

## 目的

这次本地 smoke 检查 PerspectiveGap tight-budget 40-row slice 能否被翻译成 SSEAC-v0 packet，并通过 SSEAC compiler 的 hard constraints、budget 和 slot gate。

它不调用模型，也不构成 Ours 相对 baseline 的结果。它只验证 adapter 和 oracle fixture 的格式闭环。

## 输入

- Source packet: `experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl`
- Rows: `40`
- Adapter: `scripts/build_sseac_from_perspectivegap_tight_budget.py`
- Compiler: `scripts/compile_sseac_v0.py`

## 命令

```powershell
python -m py_compile D:\develop\AgentCommReliability\scripts\build_sseac_from_perspectivegap_tight_budget.py D:\develop\AgentCommReliability\scripts\compile_sseac_v0.py
python D:\develop\AgentCommReliability\scripts\build_sseac_from_perspectivegap_tight_budget.py --packet D:\develop\AgentCommReliability\experiments\20260618-local-perspectivegap-tight-budget-v0\tight_budget_rotated20.jsonl --out D:\develop\AgentCommReliability\experiments\20260618-local-sseac-v0-pg40-adapter\sseac_pg40_packet.jsonl --oracle-predictions-out D:\develop\AgentCommReliability\experiments\20260618-local-sseac-v0-pg40-adapter\oracle_predictions.jsonl
python D:\develop\AgentCommReliability\scripts\compile_sseac_v0.py --packet D:\develop\AgentCommReliability\experiments\20260618-local-sseac-v0-pg40-adapter\sseac_pg40_packet.jsonl --predictions D:\develop\AgentCommReliability\experiments\20260618-local-sseac-v0-pg40-adapter\oracle_predictions.jsonl --out D:\develop\AgentCommReliability\experiments\20260618-local-sseac-v0-pg40-adapter\compiled_oracle.jsonl --summary-out D:\develop\AgentCommReliability\experiments\20260618-local-sseac-v0-pg40-adapter\summary_oracle.json
```

## 结果

```json
{
  "rows": 40,
  "ok_rows": 40,
  "error_rows": 0,
  "scope_violations_prevented": 0,
  "invalid_support_prevented": 0,
  "budget_rejections": 0,
  "forced_commitment_rate": 0.0,
  "downstream_ok": 1.0
}
```

## 读法

PG40 adapter 已经能把 `fragments`、`candidate_needed_by`、`reference_need_sets`、`role_budgets` 翻译成 SSEAC-v0 的 `SourceCard`、`required_slots` 和 `role_budgets`。

`downstream_ok=1.0` 在这里只表示 synthetic `routing_complete` slot 被 oracle fixture 满足；它不对应下游任务 accuracy。

下一步应补模型预测转换器：把现有 PerspectiveGap role-card response 或 source-ledger response 转成 SSEAC `candidate_units`，再与 `source_ledger_model_only`、`priority_plus_executor` 和 `oracle_executor` 同表比较。

## Artifacts

- SSEAC packet: `experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl`
- Oracle predictions: `experiments/20260618-local-sseac-v0-pg40-adapter/oracle_predictions.jsonl`
- Compiled oracle output: `experiments/20260618-local-sseac-v0-pg40-adapter/compiled_oracle.jsonl`
- Summary: `experiments/20260618-local-sseac-v0-pg40-adapter/summary_oracle.json`
