#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "use: bash tools/scan_post.sh <cfg> <ckpt> [out]"
  exit 1
fi

cfg="$1"
ckpt="$2"
out="${3:-scan_out}"

mkdir -p "$out"/log "$out"/json "$out"/cfg
mkdir -p "$out"/txt

cdir="$(dirname "$ckpt")"
sum="$out/sum.txt"
res="$out/res.tsv"
: > "$sum"
echo -e "tag\tduration_thresh\tmin_score\tvoting_thresh\tmax_seg_num\tmAP\tAR_AUC\tAR10\tAR20\tAR50\tAR100" > "$res"

if command -v rg >/dev/null 2>&1; then
  finder() { rg -n "AP@|AR@|Avg|mAP|average|Average|Area Under" "$1" || true; }
else
  finder() { grep -nE "AP@|AR@|Avg|mAP|average|Average|Area Under" "$1" || true; }
fi

dur=(0.001 0.003 0.005)
mins=(0.001 0.003 0.005)
vot=(0.85 0.90 0.95)
top=(100 200)

for d in "${dur[@]}"; do
  for m in "${mins[@]}"; do
    for v in "${vot[@]}"; do
      for t in "${top[@]}"; do
        tag="d${d}_m${m}_v${v}_t${t}"
        tmp="$out/cfg/$tag.yaml"
        log="$out/log/$tag.txt"
        jso="$out/json/$tag.json"
        txt="$out/txt/$tag.txt"

        python - "$cfg" "$tmp" "$d" "$m" "$v" "$t" <<'PY'
import sys, yaml
src, dst, d, m, v, t = sys.argv[1:]
with open(src, "r") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)
cfg["test_cfg"]["duration_thresh"] = float(d)
cfg["test_cfg"]["min_score"] = float(m)
cfg["test_cfg"]["voting_thresh"] = float(v)
cfg["test_cfg"]["max_seg_num"] = int(t)
with open(dst, "w") as f:
    yaml.safe_dump(cfg, f, sort_keys=False)
PY

        echo "[run] $tag"
        python eval.py "$tmp" "$ckpt" -p 99999 > "$log" 2>&1

        if [ -f "$cdir/test_results.json" ]; then
          cp "$cdir/test_results.json" "$jso"
        fi
        if [ -f "$cdir/test_results.txt" ]; then
          python - "$cdir/test_results.txt" "$txt" <<'PY'
import re, sys
src, dst = sys.argv[1:]
lines=[x.strip() for x in open(src,encoding='utf-8',errors='ignore') if x.strip()]
d=p=None
for i in range(len(lines)-1):
    if lines[i].startswith('Detection:') and lines[i+1].startswith('Proposal:'):
        d, p = lines[i], lines[i+1]
open(dst,'w',encoding='utf-8').write((d or '') + '\\n' + (p or '') + '\\n')
PY
        fi

        map_v="$(python - "$log" <<'PY'
import re,sys
s=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
m=re.search(r'Average-mAP:\\s*([0-9.]+)',s)
print(m.group(1) if m else '')
PY
)"
        arauc_v="$(python - "$log" <<'PY'
import re,sys
s=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
m=re.search(r'Area Under the AR vs AN curve:\\s*([0-9.]+)%',s)
print(m.group(1) if m else '')
PY
)"
        ar100_v="$(python - "$log" <<'PY'
import re,sys
s=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
m=re.search(r'AR@100\\s*([0-9.]+)',s)
print(m.group(1) if m else '')
PY
)"
        ar10_v="$(python - "$txt" <<'PY'
import re,sys
s=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
m=re.search(r'AR@10\\s*([0-9.]+)',s)
print(m.group(1) if m else '')
PY
)"
        ar20_v="$(python - "$txt" <<'PY'
import re,sys
s=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
m=re.search(r'AR@20\\s*([0-9.]+)',s)
print(m.group(1) if m else '')
PY
)"
        ar50_v="$(python - "$txt" <<'PY'
import re,sys
s=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
m=re.search(r'AR@50\\s*([0-9.]+)',s)
print(m.group(1) if m else '')
PY
)"
        if [ -z "$ar100_v" ]; then
          ar100_v="$(python - "$txt" <<'PY'
import re,sys
s=open(sys.argv[1],encoding='utf-8',errors='ignore').read()
m=re.search(r'AR@100\\s*([0-9.]+)',s)
print(m.group(1) if m else '')
PY
)"
        fi
        echo -e "$tag\t$d\t$m\t$v\t$t\t$map_v\t$arauc_v\t$ar10_v\t$ar20_v\t$ar50_v\t$ar100_v" >> "$res"

        {
          echo "[$tag]"
          finder "$log"
          echo
        } >> "$sum"
      done
    done
  done
done

echo "done: $out"
echo "sum : $sum"
echo "res : $res"
