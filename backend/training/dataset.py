import json
from pathlib import Path

import albumentations as A
import numpy as np
from PIL import Image
from torch.utils.data import Dataset


class WheatCocoDataset(Dataset):
    def __init__(self, split_dir: str | Path, augment: bool = False):
        self.split_dir = Path(split_dir)
        self.annotation_path = self.split_dir / "_annotations.coco.json"
        self.annotation_data = json.loads(self.annotation_path.read_text(encoding="utf-8"))
        self.image_items = self.annotation_data["images"]
        self.categories = {item["id"]: item["name"] for item in self.annotation_data["categories"]}
        self.annotations_by_image = {}
        for annotation in self.annotation_data["annotations"]:
            self.annotations_by_image.setdefault(annotation["image_id"], []).append(annotation)
        self.transform = self.build_transform(augment)

    def __len__(self):
        return len(self.image_items)

    def __getitem__(self, index):
        image_item = self.image_items[index]
        image_path = self.split_dir / image_item["file_name"]
        image = Image.open(image_path).convert("RGB")
        annotations = self.annotations_by_image.get(image_item["id"], [])
        boxes = [item["bbox"] for item in annotations]
        labels = [item["category_id"] for item in annotations]
        if self.transform is not None and boxes:
            transformed = self.transform(
                image=np.array(image),
                bboxes=boxes,
                category_ids=labels,
            )
            image = Image.fromarray(transformed["image"])
            boxes = [list(item) for item in transformed["bboxes"]]
            labels = list(transformed["category_ids"])
        img_w, img_h = image.size
        coco_annotations = []
        for annotation, bbox, label in zip(annotations, boxes, labels):
            x, y, w, h = [float(value) for value in bbox]
            x = max(0.0, min(x, float(img_w) - 1.0))
            y = max(0.0, min(y, float(img_h) - 1.0))
            w = max(1.0, min(w, float(img_w) - x))
            h = max(1.0, min(h, float(img_h) - y))
            coco_annotations.append(
                {
                    "bbox": [x, y, w, h],
                    "category_id": int(label) - 1,
                    "area": float(annotation.get("area", w * h)),
                    "iscrowd": int(annotation.get("iscrowd", 0)),
                }
            )
        target = {"image_id": image_item["id"], "annotations": coco_annotations}
        return image, target

    @staticmethod
    def build_transform(augment: bool):
        if not augment:
            return None
        return A.Compose(
            [
                A.HorizontalFlip(p=0.5),
                A.RandomBrightnessContrast(p=0.5),
                A.Affine(scale=(0.9, 1.1), translate_percent=(-0.05, 0.05), rotate=(-10, 10), p=0.5),
            ],
            bbox_params=A.BboxParams(format="coco", label_fields=["category_ids"], min_area=10, min_visibility=0.2),
        )
