# Evaluation results

Collected from the seven full YOLOv8l evaluations on the 300-image test split of
`coco-validation-all-classes`, using `workskop_material/env`. Visualization runs
are excluded. All runs use confidence threshold 0.001, NMS IoU threshold 0.7,
and a maximum of 300 detections per image.

The ONNX baseline runs on the CPU; converted models run on the RVC4 device.
See [the evaluation commands](../README.md) and [all results in JSON](RESULTS.json).
JSON preserves the original metric values as fractions; tables show percentages.

## Average precision

AP averages IoU thresholds from 0.50 to 0.95. AP50 and AP75 use fixed IoU
thresholds. The change from baseline is measured in percentage points (pp).

| Model | AP (%) | AP50 (%) | AP75 (%) | AP change from baseline (pp) |
| --- | ---: | ---: | ---: | ---: |
| [baseline_onnx](baseline_onnx/result.json) | 59.47 | 74.03 | 64.96 | +0.00 |
| [fp16_unoptimized](fp16_unoptimized/result.json) | 59.43 | 73.83 | 64.98 | -0.04 |
| [fp16_optimized](fp16_optimized/result.json) | 59.45 | 73.83 | 64.98 | -0.02 |
| [int8_per_tensor](int8_per_tensor/result.json) | 56.19 | 70.51 | 61.09 | -3.28 |
| [int8_per_channel](int8_per_channel/result.json) | 56.84 | 71.53 | 62.22 | -2.63 |
| [int8_int16](int8_int16/result.json) | 58.92 | 73.61 | 64.09 | -0.55 |
| [int8_wrong_calibration](int8_wrong_calibration/result.json) | 0.00 | 0.00 | 0.00 | -59.47 |

## Average precision by object size

| Model | AP_small (%) | AP_medium (%) | AP_large (%) |
| --- | ---: | ---: | ---: |
| baseline_onnx | 36.40 | 56.48 | 73.91 |
| fp16_unoptimized | 36.25 | 56.35 | 73.65 |
| fp16_optimized | 36.23 | 56.43 | 73.65 |
| int8_per_tensor | 34.90 | 51.25 | 72.00 |
| int8_per_channel | 34.78 | 52.72 | 71.80 |
| int8_int16 | 35.52 | 55.92 | 74.15 |
| int8_wrong_calibration | 0.00 | 0.00 | 0.00 |

## Average recall

| Model | AR1 (%) | AR10 (%) | AR100 (%) |
| --- | ---: | ---: | ---: |
| baseline_onnx | 46.01 | 67.63 | 72.14 |
| fp16_unoptimized | 46.05 | 67.03 | 71.06 |
| fp16_optimized | 46.05 | 67.06 | 71.09 |
| int8_per_tensor | 43.27 | 63.75 | 66.49 |
| int8_per_channel | 44.64 | 64.18 | 66.84 |
| int8_int16 | 46.03 | 67.26 | 71.65 |
| int8_wrong_calibration | 0.00 | 0.00 | 0.00 |

## Average recall by object size

| Model | AR_small (%) | AR_medium (%) | AR_large (%) |
| --- | ---: | ---: | ---: |
| baseline_onnx | 49.06 | 70.46 | 83.72 |
| fp16_unoptimized | 48.30 | 69.31 | 81.94 |
| fp16_optimized | 48.28 | 69.41 | 81.94 |
| int8_per_tensor | 43.75 | 61.75 | 79.90 |
| int8_per_channel | 44.23 | 63.06 | 78.95 |
| int8_int16 | 48.40 | 70.23 | 83.44 |
| int8_wrong_calibration | 0.00 | 0.00 | 0.00 |

AR1, AR10, and AR100 use at most 1, 10, and 100 detections per image respectively.

## Source results

- **baseline_onnx**: [result JSON](baseline_onnx/result.json) · [console log](baseline_onnx/result.log)
- **fp16_unoptimized**: [result JSON](fp16_unoptimized/result.json) · [console log](fp16_unoptimized/result.log)
- **fp16_optimized**: [result JSON](fp16_optimized/result.json) · [console log](fp16_optimized/result.log)
- **int8_per_tensor**: [result JSON](int8_per_tensor/result.json) · [console log](int8_per_tensor/result.log)
- **int8_per_channel**: [result JSON](int8_per_channel/result.json) · [console log](int8_per_channel/result.log)
- **int8_int16**: [result JSON](int8_int16/result.json) · [console log](int8_int16/result.log)
- **int8_wrong_calibration**: [result JSON](int8_wrong_calibration/result.json) · [console log](int8_wrong_calibration/result.log)
