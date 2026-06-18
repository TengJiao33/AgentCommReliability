#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/data/xuhaoming/yfy/research_workspace}"
PY="${PY:-$WORKSPACE/envs/mad-mm-vllm063/bin/python}"
MODEL_PATH="${MODEL_PATH:-/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct}"
SERVED_MODEL="${SERVED_MODEL:-qwen2.5-14b-state-admission-v1}"
GPU_ID="${GPU_ID:-7}"
PORT="${PORT:-8071}"
RUN_ID="${RUN_ID:-20260618-a8002-state-admission-v1-stratified5-qwen25-14b}"
MAX_TOKENS="${MAX_TOKENS:-1536}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-16384}"
RUN_TIMEOUT="${RUN_TIMEOUT:-2400}"
HARD_IDS_MODE="${HARD_IDS_MODE:-stratified5}"
HARD_IDS="${HARD_IDS:-}"
ROUTER_MODE="${ROUTER_MODE:-direct}"
PROMPT_STYLE="${PROMPT_STYLE:-default}"
EXECUTOR_POLICY="${EXECUTOR_POLICY:-greedy}"
PACKET="${PACKET:-$WORKSPACE/experiments/20260618-local-state-admission-v1/state_admission_v1_rotated20.jsonl}"
OUT_DIR="${OUT_DIR:-$WORKSPACE/experiments/$RUN_ID}"

DEFAULT_HARD_IDS=(
  "pg_000__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0__state_admission_v1"
  "pg_002__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0__state_admission_v1"
  "pg_006__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0__state_admission_v1"
  "pg_004__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0__state_admission_v1"
  "pg_005__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0__state_admission_v1"
)

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
  echo "[state-admission-v1] run_id=${RUN_ID}"
  echo "[state-admission-v1] workspace=${WORKSPACE}"
  echo "[state-admission-v1] model=${MODEL_PATH} served=${SERVED_MODEL} gpu=${GPU_ID} port=${PORT}"
  echo "[state-admission-v1] packet=${PACKET}"
  echo "[state-admission-v1] max_model_len=${MAX_MODEL_LEN} max_tokens=${MAX_TOKENS} run_timeout=${RUN_TIMEOUT}"
  echo "[state-admission-v1] router_mode=${ROUTER_MODE}"
  echo "[state-admission-v1] prompt_style=${PROMPT_STYLE}"
  echo "[state-admission-v1] executor_policy=${EXECUTOR_POLICY}"
  echo "[state-admission-v1] hard_ids_mode=${HARD_IDS_MODE}"
  echo "[state-admission-v1] hard_ids=${HARD_IDS:-${DEFAULT_HARD_IDS[*]}}"
  echo "[state-admission-v1] gpu before:"
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
echo "[state-admission-v1] server_pid=${SERVER_PID}" | tee -a "$RUN_LOG"

for attempt in $(seq 1 120); do
  if curl -fsS "http://127.0.0.1:${PORT}/v1/models" >/dev/null 2>&1; then
    echo "[state-admission-v1] vLLM ready after ${attempt} checks" | tee -a "$RUN_LOG"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[state-admission-v1] vLLM exited early; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
  sleep 5
  if [[ "$attempt" == "120" ]]; then
    echo "[state-admission-v1] timed out waiting for vLLM; tail follows" >&2
    tail -120 "$SERVER_LOG" >&2 || true
    exit 1
  fi
done

RUNNER_ARGS=()
if [[ "$HARD_IDS_MODE" == "all" ]]; then
  echo "[state-admission-v1] running all packet rows" | tee -a "$RUN_LOG"
elif [[ -n "$HARD_IDS" ]]; then
  read -r -a SELECTED_HARD_IDS <<< "$HARD_IDS"
  for hard_id in "${SELECTED_HARD_IDS[@]}"; do
    RUNNER_ARGS+=(--hard-evaluation-id "$hard_id")
  done
else
  for hard_id in "${DEFAULT_HARD_IDS[@]}"; do
    RUNNER_ARGS+=(--hard-evaluation-id "$hard_id")
  done
fi

RUNNER_SCRIPT="scripts/run_state_admission_v1_openai_compatible.py"
RUNNER_MODE_ARGS=(--prompt-style "$PROMPT_STYLE")
if [[ "$ROUTER_MODE" == "priority" ]]; then
  RUNNER_SCRIPT="scripts/run_state_admission_v1_priority_openai_compatible.py"
  RUNNER_MODE_ARGS+=(--executor-policy "$EXECUTOR_POLICY")
elif [[ "$ROUTER_MODE" == "ledger" ]]; then
  RUNNER_SCRIPT="scripts/run_state_admission_v1_ledger_openai_compatible.py"
elif [[ "$ROUTER_MODE" != "direct" ]]; then
  echo "[state-admission-v1] unknown ROUTER_MODE=${ROUTER_MODE}" >&2
  exit 2
fi

echo "[state-admission-v1] running prompts -> ${PREDICTIONS}" | tee -a "$RUN_LOG"
OPENAI_API_KEY=EMPTY timeout "$RUN_TIMEOUT" "$PY" "$RUNNER_SCRIPT" \
  --packet "$PACKET" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --model "$SERVED_MODEL" \
  --out "$PREDICTIONS" \
  "${RUNNER_ARGS[@]}" \
  "${RUNNER_MODE_ARGS[@]}" \
  --temperature 0 \
  --max-tokens "$MAX_TOKENS" \
  2>&1 | tee "$OUT_DIR/runner.stdout.log"
echo "[state-admission-v1] runner_status=${PIPESTATUS[0]}" | tee -a "$RUN_LOG"

"$PY" scripts/score_state_admission_v1.py \
  --packet "$PACKET" \
  --predictions "$PREDICTIONS" \
  --out "$SCORES" \
  --summary-out "$SUMMARY_MD" \
  > "$SUMMARY_JSON"

{
  echo "[state-admission-v1] predictions=$(wc -l < "$PREDICTIONS")"
  echo "[state-admission-v1] summary:"
  cat "$SUMMARY_MD"
  echo "[state-admission-v1] gpu after runner before cleanup:"
  nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits
} | tee -a "$RUN_LOG"
