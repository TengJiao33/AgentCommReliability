# SSEAC-v0 PG40 五行 GPU7 重跑记录

日期：2026-06-19

## 状态

`DIAGNOSTIC_BEHAVIOR_RESULT`

这次运行产生了完整模型预测、编译产物、评分和成对差。它是五行小样本诊断，不能作为主表胜利或真负结果。

## 目的

验证 `PG40 tight-budget` 上 true SSEAC prompt 是否能稳定输出结构化 candidate units，并检查 deterministic compiler 是否带来可解释的预算、精度或效用变化。

## 启动记录

- 主机：`A800_2` (`10-116-90-20`)
- 远程工作区：`/data/xuhaoming/yfy/research_workspace`
- 本地镜像：`experiments/20260619-a8002-sseac-v0-pg40-limit5-gpu7-rerun-qwen25-14b/`
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- 服务模型名：`qwen2.5-14b-sseac-v0-pg40`
- 显卡：`7`
- 端口：`8076`
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
GPU_ID=7 PORT=8076 RUN_ID=20260619-a8002-sseac-v0-pg40-limit5-gpu7-rerun-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 RUN_TIMEOUT=1800 bash scripts/run_sseac_v0_pg40_a8002.sh
```

## 结果摘要

| 条件 | Strict | Coverage | Precision | Budget pass | Utility | Raw utility | Exact role |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| structured no compiler | 0/5 | 0.7778 | 0.6562 | 0.0000 | 0.1803 | 1.1717 | 0.2333 |
| compiler | 0/5 | 0.3704 | 0.8333 | 1.0000 | 0.4635 | 0.4635 | 0.3333 |

成对均值：

| 指标 | 编译前 | 编译后 | 差值 |
| --- | ---: | ---: | ---: |
| strict | 0.0000 | 0.0000 | 0.0000 |
| coverage | 0.7881 | 0.4167 | -0.3714 |
| precision | 0.6533 | 0.6833 | 0.0300 |
| budget pass | 0.0000 | 1.0000 | 1.0000 |
| utility | 0.1932 | 0.5345 | 0.3412 |
| exact role | 0.2333 | 0.3333 | 0.1000 |

## 机制诊断

执行器修复了预算：`budget_pass` 从 `0.0000` 到 `1.0000`，`budget_overrun` 从 `8.6` 到 `0`。这说明 hard budget executor 在 PG40 上工作。

候选单元构造仍然粗糙。模型经常把多个高成本卡绑成一个 unit，executor 因 over-budget 拒绝整组，必要卡也被一起剪掉。例如 `pg_003__seed_1` 的三个候选单元全部超预算，编译后 coverage 变成 `0.0`。

当前 prompt 没有明显 distractor leak，解析也稳定：五行全有输出，compiler summary 是 `ok_rows=5`。主要断点已经从 schema 稳定性转到 unit construction 和 priority。

## 证据等级

诊断证据。

它支持的窄判断是：SSEAC compiler 能把过预算输出变成合法输出，但当前 true prompt 不足以产生强 PG40 方法行。

它暂不支持的判断：

- 不能说 SSEAC 在 PG40 上优于强透明基线。
- 不能扩成 full40 主表行。
- 不能把 `0/5` 写成机制真负结果，因为这只是五行小样本，且 failure mode 已定位到候选单元构造。

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

暂停 PG40 扩跑。下一步应改 candidate unit contract：

- 强制一个 unit 只含一个 card，除非明确声明原子依赖；
- 要求模型分别给每个 role 一个预算内候选排序；
- 编译器按 card-level priority 裁剪，而非直接拒绝超预算多卡 unit；
- 复跑同样五行，只比较这五行上的 coverage、budget pass、utility 和 strict。

