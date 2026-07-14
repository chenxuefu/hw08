import hashlib
import json
from pathlib import Path

from loguru import logger


ROOT = Path(__file__).resolve().parent.parent / "data" / "wheat_augmented"


def main():
    for split in ["train", "valid", "test"]:
        split_dir = ROOT / split
        ann_file = split_dir / "_annotations.coco.json"
        if not ann_file.exists():
            continue
        data = json.loads(ann_file.read_text(encoding="utf-8"))
        renamed = 0
        for img in data["images"]:
            old_name = img["file_name"]
            if len(old_name) <= 60:
                continue
            ext = Path(old_name).suffix.lower() or ".jpg"
            short = hashlib.md5(old_name.encode("utf-8")).hexdigest()[:14]
            new_name = f"img_{short}{ext}"
            old_path = split_dir / old_name
            new_path = split_dir / new_name
            if old_path.exists() and not new_path.exists():
                old_path.rename(new_path)
                renamed += 1
            elif not old_path.exists() and new_path.exists():
                renamed += 0
            img["file_name"] = new_name
        ann_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("split={} renamed={} total_images={}", split, renamed, len(data["images"]))


if __name__ == "__main__":
    main()
