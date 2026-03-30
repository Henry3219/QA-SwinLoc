#!/usr/bin/env python3
import argparse
import json


def load_json(path):
    with open(path, "r") as fid:
        return json.load(fid)


def conv_row(row):
    segs = row.get("segments", [])
    scores = row.get("scores", [])
    out = []
    n = min(len(segs), len(scores))
    for i in range(n):
        seg = segs[i]
        score = scores[i]
        if len(seg) < 2:
            continue
        out.append([
            round(float(score), 4),
            round(float(seg[0]), 2),
            round(float(seg[1]), 2),
        ])
    out.sort(key=lambda x: x[0], reverse=True)
    return out[:100]


def conv_data(data):
    out = {}
    for row in data:
        key = row["file"]
        out[key] = conv_row(row)
    return out


def write_pred(data, path):
    with open(path, "w") as fid:
        fid.write("{\n")
        keys = list(data.keys())
        for i, key in enumerate(keys):
            fid.write(f'    {json.dumps(key)}: [\n')
            rows = data[key]
            for j, row in enumerate(rows):
                tail = "," if j + 1 < len(rows) else ""
                fid.write(f"        {json.dumps(row)}{tail}\n")
            end = "," if i + 1 < len(keys) else ""
            fid.write(f"    ]{end}\n")
        fid.write("}\n")


def main():
    ap = argparse.ArgumentParser(description="Convert AV1M sub json to official pred json")
    ap.add_argument("src", help="input sub json")
    ap.add_argument("dst", nargs="?", default="prediction.json", help="output prediction json")
    args = ap.parse_args()

    data = load_json(args.src)
    out = conv_data(data)

    write_pred(out, args.dst)

    print("saved", args.dst, len(out))


if __name__ == "__main__":
    main()
