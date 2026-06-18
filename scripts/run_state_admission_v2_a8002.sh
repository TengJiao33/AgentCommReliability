#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-7b-state-admission-v2}"
GPU_ID="${GPU_ID:-7}"
PORT="${PORT:-8072}"
RUN_ID="${RUN_ID:-20260618-a8002-state-admission-v2-smoke9-qwen25-7b}"
MAX_TOKENS="${MAX_TOKENS:-900}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"
RUN_TIMEOUT="${RUN_TIMEOUT:-1800}"
PROMPT_STYLE="${PROMPT_STYLE:-unit_first}"
PACKET="${PACKET:-$WORKSPACE/experiments/20260618-local-state-admission-v2-smoke/packet.jsonl}"
OUT_DIR="${OUT_DIR:-$WORKSPACE/experiments/$RUN_ID}"

mkdir -p "$OUT_DIR"
cd "$WORKSPACE"

SERVER_LOG="$OUT_DIR/vllm.log"
RUN_LOG="$OUT_DIR/run.log"
PREDICTIONS="$OUT_DIR/predictions.jsonl"
SCORES="$OUT_DIR/scores.jsonl"
SUMMARY_MD="$OUT_DIR/summary.md"
SUMMARY_JSON="$OUT_DIR/summary.json"
if [[ "$PROMPT_STYLE" == direct_answer_* ]]; then
  SCORE_SCRIPT="scripts/score_state_admission_v2_direct_answer.py"
else
  SCORE_SCRIPT="scripts/score_state_admission_v2.py"
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
  echo "[state-admission-v2] run_id=${RUN_ID}"
  echo "[state-admission-v2] workspace=${WORKSPACE}"
  echo "[state-admission-v2] model=${MODEL_PATH} served=${SERVED_MODEL} gpu=${GPU_ID} port=${PORT}"
  echo "[state-admission-v2] packet=${PACKET}"
  echo "[state-admission-v2] max_model_len=${MAX_MODEL_LEN} max_tokens=${MAX_TOKENS} run_timeout=${RUN_TIMEOUT}"
  echo "[state-admission-v2] prompt_style=${PROMPT_STYLE}"
  echo "[state-admission-v2] gpu before:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
} | tee "$RUN_LOG"

CUDA_VISIBLE_DEVICES="$GPU_ID" nohup "$PY" -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_PATH" \
  --served-model-name "$SERVED_MODEL" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --dtype bfloat16 \
  --max-model-len "$MAX_MODEL_LEN" \
  --gpu-memory-utilization 0.90 \
  --disable-log-requests \
  >"$SERVER_LOG" 2>&1 &
SERVER_PID="$!"
echo "[state-admission-v2] server_pid=${SERVER_PID}" | tee -a "$RUN_LOG"

for attempt in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[state-admission-v2] vLLM ready after ${attempt} checks" | tee -a "$RUN_LOG"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[state-admission-v2] vLLM exited early; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "120" ]]; then
    echo "[state-admission-v2] timed out waiting for vLLM; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

echo "[state-admission-v2] running prompts -> ${PREDICTIONS}" | tee -a "$RUN_LOG"
OPENAI_API_KEY=EMPTY timeout "$RUN_TIMEOUT" "$PY" scripts/run_state_admission_v2_openai_compatible.py \
  --packet "$PACKET" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --model "$SERVED_MODEL" \
  --out "$PREDICTIONS" \
  --prompt-style "$PROMPT_STYLE" \
  --temperature 0 \
  --max-tokens "$MAX_TOKENS" \
  2>&1 | tee "$OUT_DIR/runner.stdout.log"
echo "[state-admission-v2] runner_status=${PIPESTATUS[0]}" | tee -a "$RUN_LOG"

"$PY" "$SCORE_SCRIPT" \
  --packet "$PACKET" \
  --predictions "$PREDICTIONS" \
  --out "$SCORES" \
  --summary-out "$SUMMARY_MD" \
  > "$SUMMARY_JSON"

{
  echo "[state-admission-v2] predictions=$(wc -l < "$PREDICTIONS")"
  echo "[state-admission-v2] summary:"
  cat "$SUMMARY_MD"
  echo "[state-admission-v2] gpu after runner before cleanup:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
} | tee -a "$RUN_LOG"
