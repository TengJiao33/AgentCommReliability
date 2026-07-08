#!/usr/bin/env bash
set -euo pipefail

WORK_DIR=${WORK_DIR:-/data/xuhaoming/yfy/research_workspace}
PYTHON=${PYTHON:-${WORK_DIR}/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-1}
LIMIT=${LIMIT:-50}

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
  --limit "${LIMIT}"
  --resume
)

run_variant() {
  local peer_mode=$1
  local split=$2
  local run_id=$3

  echo "[$(date -Is)] start peer_mode=${peer_mode} split=${split} limit=${LIMIT} run_id=${run_id}"
  timeout 36h "${PYTHON}" scripts/run_mca_latent_rounds.py \
    "${COMMON_ARGS[@]}" \
    --peer-mode "${peer_mode}" \
    --run-id "${run_id}" \
    --split "${split}"
  echo "[$(date -Is)] done peer_mode=${peer_mode} split=${split} run_id=${run_id}"
}

run_variant residual mca_disagreement_v1 20260708-a8002-gpu1-mca-latent-residual-disagreement50-qwen25-7b
run_variant residual mca_gold_contrast_v1 20260708-a8002-gpu1-mca-latent-residual-gold-contrast50-qwen25-7b
run_variant per_peer_branch mca_disagreement_v1 20260708-a8002-gpu1-mca-latent-per-peer-branch-disagreement50-qwen25-7b
run_variant per_peer_branch mca_gold_contrast_v1 20260708-a8002-gpu1-mca-latent-per-peer-branch-gold-contrast50-qwen25-7b

echo "[$(date -Is)] all safe-variant runs completed"
