#!/usr/bin/env bash
set -euo pipefail

WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-20260705-a8002-math500-mca-text-qwen25-7b-l20}
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

echo "== import smoke =="
"$PY" - <<'PY'
import sys
sys.path.insert(0, "scripts")
from run_mca_text import parse_cue_atoms, filter_cues
from run_consensus_quarantine import build_candidate_cards
print("run_mca_text import ok")
PY

echo "== run MCA-T smoke math500 limit 20 =="
timeout 45m "$PY" scripts/run_mca_text.py \
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
  --pool-state-scope all \
  --temperature 0.8 \
  --cue-temperature 0.2 \
  --resolve-temperature 0.2 \
  --top-p 0.95 \
  --max-tokens 2048 \
  --cue-max-tokens 512 \
  --resolve-max-tokens 1536 \
  --batch-size 16 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.85 \
  --seed 42 \
  --limit 20 \
  --disable-tqdm

echo "== summary =="
"$PY" - <<'PY'
import json
from pathlib import Path
p = Path("experiments/20260705-a8002-math500-mca-text-qwen25-7b-l20/math500-qwen25-7b-instruct-mca-text-all/summary.json")
d = json.loads(p.read_text(encoding="utf-8"))
print(p)
print("counts", d["counts"])
print("metrics", d["metrics"])
PY
