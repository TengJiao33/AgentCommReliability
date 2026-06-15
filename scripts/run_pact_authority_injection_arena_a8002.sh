#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-14b-authority-injection-arena}"
GPU_ID="${GPU_ID:-7}"
PORT="${PORT:-8035}"
RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M)}"
RUN_ID="${RUN_ID:-${RUN_STAMP}-a8002-pact-authority-injection-arena-qwen25-14b}"

PACKET="${PACKET:-$WORKSPACE/experiments/20260615-local-pact-authority-injection-arena-packet/arena_packet.jsonl}"
LOG_DIR="${LOG_DIR:-$WORKSPACE/logs}"
OUT_ROOT="${OUT_ROOT:-$WORKSPACE/experiments}"
OUT_DIR="${OUT_DIR:-$OUT_ROOT/$RUN_ID}"
EVAL_DIR="${EVAL_DIR:-$OUT_DIR/evaluation}"
SERVER_LOG="$LOG_DIR/pact-authority-injection-arena-vllm-${RUN_STAMP}.log"
RUN_LOG="$LOG_DIR/pact-authority-injection-arena-${RUN_STAMP}.log"

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

echo "[authority-injection-arena] run_id=${RUN_ID}" | tee "$RUN_LOG"
echo "[authority-injection-arena] model=${MODEL_PATH} served=${SERVED_MODEL} gpu=${GPU_ID} port=${PORT}" | tee -a "$RUN_LOG"
echo "[authority-injection-arena] packet=${PACKET}" | tee -a "$RUN_LOG"

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
    echo "[authority-injection-arena] vLLM ready after ${attempt} checks" | tee -a "$RUN_LOG"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[authority-injection-arena] vLLM exited early; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "120" ]]; then
    echo "[authority-injection-arena] timed out waiting for vLLM; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

echo "[authority-injection-arena] running packet -> ${OUT_DIR}" | tee -a "$RUN_LOG"
timeout 7200 "$PY" scripts/run_pact_public_state_field_packet.py \
  --packet "$PACKET" \
  --out-dir "$OUT_DIR" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --model "$SERVED_MODEL" \
  --api-key EMPTY \
  --temperature 0 \
  --max-tokens 64 \
  --timeout 180 \
  --keep-going \
  --progress-every 25 \
  >"$OUT_DIR/runner.stdout.jsonl" 2>"$OUT_DIR/runner.stderr.log"

echo "[authority-injection-arena] evaluating -> ${EVAL_DIR}" | tee -a "$RUN_LOG"
"$PY" scripts/evaluate_pact_authority_injection_arena.py \
  --packet "$PACKET" \
  --outputs "$OUT_DIR/outputs.jsonl" \
  --prediction-source outputs \
  --out-dir "$EVAL_DIR" \
  >"$OUT_DIR/evaluator.stdout.json" 2>"$OUT_DIR/evaluator.stderr.log"

echo "[authority-injection-arena] completed ${RUN_ID}" | tee -a "$RUN_LOG"
echo "[authority-injection-arena] outputs=${OUT_DIR}" | tee -a "$RUN_LOG"
