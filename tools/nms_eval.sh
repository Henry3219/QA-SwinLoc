#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "$0")/.." && pwd)"
base_cfg="${1:-$root_dir/configs/UMMAFormer/lavdf_tsn_audio.yaml}"
ckpt="${2:-/input0/Backup/model/UMMAFormer_exp08/paper_results/lavdf_tsn_audio_2026_03_05_06_32_07/last.pth.tar}"
tag="${3:-nms}"
max_run="${4:-2}"
num_work="${5:-4}"
eval_jobs="${6:-4}"

if [[ ! -f "$base_cfg" ]]; then
  echo "[ERR] base cfg not found: $base_cfg" >&2
  exit 1
fi
if [[ ! -f "$ckpt" ]]; then
  echo "[ERR] ckpt not found: $ckpt" >&2
  exit 1
fi

cfg_dir="/tmp/umma_cfg_${tag}"
log_dir="/tmp/umma_log_${tag}"
mkdir -p "$cfg_dir" "$log_dir"

# case_id adapt_nms export_topk len_thr sigma_s sigma_l
cases=(
  "c1 0 100 0.7 0.75 0.75"
  "c2 0 200 0.7 0.75 0.75"
  "c3 0 -1 0.7 0.75 0.75"
  "c4 1 100 0.7 0.65 0.85"
  "c5 1 200 0.7 0.65 0.85"
  "c6 1 200 0.7 0.50 0.85"
  "c7 1 200 0.5 0.50 0.80"
  "c8 1 200 0.9 0.65 0.90"
)

mk_cfg() {
  local case_id="$1"
  local adapt_nms="$2"
  local export_topk="$3"
  local len_thr="$4"
  local sigma_s="$5"
  local sigma_l="$6"
  local cfg_out="$cfg_dir/lavdf_${case_id}.yaml"

  python - <<'PY' "$base_cfg" "$cfg_out" "$adapt_nms" "$export_topk" "$len_thr" "$sigma_s" "$sigma_l" "$num_work" "$eval_jobs"
import sys, yaml
in_cfg, out_cfg, adapt_nms, export_topk, len_thr, sigma_s, sigma_l, num_work, eval_jobs = sys.argv[1:]
with open(in_cfg, 'r', encoding='utf-8') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

cfg.setdefault('model', {})
cfg.setdefault('train_cfg', {})
cfg.setdefault('test_cfg', {})
cfg.setdefault('loader', {})

cfg['model']['refine_on'] = False
cfg['train_cfg']['con_on'] = False

cfg['loader']['num_workers'] = int(num_work)
cfg['test_cfg']['adapt_nms'] = bool(int(adapt_nms))
cfg['test_cfg']['export_topk'] = int(export_topk)
cfg['test_cfg']['len_thr'] = float(len_thr)
cfg['test_cfg']['sigma_s'] = float(sigma_s)
cfg['test_cfg']['sigma_l'] = float(sigma_l)
cfg['test_cfg']['eval_jobs'] = int(eval_jobs)

with open(out_cfg, 'w', encoding='utf-8') as f:
    yaml.safe_dump(cfg, f, sort_keys=False)
PY
}

run_one() {
  local case_id="$1"
  local out_name="${tag}_${case_id}"
  local cfg_in="$cfg_dir/lavdf_${case_id}.yaml"
  local log_out="$log_dir/${out_name}.log"
  local run_dir="$root_dir/paper_results/${out_name}"
  local run_ckpt="$run_dir/last.pth.tar"
  mkdir -p "$run_dir"
  ln -sfn "$ckpt" "$run_ckpt"

  echo "[RUN] $case_id -> $out_name"
  (
    export OMP_NUM_THREADS=1
    export MKL_NUM_THREADS=1
    export NUMEXPR_NUM_THREADS=1
    cd "$root_dir"
    python eval.py "$cfg_in" "$run_ckpt"
  ) >"$log_out" 2>&1

  local res_txt="$run_dir/test_results.txt"
  echo "[DONE] $case_id => $res_txt"
  sed -n '1,2p' "$res_txt"
}

echo "[INFO] root=$root_dir"
echo "[INFO] cfg=$base_cfg"
echo "[INFO] ckpt=$ckpt"
echo "[INFO] tag=$tag"
echo "[INFO] max_run=$max_run num_work=$num_work eval_jobs=$eval_jobs"

declare -a pids=()
for c in "${cases[@]}"; do
  # shellcheck disable=SC2086
  mk_cfg $c
  case_id="${c%% *}"
  run_one "$case_id" &
  pids+=("$!")
  while [[ "$(jobs -rp | wc -l)" -ge "$max_run" ]]; do
    wait -n
  done
done

for pid in "${pids[@]}"; do
  wait "$pid"
done

echo "[OK] all eval done"
echo "[LOG] $log_dir"
