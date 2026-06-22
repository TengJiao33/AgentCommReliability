# HSA-v0 SSEAC 九行 A800_2 运行记录

日期：2026-06-19

## 状态

状态：`DIAGNOSTIC_PILOT_COMPLETE`
路线：`HSA-v0`
等级：诊断证据
本地路径：`experiments/20260619-a8002-hsa-v0-sseac-full9-qwen25-14b/`
远程路径：`/data/xuhaoming/yfy/research_workspace/experiments/20260619-a8002-hsa-v0-sseac-full9-qwen25-14b/`

这次运行把 HSA-v0 从三行小样本扩到完整 9 行。它用于检查同一批模型输出在 `model_only` 与 `compiler` 两种路径下是否维持机制差。

## 启动记录

- 主机：`A800_2` (`10-116-90-20`)
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- 服务模型名：`qwen2.5-14b-hsa-v0-sseac`
- 本次实际显卡：`2`
- 后续默认显卡：`7`
- 端口：`8075`
- 输入包：`experiments/20260618-local-hsa-v0-sseac-adapter/hsa_v0_packet.jsonl`
- 本次运行输入包：`packet_limit0.jsonl`
- 行数：`9`
- 温度：`0`
- 最大生成长度：`2048`
- 最大上下文长度：`8192`
- 显存比例：`0.75`

命令：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=2 PORT=8075 RUN_ID=20260619-a8002-hsa-v0-sseac-full9-qwen25-14b LIMIT=0 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 RUN_TIMEOUT=1800 bash scripts/run_hsa_v0_sseac_a8002.sh
```

临时 vLLM 服务已通过脚本清理路径退出。运行后检查显示 GPU 2 回到空闲，未发现本项目残留服务。

## 主要结果

同一批模型输出，两条执行路径：

| 路径 | 严格正确 | 原始行正确 | 扰动行正确 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `model_only` | `3/9` | `0.6667` | `0.1667` | `0.8148` | `8` | `0.5556` |
| `compiler` | `7/9` | `0.3333` | `1.0000` | `0.7130` | `8` | `0.7778` |

## 解释

硬准入路径的主要收益在扰动行。6 个扰动行全部被推到 `insufficient_evidence`，其中包括范围越界、隔离证据和未验证证据导致的错误承诺。这说明硬准入规则确实能把模型倾向作答的情况挡住。

原始行暴露出候选证据召回瓶颈。3 个原始行里只有 `hiddenbench_emergency_supply_drop` 被硬准入路径答对；另外两个原始行中，模型最终答案本身正确，但候选证据少提了一张必需卡片，硬准入按充分性规则保守退回 `insufficient_evidence`。

具体缺口：

| 行 | 期望答案 | 模型答案 | 硬准入结果 | 缺失证据 |
| --- | --- | --- | --- | --- |
| `hiddenbench_conference_relocation__hb11_base_verified_role_scoped__hsa_v0` | `School Gym` | `School Gym` | `insufficient_evidence` | `hb11_shared_3` |
| `hiddenbench_evacuation_west_city__hb01_base_verified_role_scoped__hsa_v0` | `West City` | `West City` | `insufficient_evidence` | `hb01_hidden_2` |

这个结果支持“模型提案 + 硬执行”的诊断路线，也指出下一步要提高候选证据召回。执行器本身在防错上表现强，但充分放行依赖模型把必需证据提全。

## 产物

- 预测：`predictions.jsonl`
- 模型直出编译产物：`compiled_model_only.jsonl`
- 硬准入编译产物：`compiled_compiler.jsonl`
- 模型直出评分：`scores_model_only.jsonl`
- 硬准入评分：`scores_compiler.jsonl`
- 模型直出摘要：`summary_model_only.md`
- 硬准入摘要：`summary_compiler.md`
- 日志：`run.log`, `vllm.log`, `runner.stdout.log`

## 下一步

HSA 下一步应围绕候选证据召回做最小改动，例如提示模型必须列全每个被排除选项的阻断证据，再复跑 9 行。后续远程运行默认使用 GPU 7；前面的卡只在用户明确允许时使用。
