# PG40 当前路线

日期：2026-06-20

## 当前判断

PG40 是当前对外报告的公开切片压力线，不是 PerspectiveGap 官方全量结果。它的透明启发式基线很强，能防止我们把普通提示改进误读成机制贡献。

2026-06-19 已补 PerspectiveGap 官方全量 direct baseline：Qwen2.5-14B official runner 默认提示在 `440` 行全网格上 combined strict `2/440`，role assignment `0/220`，prompt writing `2/220`。对外主证据应优先回到这个 full-grid 路线；PG40 继续作为预算、排序、角色分配和强基线压力表。

PG40 已有四轮五行模型行为结果。2026-06-19 的 direct routing 基线是 `0/5`、utility `0.0987`；普通 true prompt 严格正确 `0/5`，单卡候选契约后到 `1/5`，角色计划契约仍是 `1/5` 且 utility 降到 `0.7811`。这说明 candidate unit 粒度确实重要，但解释型 role plan 没有成为进步。

2026-06-20 的本地 scope-projection rerank 预检把下一瓶颈压到了 role-card affinity。五行上，`scope_project_cost_rank_pruned` 把 card-unit 输出从 `1/5` 推到 `5/5`；full40 旧 source-ledger 14B 输出从 `11/40` 推到 `17/40`、utility `0.8845`。这说明 projection + budget prune 是有效诊断组件，但它使用 PG40 `recipient_scope`，不能当 official full-grid no-gold 方法行。

同日的 no-scope 规则 selector 预检是负结果：不读取 `recipient_scope` 的 hybrid model-only 是 `0/40`、utility `0.5243`，cost model-only 是 `0/40`、utility `0.5467`。手写 lexical / cost 规则不值得继续调。

pairwise role-card selector 的本地 launch preflight 已完成，GPU7 五行真跑也已完成。结果是 `0/5`、utility `0.0000`，parse clean，prompt leak `0`，compiler 拦下 `14` 个 out-of-scope assignment 后 admitted units 为 `0`。这说明当前 no-scope pairwise prompt 会按表面 actor role 分配，缺少 target recipient assignment 的任务上下文。

公开切片基准测试主表已经落在 `docs/pg40_public_benchmark_main_table.md`。同五行上，我方当前模型方法候选 `true_sseac_cardunit_compiled` 是 `1/5`、utility `0.8155`，强于 direct 和无编译器输出，但低于 source-ledger 14B 同五行 utility `0.8498` 与透明贪心满分。当前最强诊断后处理是 `scope_project_cost_rank_pruned`，不是当前 Ours。

## 当前证据

| 项 | 内容 |
| --- | --- |
| 公开切片主表 | `docs/pg40_public_benchmark_main_table.md` |
| 官方全量 direct baseline | `experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/` |
| 强基线 | `utility_density_greedy_after_sseac_compiler` |
| 基线结果 | `25/40` 严格正确，utility `0.9825` |
| 旧模型管线 | source-ledger 14B compiled `11/40` |
| 最新工程失败 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-qwen25-14b/` |
| 当前最好行为运行 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b/` |
| 当前最好行为结果 | compiled `1/5`，budget pass `1.0000`，utility `0.8155`，coverage `0.6667` |
| 最新诊断运行 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b/` |
| 最新诊断状态 | `DIAGNOSTIC_NEGATIVE_RESULT` |
| 最新诊断结果 | compiled `1/5`，budget pass `1.0000`，utility `0.7811`，coverage `0.6667` |
| direct routing 运行 | `experiments/20260619-a8002-pg40-direct-routing-limit5-qwen25-14b/` |
| direct routing 结果 | strict `0/5`，budget pass `0.4000`，utility `0.0987` |
| scope projection 预检 | `experiments/20260620-local-pg40-scope-rerank-preflight/` |
| scope projection 五行结果 | strict `5/5`，budget pass `1.0000`，utility `1.0000` |
| scope projection full40 14B 结果 | strict `17/40`，budget pass `1.0000`，utility `0.8845` |
| no-scope 规则预检 | `experiments/20260620-local-pg40-no-scope-role-affinity-preflight/` |
| no-scope 规则结果 | hybrid model-only `0/40`、utility `0.5243`；cost model-only `0/40`、utility `0.5467` |
| pairwise selector 预飞行 | `experiments/20260620-local-pg40-pairwise-selector-preflight/` |
| pairwise selector 预飞行状态 | full40 prompts `40`；禁用字段扫描 `0`；schema smoke 通过 |
| pairwise selector 真跑 | `experiments/20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b/` |
| pairwise selector 结果 | model-only/compiler `0/5`，utility `0.0000`；parse ok `5/5`；out-of-scope prevented `14`；admitted units `0` |

解释：PG40 现在的作用是压住方法声明。SSEAC 需要在同一输入、同一评分、同一预算下和强透明基线对照。

## 当前风险

- 强透明基线太强，最终分数路线很难。
- 五行 true prompt 已确认结构稳定。
- 单卡候选契约明显改善 coverage 和 utility，但 strict 仍只有 `1/5`。
- 角色计划契约未改善，提示解释层继续加厚的收益很低。
- scope projection 依赖 PG40 `recipient_scope`，不能直接迁移到 PerspectiveGap official full-grid。
- no-scope 规则 selector 已负，说明 role-card affinity 不能靠手写 lexical / cost 规则解决。
- no-scope pairwise selector 已负，说明当前 prompt 缺少 role/recipient 转换上下文。
- full40 14B scope projection 仍低于 utility-density greedy `25/40`、utility `0.9825`。

## 下一步

direct 基线已经补完，scope-projection 透明后处理、no-scope 规则负结果和 pairwise selector 五行负结果也已补完。PG40 当前不应扩 pairwise full40；下一步应修 role/recipient interface，或转回 PerspectiveGap official role-assignment arms。HSA-v0 暂停扩包并保留为机制诊断。复现旧 SSEAC 五行时远程默认使用 GPU 7：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=<free-port> RUN_ID=<new-run-id> LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 bash scripts/run_sseac_v0_pg40_a8002.sh
```

运行前检查 `docs/remote_sync_manifest.md`，确认脚本和输入包已同步。

默认提示契约已经恢复为 `cardunit`。复现角色计划负结果时显式加：

```bash
PROMPT_CONTRACT=roleplan GPU_ID=7 PORT=<free-port> RUN_ID=<new-run-id> LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 bash scripts/run_sseac_v0_pg40_a8002.sh
```

复现 direct routing 基线时使用：

```bash
GPU_ID=7 PORT=<free-port> RUN_ID=20260619-a8002-pg40-direct-routing-limit5-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=2048 bash scripts/run_pg40_direct_routing_a8002.sh
```

pairwise selector 负结果复现使用：

```bash
GPU_ID=7 PORT=<free-port> RUN_ID=20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 bash scripts/run_pg40_pairwise_role_card_selector_a8002.sh
```

## 角色内排序预检

| 项 | 内容 |
| --- | --- |
| 预检记录 | `experiments/20260619-local-sseac-v0-pg40-roleplan-preflight/` |
| 计划 run id | `20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b` |
| GPU | `7` |
| limit | `5` |
| port | `8078` |
| max tokens | `3072` |
| 预检结论 | 五条 dry-run prompts 已生成，未发现金标字段泄漏 |
| 运行结果 | compiled `1/5`，utility `0.7811`，低于单卡契约 `0.8155` |
| 处置 | 退休该提示契约，不作为当前 Ours |

## 契约回收检查

| 项 | 内容 |
| --- | --- |
| 检查记录 | `experiments/20260619-local-sseac-v0-pg40-contract-check/` |
| 默认契约 | `cardunit` |
| 可选诊断契约 | `roleplan` |
| 本地检查 | `py_compile` 通过；默认 dry-run 不含 `role_plans`；roleplan dry-run 含 `role_plans` |
| 远程检查 | A800_2 脚本已同步；`py_compile` 和 `bash -n` 通过 |

## 当前重跑预检

| 项 | 内容 |
| --- | --- |
| 预检记录 | `experiments/20260619-local-sseac-v0-pg40-rerun-preflight/` |
| 计划 run id | `20260619-a8002-sseac-v0-pg40-limit5-gpu7-rerun-qwen25-14b` |
| GPU | `7` |
| limit | `5` |
| port | `8076` |
| 预检结论 | GPU 7 空闲；远程必要文件存在；五条 dry-run prompts 已生成，未发现金标字段泄漏 |

## 最新行为结果

| 条件 | Strict | Coverage | Precision | Budget pass | Utility | 读法 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| structured no compiler | 0/5 | 0.7778 | 0.6562 | 0.0000 | 0.1803 | 模型多塞候选，预算崩 |
| compiler | 0/5 | 0.3704 | 0.8333 | 1.0000 | 0.4635 | 预算修好，但必要证据被剪掉 |
| card-unit compiler | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.8155 | 单卡契约改善明显，但仍未达标 |
| role-plan compiler | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.7811 | 解释型角色计划未继续改善 |
| direct routing | 0/5 | 0.1481 | 0.1481 | 0.4000 | 0.0987 | 公开主表直接提示基线 |
| cost-rank pruned | 2/5 | 0.8148 | 0.9565 | 1.0000 | 0.8755 | 只改成本排序，已过 source-ledger 同五行 utility |
| scope-project cost-rank pruned | 5/5 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 使用 recipient_scope 的透明诊断后处理 |
| no-scope hybrid model-only | 0/40 | 0.5000 | 0.4605 | 1.0000 | 0.5243 | full40 规则式 no-scope selector 负结果 |
| no-scope cost model-only | 0/40 | 0.5858 | 0.3882 | 1.0000 | 0.5467 | cost prior 不能解决 role-card affinity |
| pairwise selector model-only | 0/5 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | parse clean；按表面 actor role 分配 |
| pairwise selector compiler | 0/5 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | compiler 拦截 14 个越界 assignment，admitted units 为 0 |

当前停点：PG40 不扩当前 pairwise full40；下一步修 role/recipient interface，或转回 official role-assignment arms。

## 相关文件

| 类型 | 路径 |
| --- | --- |
| 公开切片主表 | `docs/pg40_public_benchmark_main_table.md` |
| 公开切片机器表 | `docs/pg40_public_benchmark_main_table.csv` |
| SSEAC 输入包 | `experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl` |
| PG 原始包 | `experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl` |
| 强基线转换结果 | `experiments/20260618-local-sseac-v0-pg40-prediction-converter/` |
| 最新失败尝试 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-qwen25-14b/` |
| 最新行为运行 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-gpu7-rerun-qwen25-14b/` |
| 单卡契约运行 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b/` |
| 角色计划运行 | `experiments/20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b/` |
| scope projection 预检 | `experiments/20260620-local-pg40-scope-rerank-preflight/` |
| scope projection 报告 | `reports/20260620-pg40-scope-projection-rerank-preflight.md` |
| no-scope 规则预检 | `experiments/20260620-local-pg40-no-scope-role-affinity-preflight/` |
| no-scope 规则报告 | `reports/20260620-pg40-no-scope-role-affinity-preflight.md` |
| pairwise selector 预飞行 | `experiments/20260620-local-pg40-pairwise-selector-preflight/` |
| pairwise selector 报告 | `reports/20260620-pg40-pairwise-selector-preflight.md` |
| pairwise selector 五行结果 | `experiments/20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b/` |
| pairwise selector 五行报告 | `reports/20260620-pg40-pairwise-selector-limit5.md` |
| 契约回收检查 | `experiments/20260619-local-sseac-v0-pg40-contract-check/` |
| direct routing 预飞行 | `experiments/20260619-local-pg40-direct-routing-preflight/` |
| direct routing 结果 | `experiments/20260619-a8002-pg40-direct-routing-limit5-qwen25-14b/` |
| 状态报告 | `reports/20260619-hsa-pg40-a8002-small-run-status.md` |
| direct routing 预飞行报告 | `reports/20260619-pg40-direct-routing-preflight.md` |
| direct routing 结果报告 | `reports/20260619-pg40-direct-routing-limit5.md` |
| 最新解释报告 | `reports/20260619-pg40-sseac-limit5-gpu7-rerun.md` |
| 单卡契约报告 | `reports/20260619-pg40-sseac-cardunit-limit5.md` |
| 角色计划报告 | `reports/20260619-pg40-sseac-roleplan-limit5.md` |
| 运行脚本 | `scripts/run_sseac_v0_pg40_a8002.sh` |
| 通用运行器 | `scripts/run_sseac_v0_pg40_openai_compatible.py` |
| pairwise 运行脚本 | `scripts/run_pg40_pairwise_role_card_selector_a8002.sh` |
| pairwise 通用运行器 | `scripts/run_pg40_pairwise_role_card_selector_openai_compatible.py` |
| 编译器 | `scripts/compile_sseac_v0.py` |
| 评分器 | `scripts/score_sseac_pg40_compiled.py` |
