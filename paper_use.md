# Paper Use

## Scope
- Dataset: `LavDF full`
- Repo: `UMMAFormer_exp07`
- Main modules:
  - `backbone`
  - `fpn`
  - `qual`
  - `DFL`
- Fixed post for fair comparison:
  - `min_score=0.001`
  - `nms_sigma=0.50`
  - `pre_nms_topk=1000`

## Main

### Final
- Name: `base + fpn + qual(0.5) + DFL`
- Run: [q50d50_post_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_a/test_results.txt)
- average-mAP: `89.128`
- mAP@0.50 / 0.75 / 0.95: `98.923 / 95.809 / 45.773`
- AR@10 / 20 / 50 / 100: `92.639 / 92.862 / 92.927 / 93.000`
- Use: final result in thesis main table

## Ablation
- All rows use the same fixed post `A`
- This is the cleanest table for reviewer-facing comparison

### base + fpn
- Run: [base_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/base_a/test_results.txt)
- average-mAP: `88.637`
- mAP@0.50 / 0.75 / 0.95: `98.973 / 95.579 / 43.163`
- AR@10 / 20 / 50 / 100: `92.379 / 92.667 / 92.739 / 92.814`

### base + fpn + qual(0.5)
- Run: [q50_post_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50_post/q50_post_a/test_results.txt)
- average-mAP: `88.871`
- mAP@0.50 / 0.75 / 0.95: `98.906 / 95.636 / 45.175`
- AR@10 / 20 / 50 / 100: `92.393 / 92.681 / 92.736 / 92.843`

### base + fpn + qual(0.5) + DFL
- Run: [q50d50_post_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_a/test_results.txt)
- average-mAP: `89.128`
- mAP@0.50 / 0.75 / 0.95: `98.923 / 95.809 / 45.773`
- AR@10 / 20 / 50 / 100: `92.639 / 92.862 / 92.927 / 93.000`

### base + identity + qual(0.5) + DFL
- Run: [lavdf_q50d50_id_q50d50_id](/input0/Backup/model/UMMAFormer_exp07/paper_results/lavdf_q50d50_id_q50d50_id/test_results.txt)
- average-mAP: `87.855`
- mAP@0.50 / 0.75 / 0.95: `98.207 / 94.579 / 43.624`
- AR@10 / 20 / 50 / 100: `92.123 / 92.489 / 92.579 / 92.673`
- Use: FPN ablation row

## Qual
- Goal:
  - test the effect of `qual`
  - choose the best `qual_w`
- Suggested table:
  - use the same fixed post `A`

### w = 0
- Name: `base + fpn`
- Run: [base_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/base_a/test_results.txt)
- average-mAP: `88.637`
- mAP@0.50 / 0.75 / 0.95: `98.973 / 95.579 / 43.163`
- AR@10 / 20 / 50 / 100: `92.379 / 92.667 / 92.739 / 92.814`

### w = 0.25
- Name: `base + fpn + qual(0.25)`
- Run: [q25_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q25_a/test_results.txt)
- average-mAP: `88.818`
- mAP@0.50 / 0.75 / 0.95: `98.894 / 95.470 / 45.199`
- AR@10 / 20 / 50 / 100: `92.245 / 92.581 / 92.636 / 92.704`

### w = 0.50
- Name: `base + fpn + qual(0.5)`
- Run: [q50_post_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50_post/q50_post_a/test_results.txt)
- average-mAP: `88.871`
- mAP@0.50 / 0.75 / 0.95: `98.906 / 95.636 / 45.175`
- AR@10 / 20 / 50 / 100: `92.393 / 92.681 / 92.736 / 92.843`

### w = 1.00
- Name: `base + fpn + qual(1.0)`
- Run: [qual_post_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/qual_post/qual_post_a/test_results.txt)
- average-mAP: `88.767`
- mAP@0.50 / 0.75 / 0.95: `98.886 / 95.477 / 44.721`
- AR@10 / 20 / 50 / 100: `92.261 / 92.548 / 92.590 / 92.686`

## DFL
- Goal:
  - test the effect of `DFL`
  - choose the best `dfl_w`
- Suggested table:
  - keep `qual(0.5)` fixed
  - use the same fixed post `A`

### w = 0
- Name: `base + fpn + qual(0.5)`
- Run: [q50_post_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50_post/q50_post_a/test_results.txt)
- average-mAP: `88.871`
- mAP@0.50 / 0.75 / 0.95: `98.906 / 95.636 / 45.175`
- AR@10 / 20 / 50 / 100: `92.393 / 92.681 / 92.736 / 92.843`

### w = 0.25
- Name: `base + fpn + qual(0.5) + DFL(0.25)`
- Run: [q50d25_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d25_a/test_results.txt)
- average-mAP: `89.071`
- mAP@0.50 / 0.75 / 0.95: `98.928 / 95.787 / 45.648`
- AR@10 / 20 / 50 / 100: `92.573 / 92.831 / 92.871 / 92.932`

### w = 0.50
- Name: `base + fpn + qual(0.5) + DFL(0.5)`
- Run: [q50d50_post_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_a/test_results.txt)
- average-mAP: `89.128`
- mAP@0.50 / 0.75 / 0.95: `98.923 / 95.809 / 45.773`
- AR@10 / 20 / 50 / 100: `92.639 / 92.862 / 92.927 / 93.000`

### w = 1.00
- Name: `base + fpn + qual(0.5) + DFL(1.0)`
- Run: [lavdf_q50d100_q50d100](/input0/Backup/model/UMMAFormer_exp07/paper_results/lavdf_q50d100_q50d100/test_results.txt)
- average-mAP: `88.954`
- mAP@0.50 / 0.75 / 0.95: `98.842 / 95.622 / 44.987`
- AR@10 / 20 / 50 / 100: `92.579 / 92.859 / 92.914 / 92.978`

## Window Length
- Goal:
  - test the effect of `n_mha_win_size`
  - choose whether to keep the default window length setting
- Suggested table:
  - keep `base + fpn + qual(0.5) + DFL(0.5)` fixed
  - use the same fixed post `A`
- Note:
  - `lavdf_w7x6_post` is the default `lavdf_q50d50` result
  - actual default window size used by `convHRLRSwin` is `[7, 7, 7, 7, 7, 7]`
  - completed test-set results show the default setting is much better than the shorter / mixed-window settings

| Run | actual window size | Status | average-mAP | mAP@0.50 | mAP@0.75 | mAP@0.95 | AR@10 | AR@20 | AR@50 | AR@100 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `lavdf_w7x6_post` | `[7, 7, 7, 7, 7, 7]` | done | `89.128` | `98.923` | `95.809` | `45.773` | `92.639` | `92.862` | `92.927` | `93.000` |
| `lavdf_w3x6_post` | `[3, 3, 3, 3, 3, 3]` | done | `72.744` | `94.639` | `83.108` | `7.587` | `81.955` | `83.269` | `84.184` | `84.383` |
| `lavdf_w33_777_19_post` | `[3, 3, 7, 7, 7, 19]` | done | `79.031` | `96.896` | `89.612` | `14.680` | `86.366` | `87.248` | `87.665` | `87.785` |
| `lavdf_q50d50_w33_777_19_hp` | `[3, 3, 7, 7, 7, 19]` | running | `-` | `-` | `-` | `-` | `-` | `-` | `-` | `-` |
| `lavdf_q50d50_w7x5_19_hp` | `[7, 7, 7, 7, 7, 19]` | running | `-` | `-` | `-` | `-` | `-` | `-` | `-` | `-` |

### default window
- Name: `base + fpn + qual(0.5) + DFL(0.5), default window`
- Run: [lavdf_w7x6_post / q50d50_post_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_a/test_results.txt)
- Actual window size: `[7, 7, 7, 7, 7, 7]`
- average-mAP: `89.128`
- mAP@0.50 / 0.75 / 0.95: `98.923 / 95.809 / 45.773`
- AR@10 / 20 / 50 / 100: `92.639 / 92.862 / 92.927 / 93.000`
- Use: best completed window-length result

### w3x6
- Name: `base + fpn + qual(0.5) + DFL(0.5), short window`
- Run: [lavdf_w3x6_post_a](/output/UMMAFormer_exp07/paper_results/lavdf_w3x6_post/lavdf_w3x6_post_a/test_results.txt)
- Config: `n_mha_win_size = [3, 3, 3, 3, 3, 3]`
- average-mAP: `72.744`
- mAP@0.50 / 0.75 / 0.95: `94.639 / 83.108 / 7.587`
- AR@10 / 20 / 50 / 100: `81.955 / 83.269 / 84.184 / 84.383`
- Delta vs default average-mAP: `-16.384`

### w33_777_19
- Name: `base + fpn + qual(0.5) + DFL(0.5), mixed window`
- Run: [lavdf_w33_777_19_post_a](/output/UMMAFormer_exp07/paper_results/lavdf_w33_777_19_post/lavdf_w33_777_19_post_a/test_results.txt)
- Config: `n_mha_win_size = [3, 3, 7, 7, 7, 19]`
- average-mAP: `79.031`
- mAP@0.50 / 0.75 / 0.95: `96.896 / 89.612 / 14.680`
- AR@10 / 20 / 50 / 100: `86.366 / 87.248 / 87.665 / 87.785`
- Delta vs default average-mAP: `-10.097`

### running
- `lavdf_q50d50_w33_777_19_hp`: still running according to current experiment note; local directory already has `val_results.txt`, and `lavdf_w33_777_19_post` has a completed test-set post result.
- `lavdf_q50d50_w7x5_19_hp`: still running; no completed test-set result found yet.

## Post
- Goal:
  - show post sensitivity on the final model
- Suggested table:
  - use the final model `base + fpn + qual(0.5) + DFL`
  - report all scanned settings in the thesis main text

### A
- Run: [q50d50_post_a](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_a/test_results.txt)
- Post: `0.001 / 0.50 / 1000`
- average-mAP: `89.128`
- mAP@0.50 / 0.75 / 0.95: `98.923 / 95.809 / 45.773`
- AR@10 / 20 / 50 / 100: `92.639 / 92.862 / 92.927 / 93.000`
- Use: best average-mAP

### B
- Run: [q50d50_post_b](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_b/test_results.txt)
- Post: `0.001 / 0.65 / 2000`
- average-mAP: `88.941`
- mAP@0.50 / 0.75 / 0.95: `98.640 / 95.538 / 45.846`
- AR@10 / 20 / 50 / 100: `92.979 / 93.345 / 93.427 / 93.543`

### C
- Run: [q50d50_post_c](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_c/test_results.txt)
- Post: `0.001 / 0.75 / 3000`
- average-mAP: `88.753`
- mAP@0.50 / 0.75 / 0.95: `98.374 / 95.267 / 45.935`
- AR@10 / 20 / 50 / 100: `93.140 / 93.616 / 93.732 / 93.804`
- Use: higher `mAP@0.95` and higher `AR`

### D
- Run: [q50d50_post_d](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_d/test_results.txt)
- Post: `0.002 / 0.50 / 2000`
- average-mAP: `89.126`
- mAP@0.50 / 0.75 / 0.95: `98.923 / 95.807 / 45.759`
- AR@10 / 20 / 50 / 100: `92.638 / 92.861 / 92.928 / 93.000`

### E
- Run: [q50d50_post_e](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_e/test_results.txt)
- Post: `0.002 / 0.65 / 3000`
- average-mAP: `88.940`
- mAP@0.50 / 0.75 / 0.95: `98.639 / 95.536 / 45.840`
- AR@10 / 20 / 50 / 100: `92.978 / 93.343 / 93.428 / 93.543`

### F
- Run: [q50d50_post_f](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_f/test_results.txt)
- Post: `0.003 / 0.50 / 2000`
- average-mAP: `89.126`
- mAP@0.50 / 0.75 / 0.95: `98.923 / 95.807 / 45.760`
- AR@10 / 20 / 50 / 100: `92.638 / 92.861 / 92.928 / 93.000`

### G
- Run: [q50d50_post_g](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_g/test_results.txt)
- Post: `0.003 / 0.65 / 2000`
- average-mAP: `88.940`
- mAP@0.50 / 0.75 / 0.95: `98.639 / 95.538 / 45.839`
- AR@10 / 20 / 50 / 100: `92.978 / 93.344 / 93.429 / 93.544`

### H
- Run: [q50d50_post_h](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_h/test_results.txt)
- Post: `0.003 / 0.75 / 2000`
- average-mAP: `88.751`
- mAP@0.50 / 0.75 / 0.95: `98.374 / 95.267 / 45.934`
- AR@10 / 20 / 50 / 100: `93.140 / 93.613 / 93.731 / 93.803`

### I
- Run: [q50d50_post_i](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_i/test_results.txt)
- Post: `0.005 / 0.65 / 1000`
- average-mAP: `88.938`
- mAP@0.50 / 0.75 / 0.95: `98.639 / 95.536 / 45.835`
- AR@10 / 20 / 50 / 100: `93.225 / 93.390 / 93.390 / 93.390`

### J
- Run: [q50d50_post_j](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_j/test_results.txt)
- Post: `0.005 / 0.75 / 2000`
- average-mAP: `88.750`
- mAP@0.50 / 0.75 / 0.95: `98.374 / 95.266 / 45.931`
- AR@10 / 20 / 50 / 100: `93.488 / 93.703 / 93.703 / 93.703`

### K
- Run: [q50d50_post_k](/input0/Backup/model/UMMAFormer_exp07/paper_results/q50d50_post/q50d50_post_k/test_results.txt)
- Post: `0.010 / 0.75 / 2000`
- average-mAP: `88.693`
- mAP@0.50 / 0.75 / 0.95: `98.367 / 95.226 / 45.813`
- AR@10 / 20 / 50 / 100: `93.175 / 93.175 / 93.175 / 93.175`

## Sanity
- Use:
  - show `export_topk` has near-zero effect
  - show adaptive NMS is not suitable here

### topk
- [nms_c1](/input0/Backup/model/UMMAFormer_exp07/paper_results/nms_c1/test_results.txt): `88.386`
- [nms_c2](/input0/Backup/model/UMMAFormer_exp07/paper_results/nms_c2/test_results.txt): `88.386`
- [nms_c3](/input0/Backup/model/UMMAFormer_exp07/paper_results/nms_c3/test_results.txt): `88.386`

### adapt
- [nms_c4](/input0/Backup/model/UMMAFormer_exp07/paper_results/nms_c4/test_results.txt): `87.607`

## AV1M
- Dataset: `AV-Deepfake1M test`
- Main config: `configs/UMMAFormer/av1m_q50d50.yaml`
- Main run: `paper_results/av1m_q50d50_av1m_q50d50`
- Note:
  - `prediction.json` is official-style output
  - broken test video `256754.mp4` is filled with `[0.0, 0.0, 0.0]`

### in-domain epoch 9
- Train -> Test: `AV1M -> AV1M`
- Output: [prediction.json](/input0/Backup/model/UMMAFormer_exp07/paper_results/av1m_e9/prediction.json)
- score: `0.717200`
- AP@0.50 / 0.75 / 0.90 / 0.95: `0.876241 / 0.784513 / 0.498817 / 0.229938`
- AR@5 / 10 / 20 / 30 / 50: `0.797499 / 0.825270 / 0.845765 / 0.854381 / 0.862201`

### in-domain epoch 15
- Train -> Test: `AV1M -> AV1M`
- Output: [prediction.json](/input0/Backup/model/UMMAFormer_exp07/paper_results/av1m_e15/prediction.json)
- score: `0.765007`
- AP@0.50 / 0.75 / 0.90 / 0.95: `0.943692 / 0.860486 / 0.559811 / 0.289744`
- AR@5 / 10 / 20 / 30 / 50: `0.847545 / 0.862630 / 0.871287 / 0.874425 / 0.877015`
- Use: current best AV1M in-domain result

### cross-dataset LavDF -> AV1M
- Train -> Test: `LavDF -> AV1M`
- Ckpt: `paper_results/lavdf_q50d50_q50d50/last.pth.tar`
- Output: [prediction.json](/input0/Backup/model/UMMAFormer_exp07/paper_results/av1m_test/prediction.json)
- score: `0.095409`
- AP@0.50 / 0.75 / 0.90 / 0.95: `0.026636 / 0.005450 / 0.000361 / 0.000022`
- AR@5 / 10 / 20 / 30 / 50: `0.107203 / 0.150417 / 0.197939 / 0.218563 / 0.239387`
- Use: cross-dataset generalization from `LavDF` to `AV1M`

### cross-dataset AV1M -> LavDF
- Train -> Test: `AV1M -> LavDF`
- Eval config: `/output/UMMAFormer_exp07/paper_results/lavdf_xav1m/config.yaml`
- Ckpt: `paper_results/av1m_q50d50_av1m_q50d50/last.pth.tar`
- Log: `/output/UMMAFormer_exp07/paper_results/lavdf_xav1m/eval.log`
- Result: `/output/UMMAFormer_exp07/paper_results/lavdf_xav1m/test_results.json`
- Average-mAP: `0.179586`
- mAP@0.50 / 0.75 / 0.90 / 0.95: `29.790 / 19.279 / 2.808 / 0.064`
- AUC(AR vs AN): `54.814844%`
- Use: cross-dataset generalization from `AV1M` to `LavDF`

### summary
- `epoch 15` is better than `epoch 9` on all reported AP / AR metrics
- `AV1M -> AV1M` remains far stronger than `LavDF -> AV1M`
- `AV1M -> LavDF` reaches `17.959` detection average-mAP, still much lower than the in-domain `LavDF` result `89.128`

## Need
- `-`
