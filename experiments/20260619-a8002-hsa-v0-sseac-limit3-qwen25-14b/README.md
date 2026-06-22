# HSA-v0 SSEAC 三行 A800_2 运行记录

日期：2026-06-19

## 状态

`DIAGNOSTIC_PILOT_COMPLETE`

这次运行是 HSA-v0 的 3 行小样本诊断，不是主表结论。它用于检查同一批模型输出在 `model_only` 与 `compiler` 两种路径下是否出现机制差。

## 启动记录

- 主机：`A800_2` (`10-116-90-20`)
- 远程工作区：`/data/xuhaoming/yfy/research_workspace`
- 本地镜像：`experiments/20260619-a8002-hsa-v0-sseac-limit3-qwen25-14b/`
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- 服务模型名：`qwen2.5-14b-hsa-v0-sseac`
- 显卡：`7`
- 端口：`8074`
- 输入包：`experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl`
- 本次运行输入包：`packet_limit3.jsonl`
- 行数：`3`
- 温度：`0`
- 最大生成长度：`2048`
- 最大上下文长度：`16384`

命令：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=8074 RUN_ID=20260619-a8002-hsa-v0-sseac-limit3-qwen25-14b LIMIT=3 bash scripts/run_hsa_v0_sseac_a8002.sh
```

临时 vLLM 服务已通过脚本清理路径退出。运行后检查没有发现匹配的项目进程。

## 主要结果

同一批模型输出，两条执行路径：

| 路径 | 严格正确 | 原始行正确 | 扰动行正确 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `model_only` | `0/3` | `0.0000` | `0.0000` | `1.0000` | `7` | `0.0000` |
| `compiler` | `3/3` | `1.0000` | `1.0000` | `0.8333` | `7` | `0.6667` |

解释：

- Base row: model proposed useful evidence but set `final_decision=insufficient_evidence`; compiler used admitted evidence to recover `Warehouse C`.
- Perturbation rows: model proposed/committed toward `Warehouse C`; compiler blocked the final decision because one row used quarantined support and one row used support outside final scope.
- 有用信号不是“模型自己解决了 HSA-v0”。它没有。真正有用的是：模型产生了足够的候选证据，让硬准入规则能够改变下游决策。

## 产物

- 预测：`predictions.jsonl`
- 模型直出编译产物：`compiled_model_only.jsonl`
- 编译器产物：`compiled_compiler.jsonl`
- 模型直出评分：`scores_model_only.jsonl`
- 编译器评分：`scores_compiler.jsonl`
- 模型直出摘要：`summary_model_only.md`
- 编译器摘要：`summary_compiler.md`
- 日志：`run.log`, `vllm.log`, `runner.stdout.log`

## 注意

- 只有 `3` 行，不能当成主论文结果。
- 这个结果支持诊断/编译器路线，但还不足以支持宽泛的方法改进结论。
- `extra_final_card_count` remains `7`, so over-admission is not solved.
- 下一次运行应等 A800_2 真正空闲；其他用户活跃时不要重试。
