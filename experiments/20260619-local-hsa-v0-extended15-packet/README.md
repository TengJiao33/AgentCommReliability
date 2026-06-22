# HSA-v0 Extended 15 Packet

日期：2026-06-19

## 核心判断

这次把原有 9 行 HSA 包和 HB12/HB31 新 6 行草案合并成 15 行扩展包。透明控制已经闭合：理想准入 `15/15`，只给共享信息 `10/15` 且基础行 `0/5`，全范围信息 `15/15` 但多余最终卡片 `39`。

这说明 15 行扩展包继续保留了目标压力：基础行需要角色范围内的隐藏已验证证据才能作答，扰动行在证据缺失或未验证时应输出证据不足。下一步可以做远程模型真跑，再对同一输出套可见已验证阻断卡补全。

## 输入

| 项 | 路径 |
| --- | --- |
| 原 9 行包 | `experiments/20260618-local-hsa-v0-sseac-adapter/` |
| 新 6 行包 | `experiments/20260619-local-hsa-v0-hb12-hb31-draft/packet/` |
| 合并脚本 | `scripts/merge_hsa_packet_artifacts.py` |
| 输出目录 | `experiments/20260619-local-hsa-v0-extended15-packet/` |

## 合并概况

| 项 | 值 |
| --- | ---: |
| 总行数 | `15` |
| 基础行 | `5` |
| 扰动行 | `10` |
| 原始任务数 | `5` |
| 每任务行数 | `3` |

覆盖的任务编号：`1`、`10`、`11`、`12`、`31`。

## 命令

```powershell
python scripts\merge_hsa_packet_artifacts.py --left-dir experiments\20260618-local-hsa-v0-sseac-adapter --right-dir experiments\20260619-local-hsa-v0-hb12-hb31-draft\packet --out-dir experiments\20260619-local-hsa-v0-extended15-packet

python scripts\compile_sseac_v0.py --packet experiments\20260619-local-hsa-v0-extended15-packet\hsa_v0_packet.jsonl --predictions experiments\20260619-local-hsa-v0-extended15-packet\predictions_oracle_admissible_facts.jsonl --mode compiler --out experiments\20260619-local-hsa-v0-extended15-packet\compiled_oracle_admissible_facts.jsonl --summary-out experiments\20260619-local-hsa-v0-extended15-packet\compile_summary_oracle_admissible_facts.json
python scripts\score_hsa_v0_compiled.py --packet experiments\20260619-local-hsa-v0-extended15-packet\hsa_v0_packet.jsonl --compiled experiments\20260619-local-hsa-v0-extended15-packet\compiled_oracle_admissible_facts.jsonl --out experiments\20260619-local-hsa-v0-extended15-packet\scores_oracle_admissible_facts.jsonl --summary-out experiments\20260619-local-hsa-v0-extended15-packet\summary_hsa_oracle_admissible_facts.md
```

同样命令也用于 `shared_only_verified` 和 `all_scoped_verified`。

提示文本检查：

```powershell
python scripts\run_hsa_v0_sseac_openai_compatible.py --packet experiments\20260619-local-hsa-v0-extended15-packet\hsa_v0_packet.jsonl --prompt-contract constraint_recall --dry-run-prompts-out experiments\20260619-local-hsa-v0-extended15-packet\dry_run_constraint_recall.jsonl
```

## 透明控制

| 控制 | 严格正确 | 基础行 | 扰动行 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 理想准入 | `15/15` | `1.0000` | `1.0000` | `0.8400` | `0` | `0.0000` |
| 只给共享信息 | `10/15` | `0.0000` | `1.0000` | `0.1956` | `39` | `0.3333` |
| 全范围信息 | `15/15` | `1.0000` | `1.0000` | `0.8400` | `39` | `0.0000` |

## 提示检查

| 项 | 值 |
| --- | ---: |
| 行数 | `15` |
| 最短提示字符数 | `7949` |
| 最长提示字符数 | `8444` |
| 平均提示字符数 | `8185.2` |
| 评价专用字段命中 | `0` |

扫描字段包括 `gold_answer`、`required_slots`、`acceptable_card_ids`、`expected_final_decision`、`downstream_scoring_obligations`、`oracle_unit_ids`、`oracle_admission_units`、`correct_answer`、`verdict`。

## 边界

- 这不是模型结果，是扩展包和透明控制门禁。
- 15 行仍是小样本，适合做模型机制诊断，暂时不能写成规模性结论。
- 全范围信息虽然严格正确，但多余最终卡片达到 `39`，说明“全收证据”路线会被专门标出来。

## 下一步

1. 同步 `scripts/merge_hsa_packet_artifacts.py`、构建脚本、运行脚本和 15 行包到远程。
2. 若七号卡空闲，跑 `constraint_recall` 十五行真模型输出。
3. 对同一输出套 `visible_verified_blocker_completion`，比较模型直出、硬准入、后置补全三列。
