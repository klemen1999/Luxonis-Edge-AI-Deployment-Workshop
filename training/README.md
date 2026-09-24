# Dummy detector training

Train a small workshop example with Luxonis Train, using the light or heavy
configuration adapted from `../../training/`. These are predefined Luxonis
`DetectionModel` variants, separate from the YOLOv8l conversion experiments.

Both configs use `coco-validation-dummy-training`: 300 images split into
**240 train / 30 val / 30 test**, with the 80 COCO class names. This is a training
workflow demonstration, not a dataset for establishing production accuracy.
The same 300 images also form the workshop evaluation pool, so that full pool
is not an independent test set for these trained models.

## Separate training environment

Run the setup from the repository root. Use a dedicated environment for training,
with dependencies from this directory's `requirements-train.txt`:

All remaining commands run from `training` with `.venv-train`
active. The configs use mixed precision (`16-mixed`); a CUDA-capable GPU is recommended.
Check that PyTorch can access it:

```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

## Prepare and inspect the dataset

First prepare the datasets using the [data preparation instructions](../data/README.md)
in the data environment. That script registers `coco-validation-dummy-training`
locally. Virtual environments under the same user share that dataset registration;
keep the same Luxonis-ML storage settings when switching environments.
An exported directory alone does not register the dataset on another machine;
see the data README's import instructions if using the supplied export there.

Show the dataset information and inspect each split interactively:

```bash
luxonis_ml data info coco-validation-dummy-training
luxonis_ml data inspect coco-validation-dummy-training --view train
luxonis_ml data inspect coco-validation-dummy-training --view val
luxonis_ml data inspect coco-validation-dummy-training --view test
```

Generate class-distribution and annotation-health reports for each split:

```bash
luxonis_ml data health coco-validation-dummy-training --view train --save-dir output/data-health/train
luxonis_ml data health coco-validation-dummy-training --view val --save-dir output/data-health/val
luxonis_ml data health coco-validation-dummy-training --view test --save-dir output/data-health/test
```

The inspect commands open an interactive viewer and need a graphical session.
Health plots are saved to the specified folders.

## Choose a configuration

| Config | Model variant | Input height × width | Epochs | Batch size | Gradient accumulation | Workers | Output directory |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| [config_light.yaml](config_light.yaml) | light | 320 × 512 | 300 | 8 | 8 | 4 | `output/light/` |
| [config_heavy.yaml](config_heavy.yaml) | heavy | 480 × 768 | 300 | 8 | 8 | 8 | `output/heavy/` |

Both configs retain the complete training settings from `../../training/`,
including validation every 10 epochs, eight logged images, mixed precision,
EMA, the TripleLRSGD strategy, and the `ConvertOnTrainEnd` callback.
Batch size 8 with accumulation over 8 batches gives a nominal effective batch
size of 64 per device; the final accumulation group may be smaller.

The workshop adaptations are the dataset, explicit train/val/test views, model
names, and output directories. Luxonis Train's default automatic configuration
adjustments remain enabled, as in the original configs; inspect the saved resolved
configuration for effective settings. Conversion runs automatically at training end.
The export command below is available for exporting a selected checkpoint explicitly.

Start with light for the faster option. Heavy uses a larger model and higher
resolution, requiring more compute and GPU memory. These are full 300-epoch
schedules, not shortened workshop runs; training duration depends on the hardware.

## Light model

Preview the training loader and then start training:

```bash
luxonis_train inspect --config config_light.yaml --view train
luxonis_train train --config config_light.yaml
```

## Heavy model

Use these commands instead to run the heavy option:

```bash
luxonis_train inspect --config config_heavy.yaml --view train
luxonis_train train --config config_heavy.yaml
```

Run one training job at a time. For a CPU-only light demo, override the accelerator
and precision; it will be slower:

```bash
luxonis_train train --config config_light.yaml trainer.accelerator cpu trainer.precision '"32"'
```

## Inspect the training output

Named run directories and TensorBoard logs are written under `output/light/` or
`output/heavy/`. Runs include checkpoints and the resolved training configuration.
Open TensorBoard to compare losses, validation metrics and logged images:

```bash
tensorboard --logdir output
```

Select a checkpoint using validation performance. Replace the example checkpoint
path below with the selected `.ckpt` file from the light run, then evaluate it on
the separate 30-image test split and export ONNX:

```bash
luxonis_train test --config config_light.yaml --weights "output/light/<run-name>/best_val_metric/<checkpoint>.ckpt" --view test
luxonis_train export --config config_light.yaml --weights "output/light/<run-name>/best_val_metric/<checkpoint>.ckpt" --save-path output/light/export
```

For the heavy run, use `config_heavy.yaml`, its checkpoint under `output/heavy/`,
and `--save-path output/heavy/export`. Keep these exports separate from the supplied
YOLOv8l baseline and its measured conversion/evaluation results.
