#!/usr/bin/env bash
set -euo pipefail

WORK_DIR=${WORK_DIR:-/data/xuhaoming/yfy/research_workspace}
RUN_SCRIPT=${RUN_SCRIPT:-experiments/20260707-a8002-mca-latent-rounds-gpu1-qwen25-7b/run_remote_serial_safe_variants_50.sh}
CANDIDATE_GPUS=${CANDIDATE_GPUS:-"7 6 2 5 1 0 3 4"}
MIN_FREE_MB=${MIN_FREE_MB:-70000}
POLL_SECONDS=${POLL_SECONDS:-120}
LIMIT=${LIMIT:-50}

cd "${WORK_DIR}"

compute_count_for_gpu() {
  local gpu=$1
  local uuid
  uuid=$(nvidia-smi -i "${gpu}" --query-gpu=uuid --format=csv,noheader,nounits | tr -d '[:space:]')
  nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader,nounits 2>/dev/null \
    | awk -F, -v uuid="${uuid}" '
        {
          gsub(/[[:space:]]/, "", $1)
          if ($1 == uuid && $2 != "") {
            count += 1
          }
        }
        END { print count + 0 }
      '
}

free_mb_for_gpu() {
  local gpu=$1
  nvidia-smi -i "${gpu}" --query-gpu=memory.free --format=csv,noheader,nounits | tr -d '[:space:]'
}

while true; do
  echo "[$(date -Is)] scanning candidate GPUs: ${CANDIDATE_GPUS}"
  for gpu in ${CANDIDATE_GPUS}; do
    compute_count=$(compute_count_for_gpu "${gpu}")
    free_mb=$(free_mb_for_gpu "${gpu}")
    echo "[$(date -Is)] gpu=${gpu} compute_count=${compute_count} free_mb=${free_mb}"
    if [[ "${compute_count}" -eq 0 && "${free_mb}" -ge "${MIN_FREE_MB}" ]]; then
      echo "[$(date -Is)] selected gpu=${gpu}; launching safe variants with LIMIT=${LIMIT}"
      exec env GPU_ID="${gpu}" LIMIT="${LIMIT}" bash "${RUN_SCRIPT}"
    fi
  done
  echo "[$(date -Is)] no fully empty GPU found; sleeping ${POLL_SECONDS}s"
  sleep "${POLL_SECONDS}"
done
