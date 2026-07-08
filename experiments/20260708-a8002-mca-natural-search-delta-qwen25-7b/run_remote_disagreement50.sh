#!/usr/bin/env bash
set -euo pipefail

WORK_DIR=${WORK_DIR:-/data/xuhaoming/yfy/research_workspace}
PYTHON=${PYTHON:-${WORK_DIR}/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-0}
LIMIT=${LIMIT:-50}

cd "${WORK_DIR}"

echo "[$(date -Is)] natural-search-delta disagreement50 start gpu=${GPU_ID} limit=${LIMIT}"
timeout 36h "${PYTHON}" scripts/run_mca_natural_search_delta.py \
  --work-dir "${WORK_DIR}" \
  --run-id 20260708-a8002-mca-natural-search-delta-disagreement50-qwen25-7b \
  --benchmark math500 \
  --split mca_disagreement_v1 \
  --model-key qwen25-7b-instruct \
  --model-path "${MODEL_PATH}" \
  --gpu-id "${GPU_ID}" \
  --agents 3 \
  --layers 22 \
  --checkpoints 16,32,64,96 \
  --conditions same_question_peer_delta,other_question_peer_delta,random_gaussian_same_norm,same_question_peer_absolute \
  --steering-scale 0.03 \
  --message-max-norm 1.0 \
  --temperature 0.2 \
  --top-p 1.0 \
  --max-new-tokens 1536 \
  --max-model-len 8192 \
  --dtype bfloat16 \
  --seed 42 \
  --limit "${LIMIT}"
echo "[$(date -Is)] natural-search-delta disagreement50 done"
