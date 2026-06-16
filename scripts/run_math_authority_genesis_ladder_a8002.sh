#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-14b-math-authority-genesis-ladder}"
GPU_ID="${GPU_ID:-7}"
PORT="${PORT:-8039}"
RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M)}"
RUN_ID="${RUN_ID:-${RUN_STAMP}-a8002-math-authority-genesis-ladder-qwen25-14b}"
MAX_TOKENS="${MAX_TOKENS:-768}"
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-420}"
RUN_TIMEOUT="${RUN_TIMEOUT:-21600}"

PACKET="${PACKET:-$WORKSPACE/experiments/20260615-local-math-authority-genesis-ladder-packet/math_authority_genesis_ladder_packet.jsonl}"
LOG_DIR="${LOG_DIR:-$WORKSPACE/logs}"
OUT_ROOT="${OUT_ROOT:-$WORKSPACE/experiments}"
OUT_DIR="${OUT_DIR:-$OUT_ROOT/$RUN_ID}"
EVAL_DIR="${EVAL_DIR:-$OUT_DIR/evaluation}"
SERVER_LOG="$LOG_DIR/math-authority-genesis-ladder-vllm-${RUN_STAMP}.log"
RUN_LOG="$LOG_DIR/math-authority-genesis-ladder-${RUN_STAMP}.log"

mkdir -p "$LOG_DIR" "$OUT_ROOT" "$OUT_DIR"
cd "$WORKSPACE"

SERVER_PID=""
cleanup() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "[math-authority-genesis-ladder] run_id=${RUN_ID}" | tee "$RUN_LOG"
echo "[math-authority-genesis-ladder] model=${MODEL_PATH} served=${SERVED_MODEL} gpu=${GPU_ID} port=${PORT}" | tee -a "$RUN_LOG"
echo "[math-authority-genesis-ladder] packet=${PACKET}" | tee -a "$RUN_LOG"
echo "[math-authority-genesis-ladder] max_tokens=${MAX_TOKENS} request_timeout=${REQUEST_TIMEOUT} run_timeout=${RUN_TIMEOUT}" | tee -a "$RUN_LOG"

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

for attempt in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[math-authority-genesis-ladder] vLLM ready after ${attempt} checks" | tee -a "$RUN_LOG"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[math-authority-genesis-ladder] vLLM exited early; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "120" ]]; then
    echo "[math-authority-genesis-ladder] timed out waiting for vLLM; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

echo "[math-authority-genesis-ladder] running packet -> ${OUT_DIR}" | tee -a "$RUN_LOG"
timeout "$RUN_TIMEOUT" "$PY" scripts/run_pact_public_state_field_packet.py \
  --packet "$PACKET" \
  --out-dir "$OUT_DIR" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --model "$SERVED_MODEL" \
  --api-key EMPTY \
  --temperature 0 \
  --max-tokens "$MAX_TOKENS" \
  --timeout "$REQUEST_TIMEOUT" \
  --keep-going \
  --progress-every 25 \
  >"$OUT_DIR/runner.stdout.jsonl" 2>"$OUT_DIR/runner.stderr.log"

echo "[math-authority-genesis-ladder] evaluating -> ${EVAL_DIR}" | tee -a "$RUN_LOG"
"$PY" scripts/evaluate_math_authority_genesis_ladder.py \
  --packet "$PACKET" \
  --outputs "$OUT_DIR/outputs.jsonl" \
  --prediction-source outputs \
  --out-dir "$EVAL_DIR" \
  >"$OUT_DIR/evaluator.stdout.json" 2>"$OUT_DIR/evaluator.stderr.log"

echo "[math-authority-genesis-ladder] completed ${RUN_ID}" | tee -a "$RUN_LOG"
echo "[math-authority-genesis-ladder] outputs=${OUT_DIR}" | tee -a "$RUN_LOG"
