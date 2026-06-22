# PG40 Pairwise Role-Card Selector Preflight

日期：2026-06-20

## 状态

`PAIRWISE_SELECTOR_LAUNCH_PREFLIGHT_READY`

这是 pairwise role-card selector 的本地预飞行。它不调用模型、不烧 GPU，只材料化 full40 prompt、审计禁用字段、验证输出 JSON 能接入现有 SSEAC compiler 和 PG40 scorer。

## Preflight Contract

purpose:

把上一轮 no-scope 规则 selector 的负结果推进成一个可跑的模型驱动 selector：模型逐对判断 `role, card -> assign`，脚本把 assign pairs 转成 SSEAC `candidate_units`，再由 deterministic budget prune / compiler / scorer 读数。

unit:

一个 PG40/SSEAC packet row。模型请求粒度是一个 row，模型内部判断所有 role-card pairs，输出稀疏 assignments。

primary_contrast:

后续真跑的 `pairwise_role_card_selector_compiler` vs `no_scope_hybrid_budget_pruned_model_only` 和 `source_ledger_14b_scope_project_cost_rank_pruned_full40`。

secondary_contrasts:

direct routing、source-ledger 14B compiled、eligible_cheapest、utility_density_greedy、oracle。

success_signal:

full40 上超过 scope-projection 诊断的 `17/40`、utility `0.8845`，并且 prompt / runner 不读 `recipient_scope`、need sets 或 utility gold。

failure_signal:

parse 失败、assignment 太稀导致 coverage 崩、assignment 太宽导致 budget / rejected 噪声、或结果低于 source-ledger 14B compiled。

invalidation_conditions:

prompt 或 runner 读取 `recipient_scope`、`required_slots`、`acceptable_card_ids`、`expected_final_decision`、`reference_need_sets`、`candidate_need_sets`、`role_utilities`、`needed_by`、`eligible_by`、`target_needed_by`、`utility_by_recipient`、`visibility_gold`、`source_scope_ledger`、`oracle`、`gold` 或 `distractor` 字段；parser 不能稳定抽取 JSON；compiler/scorer 路径不兼容。

expected_artifacts:

本目录下 dry-run prompts、summary、schema smoke；脚本 `scripts/run_pg40_pairwise_role_card_selector_openai_compatible.py` 和 `scripts/run_pg40_pairwise_role_card_selector_a8002.sh`；解释报告 `reports/20260620-pg40-pairwise-selector-preflight.md`。

## 新脚本

| 脚本 | 用途 |
| --- | --- |
| `scripts/run_pg40_pairwise_role_card_selector_openai_compatible.py` | 生成 pairwise prompt，调用 OpenAI-compatible API，把模型 assignments 转成 SSEAC predictions |
| `scripts/run_pg40_pairwise_role_card_selector_a8002.sh` | A800_2 GPU7 包装入口：启动 vLLM、运行 selector、compile、score |

## Prompt 可见字段

```text
packet_id
roles
role_budgets
source_cards.card_id
source_cards.content
source_cards.cost
```

禁用字段见上方 invalidation conditions。full40 dry-run prompt 扫描禁用词为 `0/40` 命中。

## 本地检查

Python 语法检查通过：

```powershell
python -m py_compile scripts\run_pg40_pairwise_role_card_selector_openai_compatible.py scripts\compile_sseac_v0.py scripts\score_sseac_pg40_compiled.py
```

full40 dry-run prompt：

```powershell
python scripts\run_pg40_pairwise_role_card_selector_openai_compatible.py `
  --packet experiments\20260618-local-sseac-v0-pg40-adapter\sseac_pg40_packet.jsonl `
  --dry-run-prompts-out experiments\20260620-local-pg40-pairwise-selector-preflight\dry_run_prompts_full40.jsonl
```

输出摘要：

```json
{
  "rows": 40,
  "leak_flagged_rows": 0,
  "max_prompt_chars": 9876,
  "min_prompt_chars": 3570,
  "avg_prompt_chars": 7607.7
}
```

full40 prompt 尺寸：

| 指标 | 值 |
| --- | ---: |
| rows | 40 |
| leak flagged rows | 0 |
| roles per row | 2-6 |
| cards per row | 7-13 |
| prompt chars | 3570-9876 |

Schema smoke 已通过。一个不含金标信息的假 pairwise assignment 能写成 SSEAC prediction，并通过：

```text
compile_sseac_v0.py --mode model_only
compile_sseac_v0.py --mode compiler
score_sseac_pg40_compiled.py
```

注意：schema smoke 只验证管道兼容，不是行为结果。

本机 `bash -n scripts/run_pg40_pairwise_role_card_selector_a8002.sh` 超时，和此前 WSL / bash 初始化卡住一致。远程运行前必须在 A800_2 上执行 `bash -n`。

## 远程真跑建议

先跑同五行，不直接 full40：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=<free-port> RUN_ID=20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 bash scripts/run_pg40_pairwise_role_card_selector_a8002.sh
```

跑完后读两条：

| 条件 | 用途 |
| --- | --- |
| `summary_model_only.md` | 纯 model proposal 的 no-scope 读数 |
| `summary_compiler.md` | hard scope / budget gate 后的读数 |

只有五行超过 card-unit compiled 的 `1/5`、utility `0.8155`，并且 parse / budget / rejected 噪声可控，才考虑 full40。
