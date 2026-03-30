#!/usr/bin/env bash
set -euo pipefail

OUT=${1:-/input0/Backup/features/AV-Deepfake1M-UMM/byola_t}
QUEUE=${2:-/input0/Backup/features/AV-Deepfake1M-UMM/queue_aud}
HOST_TAG=${3:-$(hostname -s)}
WAIT_SEC=${4:-60}

CTL_DIR="${QUEUE}/ctl"
PID_FILE="${CTL_DIR}/${HOST_TAG}.pid"

if [[ ! -f "${PID_FILE}" ]]; then
  echo "[aud_down] no pid file host=${HOST_TAG}"
  exit 0
fi

pid=$(cat "${PID_FILE}")
if ! kill -0 "${pid}" 2>/dev/null; then
  rm -f "${PID_FILE}"
  echo "[aud_down] stale pid file removed host=${HOST_TAG} pid=${pid}"
  exit 0
fi

kill -TERM "-${pid}" 2>/dev/null || kill -TERM "${pid}"
for _ in $(seq 1 "${WAIT_SEC}"); do
  if ! kill -0 "${pid}" 2>/dev/null; then
    rm -f "${PID_FILE}"
    echo "[aud_down] stopped host=${HOST_TAG} pid=${pid}"
    exit 0
  fi
  sleep 1
done

echo "[aud_down] pid=${pid} still alive after ${WAIT_SEC}s"
echo "[aud_down] if forced, recycle running chunks before restart"
exit 1
