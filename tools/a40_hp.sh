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
cpu="${CPU:-6}"
log="output/UMMAFormer_exp07/tool/log"
mkdir -p "$log"

eval_one() {
  local cfg="$1"
  local out="${2:-hp}"
  local tag="$3"
  local id
  id="$(basename "$cfg" .yaml)"
  local ckpt="paper_results/${id}_${out}/last.pth.tar"

  if [[ ! -f "$ckpt" ]]; then
    echo "[SKIP] missing ckpt: $ckpt"
    return 0
  fi

  CUDA_VISIBLE_DEVICES="$gpu" OMP_NUM_THREADS="$cpu" MKL_NUM_THREADS="$cpu" PYTHONUNBUFFERED=1 \
    bash tools/scan_qual.sh "$cfg" "$ckpt" "$tag" all a \
    2>&1 | tee "$log/${id}_eval.log"
}

train_one() {
  local cfg="$1"
  local out="${2:-hp}"
  local id
  id="$(basename "$cfg" .yaml)"
  local ckpt="paper_results/${id}_${out}/last.pth.tar"

  if [[ -f "$ckpt" ]]; then
    echo "[SKIP] ckpt exists: $ckpt"
    return 0
  fi

  CUDA_VISIBLE_DEVICES="$gpu" OMP_NUM_THREADS="$cpu" MKL_NUM_THREADS="$cpu" PYTHONUNBUFFERED=1 \
    python train.py "$cfg" --output "$out" \
    2>&1 | tee "$log/${id}_train.log"
}

# A40 order:
# 1. test-set eval for the completed A40 first group
# 2. train the second A40 group
# 3. test-set eval for the second A40 group
eval_one "configs/UMMAFormer/lavdf_q50d50_w3x6.yaml" "hp" "lavdf_w3x6_post"
train_one "configs/UMMAFormer/lavdf_q50d50_w7x5_19.yaml" "hp"
eval_one "configs/UMMAFormer/lavdf_q50d50_w7x5_19.yaml" "hp" "lavdf_w7x5_19_post"
