# Analysis results

Layer-output and cycle comparisons for all six YOLOv8l variants using 10 images
per model on device. Each DLC is compared with its matching
modified ONNX, including embedded preprocessing.

See [the analysis and visualization commands](../README.md).

## Layer cycles

| Model | Sum of mean layer cycles | Reduction relative to FP16 unoptimized |
| --- | ---: | ---: |
| [fp16_unoptimized](fp16_unoptimized/output/analysis/yolov8l/layer_cycles.csv) | 49,065,750 | 0.00% |
| [fp16_optimized](fp16_optimized/output/analysis/yolov8l/layer_cycles.csv) | 39,266,086 | 19.97% |
| [int8_per_tensor](int8_per_tensor/output/analysis/yolov8l/layer_cycles.csv) | 28,380,625 | 42.16% |
| [int8_per_channel](int8_per_channel/output/analysis/yolov8l/layer_cycles.csv) | 28,490,120 | 41.93% |
| [int8_int16](int8_int16/output/analysis/yolov8l/layer_cycles.csv) | 76,798,787 | -56.52% |
| [int8_wrong_calibration](int8_wrong_calibration/output/analysis/yolov8l/layer_cycles.csv) | 28,996,096 | 40.90% |

FP16 optimization reduced reported cycles by 19.97%; INT8 per-channel used
27.44% fewer cycles than optimized FP16. The two calibrated INT8 runs have
similar cycle totals. W8A16 used 56.52% more cycles than unoptimized FP16
(the negative reduction above denotes an increase).

These are sums of per-layer mean DSP cycle counts for these profiling runs,
not end-to-end latency or FPS. Use the [benchmark results](../../benchmarks/output/RESULTS.md)
for throughput and latency. Bad calibration can change numerical outputs without
providing a corresponding signal in cycle counts.

**Why W8A16 reports more cycles but higher FPS than optimized FP16:** W8A16
has 76.80M summed layer cycles versus 39.27M, but benchmarks at 46.53 versus
39.91 FPS. Integer quantization can add rescaling, rounding, and saturation;
SiLU activations and different kernel/fusion choices may also cost more than
FP16. Both formats use 16-bit activations, so activation size alone does not
explain the difference. Summed `snpe-net-run` layer cycles are a different
measurement from DepthAI throughput with two inference threads; scheduling,
overlap, clocks, and profiling attribution may affect the comparison. Use 
benchmark FPS and latency to compare deployment performance.

## Input preprocessing

| Model | Split cycles | Concat cycles | Share of total cycles |
| --- | ---: | ---: | ---: |
| fp16_unoptimized | 4,135,313 | 2,815,016 | 14.17% |
| fp16_optimized | 0 | 0 | 0.00% |
| int8_per_tensor | 0 | 0 | 0.00% |
| int8_per_channel | 0 | 0 | 0.00% |
| int8_int16 | 0 | 0 | 0.00% |
| int8_wrong_calibration | 0 | 0 | 0.00% |

The initial `split_images` and `concat_images` operations are absent as separately
named operations in the optimized models; zero here does not mean all
preprocessing is free.

## Final output tensor differences

Each cell lists the analyzer's values for `output1_yolov6r2`,
`output2_yolov6r2`, and `output3_yolov6r2`, respectively. These are the tensor names
in the converted YOLOv8l graph. Each value is averaged over the 10 images;
the three heads are reported separately rather than pooled across tensor sizes.

| Model | MSE (outputs 1 / 2 / 3) | Cosine similarity (outputs 1 / 2 / 3) |
| --- | --- | --- |
| fp16_unoptimized | 0.000005 / 0.000005 / 0.000002 | 0.999996 / 0.999998 / 1.000000 |
| fp16_optimized | 0.000005 / 0.000004 / 0.000003 | 0.999996 / 0.999998 / 1.000000 |
| int8_per_tensor | 0.023251 / 0.020552 / 0.010779 | 0.979922 / 0.990100 / 0.996439 |
| int8_per_channel | 0.020161 / 0.017451 / 0.010259 | 0.982371 / 0.991403 / 0.996473 |
| int8_int16 | 0.001835 / 0.001445 / 0.000538 | 0.998423 / 0.999266 / 0.999810 |
| int8_wrong_calibration | 0.015507 / 0.013991 / 0.009820 | 0.986824 / 0.993232 / 0.996741 |

W8A16 has lower final-output MSE and higher cosine similarity than both calibrated
INT8 variants across all three heads. On this 10-image analyzer input set, the
random-calibration variant also has lower final-output MSE than both calibrated
INT8 variants. This observation does not establish better detection accuracy or
validate random calibration; the input preprocessing and metric differ from AP
evaluation, and the runs span different tool versions.

**Why better MSE/cosine can coexist with zero mAP:** Whole-tensor similarity can
hide errors in the few class scores or box coordinates that determine detections;
cosine also ignores uniform positive scaling. Small aggregate errors can therefore
still cause confidence filtering, wrong classes, or failed IoU matches. 

Layer differences are diagnostics, not detection accuracy. The analyzer resizes
images directly rather than applying evaluation letterboxing; use the
[evaluation results](../../eval/output/RESULTS.md) for AP.

## Interactive visualizations

| Model | Matched tensors | Layer-output differences | Layer cycles |
| --- | ---: | --- | --- |
| fp16_unoptimized | 369 | [Open HTML](fp16_unoptimized/output/analysis/yolov8l/layer_outputs_visual.html) | [Open HTML](fp16_unoptimized/output/analysis/yolov8l/layer_cycles_visual.html) |
| fp16_optimized | 367 | [Open HTML](fp16_optimized/output/analysis/yolov8l/layer_outputs_visual.html) | [Open HTML](fp16_optimized/output/analysis/yolov8l/layer_cycles_visual.html) |
| int8_per_tensor | 367 | [Open HTML](int8_per_tensor/output/analysis/yolov8l/layer_outputs_visual.html) | [Open HTML](int8_per_tensor/output/analysis/yolov8l/layer_cycles_visual.html) |
| int8_per_channel | 367 | [Open HTML](int8_per_channel/output/analysis/yolov8l/layer_outputs_visual.html) | [Open HTML](int8_per_channel/output/analysis/yolov8l/layer_cycles_visual.html) |
| int8_int16 | 367 | [Open HTML](int8_int16/output/analysis/yolov8l/layer_outputs_visual.html) | [Open HTML](int8_int16/output/analysis/yolov8l/layer_cycles_visual.html) |
| int8_wrong_calibration | 367 | [Open HTML](int8_wrong_calibration/output/analysis/yolov8l/layer_outputs_visual.html) | [Open HTML](int8_wrong_calibration/output/analysis/yolov8l/layer_cycles_visual.html) |

Open the HTML files in a browser and use the metric dropdowns to explore the
layers. Internet access is required to load Plotly. Undefined cosine similarities
appear as gaps. Only tensors matched by the analyzer are compared.

## Source artifacts

- **fp16_unoptimized**: [layer cycles CSV](fp16_unoptimized/output/analysis/yolov8l/layer_cycles.csv) · [layer comparisons CSV](fp16_unoptimized/output/analysis/yolov8l/layer_comparison.csv) · [console log](fp16_unoptimized/analyze.log)
- **fp16_optimized**: [layer cycles CSV](fp16_optimized/output/analysis/yolov8l/layer_cycles.csv) · [layer comparisons CSV](fp16_optimized/output/analysis/yolov8l/layer_comparison.csv) · [console log](fp16_optimized/analyze.log)
- **int8_per_tensor**: [layer cycles CSV](int8_per_tensor/output/analysis/yolov8l/layer_cycles.csv) · [layer comparisons CSV](int8_per_tensor/output/analysis/yolov8l/layer_comparison.csv) · [console log](int8_per_tensor/analyze.log)
- **int8_per_channel**: [layer cycles CSV](int8_per_channel/output/analysis/yolov8l/layer_cycles.csv) · [layer comparisons CSV](int8_per_channel/output/analysis/yolov8l/layer_comparison.csv) · [console log](int8_per_channel/analyze.log)
- **int8_int16**: [layer cycles CSV](int8_int16/output/analysis/yolov8l/layer_cycles.csv) · [layer comparisons CSV](int8_int16/output/analysis/yolov8l/layer_comparison.csv) · [console log](int8_int16/analyze.log)
- **int8_wrong_calibration**: [layer cycles CSV](int8_wrong_calibration/output/analysis/yolov8l/layer_cycles.csv) · [layer comparisons CSV](int8_wrong_calibration/output/analysis/yolov8l/layer_comparison.csv) · [console log](int8_wrong_calibration/analyze.log)
