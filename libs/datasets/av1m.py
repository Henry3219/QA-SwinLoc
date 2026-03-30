import os
import json
import pickle
import hashlib

import numpy as np
import torch
from torch.utils.data import Dataset
from torch.nn import functional as F

from .datasets import register_dataset
from .data_utils import truncate_feats


@register_dataset("av1m")
class AV1MDataset(Dataset):
    def __init__(
        self,
        is_training,
        split,
        feat_folder,
        audio_feat_folder,
        json_file,
        feat_stride,
        num_frames,
        default_fps,
        downsample_rate,
        max_seq_len,
        trunc_thresh,
        crop_ratio,
        input_dim,
        audio_input_dim,
        num_classes,
        file_prefix,
        file_ext,
        audio_file_ext,
        force_upsampling,
        use_cache=True,
        cache_file=None,
        audio_sr=16000,
    ):
        assert os.path.exists(feat_folder)
        assert os.path.exists(json_file)
        assert isinstance(split, (tuple, list))
        assert crop_ratio is None or len(crop_ratio) == 2

        self.feat_folder = feat_folder
        self.audio_feat_folder = audio_feat_folder
        self.file_prefix = file_prefix if file_prefix is not None else ""
        self.file_ext = file_ext
        self.audio_file_ext = audio_file_ext
        self.json_file = json_file
        self.use_cache = use_cache
        self.cache_file = cache_file
        self.audio_sr = audio_sr

        self.force_upsampling = force_upsampling
        self.split = [x.lower() for x in split]
        self.is_training = is_training

        self.feat_stride = feat_stride
        self.num_frames = num_frames
        self.input_dim = input_dim
        self.audio_input_dim = audio_input_dim
        self.default_fps = default_fps
        self.downsample_rate = downsample_rate
        self.max_seq_len = max_seq_len
        self.trunc_thresh = trunc_thresh
        self.num_classes = num_classes
        self.crop_ratio = crop_ratio

        self.data_list = self._load_db()
        assert num_classes == 1

        self.db_attributes = {
            "dataset_name": "AV1M",
            "tiou_thresholds": np.linspace(0.5, 0.95, 10),
            "empty_label_ids": [],
        }
        print("{} subset has {} videos".format(self.split, len(self.data_list)))

    def _meta_list(self):
        if os.path.isfile(self.json_file):
            return [self.json_file]

        files = []
        for name in self.split:
            cand = []
            if name == "train":
                cand = ["train.json", "train_metadata.json"]
            elif name == "test":
                cand = ["test.json", "test_metadata.json"]
            elif name in ["val", "dev", "validation"]:
                cand = ["val.json", "val_metadata.json", "dev.json"]
            else:
                cand = [name + ".json"]
            hit = None
            for base in cand:
                path = os.path.join(self.json_file, base)
                if os.path.exists(path):
                    hit = path
                    break
            if hit is None:
                raise FileNotFoundError("No meta file for split {}".format(name))
            files.append(hit)
        return files

    def _cache_path(self):
        if self.cache_file is not None:
            return self.cache_file
        key = {
            "json_file": self.json_file,
            "split": list(self.split),
            "feat_folder": self.feat_folder,
            "audio_feat_folder": self.audio_feat_folder,
            "file_prefix": self.file_prefix,
            "file_ext": self.file_ext,
            "audio_file_ext": self.audio_file_ext,
            "audio_sr": self.audio_sr,
        }
        key_raw = json.dumps(key, sort_keys=True, default=str)
        key_id = hashlib.md5(key_raw.encode("utf-8")).hexdigest()[:12]
        base = "av1m_{}.pkl".format(key_id)
        root = self.json_file if os.path.isdir(self.json_file) else os.path.dirname(self.json_file)
        return os.path.join(root, "." + base)

    def get_attributes(self):
        return self.db_attributes

    def _load_db(self):
        cache_path = self._cache_path()
        if self.use_cache and os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as fid:
                    payload = pickle.load(fid)
                print("Loaded index cache:", cache_path)
                return tuple(payload["data"] if isinstance(payload, dict) else payload)
            except Exception as err:
                print("Index cache read failed, rebuild:", err)

        db = []
        for meta_path in self._meta_list():
            with open(meta_path, "r") as fid:
                items = json.load(fid)
            for item in items:
                cur = self._map_item(item)
                if cur is not None:
                    db.append(cur)
        db = tuple(db)

        if self.use_cache:
            try:
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                tmp = cache_path + ".tmp"
                with open(tmp, "wb") as fid:
                    pickle.dump({"data": db}, fid, protocol=pickle.HIGHEST_PROTOCOL)
                os.replace(tmp, cache_path)
                print("Saved index cache:", cache_path)
            except Exception as err:
                print("Index cache write failed:", err)
        return db

    def _map_item(self, item):
        split = item.get("split", "").lower()
        if split not in self.split:
            return None

        file = item["file"]
        stem = os.path.splitext(file)[0]
        rgb_file = os.path.join(self.feat_folder, self.file_prefix[0], split, stem + self.file_ext)
        if not os.path.exists(rgb_file):
            return None

        dur = item.get("duration", None)
        fps = item.get("fps", None)
        vfrm = item.get("video_frames", None)
        afrm = item.get("audio_frames", None)

        if (dur is None) and (afrm is not None):
            dur = float(afrm) / float(self.audio_sr)
        if (fps is None) and (dur is not None) and (vfrm is not None) and (dur > 0):
            fps = float(vfrm) / float(dur)
        if fps is None and self.default_fps is not None:
            fps = float(self.default_fps)
        if (dur is None) and (fps is not None) and (vfrm is not None) and (fps > 0):
            dur = float(vfrm) / float(fps)
        if (dur is None) or (fps is None):
            return None

        mtype = item.get("modify_type", "real")
        video = int(mtype in ["visual_modified", "both_modified"])
        audio = int(mtype in ["audio_modified", "both_modified"])
        segs = item.get("fake_segments", item.get("fake_periods", []))
        if segs and len(segs) > 0:
            segs = np.asarray(segs, dtype=np.float32)
            labels = np.zeros((segs.shape[0],), dtype=np.int64)
        else:
            segs = None
            labels = None

        return {
            "id": file,
            "stem": stem,
            "fps": float(fps),
            "duration": float(dur),
            "split": split,
            "segments": segs,
            "labels": labels,
            "av_labels": np.asarray([video, audio], dtype=np.int64),
        }

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx):
        item = self.data_list[idx]
        stem = item["stem"]
        split = item["split"]

        if isinstance(self.file_prefix, list):
            rgb = np.load(os.path.join(self.feat_folder, self.file_prefix[0], split, stem + self.file_ext)).astype(np.float32)
            flow = np.load(os.path.join(self.feat_folder, self.file_prefix[1], split, stem + self.file_ext)).astype(np.float32)
            if rgb.shape[0] != flow.shape[0]:
                size = max(rgb.shape[0], flow.shape[0])
                rgb = np.resize(rgb, (size, rgb.shape[1]))
                flow = np.resize(flow, (size, flow.shape[1]))
            feats = np.concatenate((rgb, flow), axis=1)
        else:
            feats = np.load(os.path.join(self.feat_folder, self.file_prefix, split, stem + self.file_ext)).astype(np.float32)

        if self.audio_feat_folder is not None:
            audio = np.load(os.path.join(self.audio_feat_folder, split, stem + self.audio_file_ext)).astype(np.float32)
        else:
            audio = None

        if self.feat_stride > 0 and (not self.force_upsampling):
            feat_stride, num_frames = self.feat_stride, self.num_frames
            if self.downsample_rate > 1:
                feats = feats[::self.downsample_rate, :]
                feat_stride = self.feat_stride * self.downsample_rate
        elif self.feat_stride > 0 and self.force_upsampling:
            feat_stride = float((feats.shape[0] - 1) * self.feat_stride + self.num_frames) / self.max_seq_len
            num_frames = feat_stride
        else:
            seq_len = feats.shape[0]
            assert seq_len <= self.max_seq_len
            if self.force_upsampling:
                seq_len = self.max_seq_len
            feat_stride = item["duration"] * item["fps"] / seq_len
            num_frames = feat_stride
        feat_offset = 0.5 * num_frames / feat_stride

        feats = torch.from_numpy(np.ascontiguousarray(feats.transpose()))
        if (feats.shape[-1] != self.max_seq_len) and self.force_upsampling:
            feats = F.interpolate(feats.unsqueeze(0), size=self.max_seq_len, mode="linear", align_corners=False).squeeze(0)

        if audio is not None:
            if audio.ndim == 1:
                audio = audio[:, None]
            audio = torch.from_numpy(np.ascontiguousarray(audio.transpose()))
            audio = F.interpolate(
                audio.unsqueeze(0),
                size=feats.shape[1],
                mode="linear",
                align_corners=False
            ).squeeze(0)
            feats = torch.cat([feats, audio], dim=0)

        if item["segments"] is not None:
            segs = torch.from_numpy(item["segments"] * item["fps"] / feat_stride - feat_offset)
            labels = torch.from_numpy(item["labels"])
            if self.is_training:
                vid_len = feats.shape[1] + feat_offset
                keep_seg = []
                keep_lab = []
                for seg, lab in zip(segs, labels):
                    if seg[0] >= vid_len:
                        continue
                    ratio = (min(seg[1].item(), vid_len) - seg[0].item()) / (seg[1].item() - seg[0].item())
                    if ratio >= self.trunc_thresh:
                        keep_seg.append(seg.clamp(max=vid_len))
                        keep_lab.append(lab.view(1))
                if len(keep_seg) > 0:
                    segs = torch.stack(keep_seg, dim=0)
                    labels = torch.cat(keep_lab)
                else:
                    segs, labels = None, None
        else:
            segs, labels = None, None

        data = {
            "video_id": item["id"],
            "feats": feats,
            "segments": segs,
            "labels": labels,
            "av_labels": torch.from_numpy(item["av_labels"]),
            "fps": item["fps"],
            "duration": item["duration"],
            "feat_stride": feat_stride,
            "feat_num_frames": num_frames,
        }

        if self.is_training and (segs is not None):
            data = truncate_feats(data, self.max_seq_len, self.trunc_thresh, self.crop_ratio)
        return data
