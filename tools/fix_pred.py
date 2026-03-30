import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: python tools/fix_pred.py <sub.json> <prediction.json>")

    src = Path(sys.argv[1])
    out = Path(sys.argv[2])

    with src.open("r") as f:
        raw = json.load(f)

    res = {}
    for item in raw:
        key = item["file"]
        segs = item.get("segments", [])
        scores = item.get("scores", [])
        rows = []
        for seg, score in zip(segs, scores):
            if not seg or len(seg) != 2:
                continue
            beg, end = seg
            rows.append([
                round(float(score), 4),
                round(float(beg), 4),
                round(float(end), 4),
            ])
        rows.sort(key=lambda x: x[0], reverse=True)
        res[key] = rows[:100]

    res["256754.mp4"] = []
    keys = sorted(res.keys())

    with out.open("w") as f:
        f.write("{\n")
        for i, key in enumerate(keys):
            f.write(f"    {json.dumps(key)}: [\n")
            rows = res[key]
            for j, row in enumerate(rows):
                tail = "," if j + 1 < len(rows) else ""
                f.write(f"        {json.dumps(row)}{tail}\n")
            end = "," if i + 1 < len(keys) else ""
            f.write(f"    ]{end}\n")
        f.write("}\n")

    print("saved", out)
    print("count", len(res))
    print("has_256754", "256754.mp4" in res)


if __name__ == "__main__":
    main()
