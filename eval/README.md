# Evaluation commands

Run the commands from `eval` folder using the defined virtual environment.

Run the commands below sequentially. The ONNX baseline uses the CPU; converted
models use the RVC4 device, as specified in their configs.

Each full evaluation uses 300 test images with confidence threshold 0.001.
Each visualization run uses the 10-image visualization dataset with confidence
threshold 0.25. Report accuracy from `result.json`; the separate
`visualize_result.json` is a diagnostic result for that smaller, filtered run.
Images are saved under each variant's `output/<variant>/visualizations/` folder.
Rerunning writes to the same result and visualization paths.

## Baseline ONNX

```bash
luxonis_eval eval --config configs/baseline_onnx.yaml --output-json output/baseline_onnx/result.json
luxonis_eval eval --config configs/baseline_onnx_visualize.yaml --output-json output/baseline_onnx/visualize_result.json
```

## FP16 unoptimized

```bash
luxonis_eval eval --config configs/fp16_unoptimized.yaml --output-json output/fp16_unoptimized/result.json
luxonis_eval eval --config configs/fp16_unoptimized_visualize.yaml --output-json output/fp16_unoptimized/visualize_result.json
```

## FP16 optimized

```bash
luxonis_eval eval --config configs/fp16_optimized.yaml --output-json output/fp16_optimized/result.json
luxonis_eval eval --config configs/fp16_optimized_visualize.yaml --output-json output/fp16_optimized/visualize_result.json
```

## INT8 per-tensor

```bash
luxonis_eval eval --config configs/int8_per_tensor.yaml --output-json output/int8_per_tensor/result.json
luxonis_eval eval --config configs/int8_per_tensor_visualize.yaml --output-json output/int8_per_tensor/visualize_result.json
```

## INT8 per-channel

```bash
luxonis_eval eval --config configs/int8_per_channel.yaml --output-json output/int8_per_channel/result.json
luxonis_eval eval --config configs/int8_per_channel_visualize.yaml --output-json output/int8_per_channel/visualize_result.json
```

## INT8 / INT16

```bash
luxonis_eval eval --config configs/int8_int16.yaml --output-json output/int8_int16/result.json
luxonis_eval eval --config configs/int8_int16_visualize.yaml --output-json output/int8_int16/visualize_result.json
```

## INT8 with wrong calibration


```bash
luxonis_eval eval --config configs/int8_wrong_calibration.yaml --output-json output/int8_wrong_calibration/result.json
luxonis_eval eval --config configs/int8_wrong_calibration_visualize.yaml --output-json output/int8_wrong_calibration/visualize_result.json
```

## Results

See the [evaluation results](output/RESULTS.md) for all seven models on the
300-image test dataset. Only full evaluation runs are included. 
The same results are available as [JSON](output/RESULTS.json).
