#!/usr/bin/env bash
set -euo pipefail

WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-standard-mad-math500-20260705-qwen25-7b-full-4096-a8002}
PY=${PY:-$WORK/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-4}
OUT_DIR="$WORK/experiments/$RUN_ID/math500-qwen25-7b-instruct-naive"

export CUDA_VISIBLE_DEVICES="$GPU_ID"
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-$WORK/pip_cache}"
export HF_HOME="${HF_HOME:-$WORK/hf_home}"
export HF_DATASETS_CACHE="${HF_DATASETS_CACHE:-$HF_HOME/datasets}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-$HF_HOME/hub}"
export TORCH_HOME="${TORCH_HOME:-$WORK/torch_home}"
export TOKENIZERS_PARALLELISM=false

mkdir -p "$WORK/experiments/$RUN_ID"
cd "$WORK"

echo "== environment =="
hostname
date -Is
"$PY" - <<'PY'
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
"$PY" - <<'PY'
import sys
sys.path.insert(0, "scripts")
from run_basic_mad import is_correct, normalize_numeric
pairs = [
    (r"\boxed{\frac{14}{3}}", r"\frac{14}{3}"),
    (r"\boxed{137 \frac{1}{2}}", r"137 \frac{1}{2}"),
    (r"\boxed{\left(3,\frac{\pi}{2}\right)}", r"\left( 3, \frac{\pi}{2} \right)"),
    (r"\boxed{p-q}", "p - q"),
    ("YOUR FINAL ANSWER ONLY", "42"),
]
for pred, gold in pairs:
    print(pred, "=>", normalize_numeric(pred), "|", gold, "=>", normalize_numeric(gold), "| ok=", is_correct(pred, gold))
PY

if [ -e "$OUT_DIR/summary.json" ]; then
  echo "Output already has summary.json: $OUT_DIR" >&2
  exit 2
fi

echo "== run standard MAD math500 full, 4096 output =="
timeout 12h "$PY" scripts/run_mad_mm.py \
  --work-dir "$WORK" \
  --run-id "$RUN_ID" \
  --benchmark math500 \
  --split test \
  --model-key qwen25-7b-instruct \
  --model-path "$MODEL_PATH" \
  --gpu-id "$GPU_ID" \
  --agents 3 \
  --rounds 2 \
  --prune-strategy naive \
  --temperature 1.0 \
  --top-p 1.0 \
  --max-tokens 4096 \
  --batch-size 8 \
  --max-model-len 24064 \
  --gpu-memory-utilization 0.85 \
  --dtype bfloat16 \
  --seed 42

echo "== summary =="
"$PY" - <<'PY'
import json
from pathlib import Path
p = Path("experiments/standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/math500-qwen25-7b-instruct-naive/summary.json")
d = json.loads(p.read_text(encoding="utf-8"))
print(p)
print("counts", d["counts"])
print("metrics", d["metrics"])
PY
