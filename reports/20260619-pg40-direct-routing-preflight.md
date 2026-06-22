# PG40 直接路由基线预飞行

日期：2026-06-19

现状修正：远程五行已经完成，结果见 `reports/20260619-pg40-direct-routing-limit5.md`。

## 核心判断

PG40 公开切片主表原本缺一条同模型直接提示基线。本轮补出可执行的 direct routing 路线：五行干跑通过，提示没有泄漏金标、候选集合、效用值或 oracle 字段；后续已经在 A800_2 的 GPU 7 上完成五行运行。

这条线只补基线。它不会证明 SSEAC 有效，但会让公开主表更像一张可对外解释的表：direct、source-ledger、structured no compiler、compiled、transparent greedy 和 oracle 可以放到同一评价口径里。

## 做了什么

新增脚本：

| 脚本 | 用途 |
| --- | --- |
| `scripts/run_pg40_direct_routing_openai_compatible.py` | 把 PG40 tight-budget row 渲染成直接路由提示，并调用兼容接口 |
| `scripts/run_pg40_direct_routing_a8002.sh` | 在 A800_2 上启动 Qwen2.5-14B，默认 GPU 7，跑 direct 五行并评分 |

本地预飞行产物：

| 产物 | 路径 |
| --- | --- |
| 运行记录 | `experiments/20260619-local-pg40-direct-routing-preflight/README.md` |
| 五行干跑提示 | `experiments/20260619-local-pg40-direct-routing-preflight/dry_run_prompts_limit5.jsonl` |

## 门禁结果

Python 语法检查通过。五行提示干跑通过，提示长度从 `4255` 到 `8091` 字符，最大样本仍低于当前 PG40 运行的模型长度设置。

泄漏扫描无命中。提示只包含 `evaluation_id`、`scenario_id`、角色、角色预算、碎片编号、来源编号、成本和碎片文本；没有 `reference_need_sets`、`candidate_need_sets`、`role_utilities`、`target_needed_by`、`gold`、`oracle`、`required_slots` 或 `acceptable_card_ids`。

## 为什么这一步重要

当前 PG40 已有强透明基线 `25/40`、旧 source-ledger 14B compiled `11/40`、单卡 compiled 五行 `1/5`。但缺少同一模型在同一切片上直接做角色路由的结果。没有 direct 行，主表会被质疑：我们只证明了结构化方法和旧机制的差别，没有说明普通直接提示在这把尺子上处于什么位置。

## 下一步

先跑五行 direct：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=<free-port> RUN_ID=20260619-a8002-pg40-direct-routing-limit5-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=2048 bash scripts/run_pg40_direct_routing_a8002.sh
```

如果 direct 明显高于 card-unit compiled，SSEAC 当前方法优势会更弱，下一步必须优先做预算感知单卡重排或成对排序器。如果 direct 也很低，PG40 主问题会更集中到受约束信息路由本身；我们再看 compiled 相对 direct 是否有增益。
