# SSEAC-v0 PG40 单卡候选契约五行记录

日期：2026-06-19

## 状态

`DIAGNOSTIC_BEHAVIOR_RESULT`

这次运行在上一轮 true prompt limit5 的基础上，只改 PG40 提示词中的 candidate unit contract：每个 candidate unit 只允许一个 card，并按 role 分别排序。compiler、scorer、packet 保持不变。

## 目的

验证上一轮的主要失败面是否来自多卡 candidate unit 被 over-budget 整组拒绝。成功信号是 coverage 回升、budget pass 继续为 `1.0`、utility 上升，并且 strict 至少出现正例。

## 启动记录

- 主机：`A800_2` (`10-116-90-20`)
- 远程工作区：`/data/xuhaoming/yfy/research_workspace`
- 本地镜像：`experiments/20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b/`
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- 服务模型名：`qwen2.5-14b-sseac-v0-pg40`
- 显卡：`7`
- 端口：`8077`
- 输入包：`experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl`
- 原始 PG40 包：`experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl`
- 本次运行输入包：`packet_limit5.jsonl`
- 行数：`5`
- 温度：`0`
- 最大生成长度：`2048`
- 最大上下文长度：`8192`
- 显存利用：`0.75`

命令：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=8077 RUN_ID=20260619-a8002-sseac-v0-pg40-limit5-cardunit-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 RUN_TIMEOUT=1800 bash scripts/run_sseac_v0_pg40_a8002.sh
```

## 结果摘要

| 条件 | Strict | Coverage | Precision | Budget pass | Utility | Raw utility | Exact role |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| structured no compiler | 0/5 | 0.8148 | 0.6667 | 0.0000 | 0.1803 | 1.2189 | 0.2333 |
| compiler | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.8155 | 0.8155 | 0.6000 |

成对均值：

| 指标 | 编译前 | 编译后 | 差值 |
| --- | ---: | ---: | ---: |
| strict | 0.0000 | 0.2000 | 0.2000 |
| coverage | 0.8167 | 0.6500 | -0.1667 |
| precision | 0.6600 | 0.8167 | 0.1567 |
| budget pass | 0.0000 | 1.0000 | 1.0000 |
| utility | 0.1932 | 0.8051 | 0.6118 |
| exact role | 0.2333 | 0.6000 | 0.3667 |

## 与上一轮比较

上一轮 true prompt compiled 是 `0/5`，coverage `0.3704`，utility `0.4635`。单卡契约后 compiled 变为 `1/5`，coverage `0.6667`，utility `0.8155`。

这说明上一轮的失败诊断基本成立：多卡 unit 是重要瓶颈。把 unit 改成 card-level 后，executor 不再把整组必要证据一起剪掉。

## 仍然失败在哪里

五行里只有 `pg_003__seed_1` 严格通过。其余四行仍然有 role-specific missing / extra：

- `pg_000__seed_1`：reviewer 漏 `f5`，多收 `f6`。
- `pg_000__seed_42`：reviewer 漏 `f2`、`f3`，多收 `f1`。
- `pg_002__seed_1`：dispatcher 收了高成本 `f4`，漏 `f3`、`f5`、`f6`；reviewer 漏 `f5`。
- `pg_002__seed_42`：reviewer 漏 `f6`、`f7`。

当前问题已经从“候选单元太粗”推进到“角色语义排序和共享卡选择仍不准”。

## 证据等级

诊断证据。

它支持的窄判断是：PG40 上 card-level candidate unit contract 明显改善 SSEAC proposal，使 compiler 的预算修复不再严重牺牲 coverage。

它暂不支持的判断：

- 不能说 PG40 方法行已达标。
- 不能扩成 full40 主表行。
- 不能说已经超过 source-ledger 14B compiled 或 utility-density greedy。

## 关键产物

| 文件 | 用途 |
| --- | --- |
| `predictions.jsonl` | 模型原始结构输出 |
| `compiled_model_only.jsonl` | 编译前诊断态 |
| `compiled_compiler.jsonl` | hard executor 编译态 |
| `scores_model_only.jsonl` | 编译前 PG40 评分 |
| `scores_compiler.jsonl` | 编译后 PG40 评分 |
| `summary_model_only.md` | 编译前摘要 |
| `summary_compiler.md` | 编译后摘要 |
| `paired_delta_limit5.md` | 成对差摘要 |

## 下一步

暂不扩 full40。下一步应把 role-specific semantic ranking 做成显式输出：

- 每个 role 先给出预算内草案；
- 要求解释为什么放弃每个未选但可见的 support card；
- 对 shared setup card 给出“必要 / 背景 / 可省略”三类判断；
- 复跑同五行，目标是 strict 超过 `1/5`，utility 接近或超过旧 source-ledger 14B compiled 的 `0.8707`。

