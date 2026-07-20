#!/usr/bin/env bash
set -euo pipefail

HOME_ROOT=/hpc_stor03/sjtu_home/feiyang.ying
PROJECT_ROOT="$HOME_ROOT/AgentCommReliability"
PYTHON="$HOME_ROOT/acr_runtime/venv/bin/python"
MODEL="$HOME_ROOT/acr_runtime/models/Qwen2.5-7B-Instruct"
RUN_ID=${RUN_ID:-20260720-sjtu-qtoken-smoke-qwen25-7b}
LIMIT=${LIMIT:-3}
MAX_NEW_TOKENS=${MAX_NEW_TOKENS:-256}
MAX_MODEL_LEN=${MAX_MODEL_LEN:-4096}
SHARD_COUNT=${SHARD_COUNT:-1}
SHARD_INDEX=${SHARD_INDEX:-0}

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

test -x "$PYTHON"
test -f "$MODEL/config.json"
test -f "$PROJECT_ROOT/data/benchmarks/math500/mca_disagreement_v1/canonical.jsonl"

cd "$PROJECT_ROOT"
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader
"$PYTHON" -c 'import torch, transformers; print("torch", torch.__version__, "cuda", torch.version.cuda); print("transformers", transformers.__version__)'

"$PYTHON" scripts/run_mca_question_token_anchored_delta.py \
  --work-dir "$PROJECT_ROOT" \
  --run-id "$RUN_ID" \
  --benchmark math500 \
  --split mca_disagreement_v1 \
  --model-key qwen25-7b-instruct \
  --model-path "$MODEL" \
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
  --max-new-tokens "$MAX_NEW_TOKENS" \
  --max-model-len "$MAX_MODEL_LEN" \
  --dtype bfloat16 \
  --seed 42 \
  --limit "$LIMIT" \
  --shard-count "$SHARD_COUNT" \
  --shard-index "$SHARD_INDEX"
