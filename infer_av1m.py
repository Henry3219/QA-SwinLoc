#!/usr/bin/env python3
import argparse
import glob
import json
import os

import torch
import torch.nn as nn

from libs.core import load_config
from libs.datasets import make_dataset, make_data_loader
from libs.modeling import make_meta_arch
from libs.utils import fix_random_seed


def load_ckpt(path):
    if path.endswith(".pth.tar"):
        return path
    return sorted(glob.glob(os.path.join(path, "*.pth.tar")))[-1]


def to_pred(item):
    segs = item["segments"].detach().cpu().numpy().tolist()
    scores = item["scores"].detach().cpu().numpy().tolist()
    out = []
    n = min(len(segs), len(scores))
    for i in range(n):
        seg = segs[i]
        if len(seg) < 2:
            continue
        out.append([
            round(float(scores[i]), 4),
            round(float(seg[0]), 2),
            round(float(seg[1]), 2),
        ])
    out.sort(key=lambda x: x[0], reverse=True)
    out = out[:100]
    if not out:
        return [[0.0, 0.0, 0.0]]
    return out


def load_expected_ids(dataset):
    if hasattr(dataset, "_meta_list"):
        ids = []
        seen = set()
        for meta_path in dataset._meta_list():
            with open(meta_path, "r") as fid:
                items = json.load(fid)
            for item in items:
                split = item.get("split", "").lower()
                if split not in dataset.split:
                    continue
                vid = item.get("file")
                if (not vid) or (vid in seen):
                    continue
                ids.append(vid)
                seen.add(vid)
        if ids:
            return ids

    return [item["id"] for item in dataset.data_list]


def dump_pred(loader, model, out_file):
    model.eval()
    out = {}
    for video_list in loader:
        with torch.no_grad():
            res = model(video_list)
        for item in res:
            out[item["video_id"]] = to_pred(item)

    expected_ids = load_expected_ids(loader.dataset)
    for vid in expected_ids:
        if vid not in out:
            out[vid] = [[0.0, 0.0, 0.0]]

    write_pred(out, out_file, expected_ids)
    print("saved", out_file, len(out))


def write_pred(data, out_file, keys=None):
    with open(out_file, "w") as fid:
        fid.write("{\n")
        if keys is None:
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


def main(args):
    cfg = load_config(args.config)
    _ = fix_random_seed(0, include_cuda=True)

    ckpt = load_ckpt(args.ckpt)

    batch = args.batch if args.batch > 0 else cfg["loader"]["batch_size"]
    workers = args.workers if args.workers >= 0 else cfg["loader"]["num_workers"]

    data = make_dataset(
        cfg["dataset_name"],
        False,
        cfg["test_split"],
        **cfg["dataset"],
    )
    loader = make_data_loader(data, False, None, batch, workers)

    model = make_meta_arch(cfg["model_name"], **cfg["model"])
    if len(cfg["devices"]) > 1:
        model = nn.DataParallel(model, device_ids=cfg["devices"])
    else:
        model = model.to(cfg["devices"][0])

    state = torch.load(
        ckpt,
        map_location=lambda storage, loc: storage.cuda(cfg["devices"][0]),
    )
    if "state_dict_ema" in state:
        model.load_state_dict(state["state_dict_ema"])
    else:
        model.load_state_dict(state["state_dict"])

    dump_pred(loader, model, args.out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Infer AV1M and save official pred json")
    ap.add_argument("config")
    ap.add_argument("ckpt")
    ap.add_argument("--out", default="prediction.json")
    ap.add_argument("--batch", type=int, default=0, help="0 means use config loader.batch_size")
    ap.add_argument("--workers", type=int, default=-1, help="-1 means use config loader.num_workers")
    main(ap.parse_args())
