#!/usr/bin/env bash
set -euo pipefail

WORK=${WORK:-/data/xuhaoming/yfy/research_workspace}
PY=${PY:-$WORK/envs/mad-mm-vllm063/bin/python}
MODEL_PATH=${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}
GPU_ID=${GPU_ID:-7}

export CUDA_VISIBLE_DEVICES="$GPU_ID"
export TOKENIZERS_PARALLELISM=false
export HF_HOME=${HF_HOME:-$WORK/.cache/huggingface}
export TRANSFORMERS_CACHE=${TRANSFORMERS_CACHE:-$WORK/.cache/huggingface}
export PYTHONPATH="$WORK/scripts:${PYTHONPATH:-}"
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}

cd "$WORK"

echo "[serial] started_at=$(date -Is)"
echo "[serial] host=$(hostname) gpu=$CUDA_VISIBLE_DEVICES"
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits

"$PY" -m py_compile \
  scripts/run_mca_pre_kv_then_mad.py \
  scripts/mca_pre_answer_runner.py \
  scripts/mca_hidden_channel_runner.py

run_packet() {
  local split="$1"
  local run_id="$2"
  local expected_rows="$3"

  echo "[serial] split=$split run_id=$run_id expected_rows=$expected_rows started_at=$(date -Is)"
  wc -l "$WORK/data/benchmarks/math500/$split/canonical.jsonl"

  timeout 72h "$PY" scripts/run_mca_pre_kv_then_mad.py \
    --work-dir "$WORK" \
    --run-id "$run_id" \
    --benchmark math500 \
    --split "$split" \
    --model-key qwen25-7b-instruct \
    --model-path "$MODEL_PATH" \
    --gpu-id "$GPU_ID" \
    --agents 3 \
    --pre-state-temperature 0.7 \
    --first-round-temperature 0.2 \
    --debate-temperature 1.0 \
    --top-p 1.0 \
    --first-round-max-tokens 1536 \
    --debate-max-tokens 4096 \
    --batch-size 3 \
    --max-model-len 8192 \
    --dtype bfloat16 \
    --seed 42 \
    --limit 0 \
    --resume

  local out="$WORK/experiments/$run_id/math500-qwen25-7b-instruct-mca-pre-kv-then-mad"
  echo "[serial] split=$split finished_at=$(date -Is)"
  wc -l "$out/records.jsonl"
  cat "$out/summary.md"
}

run_packet "mca_disagreement_v1" "20260707-a8002-gpu7-mca-matrix-disagreement-qwen25-7b" 221
run_packet "mca_gold_contrast_v1" "20260707-a8002-gpu7-mca-matrix-gold-contrast-qwen25-7b" 142

echo "[serial] finished_at=$(date -Is)"
