# HSA-v0 focused_recall 九行 A800_2 运行记录

日期：2026-06-19

## 状态

状态：`DIAGNOSTIC_BEHAVIOR_RESULT`
路线：`HSA-v0`
等级：诊断证据
本地路径：`experiments/20260619-a8002-hsa-v0-focused-recall-full9-qwen25-14b/`
远程路径：`/data/xuhaoming/yfy/research_workspace/experiments/20260619-a8002-hsa-v0-focused-recall-full9-qwen25-14b/`

这次运行在 `recall_sweep` 后继续收窄提示契约。目标是保持 `8/9` 严格正确，同时减少 `recall_sweep` 带来的多余最终卡片。

## 启动记录

- 主机：`A800_2`
- 远程工作区：`/data/xuhaoming/yfy/research_workspace`
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- 服务模型名：`qwen2.5-14b-hsa-v0-sseac`
- 显卡：`7`
- 端口：`8080`
- 输入包：`experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl`
- 行数：`9`
- 温度：`0`
- 最大生成长度：`3072`
- 最大上下文长度：`8192`
- 显存比例：`0.75`
- 提示契约：`focused_recall`

命令：

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=focused_recall GPU_ID=7 PORT=8080 RUN_ID=20260619-a8002-hsa-v0-focused-recall-full9-qwen25-14b LIMIT=0 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 RUN_TIMEOUT=1800 bash scripts/run_hsa_v0_sseac_a8002.sh
```

运行后 GPU 7 回到空闲。

## 结果摘要

| 路径 | 严格正确 | 原始行正确 | 扰动行正确 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_only | 5/9 | 1.0000 | 0.3333 | 0.9167 | 12 | 0.2222 |
| compiler | 8/9 | 0.6667 | 1.0000 | 0.8148 | 12 | 0.5556 |

## 读法

`focused_recall` 保持了 `recall_sweep` 的 compiler `8/9`，并把 extra final cards 从 `19` 降到 `12`。它没有修好最后一个 base 行：`hiddenbench_evacuation_west_city` 仍因缺 `hb01_hidden_2` 退回 `insufficient_evidence`。

这个结果说明 focused filtering 有效，但过度收窄会漏掉某些 verified 约束卡。

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

