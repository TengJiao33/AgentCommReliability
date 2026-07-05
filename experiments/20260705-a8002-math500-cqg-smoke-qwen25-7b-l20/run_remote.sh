#!/usr/bin/env bash
set -euo pipefail

WORK_DIR=${WORK_DIR:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-20260705-a8002-math500-cqg-smoke-qwen25-7b-l20}
PYTHON=${PYTHON:-$WORK_DIR/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-7}
LIMIT=${LIMIT:-20}
MODES=${MODES:-"never divergent"}

export CUDA_VISIBLE_DEVICES="$GPU_ID"
export HF_HOME="$WORK_DIR/hf_home"
export TORCH_HOME="$WORK_DIR/torch_home"
export PIP_CACHE_DIR="$WORK_DIR/pip_cache"
export HF_DATASETS_CACHE="$HF_HOME/datasets"
export HF_HUB_CACHE="$HF_HOME/hub"
export TOKENIZERS_PARALLELISM=false

cd "$WORK_DIR"

mkdir -p "experiments/$RUN_ID"

echo "== environment =="
hostname
date
"$PYTHON" - <<'PY'
import importlib.metadata as md
import sys
print("python", sys.version)
for package in ["vllm", "torch", "transformers", "sympy", "latex2sympy2"]:
    try:
        print(package, md.version(package))
    except Exception as exc:
        print(package, "unavailable", exc)
PY

echo "== resources =="
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
df -h /data /mnt/quarkfs
wc -l data/benchmarks/math500/test/canonical.jsonl

echo "== evaluator smoke =="
"$PYTHON" - <<'PY'
import sys
sys.path.insert(0, "scripts")
from run_basic_mad import is_correct, normalize_numeric
pairs = [
    (r"\boxed{\frac{14}{3}}", r"\frac{14}{3}"),
    (r"\boxed{137 \frac{1}{2}}", r"137 \frac{1}{2}"),
    (r"\boxed{\left(3,\frac{\pi}{2}\right)}", r"\left( 3, \frac{\pi}{2} \right)"),
    (r"\boxed{p-q}", "p - q"),
]
for pred, gold in pairs:
    print(pred, "=>", normalize_numeric(pred), "|", gold, "=>", normalize_numeric(gold), "| ok=", is_correct(pred, gold))
PY

run_mode() {
  local mode="$1"
  echo "== run CQG mode=${mode} =="
  timeout 45m "$PYTHON" scripts/run_consensus_quarantine.py \
    --work-dir "$WORK_DIR" \
    --run-id "$RUN_ID" \
    --benchmark math500 \
    --split test \
    --model-key qwen25-7b-instruct \
    --model-path "$MODEL_PATH" \
    --gpu-id "$GPU_ID" \
    --agents 3 \
    --reviewers 3 \
    --quarantine-mode "$mode" \
    --temperature 0.8 \
    --appeal-temperature 0.2 \
    --review-temperature 0.2 \
    --top-p 0.95 \
    --max-tokens 2048 \
    --appeal-max-tokens 512 \
    --review-max-tokens 1536 \
    --batch-size 16 \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.85 \
    --seed 42 \
    --limit "$LIMIT"
}

for mode in $MODES; do
  run_mode "$mode"
done

echo "== summaries =="
find "experiments/$RUN_ID" -name summary.json -print -exec "$PYTHON" -c 'import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding="utf-8")); print(p); print("counts", d["counts"]); print("metrics", d["metrics"])' {} \;
