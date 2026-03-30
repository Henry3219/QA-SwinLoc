#!/usr/bin/env bash
set -euo pipefail

OUT=${1:-/input0/Backup/features/AV-Deepfake1M-UMM/byola_t}
QUEUE=${2:-/input0/Backup/features/AV-Deepfake1M-UMM/queue_aud}
TAG=${HOST_TAG:-v100}

HOST_TAG="${TAG}" bash tools/aud_down.sh "${OUT}" "${QUEUE}" "${TAG}"
