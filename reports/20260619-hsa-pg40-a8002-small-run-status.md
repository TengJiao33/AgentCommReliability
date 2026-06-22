# HSA/PG40 A800_2 Small-Run Status

日期：2026-06-19

## 结论

更新：HSA-v0 后续已经完成 full9 运行，见 `reports/20260619-hsa-v0-full9-a8002.md` 和 `experiments/20260619-a8002-hsa-v0-sseac-full9-qwen25-14b/README.md`。本报告保留为三行小样本和 PG40 显存失败的历史记录。

我们纠正了“缺端点”的说法：真实问题是新 PG40/HSA runner 没有接到项目惯用的 A800_2 包装运行路径。现在两个包装脚本已经补上并同步到远程：

- `scripts/run_hsa_v0_sseac_a8002.sh`
- `scripts/run_sseac_v0_pg40_a8002.sh`

随后只完成了 HSA-v0 `limit3` 小样本。PG40 `limit5` 因 A800_2 当时有人/任务占用导致 vLLM 启动 OOM，没有行为结果。按用户要求，暂时不再抢卡。

## HSA-v0 Limit3

运行编号：`20260619-a8002-hsa-v0-sseac-limit3-qwen25-14b`

同一批 Qwen2.5-14B 输出下：

| 路径 | 严格正确 | 原始行正确 | 扰动行正确 | 槽位召回 | 多余最终卡片 | 强制作答 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `model_only` | `0/3` | `0.0000` | `0.0000` | `1.0000` | `7` | `0.0000` |
| `compiler` | `3/3` | `1.0000` | `1.0000` | `0.8333` | `7` | `0.6667` |

有意义的读法：模型自己没有可靠决策；但模型给出的候选证据可以被硬准入规则转成正确下游状态。base 行中，模型说证据不足，compiler 推出正确答案 `Warehouse C`；两个扰动行中，模型倾向 `Warehouse C`，compiler 因隔离/范围约束挡回 `insufficient_evidence`。

这支持“模型提案 + 硬执行”的诊断/编译器路线，但样本太小，不能写成主结论。

## PG40 Limit5

运行编号：`20260619-a8002-sseac-v0-pg40-limit5-qwen25-14b`

状态：`EXECUTION_FAILURE_NO_BEHAVIOR_RESULT`

vLLM 已加载 Qwen2.5-14B 权重，但在 KV-cache 初始化时 CUDA OOM。原因是 GPU 当时已有占用且脚本默认 `--gpu-memory-utilization 0.90` 太激进。没有产生预测、编译或评分文件，因此不能读成方法失败。

## 当前停点

- 不继续使用 A800_2，除非确认机器空闲。
- 已把脚本改成支持 `GPU_MEMORY_UTILIZATION` 环境变量，默认降为 `0.80`。
- 下次重试 PG40 应在空卡上用更保守设置，例如 `GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192`。
