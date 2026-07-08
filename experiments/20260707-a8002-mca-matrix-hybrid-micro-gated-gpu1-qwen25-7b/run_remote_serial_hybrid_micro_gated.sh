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
  --pre-state-stage early_plan
  --pre-state-tokens 64
  --visible-commitment-mode micro
  --visible-commitment-max-chars 700
  --first-round-selection-policy pre_kv_unanimous_else_no_channel
  --pre-state-temperature 0.7
  --first-round-temperature 0.2
  --debate-temperature 1.0
  --top-p 1.0
  --first-round-max-tokens 1536
  --debate-max-tokens 4096
  --batch-size 1
  --max-model-len 8192
  --dtype bfloat16
  --seed 42
  --limit 0
)

timeout 96h "${PYTHON}" scripts/run_mca_pre_kv_then_mad.py \
  "${COMMON_ARGS[@]}" \
  --run-id 20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-disagreement-qwen25-7b \
  --split mca_disagreement_v1

timeout 96h "${PYTHON}" scripts/run_mca_pre_kv_then_mad.py \
  "${COMMON_ARGS[@]}" \
  --run-id 20260707-a8002-gpu1-mca-matrix-hybrid-micro-gated-gold-contrast-qwen25-7b \
  --split mca_gold_contrast_v1
