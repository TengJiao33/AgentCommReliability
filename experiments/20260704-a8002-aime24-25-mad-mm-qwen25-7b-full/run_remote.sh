#!/usr/bin/env bash
set -euo pipefail

WORK_DIR=/data/xuhaoming/yfy/research_workspace
RUN_ID=20260704-a8002-aime24-25-mad-mm-qwen25-7b-full
PYTHON="$WORK_DIR/envs/mad-mm-vllm063/bin/python"
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct
GPU_ID=${GPU_ID:-7}

export CUDA_VISIBLE_DEVICES="$GPU_ID"
export HF_HOME="$WORK_DIR/hf_home"
export TORCH_HOME="$WORK_DIR/torch_home"
export PIP_CACHE_DIR="$WORK_DIR/pip_cache"

cd "$WORK_DIR"

echo "== environment =="
hostname
date
"$PYTHON" - <<'PY'
import importlib.metadata as md
import sys
print("python", sys.version)
for package in ["vllm", "torch", "transformers"]:
    try:
        print(package, md.version(package))
    except Exception as exc:
        print(package, "unavailable", exc)
PY

echo "== resources =="
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
df -h /data /mnt/quarkfs

for benchmark in aime24 aime25; do
  for strategy in naive subjective objective; do
    echo "== run ${benchmark} ${strategy} =="
    "$PYTHON" scripts/run_mad_mm.py \
      --work-dir "$WORK_DIR" \
      --run-id "$RUN_ID" \
      --benchmark "$benchmark" \
      --split test \
      --model-key qwen25-7b-instruct \
      --model-path "$MODEL_PATH" \
      --gpu-id "$GPU_ID" \
      --agents 3 \
      --rounds 2 \
      --prune-strategy "$strategy" \
      --temperature 1.0 \
      --top-p 1.0 \
      --max-tokens 4096 \
      --batch-size 8 \
      --max-model-len 24064 \
      --gpu-memory-utilization 0.85 \
      --seed 42
  done
done

echo "== summaries =="
find "experiments/$RUN_ID" -name summary.json -print -exec "$PYTHON" -c 'import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding="utf-8")); print(p, d["metrics"])' {} \;
