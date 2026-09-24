# Model analysis

Running the analyses is optional. Download the prepared analysis results and HTML
plots from the [workshop Google Drive folder](https://drive.google.com/drive/folders/1QhlF0cnoNUDEOhW58JqMkf4cMUQ8LJkg?usp=sharing)
and place them under `analysis/output/` to use the [results](output/RESULTS.md)
and interactive views directly. SNPE tools are only needed to regenerate the
analyses, not to view supplied plots or run `modelconverter visualize` on supplied CSVs.

Analyze the FP16 unoptimized, FP16 optimized and INT8 per-channel YOLOv8l conversions using the 10 images in
`../data/coco-validation-visualization/test/images`. 

Run the commands from `analysis` folder using the defined virtual environment.
Inference runs on the device over SSH.
Run commands sequentially, with no other pipeline using the device.

If regenerating the analyses, enable the [SNPE wrappers](../tools/snpe/README.md)
from this `analysis` folder. Docker must be running and accessible:

```bash
export PATH="$(cd ../tools/snpe && pwd):$PATH"
```

Both layer output comparison and layer timing analysis are enabled. Each DLC is
paired with its conversion's **modified ONNX**, including embedded preprocessing.
The unoptimized model uses `yolov8l-modified.onnx`; the others use
`yolov8l-simplified-modified.onnx`.

The analyzer resizes images directly to the input dimensions and converts RGB to
BGR. It does not apply the evaluation pipeline's letterbox padding. These reports
compare corresponding layer tensors on identical analyzer inputs; they are not AP
measurements. Use `../eval` for accuracy and `../benchmarks` for FPS/latency.

Reports are written to `output/<variant>/output/analysis/yolov8l/`:
`layer_comparison.csv` and `layer_cycles.csv`.

## FP16 unoptimized

```bash
(
  cd output/fp16_unoptimized
  modelconverter analyze \
    --device-ip 192.168.68.110 \
    --dlc-model-path ../../../conversion/output/fp16_unoptimized/yolov8l.dlc \
    --onnx-model-path ../../../conversion/output/fp16_unoptimized/intermediate_outputs/yolov8l-modified.onnx \
    --image-dirs ../../../data/coco-validation-visualization/test/images \
    --image-subset 10 \
    --analyze-outputs \
    --analyze-cycles 2>&1 | tee analyze.log
)
```

## FP16 optimized

```bash
(
  cd output/fp16_optimized
  modelconverter analyze \
    --device-ip 192.168.68.110 \
    --dlc-model-path ../../../conversion/output/fp16_optimized/yolov8l.dlc \
    --onnx-model-path ../../../conversion/output/fp16_optimized/intermediate_outputs/yolov8l-simplified-modified.onnx \
    --image-dirs ../../../data/coco-validation-visualization/test/images \
    --image-subset 10 \
    --analyze-outputs \
    --analyze-cycles 2>&1 | tee analyze.log
)
```

## INT8 per-channel

```bash
(
  cd output/int8_per_channel
  modelconverter analyze \
    --device-ip 192.168.68.110 \
    --dlc-model-path ../../../conversion/output/int8_per_channel/yolov8l.dlc \
    --onnx-model-path ../../../conversion/output/int8_per_channel/intermediate_outputs/yolov8l-simplified-modified.onnx \
    --image-dirs ../../../data/coco-validation-visualization/test/images \
    --image-subset 10 \
    --analyze-outputs \
    --analyze-cycles 2>&1 | tee analyze.log
)
```


## Interactive visualizations

After each analysis completes, generate its interactive HTML views:

```bash
modelconverter visualize output/fp16_unoptimized/output/analysis/yolov8l
modelconverter visualize output/fp16_optimized/output/analysis/yolov8l
modelconverter visualize output/int8_per_channel/output/analysis/yolov8l
```


These commands create `layer_outputs_visual.html` and `layer_cycles_visual.html`
beside the CSVs and attempt to open them in a browser. Use the metric dropdowns in each plot, hover for exact values, and zoom into
individual sections of the graph.

## Results

See the [analysis results](output/RESULTS.md) for the three models' layer-cycle
comparison, input preprocessing costs, and links to the interactive HTML views.
