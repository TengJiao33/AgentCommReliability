# HSA 当前路线

日期：2026-06-19

## 当前判断

HSA 是当前最清楚的内部机制诊断路线。它考察模型提出候选证据后，硬准入规则能否通过来源、范围、验证状态和拒绝规则改变最终下游决策。它不承担公开基准方法有效性结论。

目前它有完整 36 行诊断信号。constraint_recall 三十六行真跑中，模型直出是 `16/36`，硬准入是 `34/36`，阻断补全后硬准入是 `35/36`，支撑型窄补全后硬准入是 `36/36`。extra final cards 是 `42`，明显低于全范围信息控制的 `195`。

## 当前证据

| 项 | 内容 |
| --- | --- |
| 当前最好运行 | `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b/` |
| 状态 | `DIAGNOSTIC_BEHAVIOR_RESULT` |
| 模型 | `Qwen2.5-14B-Instruct` |
| 行数 | `36` |
| 模型直出 | `16/36` |
| 硬准入后 | `34/36` |
| 阻断补全后硬准入 | `35/36` |
| 支撑型窄补全后硬准入 | `36/36` |
| 槽位召回 | `0.8477` |
| 多余最终卡片 | `42` |
| 强制作答 | `0.5278` |

解释：三十六行真跑里，硬准入把扰动行从模型直出的 `5/24` 推到 `24/24`；阻断补全修掉东镇基础行；支撑型窄补全补上 task 5 Roberts 正向支撑卡，并保持扰动行 `24/24`。

## 当前风险

- 样本仍是项目内 HSA 包，还不能承担公开大基准结论。
- 强制作答检出率仍高，说明模型本体仍有硬答倾向。
- 支撑型窄补全目前是本地诊断后处理，旧 33 行和 15 行重放已经干净；规则、禁区和升级门槛已经写入 `docs/hsa_support_completion_method_component.md`。
- 后续修复必须保留透明控制同表报告：`oracle_admissible_facts`、`shared_only_verified`、`all_scoped_verified`。

## 下一步

下一步暂停 HSA 扩包，把远程资源转向 PG40 / PerspectiveGap 公开切片主表。HSA 后续只在需要机制解释、错误定位或附表材料时恢复。若未来恢复远程运行，默认使用 GPU 7：

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=constraint_recall GPU_ID=7 PORT=<free-port> RUN_ID=<new-run-id> LIMIT=0 PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl GPU_MEMORY_UTILIZATION=0.80 MAX_MODEL_LEN=16384 MAX_TOKENS=3072 bash scripts/run_hsa_v0_sseac_a8002.sh
```

运行前检查 `docs/remote_sync_manifest.md`，确认脚本和输入包已同步。

## 相关文件

| 类型 | 路径 |
| --- | --- |
| 初始输入包 | `experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl` |
| 初始透明控制 | `experiments/20260618-local-hsa-v0-sseac-adapter/` |
| 最新完整模型运行 | `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b/` |
| 当前最好诊断运行 | `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b/` |
| 状态报告 | `reports/20260619-hsa-v0-constraint-recall-p0p1p2-36-a8002.md` |
| 当前最好报告 | `reports/20260619-hsa-v0-constraint-recall-p0p1p2-36-a8002.md` |
| recall_sweep 预检 | `experiments/20260619-local-hsa-v0-recall-sweep-preflight/` |
| focused_recall 预检 | `experiments/20260619-local-hsa-v0-focused-recall-preflight/` |
| constraint_recall 预检 | `experiments/20260619-local-hsa-v0-constraint-recall-preflight/` |
| constraint_completion 诊断 | `experiments/20260619-local-hsa-v0-constraint-completion-postfilter/` |
| seed shortlist gate | `experiments/20260619-local-hsa-v0-seed-shortlist-gate/` |
| seed gate 报告 | `reports/20260619-hsa-v0-seed-shortlist-gate.md` |
| HB12/HB31 draft | `experiments/20260619-local-hsa-v0-hb12-hb31-draft/` |
| HB12/HB31 draft 报告 | `reports/20260619-hsa-v0-hb12-hb31-draft-packet.md` |
| 15 行扩展包 | `experiments/20260619-local-hsa-v0-extended15-packet/` |
| 15 行扩展包报告 | `reports/20260619-hsa-v0-extended15-packet-gate.md` |
| 15 行真跑门禁 | `experiments/20260619-local-hsa-v0-extended15-launch-gate/` |
| 15 行真跑门禁报告 | `reports/20260619-hsa-v0-extended15-launch-gate.md` |
| 15 行真跑 | `experiments/20260619-a8002-hsa-v0-constraint-recall-extended15-qwen25-14b/` |
| 15 行真跑报告 | `reports/20260619-hsa-v0-constraint-recall-extended15-a8002.md` |
| 33 行 P0/P1 包 | `experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft/` |
| 33 行 P0/P1 门禁报告 | `reports/20260619-hsa-v0-p0p1-seed-expansion33-gate.md` |
| 33 行真跑 | `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1-33-qwen25-14b/` |
| 33 行真跑报告 | `reports/20260619-hsa-v0-constraint-recall-p0p1-33-a8002.md` |
| 36 行 P0/P1/P2 包 | `experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/` |
| 36 行真跑 | `experiments/20260619-a8002-hsa-v0-constraint-recall-p0p1p2-36-qwen25-14b/` |
| 36 行真跑报告 | `reports/20260619-hsa-v0-constraint-recall-p0p1p2-36-a8002.md` |
| 支撑型窄补全组件说明 | `docs/hsa_support_completion_method_component.md` |
| 更大派生包预飞行 | `docs/hsa_larger_derived_packet_preflight.md` |
| 更大派生包候选复核 | `docs/hsa_larger_derived_candidate_review.md` |
| HSA 数字主表 | `docs/hsa_v0_numeric_main_table.md` |
| 运行脚本 | `scripts/run_hsa_v0_sseac_a8002.sh` |
| 通用运行器 | `scripts/run_hsa_v0_sseac_openai_compatible.py` |
| 编译器 | `scripts/compile_sseac_v0.py` |
| 评分器 | `scripts/score_hsa_v0_compiled.py` |
