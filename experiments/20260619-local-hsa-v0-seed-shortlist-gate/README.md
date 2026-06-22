# HSA-v0 Seed Shortlist Gate

日期：2026-06-19

## 核心判断

这次 gate 只做离线审计，不启动模型，不产生新 benchmark 分数。目标是检查 HiddenBench failure seed 池里哪些 case 已经具备 HSA-v0 所需的人工标注。

结论：12 个推荐 seed 已经全部有人工 fact draft，并且全部进入当前三十六行 HSA packet。当前没有待补的 P0 推荐 seed。下一步若扩包，应先做扩展候选筛选门，从非推荐候选或新增 case 中重新筛选。

## 输入

| 项 | 路径 |
| --- | --- |
| failure seed cards | `experiments/20260618-local-hiddenbench-failure-seeds/case_cards.jsonl` |
| fact draft | `experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/p0p1p2_fact_units.draft.json` |
| perturbation draft | `experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/p0p1p2_perturbations.draft.json` |
| current HSA packet | `experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl` |
| audit script | `scripts/audit_hsa_seed_shortlist.py` |

## 命令

```powershell
python scripts\audit_hsa_seed_shortlist.py --out-dir experiments\20260619-local-hsa-v0-seed-shortlist-gate
```

## 输出

| 文件 | 用途 |
| --- | --- |
| `seed_gate_rows.csv` | 每个候选 seed 的机器可筛选状态 |
| `seed_gate_summary.json` | 计数摘要 |
| `seed_gate.md` | 中文可读 gate 说明 |

## 摘要

| 项 | 数量 |
| --- | ---: |
| extracted candidates | `32` |
| recommended seeds | `12` |
| recommended with fact draft | `12` |
| recommended packetized | `12` |
| recommended unpacketized | `0` |
| sanity packetized outside shortlist | `0` |

P0 下一步：当前没有 P0 推荐 seed 待标注。

## 边界

- 这次 gate 不是模型结果。
- 缺少人工 `oracle_admission_units` 和扰动定义的 seed 不能进入真跑。
- 推荐 seed 已经全部进入三十六行包；后续扩包不能自动沿用旧推荐队列。

## 下一步

先做扩展候选筛选门，明确从哪些非推荐候选或新增 case 中选下一批 HSA seed。选定后再补 source cards、oracle admission units、rejections、base variant 和两个 perturbation；补完后 materialize packet，跑 transparent controls；controls 闭合后才值得上 GPU。
