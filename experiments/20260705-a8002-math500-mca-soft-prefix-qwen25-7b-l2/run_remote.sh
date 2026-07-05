#!/usr/bin/env bash
set -euo pipefail

WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-20260705-a8002-math500-mca-soft-prefix-qwen25-7b-l2}
PY=${PY:-$WORK/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-1}
INPUT_RECORDS=${INPUT_RECORDS:-$WORK/experiments/20260705-a8002-math500-cpac-dcac-qwen25-7b-full/math500-qwen25-7b-instruct-cpac-dcac/records.jsonl}
OUT_DIR="$WORK/experiments/$RUN_ID/math500-qwen25-7b-instruct-mca-soft-prefix-cue-all"

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
for package in ["torch", "transformers", "sympy", "latex2sympy2"]:
    try:
        print(package, md.version(package))
    except Exception as exc:
        print(package, "unavailable", exc)
PY

echo "== resources =="
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
df -h /data /mnt/quarkfs
wc -l "$INPUT_RECORDS"

echo "== import smoke =="
"$PY" - <<'PY'
import sys
sys.path.insert(0, "scripts")
from run_mca_soft_prefix import balanced_pool_spans, parse_soft_prefix_resolve_output
print("run_mca_soft_prefix import ok", balanced_pool_spans(5, 2))
PY

if [ -e "$OUT_DIR/summary.json" ]; then
  echo "Output already has summary.json: $OUT_DIR" >&2
  exit 2
fi

echo "== run MCA-P smoke math500 limit 2 =="
timeout 30m "$PY" scripts/run_mca_soft_prefix.py \
  --work-dir "$WORK" \
  --run-id "$RUN_ID" \
  --benchmark math500 \
  --split test \
  --model-key qwen25-7b-instruct \
  --model-path "$MODEL_PATH" \
  --gpu-id "$GPU_ID" \
  --agents 3 \
  --reviewers 3 \
  --cue-k 2 \
  --prefix-len 32 \
  --prefix-mode cue \
  --prefix-fill mean \
  --pool-state-scope all \
  --input-records "$INPUT_RECORDS" \
  --temperature 0.8 \
  --cue-temperature 0.2 \
  --resolve-temperature 0.2 \
  --top-p 0.95 \
  --max-tokens 2048 \
  --cue-max-tokens 512 \
  --resolve-max-tokens 1024 \
  --batch-size 4 \
  --prefix-batch-size 2 \
  --max-model-len 8192 \
  --dtype bfloat16 \
  --seed 42 \
  --limit 2 \
  --disable-tqdm

echo "== summary =="
"$PY" - <<'PY'
import json
from pathlib import Path
p = Path("experiments/20260705-a8002-math500-mca-soft-prefix-qwen25-7b-l2/math500-qwen25-7b-instruct-mca-soft-prefix-cue-all/summary.json")
d = json.loads(p.read_text(encoding="utf-8"))
print(p)
print("counts", d["counts"])
print("metrics", d["metrics"])
PY
