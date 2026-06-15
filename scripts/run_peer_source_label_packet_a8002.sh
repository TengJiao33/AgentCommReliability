#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-7b-source-label}"
GPU_ID="${GPU_ID:-5}"
PORT="${PORT:-8031}"
RUN_STAMP="${RUN_STAMP:-$(date +%Y%m%d-%H%M)}"
MODES="${MODES:-named randomized}"

SOURCE_CASES="${SOURCE_CASES:-$WORKSPACE/experiments/20260615-1151-a8002-typed-public-state-math200-anon/source_cases.jsonl}"
LOG_DIR="${LOG_DIR:-$WORKSPACE/logs}"
OUT_ROOT="${OUT_ROOT:-$WORKSPACE/experiments}"
SERVER_LOG="$LOG_DIR/source-label-vllm-${RUN_STAMP}.log"

CONDITIONS=(
  correct_answer_only
  wrong_answer_only
  correct_rationale
  wrong_rationale
  correct_redacted_rationale
  wrong_redacted_rationale
  correct_equation_surface
  wrong_equation_surface
  correct_typed_public_state
  wrong_typed_public_state
)

mkdir -p "$LOG_DIR" "$OUT_ROOT"
cd "$WORKSPACE"

SERVER_PID=""
cleanup() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "[source-label] starting vLLM on GPU ${GPU_ID}, port ${PORT}" | tee "$LOG_DIR/source-label-packet-${RUN_STAMP}.log"
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

for attempt in $(seq 1 90); do
  if curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[source-label] vLLM ready after ${attempt} checks" | tee -a "$LOG_DIR/source-label-packet-${RUN_STAMP}.log"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[source-label] vLLM exited early; tail follows" >&2
    tail -80 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "90" ]]; then
    echo "[source-label] timed out waiting for vLLM; tail follows" >&2
    tail -80 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

for mode in $MODES; do
  RUN_ID="${RUN_STAMP}-a8002-source-label-math200-${mode}"
  OUT_DIR="$OUT_ROOT/$RUN_ID"
  PROBE_LOG="$LOG_DIR/source-label-probe-${RUN_STAMP}-${mode}.log"
  echo "[source-label] running ${mode} -> ${OUT_DIR}" | tee -a "$LOG_DIR/source-label-packet-${RUN_STAMP}.log"
  timeout 5400 "$PY" scripts/run_peer_exposure_probe.py \
    --run-id "$RUN_ID" \
    --out-dir "$OUT_DIR" \
    --source-format source_cases \
    --source-cases-jsonl "$SOURCE_CASES" \
    --selection-mode first \
    --max-cases 0 \
    --base-url "http://127.0.0.1:${PORT}/v1" \
    --model "$SERVED_MODEL" \
    --conditions "${CONDITIONS[@]}" \
    --peer-warning natural \
    --peer-source-mode "$mode" \
    --machine A800_2 \
    --gpu-ids "$GPU_ID" \
    --server-log "$SERVER_LOG" \
    --include-prompts \
    >"$PROBE_LOG" 2>&1
  echo "[source-label] completed ${mode}" | tee -a "$LOG_DIR/source-label-packet-${RUN_STAMP}.log"
done

echo "[source-label] packet completed: ${MODES}" | tee -a "$LOG_DIR/source-label-packet-${RUN_STAMP}.log"
