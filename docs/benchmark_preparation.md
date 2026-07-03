# Benchmark Preparation

This note records the current benchmark prep route for remote reproductions.

## Target Machine Boundary

On `A800_2`, all project files, environments, caches, downloads, and prepared data must stay under:

```text
/data/xuhaoming/yfy/research_workspace
```

The preparation script enforces this boundary for its output and Hugging Face cache paths.

## Benchmarks

Prepared datasets:

| Key | Source |
| --- | --- |
| `mmlu_pro` | `TIGER-Lab/MMLU-Pro` |
| `gsm8k` | `openai/gsm8k`, config `main` |
| `math500` | `HuggingFaceH4/MATH-500` |
| `aime24` | primary `HuggingFaceH4/aime_2024`; fallback `math-ai/aime24` |
| `aime25` | primary `math-ai/aime25`; fallback candidates are built into the script |

Each benchmark is written under:

```text
data/benchmarks/<benchmark>/<split>/
  raw.jsonl
  canonical.jsonl
```

The global manifest is:

```text
data/benchmarks/manifest.json
```

## A800_2 Command

Run from the project root on the remote machine:

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

Do not use default home-directory caches for these downloads.

If Hugging Face API access is unstable but a dataset repo has already been cloned
inside the project workspace, use a local override:

```bash
python "$WORK/scripts/prepare_benchmarks.py" \
  --work-dir "$WORK" \
  --local-dataset mmlu_pro="$WORK/data/source_repos/MMLU-Pro" \
  --local-dataset-source mmlu_pro=TIGER-Lab/MMLU-Pro \
  --strict
```
