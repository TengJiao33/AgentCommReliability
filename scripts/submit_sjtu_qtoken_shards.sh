#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=/hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability
IMAGE=docker.v2.aispeech.com/sjtu/sjtu_yukai-chaolei-suremaster_icefall:v1.0
QUEUE=${QUEUE:-pdgpu-3090}
BASE_RUN_ID=${BASE_RUN_ID:-20260720-sjtu-qtoken-disagreement50-qwen25-7b}
LIMIT=${LIMIT:-50}
SHARD_COUNT=${SHARD_COUNT:-8}
MAX_NEW_TOKENS=${MAX_NEW_TOKENS:-1536}
MAX_MODEL_LEN=${MAX_MODEL_LEN:-8192}

for ((shard_index = 0; shard_index < SHARD_COUNT; shard_index++)); do
  printf -v shard_label '%02d-of-%02d' "$shard_index" "$SHARD_COUNT"
  run_id="${BASE_RUN_ID}-shard${shard_label}"
  vc submit \
    -p "$QUEUE" \
    -i "$IMAGE" \
    -j "acr-qtoken-${shard_label}" \
    -n 1 \
    -c 8 \
    -m 32G \
    -g 1 \
    --project sjtu \
    --dir "$PROJECT_ROOT" \
    --cmd "LIMIT=$LIMIT MAX_NEW_TOKENS=$MAX_NEW_TOKENS MAX_MODEL_LEN=$MAX_MODEL_LEN SHARD_COUNT=$SHARD_COUNT SHARD_INDEX=$shard_index RUN_ID=$run_id bash scripts/run_sjtu_qtoken_smoke.sh"
done
