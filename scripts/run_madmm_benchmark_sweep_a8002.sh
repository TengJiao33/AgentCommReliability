#!/usr/bin/env bash
set -euo pipefail

ROOT=${ROOT:-/data/xuhaoming/yfy/research_workspace}
REPO=${REPO:-$ROOT/baselines/MAD-MM}
ENVPATH=${ENVPATH:-$ROOT/envs/mad-mm-vllm063}
LOG_DIR=${LOG_DIR:-$ROOT/logs}
RESULTS_DIR=${MAD_MM_SAVE_PATH:-$ROOT/results/mad-mm-benchmark-sweep}
GPU_ID=${MAD_MM_GPU_ID:-7}
MODEL_NAME=${MAD_MM_MODEL_NAME:-qwen2.5-7b}
SEED=${MAD_MM_SEED:-41}
STAMP=${MAD_MM_STAMP:-$(date +%Y%m%d_%H%M%S)}
RUN_LOG=${RUN_LOG:-$LOG_DIR/madmm_benchmark_sweep_${STAMP}.log}

# Format: dataset:sample_count. Use "full" for datasets where the evaluator
# should use its full local test set, such as AIME24/AIME25.
BENCHMARK_SPECS=${MAD_MM_BENCHMARK_SPECS:-"math:50 mmlu_pro:50 aime24:full aime25:full"}
METHODS=${MAD_MM_METHODS:-"cot naive objective"}

mkdir -p "$LOG_DIR" "$RESULTS_DIR" "$ROOT/hf_home" "$ROOT/torch_home" "$ROOT/pip_cache"

exec > >(tee -a "$RUN_LOG") 2>&1

echo "=== MAD-MM benchmark sweep ==="
date
hostname
whoami
echo "repo=$REPO"
echo "env=$ENVPATH"
echo "gpu=$GPU_ID"
echo "model=$MODEL_NAME"
echo "seed=$SEED"
echo "stamp=$STAMP"
echo "benchmarks=$BENCHMARK_SPECS"
echo "methods=$METHODS"
echo "results=$RESULTS_DIR"
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

run_method() {
  local dataset=$1
  local sample_count=$2
  local exp_name=$3
  local method=$4

  local common=(
    --model_name "$MODEL_NAME"
    --dataset "$dataset"
    --seed "$SEED"
    --gpu_id "$GPU_ID"
    --save_path "$RESULTS_DIR"
    --exp_name "$exp_name"
  )

  if [[ "$sample_count" != "full" ]]; then
    common+=(--sample_count "$sample_count")
  fi

  echo
  echo "=== dataset=$dataset sample_count=$sample_count method=$method ==="
  date

  case "$method" in
    cot)
      python chain_of_thoughts.py "${common[@]}"
      ;;
    naive)
      python multi_agent_debate.py "${common[@]}" --num_agents 3 --max_round 2 --prune_strategy naive
      ;;
    objective)
      python multi_agent_debate.py "${common[@]}" --num_agents 3 --max_round 2 --prune_strategy objective
      ;;
    subjective)
      python multi_agent_debate.py "${common[@]}" --num_agents 3 --max_round 2 --prune_strategy subjective
      ;;
    *)
      echo "Unknown method: $method" >&2
      return 2
      ;;
  esac
}

for spec in $BENCHMARK_SPECS; do
  dataset=${spec%%:*}
  sample_count=${spec#*:}
  sample_label=$sample_count
  if [[ "$sample_label" == "full" ]]; then
    sample_label=all
  fi
  exp_name="benchmark_sweep_${STAMP}_${dataset}_${sample_label}"

  for method in $METHODS; do
    run_method "$dataset" "$sample_count" "$exp_name" "$method"
  done
done

echo
echo "=== MAD-MM benchmark sweep complete ==="
date
echo "results=$RESULTS_DIR"
echo "stamp=$STAMP"
