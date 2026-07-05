#!/usr/bin/env bash
set -euo pipefail

WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-20260705-a8002-math500-mca-text-audit-qwen25-7b-full}
PY=${PY:-$WORK/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-1}
INPUT_RECORDS=${INPUT_RECORDS:-$WORK/experiments/20260705-a8002-math500-cpac-dcac-qwen25-7b-full/math500-qwen25-7b-instruct-cpac-dcac/records.jsonl}
OUT_DIR="$WORK/experiments/$RUN_ID/math500-qwen25-7b-instruct-mca-text-audit-all"

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
wc -l "$INPUT_RECORDS"

echo "== import smoke =="
"$PY" - <<'PY'
import sys
sys.path.insert(0, "scripts")
from run_mca_text_audit import aggregate_audit_decision, parse_audit_certificate
from run_mca_text import load_input_record_rows
print("run_mca_text_audit import ok")
PY

if [ -e "$OUT_DIR/summary.json" ]; then
  echo "Output already has summary.json: $OUT_DIR" >&2
  exit 2
fi

echo "== wait for GPU $GPU_ID =="
for attempt in $(seq 1 720); do
  line=$(nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits | awk -F, -v gpu="$GPU_ID" '$1 ~ "^ *" gpu "$" {gsub(/ /, "", $2); gsub(/ /, "", $3); print $2, $3}')
  mem=$(echo "$line" | awk '{print $1}')
  util=$(echo "$line" | awk '{print $2}')
  echo "gpu=$GPU_ID attempt=$attempt mem_mib=${mem:-unknown} util_pct=${util:-unknown} time=$(date -Is)"
  if [ -n "${mem:-}" ] && [ -n "${util:-}" ] && [ "$mem" -lt 1000 ] && [ "$util" -lt 20 ]; then
    break
  fi
  sleep 60
done

line=$(nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits | awk -F, -v gpu="$GPU_ID" '$1 ~ "^ *" gpu "$" {gsub(/ /, "", $2); gsub(/ /, "", $3); print $2, $3}')
mem=$(echo "$line" | awk '{print $1}')
util=$(echo "$line" | awk '{print $2}')
if [ -z "${mem:-}" ] || [ -z "${util:-}" ] || [ "$mem" -ge 1000 ] || [ "$util" -ge 20 ]; then
  echo "GPU $GPU_ID did not become free within wait window." >&2
  exit 3
fi

echo "== run MCA-T audit math500 full =="
timeout 8h "$PY" scripts/run_mca_text_audit.py \
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
  --min-change-certificates 2 \
  --pool-state-scope all \
  --input-records "$INPUT_RECORDS" \
  --temperature 0.8 \
  --cue-temperature 0.2 \
  --audit-temperature 0.2 \
  --top-p 0.95 \
  --max-tokens 2048 \
  --cue-max-tokens 512 \
  --audit-max-tokens 1536 \
  --batch-size 16 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.85 \
  --seed 42 \
  --limit 0 \
  --disable-tqdm

echo "== summary =="
"$PY" - <<'PY'
import json
from pathlib import Path
p = Path("experiments/20260705-a8002-math500-mca-text-audit-qwen25-7b-full/math500-qwen25-7b-instruct-mca-text-audit-all/summary.json")
d = json.loads(p.read_text(encoding="utf-8"))
print(p)
print("counts", d["counts"])
print("metrics", d["metrics"])
PY
