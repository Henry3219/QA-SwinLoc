# UMMAFormer Exp07

## Scope

This repo is the working project for temporal forgery localization on:

- `LavDF`
- `AV-Deepfake1M`

The current thesis line uses:

- `swin`
- `fpn`
- `qual`
- `DFL`

The current best `LavDF` result is:

- run: [q50d50_post_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_a/test_results.txt)
- average-mAP: `89.128`

## Main File

- [paper_use.md](/input0/Backup/model/UMMAFormer_exp07/paper_use.md)
  Main thesis record. This is the most important experiment summary file in the repo.

- [README.md](/input0/Backup/model/UMMAFormer_exp07/README.md)
  Project index. Use this file to locate code, configs, data, and result records.

- [UMMAFormer.md](/input0/Backup/model/UMMAFormer_exp07/UMMAFormer.md)
  Original project / paper note from the upstream codebase.

- [ablation.md](/input0/Backup/model/UMMAFormer_exp07/ablation.md)
  Early ablation note for `con` and `refine`. This is now historical only and is not part of the final thesis line.

## Data

### Feature Root

- [data](/input0/Backup/model/UMMAFormer_exp07/data)
  Repo-side data index and AV1M metadata.

- `/input0/Backup/features/LAV-DF-UMM`
  LavDF extracted features.

- `/input0/Backup/features/AV-Deepfake1M-UMM`
  AV-Deepfake1M extracted features.

### Raw Dataset

- `/input0/LAV-DF`
  Raw `LavDF` dataset.

- `/input0/AV-Deepfake1M`
  Raw `AV-Deepfake1M` dataset.

### Paper / Ref

- [ref](/input0/Backup/model/UMMAFormer_exp07/ref)
  Dataset papers and related method papers.

## Code

### Train / Eval

- [train.py](/input0/Backup/model/UMMAFormer_exp07/train.py)
  Main training entry.

- [eval.py](/input0/Backup/model/UMMAFormer_exp07/eval.py)
  Main `LavDF` evaluation entry.

- [infer_av1m.py](/input0/Backup/model/UMMAFormer_exp07/infer_av1m.py)
  `AV-Deepfake1M` inference entry. It outputs official-style `prediction.json`.

### Dataset

- [lavdfv2.py](/input0/Backup/model/UMMAFormer_exp07/libs/datasets/lavdfv2.py)
  Main `LavDF` dataset loader.

- [av1m.py](/input0/Backup/model/UMMAFormer_exp07/libs/datasets/av1m.py)
  `AV-Deepfake1M` dataset loader.

### Model

- [av_recoverynonorm_meta_arch.py](/input0/Backup/model/UMMAFormer_exp07/libs/modeling/av_recoverynonorm_meta_arch.py)
  Core model. This file contains the current thesis model path, including `qual` and `DFL`.

- [backbones.py](/input0/Backup/model/UMMAFormer_exp07/libs/modeling/backbones.py)
  Backbone implementations, including the current `swin` backbone.

- [necks.py](/input0/Backup/model/UMMAFormer_exp07/libs/modeling/necks.py)
  `fpn` implementation.

- [losses.py](/input0/Backup/model/UMMAFormer_exp07/libs/modeling/losses.py)
  Localization losses and `DFL`-related loss logic.

## Config

### LavDF Main

- [lavdf_q50d50.yaml](/input0/Backup/model/UMMAFormer_exp07/configs/UMMAFormer/lavdf_q50d50.yaml)
  Current best training config line for `LavDF`.

- [lavdf_q50d50_id.yaml](/input0/Backup/model/UMMAFormer_exp07/configs/UMMAFormer/lavdf_q50d50_id.yaml)
  `identity` neck config for `fpn` ablation.

### AV1M Main

- [av1m_q50d50.yaml](/input0/Backup/model/UMMAFormer_exp07/configs/UMMAFormer/av1m_q50d50.yaml)
  Main config for `AV-Deepfake1M`.

- [av1m_q50d50_tiny.yaml](/input0/Backup/model/UMMAFormer_exp07/configs/UMMAFormer/av1m_q50d50_tiny.yaml)
  Tiny smoke-test config.

## Tool

### Post

- [nms_eval.sh](/input0/Backup/model/UMMAFormer_exp07/tools/nms_eval.sh)
  Main post-process eval script.

- [scan_q50d50.sh](/input0/Backup/model/UMMAFormer_exp07/tools/scan_q50d50.sh)
  Post-process scan script for the current best model line.

### AV1M Meta

- [build_av1m.py](/input0/Backup/model/UMMAFormer_exp07/tools/build_av1m.py)
  Build `AV-Deepfake1M` test metadata index.

- [build_sub.py](/input0/Backup/model/UMMAFormer_exp07/tools/build_sub.py)
  Build tiny subsets for quick testing.

- [conv_av1m.py](/input0/Backup/model/UMMAFormer_exp07/tools/conv_av1m.py)
  Convert old generic output into official-style `prediction.json`.

- [fix_pred.py](/input0/Backup/model/UMMAFormer_exp07/tools/fix_pred.py)
  Rebuild `prediction.json` from `sub.json` and patch missing items.

- [fill.py](/input0/Backup/model/UMMAFormer_exp07/tools/fill.py)
  Fill missing `AV-Deepfake1M` feature files for a small set of videos.

### AV1M Audio

- [byola_vid.py](/input0/Backup/model/UMMAFormer_exp07/tools/byola_vid.py)
  Temporal audio feature extraction for `AV-Deepfake1M`, aligned with `LavDF byola`.

- [aud_init.sh](/input0/Backup/model/UMMAFormer_exp07/tools/aud_init.sh)
  Init audio extraction queue.

- [aud_sched.py](/input0/Backup/model/UMMAFormer_exp07/tools/aud_sched.py)
  Queue status and recycle tool.

- [aud_work.sh](/input0/Backup/model/UMMAFormer_exp07/tools/aud_work.sh)
  Worker loop for audio extraction.

- [a800-aud.sh](/input0/Backup/model/UMMAFormer_exp07/tools/a800-aud.sh)
- [a40-aud.sh](/input0/Backup/model/UMMAFormer_exp07/tools/a40-aud.sh)
- [v100-aud.sh](/input0/Backup/model/UMMAFormer_exp07/tools/v100-aud.sh)
- [3090-aud.sh](/input0/Backup/model/UMMAFormer_exp07/tools/3090-aud.sh)
  Main multi-machine audio extraction launchers.

## Result

### LavDF Main

- [q50d50_post_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_a/test_results.txt)
  Current best final result on `LavDF`.

- [lavdf_q50d50_q50d50](/input0/Backup/model/UMMAFormer_exp07/paper_results/lavdf_q50d50_q50d50)
  Training run and checkpoint for the final thesis model.

### Cross-Dataset

- [av1m_result.md](/input0/Backup/model/UMMAFormer_exp07/av1m_result.md)
  Bidirectional cross-dataset result record:
  `LavDF -> AV-Deepfake1M` and `AV-Deepfake1M -> LavDF`.

- [prediction.json](/input0/Backup/model/UMMAFormer_exp07/paper_results/av1m_test/prediction.json)
  Official-style `AV-Deepfake1M` test submission file for `LavDF -> AV-Deepfake1M`.

- `/output/UMMAFormer_exp07/paper_results/lavdf_xav1m`
  `AV-Deepfake1M -> LavDF` cross-test output folder, including `config.yaml`, `eval.log`, and `test_results.json`.

## Record

- [paper_use.md](/input0/Backup/model/UMMAFormer_exp07/paper_use.md)
  Final thesis experiment record. This is the main file to maintain.

- [av1m_result.md](/input0/Backup/model/UMMAFormer_exp07/av1m_result.md)
  Cross-dataset result snapshot for both directions.

- [av1m_use.md](/input0/Backup/model/UMMAFormer_exp07/av1m_use.md)
  AV1M usage note. This file overlaps with `README.md` and `av1m_result.md`.

## Suggest

The cleanest document structure is:

1. keep [paper_use.md](/input0/Backup/model/UMMAFormer_exp07/paper_use.md) as the only thesis experiment record
2. keep [README.md](/input0/Backup/model/UMMAFormer_exp07/README.md) as the project index
3. keep [av1m_result.md](/input0/Backup/model/UMMAFormer_exp07/av1m_result.md) as a small bidirectional cross-dataset result note
4. merge the useful parts of [av1m_use.md](/input0/Backup/model/UMMAFormer_exp07/av1m_use.md) into `README.md`, then stop expanding `av1m_use.md`

In other words:

- `paper_use.md`: paper record
- `README.md`: project map
- `av1m_result.md`: bidirectional cross-dataset result note
- `av1m_use.md`: optional historical note, not the main entry anymore
