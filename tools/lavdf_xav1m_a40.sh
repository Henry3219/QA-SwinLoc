#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

OUT_DIR="paper_results/lavdf_xav1m"
CFG="configs/UMMAFormer/lavdf_q50d50.yaml"
CKPT="paper_results/av1m_q50d50_av1m_q50d50/last.pth.tar"
CKPT_DIR="$(dirname "$CKPT")"
TMP_JSON="${CKPT_DIR}/test_results.json"

mkdir -p "${OUT_DIR}"

CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=24 MKL_NUM_THREADS=24 \
python eval.py \
  "${CFG}" \
  "${CKPT}" \
  -p 20 \
  2>&1 | tee "${OUT_DIR}/eval.log"

cp "${TMP_JSON}" "${OUT_DIR}/test_results.json"
cp "${CFG}" "${OUT_DIR}/config.yaml"

cat > "${OUT_DIR}/README.txt" <<EOF
LavDF test using AV1M-trained final checkpoint.

config: ${CFG}
ckpt: ${CKPT}
log: ${OUT_DIR}/eval.log
result: ${OUT_DIR}/test_results.json
EOF
