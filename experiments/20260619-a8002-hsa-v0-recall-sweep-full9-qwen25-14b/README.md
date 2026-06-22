# HSA-v0 recall_sweep 九行 A800_2 运行记录

日期：2026-06-19

## 状态

状态：`DIAGNOSTIC_BEHAVIOR_RESULT`
路线：`HSA-v0`
等级：诊断证据
本地路径：`experiments/20260619-a8002-hsa-v0-recall-sweep-full9-qwen25-14b/`
远程路径：`/data/xuhaoming/yfy/research_workspace/experiments/20260619-a8002-hsa-v0-recall-sweep-full9-qwen25-14b/`

这次运行在 HSA full9 baseline runner 基础上，只改提示契约为 `recall_sweep`：模型先扫描每个候选答案的支持、阻断和背景约束卡片，再输出单卡候选单元。compiler、scorer、packet 不变。

## 目的

上一轮 HSA full9 的两个 base 失败来自候选证据少提必需卡。成功信号是 base strict 提升、slot recall 提升、perturbation strict 保持 `1.0000`，并且 extra final cards 不接近 all-scoped 的 `24`。

## 启动记录

- 主机：`A800_2` (`10-116-90-20`)
- 远程工作区：`/data/xuhaoming/yfy/research_workspace`
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- 服务模型名：`qwen2.5-14b-hsa-v0-sseac`
- 显卡：`7`
- 端口：`8079`
- 输入包：`experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl`
- 本次运行输入包：`packet_limit0.jsonl`
- 行数：`9`
- 温度：`0`
- 最大生成长度：`3072`
- 最大上下文长度：`8192`
- 显存比例：`0.75`
- 提示契约：`recall_sweep`

命令：

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=recall_sweep GPU_ID=7 PORT=8079 RUN_ID=20260619-a8002-hsa-v0-recall-sweep-full9-qwen25-14b LIMIT=0 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 RUN_TIMEOUT=1800 bash scripts/run_hsa_v0_sseac_a8002.sh
```

运行后检查显示 GPU 7 回到空闲。

## 结果摘要

| 路径 | 严格正确 | 原始行正确 | 扰动行正确 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_only | 5/9 | 0.6667 | 0.5000 | 0.9259 | 19 | 0.0000 |
| compiler | 8/9 | 0.6667 | 1.0000 | 0.7963 | 19 | 0.3333 |

与上一轮 baseline compiler 对比：

| 条件 | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline compiler | 7/9 | 0.3333 | 1.0000 | 0.7130 | 8 | 0.7778 |
| recall_sweep compiler | 8/9 | 0.6667 | 1.0000 | 0.7963 | 19 | 0.3333 |

## 行级变化

| 行 | baseline strict | recall_sweep strict | 变化 |
| --- | ---: | ---: | --- |
| `hb10_base_verified_role_scoped` | 1 | 1 | 保持通过 |
| `hb10_b_hazard_quarantined` | 1 | 1 | 保持通过 |
| `hb10_c_enabler_no_final_scope` | 1 | 1 | 保持通过 |
| `hb11_base_verified_role_scoped` | 0 | 1 | 修好；召回 `hb11_shared_3` |
| `hb11_school_repair_quarantined` | 1 | 1 | 保持通过 |
| `hb11_library_fuel_no_final_scope` | 1 | 1 | 保持通过 |
| `hb01_base_verified_role_scoped` | 0 | 0 | 仍失败；召回 `hb01_hidden_2`，但漏 `hb01_shared_3`，且把 West City 判成 blocked |
| `hb01_west_bridge_unverified` | 1 | 1 | 保持通过 |
| `hb01_north_hill_split_scope_no_group_edge` | 1 | 1 | 保持通过 |

## 机制诊断

`recall_sweep` 的正面信号很明确：它把 HSA compiler strict 从 `7/9` 推到 `8/9`，base strict 从 `1/3` 推到 `2/3`，perturbation strict 保持 `6/6`。这说明证据扫描确实缓解了上一轮的漏召回问题。

主要边界也很明显：extra final cards 从 `8` 升到 `19`。它仍低于 all-scoped 的 `24`，但过度准入压力变大。当前失败行显示模型会把部分阻断卡错误归属到可行选项上，并漏掉最后一张支持卡 `hb01_shared_3`。

## 证据等级

诊断证据。

它支持的窄判断是：HSA 中候选证据召回是可被提示契约改善的，且硬准入仍能保护扰动行。

它暂不支持的判断：

- 不能写成主方法结论。
- 不能说明 HSA 已经过强对照；all-scoped 仍是 `9/9`，虽然 extra final cards 是 `24`。
- 不能忽视过度准入；`19` 张多余最终卡片会被审稿人直接质疑。

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

## 下一步

下一步不应继续单纯加宽召回。应该做一个更窄的 `focused_recall` 或排序过滤契约：保留单卡召回，但要求模型区分“所选答案的支持卡”和“其他答案的阻断卡”，减少被拒答案的普通支持卡进入 final_decider admitted state，同时纠正 blocker 归属。

