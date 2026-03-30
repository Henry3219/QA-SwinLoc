#!/usr/bin/env bash
set -euo pipefail

ROOT=${1:-data/AV-Deepfake1M/dataset}
OUT=${2:-/input0/Backup/features/AV-Deepfake1M-UMM/byola_t}
QUEUE=${3:-/input0/Backup/features/AV-Deepfake1M-UMM/queue_aud}
ENV_NAME=${4:-ummaformer-feat}
HOST_TAG=${5:-$(hostname)}

ENV_DIR="/usr/local/envs/${ENV_NAME}"
PY_BIN="${ENV_DIR}/bin/python"

CFG=${AUD_CFG:-/output/UMMAFormer/byol-a/config.yaml}
CKPT=${AUD_CKPT:-/output/UMMAFormer/byol-a/pretrained_weights/AudioNTT2020-BYOLA-64x96d2048.pth}
FF=${FF_BIN:-/usr/local/bin/ffmpeg}

CURRENT_SPLIT=""
CURRENT_RUN=""
CURRENT_BASE=""

claim_one() {
  local split root cand base run
  for split in train test; do
    root="${QUEUE}/${split}/pending"
    [[ -d "${root}" ]] || continue
    shopt -s nullglob
    for cand in "${root}"/*.txt; do
      base=$(basename "${cand}")
      run="${QUEUE}/${split}/running/${HOST_TAG}__${base}"
      if mv "${cand}" "${run}" 2>/dev/null; then
        CURRENT_SPLIT="${split}"
        CURRENT_RUN="${run}"
        CURRENT_BASE="${base}"
        printf '%s|%s|%s\n' "${split}" "${run}" "${base}"
        shopt -u nullglob
        return 0
      fi
    done
    shopt -u nullglob
  done
  return 1
}

cleanup() {
  if [[ -n "${CURRENT_RUN}" && -f "${CURRENT_RUN}" ]]; then
    mv "${CURRENT_RUN}" "${QUEUE}/${CURRENT_SPLIT}/pending/${CURRENT_BASE}" || true
  fi
}

trap cleanup INT TERM EXIT

while true; do
  if ! claim=$(claim_one); then
    echo "[aud] queue empty"
    break
  fi

  IFS='|' read -r split run base <<< "${claim}"
  log="${QUEUE}/${split}/logs/${HOST_TAG}__${base%.txt}.log"
  echo "[aud] host=${HOST_TAG} split=${split} chunk=${base}"

  set +e
  "${PY_BIN}" tools/byola_vid.py \
    --list "${run}" \
    --root "${ROOT}/${split}" \
    --out "${OUT}/${split}" \
    --cfg "${CFG}" \
    --ckpt "${CKPT}" \
    --ff "${FF}" \
    --resume 2>&1 | tee "${log}"
  rc=${PIPESTATUS[0]}
  set -e

  if [[ "${rc}" == "0" ]]; then
    mv "${run}" "${QUEUE}/${split}/done/${HOST_TAG}__${base}"
    echo "[aud] done split=${split} chunk=${base}"
  else
    mv "${run}" "${QUEUE}/${split}/failed/${HOST_TAG}__${base}"
    echo "[aud] fail split=${split} chunk=${base} rc=${rc}"
  fi

  CURRENT_SPLIT=""
  CURRENT_RUN=""
  CURRENT_BASE=""
done

trap - INT TERM EXIT
