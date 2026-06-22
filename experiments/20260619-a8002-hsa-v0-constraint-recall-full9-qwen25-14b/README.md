# HSA-v0 constraint_recall 九行 A800_2 运行记录

日期：2026-06-19

## 状态

状态：`DIAGNOSTIC_BEHAVIOR_RESULT`
路线：`HSA-v0`
等级：诊断证据
本地路径：`experiments/20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b/`
远程路径：`/data/xuhaoming/yfy/research_workspace/experiments/20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b/`

这次运行在 `focused_recall` 后增加约束卡保留规则。目标是补回最后一个 base 行漏掉的 verified constraint card，同时保持 extra final cards 低于 `recall_sweep` 的 `19`。

## 启动记录

- 主机：`A800_2`
- 远程工作区：`/data/xuhaoming/yfy/research_workspace`
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- 服务模型名：`qwen2.5-14b-hsa-v0-sseac`
- 显卡：`7`
- 端口：`8081`
- 输入包：`experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl`
- 行数：`9`
- 温度：`0`
- 最大生成长度：`3072`
- 最大上下文长度：`8192`
- 显存比例：`0.75`
- 提示契约：`constraint_recall`

命令：

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=constraint_recall GPU_ID=7 PORT=8081 RUN_ID=20260619-a8002-hsa-v0-constraint-recall-full9-qwen25-14b LIMIT=0 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 RUN_TIMEOUT=1800 bash scripts/run_hsa_v0_sseac_a8002.sh
```

运行后 GPU 7 回到空闲。

## 结果摘要

| 路径 | 严格正确 | 原始行正确 | 扰动行正确 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_only | 5/9 | 1.0000 | 0.3333 | 0.8981 | 10 | 0.2222 |
| compiler | 8/9 | 0.6667 | 1.0000 | 0.7963 | 10 | 0.5556 |

## 读法

`constraint_recall` 没有把 strict 推到 `9/9`，但它是当前 HSA 最干净的 `8/9` 行：extra final cards 从 baseline 的 `8` 到 `10`，明显低于 `recall_sweep` 的 `19` 和 `focused_recall` 的 `12`。

唯一失败行仍是 `hiddenbench_evacuation_west_city` base。模型保留了 `hb01_shared_3`，但仍没有把 `hb01_hidden_2` 作为 final_decider 候选单元输出。下一步如果继续压 HSA，应该考虑非提示式的约束卡后置过滤或候选补全器。

## 关键产物

| 文件 | 用途 |
| --- | --- |
| `predictions.jsonl` | 模型原始结构输出 |
| `compiled_model_only.jsonl` | 编译前诊断态 |
| `compiled_compiler.jsonl` | hard executor 编译态 |
| `scores_model_only.jsonl` | 编译前 HSA 评分 |
| `scores_compiler.jsonl` | 编译后 HSA 评分 |
| `summary_model_only.md` | 编译前摘要 |
| `summary_compiler.md` | 编译后摘要 |
| `paired_delta_full9.md` | 成对差摘要 |

