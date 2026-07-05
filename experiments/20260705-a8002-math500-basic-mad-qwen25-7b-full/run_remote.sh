#!/usr/bin/env bash
set -euo pipefail

WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-20260705-a8002-math500-basic-mad-qwen25-7b-full}
PY=${PY:-$WORK/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-7}

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
date
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

echo "== run basic MAD full math500 =="
timeout 90m "$PY" scripts/run_basic_mad.py \
  --work-dir "$WORK" \
  --run-id "$RUN_ID" \
  --benchmark math500 \
  --split test \
  --model-key qwen25-7b-instruct \
  --model-path "$MODEL_PATH" \
  --gpu-id "$GPU_ID" \
  --agents 3 \
  --rounds 1 \
  --max-tokens 2048 \
  --direct-temperature 0.0 \
  --debate-temperature 0.7 \
  --top-p 0.95 \
  --batch-size 16 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.85 \
  --seed 7 \
  --disable-tqdm

echo "== summary =="
"$PY" - <<'PY'
import json
from pathlib import Path
p = Path("experiments/20260705-a8002-math500-basic-mad-qwen25-7b-full/qwen25-7b-instruct/summary.json")
d = json.loads(p.read_text(encoding="utf-8"))
print(p)
print("counts", d["counts"])
print("metrics", d["metrics"])
PY
