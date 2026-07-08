#!/usr/bin/env bash
set -euo pipefail

WORK_DIR=${WORK_DIR:-/data/xuhaoming/yfy/research_workspace}
PYTHON=${PYTHON:-${WORK_DIR}/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-1}

cd "${WORK_DIR}"

COMMON_ARGS=(
  --work-dir "${WORK_DIR}"
  --benchmark math500
  --model-key qwen25-7b-instruct
  --model-path "${MODEL_PATH}"
  --gpu-id "${GPU_ID}"
  --agents 3
  --latent-rounds 2
  --thought-tokens-per-round 96
  --private-thought-style natural
  --final-max-tokens 1536
  --thought-temperature 0.7
  --final-temperature 0.2
  --top-p 1.0
  --steering-layer 16
  --steering-scale 0.05
  --normalize-steering
  --peer-fusion mean
  --peer-message-max-norm 1.0
  --same-seed-conditions
  --no-apply-peer-on-final
  --max-model-len 8192
  --max-source-tokens 1024
  --dtype bfloat16
  --seed 42
  --limit 0
)

timeout 96h "${PYTHON}" scripts/run_mca_latent_rounds.py \
  "${COMMON_ARGS[@]}" \
  --run-id 20260707-a8002-gpu1-mca-latent-rounds-disagreement-qwen25-7b \
  --split mca_disagreement_v1

timeout 96h "${PYTHON}" scripts/run_mca_latent_rounds.py \
  "${COMMON_ARGS[@]}" \
  --run-id 20260707-a8002-gpu1-mca-latent-rounds-gold-contrast-qwen25-7b \
  --split mca_gold_contrast_v1
