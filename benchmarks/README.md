# Benchmark commands

Run the commands from `benchmarks` folder using the defined virtual environment.

Run these commands sequentially with no other pipeline using the device.
Each command benchmarks the current NNArchive from `../conversion/output/` on
DepthAI RVC4 device, with identical settings: DepthAI backend, DSP runtime,
`balanced` profile, two inference threads, 50 messages per report, and a
30-second measurement period.
Device monitoring is enabled consistently for all models; the saved results
include the telemetry reported by ModelConverter. It needs shell access through
ADB or passwordless SSH as `root` on the same device. If you want to skip the device monitoring change the update the command with `--no-device-monitor` flag.

Each command runs inside its model's output directory because `--save` writes
its CSV to the current directory. The subshell returns you to this directory
afterward. Repeating a command replaces its benchmark CSV.

These are **single-run measurements**, not averages across independent trials.
FPS measures benchmark throughput; latency is the value reported for this
concurrent workload, so it is not necessarily `1000 / FPS`. These timings do
not include the full LuxonisEval data-loading, parsing and scoring pipeline.


Each model folder contains the original benchmark CSV, and console log.

## FP16 unoptimized

```bash
(
  cd output/fp16_unoptimized
  modelconverter benchmark rvc4 --model-path "../../../conversion/output/fp16_unoptimized/yolov8l.rvc4.tar.xz" --device-ip "192.168.68.110" --dai-benchmark --runtime dsp --profile balanced --benchmark-time 30 --num-threads 2 --num-messages 50 --device-monitor --save
)
```

## FP16 optimized

```bash
(
  cd output/fp16_optimized
  modelconverter benchmark rvc4 --model-path "../../../conversion/output/fp16_optimized/yolov8l.rvc4.tar.xz" --device-ip "192.168.68.110" --dai-benchmark --runtime dsp --profile balanced --benchmark-time 30 --num-threads 2 --num-messages 50 --device-monitor --save
)
```

## INT8 per-tensor

```bash
(
  cd output/int8_per_tensor
  modelconverter benchmark rvc4 --model-path "../../../conversion/output/int8_per_tensor/yolov8l.rvc4.tar.xz" --device-ip "192.168.68.110" --dai-benchmark --runtime dsp --profile balanced --benchmark-time 30 --num-threads 2 --num-messages 50 --device-monitor --save
)
```

## INT8 per-channel

```bash
(
  cd output/int8_per_channel
  modelconverter benchmark rvc4 --model-path "../../../conversion/output/int8_per_channel/yolov8l.rvc4.tar.xz" --device-ip "192.168.68.110" --dai-benchmark --runtime dsp --profile balanced --benchmark-time 30 --num-threads 2 --num-messages 50 --device-monitor --save
)
```

## INT8 / INT16

```bash
(
  cd output/int8_int16
  modelconverter benchmark rvc4 --model-path "../../../conversion/output/int8_int16/yolov8l.rvc4.tar.xz" --device-ip "192.168.68.110" --dai-benchmark --runtime dsp --profile balanced --benchmark-time 30 --num-threads 2 --num-messages 50 --device-monitor --save
)
```

## INT8 with random calibration

```bash
(
  cd output/int8_wrong_calibration
  modelconverter benchmark rvc4 --model-path "../../../conversion/output/int8_wrong_calibration/yolov8l.rvc4.tar.xz" --device-ip "192.168.68.110" --dai-benchmark --runtime dsp --profile balanced --benchmark-time 30 --num-threads 2 --num-messages 50 --device-monitor --save
)
```

## Results

See the [benchmark results](output/RESULTS.md) for all six models' FPS, latency,
system/core power, DSP utilization, memory usage, and CPU utilization.
The same results are available as [JSON](output/RESULTS.json).
