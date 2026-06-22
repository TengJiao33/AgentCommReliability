# HSA-v0 P0/P1/P2 Seed Expansion36 Draft

日期：2026-06-19

## 核心判断

这个包把 P2 长档案种子 `baker_2010` 纳入 HSA，形成完整 `12` 个推荐种子、`36` 行的准入包。透明控制已经闭合：理想准入 `36/36`，只给共享信息 `24/36` 且基础行 `0/12`，全范围信息 `36/36` 但多余最终卡片 `195`。

这个包可以进入远程真跑。主要风险是 task 5 的基础行提示较长，最长提示为 `21037` 字符；远程运行应使用 `MAX_MODEL_LEN=16384`。

## 实验目的

目的：检验 HSA 的候选证据准入机制在短任务和长档案任务混合时是否仍能工作。

单位：一个 packet row。每个推荐 seed 包含一个基础行和两个扰动行。

主对照：模型直出、硬准入、补全后硬准入。

辅助对照：理想准入、只给共享信息、全范围信息。

成功信号：硬准入或补全后硬准入保持高严格正确；多余最终卡片明显低于全范围信息控制；扰动行继续回到 `insufficient_evidence`。

失败信号：task 5 导致模型输出不可解析、基础行大量证据漏提、扰动行大量强制作答，或多余最终卡片接近全范围信息控制。

失效条件：提示泄漏评测字段、透明控制不闭合、远程脚本和本地 packet 错位、模型窗口不足导致 task 5 提示截断或失败。

## 范围

| 项 | 值 |
| --- | ---: |
| fact rows | `12` |
| packet rows | `36` |
| base rows | `12` |
| perturbation rows | `24` |
| included P2 seed | `5` |

纳入任务编号：`3`、`5`、`10`、`11`、`12`、`21`、`27`、`31`、`44`、`51`、`54`、`56`。

## Task 5 标注方式

`baker_2010` 是长档案比较任务。这个包没有把四段长私有资料作为四张大卡直接塞入，而是拆成候选人级别的 profile cards。核心证据单元包括：

| 单元 | 作用 |
| --- | --- |
| `hb05_unit_stevens_profile_blocked` | Stevens 的 fundraising、innovation、conduct 阻断 |
| `hb05_unit_jones_governance_blocked` | Jones 的 abrasive turnover 和 provost tension 阻断 |
| `hb05_unit_roberts_academic_governance_enabled` | Roberts 的 collaborative governance、teaching、research productivity 支撑 |
| `hb05_unit_roberts_advancement_diversity_enabled` | Roberts 的 contacts、diversity、federal grant 支撑 |

两个扰动分别把 Roberts grant 变成未验证事实、把 Jones provost tension 移出 final_decider 范围。两者都应使最终状态变为证据不足。

## 产物

| 类型 | 路径 |
| --- | --- |
| 生成脚本 | `scripts/build_hsa_p0p1_seed_expansion_drafts.py --include-p2-profile` |
| fact draft | `p0p1p2_fact_units.draft.json` |
| perturbation draft | `p0p1p2_perturbations.draft.json` |
| packet | `packet/hsa_v0_packet.jsonl` |
| dry-run prompts | `dry_run_constraint_recall.jsonl` |

## 命令

```powershell
python scripts\build_hsa_p0p1_seed_expansion_drafts.py --include-p2-profile --out-dir experiments\20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft

python scripts\build_hsa_v0_sseac_packet.py --fact-draft experiments\20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft\p0p1p2_fact_units.draft.json --perturbation-draft experiments\20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft\p0p1p2_perturbations.draft.json --out-dir experiments\20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft\packet

python scripts\run_hsa_v0_sseac_openai_compatible.py --packet experiments\20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft\packet\hsa_v0_packet.jsonl --prompt-contract constraint_recall --dry-run-prompts-out experiments\20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft\dry_run_constraint_recall.jsonl
```

## 透明控制

| 控制 | 严格正确 | 基础行 | 扰动行 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 理想准入 | `36/36` | `1.0000` | `1.0000` | `0.8477` | `0` | `0.0000` |
| 只给共享信息 | `24/36` | `0.0000` | `1.0000` | `0.0750` | `129` | `0.3333` |
| 全范围信息 | `36/36` | `1.0000` | `1.0000` | `0.8477` | `195` | `0.0000` |

## 提示检查

| 项 | 值 |
| --- | ---: |
| rows | `36` |
| min prompt chars | `7830` |
| max prompt chars | `21037` |
| avg prompt chars | `9320.8` |
| longest row | `hiddenbench_baker_2010__hb05_base_verified_profile_scoped__hsa_v0` |
| evaluator-only field hits | `0` |

扫描字段包括 `gold_answer`、`required_slots`、`acceptable_card_ids`、`expected_final_decision`、`downstream_scoring_obligations`、`oracle_unit_ids`、`oracle_admission_units`、`correct_answer`、`verdict`。

## 远程发射建议

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=constraint_recall GPU_ID=7 PORT=8076 RUN_ID=20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b LIMIT=0 PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl GPU_MEMORY_UTILIZATION=0.80 MAX_MODEL_LEN=16384 MAX_TOKENS=3072 RUN_TIMEOUT=3600 bash scripts/run_hsa_v0_sseac_a8002.sh
```

## 下一步

同步脚本和 packet 到 A800_2，使用 GPU 7 跑 `constraint_recall`。跑完后对同一输出套 `visible_verified_blocker_completion`，并把 36 行结果更新到 HSA 数字表和当前证据入口。
