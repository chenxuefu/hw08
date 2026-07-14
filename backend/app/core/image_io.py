from pathlib import Path

from PIL import Image


def read_image(path: str | Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGB")


def image_size(path: str | Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size
