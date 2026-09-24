# Conversion commands

Run the commands from `conversion` folder using the defined virtual environment.

The supplied baseline is an **Ultralytics YOLOv8L model with a 640 × 640 input
shape**, exported to ONNX and packaged as an NNArchive using
[Luxonis tools](https://github.com/luxonis/tools) for compatibility with DepthAI devices.
These commands convert that archive to RVC4 using the ModelConverter image with
SNPE 2.41.0. Docker must be available.
Prepare the image folders with [the data preparation script](../data/README.md)
first. Run conversions sequentially.

`--output-dir <variant>` creates `output/<variant>/`. Each result contains `yolov8l.rvc4.tar.xz`, the DLC, converter
logs and resolved settings. Repeating a command replaces that variant's output.
Use the [evaluation commands](../eval/README.md) after conversion to measure
accuracy and produce visualizations.

| Variant | Precision |
|---|---|
| `fp16_unoptimized` | FP16, ONNX optimization/simplification disabled |
| `fp16_optimized` | FP16, default ONNX optimizations |
| `int8_per_tensor` | INT8, per-channel disabled |
| `int8_per_channel` | INT8, per-channel enabled |
| `int8_int16` | W8A16, per-channel enabled |
| `int8_wrong_calibration` | INT8, per-channel enabled |

The bad-calibration case intentionally omits the entire calibration configuration.
ModelConverter then uses its default random calibration tensors instead of real
images. Quantization remains enabled; this is not the same as disabling calibration.

The commands pass the NNArchive through `--path` and settings as key/value CLI
overrides. They do not load the YAML files in `configs/` automatically. The
[bad-calibration YAML](configs/int8_wrong_calibration.yaml) documents the same
settings without a calibration block. CLI calibration paths in the other
commands are relative to the working directory shown above.

## FP16 unoptimized

```bash
modelconverter convert rvc4 --path "baseline_onnx/yolov8l.onnx.tar.xz" --output-dir "fp16_unoptimized" rvc4.quantization_mode FP16_STANDARD onnx_simplification False onnx_optimizations False
```

## FP16 optimized

```bash
modelconverter convert rvc4 --path "baseline_onnx/yolov8l.onnx.tar.xz" --output-dir "fp16_optimized" rvc4.quantization_mode FP16_STANDARD
```

## INT8 per-tensor

```bash
modelconverter convert rvc4 --path "baseline_onnx/yolov8l.onnx.tar.xz" --output-dir "int8_per_tensor" rvc4.quantization_mode INT8_STANDARD calibration.path ../data/calibration/images calibration.max_images 200 calibration.resize_method PAD rvc4.use_per_channel_quantization False
```

## INT8 per-channel

```bash
modelconverter convert rvc4 --path "baseline_onnx/yolov8l.onnx.tar.xz" --output-dir "int8_per_channel" rvc4.quantization_mode INT8_STANDARD calibration.path ../data/calibration/images calibration.max_images 200 calibration.resize_method PAD rvc4.use_per_channel_quantization True
```

## INT8 / INT16

```bash
modelconverter convert rvc4 --path "baseline_onnx/yolov8l.onnx.tar.xz" --output-dir "int8_int16" rvc4.quantization_mode INT8_INT16_MIXED calibration.path ../data/calibration/images calibration.max_images 200 calibration.resize_method PAD rvc4.use_per_channel_quantization True
```

## INT8 with bad calibration

```bash
modelconverter convert rvc4 --path "baseline_onnx/yolov8l.onnx.tar.xz" --output-dir "int8_wrong_calibration" rvc4.quantization_mode INT8_STANDARD rvc4.use_per_channel_quantization True onnx_optimizations True onnx_simplification onnxsim keep_intermediate_outputs True
```
