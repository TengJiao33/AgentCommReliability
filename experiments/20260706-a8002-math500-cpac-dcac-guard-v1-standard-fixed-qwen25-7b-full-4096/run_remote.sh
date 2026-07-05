#!/usr/bin/env bash
set -euo pipefail

WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-20260706-a8002-math500-cpac-dcac-guard-v1-standard-fixed-qwen25-7b-full-4096}
PY=${PY:-$WORK/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-2}
OUT_DIR="$WORK/experiments/$RUN_ID/math500-qwen25-7b-instruct-cpac-dcac"

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
from run_consensus_quarantine import build_candidate_cards
from run_cpac_dcac import (
    dcac_certificate_rejection_reasons,
    is_guarded_dcac_flip,
    parse_dcac_certificate,
)

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

def output(answer, text):
    return {"parsed_answer": answer, "normalized_answer": answer, "output": text}

cards = build_candidate_cards([
    output("expr:17", "majority x = 8"),
    output("expr:17", "majority x = 8 again"),
    output("expr:7", "challenger x = 7"),
])
majority, challenger = cards[0], cards[1]
cert = parse_dcac_certificate("""
<certificate>
  <condition>x > 7</condition>
  <majority>fail</majority>
  <challenger>pass</challenger>
  <calculation>The majority answer x = 8 satisfies this condition, but challenger x = 7 does not.</calculation>
  <decision>flip</decision>
</certificate>
""")
reasons = dcac_certificate_rejection_reasons(cert, majority, challenger)
print("guard reasons", reasons)
if is_guarded_dcac_flip(cert, majority, challenger):
    raise SystemExit("guard smoke failed: contradictory certificate was accepted")
print("guard smoke passed")
PY

if [ -e "$OUT_DIR/summary.json" ]; then
  echo "Output already has summary.json: $OUT_DIR" >&2
  exit 2
fi

echo "== run CPAC-DCAC guard-v1 standard-fixed full math500, 4096 output =="
timeout 18h "$PY" scripts/run_cpac_dcac.py \
  --work-dir "$WORK" \
  --run-id "$RUN_ID" \
  --benchmark math500 \
  --split test \
  --model-key qwen25-7b-instruct \
  --model-path "$MODEL_PATH" \
  --gpu-id "$GPU_ID" \
  --agents 3 \
  --reviewers 3 \
  --initial-prompt-style standard-mad \
  --no-majority-action listwise \
  --dcac-min-flip-certificates 2 \
  --temperature 1.0 \
  --claim-temperature 1.0 \
  --certificate-temperature 1.0 \
  --listwise-temperature 1.0 \
  --top-p 1.0 \
  --max-tokens 4096 \
  --claim-max-tokens 4096 \
  --certificate-max-tokens 4096 \
  --listwise-max-tokens 4096 \
  --batch-size 8 \
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

run_id = os.environ.get("RUN_ID", "20260706-a8002-math500-cpac-dcac-guard-v1-standard-fixed-qwen25-7b-full-4096")
p = Path("experiments") / run_id / "math500-qwen25-7b-instruct-cpac-dcac" / "summary.json"
d = json.loads(p.read_text(encoding="utf-8"))
print(p)
print("counts", d["counts"])
print("metrics", d["metrics"])
PY
