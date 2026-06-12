#!/usr/bin/env bash
set -euo pipefail

ROOT=${ROOT:-/data/xuhaoming/yfy/research_workspace}
REPO=${REPO:-$ROOT/baselines/MAD-MM}
ENVPATH=${ENVPATH:-$ROOT/envs/mad-mm-vllm063}
LOG_DIR=${LOG_DIR:-$ROOT/logs}
RESULTS_DIR=${MAD_MM_SAVE_PATH:-$ROOT/results/mad-mm-short-subset}
RUN_LOG=${RUN_LOG:-$LOG_DIR/madmm_short_mad_objective_$(date +%Y%m%d_%H%M%S).log}
GPU_ID=${MAD_MM_GPU_ID:-7}

mkdir -p "$LOG_DIR" "$RESULTS_DIR" "$ROOT/hf_home" "$ROOT/torch_home" "$ROOT/pip_cache"

exec > >(tee -a "$RUN_LOG") 2>&1

echo "=== MAD-MM short step: MAD-MM objective masking ==="
date
hostname
whoami
echo "repo=$REPO"
echo "env=$ENVPATH"
echo "gpu=$GPU_ID"
echo "results=$RESULTS_DIR"
echo "log=$RUN_LOG"

cd "$REPO"

export HF_HOME=$ROOT/hf_home
export TORCH_HOME=$ROOT/torch_home
export PIP_CACHE_DIR=$ROOT/pip_cache
export PATH=$ENVPATH/bin:$PATH

echo "git_head=$(git rev-parse HEAD)"
echo "gpu_preflight:"
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits

python multi_agent_debate.py \
  --model_name qwen2.5-14b \
  --dataset gsm8k \
  --seed 41 \
  --num_agents 3 \
  --max_round 2 \
  --prune_strategy objective \
  --gpu_id "$GPU_ID" \
  --save_path "$RESULTS_DIR"

echo "=== MAD-MM objective masking complete ==="
date
