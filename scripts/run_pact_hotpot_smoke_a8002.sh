#!/usr/bin/env bash
set -uo pipefail

ROOT="${PACT_ROOT:-/data/xuhaoming/yfy/research_workspace/baselines/PACT}"
PY="${PACT_PY:-/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python}"
MODEL="${PACT_MODEL:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}"
GPU="${PACT_GPU_ID:-1}"
TIMEOUT="${PACT_TIMEOUT:-30m}"
STAMP="${PACT_STAMP:-$(date +%Y%m%d_%H%M%S)}"
RUN_ID="${PACT_RUN_ID:-pact-qwen25-7b-hotpot5-${STAMP}}"
RESULT_DIR="${PACT_RESULT_DIR:-/data/xuhaoming/yfy/research_workspace/results/${RUN_ID}}"
OUT_NAME="${PACT_OUT_NAME:-pact_results.jsonl}"
MAX_SAMPLES="${PACT_MAX_SAMPLES:-5}"
MAX_NEW_TOKENS="${PACT_MAX_NEW_TOKENS:-1024}"
MAX_MODEL_LEN="${PACT_MAX_MODEL_LEN:-8192}"
GENERATE_BS="${PACT_GENERATE_BS:-1}"
MAX_TURNS="${PACT_MAX_TURNS:-4}"
SEED="${PACT_SEED:-42}"
DATA_PATH="${PACT_DATA_PATH:-data/hotpot_dev_distractor_v1.json}"

mkdir -p "$RESULT_DIR"
cd "$ROOT" || exit 1

if [ ! -f "$DATA_PATH" ]; then
  echo "Dataset not found at ${ROOT}/${DATA_PATH}."
  echo "Run from the PACT root: bash scripts/download_hotpotqa.sh"
  exit 2
fi

OUT="${RESULT_DIR}/${OUT_NAME}"
LOG="${RESULT_DIR}/run.log"

echo "RUN_ID=${RUN_ID}"
echo "ROOT=${ROOT}"
echo "GPU=${GPU}"
echo "MODEL=${MODEL}"
echo "DATA_PATH=${DATA_PATH}"
echo "MAX_SAMPLES=${MAX_SAMPLES}"
echo "MAX_NEW_TOKENS=${MAX_NEW_TOKENS}"
echo "RESULT_DIR=${RESULT_DIR}"
echo "LOG=${LOG}"

CUDA_VISIBLE_DEVICES="$GPU" timeout "$TIMEOUT" "$PY" run.py \
  --model_name "$MODEL" \
  --data_path "$DATA_PATH" \
  --use_vllm \
  --tensor_parallel_size 1 \
  --gpu_memory_utilization 0.85 \
  --max_model_len "$MAX_MODEL_LEN" \
  --seed "$SEED" \
  --generate_bs "$GENERATE_BS" \
  --max_new_tokens "$MAX_NEW_TOKENS" \
  --max_turns "$MAX_TURNS" \
  --max_samples "$MAX_SAMPLES" \
  --output_path "$OUT" > "$LOG" 2>&1

rc=$?
echo "RC=${rc}"
tail -80 "$LOG"
exit "$rc"
