#!/usr/bin/env bash
set -euo pipefail

HOME_ROOT=/hpc_stor03/sjtu_home/feiyang.ying
PROJECT_ROOT="$HOME_ROOT/AgentCommReliability"
RUNTIME_ROOT="$HOME_ROOT/acr_runtime"
VENV="$RUNTIME_ROOT/venv"
MODEL_DIR="$RUNTIME_ROOT/models/Qwen2.5-7B-Instruct"
REQUIREMENTS="$PROJECT_ROOT/config/sjtu_hpc_runtime_requirements.txt"

mkdir -p "$RUNTIME_ROOT/models" "$RUNTIME_ROOT/pip_cache" "$RUNTIME_ROOT/logs"

if [[ ! -x "$VENV/bin/python" ]]; then
  python3 -m venv --copies "$VENV"
fi

"$VENV/bin/python" -m pip install --upgrade pip
PIP_CACHE_DIR="$RUNTIME_ROOT/pip_cache" \
  "$VENV/bin/python" -m pip install -r "$REQUIREMENTS"

"$VENV/bin/python" - <<'PY'
import torch
import transformers

print("torch", torch.__version__)
print("torch_cuda", torch.version.cuda)
print("transformers", transformers.__version__)
PY

"$VENV/bin/modelscope" download \
  --model Qwen/Qwen2.5-7B-Instruct \
  --local_dir "$MODEL_DIR"

"$VENV/bin/python" - <<'PY'
from pathlib import Path
from transformers import AutoConfig, AutoTokenizer

model_dir = Path("/hpc_stor03/sjtu_home/feiyang.ying/acr_runtime/models/Qwen2.5-7B-Instruct")
config = AutoConfig.from_pretrained(model_dir, trust_remote_code=True, local_files_only=True)
tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True, local_files_only=True)
weight_bytes = sum(path.stat().st_size for path in model_dir.glob("*.safetensors"))
print("model_type", config.model_type)
print("vocab_size", len(tokenizer))
print("weight_gib", round(weight_bytes / 1024**3, 2))
print("model_dir", model_dir)
PY
