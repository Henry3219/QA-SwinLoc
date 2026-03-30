import os
import json
import argparse
from multiprocessing import Pool

import cv2


def probe_vid(args):
    root, name = args
    path = os.path.join(root, "test", name)
    cap = cv2.VideoCapture(path)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    vfrm = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    cap.release()
    if fps <= 0:
        fps = 25.0
    dur = float(vfrm) / float(fps) if fps > 0 else 0.0
    return {
        "file": name,
        "split": "test",
        "duration": dur,
        "fps": fps,
        "video_frames": vfrm,
        "fake_segments": [],
    }


def build_test(root, ann, jobs):
    src = os.path.join(root, "test_files.txt")
    dst = os.path.join(ann, "test.json")
    with open(src, "r") as fid:
        names = [x.strip() for x in fid if x.strip()]
    with Pool(processes=jobs) as pool:
        data = list(pool.imap_unordered(probe_vid, [(root, x) for x in names], chunksize=256))
    data.sort(key=lambda x: x["file"])
    os.makedirs(ann, exist_ok=True)
    with open(dst, "w") as fid:
        json.dump(data, fid)
    print("saved", dst, len(data))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="data/AV-Deepfake1M/dataset")
    parser.add_argument("--ann", default="data/AV-Deepfake1M/annatations")
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    build_test(args.root, args.ann, args.jobs)


if __name__ == "__main__":
    main()
