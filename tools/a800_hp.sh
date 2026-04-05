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
cpu=20
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

# Reviewer control 3: smaller early windows, larger late windows.
run "configs/UMMAFormer/lavdf_q50d50_w33_777_19.yaml" "hp" "lavdf_w33_777_19_post"

# Reviewer control 4: all large windows.
run "configs/UMMAFormer/lavdf_q50d50_w19x6.yaml" "hp" "lavdf_w19x6_post"
