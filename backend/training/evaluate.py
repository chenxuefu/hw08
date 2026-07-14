from pathlib import Path

import torch
import yaml
from torch.utils.data import DataLoader
from tqdm import tqdm
from transformers import AutoImageProcessor, RTDetrForObjectDetection

from training.dataset import WheatCocoDataset


def collate_fn(batch, processor):
    images = [item[0] for item in batch]
    annotations = [item[1] for item in batch]
    encoded = processor(images=images, annotations=annotations, return_tensors="pt")
    return {
        "pixel_values": encoded["pixel_values"],
        "labels": encoded["labels"],
    }


def evaluate(config_path: str | Path):
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = AutoImageProcessor.from_pretrained(config["base_model"])
    model = RTDetrForObjectDetection.from_pretrained(config["output_dir"])
    model.to(device)
    model.eval()
    dataset = WheatCocoDataset(config["val_dir"], augment=False)
    loader = DataLoader(
        dataset,
        batch_size=config["batch_size"],
        shuffle=False,
        collate_fn=lambda batch: collate_fn(batch, processor),
    )
    total_loss = 0.0
    total_steps = 0
    with torch.no_grad():
        for batch in tqdm(loader, desc="evaluate"):
            outputs = model(
                pixel_values=batch["pixel_values"].to(device),
                labels=[{key: value.to(device) if hasattr(value, "to") else value for key, value in item.items()} for item in batch["labels"]],
            )
            total_loss += float(outputs.loss.item())
            total_steps += 1
    avg_loss = total_loss / total_steps if total_steps else 0
    return {"val_loss": avg_loss}


if __name__ == "__main__":
    result = evaluate(Path(__file__).resolve().parent / "config.yaml")
    raise SystemExit(0 if result else 1)
