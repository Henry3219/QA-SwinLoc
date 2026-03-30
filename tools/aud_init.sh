#!/usr/bin/env bash
set -euo pipefail

ROOT=${1:-data/AV-Deepfake1M/dataset}
OUT=${2:-/input0/Backup/features/AV-Deepfake1M-UMM/byola_t}
QUEUE=${3:-/input0/Backup/features/AV-Deepfake1M-UMM/queue_aud}
JOBS=${4:-24}
CHUNK=${5:-2000}
MODE=${6:-full}

python3 tools/aud_sched.py build \
  --split test \
  --split train \
  --source-tpl "${ROOT}/{split}_files.txt" \
  --seed-tpl "data/todo/{split}.txt" \
  --todo-tpl "data/todo/{split}.aud.txt" \
  --queue-root "${QUEUE}" \
  --out-root "${OUT}" \
  --jobs "${JOBS}" \
  --chunk "${CHUNK}" \
  --mode "${MODE}"
