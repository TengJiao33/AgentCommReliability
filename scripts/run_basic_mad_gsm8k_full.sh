#!/usr/bin/env bash
set -euo pipefail

WORK="${WORK:-/data/xuhaoming/yfy/research_workspace}"
RUN_ID="${RUN_ID:-20260704-a8002-gsm8k-basic-mad-full}"
PY="${PY:-$WORK/envs/mad-mm-vllm063/bin/python}"
GPU_ID="${GPU_ID:-7}"

export CUDA_VISIBLE_DEVICES="$GPU_ID"
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-$WORK/pip_cache}"
export HF_HOME="${HF_HOME:-$WORK/hf_home}"
export HF_DATASETS_CACHE="${HF_DATASETS_CACHE:-$HF_HOME/datasets}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-$HF_HOME/hub}"
export TOKENIZERS_PARALLELISM=false

mkdir -p "$WORK/experiments/$RUN_ID"

COMMON_ARGS=(
  --work-dir "$WORK"
  --run-id "$RUN_ID"
  --benchmark gsm8k
  --split test
  --agents 3
  --rounds 1
  --max-tokens 512
  --batch-size 32
  --max-model-len 4096
  --gpu-memory-utilization 0.82
  --gpu-id "$GPU_ID"
  --seed 7
)

"$PY" "$WORK/scripts/run_basic_mad.py" "${COMMON_ARGS[@]}" \
  --model-key qwen25-1_5b-instruct \
  --model-path /mnt/quarkfs/share_model/Qwen2.5-1.5B-Instruct

"$PY" "$WORK/scripts/run_basic_mad.py" "${COMMON_ARGS[@]}" \
  --model-key qwen25-7b-instruct \
  --model-path /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct

"$PY" "$WORK/scripts/run_basic_mad.py" "${COMMON_ARGS[@]}" \
  --model-key qwen25-14b-instruct \
  --model-path /mnt/quarkfs/share_model/Qwen2.5-14B-Instruct
