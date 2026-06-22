# HSA-v0 SSEAC Limit3 Launch Gate

日期：2026-06-18

## 目的

这次 launch gate 把 `HSA-v0 model row` 推到可执行边界。它物化 `limit 3` prompt，核对 evaluator-only 字段泄漏、transparent controls、runner 静态检查和 endpoint 状态。

本记录没有调用模型。当前结论是：runner 和 prompt 已准备好，模型执行受 openai-compatible endpoint 缺失限制。

## Preflight Contract

```text
purpose:
  在 HSA-v0 上跑第一轮 SSEAC-v0 proposer 小样本前，确认 packet、prompt、transparent controls 和执行入口。

unit:
  一个 HiddenBench-derived HSA-v0 SSEAC packet row。limit3 包含 1 个 base row 和 2 个 perturbation rows。

primary_contrast:
  future SSEAC model output vs oracle_admissible_facts, shared_only_verified, all_scoped_verified。

secondary_contrasts:
  base strict, perturbation strict, slot recall, extra final cards, forced commitment。

success_signal:
  模型输出可解析 JSON；compiler error rows 为 0；base row 能获得比 shared-only 更好的 evidence support；perturbation rows 维持 insufficient_evidence 或被 compiler 推到 insufficient_evidence；extra final cards 低于 all_scoped_verified。

failure_signal:
  输出无法解析；candidate_units 缺失；大量 invented card ids / roles；扰动行强制作答；extra final cards 接近 all_scoped_verified。

invalidation_conditions:
  prompt 泄漏 required_slots / acceptable_card_ids / expected_final_decision / gold_answer / oracle_unit_ids / downstream_scoring_obligations / hsa_meta；
  使用了不同 HSA-v0 packet；
  predictions 与 packet_id 无法对齐；
  小样本结果被写成主表结论。
```

## 已完成检查

```powershell
python -m py_compile scripts\run_hsa_v0_sseac_openai_compatible.py scripts\build_hsa_v0_sseac_packet.py scripts\score_hsa_v0_compiled.py scripts\compile_sseac_v0.py
```

结果：通过。

```powershell
python scripts\run_hsa_v0_sseac_openai_compatible.py `
  --packet experiments\20260618-local-hsa-v0-sseac-adapter\hsa_v0_packet.jsonl `
  --limit 3 `
  --dry-run-prompts-out experiments\20260618-local-hsa-v0-sseac-launch-gate\dry_run_prompts_limit3.jsonl
```

结果：

```json
{
  "rows": 3,
  "dry_run_prompts_out": "experiments\\20260618-local-hsa-v0-sseac-launch-gate\\dry_run_prompts_limit3.jsonl"
}
```

## Limit3 Prompt Stats

| Metric | Value |
| --- | ---: |
| rows | 3 |
| base rows | 1 |
| perturbation rows | 2 |
| prompt chars min | 5548 |
| prompt chars max | 5575 |
| prompt chars avg | 5565.67 |
| source cards min | 7 |
| source cards max | 7 |
| source cards avg | 7 |

Packet ids:

```text
hiddenbench_emergency_supply_drop__hb10_base_verified_role_scoped__hsa_v0
hiddenbench_emergency_supply_drop__hb10_b_hazard_quarantined__hsa_v0
hiddenbench_emergency_supply_drop__hb10_c_enabler_no_final_scope__hsa_v0
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
hsa_meta
```

## Transparent Controls

| Condition | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `oracle_admissible_facts` | 9/9 | 1.0000 | 1.0000 | 0.8333 | 0 | 0.0000 |
| `shared_only_verified` | 6/9 | 0.0000 | 1.0000 | 0.1759 | 24 | 0.3333 |
| `all_scoped_verified` | 9/9 | 1.0000 | 1.0000 | 0.8333 | 24 | 0.0000 |

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

python scripts\run_hsa_v0_sseac_openai_compatible.py `
  --packet experiments\20260618-local-hsa-v0-sseac-adapter\hsa_v0_packet.jsonl `
  --limit 3 `
  --base-url "<openai-compatible-base-url>" `
  --model "<served-model-name>" `
  --out experiments\20260618-local-hsa-v0-sseac-launch-gate\predictions_limit3.jsonl `
  --temperature 0 `
  --max-tokens 2048

python scripts\compile_sseac_v0.py `
  --packet experiments\20260618-local-hsa-v0-sseac-adapter\hsa_v0_packet.jsonl `
  --predictions experiments\20260618-local-hsa-v0-sseac-launch-gate\predictions_limit3.jsonl `
  --out experiments\20260618-local-hsa-v0-sseac-launch-gate\compiled_limit3.jsonl `
  --summary-out experiments\20260618-local-hsa-v0-sseac-launch-gate\compile_summary_limit3.json

python scripts\score_hsa_v0_compiled.py `
  --packet experiments\20260618-local-hsa-v0-sseac-adapter\hsa_v0_packet.jsonl `
  --compiled experiments\20260618-local-hsa-v0-sseac-launch-gate\compiled_limit3.jsonl `
  --out experiments\20260618-local-hsa-v0-sseac-launch-gate\scores_limit3.jsonl `
  --summary-out experiments\20260618-local-hsa-v0-sseac-launch-gate\summary_limit3.md
```

## Status

`READY_FOR_ENDPOINT`。

下一步只有在 endpoint 可用时才启动模型调用。模型结果出来后，先写小样本 triage，暂不写主表结论。
