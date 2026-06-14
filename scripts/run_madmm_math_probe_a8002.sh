#!/usr/bin/env bash
set -euo pipefail

ROOT=${ROOT:-/data/xuhaoming/yfy/research_workspace}
REPO=${REPO:-$ROOT/baselines/MAD-MM}
ENVPATH=${ENVPATH:-$ROOT/envs/mad-mm-vllm063}
LOG_DIR=${LOG_DIR:-$ROOT/logs}
RESULTS_DIR=${MAD_MM_SAVE_PATH:-$ROOT/results/mad-mm-math-probe}
RUN_LOG=${RUN_LOG:-$LOG_DIR/madmm_math_probe_$(date +%Y%m%d_%H%M%S).log}
GPU_ID=${MAD_MM_GPU_ID:-7}
MODEL_NAME=${MAD_MM_MODEL_NAME:-qwen2.5-7b}
DATASET=${MAD_MM_DATASET:-math}
SEED=${MAD_MM_SEED:-41}
SAMPLE_COUNT=${MAD_MM_SAMPLE_COUNT:-50}
EXP_NAME=${MAD_MM_EXP_NAME:-math_probe${SAMPLE_COUNT}}

mkdir -p "$LOG_DIR" "$RESULTS_DIR" "$ROOT/hf_home" "$ROOT/torch_home" "$ROOT/pip_cache"

exec > >(tee -a "$RUN_LOG") 2>&1

echo "=== MAD-MM benchmark probe ==="
date
hostname
whoami
echo "repo=$REPO"
echo "env=$ENVPATH"
echo "gpu=$GPU_ID"
echo "model=$MODEL_NAME"
echo "dataset=$DATASET"
echo "sample_count=$SAMPLE_COUNT"
echo "results=$RESULTS_DIR"
echo "exp_name=$EXP_NAME"
echo "log=$RUN_LOG"

cd "$REPO"

export HF_HOME=$ROOT/hf_home
export TORCH_HOME=$ROOT/torch_home
export PIP_CACHE_DIR=$ROOT/pip_cache
export PATH=$ENVPATH/bin:$PATH

echo "git_head=$(git rev-parse HEAD)"
git status --short --branch

echo "gpu_preflight:"
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits

run_step() {
  local label=$1
  shift
  echo
  echo "=== $label ==="
  date
  "$@"
}

COMMON=(
  --model_name "$MODEL_NAME"
  --dataset "$DATASET"
  --seed "$SEED"
  --gpu_id "$GPU_ID"
  --save_path "$RESULTS_DIR"
  --exp_name "$EXP_NAME"
  --sample_count "$SAMPLE_COUNT"
)

run_step "CoT baseline" \
  python chain_of_thoughts.py "${COMMON[@]}"

run_step "MAD naive communication" \
  python multi_agent_debate.py "${COMMON[@]}" --num_agents 3 --max_round 2 --prune_strategy naive

run_step "MAD-MM objective masking" \
  python multi_agent_debate.py "${COMMON[@]}" --num_agents 3 --max_round 2 --prune_strategy objective

echo
echo "=== MAD-MM benchmark probe complete ==="
date
