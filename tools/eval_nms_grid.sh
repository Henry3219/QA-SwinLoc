#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BASE_CFG="${1:-$ROOT_DIR/configs/UMMAFormer/lavdf_tsn_audio.yaml}"
CKPT="${2:-/input0/Backup/model/UMMAFormer_exp08/paper_results/lavdf_tsn_audio_2026_03_05_06_32_07/last.pth.tar}"
TAG="${3:-$(date +%Y%m%d_%H%M%S)}"

if [[ ! -f "$BASE_CFG" ]]; then
  echo "[ERR] base config not found: $BASE_CFG" >&2
  exit 1
fi
if [[ ! -f "$CKPT" ]]; then
  echo "[ERR] ckpt not found: $CKPT" >&2
  exit 1
fi

TMP_DIR="/tmp/umma_eval_cfg_${TAG}"
mkdir -p "$TMP_DIR"

# case_id adapt_nms export_topk len_thr sigma_s sigma_l
CASES=(
  "c1 0 100 0.7 0.75 0.75"
  "c2 0 200 0.7 0.75 0.75"
  "c3 0 -1 0.7 0.75 0.75"
  "c4 1 100 0.7 0.65 0.85"
  "c5 1 200 0.7 0.65 0.85"
  "c6 1 200 0.7 0.50 0.85"
  "c7 1 200 0.5 0.50 0.80"
  "c8 1 200 0.9 0.65 0.90"
)

run_case() {
  local case_id="$1"
  local adapt_nms="$2"
  local export_topk="$3"
  local len_thr="$4"
  local sigma_s="$5"
  local sigma_l="$6"

  local cfg_out="$TMP_DIR/lavdf_${case_id}.yaml"
  local out_name="eval_${TAG}_${case_id}"

  python - <<'PY' "$BASE_CFG" "$cfg_out" "$adapt_nms" "$export_topk" "$len_thr" "$sigma_s" "$sigma_l"
import sys, yaml
in_cfg, out_cfg, adapt_nms, export_topk, len_thr, sigma_s, sigma_l = sys.argv[1:]
with open(in_cfg, 'r', encoding='utf-8') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

cfg.setdefault('model', {})
cfg.setdefault('train_cfg', {})
cfg.setdefault('test_cfg', {})

# force close con/refine
cfg['model']['refine_on'] = False
cfg['train_cfg']['con_on'] = False

# nms/export params
cfg['test_cfg']['adapt_nms'] = bool(int(adapt_nms))
cfg['test_cfg']['export_topk'] = int(export_topk)
cfg['test_cfg']['len_thr'] = float(len_thr)
cfg['test_cfg']['sigma_s'] = float(sigma_s)
cfg['test_cfg']['sigma_l'] = float(sigma_l)

with open(out_cfg, 'w', encoding='utf-8') as f:
    yaml.safe_dump(cfg, f, sort_keys=False)
PY

  echo "[RUN] $case_id -> output=$out_name"
  (
    cd "$ROOT_DIR"
    python train.py "$cfg_out" \
      --resume "$CKPT" \
      --eval \
      --output "$out_name"
  )

  local res_dir="$ROOT_DIR/paper_results/lavdf_${case_id}_${out_name#eval_${TAG}_}"
  # actual folder is based on cfg filename + output, so compute robustly:
  local found_dir
  found_dir=$(ls -dt "$ROOT_DIR"/paper_results/lavdf_${case_id}_"$out_name" 2>/dev/null || true)
  if [[ -z "$found_dir" ]]; then
    found_dir=$(ls -dt "$ROOT_DIR"/paper_results/*_"$out_name" | head -n 1)
  fi
  echo "[DONE] $case_id results: $found_dir/test_results.txt"
  sed -n '1,2p' "$found_dir/test_results.txt"
}

echo "[INFO] root=$ROOT_DIR"
echo "[INFO] base_cfg=$BASE_CFG"
echo "[INFO] ckpt=$CKPT"
echo "[INFO] tag=$TAG"
echo "[INFO] temp_cfg_dir=$TMP_DIR"

for c in "${CASES[@]}"; do
  # shellcheck disable=SC2086
  run_case $c
done

echo "[OK] all 8 eval runs finished"
