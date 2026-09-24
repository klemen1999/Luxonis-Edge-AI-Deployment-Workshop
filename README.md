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

Download the additional material from the
[workshop Google Drive folder](https://drive.google.com/drive/folders/1QhlF0cnoNUDEOhW58JqMkf4cMUQ8LJkg?usp=sharing):

1. Clone or download this repository, then download the required assets from Drive.
2. Extract any downloaded ZIP archives and merge their contents into the workshop
   root (the folder containing this README). Match the existing `data/`,
   `conversion/`, `eval/`, `analysis/`, and `benchmarks/` folders; if an archive
   has an enclosing folder, copy its contents rather than nesting that folder.
3. Check that the baseline is at
   `conversion/baseline_onnx/yolov8l.onnx.tar.xz`. Keep this NNArchive compressed;
   the conversion commands use it directly. Place any supplied run outputs in
   the corresponding stage's `output/` folder.
4. For downloaded datasets, follow the local registration instructions in the
   [data README](data/README.md), or regenerate them with its preparation script.

- Create a Python environment using [requirements.txt](requirements.txt) for
  data preparation and the deployment experiments. Training uses a separate
  environment with [training/requirements-train.txt](training/requirements-train.txt).
- Have Docker available for conversion and an accessible RVC4 device for
  on-device evaluation, analysis, and benchmarks. A CUDA-capable GPU is
  recommended for the training demo.
- Obtain the workshop baseline NNArchive and place it at
  `conversion/baseline_onnx/yolov8l.onnx.tar.xz`. Model binaries are excluded
  from Git and must be supplied separately.
- Replace example device addresses with your device's address. Layer analysis
  uses SSH; benchmark telemetry requires ADB or passwordless root SSH access.
  Run device jobs sequentially so only one job uses the device at a time.

From the workshop root (the folder containing this README), set up the main environment:

```bash
python3 -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
```

If you are generating the datasets instead of importing the downloaded exports,
run `python data/prepare_workshop_datasets.py` in this environment.

Run each later stage from its own folder, as specified in its README. To set up
the separate training environment, start from `workskop_material/`:

```bash
deactivate
python3 -m venv training/.venv-train
source training/.venv-train/bin/activate
python -m pip install -r training/requirements-train.txt
cd training
```

Switch back to the main environment for stages 3–6. The analysis and benchmark
commands enter per-variant output directories; create those directories before
running the commands on a fresh checkout.

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
