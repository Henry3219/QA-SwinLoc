# Cross-Dataset Result

This file records the bidirectional cross-dataset tests between `LavDF` and `AV-Deepfake1M`.

## LavDF -> AV1M

### Setting

- source train set: `LavDF`
- eval target: `AV-Deepfake1M test`
- ckpt: `paper_results/lavdf_q50d50_q50d50/last.pth.tar`
- LavDF post setting: `q50d50_post_a`
- output: `paper_results/av1m_test/prediction.json`

### Metric

- AP@0.50: `0.026636`
- AP@0.75: `0.005450`
- AP@0.90: `0.000361`
- AP@0.95: `0.000022`
- AR@50: `0.239387`
- AR@30: `0.218563`
- AR@20: `0.197939`
- AR@10: `0.150417`
- AR@5: `0.107203`
- score: `0.095409`

### Raw

```python
{
    'ap': {
        0.5: 0.026635853573679924,
        0.75: 0.005450127646327019,
        0.9: 0.00036068627377972007,
        0.95: 2.2143856767797843e-05
    },
    'ar': {
        50: 0.23938651382923126,
        30: 0.21856312453746796,
        20: 0.19793854653835297,
        10: 0.15041735768318176,
        5: 0.10720276832580566
    }
}
{
    'score': 0.09540943251022327
}
```

### Note

- this is a cross-dataset test result
- the model is trained on `LavDF` and tested on `AV-Deepfake1M`
- `prediction.json` has been aligned to official format
- the missing broken test video `256754.mp4` is filled with `[0.0, 0.0, 0.0]`

---

## AV1M -> LavDF

### Setting

- source train set: `AV-Deepfake1M`
- eval target: `LavDF test`
- eval config: `/output/UMMAFormer_exp07/paper_results/lavdf_xav1m/config.yaml`
- ckpt: `paper_results/av1m_q50d50_av1m_q50d50/last.pth.tar`
- log: `/output/UMMAFormer_exp07/paper_results/lavdf_xav1m/eval.log`
- result: `/output/UMMAFormer_exp07/paper_results/lavdf_xav1m/test_results.json`

### Metric

- Average-mAP: `0.179586`
- mAP@0.50: `29.790`
- mAP@0.55: `28.610`
- mAP@0.60: `27.337`
- mAP@0.65: `25.562`
- mAP@0.70: `23.011`
- mAP@0.75: `19.279`
- mAP@0.80: `14.501`
- mAP@0.85: `8.624`
- mAP@0.90: `2.808`
- mAP@0.95: `0.064`
- AUC(AR vs AN): `54.814844%`

### Raw

```text
Average-mAP: 0.17958606045884018
Detection: average-mAP 17.959 mAP@0.50 29.790 mAP@0.55 28.610 mAP@0.60 27.337 mAP@0.65 25.562 mAP@0.70 23.011 mAP@0.75 19.279 mAP@0.80 14.501 mAP@0.85 8.624 mAP@0.90 2.808 mAP@0.95 0.064
Area Under the AR vs AN curve: 54.814844464775845%
```

### Note

- this is a cross-dataset test result
- the model is trained on `AV-Deepfake1M` and tested on `LavDF`
- the evaluation uses the `LavDF` evaluation pipeline and `lavdf_q50d50`-style config
- the prediction file contains `2610000` proposals for `26100` test videos
