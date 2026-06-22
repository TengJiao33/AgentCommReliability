# SSEAC-v0 Compiler Smoke

日期：2026-06-18

## 目的

这次本地 smoke 检查 `SSEAC-v0` 的确定性准入层是否能独立运行。它不调用模型，不构成 benchmark 结果；它只验证 schema、compiler、hard constraints 和 evidence sufficiency gate 的最小闭环。

## 设计

输入包含两行手工 fixture：

1. `smoke_hazard_blocked`: 模型尝试把 quarantined hazard fact 当成支撑，同时强推 `Warehouse B`。compiler 应拦下 quarantined fact，并在 `Warehouse A` 支撑完整时选择 `Warehouse A`。
2. `smoke_missing_support`: 模型用背景事实强推 `Warehouse B`。真正需要的支撑一个是 unverified，一个对 final_decider 不可见。compiler 应输出 `insufficient_evidence` 并记录 forced commitment。

## 命令

```powershell
python -m py_compile D:\develop\AgentCommReliability\scripts\compile_sseac_v0.py
python D:\develop\AgentCommReliability\scripts\compile_sseac_v0.py --packet D:\develop\AgentCommReliability\experiments\20260618-local-sseac-v0-compiler-smoke\packet.jsonl --predictions D:\develop\AgentCommReliability\experiments\20260618-local-sseac-v0-compiler-smoke\predictions.jsonl --out D:\develop\AgentCommReliability\experiments\20260618-local-sseac-v0-compiler-smoke\compiled.jsonl --summary-out D:\develop\AgentCommReliability\experiments\20260618-local-sseac-v0-compiler-smoke\summary.json
```

## 结果

```json
{
  "rows": 2,
  "ok_rows": 2,
  "error_rows": 0,
  "scope_violations_prevented": 0,
  "invalid_support_prevented": 1,
  "budget_rejections": 0,
  "forced_commitment_rate": 0.5,
  "downstream_ok": 1.0
}
```

## 读法

这个结果只说明本地 compiler 骨架可运行：它能过滤 quarantined / invalid support，并能在证据槽位不足时覆盖模型强制作答。

它还没有证明 `SSEAC-v0` 优于任何 baseline。下一步必须接 `PG40` adapter，把同一 compiler 放到 PerspectiveGap source-ledger / tight-budget slice 上，与 `source_ledger_model_only` 和 `priority_plus_executor` 同表比较。

## Artifacts

- Schema: `schemas/sseac_v0.schema.json`
- Compiler: `scripts/compile_sseac_v0.py`
- Packet: `experiments/20260618-local-sseac-v0-compiler-smoke/packet.jsonl`
- Fixture predictions: `experiments/20260618-local-sseac-v0-compiler-smoke/predictions.jsonl`
- Compiled output: `experiments/20260618-local-sseac-v0-compiler-smoke/compiled.jsonl`
- Summary: `experiments/20260618-local-sseac-v0-compiler-smoke/summary.json`
