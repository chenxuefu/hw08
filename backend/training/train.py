from pathlib import Path

import torch
import yaml
from torch.optim import AdamW
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


def move_labels_to_device(labels, device):
    result = []
    for item in labels:
        payload = {}
        for key, value in item.items():
            payload[key] = value.to(device) if hasattr(value, "to") else value
        result.append(payload)
    return result


def train(config_path: str | Path):
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = AutoImageProcessor.from_pretrained(config["base_model"])
    model = RTDetrForObjectDetection.from_pretrained(
        config["base_model"],
        num_labels=4,
        ignore_mismatched_sizes=True,
        id2label={0: "rust", 1: "smut", 2: "healthy", 3: "aphid"},
        label2id={"rust": 0, "smut": 1, "healthy": 2, "aphid": 3},
    )
    model.to(device)
    train_dataset = WheatCocoDataset(config["train_dir"], augment=False)
    val_dataset = WheatCocoDataset(config["val_dir"], augment=False)
    train_loader = DataLoader(
        train_dataset,
        batch_size=config["batch_size"],
        shuffle=True,
        collate_fn=lambda batch: collate_fn(batch, processor),
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=config["batch_size"],
        shuffle=False,
        collate_fn=lambda batch: collate_fn(batch, processor),
    )
    optimizer = AdamW(model.parameters(), lr=float(config["learning_rate"]), weight_decay=float(config["weight_decay"]))
    best_val_loss = None
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    weight_file = Path(config["weight_file"]) if config.get("weight_file") else output_dir.with_suffix(".pth")
    weight_file.parent.mkdir(parents=True, exist_ok=True)
    for epoch in range(int(config["epochs"])):
        model.train()
        total_train_loss = 0.0
        train_steps = 0
        for batch in tqdm(train_loader, desc=f"train-{epoch + 1}"):
            optimizer.zero_grad()
            outputs = model(
                pixel_values=batch["pixel_values"].to(device),
                labels=move_labels_to_device(batch["labels"], device),
            )
            outputs.loss.backward()
            optimizer.step()
            total_train_loss += float(outputs.loss.item())
            train_steps += 1
        avg_train_loss = total_train_loss / train_steps if train_steps else 0
        model.eval()
        total_val_loss = 0.0
        total_steps = 0
        with torch.no_grad():
            for batch in tqdm(val_loader, desc=f"valid-{epoch + 1}"):
                outputs = model(
                    pixel_values=batch["pixel_values"].to(device),
                    labels=move_labels_to_device(batch["labels"], device),
                )
                total_val_loss += float(outputs.loss.item())
                total_steps += 1
        avg_val_loss = total_val_loss / total_steps if total_steps else 0
        print(f"epoch={epoch + 1} train_loss={avg_train_loss:.4f} val_loss={avg_val_loss:.4f}")
        if best_val_loss is None or avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            model.save_pretrained(output_dir)
            processor.save_pretrained(output_dir)
            torch.save(model.state_dict(), weight_file)
    return output_dir


if __name__ == "__main__":
    train(Path(__file__).resolve().parent / "config.yaml")
