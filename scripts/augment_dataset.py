import hashlib
import json
import shutil
from collections import defaultdict
from pathlib import Path

import albumentations as A
import cv2
import numpy as np
from loguru import logger


AUG_PER_IMAGE = 4
SRC = Path(__file__).resolve().parent.parent / "data" / "wheat_merged"
DST = Path(__file__).resolve().parent.parent / "data" / "wheat_augmented"
TRANSFORM = A.Compose(
    [
        A.HorizontalFlip(p=0.5),
        A.Affine(rotate=(-15, 15), translate_percent=(-0.05, 0.05), scale=(0.9, 1.1), p=0.7),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.6),
        A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=15, val_shift_limit=15, p=0.5),
        A.GaussNoise(p=0.3),
        A.MotionBlur(blur_limit=5, p=0.2),
    ],
    bbox_params=A.BboxParams(format="coco", label_fields=["category_ids"], min_area=10, min_visibility=0.2),
)


def imread_unicode(path: Path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def imwrite_unicode(path: Path, image, extension=".jpg"):
    success, buffer = cv2.imencode(extension, image)
    if success:
        path.write_bytes(buffer.tobytes())
    return success


def load_coco(split_dir: Path):
    return json.loads((split_dir / "_annotations.coco.json").read_text(encoding="utf-8"))


def write_coco(split_dir: Path, payload: dict):
    (split_dir / "_annotations.coco.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def copy_split(split_name: str):
    src_dir = SRC / split_name
    dst_dir = DST / split_name
    dst_dir.mkdir(parents=True, exist_ok=True)
    for item in src_dir.iterdir():
        shutil.copy2(item, dst_dir / item.name)


def augment_train():
    src_dir = SRC / "train"
    dst_dir = DST / "train"
    dst_dir.mkdir(parents=True, exist_ok=True)
    annotation_data = load_coco(src_dir)
    annotations_by_image = defaultdict(list)
    for annotation in annotation_data["annotations"]:
        annotations_by_image[annotation["image_id"]].append(annotation)
    new_images = []
    new_annotations = []
    next_image_id = 0
    next_annotation_id = 1
    for image_item in annotation_data["images"]:
        source_path = src_dir / image_item["file_name"]
        shutil.copy2(source_path, dst_dir / image_item["file_name"])
        new_images.append(
            {
                "id": next_image_id,
                "file_name": image_item["file_name"],
                "width": image_item["width"],
                "height": image_item["height"],
            }
        )
        for annotation in annotations_by_image[image_item["id"]]:
            new_annotations.append(
                {
                    "id": next_annotation_id,
                    "image_id": next_image_id,
                    "category_id": annotation["category_id"],
                    "bbox": annotation["bbox"],
                    "area": annotation["area"],
                    "segmentation": [],
                    "iscrowd": 0,
                }
            )
            next_annotation_id += 1
        next_image_id += 1
        image = imread_unicode(source_path)
        if image is None:
            continue
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = [annotation["bbox"] for annotation in annotations_by_image[image_item["id"]]]
        labels = [annotation["category_id"] for annotation in annotations_by_image[image_item["id"]]]
        if not boxes:
            continue
        for index in range(AUG_PER_IMAGE):
            try:
                transformed = TRANSFORM(image=image_rgb, bboxes=boxes, category_ids=labels)
            except Exception:
                continue
            if not transformed["bboxes"]:
                continue
            short_id = hashlib.md5(image_item["file_name"].encode("utf-8")).hexdigest()[:10]
            augmented_name = f"aug_{short_id}_{index}.jpg"
            augmented_bgr = cv2.cvtColor(transformed["image"], cv2.COLOR_RGB2BGR)
            imwrite_unicode(dst_dir / augmented_name, augmented_bgr)
            height, width = transformed["image"].shape[:2]
            new_images.append(
                {
                    "id": next_image_id,
                    "file_name": augmented_name,
                    "width": width,
                    "height": height,
                }
            )
            for bbox, category_id in zip(transformed["bboxes"], transformed["category_ids"]):
                x, y, box_w, box_h = bbox
                new_annotations.append(
                    {
                        "id": next_annotation_id,
                        "image_id": next_image_id,
                        "category_id": int(category_id),
                        "bbox": [float(x), float(y), float(box_w), float(box_h)],
                        "area": float(box_w * box_h),
                        "segmentation": [],
                        "iscrowd": 0,
                    }
                )
                next_annotation_id += 1
            next_image_id += 1
    write_coco(
        dst_dir,
        {
            "info": {"description": "Wheat Pest Augmented Dataset"},
            "licenses": [],
            "categories": annotation_data["categories"],
            "images": new_images,
            "annotations": new_annotations,
        },
    )
    stats = defaultdict(int)
    for annotation in new_annotations:
        stats[annotation["category_id"]] += 1
    names = {item["id"]: item["name"] for item in annotation_data["categories"]}
    logger.info("train images={} annotations={} by_class={}", len(new_images), len(new_annotations), {names[key]: value for key, value in stats.items()})


def main():
    if DST.exists():
        shutil.rmtree(DST)
    augment_train()
    for split_name in ["valid", "test"]:
        copy_split(split_name)
        annotation_data = load_coco(DST / split_name)
        logger.info("split={} images={} annotations={}", split_name, len(annotation_data["images"]), len(annotation_data["annotations"]))
    logger.info("output_dir={}", DST)


if __name__ == "__main__":
    main()
