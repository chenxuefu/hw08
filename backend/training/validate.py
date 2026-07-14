import json
import time
from pathlib import Path

import cv2
import numpy as np
import torch
import yaml
from loguru import logger
from PIL import Image
from tqdm import tqdm
from transformers import AutoImageProcessor, RTDetrForObjectDetection


CLASS_NAMES = {0: "rust", 1: "smut", 2: "healthy", 3: "aphid"}
CLASS_NAMES_CN = {0: "锈病", 1: "黑穗病", 2: "健康叶", 3: "蚜虫"}
CLASS_COLORS = {0: (50, 70, 216), 1: (55, 64, 93), 2: (50, 125, 46), 3: (23, 127, 245)}


def imwrite_unicode(path: Path, image, extension: str = ".jpg"):
    success, buffer = cv2.imencode(extension, image)
    if success:
        path.write_bytes(buffer.tobytes())
    return success


def draw_boxes(image_np: np.ndarray, detections: list) -> np.ndarray:
    result = image_np.copy()
    for det in detections:
        class_id = det["class_id_internal"]
        color = CLASS_COLORS.get(class_id, (0, 200, 0))
        x1, y1, x2, y2 = [int(v) for v in det["xyxy"]]
        cv2.rectangle(result, (x1, y1), (x2, y2), color, 2)
        label = f"{CLASS_NAMES[class_id]} {det['confidence']:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(result, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)
        cv2.putText(result, label, (x1 + 3, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return result


def validate(config_path: str | Path, threshold: float = 0.25, save_visualizations: int = 10):
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    weight_file = Path(config["weight_file"])
    if not weight_file.is_absolute():
        backend_root = Path(__file__).resolve().parent.parent
        weight_file = (backend_root / weight_file).resolve()
    if not weight_file.exists():
        raise FileNotFoundError(f"weight file not found: {weight_file}")

    processor = AutoImageProcessor.from_pretrained(config["base_model"])
    model = RTDetrForObjectDetection.from_pretrained(
        config["base_model"],
        num_labels=4,
        ignore_mismatched_sizes=True,
        id2label=CLASS_NAMES,
        label2id={v: k for k, v in CLASS_NAMES.items()},
    )
    state = torch.load(weight_file, map_location=device)
    model.load_state_dict(state, strict=False)
    model.to(device)
    model.eval()

    test_dir = (Path(__file__).resolve().parent.parent.parent / "data" / "wheat_augmented" / "test").resolve()
    ann_file = test_dir / "_annotations.coco.json"
    data = json.loads(ann_file.read_text(encoding="utf-8"))

    viz_dir = (Path(__file__).resolve().parent / ".." / "storage" / "validation_samples").resolve()
    viz_dir.mkdir(parents=True, exist_ok=True)

    total_images = 0
    total_detections = 0
    total_time_ms = 0
    by_class = {0: 0, 1: 0, 2: 0, 3: 0}
    confidence_values = []
    images_with_detection = 0
    saved_viz = 0
    sample_reports = []

    for item in tqdm(data["images"], desc="validate"):
        image_path = test_dir / item["file_name"]
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(device)
        start = time.perf_counter()
        with torch.no_grad():
            outputs = model(**inputs)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        target_sizes = torch.tensor([[image.height, image.width]], device=device)
        result = processor.post_process_object_detection(
            outputs, threshold=threshold, target_sizes=target_sizes
        )[0]

        detections = []
        for score, label, box in zip(result["scores"], result["labels"], result["boxes"]):
            label_id = int(label.item())
            x1, y1, x2, y2 = [float(v) for v in box.tolist()]
            detections.append(
                {
                    "class_id_internal": label_id,
                    "class_id": label_id + 1,
                    "class_name": CLASS_NAMES.get(label_id, "unknown"),
                    "class_name_cn": CLASS_NAMES_CN.get(label_id, "未知"),
                    "confidence": round(float(score.item()), 4),
                    "xyxy": [x1, y1, x2, y2],
                    "bbox": [round(x1, 2), round(y1, 2), round(x2 - x1, 2), round(y2 - y1, 2)],
                }
            )
            by_class[label_id] = by_class.get(label_id, 0) + 1
            confidence_values.append(float(score.item()))
            total_detections += 1

        total_images += 1
        total_time_ms += elapsed_ms
        if detections:
            images_with_detection += 1

        if detections and saved_viz < save_visualizations:
            image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            annotated = draw_boxes(image_np, detections)
            viz_path = viz_dir / f"sample_{saved_viz:02d}.jpg"
            imwrite_unicode(viz_path, annotated)
            saved_viz += 1
            if len(sample_reports) < 5:
                sample_reports.append(
                    {
                        "image": item["file_name"],
                        "viz": str(viz_path.name),
                        "detections": [
                            {
                                "class_id": d["class_id"],
                                "class_name": d["class_name"],
                                "class_name_cn": d["class_name_cn"],
                                "confidence": d["confidence"],
                                "bbox": d["bbox"],
                            }
                            for d in detections
                        ],
                    }
                )

    avg_inference_ms = round(total_time_ms / total_images, 2) if total_images else 0
    avg_confidence = round(float(np.mean(confidence_values)), 4) if confidence_values else 0
    detection_rate = round(images_with_detection / total_images, 4) if total_images else 0

    summary = {
        "total_images": total_images,
        "images_with_detection": images_with_detection,
        "detection_rate": detection_rate,
        "total_detections": total_detections,
        "avg_inference_time_ms": avg_inference_ms,
        "avg_confidence": avg_confidence,
        "by_class": {CLASS_NAMES[k]: v for k, v in by_class.items()},
        "threshold": threshold,
        "device": device,
        "weight_file": str(weight_file),
        "viz_dir": str(viz_dir),
        "samples": sample_reports,
    }

    logger.info("validation summary:")
    logger.info(json.dumps(summary, ensure_ascii=False, indent=2))
    report_path = viz_dir / "validation_report.json"
    report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    validate(Path(__file__).resolve().parent / "config.yaml")
