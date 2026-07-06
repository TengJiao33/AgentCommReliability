# 服务器资源清单

这是远端资源的保留操作台账。

本文件的最近一次详细快照在 2026-07-03 根据旧记录重置。机器容量和模型可用性都应视为“最后已知事实”；启动任何新任务前必须重新刷新。

## 远端根目录

| 机器 | 项目根目录 | 说明 |
| --- | --- | --- |
| `A800_2` | `/data/xuhaoming/yfy/research_workspace` | 首选受控项目根目录。 |
| `Falcon` | `/mnt/20t/xuhaoming/yfy/research_workspace` | 仅在路由可用且资源空闲时使用。 |

## A800_2 访问

SSH 别名：

```text
A800_2
```

直连形式：

```text
ssh -p 10622 xuhaoming@124.128.251.61
```

最后已知主机标识：

```text
10-116-90-20
```

## A800_2 项目工作区清理

最近清理：`2026-07-03`。

远端项目根目录：

```text
/data/xuhaoming/yfy/research_workspace
```

远端项目文件夹已重置为最小骨架。旧实验、结果、日志、脚本、基线 checkout、报告、数据、测试框架文件、临时文件、备份和传输压缩包都已从该文件夹移除。

保留的可复用运行时/缓存目录：

| 路径 | 最近检查大小 | 原因 |
| --- | ---: | --- |
| `envs/` | `7.1G` | 可复用的项目 Python 环境 |
| `pip_cache/` | `3.2G` | 可复用包缓存 |
| `hf_home/` | `20K` | 可复用 Hugging Face 缓存根目录 |
| `modelscope_cache/` | `8.0K` | 可复用 ModelScope 缓存根目录 |
| `torch_home/` | `4.0K` | 可复用 Torch 缓存根目录 |

当前保留的骨架目录：

```text
active/
baselines/
docs/
experiments/
reports/
README.md
```

## 已准备基准数据

最近准备：`2026-07-03`。

远端位置：

```text
/data/xuhaoming/yfy/research_workspace/data/benchmarks
```

这些数据只放在项目根目录下。准备时 `A800_2` 无法访问 Hugging Face，因此基准 JSONL 文件是在本地生成后传入项目文件夹的。MMLU-Pro 源 parquet 快照也复制到了：

```text
/data/xuhaoming/yfy/research_workspace/data/source_repos/MMLU-Pro
```

| 基准 | 来源 | 划分 | 行数 |
| --- | --- | --- | ---: |
| `mmlu_pro` | `TIGER-Lab/MMLU-Pro` | `test`, `validation` | 12,102 |
| `gsm8k` | `openai/gsm8k`，配置 `main` | `train`, `test` | 8,792 |
| `math500` | `HuggingFaceH4/MATH-500` | `test` | 500 |
| `aime24` | `HuggingFaceH4/aime_2024` | `train` | 30 |
| `aime25` | `math-ai/aime25` | `test` | 30 |

## 共享资源规则

- 项目文件放在项目根目录下。
- 将 `/mnt/quarkfs/share_model` 视为共享只读目录，除非得到明确许可。
- 不要把大型模型权重重复复制到项目工作区。
- 不要安装到共享 conda 环境。
- 不要杀掉其他用户的进程。
- 任何新模型、数据集、环境、缓存或成本较高的结果目录，都要记录下来。

## 最后已知共享模型根目录

```text
/mnt/quarkfs/share_model
```

早期清单中已知有用的模型族：

- `Qwen2.5-*`
- `Qwen3*`
- `BGE-large-en-v1.5`
- `bge-reranker-large`

使用前刷新可用性。

## 刷新命令

```powershell
ssh A800_2 'hostname; date -Is; df -h /data /mnt/quarkfs; nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits'
ssh A800_2 'WORK=/data/xuhaoming/yfy/research_workspace; mkdir -p "$WORK"; du -sh "$WORK"; du -sh "$WORK"/* 2>/dev/null | sort -h'
ssh A800_2 'du -sh /mnt/quarkfs/share_model/* 2>/dev/null | sort -h'
```

## 更新检查清单

发生以下情况时更新本文档：

- 新模型被下载、完成、修改或作为依赖使用；
- 新数据集或基准副本被创建；
- 新环境或大型缓存被创建；
- 某次运行写入超过 `1G`；
- 清理操作移除了远端产物；
- 长期服务被启动并留在后台运行。
