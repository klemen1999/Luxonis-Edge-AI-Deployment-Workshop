# Model analysis

Running the analyses is optional. Download the prepared analysis results and HTML
plots from the [workshop Google Drive folder](https://drive.google.com/drive/folders/1QhlF0cnoNUDEOhW58JqMkf4cMUQ8LJkg?usp=sharing)
and place them under `analysis/output/` to use the [results](output/RESULTS.md)
and interactive views directly. SNPE tools are only needed to regenerate the
analyses, not to view supplied plots or run `modelconverter visualize` on supplied CSVs.

Analyze all six YOLOv8l conversions in `../conversion/output` using the 10 images
in `../data/coco-validation-visualization/test/images`.

## Setup before running analysis

Complete the [main environment setup](../README.md#3-create-the-main-python-environment)
and prepare the [10 visualization images](../data/README.md) and
[conversion outputs](../conversion/README.md). Each variant needs its DLC and
matching modified ONNX under `intermediate_outputs/`; if missing, rerun conversion
with `keep_intermediate_outputs True`.

With Docker running, execute this from the **workshop root** (`workskop_material/`):

```bash
source env/bin/activate
export PATH="$PWD/tools/snpe:$PATH"
snpe-dlc-info --help
snpe-diagview --help
ssh -o BatchMode=yes root@192.168.68.110 'snpe-net-run --help'
cd analysis
```

The [SNPE wrappers](../tools/snpe/README.md) provide the two host tools via Docker;
`snpe-net-run` and its runtime must be available on the device. Replace the IP
above and below with your RVC4's address. It must be reachable by DepthAI and
passwordless root SSH, with `ssh`/`scp` available on the host.

Repeat activation and PATH setup in each new shell. Keep files within the
workshop directory for Docker access. Run the commands below from `analysis` in
Bash, sequentially, with no other pipeline using the device.

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
  set -euo pipefail
  mkdir -p output/fp16_unoptimized
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
  set -euo pipefail
  mkdir -p output/fp16_optimized
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
  set -euo pipefail
  mkdir -p output/int8_per_channel
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


## INT8 per-tensor

```bash
(
  set -euo pipefail
  mkdir -p output/int8_per_tensor
  cd output/int8_per_tensor
  modelconverter analyze \
    --device-ip 192.168.68.110 \
    --dlc-model-path ../../../conversion/output/int8_per_tensor/yolov8l.dlc \
    --onnx-model-path ../../../conversion/output/int8_per_tensor/intermediate_outputs/yolov8l-simplified-modified.onnx \
    --image-dirs ../../../data/coco-validation-visualization/test/images \
    --image-subset 10 \
    --analyze-outputs \
    --analyze-cycles 2>&1 | tee analyze.log
)
```

## INT8 / INT16

```bash
(
  set -euo pipefail
  mkdir -p output/int8_int16
  cd output/int8_int16
  modelconverter analyze \
    --device-ip 192.168.68.110 \
    --dlc-model-path ../../../conversion/output/int8_int16/yolov8l.dlc \
    --onnx-model-path ../../../conversion/output/int8_int16/intermediate_outputs/yolov8l-simplified-modified.onnx \
    --image-dirs ../../../data/coco-validation-visualization/test/images \
    --image-subset 10 \
    --analyze-outputs \
    --analyze-cycles 2>&1 | tee analyze.log
)
```

## INT8 with bad calibration

```bash
(
  set -euo pipefail
  mkdir -p output/int8_wrong_calibration
  cd output/int8_wrong_calibration
  modelconverter analyze \
    --device-ip 192.168.68.110 \
    --dlc-model-path ../../../conversion/output/int8_wrong_calibration/yolov8l.dlc \
    --onnx-model-path ../../../conversion/output/int8_wrong_calibration/intermediate_outputs/yolov8l-simplified-modified.onnx \
    --image-dirs ../../../data/coco-validation-visualization/test/images \
    --image-subset 10 \
    --analyze-outputs \
    --analyze-cycles 2>&1 | tee analyze.log
)
```

## Interactive visualizations

After each analysis completes, generate its interactive HTML views. These require
Plotly in the active Python environment (`python -m pip install plotly` if it is
missing):

```bash
modelconverter visualize output/fp16_unoptimized/output/analysis/yolov8l
modelconverter visualize output/fp16_optimized/output/analysis/yolov8l
modelconverter visualize output/int8_per_channel/output/analysis/yolov8l
modelconverter visualize output/int8_per_tensor/output/analysis/yolov8l
modelconverter visualize output/int8_int16/output/analysis/yolov8l
modelconverter visualize output/int8_wrong_calibration/output/analysis/yolov8l
```


These commands create `layer_outputs_visual.html` and `layer_cycles_visual.html`
beside the CSVs and attempt to open them in a browser. Use the metric dropdowns in each plot, hover for exact values, and zoom into
individual sections of the graph.


## Results

See the [analysis results](output/RESULTS.md) for all six models' layer-cycle
comparison, input preprocessing costs, final output tensor differences, run
provenance, and links to the interactive HTML views.
