#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cfg="${1:-$root/configs/UMMAFormer/lavdf_q50.yaml}"
ckpt="${2:-$root/paper_results/lavdf_q50_q50/last.pth.tar}"
tag="${3:-q50_post}"
part="${4:-all}"
sel="${5:-}"

bash "$root/tools/scan_qual.sh" "$cfg" "$ckpt" "$tag" "$part" "$sel"
