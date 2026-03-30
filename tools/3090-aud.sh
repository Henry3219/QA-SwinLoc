#!/usr/bin/env bash
set -euo pipefail

ROOT=${1:-data/AV-Deepfake1M/dataset}
OUT=${2:-/input0/Backup/features/AV-Deepfake1M-UMM/byola_t}
QUEUE=${3:-/input0/Backup/features/AV-Deepfake1M-UMM/queue_aud}
TAG=${HOST_TAG:-3090}

HOST_TAG="${TAG}" bash tools/aud_up.sh "${ROOT}" "${OUT}" "${QUEUE}" ummaformer-feat "${TAG}"
