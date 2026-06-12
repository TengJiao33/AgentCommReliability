#!/usr/bin/env bash
set -euo pipefail

ROOT=${ROOT:-/data/xuhaoming/yfy/research_workspace}
REPO=${REPO:-$ROOT/baselines/MAD-MM}
ENVPATH=${ENVPATH:-$ROOT/envs/mad-mm-vllm063}
LOG_DIR=${LOG_DIR:-$ROOT/logs}
RESULTS_DIR=${MAD_MM_SAVE_PATH:-$ROOT/results/mad-mm-standard-main}
RUN_LOG=${RUN_LOG:-$LOG_DIR/madmm_standard_main_$(date +%Y%m%d_%H%M%S).log}

mkdir -p "$LOG_DIR" "$RESULTS_DIR" "$ROOT/hf_home" "$ROOT/torch_home" "$ROOT/pip_cache" "$ROOT/modelscope_cache"

exec > >(tee -a "$RUN_LOG") 2>&1

echo "=== MAD-MM standard main reproduction ==="
date
hostname
whoami
echo "repo=$REPO"
echo "env=$ENVPATH"
echo "results=$RESULTS_DIR"
echo "log=$RUN_LOG"

cd "$REPO"

export HF_HOME=$ROOT/hf_home
export TORCH_HOME=$ROOT/torch_home
export PIP_CACHE_DIR=$ROOT/pip_cache
export MODELSCOPE_CACHE=$ROOT/modelscope_cache
export MAD_MM_GPUS=${MAD_MM_GPUS:-2,3,4,5}
export MAD_MM_SAVE_PATH=$RESULTS_DIR
export PATH=$ENVPATH/bin:$PATH

echo "git_head=$(git rev-parse HEAD)"
git status --short --branch

python - <<'PY'
import datasets
import torch
import transformers
import vllm

print("python_imports=ok")
print("vllm", vllm.__version__)
print("torch", torch.__version__)
print("transformers", transformers.__version__)
print("datasets", datasets.__version__)
PY

echo "gpu_preflight:"
nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits

echo "model_shards:"
for path in \
  /mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
  /mnt/quarkfs/share_model/Qwen2.5-32B-Instruct \
  /mnt/quarkfs/share_model/Qwen2.5-72B-Instruct
do
  printf "%s " "$path"
  find "$path" -maxdepth 1 -name 'model-*.safetensors' | wc -l
done

echo "=== run_all_model_baselines.sh ==="
bash scripts/run_all_model_baselines.sh

echo "=== run_all_mad_mm_variants.sh ==="
bash scripts/run_all_mad_mm_variants.sh

echo "=== complete ==="
date
