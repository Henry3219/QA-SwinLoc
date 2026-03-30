#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cfg="${1:-$root/configs/UMMAFormer/lavdf_qual.yaml}"
ckpt="${2:-$root/paper_results/lavdf_qual_qual/last.pth.tar}"
tag="${3:-qual_scan}"
part="${4:-all}"
sel="${5:-}"

if [[ ! -f "$cfg" ]]; then
  echo "[ERR] cfg not found: $cfg" >&2
  exit 1
fi
if [[ ! -f "$ckpt" ]]; then
  echo "[ERR] ckpt not found: $ckpt" >&2
  exit 1
fi
ckpt="$(cd "$(dirname "$ckpt")" && pwd)/$(basename "$ckpt")"

tmp="/tmp/${tag}_cfg"
out="$root/paper_results/${tag}"
mkdir -p "$tmp" "$out"

sum="$out/res_${part}.tsv"
echo -e "id\tmin\tsig\tpre\tmAP\tmAP50\tmAP75\tmAP95\tAR10\tAR20\tAR50\tAR100" > "$sum"

cases=(
  "a 0.001 0.50 1000"
  "b 0.001 0.65 2000"
  "c 0.001 0.75 3000"
  "d 0.002 0.50 2000"
  "e 0.002 0.65 3000"
  "f 0.003 0.50 2000"
  "g 0.003 0.65 2000"
  "h 0.003 0.75 2000"
  "i 0.005 0.65 1000"
  "j 0.005 0.75 2000"
  "k 0.010 0.75 2000"
)

pick() {
  local id="$1"
  if [[ -n "$sel" ]]; then
    case ",$sel," in
      *",$id,"*) return 0 ;;
      *) return 1 ;;
    esac
  fi
  case "$part" in
    all) return 0 ;;
    p1) [[ "$id" =~ ^[a-f]$ ]] ;;
    p2) [[ "$id" =~ ^[g-k]$ ]] ;;
    *)
      echo "[ERR] bad part: $part (use all|p1|p2)" >&2
      exit 1
      ;;
  esac
}

mk_cfg() {
  local id="$1"
  local min="$2"
  local sig="$3"
  local pre="$4"
  local dst="$tmp/${tag}_${id}.yaml"

  python - <<'PY' "$cfg" "$dst" "$min" "$sig" "$pre"
import sys, yaml
src, dst, min_s, sig, pre = sys.argv[1:]
with open(src, "r", encoding="utf-8") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)
cfg["test_cfg"]["min_score"] = float(min_s)
cfg["test_cfg"]["nms_sigma"] = float(sig)
cfg["test_cfg"]["pre_nms_topk"] = int(pre)
with open(dst, "w", encoding="utf-8") as f:
    yaml.safe_dump(cfg, f, sort_keys=False)
PY
}

one() {
  local id="$1"
  local min="$2"
  local sig="$3"
  local pre="$4"
  local run="$out/${tag}_${id}"
  local cfg_i="$tmp/${tag}_${id}.yaml"

  mkdir -p "$run"
  ln -sfn "$ckpt" "$run/last.pth.tar"

  echo "[RUN] $id min=$min sig=$sig pre=$pre"
  (
    cd "$root"
    python eval.py "$cfg_i" "$run/last.pth.tar"
  ) > "$run/eval.log" 2>&1

  local txt="$run/test_results.txt"
  if [[ ! -f "$txt" ]]; then
    echo "[ERR] missing result: $txt" >&2
    exit 1
  fi

  python - <<'PY' "$txt" "$sum" "$id" "$min" "$sig" "$pre"
import re, sys
txt, out, id_, min_s, sig, pre = sys.argv[1:]
s = open(txt, encoding="utf-8").read()
dm = re.search(r'average-mAP ([0-9.]+).*?mAP@0.50 ([0-9.]+).*?mAP@0.75 ([0-9.]+).*?mAP@0.95 ([0-9.]+)', s)
pm = re.search(r'AR@10 ([0-9.]+)\s+AR@20 ([0-9.]+)\s+AR@50 ([0-9.]+)\s+AR@100 ([0-9.]+)', s)
if not dm or not pm:
    raise SystemExit("parse fail: " + txt)
row = [
    id_, min_s, sig, pre,
    dm.group(1), dm.group(2), dm.group(3), dm.group(4),
    pm.group(1), pm.group(2), pm.group(3), pm.group(4),
]
with open(out, "a", encoding="utf-8") as f:
    f.write("\t".join(row) + "\n")
print("\t".join(row))
PY
}

echo "[INFO] cfg=$cfg"
echo "[INFO] ckpt=$ckpt"
echo "[INFO] out=$out"
echo "[INFO] part=$part"
if [[ -n "$sel" ]]; then
  echo "[INFO] sel=$sel"
fi

for c in "${cases[@]}"; do
  id="${c%% *}"
  if ! pick "$id"; then
    continue
  fi
  # shellcheck disable=SC2086
  mk_cfg $c
  # shellcheck disable=SC2086
  one $c
done

echo "[OK] $sum"
