#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
root="$(pwd)"
if [[ ! -f "$root/train.py" ]]; then
  root="$(cd "$here/.." && pwd)"
fi
if [[ ! -f "$root/train.py" ]]; then
  root="/input0/Backup/model/UMMAFormer_exp07"
fi
if [[ ! -f "$root/train.py" ]]; then
  echo "[ERR] train.py not found; run from repo root or fix root in $(basename "$0")" >&2
  exit 1
fi
cd "$root"

gpu="${GPU:-0}"
cpu=6
log="output/UMMAFormer_exp07/tool/log"
mkdir -p "$log"

# convHRLRSwin remaps any <=1 window to 7, so the current effective baseline is 7-7-7-7-7-7.
# All window settings below are directly runnable under max_seq_len=576; no replacement is needed.
run() {
  local cfg="$1"
  local out="$2"
  local tag="$3"
  local id
  id="$(basename "$cfg" .yaml)"
  local ckpt="paper_results/${id}_${out}/last.pth.tar"

  CUDA_VISIBLE_DEVICES="$gpu" OMP_NUM_THREADS="$cpu" MKL_NUM_THREADS="$cpu" PYTHONUNBUFFERED=1 \
    python train.py "$cfg" --output "$out" --eval \
    2>&1 | tee "$log/${id}_train.log"

  CUDA_VISIBLE_DEVICES="$gpu" OMP_NUM_THREADS="$cpu" MKL_NUM_THREADS="$cpu" PYTHONUNBUFFERED=1 \
    bash tools/scan_qual.sh "$cfg" "$ckpt" "$tag" all a \
    2>&1 | tee "$log/${id}_eval.log"
}

# Reviewer control 1: all small windows.
run "configs/UMMAFormer/lavdf_q50d50_w3x6.yaml" "hp" "lavdf_w3x6_post"

# Reviewer control 2: enlarge only the lowest-resolution level.
run "configs/UMMAFormer/lavdf_q50d50_w7x5_19.yaml" "hp" "lavdf_w7x5_19_post"
