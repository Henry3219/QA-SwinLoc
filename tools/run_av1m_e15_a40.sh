#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p paper_results/av1m_e15

CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=24 MKL_NUM_THREADS=24 \
python infer_av1m.py \
  configs/UMMAFormer/av1m_q50d50.yaml \
  paper_results/av1m_q50d50_av1m_q50d50/last.pth.tar \
  --batch 48 \
  --workers 12 \
  --out paper_results/av1m_e15/prediction.json \
  2>&1 | tee paper_results/av1m_e15/infer.log
