# Workshop COCO datasets

Run from the repository root with the virtual environment from `requirements.txt`:

```bash
python3 data/prepare_workshop_datasets.py
```

The script creates these outputs beside itself:

| Directory | Images / splits | Purpose |
|---|---|---|
| `calibration/images/` | 200 images | Model conversion calibration |
| `coco-validation-all-classes/` | 300 test | Full evaluation |
| `coco-validation-visualization/` | 10 test | Evaluation visualizations |
| `coco-validation-dummy-training/` | 240 train, 30 val, 30 test | Dummy training (80:10:10) |

The three annotated datasets are self-contained **Luxonis-ML native exports**.
Each contains `metadata.json`, split folders with `images/` and
`annotations.json`, and `source-splits.json` recording original COCO image IDs
and the class mapping. Empty splits may contain only `annotations.json`.

The script samples 500 images from all 5,000 COCO val2017 images using
`random.Random(42).sample()` over sorted IDs. The first 200 are calibration;
the other 300 form the evaluation pool. Calibration and this pool are disjoint.

The visualization set samples 10 of those 300 IDs with seed 42. The dummy
training set independently shuffles the sorted 300 IDs with seed 42 and assigns
240/30/30 to train/val/test. Its three splits are disjoint and together contain
exactly the evaluation pool. All allocations are recorded in `selection.json`.
There is no class filtering or balancing in the original 500-image selection.

All 80 COCO classes are registered in every export, including classes absent
from a small subset. Indices 0–79 follow ascending COCO category-ID order.
Exports contain bounding boxes only, excluding crowd and nonpositive-size
boxes. Images with no remaining boxes are retained as negative examples.

Downloads are cached under `.cache/`. Rerunning reuses complete downloads and
rebuilds all four outputs and the three named local Luxonis-ML datasets.

## Loading the prepared datasets

After running the script, the datasets are already registered locally:

```python
from luxonis_ml.data import LuxonisDataset, LuxonisLoader

visualization = LuxonisDataset("coco-validation-visualization")
loader = LuxonisLoader(visualization, view="test", height=640, width=640)

training = LuxonisDataset("coco-validation-dummy-training")
train_loader = LuxonisLoader(training, view="train", height=640, width=640)
# Use view="val" or view="test" for the other training-demo splits.
```

For LuxonisEval visualization configs, use dataset name
`coco-validation-visualization` and the `test` view.

On another machine, import the desired native export and restore the complete
class mapping (the native parser may infer only classes present in annotations):

```python
import json
from pathlib import Path
from luxonis_ml.data import LuxonisParser
from luxonis_ml.enums import DatasetType

path = Path("workskop_material/data/coco-validation-visualization")
dataset = LuxonisParser(
    str(path), dataset_name=path.name,
    dataset_type=DatasetType.NATIVE, delete_local=True,
).parse()
classes = json.loads((path / "source-splits.json").read_text())["classes"]
dataset.set_classes({entry["name"]: entry["class_id"] for entry in classes})
```

The same import works for `coco-validation-dummy-training` and preserves its
train/val/test assignments.

Images and annotations are subject to the [COCO terms](https://cocodataset.org/#termsofuse).
