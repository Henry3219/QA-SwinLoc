#!/usr/bin/env python3
import argparse
import os
import os.path as osp
import subprocess
import sys
import tempfile


def parse_args():
    ap = argparse.ArgumentParser(description="Fill missing AV1M features")
    ap.add_argument("--split", required=True, choices=["train", "test", "val"])
    ap.add_argument("files", nargs="+", help="relative file names")
    ap.add_argument("--root", default="data/AV-Deepfake1M/dataset")
    ap.add_argument("--out", default="/input0/Backup/features/AV-Deepfake1M-UMM")
    ap.add_argument("--aud-out", default="/input0/Backup/features/AV-Deepfake1M-UMM/byola_t")
    ap.add_argument("--tsn-batch", type=int, default=448)
    ap.add_argument("--rgb-ckpt", default="/output/UMMAFormer/mmaction2/pretrained/tsn_r50_320p_1x1x8_50e_activitynet_clip_rgb_20210301-c0f04a7e.pth")
    ap.add_argument("--flow-ckpt", default="/output/UMMAFormer/mmaction2/pretrained/tsn_r50_320p_1x1x8_150e_activitynet_clip_flow_20200804-8622cf38.pth")
    ap.add_argument("--ff", default="/usr/local/bin/ffmpeg")
    return ap.parse_args()


def npy_path(root, split, rel):
    stem = osp.splitext(rel)[0]
    return osp.join(root, split, stem + ".npy")


def has_file(path):
    return osp.exists(path) and osp.getsize(path) > 0


def split_rows(args):
    tsn_rows = []
    aud_rows = []
    for rel in args.files:
        rgb = npy_path(osp.join(args.out, "tsn", "rgb"), args.split, rel)
        flow = npy_path(osp.join(args.out, "tsn", "flow"), args.split, rel)
        aud = npy_path(args.aud_out, args.split, rel)
        need_tsn = not (has_file(rgb) and has_file(flow))
        need_aud = not has_file(aud)
        if need_tsn:
            tsn_rows.append(rel)
        if need_aud:
            aud_rows.append(rel)
    return tsn_rows, aud_rows


def write_list(rows):
    fd, path = tempfile.mkstemp(prefix="fill_", suffix=".txt")
    os.close(fd)
    with open(path, "w") as fid:
        for row in rows:
            fid.write(row + "\n")
    return path


def run_cmd(cmd):
    print("run:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def fill_tsn(args, rows):
    if not rows:
        return
    path = write_list(rows)
    try:
        cmd = [
            sys.executable,
            "/output/UMMAFormer/tools/feat_fuse.py",
            "--list", path,
            "--root", osp.join(args.root, args.split),
            "--rgb-out", osp.join(args.out, "tsn", "rgb", args.split),
            "--flow-out", osp.join(args.out, "tsn", "flow", args.split),
            "--aud-out", osp.join(args.out, "byol", args.split),
            "--rgb-ckpt", args.rgb_ckpt,
            "--flow-ckpt", args.flow_ckpt,
            "--mode", "tsn",
            "--batch", str(args.tsn_batch),
            "--resume",
        ]
        run_cmd(cmd)
    finally:
        if osp.exists(path):
            os.remove(path)


def fill_aud(args, rows):
    if not rows:
        return
    path = write_list(rows)
    try:
        cmd = [
            sys.executable,
            "tools/byola_vid.py",
            "--list", path,
            "--root", osp.join(args.root, args.split),
            "--out", osp.join(args.aud_out, args.split),
            "--ff", args.ff,
            "--resume",
        ]
        run_cmd(cmd)
    finally:
        if osp.exists(path):
            os.remove(path)


def main():
    args = parse_args()
    tsn_rows, aud_rows = split_rows(args)
    print("tsn", len(tsn_rows), "aud", len(aud_rows))
    fill_tsn(args, tsn_rows)
    fill_aud(args, aud_rows)


if __name__ == "__main__":
    main()
