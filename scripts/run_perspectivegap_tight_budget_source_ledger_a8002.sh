#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-14b-perspectivegap-tight-budget-source-ledger}"
GPU_ID="${GPU_ID:-7}"
PORT="${PORT:-8069}"
RUN_ID="${RUN_ID:-20260618-a8002-perspectivegap-tight-budget-source-ledger-rotated20-qwen25-14b}"
MAX_TOKENS="${MAX_TOKENS:-1024}"
RUN_TIMEOUT="${RUN_TIMEOUT:-3600}"
PACKET="${PACKET:-$WORKSPACE/experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl}"
OUT_DIR="${OUT_DIR:-$WORKSPACE/experiments/$RUN_ID}"

mkdir -p "$OUT_DIR"
cd "$WORKSPACE"

SERVER_LOG="$OUT_DIR/vllm.log"
RUN_LOG="$OUT_DIR/run.log"
PREDICTIONS="$OUT_DIR/predictions.jsonl"
RAW_SCORES="$OUT_DIR/scores_raw.jsonl"
RAW_SUMMARY_MD="$OUT_DIR/summary_raw.md"
RAW_SUMMARY_JSON="$OUT_DIR/summary_raw.json"
COMPILED_PREDICTIONS="$OUT_DIR/predictions_budget_compiled.jsonl"
COMPILED_SCORES="$OUT_DIR/scores_budget_compiled.jsonl"
COMPILED_SUMMARY_MD="$OUT_DIR/summary_budget_compiled.md"
COMPILED_SUMMARY_JSON="$OUT_DIR/summary_budget_compiled.json"

SERVER_PID=""
cleanup() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

{
  echo "[tight-source-ledger] run_id=${RUN_ID}"
  echo "[tight-source-ledger] workspace=${WORKSPACE}"
  echo "[tight-source-ledger] model=${MODEL_PATH} served=${SERVED_MODEL} gpu=${GPU_ID} port=${PORT}"
  echo "[tight-source-ledger] packet=${PACKET}"
  echo "[tight-source-ledger] max_tokens=${MAX_TOKENS} run_timeout=${RUN_TIMEOUT}"
  echo "[tight-source-ledger] gpu before:"
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
echo "[tight-source-ledger] server_pid=${SERVER_PID}" | tee -a "$RUN_LOG"

for attempt in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[tight-source-ledger] vLLM ready after ${attempt} checks" | tee -a "$RUN_LOG"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[tight-source-ledger] vLLM exited early; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "120" ]]; then
    echo "[tight-source-ledger] timed out waiting for vLLM; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

echo "[tight-source-ledger] running prompts -> ${PREDICTIONS}" | tee -a "$RUN_LOG"
OPENAI_API_KEY=EMPTY timeout "$RUN_TIMEOUT" "$PY" scripts/run_perspectivegap_source_ledger_router_openai_compatible.py \
  --packet "$PACKET" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --model "$SERVED_MODEL" \
  --out "$PREDICTIONS" \
  --variant rotated_scope \
  --temperature 0 \
  --max-tokens "$MAX_TOKENS" \
  2>&1 | tee "$OUT_DIR/runner.stdout.log"
echo "[tight-source-ledger] runner_status=${PIPESTATUS[0]}" | tee -a "$RUN_LOG"

"$PY" scripts/score_perspectivegap_tight_budget.py \
  --packet "$PACKET" \
  --predictions "$PREDICTIONS" \
  --out "$RAW_SCORES" \
  --summary-out "$RAW_SUMMARY_MD" \
  > "$RAW_SUMMARY_JSON"

"$PY" scripts/compile_perspectivegap_source_ledger_budget.py \
  --packet "$PACKET" \
  --predictions "$PREDICTIONS" \
  --out "$COMPILED_PREDICTIONS"

"$PY" scripts/score_perspectivegap_tight_budget.py \
  --packet "$PACKET" \
  --predictions "$COMPILED_PREDICTIONS" \
  --out "$COMPILED_SCORES" \
  --summary-out "$COMPILED_SUMMARY_MD" \
  > "$COMPILED_SUMMARY_JSON"

{
  echo "[tight-source-ledger] predictions=$(wc -l < "$PREDICTIONS")"
  echo "[tight-source-ledger] raw summary:"
  cat "$RAW_SUMMARY_MD"
  echo "[tight-source-ledger] compiled summary:"
  cat "$COMPILED_SUMMARY_MD"
  echo "[tight-source-ledger] gpu after runner before cleanup:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
} | tee -a "$RUN_LOG"
