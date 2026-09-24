# Analysis results

Collected from the three existing YOLOv8l analysis runs using the same device,
10 visualization images per model, and ModelConverter 0.6.2 in the project's `env`.
Each converted DLC was compared with its corresponding modified ONNX model.

See [the analysis and visualization commands](../README.md).

## Layer cycles

| Model | Sum of mean layer cycles | Reduction relative to FP16 unoptimized |
| --- | ---: | ---: |
| [fp16_unoptimized](fp16_unoptimized/output/analysis/yolov8l/layer_cycles.csv) | 49,065,750 | 0.00% |
| [fp16_optimized](fp16_optimized/output/analysis/yolov8l/layer_cycles.csv) | 39,266,086 | 19.97% |
| [int8_per_channel](int8_per_channel/output/analysis/yolov8l/layer_cycles.csv) | 28,490,120 | 41.93% |

FP16 optimization reduced reported layer cycles by 19.97%. INT8 per-channel used 27.44% fewer cycles than optimized FP16.

These are sums of per-layer mean DSP cycle counts for these profiling runs,
not end-to-end latency or FPS. Use the [benchmark results](../../benchmarks/output/RESULTS.md)
for throughput and latency.

## Input preprocessing

| Model | Split cycles | Concat cycles | Share of total cycles |
| --- | ---: | ---: | ---: |
| fp16_unoptimized | 4,135,313 | 2,815,016 | 14.17% |
| fp16_optimized | 0 | 0 | 0.00% |
| int8_per_channel | 0 | 0 | 0.00% |

The initial `split_images` and `concat_images` operations account for 14.17% of
the unoptimized model's reported cycles. They are absent as separately named
operations in the optimized models; zero here does not mean all preprocessing is free.

## Interactive visualizations

| Model | Matched tensors | Layer-output differences | Layer cycles |
| --- | ---: | --- | --- |
| fp16_unoptimized | 369 | [Open HTML](fp16_unoptimized/output/analysis/yolov8l/layer_outputs_visual.html) | [Open HTML](fp16_unoptimized/output/analysis/yolov8l/layer_cycles_visual.html) |
| fp16_optimized | 367 | [Open HTML](fp16_optimized/output/analysis/yolov8l/layer_outputs_visual.html) | [Open HTML](fp16_optimized/output/analysis/yolov8l/layer_cycles_visual.html) |
| int8_per_channel | 367 | [Open HTML](int8_per_channel/output/analysis/yolov8l/layer_outputs_visual.html) | [Open HTML](int8_per_channel/output/analysis/yolov8l/layer_cycles_visual.html) |

Open the HTML files in a browser and use the metric dropdowns to explore the
layers. Internet access is required to load Plotly. Undefined cosine similarities
appear as gaps. Only tensors matched by the analyzer are compared.

The analyzer resizes images directly rather than applying evaluation letterboxing.
Layer differences are diagnostics, not detection accuracy; use the evaluation
results for AP.

## Source artifacts

- **fp16_unoptimized**: [layer cycles CSV](fp16_unoptimized/output/analysis/yolov8l/layer_cycles.csv) · [layer comparisons CSV](fp16_unoptimized/output/analysis/yolov8l/layer_comparison.csv) · [console log](fp16_unoptimized/analyze.log)
- **fp16_optimized**: [layer cycles CSV](fp16_optimized/output/analysis/yolov8l/layer_cycles.csv) · [layer comparisons CSV](fp16_optimized/output/analysis/yolov8l/layer_comparison.csv) · [console log](fp16_optimized/analyze.log)
- **int8_per_channel**: [layer cycles CSV](int8_per_channel/output/analysis/yolov8l/layer_cycles.csv) · [layer comparisons CSV](int8_per_channel/output/analysis/yolov8l/layer_comparison.csv) · [console log](int8_per_channel/analyze.log)
