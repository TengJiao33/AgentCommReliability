#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-14b-hiddenbench}"
GPU_ID="${GPU_ID:-7}"
PORT="${PORT:-8047}"
RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M)}"
RUN_ID="${RUN_ID:-${RUN_STAMP}-a8002-hiddenbench-qwen25-14b}"
LIMIT="${LIMIT:-12}"
MAX_TOKENS="${MAX_TOKENS:-220}"
REQUEST_TIMEOUT="${REQUEST_TIMEOUT:-240}"
RUN_TIMEOUT="${RUN_TIMEOUT:-10800}"
CONDITIONS="${CONDITIONS:-}"
INCLUDE_PROMPTS="${INCLUDE_PROMPTS:-0}"

BENCHMARK="${BENCHMARK:-$WORKSPACE/data/external/hiddenbench/benchmark.json}"
LOG_DIR="${LOG_DIR:-$WORKSPACE/logs}"
OUT_ROOT="${OUT_ROOT:-$WORKSPACE/experiments}"
OUT_DIR="${OUT_DIR:-$OUT_ROOT/$RUN_ID}"
SERVER_LOG="$LOG_DIR/hiddenbench-vllm-${RUN_STAMP}.log"
RUN_LOG="$LOG_DIR/hiddenbench-probe-${RUN_STAMP}.log"

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

echo "[hiddenbench] run_id=${RUN_ID}" | tee "$RUN_LOG"
echo "[hiddenbench] model=${MODEL_PATH} served=${SERVED_MODEL} gpu=${GPU_ID} port=${PORT}" | tee -a "$RUN_LOG"
echo "[hiddenbench] benchmark=${BENCHMARK} limit=${LIMIT}" | tee -a "$RUN_LOG"
echo "[hiddenbench] conditions=${CONDITIONS:-default} include_prompts=${INCLUDE_PROMPTS}" | tee -a "$RUN_LOG"

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
    echo "[hiddenbench] vLLM ready after ${attempt} checks" | tee -a "$RUN_LOG"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[hiddenbench] vLLM exited early; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "120" ]]; then
    echo "[hiddenbench] timed out waiting for vLLM; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

CONDITION_ARGS=()
if [[ -n "$CONDITIONS" ]]; then
  read -r -a CONDITION_ARGS <<< "$CONDITIONS"
  CONDITION_ARGS=(--conditions "${CONDITION_ARGS[@]}")
fi

PROMPT_ARGS=()
if [[ "$INCLUDE_PROMPTS" == "1" ]]; then
  PROMPT_ARGS=(--include-prompts)
fi

echo "[hiddenbench] running probe -> ${OUT_DIR}" | tee -a "$RUN_LOG"
timeout "$RUN_TIMEOUT" "$PY" scripts/run_hiddenbench_communication_probe.py \
  --benchmark "$BENCHMARK" \
  --out-dir "$OUT_DIR" \
  --run-id "$RUN_ID" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --model "$SERVED_MODEL" \
  --api-key EMPTY \
  --temperature 0 \
  --max-tokens "$MAX_TOKENS" \
  --request-timeout "$REQUEST_TIMEOUT" \
  --limit "$LIMIT" \
  "${CONDITION_ARGS[@]}" \
  "${PROMPT_ARGS[@]}" \
  --keep-going \
  --progress-every 3 \
  >"$OUT_DIR/runner.stdout.json" 2>"$OUT_DIR/runner.stderr.log"

echo "[hiddenbench] completed ${RUN_ID}" | tee -a "$RUN_LOG"
echo "[hiddenbench] outputs=${OUT_DIR}" | tee -a "$RUN_LOG"
