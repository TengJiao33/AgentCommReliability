# SSEAC-v0 PG40 角色计划契约五行记录

日期：2026-06-19

## 状态

`DIAGNOSTIC_NEGATIVE_RESULT`

这次运行在单卡候选契约基础上，给模型增加 `role_plans`：每个角色先写预算内草案，并把每个可见 verified support card 标成 `select`、`backup` 或 `omit`。目的在于测试显式角色内排序是否能继续改善 PG40 五行结果。

结论很直接：没有改善。compiled strict 仍是 `1/5`，utility 从单卡契约的 `0.8155` 降到 `0.7811`，exact target role 从 `0.6000` 降到 `0.5000`。这个契约应作为诊断性负结果保留，不能作为当前 Ours。

## 目的

验证 card-level unit 之后的剩余瓶颈是否可以通过显式 role plan 修复。成功信号是 strict 超过 `1/5`，utility 接近或超过旧 source-ledger 14B compiled 的 `0.8707`，并保持 budget pass `1.0000`。

失败信号是 strict 不升、utility 低于 card-unit、或 role plan 只增加解释结构但没有改善 candidate unit 的实际排序。本次命中失败信号。

## 启动记录

- 主机：`A800_2` (`10-116-90-20`)
- 远程工作区：`/data/xuhaoming/yfy/research_workspace`
- 本地镜像：`experiments/20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b/`
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- 服务模型名：`qwen2.5-14b-sseac-v0-pg40`
- 显卡：`7`
- 端口：`8078`
- 输入包：`experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl`
- 原始 PG40 包：`experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl`
- 本次运行输入包：`packet_limit5.jsonl`
- 行数：`5`
- 温度：`0`
- 最大生成长度：`3072`
- 最大上下文长度：`8192`
- 显存利用：`0.75`

实际运行命令：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=8078 RUN_ID=20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 RUN_TIMEOUT=1800 bash scripts/run_sseac_v0_pg40_a8002.sh
```

归档后，runner 已改成显式契约参数。若要复现这条角色计划结果，应使用：

```bash
PROMPT_CONTRACT=roleplan GPU_ID=7 PORT=8078 RUN_ID=20260619-a8002-sseac-v0-pg40-limit5-roleplan-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 RUN_TIMEOUT=1800 bash scripts/run_sseac_v0_pg40_a8002.sh
```

默认 `PROMPT_CONTRACT` 已恢复为 `cardunit`，避免后续误用这个已退休契约。

## 结果摘要

| 条件 | Strict | Coverage | Precision | Budget pass | Utility | Raw utility | Exact role |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| structured no compiler | 0/5 | 0.7778 | 0.6774 | 0.0000 | 0.2918 | 1.1330 | 0.3000 |
| compiler | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.7811 | 0.7811 | 0.5000 |

成对均值：

| 指标 | 编译前 | 编译后 | 差值 |
| --- | ---: | ---: | ---: |
| strict | 0.0000 | 0.2000 | +0.2000 |
| coverage | 0.7714 | 0.6381 | -0.1333 |
| precision | 0.6533 | 0.7833 | +0.1300 |
| budget pass | 0.0000 | 1.0000 | +1.0000 |
| utility | 0.2745 | 0.7761 | +0.5017 |
| exact role | 0.3000 | 0.5000 | +0.2000 |

## 与单卡契约比较

| 条件 | Strict | Coverage | Precision | Budget pass | Utility | Exact role |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| card-unit compiled | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.8155 | 0.6000 |
| role-plan compiled | 1/5 | 0.6667 | 0.8571 | 1.0000 | 0.7811 | 0.5000 |

行级变化：

| 行 | 单卡 strict | 角色计划 strict | 单卡 utility | 角色计划 utility | 读法 |
| --- | ---: | ---: | ---: | ---: | --- |
| `pg_000__seed_1` | 0 | 0 | 0.9500 | 0.9500 | 没变，reviewer 仍漏 `f5`、多收 `f6` |
| `pg_000__seed_42` | 0 | 0 | 0.7429 | 0.5143 | 变差，reviewer 漏 `f2/f3`，多收 `f1` |
| `pg_002__seed_1` | 0 | 0 | 0.5882 | 0.5882 | 没变，dispatcher 仍漏 `f3/f5/f6` |
| `pg_002__seed_42` | 0 | 1 | 0.7442 | 1.0000 | 修好一行 |
| `pg_003__seed_1` | 1 | 0 | 1.0000 | 0.8281 | 打坏一行，reviewer 漏 `f1` |

## 机制诊断

模型确实输出了 `role_plans`，且五行都成功解析，所以这不是执行失败或解析失败。

问题在于 role plan 没有稳定转化成更好的 candidate unit 排序。它修好了 `pg_002__seed_42`，但同时破坏了原本通过的 `pg_003__seed_1`，并在 `pg_000__seed_42` 明显降低 coverage 与 utility。更具体地说，模型会把共享/setup 卡解释成背景或别的角色事项，从而在紧预算下漏掉最终必须出现的低成本卡。

## 证据等级

诊断性负结果。

它支持的窄判断是：在当前 PG40 五行上，额外要求模型写角色计划没有带来可用收益，反而增加了语义解释负担和选择不稳定性。

它不推翻 SSEAC。它只退休这一版 `roleplan` 提示契约。当前 PG40 最好行为结果仍是 `true_sseac_cardunit_compiler_limit5_qwen25_14b`。

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

PG40 暂不扩 full40，也不继续堆解释型 prompt。若继续压 PG40，应换成更可审计的排序机制，例如对单卡候选做预算感知重排或成对偏好排序；近期更高性价比的动作是回到 HSA-v0，先修候选证据召回。

