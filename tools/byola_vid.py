#!/usr/bin/env python3
import argparse
import os
import os.path as osp
import random
import subprocess
import sys

# --- Start Monkey Patch ---
import types
sys.modules['pytorch_lightning'] = types.ModuleType('pytorch_lightning')
# --- End Monkey Patch ---

from types import SimpleNamespace

import librosa
import numpy as np
import torch
import tqdm
import yaml

try:
    import torchaudio
    import torchaudio.transforms as T
except Exception:
    torchaudio = None
    T = None


ROOT_DIR = osp.dirname(osp.dirname(__file__))
EXTRA_DIRS = [
    osp.join(ROOT_DIR, 'byol-a'),
    '/output/UMMAFormer/byol-a',
]
for path in EXTRA_DIRS:
    if osp.isdir(path) and path not in sys.path:
        sys.path.insert(0, path)

from byol_a.augmentations import PrecomputedNorm
from byol_a.models import AudioNTT2020Task6 as AudioNTT2020Feature


class MelSpec:
    def __init__(self, fs=16000, fft=1024, hop=160, mels=64, fmin=60, fmax=7800):
        self.mfb = librosa.filters.mel(sr=fs, n_fft=fft, n_mels=mels, fmin=fmin, fmax=fmax)
        self.fft = fft
        self.hop = hop

    def __call__(self, wav):
        spec = librosa.stft(np.array(wav), n_fft=self.fft, hop_length=self.hop)
        return torch.tensor(np.matmul(self.mfb, np.abs(spec) ** 2 + np.finfo(float).eps))


def parse_arg():
    ap = argparse.ArgumentParser(description='Extract temporal BYOLA from video')
    ap.add_argument('--list', required=True, help='video list')
    ap.add_argument('--root', required=True, help='video root')
    ap.add_argument('--out', required=True, help='feat out')
    ap.add_argument('--cfg', default='byol-a/config.yaml', help='cfg path')
    ap.add_argument('--ckpt', default='byol-a/pretrained_weights/AudioNTT2020-BYOLA-64x96d2048.pth')
    ap.add_argument('--ff', default='/usr/local/bin/ffmpeg', help='ffmpeg bin')
    ap.add_argument('--stat', default='', help='stat file')
    ap.add_argument('--stat-n', type=int, default=512, help='stat sample num')
    ap.add_argument('--resume', action='store_true')
    return ap.parse_args()


def load_cfg(path):
    with open(path, 'r') as fid:
        data = yaml.safe_load(fid)
    return SimpleNamespace(**data)


def load_list(path):
    with open(path, 'r') as fid:
        return [x.strip().split()[0] for x in fid if x.strip()]


def out_file(root, rel):
    return osp.join(root, osp.splitext(rel)[0] + '.npy')


def has_file(path):
    return osp.exists(path) and os.path.getsize(path) > 0


def read_aud(path, sr, ff):
    cmd = [
        ff,
        '-hide_banner', '-loglevel', 'error',
        '-i', path,
        '-vn', '-ac', '1', '-ar', str(sr),
        '-f', 'f32le', '-'
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if res.returncode != 0:
        err = res.stderr.decode('utf-8', errors='ignore').strip()
        raise RuntimeError(err or 'ffmpeg fail')
    arr = np.frombuffer(res.stdout, dtype=np.float32)
    if arr.size == 0:
        raise RuntimeError('no audio')
    return torch.from_numpy(arr.copy()).unsqueeze(0)


def one_lms(cfg, wav, mel):
    unit = int(cfg.unit_sec * cfg.sample_rate)
    x = wav
    if x.shape[0] > 1:
        x = x.mean(dim=0, keepdim=True)
    x = x[0]
    pad = unit - len(x)
    if pad > 0:
        left = pad // 2
        x = torch.nn.functional.pad(x, (left, pad - left))
    cut = len(x) - unit
    off = random.randint(0, cut) if cut > 0 else 0
    x = x[off:off + unit]
    return (mel(x) + torch.finfo(torch.float32).eps).log().unsqueeze(0)


def load_stat(args, cfg, rows):
    stat = args.stat or osp.join(args.out, '_stat.npy')
    if osp.exists(stat):
        val = np.load(stat)
        if val.shape == (2,):
            return val

    use = rows
    if args.stat_n > 0 and len(use) > args.stat_n:
        use = random.sample(use, args.stat_n)

    mel = MelSpec(
        fs=cfg.sample_rate,
        fft=cfg.n_fft,
        hop=cfg.hop_length,
        mels=cfg.n_mels,
        fmin=cfg.f_min,
        fmax=cfg.f_max,
    )
    buf = []
    last_error = None
    for rel in tqdm.tqdm(use, desc='stat'):
        path = osp.join(args.root, rel)
        try:
            wav = read_aud(path, cfg.sample_rate, args.ff)
            lms = one_lms(cfg, wav, mel)
            buf.append(lms)
        except Exception as e:
            last_error = e
            continue
    if not buf:
        if last_error:
            raise RuntimeError(f'stat empty, last error was: {last_error}') from last_error
        raise RuntimeError('stat empty')
    arr = np.hstack(buf)
    val = np.array([arr.mean(), arr.std()], dtype=np.float32)
    os.makedirs(args.out, exist_ok=True)
    np.save(stat, val)
    return val


def main():
    args = parse_arg()
    cfg = load_cfg(args.cfg)
    dev = torch.device('cuda')

    rows = load_list(args.list)
    os.makedirs(args.out, exist_ok=True)

    stat = load_stat(args, cfg, rows)
    norm = PrecomputedNorm(stat)

    model = AudioNTT2020Feature(n_mels=cfg.n_mels, d=cfg.feature_d).cuda()
    model.load_weight(args.ckpt, dev)
    model.eval()

    if torchaudio is not None:
        mel = torchaudio.transforms.MelSpectrogram(
            sample_rate=cfg.sample_rate,
            n_fft=cfg.n_fft,
            win_length=cfg.win_length,
            hop_length=cfg.hop_length,
            n_mels=cfg.n_mels,
            f_min=cfg.f_min,
            f_max=cfg.f_max,
        )
    else:
        mel = MelSpec(
            fs=cfg.sample_rate,
            fft=cfg.n_fft,
            hop=cfg.hop_length,
            mels=cfg.n_mels,
            fmin=cfg.f_min,
            fmax=cfg.f_max,
        )

    ok = 0
    skip = 0
    fail = 0
    bad = []

    for rel in tqdm.tqdm(rows, total=len(rows), desc='byola'):
        path = osp.join(args.root, rel)
        out = out_file(args.out, rel)
        if args.resume and has_file(out):
            skip += 1
            continue
        try:
            wav = read_aud(path, cfg.sample_rate, args.ff)
            lms = norm((mel(wav) + torch.finfo(torch.float32).eps).log())
            with torch.no_grad():
                feat = model(lms.unsqueeze(0).cuda())
            out_dir = osp.dirname(out)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            tmp = out + '.tmp'
            with open(tmp, 'wb') as fid:
                np.save(fid, feat.squeeze(0).cpu().numpy())
            os.replace(tmp, out)
            ok += 1
        except Exception as err:
            fail += 1
            bad.append(f'{rel}\t{err}')

    print(f'byola ok={ok} skip={skip} fail={fail}')
    if bad:
        err = osp.join(args.out, '_byola_fail.txt')
        with open(err, 'w') as fid:
            for row in bad:
                fid.write(row + '\n')


if __name__ == '__main__':
    main()
