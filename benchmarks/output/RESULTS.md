# Benchmark results

Collected from the six existing YOLOv8l benchmark CSVs.
All results use same device, the DepthAI backend, DSP runtime,
`balanced` profile, a 30-second measurement period, two inference threads,
50 messages per report, and device monitoring enabled.

See [the benchmark commands](../README.md) and [all values in JSON](RESULTS.json).

## Performance

| Model | FPS | Latency (ms) | Throughput relative to FP16 unoptimized |
| --- | ---: | ---: | ---: |
| [fp16_unoptimized](fp16_unoptimized/yolov8l.rvc4.tar_benchmark_results.csv) | 33.76 | 57.67 | 1.00× |
| [fp16_optimized](fp16_optimized/yolov8l.rvc4.tar_benchmark_results.csv) | 39.91 | 48.35 | 1.18× |
| [int8_per_tensor](int8_per_tensor/yolov8l.rvc4.tar_benchmark_results.csv) | 107.96 | 17.11 | 3.20× |
| [int8_per_channel](int8_per_channel/yolov8l.rvc4.tar_benchmark_results.csv) | 105.77 | 17.19 | 3.13× |
| [int8_int16](int8_int16/yolov8l.rvc4.tar_benchmark_results.csv) | 46.53 | 41.49 | 1.38× |
| [int8_wrong_calibration](int8_wrong_calibration/yolov8l.rvc4.tar_benchmark_results.csv) | 104.14 | 17.50 | 3.09× |

FP16 optimization increased measured throughput by 18.22% and reduced reported latency by 16.17%. INT8 per-channel achieved 2.65× the optimized FP16 throughput.


## Device monitoring

The main monitoring measurements during benchmarking, rounded to two decimal places.

| Model | power_sys (W) | power_core (W) | dsp (%) | memory (MiB) | cpu (%) |
| --- | ---: | ---: | ---: | ---: | ---: |
| fp16_unoptimized | 6.42 | 6.96 | 74.09 | 1196.42 | 16.75 |
| fp16_optimized | 7.24 | 7.80 | 74.07 | 1200.21 | 17.59 |
| int8_per_tensor | 4.96 | 5.19 | 73.98 | 991.56 | 21.29 |
| int8_per_channel | 5.29 | 6.17 | 73.60 | 996.00 | 21.58 |
| int8_int16 | 5.84 | 5.98 | 74.46 | 1046.72 | 18.56 |
| int8_wrong_calibration | 6.17 | 6.51 | 73.83 | 1003.10 | 21.50 |

## Source artifacts

- **fp16_unoptimized**: [CSV](fp16_unoptimized/yolov8l.rvc4.tar_benchmark_results.csv) · [console log](fp16_unoptimized/benchmark.log)
- **fp16_optimized**: [CSV](fp16_optimized/yolov8l.rvc4.tar_benchmark_results.csv) · [console log](fp16_optimized/benchmark.log)
- **int8_per_tensor**: [CSV](int8_per_tensor/yolov8l.rvc4.tar_benchmark_results.csv) · [console log](int8_per_tensor/benchmark.log)
- **int8_per_channel**: [CSV](int8_per_channel/yolov8l.rvc4.tar_benchmark_results.csv) · [console log](int8_per_channel/benchmark.log)
- **int8_int16**: [CSV](int8_int16/yolov8l.rvc4.tar_benchmark_results.csv) · [console log](int8_int16/benchmark.log)
- **int8_wrong_calibration**: [CSV](int8_wrong_calibration/yolov8l.rvc4.tar_benchmark_results.csv) · [console log](int8_wrong_calibration/benchmark.log)
