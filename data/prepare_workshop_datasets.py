#!/usr/bin/env python3
"""Prepare workshop calibration, evaluation, visualization and dummy-training datasets."""

from __future__ import annotations

import json
import random
import shutil
import time
from pathlib import Path
from typing import Any

from fiftyone.utils.coco import download_coco_dataset_split
from luxonis_ml.data import LuxonisParser
from luxonis_ml.enums import DatasetType
from PIL import Image
from requests.exceptions import RequestException


DATASET_NAME = "coco-validation-all-classes"
VISUALIZATION_NAME = "coco-validation-visualization"
TRAINING_NAME = "coco-validation-dummy-training"
VISUALIZATION_COUNT = 10
TOTAL_IMAGES = 500
CALIBRATION_COUNT = 200
SEED = 42
COCO_SPLIT = "validation"
COCO_YEAR = "2017"
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / ".cache"
RAW_DIR = CACHE_DIR / "raw"
SCRATCH_DIR = CACHE_DIR / "scratch"
DOWNLOAD_DIR = CACHE_DIR / "download" / COCO_SPLIT
PREPARED_DIR = CACHE_DIR / "prepared-coco" / "test"
EXPORT_STAGING_DIR = CACHE_DIR / "native-export"
DATASET_EXPORT_DIR = BASE_DIR / DATASET_NAME
CALIBRATION_DIR = BASE_DIR / "calibration"
ANNOTATIONS_PATH = RAW_DIR / "instances_val2017.json"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(value, file, indent=2)
        file.write("\n")


def reset_directory(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True)


def download_with_retries(destination: Path, **kwargs: Any) -> None:
    for attempt in range(4):
        try:
            download_coco_dataset_split(
                str(destination),
                COCO_SPLIT,
                year=COCO_YEAR,
                label_types=["detections"],
                raw_dir=str(RAW_DIR),
                scratch_dir=str(SCRATCH_DIR),
                **kwargs,
            )
            return
        except RequestException:
            if attempt == 3:
                print("Download interrupted; rerun to reuse completed images.")
                raise
            delay = (2, 5, 10)[attempt]
            print(f"Download failed; retrying in {delay}s...")
            time.sleep(delay)


def ensure_annotations() -> dict[str, Any]:
    if not ANNOTATIONS_PATH.exists():
        # Reuse an existing official annotation file without changing its cache.
        existing = (
            BASE_DIR.parent / "data" / ".cache" / "coco-classroom-objects"
            / "raw" / ANNOTATIONS_PATH.name
        )
        if existing.exists():
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy2(existing, ANNOTATIONS_PATH)
        else:
            download_with_retries(CACHE_DIR / "annotation-bootstrap", max_samples=0)
    coco = read_json(ANNOTATIONS_PATH)
    if len(coco["images"]) != 5_000 or len(coco["categories"]) != 80:
        raise RuntimeError("Expected the full COCO 2017 validation annotations.")
    return coco


def select_images(coco: dict[str, Any]) -> dict[str, list[int]]:
    # Sample the complete image population, including images without boxes.
    image_ids = sorted(image["id"] for image in coco["images"])
    selected = random.Random(SEED).sample(image_ids, TOTAL_IMAGES)
    return {
        "calibration": selected[:CALIBRATION_COUNT],
        "test": selected[CALIBRATION_COUNT:],
    }


def download_images(
    coco: dict[str, Any], image_ids: list[int], download_dir: Path = DOWNLOAD_DIR,
) -> None:
    images_by_id = {image["id"]: image for image in coco["images"]}
    expected_names = {images_by_id[i]["file_name"] for i in image_ids}
    images_dir = download_dir / "data"
    images_dir.mkdir(parents=True, exist_ok=True)
    # Keep compatible partial downloads when the selection changes.
    for path in images_dir.glob("*.jpg"):
        if path.name not in expected_names:
            path.unlink()
    for name in expected_names:
        path = images_dir / name
        if path.exists():
            try:
                with Image.open(path) as image:
                    image.verify()
            except (OSError, SyntaxError):
                path.unlink()

    if {path.name for path in images_dir.glob("*.jpg")} != expected_names:
        # FiftyOne must recompute labels if a previous selection was cached.
        (download_dir / "labels.json").unlink(missing_ok=True)
        download_with_retries(download_dir, image_ids=image_ids, num_workers=8)

    for image_id in image_ids:
        info = images_by_id[image_id]
        with Image.open(images_dir / info["file_name"]) as image:
            if image.size != (info["width"], info["height"]):
                raise RuntimeError(f"Unexpected image dimensions: {info['file_name']}")
            image.verify()
    print(f"Verified {len(image_ids)} downloaded validation images.")


def detection_annotations(coco: dict[str, Any], image_ids: list[int]) -> dict[str, Any]:
    selected = set(image_ids)
    # Match the existing workshop's detection-only convention. Keep empty
    # images so random selection never silently loses negative examples.
    return {
        key: value for key, value in coco.items()
        if key not in {"images", "annotations"}
    } | {
        "images": [image for image in coco["images"] if image["id"] in selected],
        "annotations": [
            {key: annotation[key] for key in
             ("id", "image_id", "category_id", "bbox", "area", "iscrowd")}
            for annotation in coco["annotations"]
            if annotation["image_id"] in selected
            and not annotation.get("iscrowd", 0)
            and annotation["bbox"][2] > 0
            and annotation["bbox"][3] > 0
        ],
    }


def prepare_outputs(coco: dict[str, Any], allocations: dict[str, list[int]]) -> None:
    images_by_id = {image["id"]: image for image in coco["images"]}
    reset_directory(CALIBRATION_DIR)
    reset_directory(PREPARED_DIR)
    for split, destination in (
        ("calibration", CALIBRATION_DIR / "images"),
        ("test", PREPARED_DIR / "data"),
    ):
        destination.mkdir()
        for image_id in allocations[split]:
            name = images_by_id[image_id]["file_name"]
            shutil.copy2(DOWNLOAD_DIR / "data" / name, destination / name)

    write_json(CALIBRATION_DIR / "manifest.json", {
        "source": "COCO 2017 validation",
        "seed": SEED,
        "count": CALIBRATION_COUNT,
        "samples": [
            {"coco_image_id": i, "file_name": images_by_id[i]["file_name"]}
            for i in allocations["calibration"]
        ],
    })
    write_json(PREPARED_DIR / "labels.json", detection_annotations(coco, allocations["test"]))


def export_dataset(
    coco: dict[str, Any], splits: dict[str, list[int]],
    dataset_name: str, prepared_dir: Path,
) -> None:
    dataset = LuxonisParser(
        str(prepared_dir),
        dataset_name=dataset_name,
        dataset_type=DatasetType.COCO,
        delete_local=True,
    ).parse(split="test", random_split=False)

    # COCO IDs are sparse (1..90); detector indices are contiguous (0..79).
    # Explicitly register every class, even if absent from this random subset.
    categories = sorted(coco["categories"], key=lambda category: category["id"])
    classes = {category["name"]: index for index, category in enumerate(categories)}
    dataset.set_classes(classes)
    images_by_id = {image["id"]: image for image in coco["images"]}
    dataset.make_splits({
        split: [str(prepared_dir / "data" / images_by_id[i]["file_name"]) for i in ids]
        for split, ids in splits.items()
    }, replace_old_splits=True)
    split_counts = {name: len(ids) for name, ids in (dataset.get_splits() or {}).items() if ids}
    expected = {name: len(ids) for name, ids in splits.items()}
    if len(dataset) != sum(expected.values()) or split_counts != expected:
        raise RuntimeError(f"Unexpected dataset size/splits: {len(dataset)}, {split_counts}")
    if not dataset.get_classes() or any(mapping != classes for mapping in dataset.get_classes().values()):
        raise RuntimeError("The dataset does not contain the complete COCO class mapping.")

    shutil.rmtree(EXPORT_STAGING_DIR, ignore_errors=True)
    dataset.export(EXPORT_STAGING_DIR, dataset_type=DatasetType.NATIVE, zip_output=False)
    export_dir = BASE_DIR / dataset_name
    if export_dir.exists():
        shutil.rmtree(export_dir)
    shutil.move(str(EXPORT_STAGING_DIR / dataset_name), export_dir)
    shutil.rmtree(EXPORT_STAGING_DIR)
    write_json(export_dir / "source-splits.json", {
        "source": "COCO 2017 validation",
        "seed": SEED,
        "splits": splits,
        "classes": [
            {"name": category["name"], "coco_category_id": category["id"], "class_id": index}
            for index, category in enumerate(categories)
        ],
    })


def derived_splits(test_ids: list[int]) -> dict[str, dict[str, list[int]]]:
    """Select reproducibly without involving the calibration images."""
    if len(test_ids) != 300 or len(set(test_ids)) != 300:
        raise ValueError("Expected 300 unique evaluation images.")
    training_ids = sorted(test_ids)
    random.Random(SEED).shuffle(training_ids)
    return {
        VISUALIZATION_NAME: {
            "test": random.Random(SEED).sample(sorted(test_ids), VISUALIZATION_COUNT)
        },
        TRAINING_NAME: {
            "train": training_ids[:240],
            "val": training_ids[240:270],
            "test": training_ids[270:],
        },
    }


def parse_and_export(coco: dict[str, Any], allocations: dict[str, list[int]]) -> None:
    export_dataset(coco, {"test": allocations["test"]}, DATASET_NAME, PREPARED_DIR)
    images_by_id = {image["id"]: image for image in coco["images"]}
    for name, splits in derived_splits(allocations["test"]).items():
        prepared = CACHE_DIR / "prepared-coco" / name
        reset_directory(prepared)
        (prepared / "data").mkdir()
        ids = [i for values in splits.values() for i in values]
        for i in ids:
            filename = images_by_id[i]["file_name"]
            shutil.copy2(PREPARED_DIR / "data" / filename, prepared / "data" / filename)
        write_json(prepared / "labels.json", detection_annotations(coco, ids))
        export_dataset(coco, splits, name, prepared)


def main() -> None:
    coco = ensure_annotations()
    allocations = select_images(coco)
    selected = allocations["calibration"] + allocations["test"]
    if len(selected) != TOTAL_IMAGES or len(set(selected)) != TOTAL_IMAGES:
        raise RuntimeError("Image allocations are not unique and complete.")
    write_json(BASE_DIR / "selection.json", {
        "source": "COCO 2017 validation",
        "seed": SEED,
        "selection": "random.Random(seed).sample(sorted(all_validation_image_ids), 500)",
        "allocations": allocations,
        "derived_datasets": derived_splits(allocations["test"]),
    })
    download_images(coco, selected)
    prepare_outputs(coco, allocations)
    parse_and_export(coco, allocations)
    print(f"Calibration: {CALIBRATION_DIR / 'images'} (200 images)")
    print(f"Luxonis-ML dataset: {DATASET_EXPORT_DIR} (test: 300 images, 80 classes)")
    print(f"Visualization: {BASE_DIR / VISUALIZATION_NAME} (test: 10 images)")
    print(f"Dummy training: {BASE_DIR / TRAINING_NAME} (train: 240, val: 30, test: 30)")


if __name__ == "__main__":
    main()
