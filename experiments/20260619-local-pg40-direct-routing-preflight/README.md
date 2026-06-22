# PG40 Direct Routing Preflight

日期：2026-06-19

现状修正：远程五行已经完成，结果见 `experiments/20260619-a8002-pg40-direct-routing-limit5-qwen25-14b/README.md`。

## 目的

这次预飞行对应公开切片主表里的 `direct` 行。它让同一个 Qwen2.5-14B 服务在 PG40 tight-budget 五行上直接把碎片分配给角色，再用同一个 tight-budget scorer 评价。

## 实验门禁

| 项 | 内容 |
| --- | --- |
| purpose | 补同模型、同预算、同评分器下的直接提示基线 |
| unit | 一个 PG40 tight-budget row |
| primary contrast | direct routing vs source-ledger 14B compiled vs card-unit compiled vs transparent greedy |
| secondary contrasts | budget pass、coverage、precision、utility、exact role |
| success signal | direct 行形成可解析、可评分的五行结果，能放入公开切片主表 |
| failure signal | JSON 解析失败、预算崩、低于当前结构化行且无法诊断 |
| invalidation conditions | 提示泄漏 `reference_need_sets`、`candidate_need_sets`、`role_utilities`、`target_needed_by`、oracle 或 gold 字段 |
| packet | `experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl` |
| runner | `scripts/run_pg40_direct_routing_openai_compatible.py` |
| remote wrapper | `scripts/run_pg40_direct_routing_a8002.sh` |
| dry-run prompts | `experiments/20260619-local-pg40-direct-routing-preflight/dry_run_prompts_limit5.jsonl` |

## 本地检查

Python 语法检查通过：

```powershell
python -m py_compile scripts\run_pg40_direct_routing_openai_compatible.py scripts\score_perspectivegap_tight_budget.py
```

五行提示干跑通过：

```powershell
python scripts\run_pg40_direct_routing_openai_compatible.py --packet experiments\20260618-local-perspectivegap-tight-budget-v0\tight_budget_rotated20.jsonl --limit 5 --dry-run-prompts-out experiments\20260619-local-pg40-direct-routing-preflight\dry_run_prompts_limit5.jsonl
```

输出：

```json
{
  "rows": 5,
  "dry_run_prompts_out": "experiments\\20260619-local-pg40-direct-routing-preflight\\dry_run_prompts_limit5.jsonl"
}
```

泄漏扫描无命中。扫描词包括：

```text
reference_need_sets
candidate_need_sets
role_utilities
role_oracle
target_needed_by
needed_by
visibility_gold
source_scope_ledger
utility_by_recipient
tight_budget_policy
oracle
gold
required_slots
acceptable_card_ids
```

五行提示规模：

| row | roles | fragments | prompt chars |
| --- | ---: | ---: | ---: |
| `pg_000 seed 1` | 2 | 7 | 4550 |
| `pg_000 seed 42` | 2 | 7 | 4255 |
| `pg_002 seed 1` | 3 | 7 | 6717 |
| `pg_002 seed 42` | 3 | 7 | 6422 |
| `pg_003 seed 1` | 3 | 9 | 8091 |

本地 `bash -n` 没有完成，原因是本机 WSL 初始化卡在代理提示处；后续已在 A800_2 上完成 `bash -n scripts/run_pg40_direct_routing_a8002.sh`。

## 复现命令

远程默认使用 GPU 7：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=<free-port> RUN_ID=20260619-a8002-pg40-direct-routing-limit5-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=2048 bash scripts/run_pg40_direct_routing_a8002.sh
```

跑完后拉回：

```powershell
scp -r A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260619-a8002-pg40-direct-routing-limit5-qwen25-14b experiments/
```

## 读数方式

direct 行只承担公开切片主表基线角色。它需要和以下行同表比较：

| 行 | 当前状态 |
| --- | --- |
| direct routing | `0/5`，utility `0.0987` |
| source-ledger 14B compiled | `11/40`，utility `0.8707` |
| structured no compiler card-unit | `0/5`，utility `0.1803` |
| card-unit compiled | `1/5`，utility `0.8155` |
| role-plan compiled | `1/5`，utility `0.7811`，已退休 |
| transparent greedy | `25/40`，utility `0.9825` |
| oracle | `40/40` |

## 当前状态

预飞行通过，并已被远程 GPU7 五行模型输出吸收。该分支只补主表基线，不代表方法改进。
