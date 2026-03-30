#!/usr/bin/env bash
set -euo pipefail

ROOT=${1:-data/AV-Deepfake1M/dataset}
OUT=${2:-/input0/Backup/features/AV-Deepfake1M-UMM/byola_t}
QUEUE=${3:-/input0/Backup/features/AV-Deepfake1M-UMM/queue_aud}
ENV_NAME=${4:-ummaformer-feat}
HOST_TAG=${5:-$(hostname -s)}

CTL_DIR="${QUEUE}/ctl"
PID_FILE="${CTL_DIR}/${HOST_TAG}.pid"
LOG_FILE="${CTL_DIR}/${HOST_TAG}.log"

mkdir -p "${CTL_DIR}"

if [[ -f "${PID_FILE}" ]]; then
  old_pid=$(cat "${PID_FILE}")
  if kill -0 "${old_pid}" 2>/dev/null; then
    echo "[aud_up] already running host=${HOST_TAG} pid=${old_pid} log=${LOG_FILE}"
    exit 0
  fi
  rm -f "${PID_FILE}"
fi

setsid env HOST_TAG="${HOST_TAG}" bash tools/aud_work.sh \
  "${ROOT}" "${OUT}" "${QUEUE}" "${ENV_NAME}" "${HOST_TAG}" \
  > "${LOG_FILE}" 2>&1 &

pid=$!
echo "${pid}" > "${PID_FILE}"
echo "[aud_up] host=${HOST_TAG} pid=${pid} log=${LOG_FILE}"
