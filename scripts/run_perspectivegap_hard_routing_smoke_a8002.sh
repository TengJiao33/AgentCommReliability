#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-7b-perspectivegap-hard-smoke4}"
GPU_ID="${GPU_ID:-7}"
PORT="${PORT:-8065}"
RUN_ID="${RUN_ID:-20260618-a8002-perspectivegap-hard-routing-smoke4-qwen25-7b}"
MAX_TOKENS="${MAX_TOKENS:-1536}"
RUN_TIMEOUT="${RUN_TIMEOUT:-1800}"
PACKET="${PACKET:-$WORKSPACE/experiments/20260618-local-perspectivegap-hard-routing-v0/hard_packet_smoke4.jsonl}"
OUT_DIR="${OUT_DIR:-$WORKSPACE/experiments/$RUN_ID}"

mkdir -p "$OUT_DIR"
cd "$WORKSPACE"

SERVER_LOG="$OUT_DIR/vllm.log"
RUN_LOG="$OUT_DIR/run.log"
PREDICTIONS="$OUT_DIR/predictions.jsonl"
SCORES="$OUT_DIR/scores.jsonl"
SUMMARY_MD="$OUT_DIR/summary.md"
SUMMARY_JSON="$OUT_DIR/summary.json"

SERVER_PID=""
cleanup() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

{
  echo "[hard-routing-smoke] run_id=${RUN_ID}"
  echo "[hard-routing-smoke] workspace=${WORKSPACE}"
  echo "[hard-routing-smoke] model=${MODEL_PATH} served=${SERVED_MODEL} gpu=${GPU_ID} port=${PORT}"
  echo "[hard-routing-smoke] packet=${PACKET}"
  echo "[hard-routing-smoke] max_tokens=${MAX_TOKENS} run_timeout=${RUN_TIMEOUT}"
  echo "[hard-routing-smoke] gpu before:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
} | tee "$RUN_LOG"

CUDA_VISIBLE_DEVICES="$GPU_ID" nohup "$PY" -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_PATH" \
  --served-model-name "$SERVED_MODEL" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --dtype bfloat16 \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --disable-log-requests \
  >"$SERVER_LOG" 2>&1 &
SERVER_PID="$!"
echo "[hard-routing-smoke] server_pid=${SERVER_PID}" | tee -a "$RUN_LOG"

for attempt in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[hard-routing-smoke] vLLM ready after ${attempt} checks" | tee -a "$RUN_LOG"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[hard-routing-smoke] vLLM exited early; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "120" ]]; then
    echo "[hard-routing-smoke] timed out waiting for vLLM; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

echo "[hard-routing-smoke] running prompts -> ${PREDICTIONS}" | tee -a "$RUN_LOG"
OPENAI_API_KEY=EMPTY timeout "$RUN_TIMEOUT" "$PY" scripts/run_perspectivegap_hard_routing_openai_compatible.py \
  --packet "$PACKET" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --model "$SERVED_MODEL" \
  --out "$PREDICTIONS" \
  --temperature 0 \
  --max-tokens "$MAX_TOKENS" \
  2>&1 | tee "$OUT_DIR/runner.stdout.log"
echo "[hard-routing-smoke] runner_status=${PIPESTATUS[0]}" | tee -a "$RUN_LOG"

"$PY" scripts/score_perspectivegap_hard_routing.py \
  --packet "$PACKET" \
  --predictions "$PREDICTIONS" \
  --out "$SCORES" \
  --summary-out "$SUMMARY_MD" \
  > "$SUMMARY_JSON"

{
  echo "[hard-routing-smoke] predictions=$(wc -l < "$PREDICTIONS")"
  echo "[hard-routing-smoke] summary:"
  cat "$SUMMARY_MD"
  echo "[hard-routing-smoke] gpu after runner before cleanup:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
} | tee -a "$RUN_LOG"
