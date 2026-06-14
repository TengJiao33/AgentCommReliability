#!/usr/bin/env bash
set -uo pipefail

ROOT="${DAR_ROOT:-/data/xuhaoming/yfy/research_workspace/baselines/DAR}"
PY="${DAR_PY:-/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python}"
GPU="${DAR_GPU_ID:-7}"
TIMEOUT="${DAR_TIMEOUT:-60m}"
STAMP="${DAR_STAMP:-$(date +%Y%m%d_%H%M%S)}"
LOG_DIR="${DAR_LOG_DIR:-/data/xuhaoming/yfy/research_workspace/logs}"
RESULT_DIR="${DAR_RESULT_DIR:-/data/xuhaoming/yfy/research_workspace/results}"

mkdir -p "$LOG_DIR" "$RESULT_DIR"
cd "$ROOT" || exit 1

run="dar-guarded-answer-diversity-qwen25-7b-gsm8k100-${STAMP}"
out="${RESULT_DIR}/${run}/out"
log="${LOG_DIR}/${run}.log"

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
  --uncertainty_prompt True \
  --vote_prompt True \
  --m_role filter_critical \
  --retention_guard answer_diversity \
  --retention_guard_max 3 \
  --retention_message_mode answer_only \
  --save_full_history \
  --out_dir "$out" > "$log" 2>&1

rc=$?
echo "RC=${rc}"
tail -80 "$log"
echo
exit "$rc"
