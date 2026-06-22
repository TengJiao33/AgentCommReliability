#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-14b-sseac-v0-pg40}"
GPU_ID="${GPU_ID:-7}"
PORT="${PORT:-8073}"
RUN_ID="${RUN_ID:-20260619-a8002-sseac-v0-pg40-limit5-qwen25-14b}"
LIMIT="${LIMIT:-5}"
MAX_TOKENS="${MAX_TOKENS:-2048}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.80}"
RUN_TIMEOUT="${RUN_TIMEOUT:-1800}"
PROMPT_CONTRACT="${PROMPT_CONTRACT:-cardunit}"
PACKET="${PACKET:-$WORKSPACE/experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl}"
PG_PACKET="${PG_PACKET:-$WORKSPACE/experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl}"
OUT_DIR="${OUT_DIR:-$WORKSPACE/experiments/$RUN_ID}"

mkdir -p "$OUT_DIR"
cd "$WORKSPACE"

SERVER_LOG="$OUT_DIR/vllm.log"
RUN_LOG="$OUT_DIR/run.log"
PACKET_RUN="$OUT_DIR/packet_limit${LIMIT}.jsonl"
PREDICTIONS="$OUT_DIR/predictions.jsonl"
COMPILED_MODEL_ONLY="$OUT_DIR/compiled_model_only.jsonl"
COMPILED_COMPILER="$OUT_DIR/compiled_compiler.jsonl"
COMPILE_MODEL_ONLY_SUMMARY="$OUT_DIR/compile_summary_model_only.json"
COMPILE_COMPILER_SUMMARY="$OUT_DIR/compile_summary_compiler.json"
SCORES_MODEL_ONLY="$OUT_DIR/scores_model_only.jsonl"
SCORES_COMPILER="$OUT_DIR/scores_compiler.jsonl"
SUMMARY_MODEL_ONLY_MD="$OUT_DIR/summary_model_only.md"
SUMMARY_COMPILER_MD="$OUT_DIR/summary_compiler.md"
SUMMARY_MODEL_ONLY_JSON="$OUT_DIR/summary_model_only.json"
SUMMARY_COMPILER_JSON="$OUT_DIR/summary_compiler.json"

for required in "$PACKET" "$PG_PACKET"; do
  if [[ ! -s "$required" ]]; then
    echo "[sseac-pg40] missing required file: $required" >&2
    exit 2
  fi
done

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
  echo "[sseac-pg40] run_id=${RUN_ID}"
  echo "[sseac-pg40] workspace=${WORKSPACE}"
  echo "[sseac-pg40] model=${MODEL_PATH} served=${SERVED_MODEL} gpu=${GPU_ID} port=${PORT}"
  echo "[sseac-pg40] packet=${PACKET}"
  echo "[sseac-pg40] packet_run=${PACKET_RUN}"
  echo "[sseac-pg40] pg_packet=${PG_PACKET}"
  echo "[sseac-pg40] limit=${LIMIT} max_model_len=${MAX_MODEL_LEN} max_tokens=${MAX_TOKENS} gpu_memory_utilization=${GPU_MEMORY_UTILIZATION} run_timeout=${RUN_TIMEOUT} prompt_contract=${PROMPT_CONTRACT}"
  echo "[sseac-pg40] gpu before:"
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
echo "[sseac-pg40] server_pid=${SERVER_PID}" | tee -a "$RUN_LOG"

for attempt in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[sseac-pg40] vLLM ready after ${attempt} checks" | tee -a "$RUN_LOG"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[sseac-pg40] vLLM exited early; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "120" ]]; then
    echo "[sseac-pg40] timed out waiting for vLLM; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

echo "[sseac-pg40] running prompts -> ${PREDICTIONS}" | tee -a "$RUN_LOG"
OPENAI_API_KEY=EMPTY timeout "$RUN_TIMEOUT" "$PY" scripts/run_sseac_v0_pg40_openai_compatible.py \
  --packet "$PACKET_RUN" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --model "$SERVED_MODEL" \
  --out "$PREDICTIONS" \
  --temperature 0 \
  --max-tokens "$MAX_TOKENS" \
  --prompt-contract "$PROMPT_CONTRACT" \
  2>&1 | tee "$OUT_DIR/runner.stdout.log"
echo "[sseac-pg40] runner_status=${PIPESTATUS[0]}" | tee -a "$RUN_LOG"

"$PY" scripts/compile_sseac_v0.py \
  --packet "$PACKET_RUN" \
  --predictions "$PREDICTIONS" \
  --out "$COMPILED_MODEL_ONLY" \
  --summary-out "$COMPILE_MODEL_ONLY_SUMMARY" \
  --mode model_only \
  > "$OUT_DIR/compile_model_only.stdout.json"

"$PY" scripts/compile_sseac_v0.py \
  --packet "$PACKET_RUN" \
  --predictions "$PREDICTIONS" \
  --out "$COMPILED_COMPILER" \
  --summary-out "$COMPILE_COMPILER_SUMMARY" \
  --mode compiler \
  > "$OUT_DIR/compile_compiler.stdout.json"

"$PY" scripts/score_sseac_pg40_compiled.py \
  --pg-packet "$PG_PACKET" \
  --compiled "$COMPILED_MODEL_ONLY" \
  --out "$SCORES_MODEL_ONLY" \
  --summary-out "$SUMMARY_MODEL_ONLY_MD" \
  > "$SUMMARY_MODEL_ONLY_JSON"

"$PY" scripts/score_sseac_pg40_compiled.py \
  --pg-packet "$PG_PACKET" \
  --compiled "$COMPILED_COMPILER" \
  --out "$SCORES_COMPILER" \
  --summary-out "$SUMMARY_COMPILER_MD" \
  > "$SUMMARY_COMPILER_JSON"

{
  echo "[sseac-pg40] predictions=$(wc -l < "$PREDICTIONS")"
  echo "[sseac-pg40] model_only summary:"
  cat "$SUMMARY_MODEL_ONLY_MD"
  echo "[sseac-pg40] compiler summary:"
  cat "$SUMMARY_COMPILER_MD"
  echo "[sseac-pg40] gpu after runner before cleanup:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
} | tee -a "$RUN_LOG"
