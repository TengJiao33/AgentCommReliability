#!/usr/bin/env bash
set -euo pipefail
WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
RUN_ID=${RUN_ID:-20260706-a8002-math500-mca-pre-kv-question-only-standard-qwen25-7b-full}
PY=${PY:-$WORK/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-2}
export CUDA_VISIBLE_DEVICES="$GPU_ID"
export TOKENIZERS_PARALLELISM=false
export HF_HOME=${HF_HOME:-$WORK/.cache/huggingface}
export TRANSFORMERS_CACHE=${TRANSFORMERS_CACHE:-$WORK/.cache/huggingface}
export PYTHONPATH="$WORK/scripts:${PYTHONPATH:-}"
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}
cd "$WORK"
echo "[resume] started_at=$(date -Is)"
echo "[resume] host=$(hostname) run_id=$RUN_ID gpu=$CUDA_VISIBLE_DEVICES"
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
"$PY" -m py_compile scripts/mca_pre_answer_runner.py scripts/run_mca_pre_kv_cache.py scripts/mca_hidden_channel_runner.py
timeout 24h "$PY" scripts/run_mca_pre_kv_cache.py \
  --work-dir "$WORK" \
  --run-id "$RUN_ID" \
  --benchmark math500 \
  --split test \
  --model-key qwen25-7b-instruct \
  --model-path "$MODEL_PATH" \
  --gpu-id "$GPU_ID" \
  --agents 3 \
  --reviewers 3 \
  --pre-state-stage question_only \
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
  --resume
echo "[resume] finished_at=$(date -Is)"
cat "$WORK/experiments/$RUN_ID/math500-qwen25-7b-instruct-mca-pre-kv-cache-question_only-state/summary.md"
