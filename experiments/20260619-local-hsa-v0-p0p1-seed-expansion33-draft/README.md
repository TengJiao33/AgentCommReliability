# HSA-v0 P0/P1 Seed Expansion33 Draft

日期：2026-06-19

## 核心判断

这次把 HSA 从 15 行扩到 33 行的 P0/P1 草案包已经通过本地门禁。包内共有 `11` 个推荐种子，每个种子 `1` 个基础行和 `2` 个扰动行。透明控制闭合：理想准入 `33/33`，只给共享信息 `22/33` 且基础行 `0/11`，全范围信息 `33/33` 但多余最终卡片 `111`。

这个包可以进入远程真跑。P2 的 `baker_2010` 暂时隔离，因为它是长档案比较型种子，证据结构和应急决策型种子差异较大。

## 范围

| 项 | 值 |
| --- | ---: |
| fact rows | `11` |
| packet rows | `33` |
| base rows | `11` |
| perturbation rows | `22` |
| excluded recommended seed | `5` |

纳入任务编号：`3`、`10`、`11`、`12`、`21`、`27`、`31`、`44`、`51`、`54`、`56`。

排除任务编号：`5`。原因是该任务为长档案比较型，需要单独写 profile-level admission units。

## 产物

| 类型 | 路径 |
| --- | --- |
| 生成脚本 | `scripts/build_hsa_p0p1_seed_expansion_drafts.py` |
| fact draft | `p0p1_fact_units.draft.json` |
| perturbation draft | `p0p1_perturbations.draft.json` |
| packet | `packet/hsa_v0_packet.jsonl` |
| dry-run prompts | `dry_run_constraint_recall.jsonl` |

## 命令

```powershell
python scripts\build_hsa_p0p1_seed_expansion_drafts.py --out-dir experiments\20260619-local-hsa-v0-p0p1-seed-expansion33-draft

python scripts\build_hsa_v0_sseac_packet.py --fact-draft experiments\20260619-local-hsa-v0-p0p1-seed-expansion33-draft\p0p1_fact_units.draft.json --perturbation-draft experiments\20260619-local-hsa-v0-p0p1-seed-expansion33-draft\p0p1_perturbations.draft.json --out-dir experiments\20260619-local-hsa-v0-p0p1-seed-expansion33-draft\packet

python scripts\run_hsa_v0_sseac_openai_compatible.py --packet experiments\20260619-local-hsa-v0-p0p1-seed-expansion33-draft\packet\hsa_v0_packet.jsonl --prompt-contract constraint_recall --dry-run-prompts-out experiments\20260619-local-hsa-v0-p0p1-seed-expansion33-draft\dry_run_constraint_recall.jsonl
```

透明控制使用 `compile_sseac_v0.py` 和 `score_hsa_v0_compiled.py` 逐组评分。

## 透明控制

| 控制 | 严格正确 | 基础行 | 扰动行 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 理想准入 | `33/33` | `1.0000` | `1.0000` | `0.8394` | `0` | `0.0000` |
| 只给共享信息 | `22/33` | `0.0000` | `1.0000` | `0.0818` | `111` | `0.3333` |
| 全范围信息 | `33/33` | `1.0000` | `1.0000` | `0.8394` | `111` | `0.0000` |

## 提示检查

| 项 | 值 |
| --- | ---: |
| rows | `33` |
| min prompt chars | `7830` |
| max prompt chars | `8860` |
| avg prompt chars | `8256.6` |
| evaluator-only field hits | `0` |

扫描字段包括 `gold_answer`、`required_slots`、`acceptable_card_ids`、`expected_final_decision`、`downstream_scoring_obligations`、`oracle_unit_ids`、`oracle_admission_units`、`correct_answer`、`verdict`。

## 发射条件

这个包满足远程真跑条件：

- 理想准入闭合；
- 共享信息基础行全错，说明通信必要性仍在；
- 全范围信息暴露大量多余最终卡片，可以检测全收证据路线；
- 提示泄漏检查为零；
- 每个 seed 都有基础行和两个扰动行。

## 下一步

远程 GPU 7 跑 `constraint_recall`，然后对同一输出套 `visible_verified_blocker_completion`。若 33 行补全后仍保持高严格正确，且多余最终卡片明显低于 `111`，再处理 P2 长档案种子或进入更完整 benchmark。
