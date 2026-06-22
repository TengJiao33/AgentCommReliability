#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
UPSTREAM="${UPSTREAM:-$WORKSPACE/baselines/PerspectiveGap/upstream}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-14b-perspectivegap-official-fullgrid}"
GPU_ID="${GPU_ID:-7}"
PORT="${PORT:-8081}"
RUN_ID="${RUN_ID:-20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-32768}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.85}"
RUN_TIMEOUT="${RUN_TIMEOUT:-28800}"
TASKS="${TASKS:-both}"
OUT_DIR="${OUT_DIR:-$WORKSPACE/experiments/$RUN_ID}"

mkdir -p "$OUT_DIR"
cd "$WORKSPACE"

SERVER_LOG="$OUT_DIR/vllm.log"
RUN_LOG="$OUT_DIR/run.log"
PREDICTIONS="$OUT_DIR/predictions_official_fullgrid.jsonl"
SCORES="$OUT_DIR/scores_official_fullgrid.jsonl"
SUMMARY_TXT="$OUT_DIR/summary_official_fullgrid.txt"
VALIDATION_JSON="$OUT_DIR/validation_official_fullgrid.json"

for required in "$PY" "$UPSTREAM/scripts/run_model_predictions.py" "$UPSTREAM/scripts/score_predictions.py"; do
  if [[ ! -e "$required" ]]; then
    echo "[perspectivegap-fullgrid] missing required file: $required" >&2
    exit 2
  fi
done

SERVER_PID=""
cleanup() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

{
  echo "[perspectivegap-fullgrid] run_id=${RUN_ID}"
  echo "[perspectivegap-fullgrid] workspace=${WORKSPACE}"
  echo "[perspectivegap-fullgrid] upstream=${UPSTREAM}"
  echo "[perspectivegap-fullgrid] model=${MODEL_PATH} served=${SERVED_MODEL} gpu=${GPU_ID} port=${PORT}"
  echo "[perspectivegap-fullgrid] tasks=${TASKS} seeds=1,42 scenarios=all"
  echo "[perspectivegap-fullgrid] max_model_len=${MAX_MODEL_LEN} gpu_memory_utilization=${GPU_MEMORY_UTILIZATION} run_timeout=${RUN_TIMEOUT}"
  echo "[perspectivegap-fullgrid] predictions=${PREDICTIONS}"
  echo "[perspectivegap-fullgrid] scores=${SCORES}"
  echo "[perspectivegap-fullgrid] gpu before:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
} | tee "$RUN_LOG"

CUDA_VISIBLE_DEVICES="$GPU_ID" nohup "$PY" -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_PATH" \
  --served-model-name "$SERVED_MODEL" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --dtype bfloat16 \
  --max-model-len "$MAX_MODEL_LEN" \
  --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION" \
  --disable-log-requests \
  >"$SERVER_LOG" 2>&1 &
SERVER_PID="$!"
echo "[perspectivegap-fullgrid] server_pid=${SERVER_PID}" | tee -a "$RUN_LOG"

for attempt in $(seq 1 180); do
  if curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[perspectivegap-fullgrid] vLLM ready after ${attempt} checks" | tee -a "$RUN_LOG"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[perspectivegap-fullgrid] vLLM exited early; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "180" ]]; then
    echo "[perspectivegap-fullgrid] timed out waiting for vLLM; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

echo "[perspectivegap-fullgrid] running official PerspectiveGap full grid" | tee -a "$RUN_LOG"
OPENAI_API_KEY=EMPTY HF_HUB_OFFLINE=1 PYTHONPATH="$UPSTREAM/src" timeout "$RUN_TIMEOUT" "$PY" \
  "$UPSTREAM/scripts/run_model_predictions.py" \
  --provider openai-compatible \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --api-key-env OPENAI_API_KEY \
  --model "$SERVED_MODEL" \
  --shuffle-seed 1 \
  --shuffle-seed 42 \
  --tasks "$TASKS" \
  --out "$PREDICTIONS" \
  2>&1 | tee "$OUT_DIR/runner.stdout.log"
echo "[perspectivegap-fullgrid] runner_status=${PIPESTATUS[0]}" | tee -a "$RUN_LOG"

echo "[perspectivegap-fullgrid] scoring official predictions" | tee -a "$RUN_LOG"
HF_HUB_OFFLINE=1 PYTHONPATH="$UPSTREAM/src" "$PY" \
  "$UPSTREAM/scripts/score_predictions.py" \
  --predictions "$PREDICTIONS" \
  --out "$SCORES" \
  2>&1 | tee "$SUMMARY_TXT"

HF_HUB_OFFLINE=1 "$PY" - "$PREDICTIONS" "$SCORES" "$VALIDATION_JSON" <<'PY'
import json
import sys
from collections import Counter
from pathlib import Path

pred_path = Path(sys.argv[1])
score_path = Path(sys.argv[2])
out_path = Path(sys.argv[3])

preds = [json.loads(line) for line in pred_path.read_text(encoding="utf-8").splitlines() if line.strip()]
scores = [json.loads(line) for line in score_path.read_text(encoding="utf-8").splitlines() if line.strip()]
validation = {
    "prediction_rows": len(preds),
    "score_rows": len(scores),
    "unique_prediction_keys": len({(row.get("scenario_id"), row.get("shuffle_seed"), row.get("task")) for row in preds}),
    "unique_score_keys": len({(row.get("base_evaluation_id") or row.get("evaluation_id", "").split("__task_", 1)[0], row.get("task")) for row in scores}),
    "tasks": dict(Counter(row.get("task") for row in preds)),
    "status": dict(Counter(row.get("status", "missing") for row in preds)),
    "models": sorted({row.get("model") for row in preds}),
    "scenario_count": len({row.get("scenario_id") for row in preds}),
    "seeds": sorted({row.get("shuffle_seed") for row in preds}),
}
out_path.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(validation, indent=2, ensure_ascii=False))
PY

{
  echo "[perspectivegap-fullgrid] validation:"
  cat "$VALIDATION_JSON"
  echo "[perspectivegap-fullgrid] gpu after runner before cleanup:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
} | tee -a "$RUN_LOG"
