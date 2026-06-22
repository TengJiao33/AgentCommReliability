# PG40 Direct Routing Limit5

日期：2026-06-19

## 核心判断

direct routing 五行已经跑完，结果很弱：strict `0/5`，coverage `0.1481`，precision `0.1481`，budget pass `0.4000`，utility `0.0987`。这条线补上了公开切片主表的直接提示基线，但没有形成方法结果。

这不是解析失败。五行全部 `status=ok`，模型都返回了可解析 JSON。主要失败来自角色关系判断错误、拒掉必要碎片、以及三行预算超限。

## 运行信息

| 项 | 内容 |
| --- | --- |
| remote | `A800_2:/data/xuhaoming/yfy/research_workspace` |
| run id | `20260619-a8002-pg40-direct-routing-limit5-qwen25-14b` |
| model | `Qwen2.5-14B-Instruct` |
| served model | `qwen2.5-14b-pg40-direct-routing` |
| GPU | `7` |
| port | `8079` |
| packet | `experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl` |
| limit | `5` |
| max model len | `8192` |
| max tokens | `2048` |
| temperature | `0` |

## 命令

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=8079 RUN_ID=20260619-a8002-pg40-direct-routing-limit5-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=2048 bash scripts/run_pg40_direct_routing_a8002.sh
```

第一次模型运行完成后，评分阶段暴露一个评测接缝：direct runner 保存的是已解析 JSON 对象，旧 tight-budget scorer 只接受字符串。已修复 `scripts/score_perspectivegap_tight_budget.py`，之后复用同一预测文件重评成功，没有重新调用模型。

## 结果

| 指标 | 数值 |
| --- | ---: |
| strict | `0/5` |
| required coverage | `0.1481` |
| boundary precision | `0.1481` |
| budget pass | `0.4000` |
| budget overrun | `6.8000` |
| distractor leakage | `0.0000` |
| reject recall | `1.0000` |
| needed rejected | `1.2000` |
| utility | `0.0987` |
| raw utility | `0.1845` |
| exact target role | `0.0000` |

## 逐行诊断

| row | 主要失败 |
| --- | --- |
| `pg_000 seed 1` | coder 漏 `f3/f5`，多收 `f1/f6/f7`；reviewer 漏共享关键 `f5`；必要 `f5` 被拒 |
| `pg_000 seed 42` | coder 漏 `f6/f7`；reviewer 漏 `f3`；必要 `f6` 被拒 |
| `pg_002 seed 1` | dispatcher、coder、reviewer 多数角色错配；reviewer 超预算 |
| `pg_002 seed 42` | 三个角色都漏关键碎片；reviewer 超预算；必要 `f6/f7` 被拒 |
| `pg_003 seed 1` | 三个角色都超预算或错配；必要 `f6` 被拒 |

## 产物

| 文件 | 内容 |
| --- | --- |
| `packet_limit5.jsonl` | 五行运行包 |
| `predictions_direct.jsonl` | 模型输出 |
| `scores_direct.jsonl` | 逐行评分 |
| `summary_direct.md` | 文本摘要 |
| `summary_direct.json` | 机器摘要 |
| `run.log` | 远程运行日志 |
| `vllm.log` | 临时模型服务日志 |

## 对下一步的影响

direct 行补齐后，PG40 五行主表更清楚：直接提示 `0/5` 且 utility 很低，结构化单卡 compiled 是 `1/5`、utility `0.8155`，旧 source-ledger 14B compiled 是 `11/40`、utility `0.8707`，透明贪心是 `25/40`、utility `0.9825`。

下一步不该扩 direct。PG40 后续应压预算感知单卡重排或成对排序器，目标是超过 card-unit compiled 的 `1/5` 和 utility `0.8155`，再看是否接近 source-ledger 14B compiled。
