import json
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="data/AV-Deepfake1M/annatations/train_metadata.json")
    parser.add_argument("--dst", default="data/AV-Deepfake1M/annatations/train_tiny.json")
    parser.add_argument("--num", type=int, default=16)
    args = parser.parse_args()

    with open(args.src, "r") as fid:
        data = json.load(fid)

    out = data[:args.num]
    with open(args.dst, "w") as fid:
        json.dump(out, fid)
    print("saved", args.dst, len(out))


if __name__ == "__main__":
    main()
