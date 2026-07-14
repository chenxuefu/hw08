import json
import random
import shutil
from collections import defaultdict
from pathlib import Path

from loguru import logger


random.seed(42)
ROOT = Path(__file__).resolve().parent.parent / "data"
OUT = ROOT / "wheat_merged"
NEW_CATEGORIES = [
    {"id": 1, "name": "rust", "supercategory": "wheat"},
    {"id": 2, "name": "smut", "supercategory": "wheat"},
    {"id": 3, "name": "healthy", "supercategory": "wheat"},
    {"id": 4, "name": "aphid", "supercategory": "wheat"},
]
CATEGORY_MAP = {
    ("wheat_disease", 1): 1,
    ("wheat_disease", 2): 1,
    ("wheat_disease", 3): 2,
    ("wheat_disease", 4): 1,
    ("wheat_disease", 5): 1,
    ("wheat_disease", 6): 1,
    ("wheat_disease", 7): 1,
    ("wheat_disease", 8): 3,
    ("wheat_aphid", 1): 4,
}


def collect_samples():
    samples = []
    for dataset_name in ["wheat_disease", "wheat_aphid"]:
        dataset_dir = ROOT / dataset_name
        for split_name in ["train", "valid", "test"]:
            annotation_path = dataset_dir / split_name / "_annotations.coco.json"
            if not annotation_path.exists():
                continue
            annotation_data = json.loads(annotation_path.read_text(encoding="utf-8"))
            image_mapping = {item["id"]: item for item in annotation_data["images"]}
            annotations_by_image = defaultdict(list)
            for annotation in annotation_data["annotations"]:
                mapped_key = (dataset_name, annotation["category_id"])
                if mapped_key not in CATEGORY_MAP:
                    continue
                copied_annotation = dict(annotation)
                copied_annotation["category_id"] = CATEGORY_MAP[mapped_key]
                annotations_by_image[annotation["image_id"]].append(copied_annotation)
            for image_id, image_item in image_mapping.items():
                source_path = dataset_dir / split_name / image_item["file_name"]
                if not source_path.exists():
                    continue
                samples.append(
                    {
                        "src_path": source_path,
                        "new_name": f'{dataset_name}_{image_item["file_name"]}',
                        "width": image_item["width"],
                        "height": image_item["height"],
                        "annotations": annotations_by_image.get(image_id, []),
                    }
                )
    return samples


def split_samples(samples, ratios=(0.8, 0.1, 0.1)):
    random.shuffle(samples)
    count = len(samples)
    train_count = int(count * ratios[0])
    valid_count = int(count * ratios[1])
    return {
        "train": samples[:train_count],
        "valid": samples[train_count:train_count + valid_count],
        "test": samples[train_count + valid_count:],
    }


def write_split(split_name, split_samples):
    split_dir = OUT / split_name
    split_dir.mkdir(parents=True, exist_ok=True)
    images = []
    annotations = []
    annotation_id = 1
    for image_id, sample in enumerate(split_samples):
        shutil.copy2(sample["src_path"], split_dir / sample["new_name"])
        images.append(
            {
                "id": image_id,
                "file_name": sample["new_name"],
                "width": sample["width"],
                "height": sample["height"],
            }
        )
        for annotation in sample["annotations"]:
            annotations.append(
                {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": annotation["category_id"],
                    "bbox": annotation["bbox"],
                    "area": annotation.get("area", annotation["bbox"][2] * annotation["bbox"][3]),
                    "segmentation": annotation.get("segmentation", []),
                    "iscrowd": annotation.get("iscrowd", 0),
                }
            )
            annotation_id += 1
    payload = {
        "info": {"description": "Wheat Pest Merged Dataset"},
        "licenses": [],
        "categories": NEW_CATEGORIES,
        "images": images,
        "annotations": annotations,
    }
    (split_dir / "_annotations.coco.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    stats = defaultdict(int)
    for annotation in annotations:
        stats[annotation["category_id"]] += 1
    names = {item["id"]: item["name"] for item in NEW_CATEGORIES}
    logger.info("split={} images={} annotations={} by_class={}", split_name, len(images), len(annotations), {names[key]: value for key, value in stats.items()})


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    samples = collect_samples()
    logger.info("samples={}", len(samples))
    for split_name, split_samples in split_samples(samples).items():
        write_split(split_name, split_samples)
    logger.info("output_dir={}", OUT)


if __name__ == "__main__":
    main()
