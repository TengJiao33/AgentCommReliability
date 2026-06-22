# SSEAC-v0 PG40 五行 A800_2 尝试记录

日期：2026-06-19

## 状态

`EXECUTION_FAILURE_NO_BEHAVIOR_RESULT`

这次尝试没有产生模型预测，不能解释为支持或反对 SSEAC-v0 的证据。

## 启动记录

- 主机：`A800_2` (`10-116-90-20`)
- 远程工作区：`/data/xuhaoming/yfy/research_workspace`
- 本地镜像：`experiments/20260619-a8002-sseac-v0-pg40-limit5-qwen25-14b/`
- 模型路径：`/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- 服务模型名：`qwen2.5-14b-sseac-v0-pg40`
- 显卡：`7`
- 端口：`8073`
- 输入包：`experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl`
- 本次运行输入包：`packet_limit5.jsonl`
- 计划行数：`5`
- 计划温度：`0`
- 计划最大生成长度：`2048`
- 最大上下文长度：`16384`

命令：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=8073 RUN_ID=20260619-a8002-sseac-v0-pg40-limit5-qwen25-14b LIMIT=5 bash scripts/run_sseac_v0_pg40_a8002.sh
```

## 失败原因

vLLM 已加载模型权重，但在键值缓存分配时显存不足。相关条件是显卡已有占用，不是提示、结构或评分行为：

- 显卡 7 启动前已有约 `15409 MiB` 占用。
- vLLM used `--gpu-memory-utilization 0.90` and tried to allocate additional KV cache.
- 引擎进程在任何提示调用前失败。

没有产生 `predictions.jsonl`、编译产物或评分。

## 后续规则

其他用户或其他任务正在使用 A800_2 时不要重试。机器空闲后，可用更保守配置重试，例如：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=<free-gpu> PORT=<free-port> RUN_ID=<new-run-id> LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 bash scripts/run_sseac_v0_pg40_a8002.sh
```

这是执行失败，不是真负结果。
