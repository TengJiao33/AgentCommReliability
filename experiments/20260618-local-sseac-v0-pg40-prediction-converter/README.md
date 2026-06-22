# SSEAC-v0 PG40 Prediction Converter Diagnostic

日期：2026-06-18

## 目的

这次本地诊断把已有 PerspectiveGap tight-budget 预测转成 SSEAC `candidate_units`，再经过 `compile_sseac_v0.py` 和 PG40 scorer 回到 coverage / precision / budget / utility 指标。

它的目的很窄：确认现有 PG40 role-card 输出能否进入 SSEAC pipeline，并观察旧 source-ledger 输出经过 SSEAC hard constraints 后处在什么位置。它不调用模型，不构成 SSEAC-v0 方法效果结论。

## Preflight

```text
purpose:
  将已有 PG40 baseline / model predictions 接入 SSEAC compiler，确认同表比较入口是否可用。

unit:
  PerspectiveGap tight-budget 40-row slice 的一个 hard_evaluation_id。

primary_contrast:
  source_ledger_14b_fullprompt_budget_compiled vs utility_density_greedy under SSEAC conversion。

secondary_contrasts:
  oracle_utility, eligible_all, eligible_cheapest, source_ledger_7b_fullprompt_budget_compiled。

success_signal:
  oracle fixture 40/40 strict；所有 condition 能成功转换、编译、评分；summary 能复现 PG40 指标族。

failure_signal:
  oracle strict 低于 40/40；预测无法映射到 packet_id；compiler 与 scorer 指标不兼容。

invalidation_conditions:
  proposed_rejections 丢失；fragment_id/source_id 映射错误；budget order 不能复现预测顺序；PG40 scorer 与 compiled output 不兼容。
```

## 输入

- PG packet: `experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl`
- SSEAC packet: `sseac_pg40_packet.jsonl`
- Source predictions:
  - `predictions_oracle_utility.jsonl`
  - `predictions_eligible_all.jsonl`
  - `predictions_eligible_cheapest.jsonl`
  - `predictions_utility_density_greedy.jsonl`
  - `predictions_source_ledger_7b_fullprompt_budget_compiled.jsonl`
  - `predictions_source_ledger_14b_fullprompt_budget_compiled.jsonl`

## 命令摘要

```powershell
python -m py_compile scripts\convert_perspectivegap_predictions_to_sseac.py scripts\score_sseac_pg40_compiled.py scripts\compile_sseac_v0.py
```

每个 condition 执行三步：

```powershell
python scripts\convert_perspectivegap_predictions_to_sseac.py --sseac-packet <sseac_packet> --predictions <pg_predictions> --out <sseac_predictions>
python scripts\compile_sseac_v0.py --packet <sseac_packet> --predictions <sseac_predictions> --out <compiled> --summary-out <compile_summary>
python scripts\score_sseac_pg40_compiled.py --pg-packet <pg_packet> --compiled <compiled> --out <scores> --summary-out <pg40_summary>
```

## PG40 Summary

| Condition | Strict | Coverage | Precision | Budget pass | Utility ratio | Exact target role |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `oracle_utility` | 40/40 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `eligible_all` after SSEAC compiler | 13/40 | 0.9112 | 0.9595 | 1.0000 | 0.9731 | 0.9133 |
| `eligible_cheapest` after SSEAC compiler | 14/40 | 0.8639 | 0.8439 | 1.0000 | 0.8927 | 0.7242 |
| `utility_density_greedy` after SSEAC compiler | 25/40 | 0.9497 | 0.9386 | 1.0000 | 0.9825 | 0.8775 |
| `source_ledger_7b_fullprompt_budget_compiled` | 2/40 | 0.4675 | 0.7783 | 1.0000 | 0.6034 | 0.3712 |
| `source_ledger_14b_fullprompt_budget_compiled` | 11/40 | 0.7515 | 0.9270 | 1.0000 | 0.8707 | 0.6842 |

## Compile Summary

`source_ledger_14b_fullprompt_budget_compiled`:

```json
{
  "rows": 40,
  "ok_rows": 40,
  "error_rows": 0,
  "scope_violations_prevented": 0,
  "invalid_support_prevented": 0,
  "budget_rejections": 0,
  "forced_commitment_rate": 0.725,
  "downstream_ok": 0.275
}
```

`eligible_all`:

```json
{
  "rows": 40,
  "ok_rows": 40,
  "error_rows": 0,
  "scope_violations_prevented": 0,
  "invalid_support_prevented": 0,
  "budget_rejections": 219,
  "forced_commitment_rate": 0.275,
  "downstream_ok": 0.725
}
```

## 读法

oracle 达到 `40/40` strict，说明 adapter、compiler 和 PG40 scorer 的格式闭环通过。

`utility_density_greedy` 仍然是当前最强透明 baseline：`25/40` strict，`0.9825` utility ratio。它说明 PG40 tight-budget v0 对简单贪心仍偏友好，后续方法 claim 需要更硬的 dependency / non-greedy packet 或更强的对照。

旧 `source_ledger_14b_fullprompt_budget_compiled` 只有 `11/40` strict，低于 `utility_density_greedy`。这说明复用旧 source-ledger 输出不足以支撑 SSEAC-v0；下一步需要专门的 SSEAC prompt，让模型输出 priority、candidate_units 和 claimed_slots。

`eligible_all` 经过 SSEAC compiler 后从原始预算违规状态变成 `budget_pass=1.0000`，但只得到 `13/40` strict。它提示 hard executor 可以修 budget，但预测顺序会决定哪些必要事实被预算裁掉。

## 边界

这是本地转换诊断，没有调用新模型。

PG40 的 `downstream_ok` 是 synthetic `routing_complete` 槽位检查，不对应真实下游任务 accuracy。

当前 SSEAC compiler 对 PG40 的作用主要是 hard constraint / budget / slot gate；它还没有接入专门训练或专门提示的 SSEAC model proposal。

## 下一步

下一步应写 `run_sseac_v0_pg40_openai_compatible.py` 或在现有 PerspectiveGap runner 中加入 SSEAC prompt style。模型需要直接输出：

- `option_states`
- `candidate_units`
- `priority`
- `claimed_slots`
- `proposed_rejections`

第一轮只跑小样本，不开 GPU 大跑。成功条件是 SSEAC prompt 在 coverage 接近 source-ledger 14B 的同时，减少 budget / precision / forced-commitment 问题，并能逼近或超过 `utility_density_greedy` 这个透明强 baseline。

## Artifacts

- Converter: `scripts/convert_perspectivegap_predictions_to_sseac.py`
- Compiled scorer: `scripts/score_sseac_pg40_compiled.py`
- SSEAC packet: `sseac_pg40_packet.jsonl`
- SSEAC predictions: `sseac_predictions_*.jsonl`
- Compiled outputs: `compiled_*.jsonl`
- Compile summaries: `summary_compile_*.json`
- PG40 summaries: `summary_pg40_*.md`
