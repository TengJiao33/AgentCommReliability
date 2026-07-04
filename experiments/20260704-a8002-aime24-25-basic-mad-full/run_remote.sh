#!/usr/bin/env bash
set -euo pipefail

WORK="${WORK:-/data/xuhaoming/yfy/research_workspace}"
RUN_ID="${RUN_ID:-20260704-a8002-aime24-25-basic-mad-full}"
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
  --agents 3
  --rounds 1
  --max-tokens 1024
  --batch-size 16
  --max-model-len 4096
  --gpu-memory-utilization 0.82
  --gpu-id "$GPU_ID"
  --seed 7
)

run_one() {
  local benchmark="$1"
  local split="$2"
  local model_key="$3"
  local model_path="$4"

  "$PY" "$WORK/scripts/run_basic_mad.py" "${COMMON_ARGS[@]}" \
    --benchmark "$benchmark" \
    --split "$split" \
    --model-key "$benchmark-$model_key" \
    --model-path "$model_path"
}

for bench_split in "aime24 train" "aime25 test"; do
  read -r benchmark split <<<"$bench_split"
  run_one "$benchmark" "$split" qwen25-1_5b-instruct /mnt/quarkfs/share_model/Qwen2.5-1.5B-Instruct
  run_one "$benchmark" "$split" qwen25-7b-instruct /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct
  run_one "$benchmark" "$split" qwen25-14b-instruct /mnt/quarkfs/share_model/Qwen2.5-14B-Instruct
done
