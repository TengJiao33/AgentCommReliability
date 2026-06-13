#!/usr/bin/env bash
set -uo pipefail

ROOT="${DAR_ROOT:-/data/xuhaoming/yfy/research_workspace/baselines/DAR}"
PY="${DAR_PY:-/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python}"
GPU="${DAR_GPU_ID:-5}"
TIMEOUT="${DAR_TIMEOUT:-45m}"
STAMP="${DAR_STAMP:-$(date +%Y%m%d_%H%M%S)}"
LOG_DIR="${DAR_LOG_DIR:-/data/xuhaoming/yfy/research_workspace/logs}"
RESULT_DIR="${DAR_RESULT_DIR:-/data/xuhaoming/yfy/research_workspace/results}"

mkdir -p "$LOG_DIR" "$RESULT_DIR"
cd "$ROOT" || exit 1

run_case() {
  local name="$1"
  shift

  local run="dar-short-${name}-qwen25-7b-gsm8k100-${STAMP}"
  local out="${RESULT_DIR}/${run}/out"
  local log="${LOG_DIR}/${run}.log"

  mkdir -p "$out"
  echo "===== ${run} ====="
  echo "GPU=${GPU}"
  echo "OUT=${out}"
  echo "LOG=${log}"
  echo "TIMEOUT=${TIMEOUT}"

  CUDA_VISIBLE_DEVICES="$GPU" timeout "$TIMEOUT" "$PY" src/main.py \
    --model qwen2.5-7b \
    --num_agents 3 \
    --data gsm8k \
    --data_size 100 \
    --debate_rounds 1 \
    "$@" \
    --out_dir "$out" > "$log" 2>&1

  local rc=$?
  echo "RC=${rc}"
  tail -60 "$log"
  echo
  return "$rc"
}

rc_basic=0
rc_topk=0
rc_filter=0

run_case basic || rc_basic=$?
run_case topk05 --top_k_uncertainty 0.5 || rc_topk=$?
run_case filtercritical --uncertainty_prompt True --vote_prompt True --m_role filter_critical || rc_filter=$?

echo "SUMMARY_RC basic=${rc_basic} topk05=${rc_topk} filtercritical=${rc_filter}"

if [[ "$rc_basic" -ne 0 || "$rc_topk" -ne 0 || "$rc_filter" -ne 0 ]]; then
  exit 1
fi
