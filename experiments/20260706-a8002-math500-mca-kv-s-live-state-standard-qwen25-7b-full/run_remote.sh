#!/usr/bin/env bash
set -euo pipefail

WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-20260706-a8002-math500-mca-kv-s-live-state-standard-qwen25-7b-full}
PY=${PY:-$WORK/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
CANDIDATE_GPUS=${CANDIDATE_GPUS:-"0 1 2 3 4 5 6 7"}
MIN_FREE_MB=${MIN_FREE_MB:-80000}
WAIT_SECONDS=${WAIT_SECONDS:-120}
MAX_WAIT_LOOPS=${MAX_WAIT_LOOPS:-720}

export TOKENIZERS_PARALLELISM=false
export HF_HOME=${HF_HOME:-$WORK/.cache/huggingface}
export TRANSFORMERS_CACHE=${TRANSFORMERS_CACHE:-$WORK/.cache/huggingface}
export PYTHONPATH="$WORK/scripts:${PYTHONPATH:-}"
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}

cd "$WORK"
RUN_DIR="$WORK/experiments/$RUN_ID"
mkdir -p "$RUN_DIR"

echo "[run] started_at=$(date -Is)"
echo "[run] host=$(hostname) work=$WORK run_id=$RUN_ID"
echo "[run] python=$PY"
echo "[run] model=$MODEL_PATH"
echo "[run] candidate_gpus=$CANDIDATE_GPUS min_free_mb=$MIN_FREE_MB wait_seconds=$WAIT_SECONDS"

select_gpu() {
  for gpu in $CANDIDATE_GPUS; do
    if nvidia-smi pmon -c 1 | awk -v g="$gpu" 'NR > 2 && $1 == g && $2 != "-" {found=1} END {exit found ? 0 : 1}'; then
      echo "[run] gpu=$gpu has a pmon process; skip" >&2
      continue
    fi
    row=$(nvidia-smi --query-gpu=index,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits | awk -F', ' -v g="$gpu" '$1==g {print $0}')
    [ -n "$row" ] || continue
    free_mb=$(printf '%s\n' "$row" | awk -F', ' '{print $3}')
    util=$(printf '%s\n' "$row" | awk -F', ' '{print $4}')
    if [ "$free_mb" -ge "$MIN_FREE_MB" ] && [ "$util" -le 5 ]; then
      printf '%s\n' "$gpu"
      return 0
    fi
  done
  return 1
}

selected=""
for i in $(seq 1 "$MAX_WAIT_LOOPS"); do
  if selected=$(select_gpu); then
    break
  fi
  echo "[run] waiting_for_gpu loop=$i time=$(date -Is)"
  nvidia-smi --query-gpu=index,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
  sleep "$WAIT_SECONDS"
done

if [ -z "$selected" ]; then
  echo "[run] no GPU became available" >&2
  exit 3
fi

export CUDA_VISIBLE_DEVICES="$selected"
printf '%s\n' "$selected" > "$RUN_DIR/selected_gpu.txt"
echo "[run] selected_gpu=$CUDA_VISIBLE_DEVICES selected_at=$(date -Is)"
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits

"$PY" -m py_compile scripts/mca_hidden_channel_runner.py scripts/run_mca_kv_cache.py scripts/run_mca_activation_steering.py

KV_SUMMARY="$RUN_DIR/math500-qwen25-7b-instruct-mca-kv-cache-state-all/summary.json"
S_SUMMARY="$RUN_DIR/math500-qwen25-7b-instruct-mca-activation-steering-state-all/summary.json"

if [ -e "$KV_SUMMARY" ]; then
  echo "[run] skip KV, summary exists: $KV_SUMMARY"
else
  echo "[run] starting MCA-KV at $(date -Is)"
  timeout 48h "$PY" scripts/run_mca_kv_cache.py \
    --work-dir "$WORK" \
    --run-id "$RUN_ID" \
    --benchmark math500 \
    --split test \
    --model-key qwen25-7b-instruct \
    --model-path "$MODEL_PATH" \
    --gpu-id "$CUDA_VISIBLE_DEVICES" \
    --agents 3 \
    --reviewers 3 \
    --pool-state-scope all \
    --initial-prompt-style standard-mad \
    --channel-mode state \
    --temperature 1.0 \
    --resolve-temperature 0.2 \
    --top-p 1.0 \
    --max-tokens 4096 \
    --resolve-max-tokens 1536 \
    --max-model-len 8192 \
    --dtype bfloat16 \
    --seed 42 \
    --limit 0
fi

if [ -e "$S_SUMMARY" ]; then
  echo "[run] skip MCA-S, summary exists: $S_SUMMARY"
else
  echo "[run] starting MCA-S at $(date -Is)"
  timeout 48h "$PY" scripts/run_mca_activation_steering.py \
    --work-dir "$WORK" \
    --run-id "$RUN_ID" \
    --benchmark math500 \
    --split test \
    --model-key qwen25-7b-instruct \
    --model-path "$MODEL_PATH" \
    --gpu-id "$CUDA_VISIBLE_DEVICES" \
    --agents 3 \
    --reviewers 3 \
    --pool-state-scope all \
    --initial-prompt-style standard-mad \
    --channel-mode state \
    --temperature 1.0 \
    --resolve-temperature 0.2 \
    --top-p 1.0 \
    --max-tokens 4096 \
    --resolve-max-tokens 1536 \
    --max-model-len 8192 \
    --dtype bfloat16 \
    --seed 42 \
    --limit 0 \
    --steering-layer 16 \
    --steering-scale 1.0
fi

echo "[run] finished_at=$(date -Is)"
[ -e "$KV_SUMMARY" ] && cat "${KV_SUMMARY%.json}.md"
[ -e "$S_SUMMARY" ] && cat "${S_SUMMARY%.json}.md"
