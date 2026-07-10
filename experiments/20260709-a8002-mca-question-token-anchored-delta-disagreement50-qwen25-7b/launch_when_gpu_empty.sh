#!/usr/bin/env bash
set -euo pipefail

WORK=/data/xuhaoming/yfy/research_workspace
RUN_ID=20260709-a8002-mca-question-token-anchored-delta-disagreement50-qwen25-7b
RUN_DIR="$WORK/experiments/$RUN_ID"
PYTHON=/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python
MODEL=/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct

CANDIDATE_GPUS=${CANDIDATE_GPUS:-"0 1 2 3 4 5 6 7"}
MIN_FREE_MB=${MIN_FREE_MB:-70000}
MAX_UTIL=${MAX_UTIL:-5}
WAIT_SECONDS=${WAIT_SECONDS:-120}
MAX_WAIT_LOOPS=${MAX_WAIT_LOOPS:-720}

mkdir -p "$RUN_DIR"
cd "$WORK"

log() {
  echo "[qtoken-wait] $(date -Is) $*"
}

select_gpu() {
  for gpu in $CANDIDATE_GPUS; do
    if nvidia-smi pmon -c 1 | awk -v g="$gpu" 'NR > 2 && $1 == g && $2 != "-" {found=1} END {exit found ? 0 : 1}'; then
      log "gpu=$gpu has pmon process; skip" >&2
      continue
    fi
    row=$(nvidia-smi --query-gpu=index,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits | awk -F', ' -v g="$gpu" '$1==g {print $0}')
    free_mb=$(echo "$row" | awk -F', ' '{print $3}')
    util=$(echo "$row" | awk -F', ' '{print $4}')
    if [ -n "$free_mb" ] && [ "$free_mb" -ge "$MIN_FREE_MB" ] && [ "$util" -le "$MAX_UTIL" ]; then
      printf '%s\n' "$gpu"
      return 0
    fi
    log "gpu=$gpu not empty enough row=$row" >&2
  done
  return 1
}

log "host=$(hostname) run_id=$RUN_ID candidate_gpus=$CANDIDATE_GPUS min_free_mb=$MIN_FREE_MB max_util=$MAX_UTIL"
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits

selected=""
for i in $(seq 1 "$MAX_WAIT_LOOPS"); do
  if selected=$(select_gpu); then
    break
  fi
  log "waiting loop=$i"
  sleep "$WAIT_SECONDS"
done

if [ -z "$selected" ]; then
  log "no GPU became available"
  exit 2
fi

export CUDA_VISIBLE_DEVICES="$selected"
printf '%s\n' "$selected" > "$RUN_DIR/selected_gpu.txt"
log "selected_gpu=$CUDA_VISIBLE_DEVICES"
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits

trap 'log "received SIGTERM"; exit 143' TERM
trap 'log "received SIGHUP"; exit 129' HUP
trap 'code=$?; log "exit code=$code"; exit $code' EXIT

timeout 16h "$PYTHON" scripts/run_mca_question_token_anchored_delta.py \
  --work-dir "$WORK" \
  --run-id "$RUN_ID" \
  --benchmark math500 \
  --split mca_disagreement_v1 \
  --model-key qwen25-7b-instruct \
  --model-path "$MODEL" \
  --gpu-id "$CUDA_VISIBLE_DEVICES" \
  --agents 3 \
  --layers 22 \
  --conditions raw_delta,question_token_delta,question_token_random_same_norm \
  --span-tokens 16 \
  --max-payloads 8 \
  --max-question-anchors 3 \
  --attribution-method attention \
  --steering-scale 0.03 \
  --message-max-norm 1.0 \
  --temperature 0.2 \
  --top-p 1.0 \
  --max-new-tokens 1536 \
  --max-model-len 8192 \
  --dtype bfloat16 \
  --seed 42 \
  --limit 50 \
  > "$RUN_DIR/run_question_token_anchored.nohup.log" 2>&1

