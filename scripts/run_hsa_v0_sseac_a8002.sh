#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-14b-hsa-v0-sseac}"
GPU_ID="${GPU_ID:-7}"
PORT="${PORT:-8074}"
RUN_ID="${RUN_ID:-20260619-a8002-hsa-v0-sseac-limit3-qwen25-14b}"
LIMIT="${LIMIT:-3}"
MAX_TOKENS="${MAX_TOKENS:-2048}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.80}"
RUN_TIMEOUT="${RUN_TIMEOUT:-1200}"
PROMPT_CONTRACT="${PROMPT_CONTRACT:-baseline}"
PACKET="${PACKET:-$WORKSPACE/experiments/20260619-local-hsa-v0-extended15-packet/hsa_v0_packet.jsonl}"
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

if [[ ! -s "$PACKET" ]]; then
  echo "[hsa-sseac] missing required file: $PACKET" >&2
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
  echo "[hsa-sseac] run_id=${RUN_ID}"
  echo "[hsa-sseac] workspace=${WORKSPACE}"
  echo "[hsa-sseac] model=${MODEL_PATH} served=${SERVED_MODEL} gpu=${GPU_ID} port=${PORT}"
  echo "[hsa-sseac] packet=${PACKET}"
  echo "[hsa-sseac] packet_run=${PACKET_RUN}"
  echo "[hsa-sseac] limit=${LIMIT} max_model_len=${MAX_MODEL_LEN} max_tokens=${MAX_TOKENS} gpu_memory_utilization=${GPU_MEMORY_UTILIZATION} run_timeout=${RUN_TIMEOUT} prompt_contract=${PROMPT_CONTRACT}"
  echo "[hsa-sseac] gpu before:"
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
echo "[hsa-sseac] server_pid=${SERVER_PID}" | tee -a "$RUN_LOG"

for attempt in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[hsa-sseac] vLLM ready after ${attempt} checks" | tee -a "$RUN_LOG"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[hsa-sseac] vLLM exited early; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "120" ]]; then
    echo "[hsa-sseac] timed out waiting for vLLM; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

echo "[hsa-sseac] running prompts -> ${PREDICTIONS}" | tee -a "$RUN_LOG"
OPENAI_API_KEY=EMPTY timeout "$RUN_TIMEOUT" "$PY" scripts/run_hsa_v0_sseac_openai_compatible.py \
  --packet "$PACKET_RUN" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --model "$SERVED_MODEL" \
  --out "$PREDICTIONS" \
  --temperature 0 \
  --max-tokens "$MAX_TOKENS" \
  --prompt-contract "$PROMPT_CONTRACT" \
  2>&1 | tee "$OUT_DIR/runner.stdout.log"
echo "[hsa-sseac] runner_status=${PIPESTATUS[0]}" | tee -a "$RUN_LOG"

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

"$PY" scripts/score_hsa_v0_compiled.py \
  --packet "$PACKET_RUN" \
  --compiled "$COMPILED_MODEL_ONLY" \
  --out "$SCORES_MODEL_ONLY" \
  --summary-out "$SUMMARY_MODEL_ONLY_MD" \
  > "$SUMMARY_MODEL_ONLY_JSON"

"$PY" scripts/score_hsa_v0_compiled.py \
  --packet "$PACKET_RUN" \
  --compiled "$COMPILED_COMPILER" \
  --out "$SCORES_COMPILER" \
  --summary-out "$SUMMARY_COMPILER_MD" \
  > "$SUMMARY_COMPILER_JSON"

{
  echo "[hsa-sseac] predictions=$(wc -l < "$PREDICTIONS")"
  echo "[hsa-sseac] model_only summary:"
  cat "$SUMMARY_MODEL_ONLY_MD"
  echo "[hsa-sseac] compiler summary:"
  cat "$SUMMARY_COMPILER_MD"
  echo "[hsa-sseac] gpu after runner before cleanup:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
} | tee -a "$RUN_LOG"
