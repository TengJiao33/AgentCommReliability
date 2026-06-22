#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-14b-pg40-direct-routing}"
GPU_ID="${GPU_ID:-7}"
PORT="${PORT:-8079}"
RUN_ID="${RUN_ID:-20260619-a8002-pg40-direct-routing-limit5-qwen25-14b}"
LIMIT="${LIMIT:-5}"
MAX_TOKENS="${MAX_TOKENS:-2048}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.80}"
RUN_TIMEOUT="${RUN_TIMEOUT:-1800}"
PACKET="${PACKET:-$WORKSPACE/experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl}"
OUT_DIR="${OUT_DIR:-$WORKSPACE/experiments/$RUN_ID}"

mkdir -p "$OUT_DIR"
cd "$WORKSPACE"

SERVER_LOG="$OUT_DIR/vllm.log"
RUN_LOG="$OUT_DIR/run.log"
PACKET_RUN="$OUT_DIR/packet_limit${LIMIT}.jsonl"
PREDICTIONS="$OUT_DIR/predictions_direct.jsonl"
SCORES="$OUT_DIR/scores_direct.jsonl"
SUMMARY_MD="$OUT_DIR/summary_direct.md"
SUMMARY_JSON="$OUT_DIR/summary_direct.json"

if [[ ! -s "$PACKET" ]]; then
  echo "[pg40-direct] missing required file: $PACKET" >&2
  exit 2
fi

if [[ "$LIMIT" -gt 0 ]]; then
  head -n "$LIMIT" "$PACKET" > "$PACKET_RUN"
else
  cp "$PACKET" "$PACKET_RUN"
fi

SERVER_PID=""
cleanup() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

{
  echo "[pg40-direct] run_id=${RUN_ID}"
  echo "[pg40-direct] workspace=${WORKSPACE}"
  echo "[pg40-direct] model=${MODEL_PATH} served=${SERVED_MODEL} gpu=${GPU_ID} port=${PORT}"
  echo "[pg40-direct] packet=${PACKET}"
  echo "[pg40-direct] packet_run=${PACKET_RUN}"
  echo "[pg40-direct] limit=${LIMIT} max_model_len=${MAX_MODEL_LEN} max_tokens=${MAX_TOKENS} gpu_memory_utilization=${GPU_MEMORY_UTILIZATION} run_timeout=${RUN_TIMEOUT}"
  echo "[pg40-direct] gpu before:"
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
echo "[pg40-direct] server_pid=${SERVER_PID}" | tee -a "$RUN_LOG"

for attempt in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[pg40-direct] vLLM ready after ${attempt} checks" | tee -a "$RUN_LOG"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[pg40-direct] vLLM exited early; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "120" ]]; then
    echo "[pg40-direct] timed out waiting for vLLM; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

echo "[pg40-direct] running prompts -> ${PREDICTIONS}" | tee -a "$RUN_LOG"
OPENAI_API_KEY=EMPTY timeout "$RUN_TIMEOUT" "$PY" scripts/run_pg40_direct_routing_openai_compatible.py \
  --packet "$PACKET_RUN" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --model "$SERVED_MODEL" \
  --out "$PREDICTIONS" \
  --temperature 0 \
  --max-tokens "$MAX_TOKENS" \
  2>&1 | tee "$OUT_DIR/runner.stdout.log"
echo "[pg40-direct] runner_status=${PIPESTATUS[0]}" | tee -a "$RUN_LOG"

"$PY" scripts/score_perspectivegap_tight_budget.py \
  --packet "$PACKET_RUN" \
  --predictions "$PREDICTIONS" \
  --out "$SCORES" \
  --summary-out "$SUMMARY_MD" \
  > "$SUMMARY_JSON"

{
  echo "[pg40-direct] predictions=$(wc -l < "$PREDICTIONS")"
  echo "[pg40-direct] summary:"
  cat "$SUMMARY_MD"
  echo "[pg40-direct] gpu after runner before cleanup:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
} | tee -a "$RUN_LOG"
