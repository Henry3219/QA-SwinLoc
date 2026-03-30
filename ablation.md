# Ablation

## Scope
- Dataset: LavDF full
- Main repos/runs reviewed: `UMMAFormer_exp05/06/07/08`
- Key config base: `/output/UMMAFormer_exp07/configs/UMMAFormer/lavdf_tsn_audio.yaml`

## Best So Far
- Best run: `/input0/Backup/model/UMMAFormer_exp08/paper_results/lavdf_tsn_audio_2026_03_05_06_32_07`
- Metrics:
  - average-mAP: `88.385`
  - mAP@0.50: `98.582`
  - mAP@0.75: `95.178`
  - mAP@0.90: `75.842`
  - mAP@0.95: `43.317`
- Effective setting (core):
  - backbone: `convHRLRSwin`
  - audio: `byola`
  - input_dim/audio_dim: `4096/2048`
  - `refine_on=False`
  - `con_on=False`
  - `tfaa_on=False`, `pca_on=False`

## Backbone Ablation
- `convHRLRSwin` is clearly stronger than `convHRLRFullResSelfAttTransformerRevised`.
- Mean average-mAP (full runs reviewed):
  - `convHRLRSwin`: `88.239` (n=6)
  - old backbone: `85.664` (n=14)
- Controlled comparisons show about `+0.55 ~ +0.67` mAP gain for Swin backbone.

## Audio Feature Ablation
- `byola` > `wav2vec` on full setting.
- Mean average-mAP:
  - byola: `86.864` (n=13), best `88.385`
  - wav2vec: `85.707` (n=3), best `86.906`

## Feature Dim Ablation
- `input_dim=4096` is much better than `2048`.
- Mean average-mAP:
  - `4096`: `87.168` (n=17), best `88.385`
  - `2048`: `82.293` (n=3), best `83.329`

## Refine / Con Ablation
- Current best is with both OFF.
- Key runs:
  - refine+con ON: `/input0/Backup/model/UMMAFormer_exp07/paper_results/lavdf_tsn_audio_2026_03_03_06_10_35` -> `88.249`
  - refine OFF, con ON: `/input0/Backup/model/UMMAFormer_exp08/paper_results/lavdf_tsn_audio_2026_03_03_06_28_46` -> `88.207`
  - refine OFF, con OFF: `/input0/Backup/model/UMMAFormer_exp08/paper_results/lavdf_tsn_audio_2026_03_05_06_32_07` -> `88.385` (best)
  - refine ON, con OFF: `/input0/Backup/model/UMMAFormer_exp07/paper_results/lavdf_tsn_audio_2026_03_02_10_39_20` -> `88.183`
- Observed interaction:
  - With refine OFF, turning con OFF improved results.
  - With refine ON, con gain is very small and unstable.

## Data Alignment Note (lavdfv2)
- `lavdfv2.py` length line was tested both ways.
- Exp07 currently reverted to original public-code style:
  - `/input0/Backup/model/UMMAFormer_exp07/libs/datasets/lavdfv2.py`
  - line uses `feature_length=max(feats1.shape[0],feats1.shape[0])`
- Related run comparison in exp07:
  - `2026_03_03_06_10_35`: `88.249`
  - `2026_03_05_10_31_18`: `88.086`

## Postprocess Ablation (Experiment 1/2)
- Eval entry unified via `eval.py` on `test_split=['test']`.
- Runs: `/output/UMMAFormer_exp07/paper_results/nms_c1 ... nms_c8`
- Summary:
  - `c1`: `88.386` (baseline)
  - `c2`: `88.386`
  - `c3`: `88.386`
  - `c4`: `51.996`
  - `c5`: `52.001`
  - `c6`: `49.792`
  - `c7`: `28.970`
  - `c8`: `71.827`
- Conclusion:
  - Export topk change (`100/200/-1`) had near-zero effect.
  - Current adaptive NMS variant severely hurts performance.
  - Keep baseline postprocess: `adapt_nms=False`.

## Current Practical Baseline to Continue
- Backbone: `convHRLRSwin`
- Audio: `byola`
- Dim: `4096 + 2048`
- `refine_on=False`, `con_on=False`
- Postprocess: baseline (`adapt_nms=False`, soft-nms default params)
- Evaluate on test via `eval.py`.

## Handoff Pointers
- Main summary file: this file.
- Batch eval script: `/output/UMMAFormer_exp07/tools/nms_eval.sh`
- Primary config: `/output/UMMAFormer_exp07/configs/UMMAFormer/lavdf_tsn_audio.yaml`
