#!/usr/bin/env python3
import argparse
import math
import os
import os.path as osp
import shutil
import time
import json
from concurrent.futures import ThreadPoolExecutor


def load_list(path):
    with open(path, 'r') as fid:
        return [x.strip().split()[0] for x in fid if x.strip()]

def load_json(path):
    with open(path, 'r') as fid:
        data = json.load(fid)
        return [item['file'] for item in data]


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def out_file(root, rel):
    return osp.join(root, osp.splitext(rel)[0] + '.npy')


def has_file(path):
    return osp.exists(path) and os.path.getsize(path) > 0


def is_todo(rel, aud_root):
    return not has_file(out_file(aud_root, rel))


def chunked(rows, size):
    total = int(math.ceil(len(rows) / float(size))) if rows else 0
    for idx in range(total):
        beg = idx * size
        end = min(len(rows), beg + size)
        yield idx, rows[beg:end]


def split_dir(queue_root, split):
    return osp.join(queue_root, split)


def state_dir(queue_root, split, state):
    return osp.join(split_dir(queue_root, split), state)


def write_lines(path, rows):
    ensure_dir(osp.dirname(path) or '.')
    with open(path, 'w') as fid:
        for row in rows:
            fid.write(row + '\n')


def clean_split(queue_root, split):
    root = split_dir(queue_root, split)
    running = state_dir(queue_root, split, 'running')
    if osp.isdir(running):
        active = [x for x in os.listdir(running) if x.endswith('.txt')]
        if active:
            raise RuntimeError(f'queue split={split} has running chunks')
    if osp.isdir(root):
        shutil.rmtree(root)
    for state in ('pending', 'running', 'done', 'failed', 'logs'):
        ensure_dir(state_dir(queue_root, split, state))


def build_one(args, split):
    source = args.source_tpl.format(split=split)
    if split == 'train':
        source = source.replace('_files.txt', '_metadata.json')
    seed = args.seed_tpl.format(split=split) if args.seed_tpl else ''
    todo_out = args.todo_tpl.format(split=split)
    if not osp.exists(source):
        raise FileNotFoundError(source)

    if args.mode == 'warm' and seed and osp.exists(seed):
        rows = load_list(seed)
        src_used = seed
    else:
        if split == 'train':
            rows = load_json(source)
        else:
            rows = load_list(source)
        src_used = source

    aud_root = osp.join(args.out_root, split)

    def check(rel):
        return rel if is_todo(rel, aud_root) else None

    todo = []
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        for rel in ex.map(check, rows, chunksize=args.scan_chunk):
            if rel is not None:
                todo.append(rel)

    clean_split(args.queue_root, split)
    write_lines(todo_out, todo)

    pending = state_dir(args.queue_root, split, 'pending')
    for idx, part in chunked(todo, args.chunk):
        name = f'{idx:06d}.txt'
        write_lines(osp.join(pending, name), part)

    print(f'build split={split} mode={args.mode} src={src_used} total={len(rows)} todo={len(todo)} chunk={args.chunk}')


def iter_state_files(queue_root, split, state):
    root = state_dir(queue_root, split, state)
    if not osp.isdir(root):
        return []
    out = []
    for name in sorted(os.listdir(root)):
        path = osp.join(root, name)
        if osp.isfile(path) and name.endswith('.txt'):
            out.append(path)
    return out


def recycle_one(args, split):
    now = time.time()
    moved = 0
    states = ['running']
    if args.failed:
        states.append('failed')
    for state in states:
        for src in iter_state_files(args.queue_root, split, state):
            if args.stale > 0:
                age = now - osp.getmtime(src)
                if age < args.stale * 60:
                    continue
            base = osp.basename(src)
            if '__' in base:
                base = base.split('__', 1)[1]
            dst = osp.join(state_dir(args.queue_root, split, 'pending'), base)
            if osp.exists(dst):
                stem, ext = osp.splitext(base)
                dst = osp.join(state_dir(args.queue_root, split, 'pending'), f'{stem}_{int(now)}{ext}')
            os.replace(src, dst)
            moved += 1
    print(f'recycle split={split} moved={moved}')


def count_lines(path):
    n = 0
    with open(path, 'r') as fid:
        for _ in fid:
            n += 1
    return n


def status_one(args, split):
    parts = []
    for state in ('pending', 'running', 'done', 'failed'):
        files = iter_state_files(args.queue_root, split, state)
        items = sum(count_lines(path) for path in files)
        parts.append(f'{state}={len(files)}f/{items}i')
    print(f'status split={split} ' + ' '.join(parts))


def parse_args():
    ap = argparse.ArgumentParser(description='Queue helper for AV1M audio-only extraction')
    sub = ap.add_subparsers(dest='cmd', required=True)

    build = sub.add_parser('build')
    build.add_argument('--split', action='append', required=True)
    build.add_argument('--source-tpl', default='data/avdf/{split}.txt')
    build.add_argument('--seed-tpl', default='data/todo/{split}.txt')
    build.add_argument('--todo-tpl', default='data/todo/{split}.aud.txt')
    build.add_argument('--queue-root', required=True)
    build.add_argument('--out-root', required=True)
    build.add_argument('--mode', choices=['warm', 'full'], default='warm')
    build.add_argument('--chunk', type=int, default=2000)
    build.add_argument('--jobs', type=int, default=32)
    build.add_argument('--scan-chunk', type=int, default=256)

    recycle = sub.add_parser('recycle')
    recycle.add_argument('--split', action='append', required=True)
    recycle.add_argument('--queue-root', required=True)
    recycle.add_argument('--stale', type=int, default=0)
    recycle.add_argument('--failed', action='store_true')

    status = sub.add_parser('status')
    status.add_argument('--split', action='append', required=True)
    status.add_argument('--queue-root', required=True)
    return ap.parse_args()


def main():
    args = parse_args()
    if args.cmd == 'build':
        for split in args.split:
            build_one(args, split)
        return
    if args.cmd == 'recycle':
        for split in args.split:
            recycle_one(args, split)
        return
    if args.cmd == 'status':
        for split in args.split:
            status_one(args, split)
        return


if __name__ == '__main__':
    main()
