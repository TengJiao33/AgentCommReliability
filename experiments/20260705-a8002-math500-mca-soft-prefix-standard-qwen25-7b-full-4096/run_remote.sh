#!/usr/bin/env bash
set -euo pipefail

WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-20260705-a8002-math500-mca-soft-prefix-standard-qwen25-7b-full-4096}
PY=${PY:-$WORK/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-1}
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
wc -l data/benchmarks/math500/test/canonical.jsonl

echo "== evaluator/import smoke =="
"$PY" - <<'PY'
import sys
sys.path.insert(0, "scripts")
from run_basic_mad import is_correct, normalize_numeric
from run_mad_mm import cot_prompt
from run_mca_soft_prefix import balanced_pool_spans
pairs = [
    (r"\boxed{\frac{14}{3}}", r"\frac{14}{3}", True),
    (r"\boxed{137 \frac{1}{2}}", r"137 \frac{1}{2}", True),
    (r"\boxed{(3,\frac{\pi}{2})}", r"\left( 3, \frac{\pi}{2} \right)", True),
    ("YOUR FINAL ANSWER ONLY", "42", False),
]
for pred, gold, expected in pairs:
    got = is_correct(pred, gold)
    print(pred, "=>", normalize_numeric(pred), "|", gold, "=>", normalize_numeric(gold), "| ok=", got)
    if got is not expected:
        raise SystemExit(f"unexpected evaluator result for {pred!r} vs {gold!r}: {got}")
print("standard prompt smoke", cot_prompt("1+1?")[:80].replace("\n", " "))
print("run_mca_soft_prefix import ok", balanced_pool_spans(5, 2))
PY

if [ "$(wc -l < data/benchmarks/math500/test/canonical.jsonl)" -ne 500 ]; then
  echo "MATH500 canonical split must have exactly 500 rows" >&2
  exit 2
fi

if [ -e "$OUT_DIR/summary.json" ]; then
  echo "Output already has summary.json: $OUT_DIR" >&2
  exit 2
fi

echo "== run MCA-P standard math500 full, 4096 output =="
timeout 12h "$PY" scripts/run_mca_soft_prefix.py \
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
  --initial-prompt-style standard-mad \
  --temperature 1.0 \
  --cue-temperature 1.0 \
  --resolve-temperature 1.0 \
  --top-p 1.0 \
  --max-tokens 4096 \
  --cue-max-tokens 4096 \
  --resolve-max-tokens 4096 \
  --batch-size 4 \
  --prefix-batch-size 2 \
  --max-model-len 24064 \
  --dtype bfloat16 \
  --seed 42 \
  --limit 0 \
  --disable-tqdm

echo "== summary =="
"$PY" - <<'PY'
import json
from pathlib import Path
p = Path("experiments/20260705-a8002-math500-mca-soft-prefix-standard-qwen25-7b-full-4096/math500-qwen25-7b-instruct-mca-soft-prefix-cue-all/summary.json")
d = json.loads(p.read_text(encoding="utf-8"))
print(p)
print("counts", d["counts"])
print("metrics", d["metrics"])
PY
