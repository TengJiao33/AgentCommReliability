# HSA-v0 HB12/HB31 Draft Packet

日期：2026-06-19

## 核心判断

这次把 seed gate 选出的 P0 seeds HB12 和 HB31 转成了 HSA-v0 draft packet。该 packet 目前有 6 行：2 个 base，4 个 perturbation。透明控制已闭合：oracle `6/6`，shared-only base `0/2`，all-scoped `6/6` 但 extra final cards `15`。

这说明 HB12/HB31 已经具备扩展 HSA 的基本形状。下一步可以把它和现有 9 行合并成 15 行包，再做模型真跑前 launch gate。

## 输入

| 项 | 路径 |
| --- | --- |
| fact draft | `hb12_hb31_fact_units.draft.json` |
| perturbation draft | `hb12_hb31_perturbations.draft.json` |
| builder | `scripts/build_hsa_v0_sseac_packet.py` |
| output packet | `packet/hsa_v0_packet.jsonl` |

## Rows

| seed | base | perturbations |
| --- | --- | --- |
| HB12 `evacuate_park_dilemma` | `hb12_base_verified_role_scoped` | `hb12_red_lake_sinkhole_unverified`; `hb12_green_valley_open_no_final_scope` |
| HB31 `weather_sensor_deployment` | `hb31_base_verified_role_scoped` | `hb31_gamma_boat_no_final_scope`; `hb31_beta_bridge_unverified` |

## 命令

```powershell
python scripts\build_hsa_v0_sseac_packet.py --fact-draft experiments\20260619-local-hsa-v0-hb12-hb31-draft\hb12_hb31_fact_units.draft.json --perturbation-draft experiments\20260619-local-hsa-v0-hb12-hb31-draft\hb12_hb31_perturbations.draft.json --out-dir experiments\20260619-local-hsa-v0-hb12-hb31-draft\packet
python scripts\run_hsa_v0_sseac_openai_compatible.py --packet experiments\20260619-local-hsa-v0-hb12-hb31-draft\packet\hsa_v0_packet.jsonl --prompt-contract constraint_recall --dry-run-prompts-out experiments\20260619-local-hsa-v0-hb12-hb31-draft\dry_run_constraint_recall.jsonl
```

透明控制评分使用原编译器和原 HSA scorer。

## 透明控制

| Control | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| oracle_admissible_facts | `6/6` | `1.0000` | `1.0000` | `0.8500` | `0` | `0.0000` |
| shared_only_verified | `4/6` | `0.0000` | `1.0000` | `0.2250` | `15` | `0.3333` |
| all_scoped_verified | `6/6` | `1.0000` | `1.0000` | `0.8500` | `15` | `0.0000` |

## Prompt Gate

| 项 | 值 |
| --- | ---: |
| dry-run rows | `6` |
| min prompt chars | `8115` |
| max prompt chars | `8380` |
| avg prompt chars | `8250.7` |
| evaluator-only field hits | `0` |

扫描字段包括 `gold_answer`、`required_slots`、`acceptable_card_ids`、`expected_final_decision`、`downstream_scoring_obligations`、`oracle_unit_ids`、`oracle_admission_units`、`correct_answer`、`verdict`。

## 边界

- 这是人工 draft packet，不是模型结果。
- HB12/HB31 的 oracle slots 还需要人工复核一次，尤其是 HB12 是否必须同时要求 Blueberry power 和 bridge 两张 blocker。
- 现在还没有把这 6 行合并进主 HSA 包。

## 下一步

1. 合并现有 9 行和 HB12/HB31 6 行，形成 HSA 15 行扩展包。
2. 对 15 行包重跑 transparent controls。
3. 若控制闭合，远程 GPU7 跑 `constraint_recall`，再套 `visible_verified_blocker_completion`。
