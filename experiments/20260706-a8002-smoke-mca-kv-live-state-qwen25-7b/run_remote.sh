#!/usr/bin/env bash
set -euo pipefail

WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-20260706-a8002-smoke-mca-kv-live-state-qwen25-7b}
PY=${PY:-$WORK/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-6}

export CUDA_VISIBLE_DEVICES="$GPU_ID"
export TOKENIZERS_PARALLELISM=false
export HF_HOME=${HF_HOME:-$WORK/.cache/huggingface}
export TRANSFORMERS_CACHE=${TRANSFORMERS_CACHE:-$WORK/.cache/huggingface}
export PYTHONPATH="$WORK/scripts:${PYTHONPATH:-}"

cd "$WORK"
echo "[run] started_at=$(date -Is)"
echo "[run] host=$(hostname) work=$WORK run_id=$RUN_ID gpu=$CUDA_VISIBLE_DEVICES"
echo "[run] python=$PY"
echo "[run] model=$MODEL_PATH"
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits

"$PY" -m py_compile scripts/mca_hidden_channel_runner.py scripts/run_mca_kv_cache.py

timeout 30m "$PY" scripts/run_mca_kv_cache.py \
  --work-dir "$WORK" \
  --run-id "$RUN_ID" \
  --benchmark math500 \
  --split test \
  --model-key qwen25-7b-instruct \
  --model-path "$MODEL_PATH" \
  --gpu-id "$GPU_ID" \
  --agents 3 \
  --reviewers 3 \
  --pool-state-scope all \
  --initial-prompt-style standard-mad \
  --channel-mode state \
  --temperature 1.0 \
  --resolve-temperature 0.2 \
  --top-p 1.0 \
  --max-tokens 512 \
  --resolve-max-tokens 512 \
  --max-model-len 4096 \
  --dtype bfloat16 \
  --seed 42 \
  --limit 2

echo "[run] finished_at=$(date -Is)"
cat "$WORK/experiments/$RUN_ID/math500-qwen25-7b-instruct-mca-kv-cache-state-all/summary.md"
