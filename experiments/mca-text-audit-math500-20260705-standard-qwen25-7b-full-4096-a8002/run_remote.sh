#!/usr/bin/env bash
set -euo pipefail

WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-mca-text-audit-math500-20260705-standard-qwen25-7b-full-4096-a8002}
PY=${PY:-$WORK/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-7}
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

echo "== evaluator/import smoke =="
"$PY" - <<'PY'
import sys

sys.path.insert(0, "scripts")
from run_basic_mad import is_correct, normalize_numeric
from run_mca_text_audit import aggregate_audit_decision, parse_audit_certificate

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

cert = parse_audit_certificate(
    "<certificate><used_cues>cue-1</used_cues><condition>x</condition>"
    "<initial>fail</initial><alternative>pass</alternative>"
    "<calculation>x</calculation><answer>7</answer><decision>change</decision></certificate>"
)
answer, decision, count, required = aggregate_audit_decision("5", [cert, cert], min_change_certificates=2)
print("audit smoke", answer, decision, count, required)
if decision != "change" or normalize_numeric(answer) != "expr:7":
    raise SystemExit("audit aggregation smoke failed")
PY

if [ -e "$OUT_DIR/summary.json" ]; then
  echo "Output already has summary.json: $OUT_DIR" >&2
  exit 2
fi

echo "== run MCA-T audit standard full math500, 4096 output =="
timeout 18h "$PY" scripts/run_mca_text_audit.py \
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
  --initial-prompt-style standard-mad \
  --temperature 1.0 \
  --cue-temperature 1.0 \
  --audit-temperature 1.0 \
  --top-p 1.0 \
  --max-tokens 4096 \
  --cue-max-tokens 4096 \
  --audit-max-tokens 4096 \
  --batch-size 6 \
  --max-model-len 24064 \
  --gpu-memory-utilization 0.85 \
  --dtype bfloat16 \
  --seed 42 \
  --disable-tqdm

echo "== summary =="
"$PY" - <<'PY'
import json
import os
from pathlib import Path

run_id = os.environ.get("RUN_ID", "mca-text-audit-math500-20260705-standard-qwen25-7b-full-4096-a8002")
p = Path("experiments") / run_id / "math500-qwen25-7b-instruct-mca-text-audit-all" / "summary.json"
d = json.loads(p.read_text(encoding="utf-8"))
print(p)
print("counts", d["counts"])
print("metrics", d["metrics"])
PY
