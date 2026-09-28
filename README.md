# Edge AI deployment workshop

This workshop walks through preparing data, training a detector, converting a
model for Luxonis RVC4 hardware, and measuring its accuracy and performance.
Using a supplied Ultralytics YOLOv8L baseline with a 640 × 640 input shape,
you will compare FP16, INT8, and mixed
precision, explore the effects of calibration and ONNX optimization, and use
layer analysis to understand the results. The goal is to choose a deployment
variant based on measured accuracy, throughput, latency, and resource usage.

## Workshop roadmap

Follow the folders in this order. Each linked README contains the commands and
details for that stage.

| Step | Folder and instructions | What you will do |
| --- | --- | --- |
| 1 | [Data preparation](data/README.md) | Prepare 200 calibration images, a 300-image evaluation pool, a 10-image visualization subset, and a small training dataset from COCO. |
| 2 | [Training](training/README.md) | Inspect the data, train a light or heavy detector with Luxonis Train, review metrics, and export a checkpoint. |
| 3 | [Conversion](conversion/README.md) | Convert the supplied Ultralytics YOLOv8L (640 × 640) ONNX NNArchive into six RVC4 variants: two FP16 configurations, INT8 per-tensor, INT8 per-channel, W8A16, and INT8 with intentionally bad calibration. |
| 4 | [Evaluation](eval/README.md) | Compare the CPU ONNX baseline with converted models on the device, measure detection accuracy, and inspect prediction visualizations. |
| 5 | [Layer analysis](analysis/README.md) | Compare layer outputs and cycle counts for all six variants to locate numerical differences and expensive operations. |
| 6 | [Benchmarking](benchmarks/README.md) | Measure device throughput, latency, and telemetry under consistent settings, then compare the performance and accuracy tradeoffs. |

The training stage is a separate workflow demonstration using predefined
Luxonis detection models. **From conversion onward (steps 3–6), all experiments
use [Ultralytics YOLOv8L](https://docs.ultralytics.com/models/yolov8/) with a
640 × 640 input shape.** The supplied model was first exported to ONNX and
packaged as an NNArchive using [Luxonis tools](https://github.com/luxonis/tools)
to prepare it for compatibility with DepthAI devices. This archive is the
starting point for the workshop's RVC4 conversions; the training demo's exports
are separate.

You can proceed directly from data preparation to conversion for the deployment
experiments. The dummy training data overlaps the evaluation pool; that pool
is not an independent test set for the demo's trained models.

## Before you begin

Follow these setup steps in order. The **workshop root** is the folder containing
this README (`workskop_material/`).

### 1. Check prerequisites

| Requirement | Purpose |
| --- | --- |
| Python 3 with pip and venv support | Run the workshop tools. The recorded runs used Python 3.10. |
| Git | Clone the repository and install LuxonisEval from its repository. |
| Docker | Run model conversion and, optionally, the SNPE tool wrappers when regenerating analyses. |
| OpenSSH client (`ssh` and `scp`) | Access the device over the network. |
| Accessible RVC4 device with passwordless root SSH | Run on-device evaluation, analysis, and benchmark monitoring. |
| Internet access | Download dependencies, Docker images, and datasets; load Plotly when opening analysis HTML plots. |
| Graphical desktop, for interactive inspection | Use the dataset viewer. Saved evaluation visualizations and the Pareto plot can be generated headlessly. |
| CUDA-capable GPU, recommended for training | Accelerate the separate training demo. |

### 2. Download the repository and workshop assets

Clone or download this repository, then download the additional material from the
[workshop Google Drive folder](https://drive.google.com/drive/folders/1QhlF0cnoNUDEOhW58JqMkf4cMUQ8LJkg?usp=sharing).

Extract `workshop-results.zip` into the **workshop root** (the folder containing
this README). It contains only `conversion/output/`, so the converted models
and intermediate files land in the paths used by the workshop commands:

```bash
# Run from the workshop root; adjust the ZIP path to its download location.
unzip /path/to/workshop-results.zip -d .
```

Extract `workshop-inputs.zip` into the same workshop root. It supplies `data/`
and `conversion/baseline_onnx/yolov8l.onnx.tar.xz`. The baseline model is
distributed in this ZIP, not tracked in Git:

```bash
unzip /path/to/workshop-inputs.zip -d .
```

Check that the baseline is at `conversion/baseline_onnx/yolov8l.onnx.tar.xz`.
Keep this NNArchive compressed; conversion commands use it directly.

Reference analysis, evaluation, benchmark, and plotting results are already
included in the repository's `output_done/` folders; they are not in
`workshop-results.zip`.

### 3. Create the main Python environment

From the workshop root, install [requirements.txt](requirements.txt) for data
preparation and the deployment experiments:

```bash
python3 -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
```

### 4. Register or generate the datasets

For downloaded datasets, follow the local registration instructions in the
[data README](data/README.md). To generate them instead, run this from the
workshop root with the main environment active:

```bash
python data/prepare_workshop_datasets.py
```

### 5. Prepare device access and analysis tools

Replace the example device addresses in commands and configs with your RVC4's
address. Verify passwordless root SSH access and run device jobs sequentially.

Layer analysis is optional: use the supplied reports under `analysis/output_done/`,
or follow the [analysis setup and commands](analysis/README.md#setup-before-running-analysis)
to regenerate them. Regeneration requires the converted DLCs, matching modified
ONNX files, visualization images, and SNPE tools on the host and device. The
included [Docker wrappers](tools/snpe/README.md) provide the host tools without
a native SNPE installation.

### 6. Create a separate environment for training

If following the training stage, start from the workshop root with the main
environment active, then install
[training/requirements-train.txt](training/requirements-train.txt):

```bash
deactivate
python3 -m venv training/.venv-train
source training/.venv-train/bin/activate
python -m pip install -r training/requirements-train.txt
cd training
```

Switch back to the main environment for the deployment stages (steps 3–6 in
the workshop roadmap).

## Live YOLO demo

Run [live_demo.py](live_demo.py) from the workshop root with the main Python
environment active. Its dependencies are included in `requirements.txt`.
Requires a connected OAK camera, a web browser, and a YOLO NN archive
(`.tar.xz`) compiled for your device with YOLO parser metadata. The preview
uses the DepthAI visualizer to display camera frames and detection overlays.
Camera frames are H.264-encoded on the device to reduce preview bandwidth.

```bash
python live_demo.py --model /path/to/model.tar.xz
```

Add `-d <device ip>` (or `--device`) to select a device by IP; omit it for
automatic selection. Add `--fps 15` to set the camera preview and encoder frame
rate (default: 30 FPS). Open `http://localhost:8082` in your browser and select the
`Camera`, `Detections`, and `Controls` topics. Focus the visualizer and press `w` / `s` to increase /
decrease confidence, `e` / `d` to increase / decrease IoU, or `q` to quit.
Thresholds change by 0.05 within 0–1. The `Controls` overlay shows their current
values and keyboard hints live on the frame.

## Reading the results

Use the full evaluation's `result.json` for accuracy; the smaller visualization
runs are diagnostic. Layer comparisons explain numerical changes and compute
costs, while benchmarks measure throughput and latency separately from the
evaluation pipeline. Compare these measurements together when selecting a model.

The existing [analysis summary](analysis/output_done/RESULTS.md) and
[benchmark summary](benchmarks/output_done/RESULTS.md) provide reference results.
Reference reports, plots, logs, and summaries are tracked in `output_done/`.
Commands write fresh runs to ignored `output/` folders. Conversion outputs and
dataset downloads still come from Drive or are regenerated locally. Benchmark results are single-run
measurements, so treat them as workshop observations rather than repeated-trial
averages.

Generate an accuracy–throughput Pareto plot from the result summaries with
[the plotting tool](tools/README.md). It exports PNG and CSV files.
