# 基准数据准备

本文记录当前用于远程复现实验的基准数据准备路线。

## 目标机器边界

在 `A800_2` 上，所有项目文件、环境、缓存、下载内容和已准备数据都必须放在以下路径：

/data/xuhaoming/yfy/research_workspace


准备脚本会对输出路径和 Hugging Face 缓存路径执行这个边界约束。

## 基准数据

已准备的数据集：

| 键名 | 来源 |
| --- | --- |
| `mmlu_pro` | `TIGER-Lab/MMLU-Pro` |
| `gsm8k` | `openai/gsm8k`，配置 `main` |
| `math500` | `HuggingFaceH4/MATH-500` |
| `aime24` | 首选 `HuggingFaceH4/aime_2024`；备用 `math-ai/aime24` |
| `aime25` | 首选 `math-ai/aime25`；备用候选内置在脚本中 |

每个基准写入：

```text
data/benchmarks/<benchmark>/<split>/
  raw.jsonl
  canonical.jsonl
```

全局清单为：

```text
data/benchmarks/manifest.json
```

## A800_2 命令

在远端机器的项目根目录运行：

```bash
WORK=/data/xuhaoming/yfy/research_workspace
cd "$WORK"
mkdir -p "$WORK/envs" "$WORK/pip_cache" "$WORK/hf_home" "$WORK/data/benchmarks"
export PIP_CACHE_DIR="$WORK/pip_cache"
export HF_HOME="$WORK/hf_home"
export HF_DATASETS_CACHE="$WORK/hf_home/datasets"
python3 -m venv "$WORK/envs/benchmarks"
. "$WORK/envs/benchmarks/bin/activate"
python -m pip install -U pip
python -m pip install "datasets>=2.19" "pyarrow>=14" "huggingface_hub>=0.23"
python "$WORK/scripts/prepare_benchmarks.py" --work-dir "$WORK" --strict
```

不要使用默认 home 目录缓存保存这些下载内容。

如果 Hugging Face API 访问不稳定，但数据集仓库已经克隆到项目工作区内，可以使用本地覆盖：

```bash
python "$WORK/scripts/prepare_benchmarks.py" \
  --work-dir "$WORK" \
  --local-dataset mmlu_pro="$WORK/data/source_repos/MMLU-Pro" \
  --local-dataset-source mmlu_pro=TIGER-Lab/MMLU-Pro \
  --strict
```
