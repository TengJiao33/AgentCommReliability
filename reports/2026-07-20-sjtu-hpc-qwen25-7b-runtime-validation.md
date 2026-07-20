# SJTU HPC Qwen2.5-7B 运行验收

日期：2026-07-20

## 结论

当前项目已经具备在上海交通大学 AISPEECH D6 集群上运行 Qwen2.5-7B question-token anchored delta 实验的条件。单张 24 GB RTX 3090 完成了原 8192/1536 参数，峰值显存为 14.41 GiB。硬件不构成严重限制；主要成本是约 5 分钟/题的单卡串行耗时。

runner 已支持按题目分片。8 张 GPU 可以同时运行 8 个独立分片，卡之间不传输模型张量，因此不依赖 NVLink。

## 持久环境

| 内容 | 配置 |
| --- | --- |
| Python | 3.10.20 |
| PyTorch | 2.4.0+cu121 |
| Transformers | 4.46.2 |
| ModelScope | 1.38.1 |
| 模型 | Qwen2.5-7B-Instruct，BF16，14.19 GiB 权重 |
| 输入 | MATH-500 disagreement split，221 行，上传后 SHA-256 一致 |
| 持久环境与模型 | 约 20 GB，位于 `hpc_stor03` |

计算节点可以访问 PyPI、ModelScope 和 GitHub，不能访问 Hugging Face。环境脚本使用 ModelScope 下载模型，并把依赖和权重保存在个人持久目录。

## 实测结果

| GPU | 题数 | 上下文 / 输出上限 | runner 用时 | 峰值显存 | 作业状态 |
| --- | ---: | --- | ---: | ---: | --- |
| A10 24 GB | 1 | 4096 / 256 | 128.1 秒 | 14.30 GiB | Completed |
| RTX 3090 24 GB | 1 | 4096 / 256 | 95.4 秒 | 14.30 GiB | Completed |
| RTX 3090 24 GB | 3 | 4096 / 256 | 238.1 秒 | 14.30 GiB | Completed |
| RTX 3090 24 GB | 1 | 4096 / 512 | 165.8 秒 | 14.30 GiB | Completed |
| RTX 3090 24 GB | 1 | 8192 / 1536 | 297.4 秒 | 14.41 GiB | Completed |

这些任务只验证环境、显存、执行链路和连续运行稳定性。1–3 题结果不能用于评价方法效果。

一次初始 8192/1536 运行已写完结果，但启动脚本在作业运行中被覆盖，shell 随后以退出码 2 结束。上表采用脚本稳定落盘后的独立重跑结果。

## 正式运行方式

`scripts/submit_sjtu_qtoken_shards.sh` 默认把前 50 题分成 8 个互不重叠的单卡作业：

```bash
BASE_RUN_ID=20260720-sjtu-qtoken-disagreement50-qwen25-7b \
LIMIT=50 \
SHARD_COUNT=8 \
bash scripts/submit_sjtu_qtoken_shards.sh
```

该命令会申请账号的全部 8 张 GPU 配额。每个分片使用独立 run ID；资源不足时，未分配到 GPU 的分片保持 `Pending`，不会丢失。
