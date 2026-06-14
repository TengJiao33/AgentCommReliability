#!/usr/bin/env bash
set -uo pipefail

ROOT="${DAR_ROOT:-/data/xuhaoming/yfy/research_workspace/baselines/DAR}"
PY="${DAR_PY:-/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python}"
GPU="${DAR_GPU_ID:-7}"
TIMEOUT="${DAR_TIMEOUT:-60m}"
STAMP="${DAR_STAMP:-$(date +%Y%m%d_%H%M%S)}"
LOG_DIR="${DAR_LOG_DIR:-/data/xuhaoming/yfy/research_workspace/logs}"
RESULT_DIR="${DAR_RESULT_DIR:-/data/xuhaoming/yfy/research_workspace/results}"
VARIANTS="${DAR_VARIANTS:-answer_only_no_guard guard_full}"

mkdir -p "$LOG_DIR" "$RESULT_DIR"
cd "$ROOT" || exit 1

run_variant() {
  local variant="$1"
  local run
  local out
  local log
  local guard_args

  case "$variant" in
    answer_only_no_guard)
      run="dar-answer-only-noguard-qwen25-7b-gsm8k100-${STAMP}"
      guard_args=(--retention_guard none --retention_message_mode answer_only)
      ;;
    guard_full)
      run="dar-guard-full-qwen25-7b-gsm8k100-${STAMP}"
      guard_args=(--retention_guard answer_diversity --retention_guard_max 3 --retention_message_mode full)
      ;;
    *)
      echo "Unknown DAR_VARIANT: ${variant}" >&2
      return 2
      ;;
  esac

  out="${RESULT_DIR}/${run}/out"
  log="${LOG_DIR}/${run}.log"
  mkdir -p "$out"

  echo "===== ${run} ====="
  echo "VARIANT=${variant}"
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
    "${guard_args[@]}" \
    --save_full_history \
    --out_dir "$out" > "$log" 2>&1

  local rc=$?
  echo "RC=${rc}"
  tail -80 "$log"
  echo
  return "$rc"
}

overall_rc=0
for variant in $VARIANTS; do
  run_variant "$variant"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    overall_rc="$rc"
    break
  fi
done

exit "$overall_rc"
