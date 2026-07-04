#!/usr/bin/env bash
set -euo pipefail

WORK_DIR=/data/xuhaoming/yfy/research_workspace
RUN_ID=20260704-a8002-math500-mad-mm-qwen25-7b-full
PYTHON="$WORK_DIR/envs/mad-mm-vllm063/bin/python"
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct
GPU_ID=${GPU_ID:-1}

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

echo "== evaluator gold smoke =="
"$PYTHON" - <<'PY'
import sys
sys.path.insert(0, "scripts")
from run_basic_mad import is_correct, normalize_numeric
pairs = [
    (r"\boxed{\frac{14}{3}}", r"\frac{14}{3}"),
    (r"\boxed{\left(3,\frac{\pi}{2}\right)}", r"\left( 3, \frac{\pi}{2} \right)"),
    (r"\boxed{p-q}", "p - q"),
    (r"\boxed{\text{Evelyn}}", r"\text{Evelyn}"),
    (r"\boxed{145}", r"145^\circ"),
]
for pred, gold in pairs:
    print(pred, "=>", normalize_numeric(pred), "|", gold, "=>", normalize_numeric(gold), "| ok=", is_correct(pred, gold))
PY

for strategy in naive subjective objective; do
  echo "== run math500 test ${strategy} =="
  "$PYTHON" scripts/run_mad_mm.py \
    --work-dir "$WORK_DIR" \
    --run-id "$RUN_ID" \
    --benchmark math500 \
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

echo "== summaries =="
find "experiments/$RUN_ID" -name summary.json -print -exec "$PYTHON" -c 'import json,sys; p=sys.argv[1]; d=json.load(open(p,encoding="utf-8")); print(p, d["counts"], d["metrics"])' {} \;
