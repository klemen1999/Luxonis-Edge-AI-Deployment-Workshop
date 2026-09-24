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
| 5 | [Layer analysis](analysis/README.md) | Compare layer outputs and cycle counts for selected variants to locate numerical differences and expensive operations. |
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

Extract downloaded ZIP archives and merge their contents into the workshop root.
Match the existing `data/`, `conversion/`, `eval/`, `analysis/`, and `benchmarks/`
folders. If an archive has an enclosing folder, copy its contents rather than
nesting that folder. Place supplied run outputs in the corresponding stage's
`output/` folder.

Check that the baseline is at `conversion/baseline_onnx/yolov8l.onnx.tar.xz`.
Keep this NNArchive compressed; conversion commands use it directly. Model
binaries are excluded from Git and must be supplied separately.

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

Replace the example device addresses in commands and configs with your device's
address and verify passwordless root SSH access. Run device jobs sequentially
so only one job uses the device at a time.

**Optional: regenerate the analyses.** You can download the prepared analysis
results and HTML plots from the [workshop Google Drive folder](https://drive.google.com/drive/folders/1QhlF0cnoNUDEOhW58JqMkf4cMUQ8LJkg?usp=sharing)
and place them under `analysis/output/`. Viewing these supplied results does not
require SNPE tools or rerunning analysis.

Only if you run `modelconverter analyze` yourself, you need `snpe-dlc-info` and
`snpe-diagview` on `PATH`. The included
[SNPE wrappers](tools/snpe/README.md) run those tools in the pinned ModelConverter
Docker image (SNPE 2.41). From the workshop root, enable them in your shell:

```bash
export PATH="$PWD/tools/snpe:$PATH"
```

Docker must be running and accessible to your user. The first invocation may
pull the container image. Run analysis from within the workshop directory.

Run each stage from its own folder, as specified in its README. The analysis
and benchmark commands enter per-variant output directories; create those
directories before running the commands on a fresh checkout.

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

## Reading the results

Use the full evaluation's `result.json` for accuracy; the smaller visualization
runs are diagnostic. Layer comparisons explain numerical changes and compute
costs, while benchmarks measure throughput and latency separately from the
evaluation pipeline. Compare these measurements together when selecting a model.

The existing [analysis summary](analysis/output/RESULTS.md) and
[benchmark summary](benchmarks/output/RESULTS.md) provide reference results.
Generated reports, plots, logs, model binaries, and dataset downloads are ignored
by Git; download the supplied artifacts from Drive or regenerate them to follow
links to individual run artifacts. The results
summaries remain eligible for version control. Benchmark results are single-run
measurements, so treat them as workshop observations rather than repeated-trial
averages.

Generate an accuracy–throughput Pareto plot from the result summaries with
[the plotting tool](tools/README.md). It exports PNG and CSV files.
